"""AI 服务 - OpenAI API 集成"""
from openai import AsyncOpenAI
from app.config import settings
from app.utils.prompt_templates import PromptTemplates
from app.schemas.insight import FollowUpButton, Message
from app.utils.error_logger import log_llm_error
import json
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务类"""

    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model_used = ""

    def select_model(self, intent: str, text_length: int, use_reasoning: bool = False) -> str:
        """
        根据意图和文本长度选择合适的模型

        Args:
            intent: 用户意图
            text_length: 选中文本长度
            use_reasoning: 是否使用推理模型

        Returns:
            模型名称
        """
        # 如果启用推理模式，使用支持推理的模型
        if use_reasoning:
            return settings.reasoning_model  # 例如 deepseek-reasoner

        # 简单解释 + 短文本 → gpt-4o-mini (便宜快速)
        if intent == "explain" and text_length < 10:
            return settings.simple_model

        # 默认使用 gpt-4o (质量优先)
        return settings.default_model

    async def generate_insight_stream(
        self,
        selected_text: str,
        context: str,
        intent: str,
        custom_question: str | None = None,
        use_reasoning: bool = False,
        custom_prompt: str | None = None,
        include_full_text: bool = False,
        full_text: str | None = None
    ):
        """
        流式生成洞察

        Args:
            selected_text: 用户选中的文本
            context: 上下文
            intent: 用户意图
            custom_question: 自定义问题(可选)
            use_reasoning: 是否使用推理模型
            custom_prompt: 自定义 prompt (用于火花洞察等特殊场景)
            include_full_text: 是否附带全文
            full_text: 完整文章内容(可选)

        Yields:
            str | dict: AI 生成的文本片段或包含推理内容的字典
        """
        # 选择模型
        self.model_used = self.select_model(intent, len(selected_text), use_reasoning)

        # 构建 Prompt
        if custom_prompt:
            # 使用自定义 prompt (火花洞察场景)
            system_prompt = "你是一个专业的阅读辅助 AI，帮助用户深入理解文章内容。"
            user_prompt = custom_prompt
        else:
            # 使用标准 prompt 模板
            system_prompt = PromptTemplates.get_system_prompt(intent)
            user_prompt = PromptTemplates.get_user_prompt(
                intent=intent,
                selected_text=selected_text,
                context=context,
                custom_question=custom_question,
                include_full_text=include_full_text,
                full_text=full_text
            )

        # 调用 OpenAI API (流式)
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_used,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta

                    # 支持推理模式
                    if use_reasoning:
                        result = {}
                        # DeepSeek 推理模型会有 reasoning_content 字段
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            result['reasoning'] = delta.reasoning_content
                        if delta.content:
                            result['content'] = delta.content

                        if result:  # 只在有内容时返回
                            yield result
                    else:
                        # 非推理模式，直接返回内容
                        if delta.content:
                            yield delta.content
        except Exception as e:
            # 记录LLM调用错误
            log_llm_error(
                service_name="ai_service_generate_insight",
                model_name=self.model_used,
                error=e,
                request_data={
                    "intent": intent,
                    "selected_text_length": len(selected_text),
                    "use_reasoning": use_reasoning
                }
            )
            logger.error(f"❌ LLM 调用失败: {e}")
            raise

    async def generate_follow_up_buttons(
        self,
        selected_text: str,
        insight: str,
        intent: str,
        conversation_history: list[Message]
    ) -> list[FollowUpButton]:
        """
        生成智能追问按钮

        Args:
            selected_text: 原始选中文本
            insight: 当前洞察内容
            intent: 原始意图
            conversation_history: 对话历史

        Returns:
            追问按钮列表（3-4个）
        """
        # 构建对话历史字符串
        history_str = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # 只取最近5轮
                role_label = "用户" if msg.role == "user" else "AI"
                history_str += f"{role_label}: {msg.content}\n"

        # 构建 prompt
        system_prompt = """你是一个智能学习助手。根据用户当前的学习内容和对话历史，生成3-4个最有价值的追问建议。

追问分类：
- example: 举例说明，帮助理解抽象概念
- simplify: 用更简单的方式解释
- compare: 对比相关概念，理解区别
- extend: 延伸阅读，深入学习

要求：
1. 追问要具体、有价值，不能太泛泛
2. 避免重复之前已经追问过的内容
3. 问题要简短（5-15字）
4. 返回纯 JSON 格式，不要有其他文字"""

        user_prompt = f"""原始选中文本: {selected_text}

当前洞察: {insight}

原始意图: {intent}

对话历史:
{history_str if history_str else "（无）"}

