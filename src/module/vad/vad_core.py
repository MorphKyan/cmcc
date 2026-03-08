#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

import numpy as np
import numpy.typing as npt
from loguru import logger

from src.config.config import VADSettings
from src.module.vad.base_vad_processor import BaseVADProcessor, VADStatus


class VADCore(BaseVADProcessor):
    """
    实时语音活动检测处理器
    """

    def __init__(self, settings: VADSettings):
        """
        初始化VAD处理器

        Args:
            settings (VADSettings): VAD参数
        """
        super().__init__(settings)
        self.model = None
        logger.info("VAD处理器已创建，等待异步初始化...")

    async def initialize(self) -> None:
        """
        异步初始化VAD模型，支持重新初始化。
        """
        async with self._init_lock:
            if self.status == VADStatus.INITIALIZING:
                logger.warning("初始化已在进行中，请等待。")
                return
            self.status = VADStatus.INITIALIZING
            self.error_message = None
            logger.info("开始初始化VAD处理器...")

            try:
                # 初始化VAD模型
                logger.info("正在加载VAD模型...")
                import sherpa_onnx
                
                config = sherpa_onnx.VadModelConfig()
                config.silero_vad.model = self.settings.model_dir
                config.sample_rate = self.settings.sample_rate
                
                # 创建 VAD 实例
                self.model = sherpa_onnx.VoiceActivityDetector(
                    config=config,
                    buffer_size_in_seconds=self.settings.history_buffer_duration_sec
                )
                logger.info("VAD模型加载完成。")

                self.status = VADStatus.READY
                logger.success("VAD处理器初始化完成，状态: READY。")
            except Exception as e:
                self.status = VADStatus.ERROR
                self.error_message = f"VAD初始化失败: {e}"
                logger.exception(self.error_message)
                raise

    def process_chunk(self, chunk: npt.NDArray, cache: dict[str, Any]) -> list:
        """
        处理音频块并返回语音活动检测结果。
        Sherpa-ONNX VAD takes audio data incrementally.
        """
        if self.status != VADStatus.READY or self.model is None:
            raise RuntimeError(f"VAD处理器未准备就绪，当前状态: {self.status}")

        # Sherpa-ONNX 期望每次输入一段音频
        # 注意: Sherpa-ONNX 要求输入的波形应为 1维 np.float32 数组，范围在 [-1, 1]
        self.model.accept_waveform(chunk)
        
        segments = []
        while not self.model.empty():
            segment = self.model.front
            
            # The Sherpa-ONNX SpeechSegment contains 'start' (frames), 'samples' (float32 array)
            # Frame length usually depends on the VAD model internally but we can just use the provided samples
            # to calculate the length.
            # We want to return [start_ms, end_ms, samples] to simplify the outer processor
            
            start_ms = int((segment.start / self.settings.sample_rate) * 1000)
            
            # Extract samples as numpy array
            samples = np.array(segment.samples, dtype=np.float32)
            end_ms = start_ms + int((len(samples) / self.settings.sample_rate) * 1000)
            
            segments.append((start_ms, end_ms, samples))
            
            self.model.pop()
            
        return segments
