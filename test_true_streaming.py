#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的流式WebM解码器测试
验证长时间音频流处理能力
"""

import os
import tempfile
import numpy as np
from true_streaming_webm_decoder import TrueStreamingWebMDecoder


def create_long_test_webm():
    """创建较长的测试WebM文件（10秒）"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
    temp_file.close()
    
    # 使用ffmpeg生成10秒的测试文件
    os.system(f'ffmpeg -f lavfi -i sine=frequency=1000:duration=10 -c:a libopus "{temp_file.name}" -y -loglevel quiet')
    
    return temp_file.name


def test_long_streaming_decoder():
    """测试长时间流式解码"""
    print("=== 创建长测试文件 ===")
    test_file = create_long_test_webm()
    
    if not os.path.exists(test_file):
        print("❌ 无法创建测试文件")
        return False
        
    print(f"测试文件: {test_file}")
    
    # 读取完整文件
    with open(test_file, 'rb') as f:
        full_data = f.read()
        
    print(f"文件大小: {len(full_data)} 字节")
    
    # 完整文件解码作为基准
    print("\n=== 基准测试：完整文件解码 ===")
    baseline_decoder = TrueStreamingWebMDecoder()
    baseline_decoder.feed_data(full_data)
    # 需要多次调用get_decoded_audio来获取所有数据
    baseline_chunks = []
    while True:
        chunk = baseline_decoder.get_decoded_audio(max_data_size=len(full_data))
        if chunk is None:
            break
        baseline_chunks.append(chunk)
    
    if baseline_chunks:
        if len(baseline_chunks) == 1:
            baseline_result = baseline_chunks[0]
        else:
            baseline_result = np.concatenate(baseline_chunks, axis=1)
        print(f"基准解码成功: {baseline_result.shape}")
        baseline_samples = baseline_result.size
    else:
        print("❌ 基准解码失败")
        os.unlink(test_file)
        return False
    
    # 流式解码测试
    print("\n=== 流式解码测试 ===")
    streaming_decoder = TrueStreamingWebMDecoder()
    chunk_size = 512  # 模拟小数据块传输
    streaming_chunks = []
    buffer_sizes = []
    
    for i in range(0, len(full_data), chunk_size):
        chunk = full_data[i:i+chunk_size]
        streaming_decoder.feed_data(chunk)
        
        # 每次处理小块数据
        decoded_chunk = streaming_decoder.get_decoded_audio(max_data_size=2048)
        if decoded_chunk is not None:
            streaming_chunks.append(decoded_chunk)
            print(f"  块 {i//chunk_size + 1}: 解码 {decoded_chunk.size} 样本")
        
        # 记录缓冲区大小
        if i % (chunk_size * 10) == 0:
            buffer_size = streaming_decoder.get_buffer_size()
            buffer_sizes.append(buffer_size)
            print(f"    缓冲区大小: {buffer_size} 字节")
    
    # 获取剩余数据
    while True:
        remaining_chunk = streaming_decoder.get_decoded_audio(max_data_size=8192)
        if remaining_chunk is None:
            break
        streaming_chunks.append(remaining_chunk)
        print(f"  剩余数据: 解码 {remaining_chunk.size} 样本")
    
    if streaming_chunks:
        if len(streaming_chunks) == 1:
            streaming_result = streaming_chunks[0]
        else:
            streaming_result = np.concatenate(streaming_chunks, axis=1)
        print(f"流式解码成功: {streaming_result.shape}")
        streaming_samples = streaming_result.size
    else:
        print("❌ 流式解码未产生输出")
        os.unlink(test_file)
        return False
    
    # 结果比较
    print(f"\n=== 结果比较 ===")
    print(f"基准样本数: {baseline_samples}")
    print(f"流式样本数: {streaming_samples}")
    print(f"差异: {abs(baseline_samples - streaming_samples)}")
    
    # 检查缓冲区增长情况
    print(f"\n=== 内存使用分析 ===")
    if buffer_sizes:
        print(f"最大缓冲区大小: {max(buffer_sizes)} 字节")
        print(f"最终缓冲区大小: {streaming_decoder.get_buffer_size()} 字节")
        # 真正的流式解码器应该保持缓冲区较小
        if max(buffer_sizes) < len(full_data) * 0.5:  # 缓冲区应该小于文件大小的一半
            print("✅ 内存使用良好：缓冲区得到有效控制")
        else:
            print("⚠️  内存使用警告：缓冲区可能过大")
    
    # 验证结果
    success = abs(baseline_samples - streaming_samples) <= 1000  # 允许少量差异
    if success:
        print("\n✅ 流式解码测试成功！")
    else:
        print("\n❌ 流式解码测试失败！")
    
    # 清理
    os.unlink(test_file)
    return success


def test_memory_efficiency():
    """专门测试内存效率"""
    print("\n=== 内存效率专项测试 ===")
    
    # 创建一个很长的测试文件（15秒）
    long_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
    long_file.close()
    os.system(f'ffmpeg -f lavfi -i sine=frequency=800:duration=15 -c:a libopus "{long_file.name}" -y -loglevel quiet')
    
    with open(long_file.name, 'rb') as f:
        long_data = f.read()
    
    print(f"长文件大小: {len(long_data)} 字节")
    
    decoder = TrueStreamingWebMDecoder()
    chunk_size = 256  # 更小的数据块
    max_buffer_size = 0
    
    for i in range(0, len(long_data), chunk_size):
        chunk = long_data[i:i+chunk_size]
        decoder.feed_data(chunk)
        
        # 处理数据
        _ = decoder.get_decoded_audio(max_data_size=1024)
        
        # 监控缓冲区大小
        current_buffer = decoder.get_buffer_size()
        max_buffer_size = max(max_buffer_size, current_buffer)
        
        if i % (chunk_size * 20) == 0:
            print(f"  处理 {i} 字节，缓冲区: {current_buffer} 字节")
    
    print(f"最大缓冲区大小: {max_buffer_size} 字节")
    print(f"文件总大小: {len(long_data)} 字节")
    print(f"缓冲区占比: {max_buffer_size / len(long_data) * 100:.1f}%")
    
    # 真正的流式解码器应该保持缓冲区很小
    if max_buffer_size < 10000:  # 小于10KB
        print("✅ 内存效率优秀！")
        result = True
    else:
        print("⚠️  内存效率需要优化")
        result = False
    
    os.unlink(long_file.name)
    return result


if __name__ == '__main__':
    success1 = test_long_streaming_decoder()
    success2 = test_memory_efficiency()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！真正的流式解码方案可行。")
    else:
        print("\n❌ 部分测试失败，请检查实现。")