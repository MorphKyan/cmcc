#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的流式WebM解码器
使用单个容器实例，通过BytesIO支持流式读取
"""

import io
import logging
from typing import Optional

import av
import numpy as np
from av.audio.resampler import AudioResampler


class SimpleStreamingWebMDecoder:
    """
    简化的流式WebM解码器
    维护单个av容器实例，支持真正的流式解码
    """
    
    def __init__(self, target_sample_rate: int = 16000, target_layout: str = "mono", 
                 target_format: str = "fltp"):
        self.target_sample_rate = target_sample_rate
        self.target_layout = target_layout
        self.target_format = target_format
        
        # 流和容器
        self.container: Optional[av.container.InputContainer] = None
        self.audio_stream: Optional[av.stream.Stream] = None
        self.resampler: Optional[AudioResampler] = None
        
        # 数据流
        self.data_stream = io.BytesIO()
        self.data_stream_position = 0
        
        # 状态
        self.is_initialized = False
        self.total_samples_decoded = 0
        
        self.logger = logging.getLogger(__name__)
        
    def feed_data(self, data: bytes) -> bool:
        """喂入数据"""
        if not data:
            return False
            
        # 保存当前位置
        current_pos = self.data_stream.tell()
        
        # 移动到末尾并写入数据
        self.data_stream.seek(0, io.SEEK_END)
        self.data_stream.write(data)
        
        # 恢复位置
        self.data_stream.seek(current_pos)
        
        # 如果还没有初始化容器，尝试初始化
        if not self.is_initialized:
            try:
                self.data_stream.seek(0)
                self.container = av.open(self.data_stream, mode='r', format='matroska')
                
                if not self.container.streams.audio:
                    return False
                    
                self.audio_stream = self.container.streams.audio[0]
                self.resampler = AudioResampler(
                    format=self.target_format,
                    layout=self.target_layout,
                    rate=self.target_sample_rate
                )
                self.is_initialized = True
                self.logger.info("解码器初始化成功")
                return True
                
            except Exception as e:
                # 容器初始化失败，等待更多数据
                self.logger.debug(f"容器初始化失败（等待更多数据）: {e}")
                return True
        else:
            # 容器已初始化，数据已添加到流中
            return True
            
    def get_decoded_audio(self) -> Optional[np.ndarray]:
        """获取解码的音频"""
        if not self.is_initialized or self.container is None:
            return None
            
        try:
            decoded_frames = []
            
            # 解码可用的帧
            for packet in self.container.demux(self.audio_stream):
                for frame in packet.decode():
                    if self.resampler:
                        resampled_frames = self.resampler.resample(frame)
                        for resampled_frame in resampled_frames:
                            decoded_frames.append(resampled_frame.to_ndarray())
                    else:
                        decoded_frames.append(frame.to_ndarray())
            
            if not decoded_frames:
                return None
                
            if len(decoded_frames) == 1:
                result = decoded_frames[0]
            else:
                result = np.concatenate(decoded_frames, axis=1)
                
            self.total_samples_decoded += result.size
            return result
            
        except Exception as e:
            # 正常的流式处理中，可能会遇到不完整的包
            self.logger.debug(f"解码时遇到异常（可能数据不完整）: {e}")
            return None
            
    def reset(self):
        """重置解码器"""
        if self.container:
            self.container.close()
            
        self.container = None
        self.audio_stream = None
        self.resampler = None
        self.data_stream = io.BytesIO()
        self.data_stream_position = 0
        self.is_initialized = False
        self.total_samples_decoded = 0
        
    def get_buffer_size(self) -> int:
        """获取缓冲区大小"""
        pos = self.data_stream.tell()
        self.data_stream.seek(0, io.SEEK_END)
        size = self.data_stream.tell()
        self.data_stream.seek(pos)
        return size