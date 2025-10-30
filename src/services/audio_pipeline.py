import numpy as np
import numpy.typing as npt
from fastapi import WebSocket
from loguru import logger

from src.api.context import Context
from src.core import dependencies  # 从中心依赖文件导入全局处理器
from src.module.input.stream_decoder import StreamDecoder


async def receive_and_decode_loop(websocket: WebSocket, context: Context, decoder: StreamDecoder):
    """
    一个独立的任务，专门负责接收、解码并放入队列。
    """
    while True:
        audio_chunk = await websocket.receive_bytes()
        decoder.feed_data(audio_chunk)
        while True:
            pcm_frame = decoder.get_decoded_frame()
            if pcm_frame is None:
                break
            logger.trace("处理解码后的PCM数据，形状: {shape}, 类型: {dtype}", shape=pcm_frame.shape, dtype=pcm_frame.dtype)
            await context.audio_input_queue.put(pcm_frame)


async def run_vad_appender(context: Context):
    """VAD处理逻辑代码"""
    logger.info(f"[{context.context_id}] VAD处理器已启动。")
    while True:
        try:
            # 从WebSocket接收音频数据
            audio_bytes = await context.audio_input_queue.get()

            # 使用VAD检测语音活动
            context.VADProcessor.append_audio(audio_bytes)

        except Exception as e:
            logger.error(f"[{context.context_id}][VAD输入错误] {e}")
            # 可以选择是否继续处理或退出
            # break


async def run_vad_processor(context: Context):
    while True:
        try:
            result = await context.VADProcessor.process_chunk()
            speech_segments = context.VADProcessor.process_result(result)
            for segment in speech_segments:
                start, end, audio_data = segment
                logger.info(f"[{context.context_id}][VAD] 检测到语音段: {start:.2f}ms - {end:.2f}ms, 长度: {len(audio_data) / 16000:.2f}s")
                await context.audio_segment_queue.put(audio_data)
        except Exception as e:
            logger.error(f"[{context.context_id}][VAD处理错误] {e}")


async def run_asr_processor(context: Context):
    """ASR处理逻辑代码"""
    logger.info(f"[{context.context_id}] ASR处理器已启动。")
    while True:
        try:
            # 从VAD队列中获取分割好的语音片段
            segment: npt[np.float32] = await context.audio_segment_queue.get()
            # 使用ASR处理器处理音频数据
            recognized_text = dependencies.asr_processor.process_audio_data(segment)

            if recognized_text and recognized_text.strip():
                logger.info(f"[{context.context_id}][识别结果] {recognized_text}")
                await context.asr_output_queue.put(recognized_text)

        except Exception as e:
            logger.error(f"[{context.context_id}][ASR错误] {e}")
            # 可以选择是否继续处理或退出
            # break


async def run_llm_rag_processor(context: Context, websocket: WebSocket):
    """LLM/RAG处理逻辑代码"""
    logger.info(f"[{context.context_id}] LLM/RAG处理器已启动。")
    while True:
        try:
            recognized_text = await context.asr_output_queue.get()
            retrieved_docs = dependencies.rag_processor.retrieve_context(recognized_text)
            llm_response = dependencies.llm_processor.get_response(recognized_text, retrieved_docs)
            logger.info(f"[{context.context_id}][大模型响应] {llm_response}")
            await context.function_calling_queue.put(llm_response)

            # 通过WebSocket发送响应
            await websocket.send_text(llm_response)

        except Exception as e:
            logger.error(f"[{context.context_id}][LLM/RAG错误] {e}")
            # 可以选择是否继续处理或退出
            # break
