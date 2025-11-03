#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单流式解码器测试
"""

import os
import tempfile
import numpy as np
from simple_streaming_webm_decoder import SimpleStreamingWebMDecoder


def test_simple_streaming():
    """测试简单流式解码器"""
    # 创建测试文件
    test_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
    test_file.close()
    os.system(f'ffmpeg -f lavfi -i sine=frequency=1000:duration=5 -c:a libopus "{test_file.name}" -y -loglevel quiet')
    
    with open(test_file.name, 'rb') as f:
        full_data = f.read()
    
    print(f"测试文件大小: {len(full_data)} 字节")
    
    # 流式解码
    decoder = SimpleStreamingWebMDecoder()
    chunk_size = 512
    decoded_chunks = []
    
    for i in range(0, len(full_data), chunk_size):
        chunk = full_data[i:i+chunk_size]
        decoder.feed_data(chunk)
        
        decoded_chunk = decoder.get_decoded_audio()
        if decoded_chunk is not None:
            decoded_chunks.append(decoded_chunk)
            print(f"块 {i//chunk_size + 1}: 解码 {decoded_chunk.size} 样本")
    
    # 获取剩余数据
    while True:
        remaining = decoder.get_decoded_audio()
        if remaining is None:
            break
        decoded_chunks.append(remaining)
        print(f"剩余: 解码 {remaining.size} 样本")
    
    if decoded_chunks:
        if len(decoded_chunks) == 1:
            result = decoded_chunks[0]
        else:
            result = np.concatenate(decoded_chunks, axis=1)
        print(f"总解码样本: {result.size}")
        print(f"缓冲区大小: {decoder.get_buffer_size()}")
        success = True
    else:
        print("解码失败")
        success = False
    
    os.unlink(test_file.name)
    return success


if __name__ == '__main__':
    success = test_simple_streaming()
    if success:
        print("✅ 简单流式解码器测试通过")
    else:
        print("❌ 简单流式解码器测试失败")