"""
用户分析偏好设置 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import UserAnalysisPreferences, User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class PreferencesResponse(BaseModel):
    auto_basic_analysis: bool
    auto_meta_analysis: bool
    auto_argument_lens: bool
    auto_stance_lens: bool


class PreferencesUpdate(BaseModel):
    auto_basic_analysis: Optional[bool] = None
    auto_meta_analysis: Optional[bool] = None
    auto_argument_lens: Optional[bool] = None
    auto_stance_lens: Optional[bool] = None


@router.get("/api/v1/preferences/analysis/{user_id}", response_model=PreferencesResponse)
async def get_analysis_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户的分析偏好设置

    Args:
        user_id: 用户ID
        db: 数据库会话

    Returns:
        用户的分析偏好设置
    """
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取或创建偏好设置
    preferences = db.query(UserAnalysisPreferences).filter(
        UserAnalysisPreferences.user_id == user_id
    ).first()

    if not preferences:
        # 创建默认设置
        preferences = UserAnalysisPreferences(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return PreferencesResponse(
        auto_basic_analysis=preferences.auto_basic_analysis,
        auto_meta_analysis=preferences.auto_meta_analysis,
        auto_argument_lens=preferences.auto_argument_lens,
        auto_stance_lens=preferences.auto_stance_lens
    )


@router.put("/api/v1/preferences/analysis/{user_id}", response_model=PreferencesResponse)
async def update_analysis_preferences(
    user_id: int,
    updates: PreferencesUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户的分析偏好设置

    Args:
        user_id: 用户ID
        updates: 要更新的偏好设置
        db: 数据库会话

    Returns:
        更新后的分析偏好设置
    """
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取或创建偏好设置
    preferences = db.query(UserAnalysisPreferences).filter(
        UserAnalysisPreferences.user_id == user_id
    ).first()

    if not preferences:
        # 创建新的偏好设置
        preferences = UserAnalysisPreferences(user_id=user_id)
        db.add(preferences)

    # 更新字段
    if updates.auto_basic_analysis is not None:
        preferences.auto_basic_analysis = updates.auto_basic_analysis
    if updates.auto_meta_analysis is not None:
        preferences.auto_meta_analysis = updates.auto_meta_analysis
    if updates.auto_argument_lens is not None:
        preferences.auto_argument_lens = updates.auto_argument_lens
    if updates.auto_stance_lens is not None:
        preferences.auto_stance_lens = updates.auto_stance_lens

    try:
        db.commit()
        db.refresh(preferences)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新偏好设置失败: {str(e)}")

    return PreferencesResponse(
        auto_basic_analysis=preferences.auto_basic_analysis,
        auto_meta_analysis=preferences.auto_meta_analysis,
        auto_argument_lens=preferences.auto_argument_lens,
        auto_stance_lens=preferences.auto_stance_lens
    )
