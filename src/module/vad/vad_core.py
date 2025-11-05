#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from funasr import AutoModel
import numpy.typing as npt
from loguru import logger

from src.config.config import VADSettings


class VADCore:
    """
    实时语音活动检测处理器
    """

    def __init__(self, settings: VADSettings):
        """
        初始化VAD处理器

        Args:
            settings (VADSettings): VAD参数
        """
        self.chunk_size = settings.chunk_size
        self.sample_rate = settings.sample_rate
        self.kwargs = {
            "MAX_SINGLE_SEGMENT_TIME": settings.max_single_segment_time
        }
        self.chunk_stride = int(self.chunk_size * self.sample_rate / 1000)

        # 初始化VAD模型
        logger.info("正在加载VAD模型...")
        self.model = AutoModel(model=settings.model, model_revision="v2.0.4")
        logger.info("VAD模型加载完成。")

    def process_chunk(self, chunk: npt.NDArray, cache) -> list:
        segments = self.model.generate(
            input=chunk,
            cache=cache,
            is_final=False,
            chunk_size=self.chunk_size,
            **self.kwargs
        )

        if segments and segments[0].get("value"):
            return segments[0].get("value")
        return []
