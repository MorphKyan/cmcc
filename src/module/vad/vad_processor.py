#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import numpy as np
import numpy.typing as npt
from src.module.vad.vad_core import VADCore


class VADProcessor:
    def __init__(self, vad_core: VADCore):
        self.vad_core = vad_core
        self.sample_rate = vad_core.sample_rate
        self.chunk_size_samples = int(self.vad_core.chunk_size * self.sample_rate / 1000)
        self.cache = {}
        self.input_buffer: npt.NDArray[np.float32] = np.array([], dtype=np.float32)
        self.history_buffer_max_samples = 30 * self.sample_rate  # 时长*采样率
        self.history_buffer: npt.NDArray[np.float32] = np.array([], dtype=np.float32)
        self.history_buffer_head_index = 0  # buffer头的偏移量
        self.last_start_time = None  # 上一segment的开始时间戳（累积）
        self.last_end_time = None  # 上一segment的结束时间戳（累积）
        self.last_start_time_ms = None  # Start timestamp of the current speech segment in milliseconds
        self.total_samples_processed = 0  # A running counter of all samples seen so far
        self.chunk_queue: asyncio.Queue[npt.NDArray] = asyncio.Queue()

    def append_audio(self, data: npt.NDArray[np.float32]) -> None:
        # 加入缓冲区
        data_flat = data.flatten()
        self.input_buffer = np.concatenate([self.input_buffer, data_flat])
        self.history_buffer = np.concatenate([self.history_buffer, data_flat])

        # 维护history buffer的固定大小
        # overflow = len(self.history_buffer) - self.history_buffer_max_samples
        # if overflow > 0:
        #     self.history_buffer = self.history_buffer[overflow:]

        # 处理为chunk
        while len(self.input_buffer) >= self.chunk_size_samples:
            chunk_np = self.input_buffer[:self.chunk_size_samples]
            self.input_buffer = self.input_buffer[self.chunk_size_samples:]
            try:
                self.chunk_queue.put_nowait(chunk_np)
            except asyncio.QueueFull:
                print("[VAD警告] chunk_queue已满，处理速度跟不上输入速度。")

    # def flush(self):
    #     # 音频流结束时调用
    #     if self.last_start_time is not None:
    #         end_ms = self.total_sample_processed * 1000 / self.sample_rate
    #         result = self._extract_audio(self.last_start_time, end_ms)
    #         self.last_start_time = None

    async def process_chunk(self) -> list:
        chunk = await self.chunk_queue.get()
        segments = self.vad_core.process_chunk(chunk, self.cache)
        self.total_samples_processed += len(chunk)
        return segments

    def process_result(self, segments: list) -> list:
        completed_segments = []
        for start_ms, end_ms in segments:
            # 情况一：新的语音段开始
            if start_ms != -1 and end_ms == -1:
                # 如果之前有一个未结束的段，先将其结束
                if self.last_start_time is not None:
                    print(f"[VAD警告] 检测到之前有未完结的音频段: {self.last_start_time}ms - {start_ms}ms")
                    audio = self._extract_audio(self.last_start_time, start_ms)
                    if audio is not None:
                        completed_segments.append((self.last_start_time, start_ms, audio))
                    self.last_start_time = None
                    self.last_end_time = start_ms
                self.last_start_time = start_ms

            # 情况二：语音段结束
            elif start_ms == -1 and end_ms != -1:
                if self.last_start_time is not None:
                    # 语音段已完整，提取音频
                    audio = self._extract_audio(self.last_start_time, end_ms)
                    if audio is not None:
                        completed_segments.append((self.last_start_time, end_ms, audio))
                    self.last_start_time = None
                    self.last_end_time = end_ms

            # 情况三：短语音段（在单个块内开始和结束）
            elif start_ms != -1 and end_ms != -1:
                # 如果之前有一个未结束的段，先将其结束
                if self.last_start_time is not None:
                    print(f"[VAD警告] 检测到之前有未完结的音频段: {self.last_start_time}ms - {start_ms}ms")
                    audio = self._extract_audio(self.last_start_time, start_ms)
                    if audio is not None:
                        completed_segments.append((self.last_start_time, start_ms, audio))
                    self.last_start_time = None
                    self.last_end_time = start_ms

                audio = self._extract_audio(start_ms, end_ms)
                if audio is not None:
                    completed_segments.append((start_ms, end_ms, audio))
                self.last_start_time = None
                self.last_end_time = end_ms

        return completed_segments

    def _extract_audio(self, start_ms, end_ms):
        global_start_sample = int(start_ms * self.sample_rate / 1000)
        global_end_sample = int(end_ms * self.sample_rate / 1000)

        start_index_in_buffer = global_start_sample - self.history_buffer_head_index
        end_index_in_buffer = global_end_sample - self.history_buffer_head_index

        if start_index_in_buffer < 0 or end_index_in_buffer > len(self.history_buffer):
            print(f"[VAD警告] 无法提取音频段: {start_ms:.0f}ms-{end_ms:.0f}ms。所需数据超出历史缓冲区范围。")
            return None
        if start_index_in_buffer >= end_index_in_buffer:
            print(f"[VAD警告] 检测到空的音频段: {start_ms}ms - {end_ms}ms")
            return None
        return self.history_buffer[start_index_in_buffer:end_index_in_buffer]
