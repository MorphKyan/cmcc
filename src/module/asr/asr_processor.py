#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio

import numpy as np
import numpy.typing as npt
import torch
from enum import Enum
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from loguru import logger

from src.config.config import FunASRSettings


class ASRStatus(Enum):
    """ASR处理器状态枚举。"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"


class ASRProcessor:
    """实时语音识别处理器。"""

    def __init__(self, settings: FunASRSettings, device: str = "auto") -> None:
        """初始化ASR处理器。"""
        self.settings = settings
        self._setup_device(device)
        
        # 状态管理
        self.status = ASRStatus.UNINITIALIZED
        self.error_message = None
        self.model = None
        
        # 初始化锁，确保线程安全
        self._init_lock = asyncio.Lock()
        logger.info(f"{self.__class__.__name__}已创建，状态: {self.status.value}。")

    def _setup_device(self, device: str) -> None:
        """设置推理设备。"""
        if device == "auto":
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        logger.info("ASR处理器使用 {device} 进行推理...", device=self.device)

    async def initialize(self) -> None:
        """异步初始化FunASR语音识别模型。"""
        async with self._init_lock:
            if self.status == ASRStatus.INITIALIZING:
                logger.warning("ASR处理器正在初始化中，请勿重复调用。")
                return
            
            if self.status == ASRStatus.READY:
                logger.warning("ASR处理器已初始化完成，请勿重复调用。")
                return
            
            self.status = ASRStatus.INITIALIZING
            self.error_message = None
            
            try:
                logger.info("ASR处理器正在加载语音识别模型...")
                self.model = AutoModel(
                    model=self.settings.model,
                    trust_remote_code=False,
                    # vad_model=self.settings.VAD_MODEL,
                    # vad_kwargs=self.settings.VAD_KWARGS,
                    device=self.device,
                )
                self.status = ASRStatus.READY
                logger.info("ASR处理器语音识别模型加载完成。")
            except Exception as e:
                self.status = ASRStatus.ERROR
                self.error_message = f"ASR处理器初始化失败: {str(e)}"
                logger.exception(self.error_message)
                raise

    def process_audio_data(self, audio_data: npt.NDArray[np.float32]) -> str | None:
        """处理音频数据并返回识别结果。"""
        if self.status != ASRStatus.READY:
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return None
        
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0

        res = self.model.generate(
            input=audio_data, cache={}, language=self.settings.language, use_itn=self.settings.use_itn,
            batch_size_s=self.settings.batch_size_s, merge_vad=self.settings.merge_vad,
            merge_length_s=self.settings.merge_length_s,
            ban_emo_unk=True  # 禁止输出感情标签
        )

        if res and res[0].get("text"):
            recognized_text = rich_transcription_postprocess(res[0]["text"])
            return recognized_text
        return None

    def process_audio(self, audio_data: list[npt.NDArray[np.float32]]) -> list[str]:
        """批量处理音频数据。"""
        if self.status != ASRStatus.READY:
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return []
        
        for data in audio_data:
            if data.dtype == np.int16:
                data = data.astype(np.float32) / 32768.0

        model_results = self.model.generate(
            input=audio_data, cache={}, language=self.settings.language, use_itn=self.settings.use_itn,
            batch_size_s=self.settings.batch_size_s, merge_vad=self.settings.merge_vad,
            merge_length_s=self.settings.merge_length_s,
            ban_emo_unk=True
        )

        results = []
        if model_results:
            for result in model_results:
                recognized_text = rich_transcription_postprocess(result["text"])
                results.append(recognized_text)

        return results
