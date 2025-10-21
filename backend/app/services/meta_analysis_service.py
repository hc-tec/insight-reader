"""
元信息分析服务
负责调用LLM分析文章的元信息（作者意图、时效性、偏见、知识缺口）
"""

from openai import OpenAI
from sqlalchemy.orm import Session
from app.models.models import MetaAnalysis, Article
from app.config import settings
from app.utils.sentence_splitter import split_sentences
from app.utils.error_logger import log_llm_error
import json
import json_repair
import hashlib
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class MetaAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        # 使用 settings 中的配置初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url if settings.openai_base_url else None
        )

    async def analyze_article(
        self,
        title: str,
        author: str,
        publish_date: str,
        content: str,
        user_id: Optional[int] = None,
        source_url: Optional[str] = None,
        language: str = "zh",
        force_reanalyze: bool = False
    ) -> Dict:
        """
        元信息分析主方法

        Args:
            title: 文章标题
            author: 作者
            publish_date: 发布日期
            content: 文章内容
            user_id: 用户ID (可选，匿名用户为None)
            source_url: 文章来源URL (可选)
            language: 语言 (zh/en)
            force_reanalyze: 是否强制重新分析

        Returns:
            元信息分析结果
        """

        # 计算内容哈希用于去重
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        # 查找或创建文章记录
        article = self.db.query(Article).filter(
            Article.content_hash == content_hash
        ).first()

        if article:
            # 文章已存在，更新最后阅读时间和阅读次数
            article.last_read_at = datetime.utcnow()
            article.read_count += 1
            logger.info(f"文章已存在: article_id={article.id}, 阅读次数={article.read_count}")
        else:
            # 创建新文章记录
            try:
                publish_dt = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            except:
                publish_dt = None

            article = Article(
                user_id=user_id,
                title=title,
                author=author,
                source_url=source_url,
                publish_date=publish_dt,
                content=content,
                content_hash=content_hash,
                language=language,
                word_count=len(content)
            )
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            logger.info(f"新建文章记录: article_id={article.id}")

        # 检查是否已有元信息分析
        if not force_reanalyze and article.meta_analysis:
            logger.info(f"使用缓存的元信息分析: article_id={article.id}")
            return self._format_response(article.meta_analysis)

        # 执行分析
        logger.info(f"开始元信息分析: article_id={article.id}")
        start_time = datetime.utcnow()

        try:
            # 调用 LLM
            llm_result = await self._call_llm_for_meta_analysis(
                title=title,
                author=author,
                publish_date=publish_date,
                content=content,
                language=language
            )

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # 如果是重新分析，删除旧记录
            if force_reanalyze and article.meta_analysis:
                self.db.delete(article.meta_analysis)
                self.db.commit()

            # 保存分析结果
            meta_analysis = MetaAnalysis(
                article_id=article.id,
                author_intent=llm_result['author_intent'],
                timeliness_score=llm_result['timeliness']['score'],
                timeliness_analysis=llm_result['timeliness'],
                bias_analysis=llm_result['bias'],
                knowledge_gaps=llm_result['knowledge_gaps'],
                raw_llm_response=json.dumps(llm_result, ensure_ascii=False),
                analysis_quality={
                    "confidence_score": llm_result['author_intent']['confidence'],
                    "processing_time_ms": processing_time,
                    "llm_model": settings.default_model,
                    "prompt_version": "v1.0"
                }
            )

            self.db.add(meta_analysis)

            # 更新文章标题（如果AI生成了标题）
            if 'generated_title' in llm_result and llm_result['generated_title']:
                # 如果当前标题是自动截取的（以...结尾），则更新为AI生成的标题
                if article.title.endswith('...') or len(article.title) <= 50:
                    article.title = llm_result['generated_title']
                    logger.info(f"使用AI生成的标题更新文章: {article.title}")

            self.db.commit()
            self.db.refresh(meta_analysis)

            logger.info(f"元信息分析完成: article_id={article.id}, 耗时={processing_time}ms")

            return self._format_response(meta_analysis)

        except Exception as e:
            logger.error(f"元信息分析失败: article_id={article.id}, error={str(e)}")
            self.db.rollback()
            raise

    async def _call_llm_for_meta_analysis(
        self,
        title: str,
        author: str,
        publish_date: str,
        content: str,
        language: str
    ) -> Dict:
        """调用 LLM 进行元信息分析"""

        # 限制内容长度，避免超出 token 限制
        max_content_length = settings.max_context_length * 2  # 使用 settings 中的配置
        truncated_content = content[:max_content_length]

        # 分句
        sentences = split_sentences(truncated_content)

        # 构建 Prompt
        system_prompt = self._get_meta_analysis_system_prompt()
        user_prompt = self._get_meta_analysis_user_prompt(
            title=title,
            author=author,
            publish_date=publish_date,
            sentences=sentences,
            language=language
        )

        # 调用 OpenAI API，使用 settings 中的配置
        try:
            response = self.client.chat.completions.create(
                model=settings.default_model,  # 使用配置中的默认模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # 元信息分析需要较低温度以保证一致性
                max_tokens=2000
            )
        except Exception as e:
            # 记录LLM调用错误
            log_llm_error(
                service_name="meta_analysis",
                model_name=settings.default_model,
                error=e,
                request_data={
                    "title": title,
                    "author": author,
                    "sentence_count": len(sentences),
                    "language": language
                }
            )
            logger.error(f"❌ LLM 调用失败: {e}")
            raise

        # 解析响应
        try:
            # 先尝试使用json_repair修复可能的JSON格式错误
            raw_content = response.choices[0].message.content
            result = json_repair.repair_json(raw_content, return_objects=True, ensure_ascii=False)
            logger.info("✅ JSON解析成功（使用json_repair）")
        except Exception as e:
            # 记录JSON解析错误
            log_llm_error(
                service_name="meta_analysis",
                model_name=settings.default_model,
                error=e,
                request_data={
                    "response_content": response.choices[0].message.content[:500]
                }
            )
            logger.error(f"❌ JSON 解析失败: {e}")
            raise

        # 验证结构
        self._validate_llm_result(result)

        return result

    def _validate_llm_result(self, result: Dict):
        """验证 LLM 输出结构"""
        required_keys = ['generated_title', 'author_intent', 'timeliness', 'bias', 'knowledge_gaps']

        for key in required_keys:
            if key not in result:
                if key == 'generated_title':
                    logger.warning("LLM 输出缺少 generated_title 字段，将使用默认标题")
                    result['generated_title'] = "未命名文章"
                else:
                    raise ValueError(f"LLM 输出缺少必需字段: {key}")

        # 验证作者意图
        valid_intents = ['inform', 'persuade', 'entertain', 'provoke']
        if result['author_intent']['primary'] not in valid_intents:
            logger.warning(f"无效的作者意图类型: {result['author_intent']['primary']}, 使用默认值 'inform'")
            result['author_intent']['primary'] = 'inform'

        # 验证置信度
        if not 0 <= result['author_intent']['confidence'] <= 1:
            logger.warning(f"置信度超出范围: {result['author_intent']['confidence']}, 调整为 0.5")
            result['author_intent']['confidence'] = 0.5

        # 验证时效性分数
        if not 0 <= result['timeliness']['score'] <= 1:
            logger.warning(f"时效性分数超出范围: {result['timeliness']['score']}, 调整为 0.5")
            result['timeliness']['score'] = 0.5

    def _get_meta_analysis_system_prompt(self) -> str:
        """获取元信息分析的系统 Prompt"""
        return """你是一位专业的文本分析专家，擅长识别文章的元信息。

你的任务是分析用户提供的文章，并以JSON格式输出结构化的元信息分析结果。

# 分析维度

0. **文章标题 (generated_title)**
   - 为文章生成一个简洁、准确的标题（10-30字）
   - 标题应概括文章的核心主题
   - 使用中文，避免过于学术或晦涩的表达

1. **作者意图 (author_intent)**
   - primary: "inform" (告知), "persuade" (说服), "entertain" (娱乐), "provoke" (激发思考)
   - confidence: 0.0-1.0
   - description: 100字以内的详细说明
   - indicators: 3-5个关键识别依据

2. **时效性 (timeliness)**
   - score: 0.0-1.0 (0=永恒内容, 1=高度时效敏感)
   - category: "timeless" (永恒), "evergreen" (常青), "time-sensitive" (时效敏感), "breaking" (突发新闻)
   - decay_rate: "low" (慢), "medium" (中等), "high" (快)
   - best_before: ISO 8601日期或null
   - context_dependencies: 影响时效性的关键因素列表

3. **潜在偏见 (bias)**
   - detected: true/false
   - types: ["confirmation_bias", "political_bias", "cultural_bias", "selection_bias"]等
   - severity: "low", "medium", "high"
   - examples: [{text, type, explanation}]，最多3个
   - overall_balance: "balanced", "slightly_biased", "heavily_biased"

4. **知识缺口 (knowledge_gaps)**
   - prerequisites: 前置知识列表
   - assumptions: 隐含假设列表
   - missing_context: 缺失背景列表
   - related_concepts: 相关概念列表

# 输出格式

严格按照以下JSON schema输出：

{
  "generated_title": "文章的精炼标题",
  "author_intent": {
    "primary": "inform|persuade|entertain|provoke",
    "confidence": 0.85,
    "description": "string",
    "indicators": ["string", "string", "string"]
  },
  "timeliness": {
    "score": 0.4,
    "category": "timeless|evergreen|time-sensitive|breaking",
    "decay_rate": "low|medium|high",
    "best_before": "2025-12-31T00:00:00Z or null",
    "context_dependencies": ["string", "string"]
  },
  "bias": {
    "detected": false,
    "types": [],
    "severity": "low|medium|high",
    "examples": [],
    "overall_balance": "balanced|slightly_biased|heavily_biased"
  },
  "knowledge_gaps": {
    "prerequisites": ["string", "string"],
    "assumptions": ["string"],
    "missing_context": [],
    "related_concepts": ["string", "string", "string"]
  }
}

# 注意事项

- 分析要客观、中立，避免主观判断
- 对于不确定的分析，降低置信度
- 偏见检测要谨慎，避免误报
- 所有列表字段至少1个元素，最多5个
- 如果没有检测到偏见，types和examples为空数组
"""

    def _get_meta_analysis_user_prompt(
        self,
        title: str,
        author: str,
        publish_date: str,
        sentences: List[str],
        language: str
    ) -> str:
        """构建用户 Prompt"""
        # 格式化句子列表
        sentence_list = "\n".join([f"[{i}] {sentence}" for i, sentence in enumerate(sentences)])

        return f"""请分析以下文章的元信息：

---
标题：{title}
作者：{author}
发布时间：{publish_date}
语言：{language}
句子总数：{len(sentences)}

文章句子列表：
{sentence_list}
---

**注意**: 文章已拆分为带编号的句子列表，请直接引用句子编号（如 [5]）而不是搜索文本位置。

请按照系统提示中的JSON schema输出分析结果。"""

    def _format_response(self, meta_analysis: MetaAnalysis) -> Dict:
        """格式化响应"""
        # 解析raw_llm_response以获取generated_title
        generated_title = None
        try:
            if meta_analysis.raw_llm_response:
                raw_data = json.loads(meta_analysis.raw_llm_response)
                generated_title = raw_data.get('generated_title')
        except:
            pass

        return {
            "id": meta_analysis.id,
            "article_id": meta_analysis.article_id,
            "generated_title": generated_title,  # 添加AI生成的标题
            "author_intent": meta_analysis.author_intent,
            "timeliness_score": meta_analysis.timeliness_score,
            "timeliness_analysis": meta_analysis.timeliness_analysis,
            "bias_analysis": meta_analysis.bias_analysis,
            "knowledge_gaps": meta_analysis.knowledge_gaps,
            "analysis_quality": meta_analysis.analysis_quality,
            "created_at": meta_analysis.created_at.isoformat(),
            "updated_at": meta_analysis.updated_at.isoformat()
        }

    def get_meta_analysis(self, article_id: int) -> Optional[Dict]:
        """获取元信息分析结果"""
        meta_analysis = self.db.query(MetaAnalysis).filter(
            MetaAnalysis.article_id == article_id
        ).first()

        if not meta_analysis:
            return None

        return self._format_response(meta_analysis)
