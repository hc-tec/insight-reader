"""
洞察历史 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.models.models import Article, InsightHistory
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib

router = APIRouter()


# ==================== Pydantic 模型 ====================

class SaveArticleRequest(BaseModel):
    """保存文章请求"""
    title: str
    author: Optional[str] = "Unknown"
    content: str
    user_id: Optional[int] = None
    source_url: Optional[str] = None
    language: str = "zh"


class SaveInsightRequest(BaseModel):
    """保存洞察记录请求"""
    article_id: int
    user_id: Optional[int] = None
    selected_text: str
    selected_start: Optional[int] = None
    selected_end: Optional[int] = None
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    intent: str
    question: Optional[str] = None
    insight: str
    reasoning: Optional[str] = None


# ==================== 文章相关 API ====================

@router.post("/api/v1/articles/save")
async def save_article(request: SaveArticleRequest, db: Session = Depends(get_db)):
    """
    保存文章（如果已存在则返回现有文章）

    Args:
        request: 文章信息
        db: 数据库会话

    Returns:
        文章信息 + is_new 标志
    """
    try:
        # 计算 MD5 哈希
        content_hash = hashlib.md5(request.content.encode('utf-8')).hexdigest()

        # 查找是否已存在
        article = db.query(Article).filter(Article.content_hash == content_hash).first()

        if article:
            # 文章已存在，更新阅读统计
            article.last_read_at = datetime.utcnow()
            article.read_count += 1
            db.commit()
            db.refresh(article)

            return {
                "status": "success",
                "article": {
                    "id": article.id,
                    "title": article.title,
                    "content_hash": article.content_hash,
                    "insight_count": article.insight_count,
                    "is_new": False
                }
            }
        else:
            # 创建新文章
            new_article = Article(
                user_id=request.user_id,
                title=request.title,
                author=request.author,
                source_url=request.source_url,
                content=request.content,
                content_hash=content_hash,
                language=request.language,
                word_count=len(request.content)
            )

            db.add(new_article)
            db.commit()
            db.refresh(new_article)

            return {
                "status": "success",
                "article": {
                    "id": new_article.id,
                    "title": new_article.title,
                    "content_hash": new_article.content_hash,
                    "insight_count": 0,
                    "is_new": True
                }
            }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存文章失败: {str(e)}")


# ==================== 洞察历史 API ====================

@router.post("/api/v1/insights/history")
async def save_insight_history(request: SaveInsightRequest, db: Session = Depends(get_db)):
    """
    保存洞察记录

    Args:
        request: 洞察信息
        db: 数据库会话

    Returns:
        成功消息 + 洞察ID
    """
    try:
        # 验证文章是否存在
        article = db.query(Article).filter(Article.id == request.article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 创建洞察记录
        insight_history = InsightHistory(
            article_id=request.article_id,
            user_id=request.user_id,
            selected_text=request.selected_text,
            selected_start=request.selected_start,
            selected_end=request.selected_end,
            context_before=request.context_before,
            context_after=request.context_after,
            intent=request.intent,
            question=request.question,
            insight=request.insight,
            reasoning=request.reasoning
        )

        db.add(insight_history)

        # 更新文章的洞察计数
        article.insight_count += 1

        db.commit()
        db.refresh(insight_history)

        return {
            "status": "success",
            "insight_history_id": insight_history.id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存洞察记录失败: {str(e)}")


@router.get("/api/v1/insights/history")
async def get_insight_history(
    article_id: int,
    user_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    获取文章的洞察历史

    Args:
        article_id: 文章ID
        user_id: 用户ID（可选，不传则返回所有用户的记录）
        limit: 每页数量
        offset: 偏移量
        db: 数据库会话

    Returns:
        洞察历史列表
    """
    try:
        # 构建查询
        query = db.query(InsightHistory).filter(InsightHistory.article_id == article_id)

        if user_id is not None:
            query = query.filter(InsightHistory.user_id == user_id)

        # 按时间倒序
        query = query.order_by(desc(InsightHistory.created_at))

        # 分页
        total = query.count()
        insights = query.offset(offset).limit(limit).all()

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "insights": [
                {
                    "id": insight.id,
                    "selected_text": insight.selected_text,
                    "selected_start": insight.selected_start,
                    "selected_end": insight.selected_end,
                    "context_before": insight.context_before,
                    "context_after": insight.context_after,
                    "intent": insight.intent,
                    "question": insight.question,
                    "insight": insight.insight,
                    "reasoning": insight.reasoning,
                    "created_at": insight.created_at.isoformat()
                }
                for insight in insights
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取洞察历史失败: {str(e)}")


@router.delete("/api/v1/insights/history/{insight_id}")
async def delete_insight_history(insight_id: int, db: Session = Depends(get_db)):
    """
    删除洞察记录

    Args:
        insight_id: 洞察ID
        db: 数据库会话

    Returns:
        成功消息
    """
    try:
        insight = db.query(InsightHistory).filter(InsightHistory.id == insight_id).first()

        if not insight:
            raise HTTPException(status_code=404, detail="洞察记录不存在")

        # 更新文章的洞察计数
        article = db.query(Article).filter(Article.id == insight.article_id).first()
        if article and article.insight_count > 0:
            article.insight_count -= 1

        db.delete(insight)
        db.commit()

        return {
            "status": "success",
            "message": "洞察记录已删除"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除洞察记录失败: {str(e)}")
