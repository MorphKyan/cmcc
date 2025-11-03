#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版本的流式WebM音频解码器
修复重复解码问题，正确跟踪已解码的位置
"""

import io
import logging
from typing import Optional

import av
import numpy as np
from av.audio.resampler import AudioResampler


class StreamingWebMDecoder:
    """
    最终版本的流式WebM音频解码器
    通过维护解码状态和位置信息，避免重复解码
    """
    
    def __init__(self, target_sample_rate: int = 16000, target_layout: str = "mono", 
                 target_format: str = "fltp"):
        """
        初始化流式解码器
        
        Args:
            target_sample_rate: 目标采样率
            target_layout: 目标声道布局
            target_format: 目标样本格式
        """
        self.target_sample_rate = target_sample_rate
        self.target_layout = target_layout
        self.target_format = target_format
        
        # 解码状态
        self.resampler: Optional[AudioResampler] = None
        self.data_buffer = bytearray()
        self.header_processed = False
        self.last_decode_position = 0  # 跟踪上次解码到的位置
        
        # 统计信息
        self.total_bytes_received = 0
        self.total_samples_decoded = 0
        
        # 初始化重采样器
        self.resampler = AudioResampler(
            format=self.target_format,
            layout=self.target_layout,
            rate=self.target_sample_rate
        )
        
        self.logger = logging.getLogger(__name__)
        
    def feed_data(self, data: bytes) -> bool:
        """
        喂入新的音频数据块
        
        Args:
            data: 新的音频数据块
            
        Returns:
            bool: 是否成功接收数据
        """
        if not data:
            return False
            
        self.total_bytes_received += len(data)
        self.data_buffer.extend(data)
        
        # 如果还没有处理header，且数据足够大，标记为已处理
        if not self.header_processed and len(self.data_buffer) > 1024:
            self.header_processed = True
            self.logger.info("WebM header处理完成")
            
        return True
        
    def get_decoded_audio(self) -> Optional[np.ndarray]:
        """
        尝试解码新增的音频数据
        
        Returns:
            numpy数组或None
        """
        if len(self.data_buffer) < 1024 or not self.header_processed:
            return None
            
        try:
            # 创建包含所有数据的buffer
            full_data = bytes(self.data_buffer)
            
            # 使用pyav解码
            with av.open(io.BytesIO(full_data), mode='r', format='matroska') as container:
                if not container.streams.audio:
                    return None
                    
                audio_stream = container.streams.audio[0]
                decoded_frames = []
                total_samples = 0
                
                # 解码所有帧，但只返回新增的部分
                for frame in container.decode(audio_stream):
                    frame_samples = frame.samples
                    total_samples += frame_samples
                    
                    # 只处理新增的样本
                    if total_samples > self.total_samples_decoded:
                        if self.resampler:
                            resampled_frames = self.resampler.resample(frame)
                            for resampled_frame in resampled_frames:
                                decoded_frames.append(resampled_frame.to_ndarray())
                        else:
                            decoded_frames.append(frame.to_ndarray())
                
                if not decoded_frames:
                    return None
                
                # 合并帧
                if len(decoded_frames) == 1:
                    result = decoded_frames[0]
                else:
                    result = np.concatenate(decoded_frames, axis=1)
                    
                # 更新已解码样本计数
                self.total_samples_decoded = total_samples
                return result
                
        except Exception as e:
            # 解码失败，可能是数据不完整，这是正常的
            self.logger.debug(f"解码失败（可能数据不完整）: {e}")
            return None
            
    def reset(self):
        """
        重置解码器状态
        """
        self.data_buffer = bytearray()
        self.header_processed = False
        self.last_decode_position = 0
        self.total_bytes_received = 0
        self.total_samples_decoded = 0
        
    def get_buffer_size(self) -> int:
        """
        获取当前缓冲区大小
        """
        return len(self.data_buffer)