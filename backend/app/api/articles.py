"""
文章历史 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Article
from typing import Optional, List
from datetime import datetime

router = APIRouter()


@router.get("/api/v1/articles")
async def get_articles(
    user_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    获取文章列表

    Args:
        user_id: 用户ID (可选，不传则返回所有文章)
        limit: 每页数量
        offset: 偏移量
        db: 数据库会话

    Returns:
        文章列表
    """
    query = db.query(Article)

    if user_id is not None:
        query = query.filter(Article.user_id == user_id)

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
    db: Session = Depends(get_db)
):
    """
    获取单篇文章详情

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        文章详情（包括完整内容）
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    # 更新阅读次数和时间
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
        "last_read_at": article.last_read_at.isoformat(),
        "read_count": article.read_count,
        "has_meta_analysis": article.meta_analysis is not None,
        "meta_analysis_id": article.meta_analysis.id if article.meta_analysis else None
    }


@router.delete("/api/v1/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    删除文章

    Args:
        article_id: 文章ID
        db: 数据库会话

    Returns:
        成功消息
    """
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    db.delete(article)
    db.commit()

    return {
        "status": "success",
        "message": "文章已删除"
    }