请生成3-4个追问建议，JSON格式如下：
[
  {{"id": "example_1", "label": "举个实际例子", "icon": "🌰", "category": "example"}},
  {{"id": "simplify_1", "label": "说得更简单点", "icon": "🎯", "category": "simplify"}},
  {{"id": "compare_1", "label": "和XX的区别？", "icon": "🔍", "category": "compare"}}
]"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.simple_model,  # 使用快速模型生成按钮
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # 解析 JSON
            try:
                buttons_data = json.loads(content)
            except json.JSONDecodeError as e:
                # 记录JSON解析错误
                log_llm_error(
                    service_name="ai_service_follow_up_buttons",
                    model_name=settings.simple_model,
                    error=e,
                    request_data={
                        "response_content": content[:500]
                    }
                )
                logger.error(f"❌ JSON 解析失败: {e}")
                raise

            # 转换为 FollowUpButton 对象
            buttons = [FollowUpButton(**btn) for btn in buttons_data]

            return buttons[:4]  # 最多返回4个

        except json.JSONDecodeError:
            # JSON解析错误已经在内部try-catch处理，这里直接返回默认按钮
            logger.warning("JSON解析失败，返回默认按钮")
            return [
                FollowUpButton(
                    id="example_default",
                    label="举个例子",
                    icon="🌰",
                    category="example"
                ),
                FollowUpButton(
                    id="simplify_default",
                    label="说得简单点",
                    icon="🎯",
                    category="simplify"
                )
            ]
        except Exception as e:
            # 记录LLM调用错误
            log_llm_error(
                service_name="ai_service_follow_up_buttons",
                model_name=settings.simple_model,
                error=e,
                request_data={
                    "selected_text_length": len(selected_text),
                    "insight_length": len(insight),
                    "intent": intent
                }
            )
            logger.error(f"❌ 生成追问按钮失败: {e}")
            # 返回默认按钮
            return [
                FollowUpButton(
                    id="example_default",
                    label="举个例子",
                    icon="🌰",
                    category="example"
                ),
                FollowUpButton(
                    id="simplify_default",
                    label="说得简单点",
                    icon="🎯",
                    category="simplify"
                )
            ]

    async def generate_follow_up_answer_stream(
        self,
        selected_text: str,
        initial_insight: str,
        conversation_history: list[Message],
        follow_up_question: str,
        use_reasoning: bool = False
    ):
        """
        流式生成追问的回答

        Args:
            selected_text: 原始选中文本
            initial_insight: 初始洞察内容
            conversation_history: 对话历史
            follow_up_question: 追问问题
            use_reasoning: 是否使用推理模型

        Yields:
            str | dict: AI 生成的文本片段或包含推理内容的字典
        """
        # 选择模型
        self.model_used = settings.reasoning_model if use_reasoning else settings.default_model

        # 构建消息列表
        messages = [
            {
                "role": "system",
                "content": "你是一个耐心的学习助手。用户正在深入理解某个概念，你需要根据对话历史，回答他的追问。"
            },
            {
                "role": "user",
                "content": f"原始文本: {selected_text}\n\n初始洞察: {initial_insight}"
            }
        ]

        # 添加对话历史
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 添加当前追问
        messages.append({
            "role": "user",
            "content": follow_up_question
        })

        # 调用 API
        try:
            stream = await self.client.chat.completions.create(
                model=self.model_used,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                messages=messages,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta

                    # 支持推理模式
                    if use_reasoning:
                        result = {}
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                            result['reasoning'] = delta.reasoning_content
                        if delta.content:
                            result['content'] = delta.content

                        if result:
                            yield result
                    else:
                        if delta.content:
                            yield delta.content

        except Exception as e:
            # 记录LLM调用错误
            log_llm_error(
                service_name="ai_service_follow_up_answer",
                model_name=self.model_used,
                error=e,
                request_data={
                    "selected_text_length": len(selected_text),
                    "follow_up_question": follow_up_question,
                    "use_reasoning": use_reasoning,
                    "conversation_history_length": len(conversation_history)
                }
            )
            logger.error(f"❌ 生成追问回答失败: {e}")
            raise

    async def generate_simple_response(self, prompt: str) -> str:
        """
        生成简单响应（非流式）

        用于火花解释等简单场景

        Args:
            prompt: 完整的提示词

        Returns:
            AI 生成的文本响应
        """
        try:
            response = await self.client.chat.completions.create(
                model=settings.default_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            # 记录LLM调用错误
            log_llm_error(
                service_name="ai_service_simple_response",
                model_name=settings.default_model,
                error=e,
                request_data={
                    "prompt_length": len(prompt)
                }
            )
            logger.error(f"❌ 生成简单响应失败: {e}")
            raise
