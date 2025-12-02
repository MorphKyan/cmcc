#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        异步初始化VAD模型。
        """
        async with self._init_lock:
            if self.status == VADStatus.INITIALIZING:
                logger.warning("初始化已在进行中，请等待。")
                return
            self.status = VADStatus.INITIALIZING
            logger.info("开始初始化VAD处理器...")

            try:
                # 初始化VAD模型
                logger.info("正在加载VAD模型...")
                from funasr import AutoModel
                self.model = AutoModel(model=self.settings.model, model_revision="v2.0.4")
                logger.info("VAD模型加载完成。")

                self.status = VADStatus.READY
                self.error_message = None
                logger.success("VAD处理器初始化完成，状态: READY。")
            except Exception as e:
                self.status = VADStatus.ERROR
                self.error_message = f"VAD初始化失败: {e}"
                logger.exception(self.error_message)
                # 向上抛出异常，让调用者知道失败了
                raise

    async def restart(self) -> None:
        """
        强制重启VAD处理器，可用于从任何状态恢复。
        此方法是幂等的，并且是线程安全的。
        """
        logger.info("开始强制重启VAD处理器...")
        await self.initialize()

    def process_chunk(self, chunk: npt.NDArray, cache) -> list:
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
