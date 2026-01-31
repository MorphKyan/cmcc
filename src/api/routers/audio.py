import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import ValidationError

from src.api.context import Context
from src.api.schemas import WebSocketConfig
from src.config.logging_config import request_id_var
from src.core import dependencies
from src.module.input.stream_decoder import StreamDecoder
from src.services.audio_pipeline import run_vad_processor, run_decode_vad_appender, run_asr_processor, run_llm_rag_processor, receive_loop, run_command_executor

router = APIRouter(
    prefix="/audio",
    tags=["Audio Processing"]
)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str) -> None:
    await websocket.accept()
    token = request_id_var.set(client_id)
    logger.info("客户端已连接")

    context: Context | None = None
    all_tasks: list[asyncio.Task] = []
    try:
        # 等待第一条元数据消息
        config_message = await websocket.receive_text()
        try:
            config_data = json.loads(config_message)
            config = WebSocketConfig(**config_data)
            if config.type != "config":
                raise ValueError("第一条消息必须是配置信息")
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            logger.exception("配置消息无效")
            await websocket.close(code=1008, reason=f"无效的配置消息: {e}")
            return

        logger.info("收到配置: {config}", config=config_data)

        # 根据前端配置初始化解码器
        decoder = StreamDecoder()
        # 初始化与配置
        context = Context(context_id=client_id, decoder=decoder, vad_core=dependencies.vad_core)
        dependencies.active_contexts[client_id] = context

        # 启动处理管道
        all_tasks = [
            asyncio.create_task(receive_loop(websocket, context)),
            asyncio.create_task(run_decode_vad_appender(context)),
            asyncio.create_task(run_vad_processor(context)),
            asyncio.create_task(run_asr_processor(context, websocket)),
            asyncio.create_task(run_llm_rag_processor(context, websocket)),
            asyncio.create_task(run_command_executor(context, websocket))
        ]

        done, pending = await asyncio.wait(all_tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            if task.exception():
                raise task.exception()

    except WebSocketDisconnect:
        logger.info("客户端断开连接")
    except Exception as e:
        logger.exception("WebSocket 处理过程中发生意外错误")
    finally:
        # 清理资源
        logger.info("正在清理资源...")

        # 取消所有仍在运行的任务
        for task in all_tasks:
            if not task.done():
                task.cancel()
        
        # 等待所有任务真正取消，设置超时防止卡死
        if all_tasks:
            try:
                await asyncio.wait_for(asyncio.gather(*all_tasks, return_exceptions=True), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("WebSocket任务清理超时，部分任务可能未正常退出")

        if client_id in dependencies.active_contexts:
            del dependencies.active_contexts[client_id]

        logger.info("资源已清理")
        request_id_var.reset(token)
