#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证MediaRecorder WebM数据块的独立性
"""

import io
import av
import numpy as np


def test_webm_chunk_independence():
    """测试WebM数据块是否独立可解码"""
    # 创建一个测试WebM文件
    import os
    import tempfile
    
    test_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
    test_file.close()
    os.system(f'ffmpeg -f lavfi -i sine=frequency=1000:duration=2 -c:a libopus "{test_file.name}" -y -loglevel quiet')
    
    with open(test_file.name, 'rb') as f:
        full_data = f.read()
    
    print(f"完整WebM文件大小: {len(full_data)} 字节")
    
    # 尝试将文件分成两部分，看每部分是否能独立解码
    mid_point = len(full_data) // 2
    chunk1 = full_data[:mid_point]
    chunk2 = full_data[mid_point:]
    
    def try_decode(data, name):
        try:
            with av.open(io.BytesIO(data), mode='r') as container:
                audio_stream = container.streams.audio[0]
                frames = []
                for frame in container.decode(audio_stream):
                    frames.append(frame.to_ndarray())
                if frames:
                    print(f"{name}: 解码成功，{len(frames)} 帧")
                    return True
                else:
                    print(f"{name}: 解码失败（无帧）")
                    return False
        except Exception as e:
            print(f"{name}: 解码失败 - {e}")
            return False
    
    # 测试完整文件
    print("\n=== 测试完整文件 ===")
    try_decode(full_data, "完整文件")
    
    # 测试分块
    print("\n=== 测试分块 ===")
    try_decode(chunk1, "前半部分")
    try_decode(chunk2, "后半部分")
    
    os.unlink(test_file.name)


if __name__ == '__main__':
    test_webm_chunk_independence()