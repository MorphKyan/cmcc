#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from funasr import AutoModel

# 使用相对导入
from src.config import FUNASR_VAD_MODEL, FUNASR_VAD_KWARGS

class VADProcessor:
    """
    实时语音活动检测(VAD)处理器
    
    该处理器使用输入缓存机制来处理任意长度的音频输入流，确保能够正确处理不规则大小的音频块。
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
        self.model = AutoModel(model=FUNASR_VAD_MODEL, model_revision="v2.0.4")
        print("VAD模型加载完成。")
        
        # VAD模型缓存
        self.cache = {}
        
        # 全局音频缓存
        self.audio_buffer = None
        
        # 当前语音段的开始时间
        self.last_start_time = None
        self.buffer_start_sample_num = 0
        
        # 输入缓存，用于累积音频数据直到满足处理要求
        self.input_buffer = np.array([], dtype=np.float32)
        
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

        # 将新的音频块添加到输入缓存
        self.input_buffer = np.concatenate([self.input_buffer, audio_chunk])
        
        # 将新的音频块拼接到全局缓存
        if self.audio_buffer is None:
            self.audio_buffer = audio_chunk
        else:
            self.audio_buffer = np.concatenate([self.audio_buffer, audio_chunk])
            
        # 处理缓存中的音频数据
        segments = self._process_buffered_audio()
        
        completed_segments = []
        last_end_time = -1

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
                    if(segment_audio.size == 0):
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
                print(f"[VAD] 移除已处理的音频数据: {self.buffer_start_sample_num}到{remove_samples}的采样点, 当前缓存起始时间为: {remove_samples / self.sample_rate:.2f}秒")
                self.audio_buffer = self.audio_buffer[remove_samples - self.buffer_start_sample_num:]
                self.buffer_start_sample_num = remove_samples
            
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
        
    def _get_processable_chunks(self) -> list:
        """
        从输入缓存中提取可处理的音频块
        
        该方法会从输入缓存中提取所有完整的音频块，并更新缓存以移除已处理的数据。
        
        Returns:
            可处理的音频块列表
        """
        chunks = []
        while len(self.input_buffer) >= self.chunk_stride:
            # 提取一个完整的块
            chunk = self.input_buffer[:self.chunk_stride]
            chunks.append(chunk)
            # 更新缓存（移除已处理的数据）
            self.input_buffer = self.input_buffer[self.chunk_stride:]
        return chunks
    
    def _process_buffered_audio(self) -> list:
        """
        处理缓存中的音频数据
        
        该方法会获取所有可处理的音频块，并使用VAD模型处理这些块以检测语音活动。
        
        Returns:
            检测到的语音段列表
        """
        # 获取可处理的音频块
        processable_chunks = self._get_processable_chunks()
        
        all_segments = []
        for chunk in processable_chunks:
            # 处理每个音频块
            segments = self.model.generate(
                input=chunk,
                cache=self.cache,
                is_final=False,
                chunk_size=self.chunk_size,
                **FUNASR_VAD_KWARGS
            )
            
            if segments and segments[0].get("value"):
                all_segments.extend(segments[0]["value"])
                
        return all_segments
    
    def reset_cache(self):
        """重置VAD缓存和语音段状态"""
        self.cache = {}
        self.audio_buffer = None
        self.last_start_time = None
        self.input_buffer = np.array([], dtype=np.float32)
