import asyncio

import numpy as np
import numpy.typing as npt
from fastapi import WebSocket
from loguru import logger

from src.api.context import Context
from src.core import dependencies
from src.module.llm.smart_retry_handler import SmartRetryHandler


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

    # 创建指令重试处理器
    retry_handler = SmartRetryHandler(dependencies.llm_processor.settings)

    while True:
        try:
            recognized_text = await context.asr_output_queue.get()
            retrieved_docs = await dependencies.rag_processor.retrieve_context(recognized_text)

            # 执行指令重试
            retry_result = await retry_handler.execute_instruction_retry(
                original_input=recognized_text,
                llm_function=dependencies.llm_processor.get_response,
                rag_docs=retrieved_docs,
                user_location=context.location
            )

            # 记录重试统计信息
            if retry_result.attempt_count > 1:
                logger.info(f"[重试统计] 尝试次数: {retry_result.attempt_count}, 总耗时: {retry_result.total_time:.2f}s, 成功: {retry_result.success}")

            llm_response = retry_result.response
            logger.info("[大模型响应] {llm_response}", llm_response=llm_response)

            # 处理位置更新
            try:
                import json
                commands = json.loads(llm_response)
                if isinstance(commands, list):
                    for command in commands:
                        if command.get("action") == "update_location":
                            new_location = command.get("target")
                            if new_location:
                                logger.info(f"[位置更新] 用户位置从 '{context.location}' 更新为 '{new_location}'")
                                context.location = new_location
            except Exception as e:
                logger.warning(f"解析LLM响应以更新位置时出错: {e}")

            await context.function_calling_queue.put(llm_response)

            # 通过WebSocket发送响应
            await websocket.send_text(llm_response)

        except Exception as e:
            logger.exception("[LLM/RAG错误]")
            # 可以选择是否继续处理或退出
            # break
