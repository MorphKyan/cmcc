#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fun-ASR-Nano ASR处理器实现。"""

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
from funasr import AutoModel
from loguru import logger

from src.module.asr.base_asr_processor import ASRStatus, BaseASRProcessor


@dataclass
class NanoASRSettings:
    """Nano ASR处理器配置。
    
    Attributes:
        model: 模型路径或名称。
        language: 识别语言，可选值：
            - Fun-ASR-Nano-2512: 中文、英文、日文
            - Fun-ASR-MLT-Nano-2512: 中文、英文、粤语、日文、韩文、越南语、
              印尼语、泰语、马来语、菲律宾语、阿拉伯语、印地语、保加利亚语、
              克罗地亚语、捷克语、丹麦语、荷兰语、爱沙尼亚语、芬兰语、希腊语、
              匈牙利语、爱尔兰语、拉脱维亚语、立陶宛语、马耳他语、波兰语、
              葡萄牙语、罗马尼亚语、斯洛伐克语、斯洛文尼亚语、瑞典语
        itn: 是否启用逆文本正则化（数字、日期等格式化）。
        batch_size: 批量处理大小。
        use_vad: 是否启用VAD（语音活动检测）。
        vad_model: VAD模型名称。
        vad_max_single_segment_time: VAD单段最大时长(ms)。
        hotwords: 热词列表，用于提升特定词汇的识别准确率。
    """
    model: str = "FunAudioLLM/Fun-ASR-Nano-2512"
    language: str = "中文"
    itn: bool = True
    batch_size: int = 1
    use_vad: bool = False
    # vad_model: str = "fsmn-vad"
    # vad_max_single_segment_time: int = 30000
    hotwords: list[str] = field(default_factory=list)


class NanoASRProcessor(BaseASRProcessor):
    """Fun-ASR-Nano ASR处理器。
    
    基于FunAudioLLM/Fun-ASR-Nano-2512模型的语音识别处理器。
    支持中文、英文、日文等语言的实时语音识别。
    """

    def __init__(self, settings: NanoASRSettings | None = None, device: str = "auto") -> None:
        """初始化Nano ASR处理器。
        
        Args:
            settings: Nano ASR配置，如果为None则使用默认配置。
            device: 推理设备，可选 "auto", "cuda:0", "cpu" 等。
        """
        super().__init__(device=device)
        self.settings = settings or NanoASRSettings()

    async def initialize(self) -> None:
        """异步初始化Fun-ASR-Nano语音识别模型。"""
        async with self._init_lock:
            if self.status == ASRStatus.INITIALIZING:
                logger.warning("Nano ASR处理器正在初始化中，请等待。")
                return
            
            self.status = ASRStatus.INITIALIZING
            self.error_message = None
            
            try:
                logger.info(f"Nano ASR处理器正在加载模型: {self.settings.model}...")
                
                if self.settings.use_vad:
                    # 使用VAD模式初始化
                    self.model = AutoModel(
                        model=self.settings.model,
                        trust_remote_code=True,
                        remote_code="./model.py",
                        vad_model=self.settings.vad_model,
                        vad_kwargs={"max_single_segment_time": self.settings.vad_max_single_segment_time},
                        device=self.device,
                    )
                else:
                    # 标准模式初始化
                    self.model = AutoModel(
                        model=self.settings.model,
                        trust_remote_code=True,
                        remote_code="./model.py",
                        device=self.device,
                    )
                
                self.status = ASRStatus.READY
                logger.info("Nano ASR处理器模型加载完成。")
            except Exception as e:
                self.status = ASRStatus.ERROR
                self.error_message = f"Nano ASR处理器初始化失败: {str(e)}"
                logger.exception(self.error_message)
                raise

    def process_audio_data(self, audio_data: npt.NDArray[np.float32]) -> str | None:
        """处理音频数据并返回识别结果。
        
        Args:
            audio_data: 音频数据，numpy数组格式。
            
        Returns:
            识别的文本结果，如果失败则返回None。
        """
        if not self.is_ready():
            logger.error("Nano ASR处理器未就绪，无法处理音频数据。")
            return None
        
        audio_data = self._convert_audio_dtype(audio_data)
        
        generate_kwargs = {
            "input": audio_data,
            "cache": {},
            "batch_size": self.settings.batch_size,
            "language": self.settings.language,
            "itn": self.settings.itn,
        }
        
        # 添加热词（如果有）
        if self.settings.hotwords:
            generate_kwargs["hotwords"] = self.settings.hotwords
        
        res = self.model.generate(**generate_kwargs)
        
        if res and res[0].get("text"):
            return res[0]["text"]
        return None

    def process_audio(self, audio_data: list[npt.NDArray[np.float32]]) -> list[str]:
        """批量处理音频数据。
        
        Args:
            audio_data: 音频数据列表。
            
        Returns:
            识别结果列表。
        """
        if not self.is_ready():
            logger.error("Nano ASR处理器未就绪，无法处理音频数据。")
            return []
        
        # 转换所有音频数据类型
        converted_audio_data = [self._convert_audio_dtype(data) for data in audio_data]
        
        generate_kwargs = {
            "input": converted_audio_data,
            "cache": {},
            "batch_size": self.settings.batch_size,
            "language": self.settings.language,
            "itn": self.settings.itn,
        }
        
        # 添加热词（如果有）
        if self.settings.hotwords:
            generate_kwargs["hotwords"] = self.settings.hotwords
        
        model_results = self.model.generate(**generate_kwargs)
        
        results = []
        if model_results:
            for result in model_results:
                if result.get("text"):
                    results.append(result["text"])
        
        return results

    def process_audio_file(self, file_path: str) -> str | None:
        """处理音频文件并返回识别结果。
        
        Args:
            file_path: 音频文件路径。
            
        Returns:
            识别的文本结果，如果失败则返回None。
        """
        if not self.is_ready():
            logger.error("Nano ASR处理器未就绪，无法处理音频文件。")
            return None
        
        generate_kwargs = {
            "input": [file_path],
            "cache": {},
            "batch_size": self.settings.batch_size,
            "language": self.settings.language,
            "itn": self.settings.itn,
        }
        
        # 添加热词（如果有）
        if self.settings.hotwords:
            generate_kwargs["hotwords"] = self.settings.hotwords
        
        res = self.model.generate(**generate_kwargs)
        
        if res and res[0].get("text"):
            return res[0]["text"]
        return None
