"""洞察卡片收藏 API"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.database import get_db
from app.models.models import User, InsightCard
from app.schemas.insight_card import (
    InsightCardCreate,
    InsightCardUpdate,
    InsightCardResponse,
    InsightCardListResponse
)
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=InsightCardResponse, status_code=status.HTTP_201_CREATED)
async def create_insight_card(
    card_data: InsightCardCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建洞察卡片（收藏）"""
    # 将标签列表转换为JSON字符串存储
    tags_json = json.dumps(card_data.tags) if card_data.tags else None

    new_card = InsightCard(
        user_id=current_user.id,
        article_title=card_data.article_title,
        article_content=card_data.article_content,
        selected_text=card_data.selected_text,
        context=card_data.context,
        intent=card_data.intent,
        custom_question=card_data.custom_question,
        insight=card_data.insight,
        model_used=card_data.model_used,
        tokens=card_data.tokens,
        tags=tags_json
    )

    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    # 将JSON字符串转回列表
    response = InsightCardResponse.model_validate(new_card)
    if new_card.tags:
        response.tags = json.loads(new_card.tags)

    return response


@router.get("/", response_model=InsightCardListResponse)
async def get_insight_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    intent: Optional[str] = Query(None, pattern="^(explain|analyze|counter)$"),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的洞察卡片列表"""
    # 基础查询
    query = db.query(InsightCard).filter(InsightCard.user_id == current_user.id)

    # 按意图筛选
    if intent:
        query = query.filter(InsightCard.intent == intent)

    # 搜索
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (InsightCard.selected_text.like(search_pattern)) |
            (InsightCard.insight.like(search_pattern)) |
            (InsightCard.article_title.like(search_pattern))
        )

    # 总数
    total = query.count()

    # 分页
    cards = query.order_by(InsightCard.created_at.desc()).offset(skip).limit(limit).all()

    # 转换响应
    items = []
    for card in cards:
        response = InsightCardResponse.model_validate(card)
        if card.tags:
            response.tags = json.loads(card.tags)
        items.append(response)

    return InsightCardListResponse(total=total, items=items)


@router.get("/{card_id}", response_model=InsightCardResponse)
async def get_insight_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取单个洞察卡片"""
    card = db.query(InsightCard).filter(
        InsightCard.id == card_id,
        InsightCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该洞察卡片"
        )

    response = InsightCardResponse.model_validate(card)
    if card.tags:
        response.tags = json.loads(card.tags)

    return response


@router.patch("/{card_id}", response_model=InsightCardResponse)
async def update_insight_card(
    card_id: int,
    card_update: InsightCardUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新洞察卡片（主要用于更新标签）"""
    card = db.query(InsightCard).filter(
        InsightCard.id == card_id,
        InsightCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该洞察卡片"
        )

    # 更新标签
    if card_update.tags is not None:
        card.tags = json.dumps(card_update.tags) if card_update.tags else None

    db.commit()
    db.refresh(card)

    response = InsightCardResponse.model_validate(card)
    if card.tags:
        response.tags = json.loads(card.tags)

    return response


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_insight_card(
    card_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除洞察卡片"""
    card = db.query(InsightCard).filter(
        InsightCard.id == card_id,
        InsightCard.user_id == current_user.id
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该洞察卡片"
        )

    db.delete(card)
    db.commit()

    return None
