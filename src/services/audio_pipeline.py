import asyncio

import numpy as np
import numpy.typing as npt
from fastapi import WebSocket
from loguru import logger
from langchain_core.messages import HumanMessage

from src.api.context import Context
from src.core import dependencies
from src.module.llm.tool.definitions import ExecutableCommand, ExhibitionCommand


async def receive_loop(websocket: WebSocket, context: Context) -> None:
    logger.info("WebSocket接收已启动")
    while True:
        try:
            data_bytes = await websocket.receive_bytes()
            logger.trace("WebSocket receive bytes size {size}", size=len(data_bytes))
            await context.audio_input_queue.put(data_bytes)
            logger.trace("WebSocket put audio_input_queue size {size}", size=len(data_bytes))
        except Exception as e:
            logger.error("WebSocket接收错误，{e}", e=e)
            break


async def decode_loop(context: Context) -> None:
    """负责解码并放入队列"""
    logger.info("解码已启动")
    while True:
        try:
            data_bytes = await context.audio_input_queue.get()
            # 将bytes转换为int16数组，然后归一化到-1.0到1.0的float32范围
            int16_array = np.frombuffer(data_bytes, dtype=np.int16)
            float32_array = int16_array.astype(np.float32) / 32767.0
            logger.trace("处理PCM数据，形状: {shape}, 类型: {dtype}", shape=float32_array.shape, dtype=float32_array.dtype)
            await context.audio_np_queue.put(float32_array)
        except Exception as e:
            logger.exception("解码错误")


async def run_vad_appender(context: Context) -> None:
    """VAD处理逻辑代码"""
    logger.info("VAD处理器已启动")
    while True:
        try:
            # 从WebSocket接收音频数据
            audio = await context.audio_np_queue.get()

            # 使用VAD检测语音活动
            context.VADProcessor.append_audio(audio)

        except Exception as e:
            logger.exception("VAD输入错误")
            # 可以选择是否继续处理或退出
            # break


async def run_vad_processor(context: Context) -> None:
    while True:
        try:
            result = await context.VADProcessor.process_chunk()
            speech_segments = context.VADProcessor.process_result(result)
            for segment in speech_segments:
                start, end, audio_data = segment
                logger.info("[VAD] 检测到语音段: {start:.2f}s - {end:.2f}s, 长度: {length:.2f}s", start=start / 1000, end=end / 1000,
                            length=len(audio_data) / 16000)
                await context.audio_segment_queue.put(audio_data)
        except Exception as e:
            logger.exception("VAD处理错误")


async def run_asr_processor(context: Context) -> None:
    """ASR处理逻辑代码"""
    logger.info("ASR处理器已启动")
    while True:
        try:
            # 从VAD队列中获取分割好的语音片段
            segment: npt[np.float32] = await context.audio_segment_queue.get()
            # 使用ASR处理器处理音频数据
            recognized_text = await asyncio.to_thread(dependencies.asr_processor.process_audio_data, segment)
            if recognized_text and recognized_text.strip():
                logger.info("[识别结果] {recognized_text}", recognized_text=recognized_text)
                await context.asr_output_queue.put(recognized_text)

        except Exception as e:
            logger.exception("[ASR错误]")
            # 可以选择是否继续处理或退出
            # break


async def run_llm_rag_processor(context: Context) -> None:
    """LLM/RAG处理逻辑代码"""
    logger.info("LLM/RAG处理器已启动")
    
    # 导入MetadataType用于分类检索
    from src.module.rag.base_rag_processor import MetadataType

    while True:
        try:
            recognized_text = await context.asr_output_queue.get()
            
            # 分别检索每种类型的文档，每种5个
            door_docs = await dependencies.rag_processor.retrieve_context(
                recognized_text, metadata_types=[MetadataType.DOOR], top_k=5
            )
            video_docs = await dependencies.rag_processor.retrieve_context(
                recognized_text, metadata_types=[MetadataType.VIDEO], top_k=5
            )
            device_docs = await dependencies.rag_processor.retrieve_context(
                recognized_text, metadata_types=[MetadataType.DEVICE], top_k=5
            )
            
            # 构建分类后的RAG文档字典
            retrieved_docs_by_type = {
                "door": door_docs,
                "video": video_docs,
                "device": device_docs
            }

            # 获取聊天历史
            chat_history_messages = context.chat_history

            # 执行指令重试，获取AI消息和命令列表
            ai_message, commands = await dependencies.llm_processor.get_response_with_retries(
                user_input=recognized_text,
                rag_docs=retrieved_docs_by_type,
                user_location=context.location,
                chat_history=chat_history_messages
            )
            
            logger.info("[大模型响应] 返回 {count} 个命令", count=len(commands))

            # 构建可执行命令对象
            executable_cmd = ExecutableCommand(
                user_id=context.context_id,
                commands=commands
            )

            # 自动保存对话到历史
            context.chat_history.append(HumanMessage(content=recognized_text))
            context.chat_history.append(ai_message)

            # 放入命令队列，由执行器异步处理
            await context.command_queue.put(executable_cmd)

        except Exception as e:
            logger.exception("[LLM/RAG错误]")
            # 可以选择是否继续处理或退出
            # break


async def run_command_executor(context: Context, websocket: WebSocket) -> None:
    """异步执行命令：本地执行或发送到前端"""
    logger.info("命令执行器已启动")
    while True:
        try:
            executable_cmd = await context.command_queue.get()
            
            # 1. 先执行本地命令（如更新位置）
            for cmd in executable_cmd.get_local_commands():
                await _execute_local_command(cmd, context)
            
            # 2. 发送远程命令到前端
            remote_commands = executable_cmd.get_remote_commands()
            if remote_commands:
                payload = executable_cmd.to_websocket_payload()
                logger.info("[发送命令] user={user_id}, count={count}", 
                           user_id=executable_cmd.user_id, count=len(remote_commands))
                await websocket.send_text(payload)
                
        except Exception as e:
            logger.exception("[命令执行错误]")


async def _execute_local_command(cmd: ExhibitionCommand, context: Context) -> None:
    """执行本地命令"""
    if cmd.action == "update_location" and cmd.target:
        old_location = context.location
        context.location = cmd.target
        logger.info("[位置更新] {old} -> {new}", old=old_location, new=cmd.target)
