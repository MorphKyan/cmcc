#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from funasr import AutoModel
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VAD_MODEL, VAD_KWARGS

class VADProcessor:
    """
    实时语音活动检测(VAD)处理器
    """
    def __init__(self, chunk_size: int = 200, sample_rate: int = 16000):
        """
        初始化VAD处理器
        
        Args:
            chunk_size: 音频块大小(ms)
            sample_rate: 音频采样率
        """
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.chunk_stride = int(chunk_size * sample_rate / 1000)
        
        # 初始化VAD模型
        print("正在加载VAD模型...")
        self.model = AutoModel(model=VAD_MODEL, model_revision="v2.0.4")
        print("VAD模型加载完成。")
        
        # VAD模型缓存
        self.cache = {}
        
        # 全局音频缓存和已处理时间戳
        self.audio_buffer = None
        self.processed_timestamp_ms = 0
        
        # 当前语音段的开始时间
        self.current_segment_start_time = None
        
    def process_audio_chunk(self, audio_chunk: np.ndarray) -> list:
        """
        处理音频块，检测语音活动
        
        Args:
            audio_chunk: 音频数据块
            
        Returns:
            检测到的语音段列表，每个元素包含(开始时间ms, 结束时间ms, 音频数据)
        """
        # 确保音频数据是float32类型
        if audio_chunk.dtype == np.int16:
            audio_chunk = audio_chunk.astype(np.float32) / 32768.0
        elif audio_chunk.dtype == np.int32:
            audio_chunk = audio_chunk.astype(np.float32) / 2147483648.0

        # 将新的音频块拼接到全局缓存
        if self.audio_buffer is None:
            self.audio_buffer = audio_chunk
        else:
            self.audio_buffer = np.concatenate([self.audio_buffer, audio_chunk])
            
        res = self.model.generate(
            input=audio_chunk, 
            cache=self.cache, 
            is_final=False,
            chunk_size=self.chunk_size,
            **VAD_KWARGS
        )
        
        segments = []
        if res and res[0].get("value"):
            segments = res[0]["value"]

        completed_segments = []
        last_end_time = -1
        
        # 计算当前块在全局缓存中的偏移量（以采样点和毫秒为单位）
        buffer_offset_samples = len(self.audio_buffer) - len(audio_chunk)
        chunk_start_time_ms = self.processed_timestamp_ms + buffer_offset_samples * 1000 / self.sample_rate

        for start, end in segments:
            # 将相对于块的时间戳转换为绝对时间戳
            abs_start = -1
            if start != -1:
                abs_start = start + chunk_start_time_ms

            abs_end = -1
            if end != -1:
                abs_end = end + chunk_start_time_ms

            # 情况一：新的语音段开始
            if start != -1 and end == -1:
                if self.current_segment_start_time is None:
                    self.current_segment_start_time = abs_start
            
            # 情况二：语音段结束
            elif start == -1 and end != -1:
                if self.current_segment_start_time is not None:
                    # 语音段已完整，提取音频
                    start_sample = int((self.current_segment_start_time - self.processed_timestamp_ms) * self.sample_rate / 1000)
                    end_sample = int((abs_end - self.processed_timestamp_ms) * self.sample_rate / 1000)
                    
                    segment_audio = self.audio_buffer[max(0, start_sample):end_sample]
                    completed_segments.append((self.current_segment_start_time, abs_end, segment_audio))
                    last_end_time = abs_end
                    
                    # 重置当前语音段状态
                    self.current_segment_start_time = None

            # 情况三：短语音段（在单个块内开始和结束）
            elif start != -1 and end != -1:
                # 如果之前有一个未结束的段，先将其结束
                if self.current_segment_start_time is not None:
                    start_sample = int((self.current_segment_start_time - self.processed_timestamp_ms) * self.sample_rate / 1000)
                    end_sample = int((abs_start - self.processed_timestamp_ms) * self.sample_rate / 1000)
                    segment_audio = self.audio_buffer[max(0, start_sample):end_sample]
                    completed_segments.append((self.current_segment_start_time, abs_start, segment_audio))
                    self.current_segment_start_time = None

                start_sample = int((abs_start - self.processed_timestamp_ms) * self.sample_rate / 1000)
                end_sample = int((abs_end - self.processed_timestamp_ms) * self.sample_rate / 1000)

                segment_audio = self.audio_buffer[max(0, start_sample):end_sample]
                completed_segments.append((abs_start, abs_end, segment_audio))
                last_end_time = abs_end

        if last_end_time != -1:
            # 移除已处理的音频数据，并更新时间戳
            remove_samples = int((last_end_time - self.processed_timestamp_ms) * self.sample_rate / 1000)
            if remove_samples > 0:
                self.audio_buffer = self.audio_buffer[remove_samples:]
                self.processed_timestamp_ms = last_end_time
            
        return completed_segments
        
    def process_audio_stream(self, audio_data: np.ndarray) -> list:
        """
        处理音频流，分块检测语音活动
        
        Args:
            audio_data: 完整的音频数据
            
        Returns:
            检测到的所有语音段列表，每个元素包含(开始时间ms, 结束时间ms)
        """
        speech_segments = []
        
        # 重置缓存
        self.reset_cache()
        
        # 对于实时流，我们按块处理，不需要计算总块数
        # 直接按块大小处理音频数据
        for i in range(0, len(audio_data), self.chunk_stride):
            # 获取音频块
            speech_chunk = audio_data[i:i + self.chunk_stride]
            
            # 处理音频块（实时处理中不使用is_final参数）
            segments = self.process_audio_chunk(speech_chunk)
            
            # 从(开始时间, 结束时间, 音频数据)元组中提取时间信息
            for segment in segments:
                start, end, _ = segment
                speech_segments.append([start, end])
                
        return speech_segments
        
    def reset_cache(self):
        """重置VAD缓存和语音段状态"""
        self.cache = {}
        self.audio_buffer = None
        self.processed_timestamp_ms = 0
        self.current_segment_start_time = None
