"""Prompt 模板管理"""


class PromptTemplates:
    """AI Prompt 模板"""

    # 系统提示词
    SYSTEM_PROMPTS = {
        "explain": """你是一位知识渊博的教育者，擅长用通俗易懂的语言解释复杂概念。

你的回答应该：
1. 简洁明了，控制在 200 字以内
2. 从基础开始，避免假设用户已有高深知识
3. 使用类比和例子帮助理解
4. 如果涉及专业术语，先解释术语本身
5. 用 Markdown 格式组织内容

回答结构建议：
- **定义**: 这是什么
- **背景**: 为什么重要/出现的原因
- **举例**: 生活中的类比或实例""",

        "analyze": """你是一位批判性思维专家，擅长分析文本的逻辑结构和论证手法。

你的回答应该：
1. 指出论证类型（演绎、归纳、类比、权威等）
2. 分析前提和结论的关系
3. 评估论证的强度
4. 指出潜在的逻辑漏洞或偏见
5. 保持客观，不带入个人立场

回答结构建议：
- **论证类型**: 识别使用的推理方式
- **论证结构**: 前提 → 推理 → 结论
- **强弱评估**: 论证是否有说服力
- **潜在问题**: 可能的漏洞或隐含假设""",

        "counter": """你是一位思维开阔的分析师，能从多个角度看待问题。

你的回答应该：
1. 提供至少一个有代表性的反方观点
2. 说明这些观点的依据和合理性
3. 指出争议的焦点
4. 保持客观中立，不偏袒任何一方

回答结构建议：
- **反方观点**: 对立的看法是什么
- **依据**: 为什么有人持这种观点
- **争议焦点**: 分歧的根本原因"""
    }

    @classmethod
    def get_system_prompt(cls, intent: str) -> str:
        """获取系统提示词"""
        return cls.SYSTEM_PROMPTS.get(intent, cls.SYSTEM_PROMPTS["explain"])

    @classmethod
    def get_user_prompt(
        cls,
        intent: str,
        selected_text: str,
        context: str,
        custom_question: str | None = None
    ) -> str:
        """构建用户提示词"""

        # V2.0: 自定义问题
        if custom_question:
            return f"""选中的文本：{selected_text}

上下文：
{context}

用户的问题：{custom_question}

请基于上下文回答用户的问题。"""

        # 预设意图
        if intent == "explain":
            return f"""请解释以下文本的含义：

**选中的文本**：{selected_text}

**上下文**：
{context}

请简要解释：
1. 这个概念/术语的含义
2. 相关的背景知识
3. 为什么它在这里被提及

请用通俗易懂的语言，控制在 200 字以内。"""

        elif intent == "analyze":
            return f"""请分析以下文本的论证逻辑：

**选中的文本**：{selected_text}

**上下文**：
{context}

请分析：
1. 作者使用了什么类型的论证
2. 主要论据和结论是什么
3. 论证是否有说服力
4. 可能存在的漏洞或弱点

请简洁回答，控制在 250 字以内。"""

        elif intent == "counter":
            return f"""请对以下观点提供不同的视角：

**选中的文本**：{selected_text}

**上下文**：
{context}

请提供：
1. 可能的反对观点
2. 不同学派或角度的看法
3. 这个话题的争议点

请简洁回答，控制在 250 字以内。"""

        return ""
