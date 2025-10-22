import asyncio


class Context:
    """
    封装了单个用户连接所需的所有状态和缓冲区。
    """

    def __init__(self, context_id: int):
        self.context_id: int = context_id
        self.audio_input_queue: asyncio.Queue = asyncio.Queue()  # 缓冲输入的原始byte
        self.audio_segment_queue: asyncio.Queue = asyncio.Queue()
        self.speech_text_queue: asyncio.Queue = asyncio.Queue()
        self.function_calling_queue: asyncio.Queue = asyncio.Queue()
