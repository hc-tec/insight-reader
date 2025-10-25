"""Pydantic 数据模型"""
from pydantic import BaseModel, Field


class InsightRequest(BaseModel):
    """洞察生成请求"""

    selected_text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="用户选中的文本"
    )
    context: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="选中文本的上下文"
    )
    intent: str = Field(
        ...,
        pattern="^(explain|analyze|counter|custom)$",
        description="用户意图: explain(解释) | analyze(分析) | counter(反驳) | custom(自定义)"
    )
    custom_question: str | None = Field(
        None,
        max_length=200,
        description="用户自定义问题（V2.0）"
    )
    use_reasoning: bool = Field(
        False,
        description="是否使用推理模型（支持思维链）"
    )
    include_full_text: bool = Field(
        False,
        description="是否附带全文内容（用于更深入的分析）"
    )
    full_text: str | None = Field(
        None,
        max_length=50000,
        description="完整文章内容（当include_full_text为true时提供）"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "selected_text": "康德的绝对命令",
                    "context": "在伦理学中，康德的绝对命令是一个核心概念。它要求我们的行为准则能够成为普遍法则。",
                    "intent": "explain",
                    "use_reasoning": False,
                    "include_full_text": False
                }
            ]
        }
    }


class InsightMetadata(BaseModel):
    """洞察元数据"""

    model: str = Field(..., description="使用的AI模型")
    tokens: int = Field(..., description="消耗的token数")
    duration_ms: int = Field(..., description="生成耗时(毫秒)")


class Message(BaseModel):
    """对话消息"""

    role: str = Field(..., pattern="^(user|assistant)$", description="角色: user | assistant")
    content: str = Field(..., min_length=1, description="消息内容")
    reasoning: str | None = Field(None, description="推理内容（仅assistant角色）")
    timestamp: int | None = Field(None, description="时间戳(毫秒)")


class FollowUpButton(BaseModel):
    """追问按钮"""

    id: str = Field(..., description="按钮ID")
    label: str = Field(..., min_length=1, max_length=50, description="按钮文字")
    icon: str = Field(default="💬", description="按钮图标(emoji)")
    category: str = Field(
        ...,
        pattern="^(example|simplify|compare|extend)$",
        description="按钮分类: example(举例) | simplify(简化) | compare(对比) | extend(延伸)"
    )


class ButtonGenerationRequest(BaseModel):
    """生成追问按钮的请求"""

    selected_text: str = Field(..., min_length=1, max_length=500, description="选中的文本")
    insight: str = Field(..., min_length=1, description="当前洞察内容")
    intent: str = Field(..., pattern="^(explain|analyze|counter)$", description="原始意图")
    conversation_history: list[Message] = Field(default_factory=list, description="对话历史")


class ButtonGenerationResponse(BaseModel):
    """生成追问按钮的响应"""

    buttons: list[FollowUpButton] = Field(..., min_items=2, max_items=4, description="追问按钮列表")


class FollowUpRequest(BaseModel):
    """追问请求"""

    selected_text: str = Field(..., min_length=1, max_length=500, description="原始选中文本")
    initial_insight: str = Field(..., min_length=1, description="初始洞察内容")
    conversation_history: list[Message] = Field(default_factory=list, description="对话历史")
    follow_up_question: str = Field(..., min_length=1, max_length=200, description="追问问题")
    use_reasoning: bool = Field(False, description="是否使用推理模型")
