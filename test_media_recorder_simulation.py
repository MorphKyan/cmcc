#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟MediaRecorder的WebM数据块生成和测试
"""

import os
import tempfile
import av
import io


def simulate_media_recorder_chunks():
    """模拟MediaRecorder生成多个WebM数据块"""
    # 创建多个短的WebM文件来模拟MediaRecorder的行为
    chunks = []
    
    for i in range(3):
        temp_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        temp_file.close()
        # 创建0.5秒的音频片段
        os.system(f'ffmpeg -f lavfi -i sine=frequency={1000+i*200}:duration=0.5 -c:a libopus "{temp_file.name}" -y -loglevel quiet')
        
        with open(temp_file.name, 'rb') as f:
            chunk_data = f.read()
            chunks.append(chunk_data)
            print(f"块 {i+1}: {len(chunk_data)} 字节")
        
        os.unlink(temp_file.name)
    
    return chunks


def test_individual_chunks(chunks):
    """测试每个块是否能独立解码"""
    print("\n=== 测试独立解码 ===")
    for i, chunk in enumerate(chunks):
        try:
            with av.open(io.BytesIO(chunk), mode='r') as container:
                audio_stream = container.streams.audio[0]
                frame_count = 0
                for frame in container.decode(audio_stream):
                    frame_count += 1
                print(f"块 {i+1}: 解码成功，{frame_count} 帧")
        except Exception as e:
            print(f"块 {i+1}: 解码失败 - {e}")


def test_concatenated_chunks(chunks):
    """测试拼接所有块是否能解码"""
    print("\n=== 测试拼接解码 ===")
    concatenated = b''.join(chunks)
    try:
        with av.open(io.BytesIO(concatenated), mode='r') as container:
            audio_stream = container.streams.audio[0]
            frame_count = 0
            for frame in container.decode(audio_stream):
                frame_count += 1
            print(f"拼接块: 解码成功，{frame_count} 帧")
    except Exception as e:
        print(f"拼接块: 解码失败 - {e}")


if __name__ == '__main__':
    chunks = simulate_media_recorder_chunks()
    test_individual_chunks(chunks)
    test_concatenated_chunks(chunks)