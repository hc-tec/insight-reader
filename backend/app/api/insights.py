"""洞察生成 API"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import time
import logging

from app.schemas.insight import (
    InsightRequest,
    InsightMetadata,
    ButtonGenerationRequest,
    ButtonGenerationResponse,
    FollowUpRequest,
    FollowUpButton
)
from app.services.ai_service import AIService
from app.core.task_manager import task_manager
from app.utils.auth import get_current_active_user
from app.models.models import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/insights/generate")
async def generate_insight(request: InsightRequest):
    """
    流式生成洞察卡片

    Args:
        request: 包含选中文本、上下文和意图的请求

    Returns:
        SSE 流式响应
    """
    ai_service = AIService()
    request_id = f"req_{int(time.time() * 1000)}"
    start_time = time.time()

    async def event_stream():
        """SSE 事件流生成器"""
        try:
            # 1. 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'request_id': request_id})}\n\n"

            full_content = ""
            full_reasoning = ""
            chunk_count = 0

            # 2. 流式生成洞察
            async for chunk in ai_service.generate_insight_stream(
                selected_text=request.selected_text,
                context=request.context,
                intent=request.intent,
                custom_question=request.custom_question,
                use_reasoning=request.use_reasoning,
                include_full_text=request.include_full_text,
                full_text=request.full_text
            ):
                # chunk 可能包含 content 或 reasoning_content
                if isinstance(chunk, dict):
                    if 'reasoning' in chunk:
                        full_reasoning += chunk['reasoning']
                        # 发送推理内容
                        yield f"data: {json.dumps({'type': 'reasoning', 'content': chunk['reasoning']})}\n\n"
                    if 'content' in chunk:
                        full_content += chunk['content']
                        # 发送正常内容
                        yield f"data: {json.dumps({'type': 'delta', 'content': chunk['content']})}\n\n"
                else:
                    # 兼容非推理模式
                    full_content += chunk
                    chunk_count += 1
                    yield f"data: {json.dumps({'type': 'delta', 'content': chunk})}\n\n"

            # 3. 计算元数据
            duration_ms = int((time.time() - start_time) * 1000)

            # 简化的 token 计数（实际应该使用 tiktoken）
            # 中文：1字≈1.5tokens，英文：1词≈1.3tokens
            estimated_tokens = int((len(full_content) + len(full_reasoning)) * 1.5)

            metadata = InsightMetadata(
                model=ai_service.model_used,
                tokens=estimated_tokens,
                duration_ms=duration_ms
            )

            # 4. 发送完成事件
            complete_event = {
                "type": "complete",
                "full_content": full_content,
                "full_reasoning": full_reasoning if full_reasoning else None,
                "metadata": metadata.model_dump()
            }
            yield f"data: {json.dumps(complete_event)}\n\n"

        except Exception as e:
            # 发送错误事件
            error_event = {
                "type": "error",
                "message": str(e),
                "code": "GENERATION_FAILED"
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )


@router.get("/insights/health")
async def health():
    """API 健康检查"""
    return {"status": "ok", "endpoint": "insights"}


# ============= 后台任务函数 =============

async def generate_buttons_task(
    selected_text: str,
    insight: str,
    intent: str,
    conversation_history: list
):
    """
    后台按钮生成任务

    Args:
        selected_text: 选中文本
        insight: 洞察内容
        intent: 意图
        conversation_history: 对话历史

    Returns:
        按钮列表
    """
    try:
        logger.info(f"[后台任务] 开始生成追问按钮")

        ai_service = AIService()
        buttons = await ai_service.generate_follow_up_buttons(
            selected_text=selected_text,
            insight=insight,
            intent=intent,
            conversation_history=conversation_history
        )

        logger.info(f"[后台任务] 按钮生成完成，共 {len(buttons)} 个")

        return {
            "status": "completed",
            "buttons": [btn.model_dump() for btn in buttons]
        }

    except Exception as e:
        logger.error(f"[后台任务] 按钮生成失败: {str(e)}", exc_info=True)

        # 返回默认按钮
        default_buttons = [
            {"id": "example_default", "label": "举个例子", "icon": "🌰", "category": "example"},
            {"id": "simplify_default", "label": "说得简单点", "icon": "🎯", "category": "simplify"},
            {"id": "extend_default", "label": "深入了解", "icon": "📚", "category": "extend"}
        ]

        return {
            "status": "completed",
            "buttons": default_buttons,
            "error": str(e)
        }


@router.post("/insights/generate-buttons")
async def generate_follow_up_buttons(
    request: ButtonGenerationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    生成智能追问按钮（异步版本）

    Args:
        request: 包含选中文本、洞察内容、意图和对话历史的请求
        current_user: 当前登录用户（从 JWT 获取）

    Returns:
        {
            "status": "completed" | "pending",
            "buttons": [...] | null,
            "task_id": str | null
        }
    """
    # 默认按钮（立即返回或失败时使用）
    default_buttons = [
        FollowUpButton(
            id="example_default",
            label="举个例子",
            icon="🌰",
            category="example"
        ),
        FollowUpButton(
            id="simplify_default",
            label="说得简单点",
            icon="🎯",
            category="simplify"
        ),
        FollowUpButton(
            id="extend_default",
            label="深入了解",
            icon="📚",
            category="extend"
        )
    ]

    try:
        # 提交后台任务
        task_id = task_manager.submit_task(
            "button_generation",
            generate_buttons_task,
            {
                "user_id": current_user.id,  # 从 JWT 获取用户 ID
                "insight_preview": request.insight[:50] + "..."
            },
            request.selected_text,
            request.insight,
            request.intent,
            request.conversation_history
        )

        logger.info(f"[API] 按钮生成任务已提交，任务ID: {task_id}")

        return {
            "status": "pending",
            "buttons": None,
            "task_id": task_id
        }

    except Exception as e:
        logger.error(f"[API] 提交按钮生成任务失败: {str(e)}")

        # 失败时直接返回默认按钮
        return {
            "status": "completed",
            "buttons": [btn.model_dump() for btn in default_buttons],
            "task_id": None
        }


