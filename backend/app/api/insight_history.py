"""
洞察历史 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.models.models import Article, InsightHistory, User
from app.utils.auth import get_current_active_user, get_current_user_optional
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
    source_url: Optional[str] = None
    language: str = "zh"


class SaveInsightRequest(BaseModel):
    """保存洞察记录请求"""
    article_id: int
    selected_text: str
    selected_start: Optional[int] = None
    selected_end: Optional[int] = None
    context_before: Optional[str] = None
    context_after: Optional[str] = None
    intent: str
    question: Optional[str] = None
    insight: str
    reasoning: Optional[str] = None
    parent_id: Optional[int] = None  # 追问时指向原始洞察的 ID


# ==================== 文章相关 API ====================

@router.post("/api/v1/articles/save")
async def save_article(
    request: SaveArticleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    保存文章（如果已存在则返回现有文章）

    Args:
        request: 文章信息
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        文章信息 + is_new 标志
    """
    try:
        # 计算 MD5 哈希
        content_hash = hashlib.md5(request.content.encode('utf-8')).hexdigest()

        # 查找是否已存在（限定为当前用户）
        article = db.query(Article).filter(
            Article.content_hash == content_hash,
            Article.user_id == current_user.id
        ).first()

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
                user_id=current_user.id,
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
async def save_insight_history(
    request: SaveInsightRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    保存洞察记录

    Args:
        request: 洞察信息
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        成功消息 + 洞察ID
    """
    try:
        # 验证文章是否存在并属于当前用户
        article = db.query(Article).filter(Article.id == request.article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        if article.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此文章")

        # 创建洞察记录
        insight_history = InsightHistory(
            article_id=request.article_id,
            user_id=current_user.id,
            parent_id=request.parent_id,  # 支持追问链
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
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取文章的洞察历史（按对话链分组）

    **权限控制：**
    - 示例文章（is_demo=True）：任何人都可以访问，返回所有洞察
    - 普通文章：需要登录且是文章所有者，返回该用户的洞察

    **返回格式：**
    返回按对话链分组的结构，每个对话包含完整的 messages 数组（user/assistant 交替）

    Args:
        article_id: 文章ID
        limit: 每页数量（限制对话链数量）
        offset: 偏移量
        current_user: 当前用户（可选）
        db: 数据库会话

    Returns:
        对话链列表，每个对话包含 messages 数组
    """
    try:
        # 验证文章是否存在
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            raise HTTPException(status_code=404, detail="文章不存在")

        # 权限检查：示例文章可公开访问，普通文章需要所有权验证
        if not article.is_demo:
            if not current_user:
                raise HTTPException(status_code=401, detail="需要登录")
            if article.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="无权访问此文章")

        # 构建查询：获取所有洞察记录
        query = db.query(InsightHistory).filter(
            InsightHistory.article_id == article_id
        )

        # 如果是普通文章，只返回当前用户的洞察
        if not article.is_demo and current_user:
            query = query.filter(InsightHistory.user_id == current_user.id)

        # 按时间正序（先发生的在前）
        all_insights = query.order_by(InsightHistory.created_at).all()

        # 构建对话链：将洞察组织成树形结构
        # 1. 找到所有根洞察（parent_id == null）
        root_insights = [i for i in all_insights if i.parent_id is None]

        # 2. 构建 ID -> 洞察的映射
        insight_map = {i.id: i for i in all_insights}

        # 3. 为每个根洞察构建完整的对话链
        conversations = []
        for root in root_insights:
            messages = []

            # 添加初始问题（用户消息）
            messages.append({
                "role": "user",
                "content": root.question or root.selected_text,  # 如果有自定义问题用问题，否则用选中文本
                "timestamp": root.created_at.isoformat(),
                "insight_id": None  # 用户消息没有 insight_id
            })

            # 添加初始洞察（助手消息）
            assistant_message = {
                "role": "assistant",
                "content": root.insight,
                "timestamp": root.created_at.isoformat(),
                "insight_id": root.id  # 重要：添加洞察记录的 ID
            }
            if root.reasoning:
                assistant_message["reasoning"] = root.reasoning
            messages.append(assistant_message)

            # 递归添加所有追问（通过 parent_id 链接）
            def add_follow_ups(parent_id: int):
                # 找到所有直接子追问
                children = [i for i in all_insights if i.parent_id == parent_id]
                for child in children:
                    # 添加用户追问
                    messages.append({
                        "role": "user",
                        "content": child.question or child.selected_text,
                        "timestamp": child.created_at.isoformat(),
                        "insight_id": None  # 用户消息没有 insight_id
                    })

                    # 添加 AI 回答
                    child_message = {
                        "role": "assistant",
                        "content": child.insight,
                        "timestamp": child.created_at.isoformat(),
                        "insight_id": child.id  # 重要：添加洞察记录的 ID
                    }
                    if child.reasoning:
                        child_message["reasoning"] = child.reasoning
                    messages.append(child_message)

                    # 递归处理子追问的追问
                    add_follow_ups(child.id)

            add_follow_ups(root.id)

            # 构建对话对象
            conversation = {
                "root_insight_id": root.id,
                "selected_text": root.selected_text,
                "selected_start": root.selected_start,
                "selected_end": root.selected_end,
                "context_before": root.context_before,
                "context_after": root.context_after,
                "intent": root.intent,
                "question": root.question,  # ✅ 添加 question 字段（自定义问题）
                "created_at": root.created_at.isoformat(),
                "messages": messages
            }
            conversations.append(conversation)

        # 按创建时间倒序排列（最新的对话在前）
        conversations.sort(key=lambda x: x["created_at"], reverse=True)

        # 分页
        total = len(conversations)
        paginated_conversations = conversations[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "conversations": paginated_conversations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取洞察历史失败: {str(e)}")


@router.delete("/api/v1/insights/history/{insight_id}")
async def delete_insight_history(
    insight_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除洞察记录

    Args:
        insight_id: 洞察ID
        current_user: 当前用户（从 JWT 获取）
        db: 数据库会话

    Returns:
        成功消息
    """
    try:
        insight = db.query(InsightHistory).filter(InsightHistory.id == insight_id).first()

        if not insight:
            raise HTTPException(status_code=404, detail="洞察记录不存在")

        # 权限检查：只能删除自己的洞察记录
        if insight.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除此洞察记录")

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
