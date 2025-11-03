#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的流式WebM音频解码器
支持长时间音频流，避免内存累积和重复解码
"""

import io
import logging
from typing import Optional, Tuple

import av
import numpy as np
from av.audio.resampler import AudioResampler


class TrueStreamingWebMDecoder:
    """
    真正的流式WebM音频解码器
    通过分离header和数据，实现高效的流式处理
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
        
        # Header和状态管理
        self.webm_header: Optional[bytes] = None
        self.header_size = 0
        self.is_header_processed = False
        
        # 音频流信息（从header中提取）
        self.audio_sample_rate: Optional[int] = None
        self.audio_channels: Optional[int] = None
        self.audio_format: Optional[str] = None
        
        # 重采样器
        self.resampler: Optional[AudioResampler] = None
        
        # 数据缓冲区（只保存未处理的数据）
        self.data_buffer = bytearray()
        
        # 统计信息
        self.total_bytes_received = 0
        self.total_samples_decoded = 0
        
        self.logger = logging.getLogger(__name__)
        
    def _extract_header_info(self, header_data: bytes) -> bool:
        """
        从WebM header中提取音频流信息
        """
        try:
            with av.open(io.BytesIO(header_data), mode='r', format='matroska') as container:
                if not container.streams.audio:
                    self.logger.error("未找到音频流")
                    return False
                    
                audio_stream = container.streams.audio[0]
                self.audio_sample_rate = audio_stream.rate
                self.audio_channels = audio_stream.channels
                self.audio_format = str(audio_stream.format)
                
                # 初始化重采样器
                self.resampler = AudioResampler(
                    format=self.target_format,
                    layout=self.target_layout,
                    rate=self.target_sample_rate
                )
                
                self.logger.info(f"音频信息提取成功 - 采样率: {self.audio_sample_rate}, "
                               f"声道: {self.audio_channels}, 格式: {self.audio_format}")
                return True
                
        except Exception as e:
            self.logger.error(f"提取header信息失败: {e}")
            return False
            
    def _detect_webm_header_end(self, data: bytes) -> int:
        """
        检测WebM header的结束位置
        """
        # WebM文件结构：EBML header + Segment header + Cluster数据
        # 简化策略：找到第一个Cluster的开始位置
        # Cluster ID: 0x1F 0x43 0xB6 0x75
        cluster_id = b'\x1f\x43\xb6\x75'
        cluster_pos = data.find(cluster_id)
        
        if cluster_pos != -1:
            # 找到Cluster，header结束位置就是Cluster开始位置
            return cluster_pos
        else:
            # 保守估计header大小
            return min(1024, len(data))
            
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
        
        if not self.is_header_processed:
            # 累积数据直到可以分离header
            self.data_buffer.extend(data)
            
            # 尝试分离header
            if len(self.data_buffer) > 2048:  # 足够大的数据来检测header
                full_data = bytes(self.data_buffer)
                header_end = self._detect_webm_header_end(full_data)
                
                if header_end > 0:
                    self.webm_header = full_data[:header_end]
                    # 将剩余数据作为音频数据
                    audio_data = full_data[header_end:]
                    self.data_buffer = bytearray(audio_data)
                    
                    # 提取音频信息
                    if self._extract_header_info(self.webm_header):
                        self.is_header_processed = True
                        self.header_size = header_end
                        self.logger.info(f"WebM header分离成功，大小: {header_end} 字节")
                        return True
                    else:
                        self.logger.warning("header信息提取失败，继续累积数据")
                        return False
                else:
                    self.logger.debug("未找到header结束位置，继续累积数据")
                    return True
            else:
                return True
        else:
            # header已处理，直接添加音频数据
            self.data_buffer.extend(data)
            return True
            
    def get_decoded_audio(self, max_data_size: int = 8192) -> Optional[np.ndarray]:
        """
        解码部分音频数据，避免处理过大的缓冲区
        
        Args:
            max_data_size: 最大处理的数据大小（字节）
            
        Returns:
            numpy数组或None
        """
        if not self.is_header_processed or len(self.data_buffer) == 0:
            return None
            
        # 限制每次处理的数据量
        process_size = min(len(self.data_buffer), max_data_size)
        if process_size == 0:
            return None
            
        audio_chunk = bytes(self.data_buffer[:process_size])
        
        # 创建临时的WebM文件：header + 音频数据块
        temp_webm = self.webm_header + audio_chunk
        
        try:
            with av.open(io.BytesIO(temp_webm), mode='r', format='matroska') as container:
                if not container.streams.audio:
                    return None
                    
                audio_stream = container.streams.audio[0]
                decoded_frames = []
                
                for frame in container.decode(audio_stream):
                    if self.resampler:
                        resampled_frames = self.resampler.resample(frame)
                        for resampled_frame in resampled_frames:
                            decoded_frames.append(resampled_frame.to_ndarray())
                    else:
                        decoded_frames.append(frame.to_ndarray())
                
                if not decoded_frames:
                    # 没有解码出帧，可能是数据不完整，保留数据等待更多数据
                    return None
                
                # 合并帧
                if len(decoded_frames) == 1:
                    result = decoded_frames[0]
                else:
                    result = np.concatenate(decoded_frames, axis=1)
                    
                # 更新统计信息
                self.total_samples_decoded += result.size
                
                # 从缓冲区中移除已处理的数据
                del self.data_buffer[:process_size]
                
                return result
                
        except Exception as e:
            # 解码失败，可能是数据块不完整
            self.logger.debug(f"解码数据块失败（可能不完整）: {e}")
            # 不移除数据，等待更多数据到来
            return None
            
    def reset(self):
        """
        重置解码器状态
        """
        self.webm_header = None
        self.header_size = 0
        self.is_header_processed = False
        self.audio_sample_rate = None
        self.audio_channels = None
        self.audio_format = None
        self.resampler = None
        self.data_buffer = bytearray()
        self.total_bytes_received = 0
        self.total_samples_decoded = 0
        
    def get_buffer_size(self) -> int:
        """
        获取当前数据缓冲区大小
        """
        return len(self.data_buffer)
        
    def is_ready(self) -> bool:
        """
        检查解码器是否已准备好处理音频数据
        """
        return self.is_header_processed