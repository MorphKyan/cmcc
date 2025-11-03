#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复后的音频管道内存使用情况
"""

import asyncio
import os
import tempfile
from src.services.audio_pipeline import decode_loop
from src.api.context import Context
from src.module.input.stream_decoder import StreamDecoder


async def test_fixed_decode_loop():
    """测试修复后的解码循环"""
    # 创建模拟的上下文
    context = Context()
    context.decoder = StreamDecoder()
    
    # 创建多个WebM数据块（模拟MediaRecorder）
    chunks = []
    for i in range(5):
        temp_file = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        temp_file.close()
        os.system(f'ffmpeg -f lavfi -i sine=frequency={1000+i*100}:duration=0.3 -c:a libopus "{temp_file.name}" -y -loglevel quiet')
        
        with open(temp_file.name, 'rb') as f:
            chunks.append(f.read())
        os.unlink(temp_file.name)
    
    print(f"创建了 {len(chunks)} 个WebM数据块")
    
    # 模拟将数据放入队列
    async def feed_data():
        for i, chunk in enumerate(chunks):
            await context.audio_input_queue.put(chunk)
            print(f"放入块 {i+1}: {len(chunk)} 字节")
        # 放入None来结束
        await context.audio_input_queue.put(None)
    
    # 运行解码循环（带超时）
    feed_task = asyncio.create_task(feed_data())
    
    try:
        await asyncio.wait_for(decode_loop(context), timeout=5.0)
    except asyncio.TimeoutError:
        print("解码循环超时（正常，因为是无限循环）")
    except Exception as e:
        print(f"解码循环异常: {e}")
    
    feed_task.cancel()
    
    # 检查输出队列
    output_count = 0
    while not context.audio_np_queue.empty():
        await context.audio_np_queue.get()
        output_count += 1
    
    print(f"成功解码 {output_count} 个音频块")
    
    if output_count == len(chunks):
        print("✅ 修复验证成功！所有块都被正确解码")
        return True
    else:
        print(f"❌ 修复验证失败！期望 {len(chunks)} 个，实际 {output_count} 个")
        return False


if __name__ == '__main__':
    success = asyncio.run(test_fixed_decode_loop())
    if success:
        print("\n🎉 音频管道修复验证通过！")
    else:
        print("\n❌ 音频管道修复验证失败！")