#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from funasr import AutoModel
import numpy.typing as npt
from src.config import FUNASR_VAD_MODEL, FUNASR_VAD_KWARGS


class VADCore:
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
        self.model = AutoModel(model=FUNASR_VAD_MODEL, model_revision="v2.0.4")
        print("VAD模型加载完成。")

    def process_chunk(self, chunk: npt.NDArray, cache) -> list:
        segments = self.model.generate(
            input=chunk,
            cache=cache,
            is_final=False,
            chunk_size=self.chunk_size,
            **FUNASR_VAD_KWARGS
        )

        # if segments and segments[0].get("value"):
        #     all_segments.extend(segments[0]["value"])
        return segments
