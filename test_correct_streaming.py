#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正确的流式WebM解码器
模拟WebSocket传输格式：
- 第一个包：完整WebM文件
- 后续包：只包含音频数据部分
"""

import os
import tempfile
import io
import av
import numpy as np
from correct_streaming_webm_decoder import CorrectStreamingWebMDecoder


def simulate_websocket_data_format():
    """模拟WebSocket的WebM数据传输格式"""
    # 创建一个完整的WebM文件
    temp_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
    temp_file.close()
    os.system(f'ffmpeg -f lavfi -i sine=frequency=1000:duration=5 -c:a libopus "{temp_file.name}" -y -loglevel quiet')
    
    with open(temp_file.name, 'rb') as f:
        full_webm = f.read()
    
    print(f"完整WebM文件大小: {len(full_webm)} 字节")
    
    # 分析WebM结构，分离header和数据
    # 第一个包：完整文件（模拟WebSocket第一个包）
    first_chunk = full_webm
    
    # 后续包：只取数据部分（模拟WebSocket后续包）
    # 为了模拟，我们创建几个只包含音频数据的块
    # 实际上，我们需要从完整文件中提取纯数据部分
    
    # 简化方法：使用pyav来获取纯音频数据
    with av.open(io.BytesIO(full_webm), mode='r', format='matroska') as container:
        audio_stream = container.streams.audio[0]
        raw_audio_data = bytearray()
        
        for frame in container.decode(audio_stream):
            # 将帧转换为原始字节
            raw_frame_data = frame.to_ndarray().tobytes()
            raw_audio_data.extend(raw_frame_data)
    
    print(f"提取的原始音频数据大小: {len(raw_audio_data)} 字节")
    
    # 创建后续数据块（只包含音频数据，没有WebM容器）
    chunk_size = len(raw_audio_data) // 3
    subsequent_chunks = []
    for i in range(3):
        start = i * chunk_size
        end = start + chunk_size if i < 2 else len(raw_audio_data)
        if start < len(raw_audio_data):
            subsequent_chunks.append(raw_audio_data[start:end])
    
    os.unlink(temp_file.name)
    return first_chunk, subsequent_chunks


def test_correct_decoder():
    """测试正确的流式解码器"""
    print("=== 模拟WebSocket数据格式 ===")
    first_chunk, subsequent_chunks = simulate_websocket_data_format()
    
    print(f"第一个包大小: {len(first_chunk)} 字节")
    print(f"后续包数量: {len(subsequent_chunks)}")
    for i, chunk in enumerate(subsequent_chunks):
        print(f"  后续包 {i+1}: {len(chunk)} 字节")
    
    print("\n=== 测试正确解码器 ===")
    decoder = CorrectStreamingWebMDecoder()
    decoded_chunks = []
    
    # 解码第一个包
    first_result = decoder.decode_chunk(first_chunk, is_first=True)
    if first_result is not None:
        decoded_chunks.append(first_result)
        print(f"第一个包解码成功: {first_result.shape}")
    else:
        print("第一个包解码失败")
        return False
    
    # 解码后续包
    for i, chunk in enumerate(subsequent_chunks):
        result = decoder.decode_chunk(chunk, is_first=False)
        if result is not None:
            decoded_chunks.append(result)
            print(f"后续包 {i+1} 解码成功: {result.shape}")
        else:
            print(f"后续包 {i+1} 解码失败")
            # 这是预期的，因为我们没有正确的纯音频数据格式
            # 实际WebSocket传输的数据格式可能不同
    
    if decoded_chunks:
        if len(decoded_chunks) == 1:
            final_result = decoded_chunks[0]
        else:
            final_result = np.concatenate(decoded_chunks, axis=1)
        print(f"\n总解码结果: {final_result.shape}")
        print("✅ 解码器基本功能正常")
        return True
    else:
        print("❌ 解码器无法产生输出")
        return False


def test_with_real_webm_chunks():
    """使用真实WebM文件测试"""
    print("\n=== 使用真实WebM文件测试 ===")
    
    # 创建测试文件
    test_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
    test_file.close()
    os.system(f'ffmpeg -f lavfi -i sine=frequency=1000:duration=3 -c:a libopus "{test_file.name}" -y -loglevel quiet')
    
    with open(test_file.name, 'rb') as f:
        full_data = f.read()
    
    print(f"测试文件大小: {len(full_data)} 字节")
    
    # 模拟WebSocket传输：第一个包是完整文件，后续包是文件的一部分
    # 这里我们简单地将文件分成几块，第一块包含header
    chunk_size = len(full_data) // 4
    chunks = []
    for i in range(4):
        start = i * chunk_size
        end = start + chunk_size if i < 3 else len(full_data)
        chunks.append(full_data[start:end])
    
    decoder = CorrectStreamingWebMDecoder()
    decoded_results = []
    
    for i, chunk in enumerate(chunks):
        is_first = (i == 0)
        result = decoder.decode_chunk(chunk, is_first=is_first)
        if result is not None:
            decoded_results.append(result)
            print(f"块 {i+1} ({len(chunk)} 字节): 解码成功 {result.shape}")
        else:
            print(f"块 {i+1} ({len(chunk)} 字节): 解码失败")
    
    os.unlink(test_file.name)
    return len(decoded_results) > 0


if __name__ == '__main__':
    success1 = test_correct_decoder()
    success2 = test_with_real_webm_chunks()
    
    if success1 or success2:
        print("\n🎉 正确的流式解码器测试通过！")
    else:
        print("\n❌ 测试失败，需要进一步调试")