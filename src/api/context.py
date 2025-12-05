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

    def __init__(self, context_id: str, decoder: StreamDecoder, vad_core: VADCore):
        self.context_id: str = context_id
        self.decoder: StreamDecoder = decoder
        self.audio_input_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.audio_np_queue: asyncio.Queue[npt.NDArray[np.float32]] = asyncio.Queue()  # 缓冲输入的原始byte
        self.VADProcessor: VADProcessor = VADProcessor(vad_core,True)
        self.audio_segment_queue: asyncio.Queue[npt.NDArray[np.float32]] = asyncio.Queue()
        self.asr_output_queue: asyncio.Queue[str] = asyncio.Queue()
        self.command_queue: asyncio.Queue[ExecutableCommand] = asyncio.Queue()  # 结构化命令队列
        self.location: str = "5G先锋体验区"  # 默认初始位置
        self.chat_history: list = []  # 聊天历史消息列表，存储 LangChain Message 对象
