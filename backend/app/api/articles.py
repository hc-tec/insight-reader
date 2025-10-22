"""
文章历史 API 路由（JWT 认证版本）
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Article, User
from app.utils.auth import get_current_active_user, get_current_user_optional
from typing import Optional, List
from datetime import datetime

router = APIRouter()


@router.get("/api/v1/articles")
async def get_articles(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取文章列表

    Args:
        limit: 每页数量
        offset: 偏移量
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        文章列表
    """
    # 只返回当前用户的文章
    query = db.query(Article).filter(Article.user_id == current_user.id)

    # 按最后阅读时间倒序
    query = query.order_by(Article.last_read_at.desc())

    # 分页
    total = query.count()
    articles = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "articles": [
            {
                "id": article.id,
                "title": article.title,
                "author": article.author,
                "source_url": article.source_url,
                "publish_date": article.publish_date.isoformat() if article.publish_date else None,
                "language": article.language,
                "word_count": article.word_count,
                "created_at": article.created_at.isoformat(),
                "last_read_at": article.last_read_at.isoformat(),
                "read_count": article.read_count,
                "has_meta_analysis": article.meta_analysis is not None
            }
            for article in articles
        ]
    }


@router.get("/api/v1/articles/{article_id}")
async def get_article(
    article_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取单篇文章详情

    **权限控制：**
    - 示例文章（is_demo=True）：任何人都可以访问，无需登录
    - 普通文章：需要登录且是文章所有者

    Args:
        article_id: 文章ID
        current_user: 当前用户（可选）
        db: 数据库会话

    Returns:
        文章详情（包括完整内容）
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 权限检查：示例文章可公开访问，普通文章需要所有权验证
    if not article.is_demo:
        if not current_user:
            raise HTTPException(status_code=401, detail="需要登录")
        if article.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此文章")

    # 更新阅读次数和时间（只对已登录用户的文章更新）
    if current_user and article.user_id == current_user.id:
        article.last_read_at = datetime.utcnow()
        article.read_count += 1
        db.commit()

    return {
        "id": article.id,
        "user_id": article.user_id,
        "title": article.title,
        "author": article.author,
        "source_url": article.source_url,
        "publish_date": article.publish_date.isoformat() if article.publish_date else None,
        "content": article.content,
        "language": article.language,
        "word_count": article.word_count,
        "created_at": article.created_at.isoformat(),
        "last_read_at": article.last_read_at.isoformat() if article.last_read_at else None,
        "read_count": article.read_count,
        "has_meta_analysis": article.meta_analysis is not None,
        "meta_analysis_id": article.meta_analysis.id if article.meta_analysis else None
    }


@router.delete("/api/v1/articles/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除文章

    Args:
        article_id: 文章ID
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        成功消息
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 权限检查：只能删除自己的文章
    if article.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此文章")

    db.delete(article)
    db.commit()

    return {
        "status": "success",
        "message": "文章已删除"
    }
