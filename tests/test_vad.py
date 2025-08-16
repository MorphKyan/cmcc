#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import soundfile as sf

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.vad_processor import VADProcessor

def test_vad_with_file(audio_file_path):
    """使用音频文件测试VAD功能"""
    print(f"正在加载音频文件: {audio_file_path}")
    
    # 读取音频文件
    try:
        speech, sample_rate = sf.read(audio_file_path)
        print(f"音频文件加载成功: {sample_rate}Hz, {len(speech)} samples")
    except Exception as e:
        print(f"加载音频文件失败: {e}")
        return
    
    # 初始化VAD处理器
    vad_processor = VADProcessor(chunk_size=200, sample_rate=sample_rate)
    
    # 处理音频流
    print("正在处理音频流...")
    speech_segments = vad_processor.process_audio_stream(speech)
    
    # 输出结果
    if speech_segments:
        print(f"检测到语音段: {len(speech_segments)} 个")
        for i, segment in enumerate(speech_segments):
            print(f"段 {i+1}: 开始={segment[0]}ms, 结束={segment[1]}ms")
    else:
        print("未检测到语音段")

def test_vad_with_model_example():
    """使用模型自带的示例音频测试VAD功能"""
    print("正在测试VAD模型自带的示例...")
    
    try:
        from funasr import AutoModel
        model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")
        
        # 获取模型路径
        model_path = model.model_path
        wav_file = f"{model_path}/example/vad_example.wav"
        
        if os.path.exists(wav_file):
            test_vad_with_file(wav_file)
        else:
            print(f"示例音频文件不存在: {wav_file}")
    except Exception as e:
        print(f"测试VAD模型示例时出错: {e}")

def test_process_audio_chunk():
    """测试 process_audio_chunk 函数"""
    print("正在测试 process_audio_chunk 函数...")
    
    sample_rate = 16000
    chunk_size_ms = 200
    chunk_size_samples = int(chunk_size_ms * sample_rate / 1000)
    
    # 初始化VAD处理器
    vad_processor = VADProcessor(chunk_size=chunk_size_ms, sample_rate=sample_rate)
    
    # 1. 测试静音音频块
    print("  测试静音块...")
    silent_chunk = np.zeros(chunk_size_samples, dtype=np.float32)
    segments = vad_processor.process_audio_chunk(silent_chunk)
    if not segments:
        print("静音块测试通过: 未检测到语音段")
    else:
        print(f"静音块测试失败: 检测到 {len(segments)} 个语音段")

    # 2. 测试真实语音块
    print("  测试真实语音块...")
    try:
        from funasr import AutoModel
        model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")
        model_path = model.model_path
        wav_file = f"{model_path}/example/vad_example.wav"
        
        if os.path.exists(wav_file):
            speech, sr = sf.read(wav_file)
            if sr != sample_rate:
                print(f"    警告: 示例音频采样率 ({sr}Hz) 与测试采样率 ({sample_rate}Hz) 不同。")
            
            chunk_stride = int(chunk_size_ms * sample_rate / 1000)
            total_chunk_num = (len(speech) + chunk_stride - 1) // chunk_stride
            
            found_speech = False
            vad_processor.reset_cache() # 重置缓存以进行独立测试
            
            for i in range(total_chunk_num):
                speech_chunk = speech[i * chunk_stride:(i + 1) * chunk_stride]
                if len(speech_chunk) == 0:
                    continue
                
                segments = vad_processor.process_audio_chunk(speech_chunk)
                if segments:
                    found_speech = True
                    # 提取时间信息用于显示
                    segment_info = [(start, end) for start, end, _ in segments]
                    print(f"在块 {i} 中检测到语音段: {segment_info}")
            
            if found_speech:
                print("真实语音块测试通过: 成功检测到语音段")
            else:
                print("真实语音块测试失败: 未检测到任何语音段")
        else:
            print(f"示例音频文件不存在，跳过真实语音块测试: {wav_file}")
    except Exception as e:
        print(f"测试真实语音块时出错: {e}")

if __name__ == "__main__":
    print("VAD功能测试")
    print("=" * 50)
    
    # 测试模型自带的示例
    test_vad_with_model_example()
    
    print("\n" + "=" * 50)
    
    # 测试 process_audio_chunk 函数
    # test_process_audio_chunk()
    
    print("\n" + "=" * 50)
    
    # 如果提供了音频文件路径作为参数，则测试该文件
    if len(sys.argv) > 1:
        audio_file_path = sys.argv[1]
        test_vad_with_file(audio_file_path)
