"""仪表盘 (Dashboard) 相关 API 端点"""
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict

from app.db.database import get_db
from app.models.models import User
from app.utils.auth import get_current_active_user
from app.services.analytics_service import AnalyticsService
from app.services.knowledge_graph_service import KnowledgeGraphService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取仪表盘总览

    Args:
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        仪表盘总览数据
    """
    try:
        analytics_service = AnalyticsService(db)
        graph_service = KnowledgeGraphService(db)

        # 获取知识图谱统计
        graph_data = graph_service.get_knowledge_graph(current_user.id)

        # 获取好奇心指纹
        fingerprint = analytics_service.get_curiosity_fingerprint(current_user.id)

        # 获取火花统计
        spark_stats = analytics_service.get_spark_stats(current_user.id, days=30)

        # 获取盲区
        blind_spots = graph_service.get_blind_spots(current_user.id)

        return {
            "knowledgeGraph": {
                "totalNodes": graph_data["stats"]["totalNodes"],
                "totalEdges": graph_data["stats"]["totalEdges"],
                "domains": graph_data["stats"]["domains"]
            },
            "curiosityFingerprint": {
                "sparkDistribution": fingerprint["spark_distribution"],
                "dominantType": spark_stats["dominant_type"]
            },
            "blindSpots": {
                "missingDomains": blind_spots["missingDomains"],
                "knowledgeIslands": len(blind_spots["knowledgeIslands"])
            },
            "stats": {
                "totalSparkClicks": spark_stats["total_clicks"],
                "activeDays": 30
            }
        }

    except Exception as e:
        logger.error(f" 仪表盘总览获取失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-graph")
async def get_knowledge_graph(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取用户的知识图谱数据

    Args:
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        知识图谱数据（nodes + edges）
    """
    try:
        service = KnowledgeGraphService(db)
        return service.get_knowledge_graph(current_user.id)

    except Exception as e:
        logger.error(f" 知识图谱获取失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge-graph/rebuild")
async def rebuild_knowledge_graph(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    重新构建用户的知识图谱

    Args:
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        构建结果
    """
    try:
        service = KnowledgeGraphService(db)
        result = service.rebuild_graph(current_user.id)
        return result

    except Exception as e:
        logger.error(f" 知识图谱重建失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curiosity-fingerprint")
async def get_curiosity_fingerprint(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取用户的好奇心指纹

    Args:
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        好奇心指纹数据
    """
    try:
        service = AnalyticsService(db)
        return service.get_curiosity_fingerprint(current_user.id)

    except Exception as e:
        logger.error(f" 好奇心指纹获取失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blind-spots")
async def get_blind_spots(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    获取用户的思维盲区

    Args:
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        盲区数据
    """
    try:
        service = KnowledgeGraphService(db)
        return service.get_blind_spots(current_user.id)

    except Exception as e:
        logger.error(f" 盲区检测失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
