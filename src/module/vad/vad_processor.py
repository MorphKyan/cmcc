#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import numpy as np
from src.module.vad.vad_core import VADCore


class VADProcessor:
    def __init__(self, vad_core: VADCore):
        self.vad_core = vad_core
        self.sample_rate = vad_core.sample_rate
        self.cache = {}
        self.input_buffer: bytearray = bytearray()
        self.input_buffer_index = 0
        self.last_start_time = None  # 上一segment的开始时间戳（累积）
        self.last_end_time = None  # 上一segment的结束时间戳（累积）
        self.buffer_start_sample_num = 0  # buffer头的偏移量
        self.chunk_queue: asyncio.Queue[np.ndarray[np.float32]] = asyncio.Queue()

    def append_audio(self, data: bytes):
        self.input_buffer.extend(data)

        while len(self.input_buffer) - self.input_buffer_index > self.vad_core.chunk_stride:
            chunk = self.input_buffer[self.input_buffer_index:self.input_buffer_index + self.vad_core.chunk_stride]
            chunk_np = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
            self.input_buffer_index += self.vad_core.chunk_stride
            self.chunk_queue.put(chunk_np)

    def process_chunk(self):
        chunk = self.chunk_queue.get()
        self.vad_core.process_chunk(chunk, self.cache)

    def process_result(self, segments: list) -> list:
        completed_segments = []
        for start, end in segments:
            # 情况一：新的语音段开始
            if start != -1 and end == -1:
                # 如果之前有一个未结束的段，先将其结束
                if self.last_start_time is not None:
                    print(f"[VAD警告] 检测到之前有未完结的音频段: {self.last_start_time}ms - {start}ms")
                    result = self._extract_audio(self.last_start_time, start)
                    if result is not None:
                        completed_segments.append(result)
                    self.last_start_time = None
                    self.last_end_time = start
                self.last_start_time = start

            # 情况二：语音段结束
            elif start == -1 and end != -1:
                if self.last_start_time is not None:
                    # 语音段已完整，提取音频
                    result = self._extract_audio(self.last_start_time, end)
                    if result is not None:
                        completed_segments.append(result)
                    self.last_start_time = None
                    self.last_end_time = end

            # 情况三：短语音段（在单个块内开始和结束）
            elif start != -1 and end != -1:
                # 如果之前有一个未结束的段，先将其结束
                if self.last_start_time is not None:
                    print(f"[VAD警告] 检测到之前有未完结的音频段: {self.last_start_time}ms - {start}ms")
                    result = self._extract_audio(self.last_start_time, start)
                    if result is not None:
                        completed_segments.append(result)
                    self.last_start_time = None
                    self.last_end_time = start

                result = self._extract_audio(start, end)
                if result is not None:
                    completed_segments.append(result)
                self.last_start_time = None
                self.last_end_time = end

        self._clean_buffer()

        return completed_segments

    def _clean_buffer(self):
        if self.last_end_time is not None:
            # 移除已处理的音频数据
            last_segment_end_buffer_index = int(self.last_end_time * self.sample_rate / 1000)
            count_to_remove = last_segment_end_buffer_index - self.buffer_start_sample_num
            if count_to_remove > 0:
                print(
                    f"[VAD] 移除已处理的音频数据: {self.buffer_start_sample_num}到{last_segment_end_buffer_index}的采样点, 当前缓存起始时间为: {last_segment_end_buffer_index / self.sample_rate:.2f}秒")
                self.input_buffer = self.input_buffer[count_to_remove:]
                self.buffer_start_sample_num = last_segment_end_buffer_index

    def _extract_audio(self, start, end):
        buffer_start_index = int(start * self.sample_rate / 1000) - self.buffer_start_sample_num
        buffer_start_index = max(0, buffer_start_index)
        buffer_end_index = int(end * self.sample_rate / 1000) - self.buffer_start_sample_num

        if buffer_end_index - buffer_start_index <= 0:
            print(f"[VAD警告] 检测到空的音频段: {start}ms - {end}ms")
            return None
        else:
            segment_audio = self.input_buffer[buffer_start_index:buffer_end_index]
            return start, end, segment_audio
