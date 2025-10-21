# -*- coding: utf-8 -*-
"""
统一深度分析服务 (Unified Deep Analysis Service)
使用 GPT-4o 对文章进行全面深度分析，生成结构化报告
"""

from openai import OpenAI
from app.config import settings
from app.utils.sentence_splitter import split_sentences
from app.utils.error_logger import log_llm_error
import json
import json_repair
import re
import time
from typing import List, Dict, Optional


class UnifiedAnalysisService:
    """统一深度分析服务"""

    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.default_model

    async def analyze_article(self, article_content: str, article_title: str = "") -> Dict:
        """
        执行文章的统一深度分析

        Args:
            article_content: 文章内容
            article_title: 文章标题（可选）

        Returns:
            包含报告和元数据的字典：
            {
                "report": {...},  # 分析报告 JSON
                "metadata": {
                    "model": str,
                    "tokens": int,
                    "processing_time_ms": int
                }
            }
        """
        start_time = time.time()

        # 1. 预处理：分句
        sentences = self._split_sentences(article_content)
        print(f"📄 文章分句完成，共 {len(sentences)} 个句子")

        # 2. 构建 Prompt（传递句子列表而非原始内容）
        prompt = self._build_analysis_prompt(sentences, article_title)

        # 3. 调用 LLM
        print("🤖 开始调用 LLM 进行深度分析...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一名世界级的跨学科研究分析师，拥有深厚的批判性思维能力和教育心理学背景。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
        except Exception as e:
            # 记录LLM调用错误
            log_llm_error(
                service_name="unified_analysis",
                model_name=self.model,
                error=e,
                request_data={
                    "article_title": article_title,
                    "sentence_count": len(sentences),
                    "prompt_length": len(prompt)
                }
            )
            print(f"❌ LLM 调用失败: {e}")
            raise

        # 4. 解析响应
        try:
            # 先尝试使用json_repair修复可能的JSON格式错误
            raw_content = response.choices[0].message.content
            report_json = json_repair.repair_json(raw_content, return_objects=True, ensure_ascii=False)
            print("✅ JSON解析成功（使用json_repair）")
        except Exception as e:
            # 记录JSON解析错误
            log_llm_error(
                service_name="unified_analysis",
                model_name=self.model,
                error=e,
                request_data={
                    "response_content": response.choices[0].message.content[:500]  # 只记录前500字符
                }
            )
            print(f"❌ JSON 解析失败: {e}")
            raise

        # 5. 后处理：添加 DOM 路径
        report_json = self._add_dom_paths(report_json, sentences)

        # 6. 添加分句结果到报告（供前端使用）
        report_json['sentences'] = sentences
        print(f"✅ 已将 {len(sentences)} 个句子添加到报告")

        # 7. 验证报告
        self._validate_report(report_json)
        print("✅ 报告验证通过")

        # 8. 计算处理时间
        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "report": report_json,
            "metadata": {
                "model": response.model,
                "tokens": response.usage.total_tokens,
                "processing_time_ms": processing_time_ms
            }
        }

    def _split_sentences(self, text: str) -> List[str]:
        """
        智能分句

        使用正则表达式将文章拆分成句子列表。

        Args:
            text: 原始文本

        Returns:
            句子列表
        """
        return split_sentences(text)

    def _build_analysis_prompt(self, sentences: List[str], title: str) -> str:
        """
        构建分析 Prompt

        Args:
            sentences: 句子列表（已分句）
            title: 文章标题

        Returns:
            完整的 Prompt 字符串
        """
        # 格式化句子列表：每句一行，带编号
        sentence_list = "\n".join([f"[{i}] {sentence}" for i, sentence in enumerate(sentences)])
        prompt = f"""# 任务目标

对以下文章进行全面的深度分析，并严格按照指定的 JSON Schema 返回结果。

# 文章信息

标题：{title if title else "（无标题）"}
句子总数：{len(sentences)}

# 文章句子列表

以下是文章的完整句子列表，每句都有唯一编号。**请直接使用句子编号（如 [5]）来定位句子，不要搜索句子文本。**

{sentence_list}

# 分析维度

## 1. 元信息分析 (meta_info)

分析以下维度：
- **author_stance**: 作者立场（客观/主观/批判性/辩护性）
- **writing_intent**: 写作意图��教育/说服/娱乐/记录）
- **emotional_tone**: 情感基调（中性/激昂/冷静/讽刺）
- **target_audience**: 目标读者（专业人士/普通大众/学生）
- **timeliness**: 时效性（时效性强/长期有效）

## 2. 核心概念提炼 (concept_sparks)

**严格标准**：
- 仅选择理解本文**核心论点**所必需的概念
- 概念必须是**读者可能陌生**的专业术语或抽象概念
- 数量限制：**3-7 个**
- 质量优先于数量：宁缺毋滥

**重要**：请直接使用上方句子列表中的编号（如 [5]），不要尝试搜索句子文本位置。

对于每个概念，提供：
```json
{{
  "text": "概念原文",
  "sentence_index": 5,  // 直接使用句子列表中的编号（从 0 开始）
  "importance_score": 9,  // 1-10 分
  "explanation_hint": "用一个日常生活中的例子解释该概念，并说明它为何重要。"
}}
```

## 3. 论证结构分析 (argument_sparks)

识别文章中的关键论证元素：
- **核心观点句** (claim): 作者的主要论点
- **支撑证据句** (evidence): 数据、案例、引用
- **关键转折句** (transition): "然而"、"事实上"等转折

**重要**：直接引用句子列表中的编号，无需搜索文本。

对于每个论证点，提供：
```json
{{
  "type": "claim",  // claim / evidence / transition
  "text": "句子原文（从句子列表中复制）",
  "sentence_index": 3,  // 直接使用句子列表中的编号
  "role_description": "这句话在论证中的作用"
}}
```

## 4. 知识图谱节点 (knowledge_graph_nodes)

提取 5-10 个可以构建知识网络的核心概念（字符串数组）。

## 5. 文章摘要与标签

- `summary`: 150 字左右的核心摘要
- `tags`: 3-5 个主题标签

# 输出格式

严格按照以下 JSON 格式返回结果：

```json
{{
  "meta_info": {{
    "author_stance": "批判性",
    "writing_intent": "教育",
    "emotional_tone": "冷静",
    "target_audience": "普通大众",
    "timeliness": "长期有效"
  }},
  "concept_sparks": [
    {{
      "text": "元信息",
      "sentence_index": 5,
      "importance_score": 9,
      "explanation_hint": "用一个日常生活中的例子解释'元信息'的概念。"
    }}
  ],
  "argument_sparks": [
    {{
      "type": "claim",
      "text": "元信息思维是高效学习的核心能力。",
      "sentence_index": 3,
      "role_description": "文章核心论点"
    }}
  ],
  "knowledge_graph_nodes": ["元信息", "批判性思维", "认知闭环"],
  "summary": "本文探讨了...",
  "tags": ["思维模型", "学习方法", "批判性思维"]
}}
```

# 质量要求

1. **精准性**: 所有引用的文本必须与句子列表中的原文完全一致
2. **可定位性**: sentence_index 必须直接使用句子列表中的编号（从 0 开始计数），不要搜索文本位置
3. **价值导向**: 只标注真正有价值的内容
4. **结构化**: 严格遵守 JSON 格式

**特别提醒**：为避免幻觉，请务必直接从句子列表中复制句子编号，不要尝试自行计算或搜索位置。
"""
        return prompt

    def _add_dom_paths(self, report: Dict, sentences: List[str]) -> Dict:
        """
        为每个火花添加 DOM 路径

        Args:
            report: 原始报告
            sentences: 句子列表

        Returns:
            添加了 DOM 路径的报告
        """
        # 为概念火花添加 DOM 路径
        for spark in report.get('concept_sparks', []):
            idx = spark['sentence_index']
            spark['dom_path'] = f"#sentence-{idx}"

        # 为论证火花添加 DOM 路径
        for spark in report.get('argument_sparks', []):
            idx = spark['sentence_index']
            spark['dom_path'] = f"#sentence-{idx}"

        return report

    def _validate_report(self, report: Dict):
        """
        验证报告结构

        Args:
            report: 分析报告

        Raises:
            ValueError: 如果报告结构不符合要求
        """
        # 必需字段
        required_fields = ['meta_info', 'concept_sparks', 'summary', 'tags']
        for field in required_fields:
            if field not in report:
                raise ValueError(f"缺少必需字段: {field}")

        # 验证 meta_info
        meta_info = report['meta_info']
        required_meta_fields = ['author_stance', 'writing_intent', 'emotional_tone', 'target_audience', 'timeliness']
        for field in required_meta_fields:
            if field not in meta_info:
                raise ValueError(f"meta_info 缺少字段: {field}")

        # 验证概念火花
        for i, spark in enumerate(report['concept_sparks']):
            required_spark_fields = ['text', 'sentence_index', 'importance_score', 'explanation_hint']
            for field in required_spark_fields:
                if field not in spark:
                    raise ValueError(f"concept_sparks[{i}] 缺少字段: {field}")

        # 验证标签数量
        tags = report['tags']
        if not isinstance(tags, list) or len(tags) < 3 or len(tags) > 5:
            raise ValueError(f"tags 数量应在 3-5 个之间，当前: {len(tags)}")

        print(f"✅ 报告验证通过：{len(report['concept_sparks'])} 个概念火花，{len(report.get('argument_sparks', []))} 个论证火花")
