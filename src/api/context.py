import asyncio

import numpy as np


class Context:
    """
    封装了单个用户连接所需的所有状态和缓冲区。
    """

    def __init__(self, context_id: int):
        self.context_id: int = context_id
        self.audio_input_queue: asyncio.Queue = asyncio.Queue()  # 缓冲输入的原始byte
        self.audio_input_buffer: bytearray = bytearray()  # vad前置缓冲，等待数据满足足够的chunk size
        self.audio_input_chunk: asyncio.Queue[np.ndarray] = asyncio.Queue() # 输入音频切割为chunk
        self.audio_input_buffer_start_index: int = 0 # vad 流式处理，需要记录当前audio_input_buffer中头的偏移量
        self.last_start_time: int = 0 # vad 流式处理，需要记录当前audio_input_buffer的头所对应的时间
        self.vad_cache = {}
        self.speech_text_queue: asyncio.Queue = asyncio.Queue()

    def get_audio_from_segments(self, segments: list) -> np.ndarray:
        for start, end in segments:
            # 情况一：新的语音段开始
            if start != -1 and end == -1:
                if self.last_start_time is None:
                    self.last_start_time = start

            # 情况二：语音段结束
            elif start == -1 and end != -1:
                if self.last_start_time is not None:
                    # 语音段已完整，提取音频
                    start_sample = int(self.last_start_time * self.sample_rate / 1000) - self.buffer_start_sample_num
                    end_sample = int(end * self.sample_rate / 1000) - self.buffer_start_sample_num

                    segment_audio = self.audio_buffer[max(0, start_sample):end_sample]
                    if segment_audio.size == 0:
                        print(f"[VAD警告] 检测到空的音频段: {self.last_start_time}ms - {end}ms")
                    completed_segments.append((self.last_start_time, end, segment_audio))
                    last_end_time = end

                    # 重置当前语音段状态
                    self.last_start_time = None

            # 情况三：短语音段（在单个块内开始和结束）
            elif start != -1 and end != -1:
                # 如果之前有一个未结束的段，先将其结束
                if self.last_start_time is not None:
                    start_sample = int(self.last_start_time * self.sample_rate / 1000) - self.buffer_start_sample_num
                    end_sample = int(start * self.sample_rate / 1000) - self.buffer_start_sample_num

                    segment_audio = self.audio_buffer[max(0, start_sample):end_sample]
                    completed_segments.append((self.last_start_time, start, segment_audio))
                    self.last_start_time = None

                start_sample = int(start * self.sample_rate / 1000) - self.buffer_start_sample_num
                end_sample = int(end * self.sample_rate / 1000) - self.buffer_start_sample_num

                segment_audio = self.audio_buffer[max(0, start_sample):end_sample]
                completed_segments.append((start, end, segment_audio))
                last_end_time = end

        if last_end_time != -1:
            # 移除已处理的音频数据
            remove_samples = int(last_end_time * self.sample_rate / 1000)
            if remove_samples > 0:
                print(
                    f"[VAD] 移除已处理的音频数据: {self.buffer_start_sample_num}到{remove_samples}的采样点, 当前缓存起始时间为: {remove_samples / self.sample_rate:.2f}秒")
                self.audio_buffer = self.audio_buffer[remove_samples - self.buffer_start_sample_num:]
                self.buffer_start_sample_num = remove_samples
