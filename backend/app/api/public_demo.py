"""
公开示例文章 API（无需认证）
只提供示例文章列表，详情使用现有的 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Article
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/public/demo", tags=["公开示例"])


class DemoArticleBrief(BaseModel):
    """示例文章简要信息"""
    id: int
    title: str
    author: str | None = None
    word_count: int | None = None
    created_at: datetime
    demo_order: int | None = None
    has_analysis: bool = Field(description="是否有完整分析报告")

    class Config:
        from_attributes = True


class DemoArticleListResponse(BaseModel):
    """示例文章列表响应"""
    total: int
    articles: List[DemoArticleBrief]

    class Config:
        from_attributes = True


@router.get("/articles", response_model=DemoArticleListResponse)
async def get_demo_articles(
    limit: int = Query(10, ge=1, le=50, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """
    获取示例文章列表（公开访问，无需登录）

    点击文章后跳转到 /?articleId=X 查看详情
    """
    try:
        query = db.query(Article)\
            .filter(Article.is_demo == True)\
            .order_by(Article.demo_order.asc().nulls_last(), Article.created_at.desc())

        total = query.count()
        articles = query.offset(offset).limit(limit).all()

        articles_data = []
        for article in articles:
            articles_data.append(DemoArticleBrief(
                id=article.id,
                title=article.title,
                author=article.author,
                word_count=article.word_count,
                created_at=article.created_at,
                demo_order=article.demo_order,
                has_analysis=article.analysis_report is not None
            ))

        logger.info(f"[Public Demo] 返回 {len(articles_data)} 篇示例文章")

        return DemoArticleListResponse(
            total=total,
            articles=articles_data
        )

    except Exception as e:
        logger.error(f"[Public Demo] 获取示例文章列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")
