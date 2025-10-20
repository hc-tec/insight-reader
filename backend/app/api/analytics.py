"""分析统计 (Analytics) 相关 API 端点"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


class SparkClickRequest(BaseModel):
    """火花点击请求"""
    user_id: int
    spark_type: str  # concept / argument
    spark_text: str
    article_id: Optional[int] = None


@router.post("/spark-click")
async def record_spark_click(
    request: SparkClickRequest,
    db: Session = Depends(get_db)
):
    """
    记录火花点击事件

    Args:
        request: 点击事件数据

    Returns:
        成功消息
    """
    try:
        service = AnalyticsService(db)
        click = service.record_spark_click(
            user_id=request.user_id,
            spark_type=request.spark_type,
            spark_text=request.spark_text,
            article_id=request.article_id
        )

        return {
            "success": True,
            "clickId": click.id,
            "message": "火花点击已记录"
        }

    except Exception as e:
        print(f"❌ 火花点击记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spark-stats")
async def get_spark_stats(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取火花统计数据

    Args:
        user_id: 用户 ID
        days: 统计天数（默认 30 天）

    Returns:
        统计数据
    """
    try:
        service = AnalyticsService(db)
        return service.get_spark_stats(user_id, days)

    except Exception as e:
        print(f"❌ 火花统计获取失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
