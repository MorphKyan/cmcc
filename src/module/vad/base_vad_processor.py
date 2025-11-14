#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from abc import ABC, abstractmethod
from enum import Enum

import numpy.typing as npt
from loguru import logger

from src.config.config import VADSettings


class VADStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class BaseVADProcessor(ABC):
    def __init__(self, settings: VADSettings) -> None:
        """
        初始化VAD处理器基类。

        Args:
            settings (VADSettings): VAD配置
        """
        self.settings = settings
        self.chunk_size = settings.chunk_size
        self.sample_rate = settings.sample_rate
        self.kwargs = {
            "MAX_SINGLE_SEGMENT_TIME": settings.max_single_segment_time
        }
        self.chunk_stride = int(self.chunk_size * self.sample_rate / 1000)

        # 初始化状态和核心组件
        self.status = VADStatus.UNINITIALIZED
        self.error_message: str | None = None

        # 使用asyncio.Lock来防止并发初始化
        self._init_lock = asyncio.Lock()
        logger.info(f"{self.__class__.__name__}已创建，状态: UNINITIALIZED。")

    @abstractmethod
    async def initialize(self) -> None:
        """
        执行耗时的初始化过程：加载VAD模型。
        此方法是幂等的，并且是线程安全的。
        """
        pass

    @abstractmethod
    def process_chunk(self, chunk: npt.NDArray, cache) -> list:
        """
        处理音频块并返回语音活动检测结果。
        """
        pass