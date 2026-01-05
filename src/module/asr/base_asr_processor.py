#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ASR处理器基类定义。"""

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import numpy as np
import numpy.typing as npt
import torch
from loguru import logger


class ASRStatus(Enum):
    """ASR处理器状态枚举。"""
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class BaseASRProcessor(ABC):
    """ASR处理器抽象基类。
    
    定义了ASR处理器的通用接口和基础功能。
    所有具体的ASR处理器实现都应继承此类。
    """

    def __init__(self, device: str = "auto") -> None:
        """初始化ASR处理器基类。
        
        Args:
            device: 推理设备，可选 "auto", "cuda:0", "cpu" 等。
        """
        self._setup_device(device)

        # 状态管理
        self.status = ASRStatus.UNINITIALIZED
        self.error_message: str | None = None
        self.model: Any = None
        
        # 初始化锁，确保线程安全
        self._init_lock = asyncio.Lock()
        logger.info(f"{self.__class__.__name__}已创建，状态: {self.status.value}。")

    def _setup_device(self, device: str) -> None:
        """设置推理设备。

        Args:
            device: 推理设备配置。
        """
        if device == "auto":
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        logger.info("ASR处理器使用 {device} 进行推理...", device=self.device)

    @abstractmethod
    async def initialize(self) -> None:
        """异步初始化ASR模型。
        
        子类必须实现此方法来加载具体的模型。
        """
        pass

    @abstractmethod
    def process_audio_data(self, audio_data: npt.NDArray[np.float32]) -> str | None:
        """处理单个音频数据并返回识别结果。
        
        Args:
            audio_data: 音频数据，numpy数组格式。
            
        Returns:
            识别的文本结果，如果失败则返回None。
        """
        pass

    @abstractmethod
    def process_audio(self, audio_data: list[npt.NDArray[np.float32]]) -> list[str]:
        """批量处理音频数据。
        
        Args:
            audio_data: 音频数据列表。
            
        Returns:
            识别结果列表。
        """
        pass

    def is_ready(self) -> bool:
        """检查处理器是否就绪。
        
        Returns:
            如果处理器已就绪返回True，否则返回False。
        """
        return self.status == ASRStatus.READY

    @staticmethod
    def _convert_audio_dtype(audio_data: npt.NDArray) -> npt.NDArray[np.float32]:
        """转换音频数据类型。

        将int16格式的音频数据转换为float32格式。

        Args:
            audio_data: 原始音频数据。

        Returns:
            转换后的float32格式音频数据。
        """
        if audio_data.dtype == np.int16:
            return audio_data.astype(np.float32) / 32768.0
        return audio_data

    @abstractmethod
    def process_audio_file(self, file_path: str) -> str | None:
        """处理音频文件并返回识别结果。
        
        Args:
            file_path: 音频文件路径。
            
        Returns:
            识别的文本结果，如果失败则返回None。
        """
        pass
