"""
监控 API 路由

提供系统状态、队列深度等实时监控接口。
"""
import asyncio
import json
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger

from src.core import dependencies

router = APIRouter(
    prefix="/monitoring",
    tags=["Monitoring"]
)


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(dependencies.active_contexts)
    }


@router.get("/queues")
async def get_queue_stats():
    """获取所有活跃连接的队列状态快照"""
    stats = []
    for context_id, context in dependencies.active_contexts.items():
        try:
            stats.append(context.get_queue_stats())
        except Exception as e:
            logger.warning("获取队列状态失败: {context_id}, {e}", context_id=context_id, e=e)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(dependencies.active_contexts),
        "contexts": stats
    }


@router.get("/queues/stream")
async def stream_queue_stats():
    """
    SSE 实时推送队列状态
    
    使用方式:
    ```javascript
    const eventSource = new EventSource('/api/monitoring/queues/stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Queue stats:', data);
    };
    ```
    """
    async def generate():
        while True:
            stats = []
            for context_id, context in list(dependencies.active_contexts.items()):
                try:
                    stats.append(context.get_queue_stats())
                except Exception as e:
                    logger.warning("获取队列状态失败: {context_id}", context_id=context_id)
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "active_connections": len(dependencies.active_contexts),
                "contexts": stats
            }
            
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1)  # 每秒推送一次
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 nginx 缓冲
        }
    )


@router.get("/queues/{context_id}")
async def get_context_queue_stats(context_id: str):
    """获取指定连接的队列状态"""
    context = dependencies.active_contexts.get(context_id)
    if not context:
        return {"error": f"Context {context_id} not found", "active_contexts": list(dependencies.active_contexts.keys())}
    
    return {
        "timestamp": datetime.now().isoformat(),
        **context.get_queue_stats()
    }
