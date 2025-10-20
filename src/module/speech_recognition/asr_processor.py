#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import torch
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

from config import (
    FUNASR_MODEL, FUNASR_VAD_MODEL, FUNASR_VAD_KWARGS, FUNASR_LANGUAGE, FUNASR_USE_ITN,
    BATCH_SIZE_S, MERGE_VAD, MERGE_LENGTH_S
)

class ASRProcessor:
    """
    实时语音识别(ASR)处理器
    """
    def __init__(self, device: str = "auto"):
        """
        初始化ASR处理器。
        
        Args:
            device: 推理设备 ("auto", "cuda:0", or "cpu").
        """
        self._setup_device(device)
        self._init_model()
        
    def _setup_device(self, device: str):
        """设置推理设备 (CPU/GPU)"""
        if device == "auto":
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        print(f"ASR处理器正在使用 {self.device} 进行推理...")

    def _init_model(self):
        """初始化FunASR语音识别模型"""
        print("ASR处理器正在加载语音识别模型...")
        self.model = AutoModel(
            model=FUNASR_MODEL,
            trust_remote_code=True,
            # vad_model=FUNASR_VAD_MODEL,
            # vad_kwargs=FUNASR_VAD_KWARGS,
            device=self.device,
        )
        print("ASR处理器语音识别模型加载完成。")

    def process_audio_data(self, audio_data):
        """
        处理音频数据并返回识别结果。
        
        Args:
            audio_data: 音频数据
            
        Returns:
            str: 识别的文本结果
        """
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # 进行语音识别
        res = self.model.generate(
            input=audio_data, cache={}, language=FUNASR_LANGUAGE, use_itn=FUNASR_USE_ITN,
            batch_size_s=BATCH_SIZE_S, merge_vad=MERGE_VAD,
            merge_length_s=MERGE_LENGTH_S,
            ban_emo_unk=True # 禁止输出感情标签
        )

        if res and res[0].get("text"):
            recognized_text = rich_transcription_postprocess(res[0]["text"])
            return recognized_text
        return None
