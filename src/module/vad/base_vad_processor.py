#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

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
        """初始化VAD处理器基类。"""
        self.settings = settings
        self.chunk_size = settings.chunk_size
        self.sample_rate = settings.sample_rate
        self.kwargs = {
            "MAX_SINGLE_SEGMENT_TIME": settings.max_single_segment_time
        }
        self.chunk_stride = int(self.chunk_size * self.sample_rate / 1000)

        self.status = VADStatus.UNINITIALIZED
        self.error_message: str | None = None

        self._init_lock = asyncio.Lock()
        logger.info(f"{self.__class__.__name__}已创建，状态: UNINITIALIZED。")

    @abstractmethod
    async def initialize(self) -> None:
        """初始化VAD模型，此方法幂等且线程安全。"""
        pass

    @abstractmethod
    def process_chunk(self, chunk: npt.NDArray, cache: dict[str, Any]) -> list:
        """处理音频块并返回语音活动检测结果。"""
        pass