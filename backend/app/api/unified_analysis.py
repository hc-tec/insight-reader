# -*- coding: utf-8 -*-
"""
统一深度分析 API（异步版本 + JWT 认证）
提供文章保存、异步分析触发、报告查询等接口
"""

import logging
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db, SessionLocal
from app.models.models import Article, AnalysisReport, User
from app.services.unified_analysis_service import UnifiedAnalysisService
from app.core.task_manager import task_manager
from app.utils.auth import get_current_active_user, get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter()


class SaveArticleWithAnalysisRequest(BaseModel):
    """保存文章并触发分析的请求"""
    title: str
    author: Optional[str] = None
    source_url: Optional[str] = None
    content: str


class AnalysisStatusResponse(BaseModel):
    """分析状态响应"""
    status: str  # pending, processing, completed, failed
    progress: Optional[int] = None  # 0-100
    error_message: Optional[str] = None


# ============= 后台任务函数 =============

async def analyze_article_task(article_id: int):
    """
    后台分析文章任务

    Args:
        article_id: 文章ID

    Returns:
        分析结果字典
    """
    db = SessionLocal()

    try:
        logger.info(f"[后台任务] 开始分析文章，ID: {article_id}")

        # 获取文章
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise Exception(f"文章不存在: {article_id}")

        # 获取或创建分析报告
        report = db.query(AnalysisReport).filter(
            AnalysisReport.article_id == article_id
        ).first()

        if not report:
            report = AnalysisReport(
                article_id=article_id,
                status='processing'
            )
            db.add(report)
        else:
            report.status = 'processing'

        db.commit()

        # 执行分析
        analysis_service = UnifiedAnalysisService()
        start_time = datetime.utcnow()

        result = await analysis_service.analyze_article(
            article_content=article.content,
            article_title=article.title or ""
        )

        # 计算处理时间
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # 保存分析结果
        report.status = 'completed'
        report.report_data = result['report']
        report.metadata = result['metadata']
        report.model_used = result['metadata'].get('model_used')
        report.tokens_used = result['metadata'].get('tokens_used')
        report.processing_time_ms = processing_time_ms
        report.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"[后台任务] 文章分析完成，ID: {article_id}, 耗时: {processing_time_ms}ms")

        return {
            "article_id": article_id,
            "status": "completed",
            "report_data": result['report']
        }

    except Exception as e:
        logger.error(f"[后台任务] 文章分析失败，ID: {article_id}, 错误: {str(e)}", exc_info=True)

        # 更新失败状态
        try:
            report = db.query(AnalysisReport).filter(
                AnalysisReport.article_id == article_id
            ).first()
            if report:
                report.status = 'failed'
                report.error_message = str(e)
                db.commit()
        except Exception as db_error:
            logger.error(f"[后台任务] 更新失败状态出错: {str(db_error)}")

        raise

    finally:
        db.close()


