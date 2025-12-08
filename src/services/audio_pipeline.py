import asyncio
import json

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


async def run_llm_rag_processor(context: Context, websocket: WebSocket) -> None:
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

            # 自动保存对话到历史
            context.chat_history.append(HumanMessage(content=recognized_text))
            context.chat_history.append(ai_message)

            # 当LLM未返回任何命令时，向前端发送提示
            if not commands:
                no_command_payload = json.dumps({
                    "type": "system_message",
                    "user_id": context.context_id,
                    "message": "抱歉，我无法理解您的指令。请尝试重新描述您的需求。"
                }, ensure_ascii=False)
                await websocket.send_text(no_command_payload)
                logger.info("[提示] 未识别到有效指令，已通知用户")
                continue

            # 构建可执行命令对象
            executable_cmd = ExecutableCommand(
                user_id=context.context_id,
                commands=commands
            )

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
            execution_results: list[dict] = []
            
            # 1. 先执行本地命令（如更新位置）
            for cmd in executable_cmd.get_local_commands():
                result = await _execute_local_command(cmd, context)
                execution_results.append(result)
                # 发送本地命令执行结果到前端
                local_result_payload = json.dumps({
                    "type": "command_result",
                    "user_id": executable_cmd.user_id,
                    "command": cmd.model_dump(),
                    "result": result
                }, ensure_ascii=False)
                await websocket.send_text(local_result_payload)
                logger.info("[本地命令结果] action={action}, success={success}, message={message}", 
                           action=cmd.action, success=result.get("success"), message=result.get("message"))
            
            # 2. 发送远程命令到前端
            remote_commands = executable_cmd.get_remote_commands()
            if remote_commands:
                payload = executable_cmd.to_websocket_payload()
                logger.info("[发送命令] user={user_id}, count={count}", 
                           user_id=executable_cmd.user_id, count=len(remote_commands))
                await websocket.send_text(payload)
            
            # 3. 发送执行摘要到前端（用户友好的提示）
            summary_messages: list[str] = []
            for result in execution_results:
                if result.get("success"):
                    summary_messages.append(result.get("message", "操作成功"))
            for cmd in remote_commands:
                summary_messages.append(_get_command_description(cmd))
            
            if summary_messages:
                summary_payload = json.dumps({
                    "type": "execution_summary",
                    "user_id": executable_cmd.user_id,
                    "messages": summary_messages,
                    "summary": "正在执行：" + "；".join(summary_messages)
                }, ensure_ascii=False)
                await websocket.send_text(summary_payload)
                
        except Exception as e:
            logger.exception("[命令执行错误]")


async def _execute_local_command(cmd: ExhibitionCommand, context: Context) -> dict:
    """执行本地命令，返回执行结果"""
    if cmd.action == "update_location" and cmd.target:
        old_location = context.location
        context.location = cmd.target
        logger.info("[位置更新] {old} -> {new}", old=old_location, new=cmd.target)
        return {
            "success": True,
            "action": cmd.action,
            "message": f"位置从「{old_location}」更新为「{cmd.target}」" if old_location else f"位置设置为「{cmd.target}」"
        }
    return {
        "success": False,
        "action": cmd.action,
        "message": f"未知的本地命令：{cmd.action}"
    }


def _get_command_description(cmd: ExhibitionCommand) -> str:
    """获取命令的用户友好描述"""
    action_descriptions = {
        "play": lambda c: f"在「{c.device}」上播放「{c.target}」",
        "open_media": lambda c: f"在「{c.device}」上打开「{c.target}」",
        "open": lambda c: f"打开「{c.target}」",
        "close": lambda c: f"关闭「{c.target}」",
        "seek": lambda c: f"将「{c.device}」跳转到{c.value}秒",
        "set_volume": lambda c: f"将「{c.device}」音量设置为{c.value}",
        "adjust_volume": lambda c: f"{'提高' if c.value == 'up' else '降低'}「{c.device}」音量",
    }
    
    if cmd.action in action_descriptions:
        return action_descriptions[cmd.action](cmd)
    return f"执行{cmd.action}操作"
