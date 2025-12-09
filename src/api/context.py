import asyncio
from typing import Any

import numpy as np
import numpy.typing as npt

from src.module.input.stream_decoder import StreamDecoder
from src.module.vad.vad_core import VADCore
from src.module.vad.vad_processor import VADProcessor
from src.module.llm.tool.definitions import ExecutableCommand


class Context:
    """
    封装了单个用户连接所需的所有状态和缓冲区。
    """
    
    # 队列大小限制配置
    AUDIO_INPUT_QUEUE_SIZE = 10000  # 原始音频数据队列
    AUDIO_NP_QUEUE_SIZE = 10000     # 解码后的音频队列
    AUDIO_SEGMENT_QUEUE_SIZE = 50 # VAD 分割后的语音段队列
    ASR_OUTPUT_QUEUE_SIZE = 20    # ASR 识别结果队列
    COMMAND_QUEUE_SIZE = 20       # 命令队列

    def __init__(self, context_id: str, decoder: StreamDecoder, vad_core: VADCore):
        self.context_id: str = context_id
        self.decoder: StreamDecoder = decoder
        self.audio_input_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=self.AUDIO_INPUT_QUEUE_SIZE)
        self.audio_np_queue: asyncio.Queue[npt.NDArray[np.float32]] = asyncio.Queue(maxsize=self.AUDIO_NP_QUEUE_SIZE)
        self.VADProcessor: VADProcessor = VADProcessor(vad_core, True)
        self.audio_segment_queue: asyncio.Queue[npt.NDArray[np.float32]] = asyncio.Queue(maxsize=self.AUDIO_SEGMENT_QUEUE_SIZE)
        self.asr_output_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=self.ASR_OUTPUT_QUEUE_SIZE)
        self.command_queue: asyncio.Queue[ExecutableCommand] = asyncio.Queue(maxsize=self.COMMAND_QUEUE_SIZE)
        self.location: str = "5G先锋体验区"  # 默认初始位置
        self.chat_history: list = []  # 聊天历史消息列表，存储 LangChain Message 对象
    
    def get_queue_stats(self) -> dict:
        """获取当前队列状态统计"""
        return {
            "context_id": self.context_id,
            "audio_input": {"current": self.audio_input_queue.qsize(), "max": self.AUDIO_INPUT_QUEUE_SIZE},
            "audio_np": {"current": self.audio_np_queue.qsize(), "max": self.AUDIO_NP_QUEUE_SIZE},
            "audio_segment": {"current": self.audio_segment_queue.qsize(), "max": self.AUDIO_SEGMENT_QUEUE_SIZE},
            "asr_output": {"current": self.asr_output_queue.qsize(), "max": self.ASR_OUTPUT_QUEUE_SIZE},
            "command": {"current": self.command_queue.qsize(), "max": self.COMMAND_QUEUE_SIZE},
            "vad_chunk": {"current": self.VADProcessor.chunk_queue.qsize(), "max": self.VADProcessor.chunk_queue.maxsize or 0}
        }