@router.post("/insights/follow-up")
async def generate_follow_up_answer(request: FollowUpRequest):
    """
    流式生成追问回答

    Args:
        request: 包含原始文本、初始洞察、对话历史和追问问题的请求

    Returns:
        SSE 流式响应
    """
    ai_service = AIService()
    request_id = f"followup_{int(time.time() * 1000)}"
    start_time = time.time()

    async def event_stream():
        """SSE 事件流生成器"""
        try:
            # 1. 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'request_id': request_id})}\n\n"

            full_content = ""
            full_reasoning = ""

            # 2. 流式生成回答
            async for chunk in ai_service.generate_follow_up_answer_stream(
                selected_text=request.selected_text,
                initial_insight=request.initial_insight,
                conversation_history=request.conversation_history,
                follow_up_question=request.follow_up_question,
                use_reasoning=request.use_reasoning
            ):
                # chunk 可能包含 content 或 reasoning
                if isinstance(chunk, dict):
                    if 'reasoning' in chunk:
                        full_reasoning += chunk['reasoning']
                        yield f"data: {json.dumps({'type': 'reasoning', 'content': chunk['reasoning']})}\n\n"
                    if 'content' in chunk:
                        full_content += chunk['content']
                        yield f"data: {json.dumps({'type': 'delta', 'content': chunk['content']})}\n\n"
                else:
                    full_content += chunk
                    yield f"data: {json.dumps({'type': 'delta', 'content': chunk})}\n\n"

            # 3. 计算元数据
            duration_ms = int((time.time() - start_time) * 1000)
            estimated_tokens = int((len(full_content) + len(full_reasoning)) * 1.5)

            metadata = InsightMetadata(
                model=ai_service.model_used,
                tokens=estimated_tokens,
                duration_ms=duration_ms
            )

            # 4. 发送完成事件
            complete_event = {
                "type": "complete",
                "full_content": full_content,
                "full_reasoning": full_reasoning if full_reasoning else None,
                "metadata": metadata.model_dump()
            }
            yield f"data: {json.dumps(complete_event)}\n\n"

        except Exception as e:
            error_event = {
                "type": "error",
                "message": str(e),
                "code": "FOLLOWUP_FAILED"
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
