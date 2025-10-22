"""
元信息分析 API 路由（异步版本 + JWT 认证）
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, SessionLocal
from app.services.meta_analysis_service import MetaAnalysisService
from app.core.task_manager import task_manager
from app.utils.auth import get_current_active_user, get_current_user_optional
from app.models.models import User, Article
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


# ============= 后台任务函数 =============

async def meta_analysis_task(
    article_id: int,
    title: str,
    author: str,
    publish_date: str,
    content: str,
    user_id: Optional[int],
    source_url: Optional[str],
    language: str
):
    """
    后台元视角分析任务

    Args:
        article_id: 文章ID
        title: 标题
        author: 作者
        publish_date: 发布日期
        content: 内容
        user_id: 用户ID
        source_url: 来源URL
        language: 语言

    Returns:
        分析结果
    """
    db = SessionLocal()

    try:
        logger.info(f"[后台任务] 开始元视角分析，文章ID: {article_id}")

        service = MetaAnalysisService(db)

        result = await service.analyze_article(
            title=title,
            author=author,
            publish_date=publish_date,
            content=content,
            user_id=user_id,
            source_url=source_url,
            language=language,
            force_reanalyze=False
        )

        logger.info(f"[后台任务] 元视角分析完成，文章ID: {article_id}")

        return {
            "article_id": article_id,
            "status": "completed",
            "meta_analysis": result
        }

    except Exception as e:
        logger.error(f"[后台任务] 元视角分析失败，文章ID: {article_id}, 错误: {str(e)}", exc_info=True)
        raise

    finally:
        db.close()


class AnalyzeRequest(BaseModel):
    title: str
    author: str = "未知作者"
    publish_date: str = ""
    full_text: str
    source_url: Optional[str] = None
    language: str = "zh"
    force_reanalyze: bool = False


@router.post("/api/v1/meta-analysis/analyze")
async def analyze_article(
    request: AnalyzeRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    触发元信息分析（异步版本）

    **权限控制：**
    - 如果分析已存在：任何人都可以获取（示例文章场景）
    - 如果需要创建新分析：需要登录

    工作流程：
    1. 检查是否已有分析结果
    2. 如果有且不强制重新分析，立即返回（无需登录）
    3. 否则需要登录才能提交后台分析任务
    4. 通过SSE通知前端分析完成

    Args:
        request: 分析请求
        current_user: 当前用户（可选）
        db: 数据库会话

    Returns:
        {
            "status": "completed" | "pending",
            "message": str,
            "meta_analysis": dict | null,
            "task_id": str | null
        }
    """
    service = MetaAnalysisService(db)

    try:
        # 如果不强制重新分析，先检查是否已有结果
        if not request.force_reanalyze:
            # 尝试通过内容哈希查找已有的元分析
            from app.models.models import Article
            import hashlib

            content_hash = hashlib.md5(request.full_text.encode('utf-8')).hexdigest()
            article = db.query(Article).filter(Article.content_hash == content_hash).first()

            if article:
                existing_result = service.get_meta_analysis(article.id)
                if existing_result:
                    logger.info(f"[API] 元视角分析已存在，文章ID: {article.id}")
                    return {
                        "status": "completed",
                        "message": "分析已存在",
                        "meta_analysis": existing_result,
                        "task_id": None
                    }

        # 需要重新分析或首次分析 - 需要登录
        if not current_user:
            raise HTTPException(status_code=401, detail="创建新分析需要登录")

        # 先保存文章
        from app.models.models import Article
        import hashlib

        content_hash = hashlib.md5(request.full_text.encode('utf-8')).hexdigest()
        article = db.query(Article).filter(Article.content_hash == content_hash).first()

        if not article:
            article = Article(
                user_id=current_user.id,
                title=request.title,
                author=request.author,
                source_url=request.source_url,
                content=request.full_text,
                content_hash=content_hash,
                word_count=len(request.full_text)
            )
            db.add(article)
            db.commit()
            db.refresh(article)
            logger.info(f"[API] 新文章已保存用于元视角分析，ID: {article.id}")

        # 提交异步分析任务
        task_id = task_manager.submit_task(
            "meta_analysis",
            meta_analysis_task,
            {
                "article_id": article.id,
                "user_id": current_user.id,
                "title": request.title
            },
            article.id,
            request.title,
            request.author,
            request.publish_date,
            request.full_text,
            current_user.id,
            request.source_url,
            request.language
        )

        logger.info(f"[API] 元视角分析任务已提交，文章ID: {article.id}, 任务ID: {task_id}")

        return {
            "status": "pending",
            "message": "分析已开始",
            "meta_analysis": None,
            "task_id": task_id
        }

    except Exception as e:
        logger.error(f"[API] 触发元视角分析失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.get("/api/v1/meta-analysis/{article_id}")
async def get_meta_analysis(
    article_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取元信息分析结果

    **权限控制：**
    - 示例文章（is_demo=True）：任何人都可以访问，无需登录
    - 普通文章：需要登录且是文章所有者

    Args:
        article_id: 文章ID
        current_user: 当前用户（可选）
        db: 数据库会话

    Returns:
        元信息分析结果或null
    """
    # 查询文章
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 权限验证：示例文章可公开访问，普通文章需要所有权验证
    if not article.is_demo:
        if not current_user:
            raise HTTPException(status_code=401, detail="需要登录")
        if article.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此文章")

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
    meta_analysis_id: Optional[int] = None
    lens_result_id: Optional[int] = None
    feedback_type: str  # 'meta_info_card' | 'lens_highlight' | 'overall'
    rating: Optional[int] = None  # 1-5
    comment: Optional[str] = None
    feedback_data: Optional[dict] = None


@router.post("/api/v1/meta-analysis/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_active_user),
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
            user_id=current_user.id,
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
