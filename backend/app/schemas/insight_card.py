"""洞察卡片相关的数据模型"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class InsightCardCreate(BaseModel):
    """创建洞察卡片请求"""
    article_title: Optional[str] = None
    article_content: Optional[str] = None
    selected_text: str
    context: Optional[str] = None
    intent: str = Field(..., pattern="^(explain|analyze|counter)$")
    custom_question: Optional[str] = None
    insight: str
    model_used: Optional[str] = None
    tokens: Optional[int] = None
    tags: Optional[List[str]] = None


class InsightCardUpdate(BaseModel):
    """更新洞察卡片请求"""
    tags: Optional[List[str]] = None


class InsightCardResponse(BaseModel):
    """洞察卡片响应"""
    id: int
    user_id: int
    article_title: Optional[str]
    selected_text: str
    context: Optional[str]
    intent: str
    custom_question: Optional[str]
    insight: str
    model_used: Optional[str]
    tokens: Optional[int]
    created_at: datetime
    tags: Optional[List[str]]

    class Config:
        from_attributes = True


class InsightCardListResponse(BaseModel):
    """洞察卡片列表响应"""
    total: int
    items: List[InsightCardResponse]
