"""用户相关的数据模型 - 无密码设计"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class MagicLinkRequest(BaseModel):
    """魔法链接请求"""
    email: EmailStr


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    email: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    created_at: datetime
    last_login: datetime
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token数据"""
    user_id: Optional[int] = None