@router.post("/api/v1/articles/save-with-analysis")
async def save_article_with_analysis(
    request: SaveArticleWithAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    保存文章并触发深度分析（异步版本）

    工作流程：
    1. 保存文章到数据库（MD5去重） - 快速返回
    2. 检查是否已有分析报告
    3. 如果没有报告，提交后台分析任务
    4. 立即返回文章ID和任务状态
    5. 分析完成后通过SSE通知前端

    Returns:
        {
            "article": {
                "id": int,
                "is_new": bool
            },
            "analysis": {
                "status": "completed" | "pending" | "processing",
                "task_id": str | None
            }
        }
    """
    # 1. 计算内容哈希
    content_hash = hashlib.md5(request.content.encode('utf-8')).hexdigest()

    # 2. 检查文章是否已存在
    article = db.query(Article).filter(Article.content_hash == content_hash).first()
    is_new_article = False

    if article:
        # 文章已存在，更新阅读信息
        article.last_read_at = datetime.utcnow()
        article.read_count += 1
        db.commit()

        # 检查是否已有分析报告
        report = db.query(AnalysisReport).filter(
            AnalysisReport.article_id == article.id
        ).first()

        if report and report.status == 'completed':
            # 已有完整报告，直接返回
            logger.info(f"[API] 文章已存在且有分析报告，ID: {article.id}")
            return {
                "article": {
                    "id": article.id,
                    "is_new": False
                },
                "analysis": {
                    "status": "completed",
                    "task_id": None
                }
            }

        if report and report.status == 'processing':
            # 正在分析中
            logger.info(f"[API] 文章正在分析中，ID: {article.id}")
            return {
                "article": {
                    "id": article.id,
                    "is_new": False
                },
                "analysis": {
                    "status": "processing",
                    "task_id": None
                }
            }

    else:
        # 创建新文章
        is_new_article = True
        article = Article(
            user_id=current_user.id,
            title=request.title,
            author=request.author,
            source_url=request.source_url,
            content=request.content,
            content_hash=content_hash,
            word_count=len(request.content)
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        logger.info(f"[API] 新文章已保存，ID: {article.id}")

    # 3. 创建或获取分析报告记录
    report = db.query(AnalysisReport).filter(
        AnalysisReport.article_id == article.id
    ).first()

    if not report:
        report = AnalysisReport(
            article_id=article.id,
            status='pending'
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    # 4. 提交异步分析任务
    task_id = task_manager.submit_task(
        "article_analysis",
        analyze_article_task,
        {
            "article_id": article.id,
            "user_id": current_user.id,
            "article_title": request.title
        },
        article.id  # 传递给任务函数的参数
    )

    logger.info(f"[API] 异步分析任务已提交，文章ID: {article.id}, 任务ID: {task_id}")

    return {
        "article": {
            "id": article.id,
            "is_new": is_new_article
        },
        "analysis": {
            "status": "pending",
            "task_id": task_id
        }
    }


@router.get("/api/v1/articles/{article_id}/analysis-status")
async def get_analysis_status(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    获取文章分析状态

    Returns:
        {
            "status": "pending" | "processing" | "completed" | "failed",
            "progress": 0-100,
            "error_message": str | null
        }
    """
    report = db.query(AnalysisReport).filter(
        AnalysisReport.article_id == article_id
    ).first()

    if not report:
        return {
            "status": "not_started",
            "progress": 0,
            "error_message": None
        }

    return {
        "status": report.status,
        "progress": 100 if report.status == 'completed' else (50 if report.status == 'processing' else 0),
        "error_message": report.error_message
    }


@router.get("/api/v1/articles/{article_id}/analysis-report")
async def get_analysis_report(
    article_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取文章的完整分析报告

    **权限控制：**
    - 示例文章（is_demo=True）：任何人都可以访问，无需登录
    - 普通文章：需要登录且是文章所有者

    Returns:
        {
            "report_data": {...},  # 完整的JSON报告
            "metadata": {
                "model_used": str,
                "tokens_used": int,
                "processing_time_ms": int,
                "completed_at": datetime
            }
        }
    """
    # 查询文章和分析报告
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 权限验证：示例文章可公开访问，普通文章需要所有权验证
    if not article.is_demo:
        if not current_user:
            raise HTTPException(status_code=401, detail="需要登录")
        if article.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此文章")

    # 查询分析报告
    report = db.query(AnalysisReport).filter(
        AnalysisReport.article_id == article_id,
        AnalysisReport.status == 'completed'
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="分析报告不存在或尚未完成"
        )

    return {
        "report_data": report.report_data,
        "metadata": {
            "model_used": report.model_used,
            "tokens_used": report.tokens_used,
            "processing_time_ms": report.processing_time_ms,
            "completed_at": report.completed_at.isoformat() if report.completed_at else None
        }
    }


@router.post("/api/v1/articles/{article_id}/reanalyze")
async def reanalyze_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    重新分析文章（异步版本）

    例如当分析失败或需要更新时

    Returns:
        {
            "task_id": str,
            "message": "重新分析已开始"
        }
    """
    # 检查文章是否存在
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 重置分析报告状态
    report = db.query(AnalysisReport).filter(
        AnalysisReport.article_id == article_id
    ).first()

    if report:
        report.status = 'pending'
        report.error_message = None
    else:
        report = AnalysisReport(
            article_id=article_id,
            status='pending'
        )
        db.add(report)

    db.commit()

    # 提交异步分析任务
    task_id = task_manager.submit_task(
        "article_reanalysis",
        analyze_article_task,
        {
            "article_id": article_id,
            "user_id": current_user.id,
            "article_title": article.title
        },
        article_id  # 传递给任务函数的参数
    )

    logger.info(f"[API] 重新分析任务已提交，文章ID: {article_id}, 任务ID: {task_id}")

    return {
        "task_id": task_id,
        "message": "重新分析已开始"
    }
