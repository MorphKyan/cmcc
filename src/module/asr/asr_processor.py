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


from src.module.asr.base_asr_processor import ASRStatus, BaseASRProcessor

class ASRProcessor(BaseASRProcessor):
    """实时语音识别处理器。"""

    def __init__(self, settings: FunASRSettings, device: str) -> None:
        """初始化ASR处理器。"""
        super().__init__(device=device)
        self.settings = settings
        
    async def initialize(self) -> None:
        """异步初始化FunASR语音识别模型，支持重新初始化。"""
        async with self._init_lock:
            if self.status == ASRStatus.INITIALIZING:
                logger.warning("ASR处理器正在初始化中，请等待。")
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
                    ban_emo_unk=True,  # 禁止输出感情标签
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
        if not self.is_ready():
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return None
        
        audio_data = self._convert_audio_dtype(audio_data)

        generate_kwargs = {
            "input": audio_data,
            "cache": {},
            "language": self.settings.language,
            "use_itn": self.settings.use_itn,
            "batch_size_s": self.settings.batch_size_s,
            "merge_vad": self.settings.merge_vad,
            "merge_length_s": self.settings.merge_length_s,
            "ban_emo_unk": True,
            "disable_pbar": True
        }

        if hasattr(self.settings, "hotwords") and self.settings.hotwords:
            generate_kwargs["hotwords"] = self.settings.hotwords

        res = self.model.generate(**generate_kwargs)

        if res and res[0].get("text"):
            recognized_text = rich_transcription_postprocess(res[0]["text"])
            return recognized_text
        return None

    def process_audio(self, audio_data: list[npt.NDArray[np.float32]]) -> list[str]:
        """批量处理音频数据。"""
        if not self.is_ready():
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return []
        
        audio_data = [self._convert_audio_dtype(data) for data in audio_data]

        generate_kwargs = {
            "input": audio_data,
            "cache": {},
            "language": self.settings.language,
            "use_itn": self.settings.use_itn,
            "batch_size_s": self.settings.batch_size_s,
            "merge_vad": self.settings.merge_vad,
            "merge_length_s": self.settings.merge_length_s,
            "ban_emo_unk": True,
            "disable_pbar": True
        }

        if hasattr(self.settings, "hotwords") and self.settings.hotwords:
            generate_kwargs["hotwords"] = self.settings.hotwords

        model_results = self.model.generate(**generate_kwargs)

        results = []
        if model_results:
            for result in model_results:
                recognized_text = rich_transcription_postprocess(result["text"])
                results.append(recognized_text)

        return results

    def process_audio_file(self, file_path: str) -> str | None:
        """处理音频文件并返回识别结果。"""
        if not self.is_ready():
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return None
            
        generate_kwargs = {
            "input": [file_path],
            "cache": {},
            "language": self.settings.language,
            "use_itn": self.settings.use_itn,
            "batch_size_s": self.settings.batch_size_s,
            "merge_vad": self.settings.merge_vad,
            "merge_length_s": self.settings.merge_length_s,
            "ban_emo_unk": True,
            "disable_pbar": True
        }

        if hasattr(self.settings, "hotwords") and self.settings.hotwords:
            generate_kwargs["hotwords"] = self.settings.hotwords

        res = self.model.generate(**generate_kwargs)

        if res and res[0].get("text"):
            recognized_text = rich_transcription_postprocess(res[0]["text"])
            return recognized_text
        return None
