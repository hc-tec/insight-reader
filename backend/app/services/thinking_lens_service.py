"""
思维透镜服务
负责应用不同的思维透镜到文章上（论证结构、作者立场）
"""

import logging
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from app.models.models import ThinkingLensResult, MetaAnalysis
from app.config import settings
from app.utils.sentence_splitter import split_sentences
import json
import json_repair
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ThinkingLensService:
    def __init__(self, db: Session):
        self.db = db
        # 使用 settings 中的配置初始化 AsyncOpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url if settings.openai_base_url else None
        )

    async def apply_lens(
        self,
        meta_analysis_id: int,
        lens_type: str,
        full_text: str,
        language: str = "zh",
        force_reanalyze: bool = False
    ) -> Dict:
        """
        应用思维透镜

        Args:
            meta_analysis_id: 元信息分析ID
            lens_type: 透镜类型 ('argument_structure' | 'author_stance')
            full_text: 文章完整文本
            language: 语言
            force_reanalyze: 是否强制重新分析

        Returns:
            透镜分析结果
        """

        # 验证元信息分析是否存在
        meta_analysis = self.db.query(MetaAnalysis).filter(
            MetaAnalysis.id == meta_analysis_id
        ).first()

        if not meta_analysis:
            raise ValueError(f"元信息分析不存在: id={meta_analysis_id}")

        # 检查缓存
        if not force_reanalyze:
            existing = self.db.query(ThinkingLensResult).filter(
                ThinkingLensResult.meta_analysis_id == meta_analysis_id,
                ThinkingLensResult.lens_type == lens_type
            ).first()

            if existing:
                logger.info(f"使用缓存的透镜结果: meta_analysis_id={meta_analysis_id}, lens_type={lens_type}")
                return self._format_response(existing)

        # 执行分析
        logger.info(f"开始透镜分析: lens_type={lens_type}")

        try:
            if lens_type == "argument_structure":
                result = await self._apply_argument_lens(full_text, language)
            elif lens_type == "author_stance":
                result = await self._apply_stance_lens(full_text, language)
            else:
                raise ValueError(f"不支持的透镜类型: {lens_type}")

            # 如果是重新分析，删除旧记录
            if force_reanalyze:
                old_record = self.db.query(ThinkingLensResult).filter(
                    ThinkingLensResult.meta_analysis_id == meta_analysis_id,
                    ThinkingLensResult.lens_type == lens_type
                ).first()
                if old_record:
                    self.db.delete(old_record)
                    self.db.commit()

            # 保存到数据库
            lens_result = ThinkingLensResult(
                meta_analysis_id=meta_analysis_id,
                lens_type=lens_type,
                highlights=result['highlights'],
                annotations=result['annotations']
            )

            self.db.add(lens_result)
            self.db.commit()
            self.db.refresh(lens_result)

            logger.info(f"透镜分析完成: lens_type={lens_type}, highlights_count={len(result['highlights'])}")

            return self._format_response(lens_result)

        except Exception as e:
            logger.error(f"透镜分析失败: lens_type={lens_type}, error={str(e)}")
            self.db.rollback()
            raise

    async def _apply_argument_lens(self, full_text: str, language: str) -> Dict:
        """应用论证结构透镜"""

        # 分句
        sentences = split_sentences(full_text)
        sentence_list = "\n".join([f"[{i}] {sentence}" for i, sentence in enumerate(sentences)])

        system_prompt = """你是一位逻辑分析专家，擅长识别文本中的论证结构。

你的任务是分析文章，标注出：
1. **核心主张 (Claims)**: 作者想要证明或传达的核心观点
2. **支撑证据 (Evidence)**: 用于支持主张的数据、事实、例子、引用等

# 标注规则

- 每个标注必须包含：句子编号、文本片段、类别、提示信息
- 使用句子列表中的编号（从0开始）定位句子
- 主张和证据要形成逻辑对应关系
- 避免标注过短或无意义的句子
- 标注要准确，每个句子只标注一次

# 输出格式

{
  "highlights": [
    {
      "sentence_index": 5,
      "text": "深度学习是机器学习的一个重要分支",
      "category": "claim",
      "color": "#dbeafe",
      "tooltip": "核心主张：定义深度学习"
    },
    {
      "sentence_index": 7,
      "text": "研究表明，深度神经网络在图像识别任务上达到了超越人类的准确率",
      "category": "evidence",
      "color": "#d1fae5",
      "tooltip": "支撑证据：引用研究结果"
    }
  ],
  "annotations": {
    "summary": "文章采用'主张-证据'结构，逻辑清晰",
    "key_insights": [
      "共识别3个核心主张",
      "每个主张都有相应证据支撑",
      "主张-证据比例: 1:1.5"
    ],
    "statistics": {
      "claim_count": 3,
      "evidence_count": 5,
      "claim_to_evidence_ratio": 1.67
    }
  }
}

注意：
- highlights数组中每个对象必须包含sentence_index字段
- sentence_index是句子列表中的编号（从0开始）
- category只能是"claim"或"evidence"
- color固定为: claim="#dbeafe", evidence="#d1fae5"
- 所有文本片段必须与句子列表中的原文完全一致"""

        user_prompt = f"""请分析以下文章的论证结构，标注出核心主张和支撑证据：

句子总数：{len(sentences)}

文章句子列表：
{sentence_list}

**注意**: 文章已拆分为带编号的句子列表，请直接引用句子编号（如 [5]）而不是搜索文本位置。

请输出JSON格式的分析结果。"""

        return await self._call_llm_for_lens(system_prompt, user_prompt)

    async def _apply_stance_lens(self, full_text: str, language: str) -> Dict:
        """应用作者立场透镜"""

        # 分句
        sentences = split_sentences(full_text)
        sentence_list = "\n".join([f"[{i}] {sentence}" for i, sentence in enumerate(sentences)])

        system_prompt = """你是一位语言学专家，擅长区分文本中的主观表达和客观陈述。

你的任务是分析文章，标注出：
1. **主观表达 (Subjective)**: 包含个人观点、价值判断、情感色彩的句子
2. **客观陈述 (Objective)**: 中性描述事实的句子
3. **反讽/讽刺 (Irony)**: 表面意思与实际意图相反的表达（较少见，不确定时不标注）

# 标注规则

- 主观表达的标志：情感词汇、价值判断、模糊限定词（"我认为"、"可能"、"应该"）
- 客观陈述的标志：具体数据、明确事实、中性动词
- 反讽较难识别，需结合语境，不确定时不标注
- 每个句子只标注一次，选择最主要的类别
- 避免过度标注，只标注典型案例

# 输出格式

{
  "highlights": [
    {
      "sentence_index": 10,
      "text": "我认为这项技术将彻底改变我们的生活方式",
      "category": "subjective",
      "color": "#fef3c7",
      "tooltip": "主观判断：个人观点"
    },
    {
      "sentence_index": 12,
      "text": "根据2024年的统计数据，该技术的市场份额增长了35%",
      "category": "objective",
      "color": "#e2e8f0",
      "tooltip": "客观陈述：数据事实"
    }
  ],
  "annotations": {
    "summary": "文章整体较为客观，少量主观表达用于引出观点",
    "key_insights": [
      "主观表达占比约30%",
      "客观陈述占比约70%",
      "作者立场相对中立"
    ],
    "statistics": {
      "subjective_count": 8,
      "objective_count": 18,
      "irony_count": 0,
      "subjectivity_ratio": 0.31
    }
  }
}

注意：
- highlights数组中每个对象必须包含sentence_index字段
- sentence_index是句子列表中的编号（从0开始）
- category只能是"subjective"、"objective"或"irony"
- color固定为: subjective="#fef3c7", objective="#e2e8f0", irony="#fde68a"
- 所有文本片段必须与句子列表中的原文完全一致"""

        user_prompt = f"""请分析以下文章的作者立场，标注出主观表达和客观陈述：

句子总数：{len(sentences)}

文章句子列表：
{sentence_list}

**注意**: 文章已拆分为带编号的句子列表，请直接引用句子编号（如 [5]）而不是搜索文本位置。

请输出JSON格式的分析结果。"""

        return await self._call_llm_for_lens(system_prompt, user_prompt)

    async def _call_llm_for_lens(self, system_prompt: str, user_prompt: str) -> Dict:
        """调用 LLM 进行透镜分析"""

        # 使用 settings 中的配置调用 OpenAI API (异步)
        try:
            response = await self.client.chat.completions.create(
                model=settings.default_model,  # 使用配置中的默认模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,  # 降低温度以提高准确性
                max_tokens=3000
            )
        except Exception as e:
            logger.error(f"LLM调用失败 - thinking_lens - model={settings.default_model}, error={e}")
            raise

        # 解析响应
        try:
            # 先尝试使用json_repair修复可能的JSON格式错误
            raw_content = response.choices[0].message.content
            result = json_repair.repair_json(raw_content, return_objects=True, ensure_ascii=False)
            logger.info("✅ JSON解析成功（使用json_repair）")
        except Exception as e:
            logger.error(f"JSON解析失败 - thinking_lens - model={settings.default_model}, error={e}")
            raise

        # 验证结构
        self._validate_lens_result(result)

        return result

    def _validate_lens_result(self, result: Dict):
        """验证透镜分析结果，并为缺失字段提供默认值"""

        if 'highlights' not in result or not isinstance(result['highlights'], list):
            logger.warning("LLM 输出缺少 highlights 字段或格式错误，使用空数组")
            result['highlights'] = []

        if 'annotations' not in result:
            logger.warning("LLM 输出缺少 annotations 字段，使用默认值")
            result['annotations'] = {
                "summary": "分析完成",
                "key_insights": [],
                "statistics": {}
            }

        # 验证并修复每个高亮
        valid_highlights = []
        for idx, highlight in enumerate(result['highlights']):
            # 检查必需字段，提供默认值
            if 'sentence_index' not in highlight:
                if 'start' in highlight:
                    # 如果有start字段，使用0作为默认sentence_index
                    highlight['sentence_index'] = 0
                    logger.warning(f"高亮 {idx} 缺少 sentence_index，使用默认值 0")
                else:
                    logger.warning(f"高亮 {idx} 缺少 sentence_index 且无法推断，跳过此高亮")
                    continue

            if 'text' not in highlight or not highlight['text']:
                logger.warning(f"高亮 {idx} 缺少 text 字段，跳过此高亮")
                continue

            if 'category' not in highlight:
                logger.warning(f"高亮 {idx} 缺少 category 字段，使用默认值 'claim'")
                highlight['category'] = 'claim'

            if 'color' not in highlight:
                # 根据category提供默认颜色
                default_colors = {
                    'claim': '#dbeafe',
                    'evidence': '#d1fae5',
                    'subjective': '#fef3c7',
                    'objective': '#e2e8f0',
                    'irony': '#fde68a'
                }
                highlight['color'] = default_colors.get(highlight['category'], '#e5e7eb')
                logger.warning(f"高亮 {idx} 缺少 color 字段，使用默认颜色 {highlight['color']}")

            if 'tooltip' not in highlight or not highlight['tooltip']:
                # 根据category提供默认tooltip
                default_tooltips = {
                    'claim': '核心主张',
                    'evidence': '支撑证据',
                    'subjective': '主观表达',
                    'objective': '客观陈述',
                    'irony': '反讽/讽刺'
                }
                highlight['tooltip'] = default_tooltips.get(highlight['category'], '标注内容')
                logger.warning(f"高亮 {idx} 缺少 tooltip 字段，使用默认值 '{highlight['tooltip']}'")

            # 验证sentence_index是数字
            if not isinstance(highlight['sentence_index'], int):
                try:
                    highlight['sentence_index'] = int(highlight['sentence_index'])
                except:
                    logger.warning(f"高亮 {idx} 的sentence_index无法转换为整数，跳过此高亮")
                    continue

            if highlight['sentence_index'] < 0:
                logger.warning(f"高亮 {idx} 的sentence_index为负数，调整为0")
                highlight['sentence_index'] = 0

            # 通过所有验证，添加到有效列表
            valid_highlights.append(highlight)

        # 更新为过滤后的有效高亮列表
        result['highlights'] = valid_highlights
        logger.info(f"验证完成: 原始高亮数={len(result.get('highlights', []))}, 有效高亮数={len(valid_highlights)}")

    def _format_response(self, lens_result: ThinkingLensResult) -> Dict:
        """格式化响应"""
        return {
            "id": lens_result.id,
            "meta_analysis_id": lens_result.meta_analysis_id,
            "lens_type": lens_result.lens_type,
            "highlights": lens_result.highlights,
            "annotations": lens_result.annotations,
            "created_at": lens_result.created_at.isoformat()
        }

    def get_lens_result(
        self,
        meta_analysis_id: int,
        lens_type: str
    ) -> Optional[Dict]:
        """获取透镜分析结果"""

        lens_result = self.db.query(ThinkingLensResult).filter(
            ThinkingLensResult.meta_analysis_id == meta_analysis_id,
            ThinkingLensResult.lens_type == lens_type
        ).first()

        if not lens_result:
            return None

        return self._format_response(lens_result)
