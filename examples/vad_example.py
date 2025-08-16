#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.vad_processor import VADProcessor
from core.audio_input import AudioInputHandler
import pyaudio
import wave

def record_audio(duration=5, rate=16000, chunk=1024, channels=1, format=pyaudio.paInt16):
    """录制音频"""
    print(f"正在录制音频 {duration} 秒...")
    
    audio = pyaudio.PyAudio()
    
    # 打开音频流
    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
    
    frames = []
    
    # 录制音频
    for i in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    # 停止音频流
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # 将音频数据转换为numpy数组
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    
    print("音频录制完成")
    return audio_data, rate

def save_audio_to_file(audio_data, rate, filename="recorded_audio.wav"):
    """将音频数据保存到文件"""
    # 保存为WAV文件
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(rate)
    wf.writeframes(audio_data.tobytes())
    wf.close()
    print(f"音频已保存到 {filename}")

def main():
    print("VAD功能演示")
    print("=" * 50)
    
    # 录制音频
    audio_data, sample_rate = record_audio(duration=5)
    
    # 保存音频到文件（可选）
    save_audio_to_file(audio_data, sample_rate, "recorded_audio.wav")
    
    # 初始化VAD处理器
    vad_processor = VADProcessor(chunk_size=200, sample_rate=sample_rate)
    
    # 处理音频流
    print("正在处理音频流...")
    speech_segments = vad_processor.process_audio_stream(audio_data)
    
    # 输出结果
    if speech_segments:
        print(f"检测到语音段: {len(speech_segments)} 个")
        for i, segment in enumerate(speech_segments):
            print(f"  段 {i+1}: 开始={segment[0]}ms, 结束={segment[1]}ms")
    else:
        print("未检测到语音段")
    
    print("\n演示完成")

if __name__ == "__main__":
    main()
