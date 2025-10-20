"""洞察生成 API"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import time

from app.schemas.insight import (
    InsightRequest,
    InsightMetadata,
    ButtonGenerationRequest,
    ButtonGenerationResponse,
    FollowUpRequest
)
from app.services.ai_service import AIService

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
                use_reasoning=request.use_reasoning
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


@router.post("/insights/generate-buttons", response_model=ButtonGenerationResponse)
async def generate_follow_up_buttons(request: ButtonGenerationRequest):
    """
    生成智能追问按钮

    Args:
        request: 包含选中文本、洞察内容、意图和对话历史的请求

    Returns:
        追问按钮列表（3-4个）
    """
    try:
        ai_service = AIService()

        buttons = await ai_service.generate_follow_up_buttons(
            selected_text=request.selected_text,
            insight=request.insight,
            intent=request.intent,
            conversation_history=request.conversation_history
        )

        return ButtonGenerationResponse(buttons=buttons)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成追问按钮失败: {str(e)}")


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
