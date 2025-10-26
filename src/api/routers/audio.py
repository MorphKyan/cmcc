import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.context import Context
from src.core import dependencies
from src.services.audio_pipeline import run_vad_processor, run_asr_processor, run_llm_rag_processor

router = APIRouter(
    prefix="/api/audio",
    tags=["Audio Processing"]
)

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    print(f"客户端 {client_id} 已连接。")

    context = Context(context_id=client_id)
    dependencies.active_contexts[client_id] = context

    # 启动处理管道
    processing_tasks = [
        asyncio.create_task(run_vad_processor(context)),
        asyncio.create_task(run_asr_processor(context)),
        asyncio.create_task(run_llm_rag_processor(context, websocket))
    ]

    try:
        while True:
            audio_data = await websocket.receive_bytes()
            await context.audio_input_queue.put(audio_data)
    except WebSocketDisconnect:
        print(f"客户端 {client_id} 断开连接。")
    finally:
        # 清理资源
        print(f"正在为客户端 {client_id} 清理资源...")
        for task in processing_tasks:
            task.cancel()
        await asyncio.gather(*processing_tasks, return_exceptions=True)
        if client_id in dependencies.active_contexts:
            del dependencies.active_contexts[client_id]
        print(f"客户端 {client_id} 资源已清理")