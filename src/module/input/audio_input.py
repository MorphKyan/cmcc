#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio
import queue
from typing import Optional, Mapping
from src.config import FORMAT, CHANNELS, RATE, CHUNK


class AudioInputer:
    """
    处理麦克风音频输入的类
    """

    def __init__(self):
        """
        初始化音频输入处理器
        """
        self.audio_queue = queue.Queue()
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._audio_callback
        )

    def _audio_callback(self, in_data: bytes | None, frame_count: int, time_info: Mapping[str, float], status: int) \
            -> tuple[Optional[bytes], int] | None:
        """音频流回调函数，将数据放入队列。"""
        self.audio_queue.put(in_data)
        return None, pyaudio.paContinue

    def start(self) -> None:
        """启动音频流"""
        if self.stream:
            self.stream.start_stream()

    def stop(self) -> None:
        """停止并清理音频资源"""
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
            except OSError:
                # 流可能已经关闭，忽略错误
                pass
            try:
                self.stream.close()
            except OSError:
                # 流可能已经关闭，忽略错误
                pass
        self.audio.terminate()

    def get_audio_data(self, timeout=None):
        """
        从音频队列中获取数据
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
            
        Returns:
            音频数据
            
        Raises:
            queue.Empty: 如果在指定的超时时间内没有数据
        """
        return self.audio_queue.get(timeout=timeout)
