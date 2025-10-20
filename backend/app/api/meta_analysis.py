"""
元信息分析 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.meta_analysis_service import MetaAnalysisService
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class AnalyzeRequest(BaseModel):
    title: str
    author: str = "未知作者"
    publish_date: str = ""
    full_text: str
    user_id: Optional[int] = None  # 可选，支持匿名用户
    source_url: Optional[str] = None
    language: str = "zh"
    force_reanalyze: bool = False


@router.post("/api/v1/meta-analysis/analyze")
async def analyze_article(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    触发元信息分析

    Args:
        request: 分析请求
        db: 数据库会话

    Returns:
        元信息分析结果
    """
    service = MetaAnalysisService(db)

    try:
        result = await service.analyze_article(
            title=request.title,
            author=request.author,
            publish_date=request.publish_date,
            content=request.full_text,
            user_id=request.user_id,
            source_url=request.source_url,
            language=request.language,
            force_reanalyze=request.force_reanalyze
        )

        return {
            "status": "success",
            "message": "分析完成",
            "meta_analysis": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/api/v1/meta-analysis/{article_id}")
async def get_meta_analysis(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    获取元信息分析结果

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        元信息分析结果或null
    """
    service = MetaAnalysisService(db)
    result = service.get_meta_analysis(article_id)

    if result is None:
        return {
            "exists": False,
            "meta_analysis": None
        }

    return {
        "exists": True,
        "meta_analysis": result
    }


class FeedbackRequest(BaseModel):
    user_id: int
    meta_analysis_id: Optional[int] = None
    lens_result_id: Optional[int] = None
    feedback_type: str  # 'meta_info_card' | 'lens_highlight' | 'overall'
    rating: Optional[int] = None  # 1-5
    comment: Optional[str] = None
    feedback_data: Optional[dict] = None


@router.post("/api/v1/meta-analysis/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    提交用户反馈

    Args:
        request: 反馈请求
        db: 数据库会话

    Returns:
        成功消息
    """
    from app.models.models import MetaViewFeedback

    try:
        feedback = MetaViewFeedback(
            user_id=request.user_id,
            meta_analysis_id=request.meta_analysis_id,
            lens_result_id=request.lens_result_id,
            feedback_type=request.feedback_type,
            rating=request.rating,
            comment=request.comment,
            feedback_data=request.feedback_data
        )

        db.add(feedback)
        db.commit()

        return {
            "status": "success",
            "message": "感谢您的反馈！"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")
