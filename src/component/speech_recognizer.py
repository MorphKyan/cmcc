#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio
import numpy as np
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import numpy as np
import pyaudio
import torch
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

from .config import (
    SENSE_VOICE_MODEL_DIR, VAD_MODEL, VAD_KWARGS, LANGUAGE, USE_ITN,
    BATCH_SIZE_S, MERGE_VAD, MERGE_LENGTH_S, FORMAT, CHANNELS, RATE,
    CHUNK, RECORD_SECONDS
)
from .rag_processor import RAGProcessor
from .llm_handler import LLMHandler

class RealTimeSpeechRecognizer:
    """
    一个集成了实时语音识别、RAG和LLM的控制器。
    """
    def __init__(self, device: str = "auto", force_rag_reload: bool = False, record_seconds: int = 5):
        """
        初始化实时语音识别器。
        
        Args:
            device: 推理设备 ("auto", "cuda:0", or "cpu").
            force_rag_reload: 是否强制重新加载RAG数据。
            record_seconds: 每次识别的录音时长。
        """
        self.record_seconds = record_seconds
        self._setup_device(device)
        self._init_asr_model()
        
        # 初始化核心处理器
        self.rag_processor = RAGProcessor(force_reload=force_rag_reload)
        self.llm_handler = LLMHandler()
        
        self.audio_queue: queue.Queue[bytes] = queue.Queue()
        self._init_audio_stream()
        
        # 使用线程池管理识别任务
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _setup_device(self, device: str):
        """设置推理设备 (CPU/GPU)"""
        if device == "auto":
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        print(f"正在使用 {self.device} 进行推理...")

    def _init_asr_model(self):
        """初始化FunASR语音识别模型"""
        print("正在加载语音识别模型...")
        self.model = AutoModel(
            model=SENSE_VOICE_MODEL_DIR,
            vad_model=VAD_MODEL,
            vad_kwargs=VAD_KWARGS,
            device=self.device,
        )
        print("语音识别模型加载完成。")

    def _init_audio_stream(self):
        """初始化PyAudio音频流"""
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            stream_callback=self._audio_callback
        )

    def _audio_callback(self, in_data: bytes, frame_count: int, time_info: dict, status: int) -> tuple[Optional[bytes], int]:
        """音频流回调函数，将数据放入队列。"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def _process_recognition_and_llm(self, audio_data: np.ndarray):
        """在一个线程中处理ASR识别和LLM调用"""
        try:
            # 1. ASR - 语音转文字
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            res = self.model.generate(
                input=audio_data, cache={}, language=LANGUAGE, use_itn=USE_ITN,
                batch_size_s=BATCH_SIZE_S, merge_vad=MERGE_VAD, 
                merge_length_s=MERGE_LENGTH_S
            )
            
            if not res or not res[0].get("text"):
                return
                
            recognized_text = rich_transcription_postprocess(res[0]["text"])
            if not recognized_text.strip():
                return
                
            print(f"\n[识别结果] {recognized_text}")
            
            # 2. RAG - 检索相关上下文
            retrieved_docs = self.rag_processor.retrieve_context(recognized_text)
            
            # 3. LLM - 获取结构化指令
            llm_response = self.llm_handler.get_response(recognized_text, retrieved_docs)
            
            print(f"[大模型响应] {llm_response}")

        except Exception as e:
            print(f"[错误] 处理音频时出错: {e}")

    def start(self):
        """启动实时识别流程"""
        print("\n" + "=" * 50)
        print("      中国移动智慧展厅 - 中央控制AI助手")
        print("=" * 50)
        print("开始录音，按 Ctrl+C 停止...")
        
        self.stream.start_stream()
        
        try:
            while True:
                # 从队列中获取数据并拼接成一个完整的音频块
                frames = [self.audio_queue.get() for _ in range(int(RATE / CHUNK * self.record_seconds))]
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                
                # 使用线程池提交任务，避免阻塞主录音循环
                self.executor.submit(self._process_recognition_and_llm, audio_data)
                
        except KeyboardInterrupt:
            print("\n" + "-" * 50)
            print("录音已停止。")
        finally:
            self.stop()

    def stop(self):
        """停止并清理资源"""
        print("正在关闭音频流和清理资源...")
        self.executor.shutdown(wait=True)  # 等待所有任务完成
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print("程序已退出。")
