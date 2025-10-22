# -*- coding: utf-8 -*-
"""
SSE (Server-Sent Events) 实时通知服务
用于通知前端分析完成等事件
"""

import asyncio
import json
import time
import logging
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from app.core.task_manager import task_manager
from app.utils.auth import verify_token

logger = logging.getLogger(__name__)
router = APIRouter()


async def event_generator(user_id: int):
    """
    SSE 事件生成器

    生成服务器发送事件流，包括：
    - connected: 连接建立事件
    - heartbeat: 心跳保持连接
    - task_started: 任务开始
    - task_completed: 任务完成
    - task_failed: 任务失败
    """
    # 创建新的 SSE 连接
    queue = task_manager.sse_manager.add_connection(user_id)

    try:
        # 发送初始连接事件
        yield f"event: connected\ndata: {json.dumps({'user_id': user_id, 'timestamp': time.time()})}\n\n"
        logger.info(f"[SSE] 用户 {user_id} 连接已建立")

        while True:
            try:
                # 等待新事件（30秒超时，用于发送心跳）
                event = await asyncio.wait_for(queue.get(), timeout=30.0)

                # 发送事件
                event_type = event.get("type", "message")
                data = json.dumps(event.get("data", {}))
                yield f"event: {event_type}\ndata: {data}\n\n"

                logger.info(f"[SSE] 发送事件给用户 {user_id}: {event_type}")

            except asyncio.TimeoutError:
                # 发送心跳保持连接
                yield f"event: heartbeat\ndata: {json.dumps({'timestamp': time.time()})}\n\n"

    except asyncio.CancelledError:
        logger.info(f"[SSE] 用户 {user_id} 连接被取消")
    except Exception as e:
        logger.error(f"[SSE] 用户 {user_id} 连接异常: {str(e)}")
    finally:
        # 清理连接
        task_manager.sse_manager.remove_connection(user_id, queue)
        logger.info(f"[SSE] 用户 {user_id} 连接已关闭")


@router.get("/api/v1/sse/analysis-notifications")
async def sse_notifications(
    token: str = Query(..., description="JWT 认证 token")
):
    """
    SSE 通知端点

    用户连接此端点后，将接收实时的任务状态更新。

    Args:
        token: JWT 认证 token

    事件类型：
    - connected: 连接成功
    - heartbeat: 心跳（每30秒）
    - task_started: 任务开始
    - task_completed: 任务完成
    - task_failed: 任务失败
    """
    try:
        # 验证 token 并获取 user_id
        payload = verify_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="无效的认证 token")

        # JWT payload 中 user_id 存储在 "sub" 字段中
        user_id_str = payload.get("sub")

        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token 中缺少用户信息")

        # 转换为整数
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="无效的用户ID格式")

        logger.info(f"[SSE] 用户 {user_id} 正在建立 SSE 连接")

        return StreamingResponse(
            event_generator(user_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SSE] Token 验证失败: {str(e)}")
        raise HTTPException(status_code=401, detail="认证失败")
