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
        
        # 缓存用于VAD模型
        self.cache = {}
        self.speech_start_ms = -1
        
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
            
        # 使用VAD模型处理音频块
        res = self.model.generate(
            input=audio_chunk, 
            cache=self.cache, 
            is_final=False,  # 实时处理中不使用is_final参数
            chunk_size=self.chunk_size,
            **VAD_KWARGS
        )
        
        segments = []
        if res and res[0].get("value"):
            segments = res[0]["value"]

        completed_segments = []
        for seg in segments:
            start, end = seg
            if start != -1 and end != -1:  # 一个块内检测到完整的语音段
                # 计算音频块的起始和结束样本索引
                start_sample = int(start * self.sample_rate / 1000)
                end_sample = int(end * self.sample_rate / 1000)
                # 裁剪音频数据
                audio_data = audio_chunk[start_sample:end_sample]
                # 添加(开始时间, 结束时间, 音频数据)元组
                completed_segments.append((start, end, audio_data))
            elif start != -1 and end == -1:  # 检测到语音段的开始
                self.speech_start_ms = start
            elif start == -1 and end != -1:  # 检测到语音段的结束
                if self.speech_start_ms != -1:
                    # 计算音频块的起始和结束样本索引
                    start_sample = int(self.speech_start_ms * self.sample_rate / 1000)
                    end_sample = int(end * self.sample_rate / 1000)
                    # 裁剪音频数据
                    audio_data = audio_chunk[start_sample:end_sample]
                    # 添加(开始时间, 结束时间, 音频数据)元组
                    completed_segments.append((self.speech_start_ms, end, audio_data))
                    self.speech_start_ms = -1
        
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
        self.cache = {}
        
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
        self.speech_start_ms = -1
