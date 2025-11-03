#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确的流式WebM解码器
处理WebSocket传输的WebM流格式：
- 第一个包：WebM header + 音频数据
- 后续包：纯音频数据
"""

import io
from typing import Optional

import av
import numpy as np
from av.audio.resampler import AudioResampler


class CorrectStreamingWebMDecoder:
    """
    正确的流式WebM解码器
    专门处理WebSocket WebM流格式
    """
    
    def __init__(self, target_sample_rate: int = 16000, target_layout: str = "mono", 
                 target_format: str = "fltp"):
        self.target_sample_rate = target_sample_rate
        self.target_layout = target_layout
        self.target_format = target_format
        
        # WebM header管理
        self.webm_header: Optional[bytes] = None
        self.header_extracted = False
        
        # 重采样器
        self.resampler: Optional[AudioResampler] = None
        
        # 状态
        self.is_first_chunk = True
        self.total_samples_decoded = 0
        
    def _extract_webm_header(self, first_chunk: bytes) -> Optional[bytes]:
        """
        从第一个数据块中提取WebM header
        返回header部分，剩余部分作为音频数据
        """
        try:
            # WebM文件结构分析
            # EBML header: 0x1A 0x45 0xDF 0xA3
            if not first_chunk.startswith(b'\x1a\x45\xdf\xa3'):
                print("第一个数据块不包含WebM header")
                return None
                
            # 使用pyav解析第一个块来确定header结束位置
            with av.open(io.BytesIO(first_chunk), mode='r', format='matroska') as container:
                # 成功打开说明这是有效的WebM文件
                # 现在需要找到header的结束位置
                
                # 简化策略：使用一个保守的header大小估计
                # WebM header通常在前1-2KB内
                header_size = min(2048, len(first_chunk) // 2)
                
                # 确保header包含必要的元数据
                while header_size < len(first_chunk):
                    try:
                        with av.open(io.BytesIO(first_chunk[:header_size]), mode='r', format='matroska') as test_container:
                            if test_container.streams.audio:
                                # 找到最小的有效header
                                break
                    except:
                        pass
                    header_size += 512
                    if header_size > len(first_chunk):
                        header_size = min(2048, len(first_chunk))
                        break

                print(f"提取WebM header，大小: {header_size} 字节")
                return first_chunk[:header_size]
                
        except Exception as e:
            print(f"提取WebM header失败: {e}")
            return None
            
    def _decode_webm_data(self, webm_data: bytes) -> Optional[np.ndarray]:
        """
        解码完整的WebM数据（包含header）
        """
        try:
            with av.open(io.BytesIO(webm_data), mode='r', format='matroska') as container:
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
                    return None
                
                if len(decoded_frames) == 1:
                    result = decoded_frames[0]
                else:
                    result = np.concatenate(decoded_frames, axis=1)
                    
                self.total_samples_decoded += result.size
                return result
                
        except Exception as e:
            print(f"解码WebM数据失败: {e}")
            return None
            
    def decode_chunk(self, data_chunk: bytes, is_first: bool = False) -> Optional[np.ndarray]:
        """
        解码数据块
        
        Args:
            data_chunk: 数据块
            is_first: 是否是第一个数据块
            
        Returns:
            解码后的音频数据或None
        """
        if not data_chunk:
            return None
            
        if is_first or self.is_first_chunk:
            # 第一个块：提取header并解码
            self.is_first_chunk = False
            
            # 提取header
            self.webm_header = self._extract_webm_header(data_chunk)
            if self.webm_header is None:
                print("无法从第一个数据块提取WebM header")
                return None
                
            # 初始化重采样器（从第一个块获取音频信息）
            try:
                with av.open(io.BytesIO(data_chunk), mode='r', format='matroska') as container:
                    audio_stream = container.streams.audio[0]
                    self.resampler = AudioResampler(
                        format=self.target_format,
                        layout=self.target_layout,
                        rate=self.target_sample_rate
                    )
            except Exception as e:
                print(f"初始化重采样器失败: {e}")
                return None
            
            # 直接解码第一个完整块
            return self._decode_webm_data(data_chunk)
            
        else:
            # 后续块：拼接header后解码
            if self.webm_header is None:
                print("缺少WebM header，无法解码后续数据块")
                return None
                
            complete_webm = self.webm_header + data_chunk
            return self._decode_webm_data(complete_webm)
            
    def reset(self):
        """重置解码器状态"""
        self.webm_header = None
        self.header_extracted = False
        self.resampler = None
        self.is_first_chunk = True
        self.total_samples_decoded = 0
        
    def is_ready(self) -> bool:
        """检查解码器是否已准备好"""
        return self.webm_header is not None