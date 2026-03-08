import asyncio
import os
import onnxruntime
import soundfile as sf
import sherpa_onnx
import numpy as np
import numpy.typing as npt
from loguru import logger

from src.config.config import ASRSettings


from src.module.asr.base_asr_processor import ASRStatus, BaseASRProcessor

class ASRProcessor(BaseASRProcessor):
    """实时语音识别与声纹识别处理器"""

    def __init__(self, settings: ASRSettings, device: str) -> None:
        """初始化ASR处理器。"""
        super().__init__(device=device)
        self.settings = settings
        self.recognizer = None
        self.spk_session = None
        
    async def initialize(self) -> None:
        """异步初始化ONNX模型，支持重新初始化。"""
        async with self._init_lock:
            if self.status == ASRStatus.INITIALIZING:
                logger.warning("ASR处理器正在初始化中，请等待。")
                return
            
            self.status = ASRStatus.INITIALIZING
            self.error_message = None
            
            try:
                # 1. 初始 SenseVoice (ASR)
                logger.info("正在加载 sherpa-onnx SenseVoice 模型...")
                sv_dir = self.settings.model_dir
                
                model_file = os.path.join(sv_dir, "model.onnx")
                tokens_file = os.path.join(sv_dir, "tokens.txt")
                
                self.recognizer = sherpa_onnx.OfflineRecognizer.from_sense_voice(
                    model=model_file,
                    tokens=tokens_file,
                    num_threads=1,
                    language=self.settings.language,
                    use_itn=self.settings.use_itn,
                    debug=False
                )
                
                # 2. 初始 WeSpeaker (SPK)
                logger.info("正在加载 onnxruntime WeSpeaker 模型...")
                providers = ['CPUExecutionProvider']
                # if "cuda" in self.device.lower():
                #     providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                self.spk_session = onnxruntime.InferenceSession(
                    self.settings.spk_model_path, 
                    providers=providers
                )
                
                self.status = ASRStatus.READY
                logger.info("ASR和SPK全部ONNX模型加载完成。")
            except Exception as e:
                self.status = ASRStatus.ERROR
                self.error_message = f"ASR处理器初始化失败: {str(e)}"
                logger.exception(self.error_message)
                raise


    def is_ready(self) -> bool:
        return self.status == ASRStatus.READY and self.recognizer is not None and self.spk_session is not None

    def extract_speaker_embedding(self, audio_data: npt.NDArray[np.float32]) -> npt.NDArray[np.float32] | None:
        """从音频数据中提取声纹特征（WeSpeaker ResNet34 ONNX）"""
        if not self.is_ready():
            logger.error("ASR和SPK处未就绪，无法提取声纹。")
            return None
            
        try:
            # WeSpeaker ResNet34 处理
            # WeSpeaker 模型通常期望输入的 shape 是 ( batch_size, T_frames, feat_dim)
            # 或者直接包含原始音频的 Fbank 特征。我们在此处引入 torch-free 的 fbank 提取
            import kaldi_native_fbank as knf
            
            opts = knf.FbankOptions()
            opts.frame_opts.samp_freq = self.settings.sample_rate
            opts.frame_opts.dither = 0.0
            opts.mel_opts.num_bins = 80
            
            fbank = knf.OnlineFbank(opts)
            fbank.accept_waveform(self.settings.sample_rate, (audio_data * 32768).tolist())
            fbank.input_finished()
            
            features = []
            for i in range(fbank.num_frames_ready):
                features.append(fbank.get_frame(i))
            
            if not features:
                logger.warning("未能提取有效 fbank 特征。")
                return None
                
            features = np.vstack(features)
            # 均值方差归一化可以提高稳定性，如果模型自带可以忽略
            features = features - np.mean(features, axis=0, keepdims=True)
            
            # shape 调整为 (1, T, 80)
            features = np.expand_dims(features, axis=0).astype(np.float32)

            inputs = {self.spk_session.get_inputs()[0].name: features}
            outputs = self.spk_session.run(None, inputs)
            embedding = outputs[0][0] # shape (256,) or similar
            
            logger.info(f"[声纹提取成功] 成功提取当前帧的声纹特征 (维度: {embedding.shape})。")
            return embedding
        except Exception as e:
            logger.error(f"提取声纹失败: {e}")
            return None
            
    def compute_similarity(self, emb1: npt.NDArray[np.float32], emb2: npt.NDArray[np.float32]) -> float:
        """计算两个声纹特征的余弦相似度"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def process_audio_data(self, audio_data: npt.NDArray[np.float32]) -> str | None:
        """处理音频数据并返回识别结果。"""
        if not self.is_ready():
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return None
        
        audio_data = self._convert_audio_dtype(audio_data)
        
        # Sherpa-ONNX 的离线识别流程
        stream = self.recognizer.create_stream()
        stream.accept_waveform(self.settings.sample_rate, audio_data)
        self.recognizer.decode_stream(stream)
        
        recognized_text = stream.result.text
        
        if recognized_text:
            logger.info(f"[ASR 识别成功] 识别出文本: '{recognized_text}'")
            return recognized_text
        
        logger.warning("[ASR 识别截断] ASR 引擎未识别出任何有效文本。")
        return None

    def process_audio(self, audio_data_list: list[npt.NDArray[np.float32]]) -> list[str]:
        """批量处理音频数据。"""
        if not self.is_ready():
            logger.error("ASR处理器未就绪，无法处理音频数据。")
            return []
        
        results = []
        for audio_data in audio_data_list:
            text = self.process_audio_data(audio_data)
            if text:
                results.append(text)
                
        return results


