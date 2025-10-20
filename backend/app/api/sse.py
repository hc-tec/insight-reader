# -*- coding: utf-8 -*-
"""
SSE (Server-Sent Events) 实时通知服务
用于通知前端分析完成等事件
"""

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from asyncio import Queue
import asyncio
import json
import time
from typing import Dict

router = APIRouter()

# 用户通知队列字典 {user_id: Queue}
user_queues: Dict[int, Queue] = {}


async def get_user_queue(user_id: int) -> Queue:
    """获取或创建用户的通知队列"""
    if user_id not in user_queues:
        user_queues[user_id] = Queue()
    return user_queues[user_id]


async def notify_analysis_complete(user_id: int, article_id: int):
    """
    通知用户文章分析完成

    Args:
        user_id: 用户 ID
        article_id: 文章 ID
    """
    queue = await get_user_queue(user_id)
    await queue.put({
        "event": "analysis_complete",
        "data": {
            "article_id": article_id,
            "timestamp": time.time()
        }
    })
    print(f"已通知用户 {user_id} 文章 {article_id} 分析完成")


async def notify_analysis_progress(user_id: int, article_id: int, stage: str, progress: int):
    """
    通知用户分析进度

    Args:
        user_id: 用户 ID
        article_id: 文章 ID
        stage: 当前阶段（如 "extracting_concepts", "analyzing_arguments"）
        progress: 进度百分比 (0-100)
    """
    queue = await get_user_queue(user_id)
    await queue.put({
        "event": "analysis_progress",
        "data": {
            "article_id": article_id,
            "stage": stage,
            "progress": progress,
            "timestamp": time.time()
        }
    })


async def event_generator(user_id: int):
    """
    SSE 事件生成器

    生成服务器发送事件流，包括：
    - connected: 连接建立事件
    - heartbeat: 心跳保持连接
    - analysis_complete: 分析完成通知
    - analysis_progress: 分析进度更新
    """
    queue = await get_user_queue(user_id)

    # 发送初始连接事件
    yield f"event: connected\ndata: {json.dumps({'user_id': user_id, 'timestamp': time.time()})}\n\n"

    print(f"用户 {user_id} SSE 连接已建立")

    while True:
        try:
            # 等待新事件（30秒超时，用于发送心跳）
            message = await asyncio.wait_for(queue.get(), timeout=30.0)

            # 发送事件
            event_type = message.get("event", "message")
            data = json.dumps(message.get("data", {}))
            yield f"event: {event_type}\ndata: {data}\n\n"

            print(f"发送事件给用户 {user_id}: {event_type}")

        except asyncio.TimeoutError:
            # 发送心跳保持连接
            yield f"event: heartbeat\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
            # print(f"发送心跳给用户 {user_id}")


@router.get("/api/v1/sse/analysis-notifications")
async def sse_notifications(
    user_id: int = Query(..., description="用户ID")
):
    """
    SSE 通知端点

    用户连接此端点后，将接收实时的分析状态更新。

    事件类型：
    - connected: 连接成功
    - heartbeat: 心跳（每30秒）
    - analysis_complete: 分析完成
    - analysis_progress: 分析进度
    """
    return StreamingResponse(
        event_generator(user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )


# 清理断开连接的队列
async def cleanup_user_queue(user_id: int):
    """
    清理用户队列（当连接断开时）

    Args:
        user_id: 用户 ID
    """
    if user_id in user_queues:
        del user_queues[user_id]
        print(f"用户 {user_id} SSE 队列已清理")
