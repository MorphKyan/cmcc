"""Text-to-Speech (TTS) Service using Sherpa-ONNX."""

import os
import time
from typing import Optional

import sherpa_onnx
from loguru import logger

from src.config.config import TTSSettings


class TTSService:
    """TTS Service to generate audio from text using Sherpa-ONNX VITS models."""

    def __init__(self, config: TTSSettings):
        self.config = config
        self.tts: Optional[sherpa_onnx.OfflineTts] = None
        self._is_initialized = False

    async def initialize(self) -> None:
        """异步初始化 TTS 模型，避免阻塞主线程"""
        if self._is_initialized:
            return

        try:
            logger.info(f"正在初始化 TTS 模型，路径: {self.config.model_dir}")
            
            # 校验模型文件
            model_path = os.path.join(self.config.model_dir, "model.onnx")
            lexicon_path = os.path.join(self.config.model_dir, "lexicon.txt")
            tokens_path = os.path.join(self.config.model_dir, "tokens.txt")
            
            if not os.path.exists(model_path):
                logger.error(f"TTS 模型初始化失败：找不到模型文件 {model_path}")
                return

            # 配置模型参数
            # 使用 try-except 以防止因为缺少字典带来的崩溃
            dict_dir = os.path.join(self.config.model_dir, "dict")
            if not os.path.exists(dict_dir):
                dict_dir = ""
                
            tts_config = sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(
                    vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                        model=model_path,
                        lexicon=lexicon_path,
                        tokens=tokens_path,
                        dict_dir=dict_dir,
                    ),
                    num_threads=self.config.num_threads,
                ),
            )
            
            # 添加规则 FST（如果是 MeloTTS 转换版，通常有 date.fst 和 number.fst）
            rule_fsts = []
            for fst_name in ["date.fst", "number.fst", "phone.fst", "new_heteronym.fst"]:
                fst_path = os.path.join(self.config.model_dir, fst_name)
                if os.path.exists(fst_path):
                    rule_fsts.append(fst_path)
            
            if rule_fsts:
                tts_config.rule_fsts = ",".join(rule_fsts)

            # 初始化引擎
            self.tts = sherpa_onnx.OfflineTts(tts_config)
            self._is_initialized = True
            
            # 预热模型
            self.tts.generate("预热完毕", sid=self.config.speaker_id, speed=self.config.speed)
            
            logger.info("TTS 模型初始化并预热完毕")
        except Exception as e:
            logger.exception(f"TTS 模型初始化失败: {e}")

    def generate_audio_bytes(self, text: str) -> Optional[bytes]:
        """将文本转换为 WAV 音频字节流 (同步方法)"""
        if not self._is_initialized or self.tts is None:
            logger.error("TTS 模型尚未初始化，无法生成语音")
            return None
            
        try:
            start_time = time.perf_counter()
            
            # 生成音频
            audio = self.tts.generate(
                text, 
                sid=self.config.speaker_id, 
                speed=self.config.speed
            )
            
            # 将生成的采样点数据打包成标准的 WAV 格式字节流
            import io
            import soundfile as sf
            
            buffer = io.BytesIO()
            sf.write(buffer, audio.samples, audio.sample_rate, format='WAV', subtype='PCM_16')
            
            elapsed = time.perf_counter() - start_time
            logger.info(f"[TTS] 语音生成完毕，耗时 {elapsed:.3f}s，字数 {len(text)}")
            
            return buffer.getvalue()
        except Exception as e:
            logger.exception(f"TTS 语音生成失败: {e}")
            return None
