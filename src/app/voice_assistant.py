#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import queue
import threading

from config import (
    RATE,
    VIDEOS_DATA_PATH, CHROMA_DB_PATH, EMBEDDING_MODEL, TOP_K_RESULTS
)
from core.rag_processor import RAGProcessor
from core.audio_input import AudioInputHandler
from core.vad_processor import VADProcessor
from core.asr_processor import ASRProcessor

class VoiceAssistant:
    """
    一个集成了实时语音识别、RAG和LLM的控制器。
    """
    def __init__(self, llm_handler, device: str = "auto", force_rag_reload: bool = False):
        """
        初始化实时语音识别器。
        
        Args:
            llm_handler: 已初始化的LLM处理器实例。
            device: 推理设备 ("auto", "cuda:0", or "cpu").
            force_rag_reload: 是否强制重新加载RAG数据。
        """
        self.device = device

        # 初始化音频输入处理器
        self.audio_input_handler = AudioInputHandler()
        self.audio_input_handler.init_audio_stream()
        # 初始化VAD处理器
        self.vad_processor = VADProcessor()        
        # 初始化ASR处理器
        self.asr_processor = ASRProcessor(device=device)
        # 初始化RAG处理器
        self.rag_processor = RAGProcessor(
            videos_data_path=VIDEOS_DATA_PATH,
            chroma_db_path=CHROMA_DB_PATH,
            embedding_model=EMBEDDING_MODEL,
            top_k_results=TOP_K_RESULTS,
            force_reload=force_rag_reload
        )
        # LLM处理器
        self.llm_handler = llm_handler

        # 初始化处理队列
        self.vad_output_queue = queue.Queue()
        self.asr_output_queue = queue.Queue()
        self.rag_output_queue = queue.Queue()

        # 初始化线程和停止事件
        self.stop_event = threading.Event()
        self.vad_thread = None
        self.asr_thread = None
        self.rag_thread = None
        self.llm_thread = None

    def _vad_thread_loop(self):
        """VAD线程循环，处理实时音频流并分割语音片段。"""
        while not self.stop_event.is_set():
            try:
                audio_chunk_bytes = self.audio_input_handler.get_audio_data(timeout=1)
                audio_chunk = np.frombuffer(audio_chunk_bytes, dtype=np.int16)
                # 使用VAD检测语音活动
                speech_segments = self.vad_processor.process_audio_chunk(audio_chunk)

                # 将检测到的语音片段放入ASR队列
                for segment in speech_segments:
                    start, end, audio_data = segment
                    print(f"[VAD] 检测到语音段: {start:.2f}ms - {end:.2f}ms, 长度: {len(audio_data)/RATE:.2f}s")
                    self.vad_output_queue.put(audio_data)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VAD错误] {e}")

    def _asr_thread_loop(self):
        """ASR线程循环，处理语音识别。"""
        while not self.stop_event.is_set():
            try:
                # 从VAD队列中获取分割好的语音片段
                audio_data = self.vad_output_queue.get(timeout=1)
                
                # 使用ASR处理器处理音频数据
                recognized_text = self.asr_processor.process_audio_data(audio_data)
                
                if recognized_text and recognized_text.strip():
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
        self.vad_thread = threading.Thread(target=self._vad_thread_loop, daemon=True)
        self.asr_thread = threading.Thread(target=self._asr_thread_loop, daemon=True)
        self.rag_thread = threading.Thread(target=self._rag_thread_loop, daemon=True)
        self.llm_thread = threading.Thread(target=self._llm_thread_loop, daemon=True)

        self.vad_thread.start()
        self.asr_thread.start()
        self.rag_thread.start()
        self.llm_thread.start()

        self.audio_input_handler.start_stream()

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
        self.audio_input_handler.stop()

        # 等待所有线程结束
        if self.vad_thread and self.vad_thread.is_alive():
            self.vad_thread.join()
        if self.asr_thread and self.asr_thread.is_alive():
            self.asr_thread.join()
        if self.rag_thread and self.rag_thread.is_alive():
            self.rag_thread.join()
        if self.llm_thread and self.llm_thread.is_alive():
            self.llm_thread.join()

        print("程序已退出。")
