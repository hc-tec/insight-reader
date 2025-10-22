"""
管理员示例文章管理 API
用于标记/取消示例文章、预生成分析等管理操作

**最佳实践：**
- 所有端点都需要管理员权限验证
- 操作记录详细日志
- 提供原子性操作（事务保证）
- 幂等性设计
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Article, User
from app.utils.auth import get_current_active_user
from app.config import settings
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/demo", tags=["管理员-示例文章"])


# ===== 辅助函数：权限验证 =====

def verify_admin(current_user: User):
    """
    验证用户是否为管理员

    **最佳实践：**
    - 从环境变量读取管理员邮箱列表
    - 支持逗号分隔的多个邮箱
    - 统一权限验证逻辑
    - 记录未授权访问尝试
    """
    # 从配置读取管理员邮箱列表（支持逗号分隔）
    admin_emails_str = settings.admin_emails
    admin_emails = [email.strip() for email in admin_emails_str.split(",") if email.strip()]

    if not admin_emails:
        logger.error("[Admin] 管理员邮箱列表为空，请检查配置")
        raise HTTPException(
            status_code=500,
            detail="系统配置错误：未设置管理员"
        )

    if current_user.email not in admin_emails:
        logger.warning(
            f"[Admin] 未授权访问尝试: {current_user.email} "
            f"(管理员列表: {', '.join(admin_emails)})"
        )
        raise HTTPException(
            status_code=403,
            detail="需要管理员权限"
        )

    logger.info(f"[Admin] 管理员身份验证成功: {current_user.email}")
    return current_user


# ===== Pydantic 请求/响应模型 =====

class MarkDemoRequest(BaseModel):
    """标记为示例文章的请求"""
    demo_order: Optional[int] = Field(None, description="展示顺序（可选）")


class DemoArticleStatus(BaseModel):
    """示例文章状态"""
    article_id: int
    is_demo: bool
    demo_order: Optional[int]
    has_analysis: bool
    has_meta_analysis: bool


# ===== API 端点 =====

@router.post("/articles/{article_id}/mark", response_model=DemoArticleStatus)
async def mark_as_demo(
    article_id: int,
    request: MarkDemoRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记文章为示例文章

    **功能：**
    1. 将文章标记为示例（is_demo=True）
    2. 设置展示顺序

    **说明：**
    - 文章应该已经完成了正常的分析流程
    - 标记后，公开 API 会直接读取已有的分析结果
    - 无需预生成分析

    **最佳实践：**
    - 使用事务保证原子性
    - 详细的操作日志
    - 幂等性设计（重复调用不会出错）
    """
    # 验证管理员权限
    verify_admin(current_user)

    try:
        # 查询文章
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 检查是否有分析报告
        if not article.analysis_report:
            logger.warning(f"[Admin] 文章 {article_id} 没有分析报告，建议先分析再标记为示例")

        # 标记为示例
        article.is_demo = True
        article.demo_order = request.demo_order

        db.commit()
        db.refresh(article)

        logger.info(f"[Admin] 文章 {article_id} 已标记为示例，顺序: {request.demo_order}，操作人: {current_user.email}")

        # 返回状态
        return DemoArticleStatus(
            article_id=article.id,
            is_demo=article.is_demo,
            demo_order=article.demo_order,
            has_analysis=article.analysis_report is not None,
            has_meta_analysis=article.meta_analysis is not None
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] 标记示例文章失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")


@router.delete("/articles/{article_id}/unmark", response_model=DemoArticleStatus)
async def unmark_demo(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消示例文章标记

    **最佳实践：**
    - 保留分析数据（不删除），只改变标记
    - 记录操作日志
    - 幂等性设计
    """
    verify_admin(current_user)

    try:
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 取消示例标记
        article.is_demo = False
        article.demo_order = None

        db.commit()
        db.refresh(article)

        logger.info(f"[Admin] 文章 {article_id} 已取消示例标记，操作人: {current_user.email}")

        return DemoArticleStatus(
            article_id=article.id,
            is_demo=article.is_demo,
            demo_order=article.demo_order,
            has_analysis=article.analysis_report is not None,
            has_meta_analysis=article.meta_analysis is not None
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] 取消示例标记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")


@router.put("/articles/{article_id}/order")
async def update_demo_order(
    article_id: int,
    order: int = Query(..., ge=0, description="新的展示顺序"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新示例文章的展示顺序

    **最佳实践：**
    - 只允许修改已标记为示例的文章
    - 验证顺序值的有效性
    """
    verify_admin(current_user)

    try:
        article = db.query(Article).filter(
            Article.id == article_id,
            Article.is_demo == True
        ).first()

        if not article:
            raise HTTPException(status_code=404, detail="示例文章不存在")

        old_order = article.demo_order
        article.demo_order = order

        db.commit()

        logger.info(f"[Admin] 文章 {article_id} 顺序更新: {old_order} -> {order}，操作人: {current_user.email}")

        return {
            "article_id": article_id,
            "old_order": old_order,
            "new_order": order,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[Admin] 更新顺序失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")




@router.get("/articles")
async def list_demo_articles_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取所有示例文章（管理员视图）

    包含更多管理信息：
    - 创建者信息
    - 分析状态
    - 访问统计（TODO）
    """
    verify_admin(current_user)

    try:
        articles = db.query(Article)\
            .filter(Article.is_demo == True)\
            .order_by(Article.demo_order.asc().nulls_last())\
            .all()

        results = []
        for article in articles:
            results.append({
                "id": article.id,
                "title": article.title,
                "author": article.author,
                "demo_order": article.demo_order,
                "word_count": article.word_count,
                "has_analysis": article.analysis_report is not None,
                "has_meta_analysis": article.meta_analysis is not None,
                "created_at": article.created_at,
                "owner_id": article.user_id
            })

        logger.info(f"[Admin] 查询示例文章列表，共 {len(results)} 篇，操作人: {current_user.email}")

        return {
            "total": len(results),
            "articles": results
        }

    except Exception as e:
        logger.error(f"[Admin] 获取示例文章列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="操作失败")
