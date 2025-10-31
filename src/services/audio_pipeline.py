import asyncio

import numpy as np
import numpy.typing as npt
from fastapi import WebSocket
from loguru import logger

from src.api.context import Context
from src.core import dependencies  # 从中心依赖文件导入全局处理器


async def receive_loop(websocket: WebSocket, context: Context) -> None:
    logger.info("WebSocket接收已启动")
    while True:
        try:
            data_bytes = await websocket.receive_bytes()
            await context.audio_input_queue.put(data_bytes)
        except Exception as e:
            logger.exception("WebSocket接收错误")


async def decode_loop(context: Context) -> None:
    """负责解码并放入队列"""
    logger.info("解码已启动")
    while True:
        try:
            data_bytes = await context.audio_input_queue.get()
            context.decoder.feed_data(data_bytes)
            while True:
                pcm_frame = context.decoder.get_decoded_frame()
                if pcm_frame is None:
                    break
                logger.trace("处理解码后的PCM数据，形状: {shape}, 类型: {dtype}", shape=pcm_frame.shape, dtype=pcm_frame.dtype)
                await context.audio_np_queue.put(pcm_frame)
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
                logger.info("[VAD] 检测到语音段: {start:.2f}ms - {end:.2f}ms, 长度: {length:.2f}s", start=start, end=end,
                            length=len(audio_data) / 16000)
                await context.audio_segment_queue.put(audio_data)
        except Exception as e:
            logger.exception("VAD处理错误")


async def run_asr_processor(context: Context) -> None:
    """ASR处理逻辑代码"""
    logger.info("ASR处理器已启动")
    loop = asyncio.get_running_loop()
    while True:
        try:
            # 从VAD队列中获取分割好的语音片段
            segment: npt[np.float32] = await context.audio_segment_queue.get()
            # 使用ASR处理器处理音频数据
            recognized_text = await loop.run_in_executor(None, dependencies.asr_processor.process_audio_data, segment)
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
    loop = asyncio.get_running_loop()
    while True:
        try:
            recognized_text = await context.asr_output_queue.get()
            retrieved_docs = await loop.run_in_executor(None, dependencies.rag_processor.retrieve_context, recognized_text)
            llm_response = await loop.run_in_executor(None, dependencies.llm_processor.get_response, recognized_text, retrieved_docs)
            logger.info("[大模型响应] {llm_response}", llm_response=llm_response)
            await context.function_calling_queue.put(llm_response)

            # 通过WebSocket发送响应
            await websocket.send_text(llm_response)

        except Exception as e:
            logger.exception("[LLM/RAG错误]")
            # 可以选择是否继续处理或退出
            # break
