#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时语音转文字程序
使用FunASR库和SenseVoiceSmall模型进行实时语音识别
支持中英文等多种语言的实时识别
"""

import pyaudio
import numpy as np
import threading
import queue
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

class RealTimeSpeechRecognizer:
    def __init__(self, device="auto"):
        """
        初始化实时语音识别器
        
        Args:
            device (str): 设备类型，"cuda:0"表示使用GPU，"cpu"表示使用CPU，"auto"表示自动检测
        """
        # 初始化模型
        model_dir = "iic/SenseVoiceSmall"
        
        # 根据设备选择使用GPU还是CPU
        if device == "auto":
            device = "cuda:0" if self._check_cuda() else "cpu"
        
        print(f"正在使用 {device} 进行推理...")
        
        self.model = AutoModel(
            model=model_dir,
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device=device,
            disable_update=True
        )
        
        # 音频参数
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # 采样率
        self.CHUNK = 1024  # 每个音频块的大小
        self.RECORD_SECONDS = 5  # 每次识别的时长（秒）
        
        # 创建音频流队列
        self.audio_queue = queue.Queue()
        
        # 初始化PyAudio
        self.audio = pyaudio.PyAudio()
        
        # 打开音频流
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_callback
        )
        
    def _check_cuda(self):
        """检查CUDA是否可用"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def start_recognition(self):
        """开始实时语音识别"""
        print("=" * 50)
        print("实时语音转文字程序")
        print("=" * 50)
        print("正在加载模型，请稍候...")
        print("开始录音，按 Ctrl+C 停止...")
        print("-" * 50)
        
        # 开始录音
        self.stream.start_stream()
        
        try:
            while True:
                # 收集音频数据
                frames = []
                for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    data = self.audio_queue.get()
                    frames.append(data)
                
                # 将音频数据转换为numpy数组
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                
                # 在新线程中进行语音识别，避免阻塞录音
                recognition_thread = threading.Thread(target=self.recognize_audio, args=(audio_data,))
                recognition_thread.start()
                
        except KeyboardInterrupt:
            print("\n" + "-" * 50)
            print("录音已停止")
            print("感谢使用实时语音转文字程序！")
        
        # 停止并关闭音频流
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
    
    def recognize_audio(self, audio_data):
        """识别音频数据"""
        try:
            # 将音频数据转换为float32格式
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            # 进行语音识别
            res = self.model.generate(
                input=audio_data,
                cache={},
                language="auto",  # 自动检测语言
                use_itn=True,     # 使用逆文本归一化
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15,
            )
            
            # 处理结果
            if res and len(res) > 0:
                text = rich_transcription_postprocess(res[0]["text"])
                if text.strip():  # 只输出非空结果
                    print(f"[识别结果] {text}")
        except Exception as e:
            print(f"[错误] 识别出错: {e}")

def main():
    """主函数"""
    # 创建识别器实例（默认自动选择设备）
    recognizer = RealTimeSpeechRecognizer(device="cpu")
    
    # 开始识别
    recognizer.start_recognition()

if __name__ == "__main__":
    main()
