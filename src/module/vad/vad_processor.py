#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
from typing import Any, Optional, TypeAlias

import numpy as np
import numpy.typing as npt
from loguru import logger
from scipy.io import wavfile

from src.config.config import VADSettings
from src.module.vad.vad_core import VADCore

# 类型别名
AudioSegment: TypeAlias = tuple[int, int, npt.NDArray[np.float32]]
VADCache: TypeAlias = dict[str, Any]


class VADProcessor:
    def __init__(self, vad_core: VADCore, settings: VADSettings) -> None:
        self.vad_core = vad_core
        self.settings = settings
        self.sample_rate = vad_core.sample_rate
        self.chunk_size_samples = int(self.vad_core.chunk_size * self.sample_rate / 1000)
        self.cache: VADCache = {}
        self.input_buffer: npt.NDArray[np.float32] = np.array([], dtype=np.float32)
        self.history_buffer_max_samples = settings.history_buffer_duration_sec * self.sample_rate
        self.history_buffer: npt.NDArray[np.float32] = np.array([], dtype=np.float32)
        self.history_buffer_head_index = 0  # buffer头的偏移量
        self.last_start_time: Optional[int] = None  # 上一segment的开始时间戳（累积）
        self.last_end_time: Optional[int] = None  # 上一segment的结束时间戳（累积）
        self.total_samples_processed = 0  # A running counter of all samples seen so far
        self.chunk_queue: asyncio.Queue[npt.NDArray] = asyncio.Queue(maxsize=settings.chunk_queue_maxsize)

    def append_audio(self, data: npt.NDArray[np.float32]) -> None:
        # 加入缓冲区
        data_flat = data.flatten()
        self.input_buffer = np.concatenate([self.input_buffer, data_flat])
        self.history_buffer = np.concatenate([self.history_buffer, data_flat])

        # 维护history buffer的最大容量
        if len(self.history_buffer) > self.history_buffer_max_samples:
            overflow = len(self.history_buffer) - self.history_buffer_max_samples
            self.history_buffer = self.history_buffer[overflow:]
            self.history_buffer_head_index += overflow
            logger.debug(f"history_buffer超出限制，强制裁剪 {overflow} 样本")

        # 处理为chunk
        while len(self.input_buffer) >= self.chunk_size_samples:
            chunk_np = self.input_buffer[:self.chunk_size_samples]
            self.input_buffer = self.input_buffer[self.chunk_size_samples:]
            try:
                self.chunk_queue.put_nowait(chunk_np)
            except asyncio.QueueFull:
                logger.warning("chunk_queue已满，处理速度跟不上输入速度。")

    async def process_chunk(self) -> list[tuple[int, int]]:
        chunk = await self.chunk_queue.get()
        segments = self.vad_core.process_chunk(chunk, self.cache)
        self.total_samples_processed += len(chunk)
        return segments

    def _complete_pending_segment(self, end_ms: int) -> Optional[AudioSegment]:
        """
        完成之前未结束的语音段。
        
        Args:
            end_ms: 语音段结束时间（毫秒）
            
        Returns:
            完成的语音段 (start_ms, end_ms, audio)，如果无法提取则返回 None
        """
        if self.last_start_time is None:
            return None
            
        logger.warning("检测到之前有未完结的音频段: {start}ms - {end}ms", 
                      start=self.last_start_time, end=end_ms)
        audio = self._extract_audio(self.last_start_time, end_ms)
        if audio is not None:
            result = (self.last_start_time, end_ms, audio)
            if self.settings.save_audio_segments:
                self._save_audio_segment(audio, self.last_start_time, end_ms)
            return result
        return None

    def _finalize_segment(self, start_ms: int, end_ms: int) -> Optional[AudioSegment]:
        """
        完成一个语音段并返回结果。
        
        Args:
            start_ms: 语音段开始时间（毫秒）
            end_ms: 语音段结束时间（毫秒）
            
        Returns:
            完成的语音段 (start_ms, end_ms, audio)，如果无法提取则返回 None
        """
        audio = self._extract_audio(start_ms, end_ms)
        if audio is not None:
            if self.settings.save_audio_segments:
                self._save_audio_segment(audio, start_ms, end_ms)
            return (start_ms, end_ms, audio)
        return None

    def process_result(self, segments: list[tuple[int, int]]) -> list[AudioSegment]:
        completed_segments: list[AudioSegment] = []
        
        for start_ms, end_ms in segments:
            # 情况一：新的语音段开始
            if start_ms != -1 and end_ms == -1:
                # 如果之前有一个未结束的段，先将其结束
                pending = self._complete_pending_segment(start_ms)
                if pending:
                    completed_segments.append(pending)
                    self.last_end_time = start_ms
                self.last_start_time = start_ms

            # 情况二：语音段结束
            elif start_ms == -1 and end_ms != -1:
                if self.last_start_time is not None:
                    segment = self._finalize_segment(self.last_start_time, end_ms)
                    if segment:
                        completed_segments.append(segment)
                    self.last_start_time = None
                    self.last_end_time = end_ms

            # 情况三：短语音段（在单个块内开始和结束）
            elif start_ms != -1 and end_ms != -1:
                # 如果之前有一个未结束的段，先将其结束
                pending = self._complete_pending_segment(start_ms)
                if pending:
                    completed_segments.append(pending)
                    self.last_end_time = start_ms
                self.last_start_time = None

                segment = self._finalize_segment(start_ms, end_ms)
                if segment:
                    completed_segments.append(segment)
                self.last_end_time = end_ms

        return completed_segments

    def _extract_audio(self, start_ms: int, end_ms: int) -> Optional[npt.NDArray[np.float32]]:
        global_start_sample = int(start_ms * self.sample_rate / 1000)
        global_end_sample = int(end_ms * self.sample_rate / 1000)

        start_index_in_buffer = global_start_sample - self.history_buffer_head_index
        end_index_in_buffer = global_end_sample - self.history_buffer_head_index

        if start_index_in_buffer < 0 or end_index_in_buffer > len(self.history_buffer):
            logger.warning("无法提取音频段: {start:.0f}ms-{end:.0f}ms。所需数据超出历史缓冲区范围。", start=start_ms, end=end_ms)
            return None
        if start_index_in_buffer >= end_index_in_buffer:
            logger.warning("检测到空的音频段: {start}ms - {end}ms", start=start_ms, end=end_ms)
            return None
        
        # 提取音频
        audio = self.history_buffer[start_index_in_buffer:end_index_in_buffer].copy()

        # 清理已使用的历史数据
        # 保留一定的安全边界，以防VAD可能的检测延迟或需要重新提取
        safety_margin_samples = self.settings.safety_margin_sec * self.sample_rate
        trim_index = max(0, end_index_in_buffer - safety_margin_samples)
        
        if trim_index > 0:
            self.history_buffer = self.history_buffer[trim_index:]
            self.history_buffer_head_index += trim_index
            
        return audio

    def _save_audio_segment(self, audio_data: npt.NDArray[np.float32], start_ms: int, end_ms: int) -> None:
        """保存音频片段为WAV文件"""
        try:
            # 创建保存目录
            save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "audio_segments")
            os.makedirs(save_dir, exist_ok=True)

            # 使用时间戳命名文件
            filename = f"segment_{start_ms}_{end_ms}.wav"
            filepath = os.path.join(save_dir, filename)

            # 保存为WAV文件（需要将float32转换为int16）
            # 假设音频数据在-1到1之间，乘以32767转换为int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wavfile.write(filepath, self.sample_rate, audio_int16)

            logger.info(f"音频片段已保存: {filepath}")
        except Exception as e:
            logger.error(f"保存音频片段失败: {e}")
