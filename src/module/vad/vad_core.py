#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

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
                from funasr import AutoModel
                self.model = AutoModel(model=self.settings.model, model_revision="v2.0.4", disable_pbar=True)
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
        """
        if self.status != VADStatus.READY:
            raise RuntimeError(f"VAD处理器未准备就绪，当前状态: {self.status}")

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
