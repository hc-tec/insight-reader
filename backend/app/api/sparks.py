# -*- coding: utf-8 -*-
"""
火花解释 API
提供概念火花的 AI 解释功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/v1/sparks", tags=["sparks"])


class ExplainRequest(BaseModel):
    """解释请求"""
    hint: str  # 提示词（来自 concept_spark 的 explanation_hint）
    concept: str  # 概念文本


class ExplainResponse(BaseModel):
    """解释响应"""
    explanation: str


@router.post("/explain", response_model=ExplainResponse)
async def explain_concept(request: ExplainRequest):
    """
    生成概念解释

    用于点击概念火花时，根据提示词生成解释。

    Args:
        request: 包含提示词和概念文本

    Returns:
        AI 生成的解释
    """
    try:
        ai_service = AIService()

        # 构建 prompt
        prompt = f"""你是一个专业的知识解释助手。

**用户关注的概念**：{request.concept}

**解释要求**：{request.hint}

**格式要求**：
1. 用简洁、清晰的语言解释
2. 直接开始解释，不要有"这个概念是指..."这样的开场白
3. 总字数控制在 200 字以内

请开始你的解释："""

        # 调用 AI 生成（非流式）
        explanation = await ai_service.generate_simple_response(prompt)

        return ExplainResponse(explanation=explanation)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成解释失败: {str(e)}"
        )
