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


# ==================== 性能指标 API ====================

@router.get("/metrics")
async def get_performance_metrics(minutes: int = 5):
    """
    获取最近 N 分钟的性能指标数据
    
    Args:
        minutes: 获取最近多少分钟的数据，默认5分钟，最大5分钟
        
    Returns:
        各处理阶段的耗时数据时序列表
    """
    # 限制最大查询范围为5分钟
    minutes = min(minutes, 5)
    return {
        "timestamp": datetime.now().isoformat(),
        **dependencies.metrics_manager.get_metrics(minutes)
    }


@router.get("/metrics/stats")
async def get_performance_stats():
    """
    获取性能指标统计摘要
    
    Returns:
        各处理阶段的平均值、最大值、最小值、计数等统计信息
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "stats": dependencies.metrics_manager.get_stats()
    }


@router.get("/metrics/stream")
async def stream_performance_metrics():
    """
    SSE 实时推送性能指标
    
    每秒推送一次最近1分钟的性能指标数据和统计摘要。
    
    使用方式:
    ```javascript
    const eventSource = new EventSource('/api/monitoring/metrics/stream');
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Performance metrics:', data);
    };
    ```
    """
    async def generate():
        while True:
            data = {
                "timestamp": datetime.now().isoformat(),
                **dependencies.metrics_manager.get_metrics(minutes=1),
                "stats": dependencies.metrics_manager.get_stats()
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

