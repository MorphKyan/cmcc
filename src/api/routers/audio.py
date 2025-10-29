import asyncio
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.context import Context
from src.core import dependencies
from src.services.audio_pipeline import run_vad_appender, run_vad_processor, run_asr_processor, run_llm_rag_processor
from src.module.input.stream_decoder import StreamDecoder

router = APIRouter(
    prefix="/api/audio",
    tags=["Audio Processing"]
)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    print(f"客户端 {client_id} 已连接。")

    decoder: Optional[StreamDecoder] = None

    context = Context(context_id=client_id, vad_core=dependencies.vad_core)
    dependencies.active_contexts[client_id] = context

    # 启动处理管道
    processing_tasks = [
        asyncio.create_task(run_vad_appender(context)),
        asyncio.create_task(run_vad_processor(context)),
        # asyncio.create_task(run_asr_processor(context)),
        # asyncio.create_task(run_llm_rag_processor(context, websocket))
    ]

    # 等待第一条元数据消息
    config_message = await websocket.receive_text()
    config = json.loads(config_message)

    if config.get("type") != "config":
        print("错误: 第一条消息必须是配置信息")
        await websocket.close(code=1008, reason="第一条消息必须是配置信息")
        return

    print(f"收到来自 {client_id} 的配置: {config}")

    # 根据前端配置初始化解码器
    decoder = StreamDecoder()

    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            decoder.feed_data(audio_chunk)

            # 检查解码器是否有新的PCM数据输出
            while True:
                pcm_frame = decoder.get_decoded_frame()
                if pcm_frame is None:
                    break
                # print(f"处理解码后的PCM数据，形状: {pcm_frame.shape}, 类型: {pcm_frame.dtype}")
                await context.audio_input_queue.put(pcm_frame)
    except WebSocketDisconnect:
        print(f"客户端 {client_id} 断开连接。")
    finally:
        # 清理资源
        print(f"正在为客户端 {client_id} 清理资源...")
        decoder.close()
        for task in processing_tasks:
            task.cancel()
        await asyncio.gather(*processing_tasks, return_exceptions=True)
        if client_id in dependencies.active_contexts:
            del dependencies.active_contexts[client_id]
        print(f"客户端 {client_id} 资源已清理")
