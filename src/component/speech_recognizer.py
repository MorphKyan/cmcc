#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyaudio
import numpy as np
import queue
import threading
from typing import Optional, Tuple

import numpy as np
import pyaudio
import torch
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

from config import (
    SENSE_VOICE_MODEL_DIR, VAD_MODEL, VAD_KWARGS, LANGUAGE, USE_ITN,
    BATCH_SIZE_S, MERGE_VAD, MERGE_LENGTH_S, FORMAT, CHANNELS, RATE,
    CHUNK,
    SCREENS_DATA_PATH, DOORS_DATA_PATH, VIDEOS_DATA_PATH,
    CHROMA_DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS,
    ARK_API_KEY, ARK_BASE_URL, LLM_MODEL_NAME, SYSTEM_PROMPT_TEMPLATE
)
from .rag_processor import RAGProcessor

class RealTimeSpeechRecognizer:
    """
    一个集成了实时语音识别、RAG和LLM的控制器。
    """
    def __init__(self, llm_handler, device: str = "auto", force_rag_reload: bool = False, record_seconds: int = 5):
        """
        初始化实时语音识别器。
        
        Args:
            llm_handler: 已初始化的LLM处理器实例。
            device: 推理设备 ("auto", "cuda:0", or "cpu").
            force_rag_reload: 是否强制重新加载RAG数据。
            record_seconds: 每次识别的录音时长。
        """
        self.record_seconds = record_seconds
        self._setup_device(device)
        self._init_asr_model()
        
        # 初始化核心处理器
        self.rag_processor = RAGProcessor(
            screens_data_path=SCREENS_DATA_PATH,
            doors_data_path=DOORS_DATA_PATH,
            videos_data_path=VIDEOS_DATA_PATH,
            chroma_db_path=CHROMA_DB_PATH,
            embedding_model=EMBEDDING_MODEL,
            top_k_results=TOP_K_RESULTS,
            force_reload=force_rag_reload
        )
        self.llm_handler = llm_handler

        # 初始化处理队列
        self.audio_queue = queue.Queue()
        self.asr_output_queue = queue.Queue()
        self.rag_output_queue = queue.Queue()

        self._init_audio_stream()

        # 初始化线程和停止事件
        self.stop_event = threading.Event()
        self.asr_thread = None
        self.rag_thread = None
        self.llm_thread = None

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

    def _asr_thread_loop(self):
        """ASR线程循环，处理语音识别。"""
        while not self.stop_event.is_set():
            try:
                # 从队列中获取数据并拼接成一个完整的音频块
                frames = [self.audio_queue.get(timeout=1) for _ in range(int(RATE / CHUNK * self.record_seconds))]
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                
                if audio_data.dtype == np.int16:
                    audio_data = audio_data.astype(np.float32) / 32768.0

                res = self.model.generate(
                    input=audio_data, cache={}, language=LANGUAGE, use_itn=USE_ITN,
                    batch_size_s=BATCH_SIZE_S, merge_vad=MERGE_VAD,
                    merge_length_s=MERGE_LENGTH_S
                )

                if res and res[0].get("text"):
                    recognized_text = rich_transcription_postprocess(res[0]["text"])
                    if recognized_text.strip():
                        print(f"\n[识别结果] {recognized_text}")
                        self.asr_output_queue.put(recognized_text)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ASR错误] {e}")

    def _rag_thread_loop(self):
        """RAG线程循环，处理上下文检索。"""
        while not self.stop_event.is_set():
            try:
                recognized_text = self.asr_output_queue.get(timeout=1)
                retrieved_docs = self.rag_processor.retrieve_context(recognized_text)
                self.rag_output_queue.put((recognized_text, retrieved_docs))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[RAG错误] {e}")

    def _llm_thread_loop(self):
        """LLM线程循环，处理最终响应。"""
        while not self.stop_event.is_set():
            try:
                recognized_text, retrieved_docs = self.rag_output_queue.get(timeout=1)
                llm_response = self.llm_handler.get_response(recognized_text, retrieved_docs)
                print(f"[大模型响应] {llm_response}")
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[LLM错误] {e}")

    def start(self):
        """启动实时识别流程"""
        print("\n" + "=" * 50)
        print("      中国移动智慧展厅 - 中央控制AI助手")
        print("=" * 50)
        print("开始录音，按 Ctrl+C 停止...")

        # 启动处理线程
        self.stop_event.clear()
        self.asr_thread = threading.Thread(target=self._asr_thread_loop, daemon=True)
        self.rag_thread = threading.Thread(target=self._rag_thread_loop, daemon=True)
        self.llm_thread = threading.Thread(target=self._llm_thread_loop, daemon=True)

        self.asr_thread.start()
        self.rag_thread.start()
        self.llm_thread.start()

        self.stream.start_stream()

        try:
            # 保持主线程运行，直到接收到中断信号
            while not self.stop_event.is_set():
                threading.Event().wait(0.1)
        except KeyboardInterrupt:
            print("\n" + "-" * 50)
            print("收到停止信号，正在关闭...")
        finally:
            self.stop()

    def stop(self):
        """停止并清理资源"""
        print("正在关闭音频流和清理资源...")
        self.stop_event.set()

        # 停止音频流
        if self.stream.is_active():
            self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        # 等待所有线程结束
        if self.asr_thread and self.asr_thread.is_alive():
            self.asr_thread.join()
        if self.rag_thread and self.rag_thread.is_alive():
            self.rag_thread.join()
        if self.llm_thread and self.llm_thread.is_alive():
            self.llm_thread.join()

        print("程序已退出。")
