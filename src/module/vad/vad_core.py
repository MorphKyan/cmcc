#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from funasr import AutoModel
import numpy.typing as npt

from src.config import VADSettings


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
        self.chunk_size = settings.CHUNK_SIZE
        self.sample_rate = settings.SAMPLE_RATE
        self.kwargs = settings.KWARGS
        self.chunk_stride = int(self.chunk_size * self.sample_rate / 1000)

        # 初始化VAD模型
        print("正在加载VAD模型...")
        self.model = AutoModel(model=settings.MODEL, model_revision="v2.0.4")
        print("VAD模型加载完成。")

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
