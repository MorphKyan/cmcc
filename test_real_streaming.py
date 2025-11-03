#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的流式WebM解码器实际测试
使用真实的WebM文件验证解码器功能
"""

import os
import numpy as np
from streaming_webm_decoder import StreamingWebMDecoder


def test_streaming_decoder_with_real_file():
    """使用真实WebM文件测试流式解码器"""
    test_file = "test_audio.webm"
    
    if not os.path.exists(test_file):
        print(f"测试文件 {test_file} 不存在")
        return False
        
    print(f"开始测试流式解码器 - 文件: {test_file}")
    
    # 读取完整文件
    with open(test_file, 'rb') as f:
        full_data = f.read()
        
    print(f"文件大小: {len(full_data)} 字节")
    
    # 测试1: 一次性解码完整文件
    print("\n=== 测试1: 完整文件解码 ===")
    decoder_full = StreamingWebMDecoder()
    decoder_full.feed_data(full_data)
    full_result = decoder_full.get_decoded_audio()
    
    if full_result is not None:
        print(f"完整解码成功: 形状={full_result.shape}, 类型={full_result.dtype}")
        print(f"总样本数: {full_result.size}")
    else:
        print("完整解码失败")
        return False
        
    # 测试2: 流式解码（分块处理）
    print("\n=== 测试2: 流式分块解码 ===")
    decoder_stream = StreamingWebMDecoder()
    chunk_size = 1024  # 模拟网络传输的小数据块
    total_decoded_samples = 0
    decoded_chunks = []
    
    for i in range(0, len(full_data), chunk_size):
        chunk = full_data[i:i+chunk_size]
        decoder_stream.feed_data(chunk)
        
        # 尝试解码当前可用的数据
        decoded_audio = decoder_stream.get_decoded_audio()
        if decoded_audio is not None:
            decoded_chunks.append(decoded_audio)
            total_decoded_samples += decoded_audio.size
            print(f"  块 {i//chunk_size + 1}: 解码 {decoded_audio.size} 样本")
    
    if decoded_chunks:
        # 合并所有解码的块
        if len(decoded_chunks) == 1:
            stream_result = decoded_chunks[0]
        else:
            stream_result = np.concatenate(decoded_chunks, axis=1)
            
        print(f"流式解码成功: 形状={stream_result.shape}, 总样本数={stream_result.size}")
        
        # 比较两种解码结果
        print(f"\n=== 结果比较 ===")
        print(f"完整解码样本数: {full_result.size}")
        print(f"流式解码样本数: {stream_result.size}")
        
        if abs(full_result.size - stream_result.size) <= 1000:  # 允许少量差异
            print("✅ 测试成功: 流式解码结果与完整解码基本一致")
            return True
        else:
            print("❌ 测试失败: 解码结果差异过大")
            return False
    else:
        print("流式解码未产生任何输出")
        return False


def test_memory_usage():
    """测试内存使用情况"""
    print("\n=== 测试3: 内存使用测试 ===")
    test_file = "test_audio.webm"
    
    with open(test_file, 'rb') as f:
        full_data = f.read()
        
    decoder = StreamingWebMDecoder()
    chunk_size = 512
    
    # 模拟长时间运行
    for i in range(0, len(full_data), chunk_size):
        chunk = full_data[i:i+chunk_size]
        decoder.feed_data(chunk)
        buffer_size = decoder.get_buffer_size()
        
        if i % (chunk_size * 10) == 0:  # 每10块打印一次
            print(f"  处理 {i} 字节后，缓冲区大小: {buffer_size} 字节")
    
    print(f"最终缓冲区大小: {decoder.get_buffer_size()} 字节")
    print("✅ 内存使用测试完成")


if __name__ == '__main__':
    success = test_streaming_decoder_with_real_file()
    test_memory_usage()
    
    if success:
        print("\n🎉 所有测试通过！流式解码方案可行。")
    else:
        print("\n❌ 测试失败，请检查实现。")