import asyncio

import numpy.typing as npt
import numpy as np
from src.module import VADProcessor
from src.module.vad.vad_core import VADCore


class Context:
    """
    封装了单个用户连接所需的所有状态和缓冲区。
    """

    def __init__(self, context_id: str, vad_core: VADCore):
        self.context_id: str = context_id
        self.audio_input_queue: asyncio.Queue = asyncio.Queue()  # 缓冲输入的原始byte
        self.VADProcessor: VADProcessor = VADProcessor(vad_core)
        self.audio_segment_queue: asyncio.Queue[npt.NDArray[np.float32]] = asyncio.Queue()
        self.asr_output_queue: asyncio.Queue = asyncio.Queue()
        self.function_calling_queue: asyncio.Queue = asyncio.Queue()
