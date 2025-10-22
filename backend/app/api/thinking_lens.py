"""
思维透镜 API 路由（异步版本）
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, SessionLocal
from app.services.thinking_lens_service import ThinkingLensService
from app.services.meta_analysis_service import MetaAnalysisService
from app.models.models import Article, MetaAnalysis
from app.core.task_manager import task_manager
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()


# ============= 后台任务函数 =============

async def thinking_lens_task(
    meta_analysis_id: int,
    lens_type: str,
    full_text: str,
    language: str
):
    """
    后台思维透镜分析任务

    Args:
        meta_analysis_id: 元分析ID
        lens_type: 透镜类型
        full_text: 全文
        language: 语言

    Returns:
        分析结果
    """
    db = SessionLocal()

    try:
        logger.info(f"[后台任务] 开始思维透镜分析，类型: {lens_type}, 元分析ID: {meta_analysis_id}")

        service = ThinkingLensService(db)

        result = await service.apply_lens(
            meta_analysis_id=meta_analysis_id,
            lens_type=lens_type,
            full_text=full_text,
            language=language,
            force_reanalyze=False
        )

        logger.info(f"[后台任务] 思维透镜分析完成，类型: {lens_type}")

        return {
            "lens_type": lens_type,
            "status": "completed",
            "lens_result": result
        }

    except Exception as e:
        logger.error(f"[后台任务] 思维透镜分析失败，类型: {lens_type}, 错误: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()


class ApplyLensRequest(BaseModel):
    meta_analysis_id: int
    lens_type: str  # 'argument_structure' | 'author_stance'
    full_text: str
    language: str = "zh"
    force_reanalyze: bool = False


@router.post("/api/v1/thinking-lens/apply")
async def apply_lens(
    request: ApplyLensRequest,
    db: Session = Depends(get_db)
):
    """
    应用思维透镜

    Args:
        request: 透镜请求
        db: 数据库会话

    Returns:
        透镜分析结果
    """

    # 验证 lens_type
    valid_types = ['argument_structure', 'author_stance']
    if request.lens_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的透镜类型。支持的类型: {', '.join(valid_types)}"
        )

    service = ThinkingLensService(db)

    try:
        result = await service.apply_lens(
            meta_analysis_id=request.meta_analysis_id,
            lens_type=request.lens_type,
            full_text=request.full_text,
            language=request.language,
            force_reanalyze=request.force_reanalyze
        )

        return {
            "status": "success",
            "lens_result": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"透镜分析失败: {str(e)}")


@router.get("/api/v1/thinking-lens/{meta_analysis_id}/{lens_type}")
async def get_lens_result(
    meta_analysis_id: int,
    lens_type: str,
    db: Session = Depends(get_db)
):
    """
    获取透镜分析结果

    Args:
        meta_analysis_id: 元信息分析ID
        lens_type: 透镜类型
        db: 数据库会话

    Returns:
        透镜分析结果或null
    """

    # 验证 lens_type
    valid_types = ['argument_structure', 'author_stance']
    if lens_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的透镜类型。支持的类型: {', '.join(valid_types)}"
        )

    service = ThinkingLensService(db)
    result = service.get_lens_result(meta_analysis_id, lens_type)

    if result is None:
        return {
            "exists": False,
            "lens_result": None
        }

    return {
        "exists": True,
        "lens_result": result
    }


@router.get("/api/v1/articles/{article_id}/thinking-lens/{lens_type}")
async def get_lens_by_article(
    article_id: int,
    lens_type: str,
    force_reanalyze: bool = False,
    db: Session = Depends(get_db)
):
    """
    通过文章ID获取或生成透镜分析结果（异步版本）

    工作流程：
    1. 获取文章
    2. 确保有 meta_analysis 记录
    3. 检查是否已有透镜结果
    4. 没有则提交后台分析任务
    5. 通过SSE通知前端分析完成

    Args:
        article_id: 文章ID
        lens_type: 透镜类型 ('argument_structure' | 'author_stance')
        force_reanalyze: 是否强制重新分析
        db: 数据库会话

    Returns:
        {
            "status": "completed" | "pending",
            "lens_result": dict | null,
            "task_id": str | null
        }
    """
    # 验证 lens_type
    valid_types = ['argument_structure', 'author_stance']
    if lens_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"无效的透镜类型。支持的类型: {', '.join(valid_types)}"
        )

    # 1. 获取文章
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 2. 确保有 meta_analysis 记录
    meta_analysis = db.query(MetaAnalysis).filter(
        MetaAnalysis.article_id == article_id
    ).first()

    if not meta_analysis:
        # 需要先进行元视角分析
        raise HTTPException(
            status_code=400,
            detail="需要先进行元视角分析。请先调用元视角分析接口。"
        )

    meta_analysis_id = meta_analysis.id

    # 3. 检查是否已有透镜结果
    if not force_reanalyze:
        lens_service = ThinkingLensService(db)
        existing_result = lens_service.get_lens_result(meta_analysis_id, lens_type)

        if existing_result:
            logger.info(f"[API] 思维透镜结果已存在，文章ID: {article_id}, 类型: {lens_type}")
            return {
                "status": "completed",
                "lens_result": existing_result,
                "task_id": None
            }

    # 4. 提交异步透镜分析任务
    task_id = task_manager.submit_task(
        f"thinking_lens_{lens_type}",
        thinking_lens_task,
        {
            "article_id": article_id,
            "meta_analysis_id": meta_analysis_id,
            "lens_type": lens_type,
            "user_id": article.user_id
        },
        meta_analysis_id,
        lens_type,
        article.content,
        article.language or "zh"
    )

    logger.info(f"[API] 思维透镜任务已提交，文章ID: {article_id}, 类型: {lens_type}, 任务ID: {task_id}")

    return {
        "status": "pending",
        "lens_result": None,
        "task_id": task_id
    }
