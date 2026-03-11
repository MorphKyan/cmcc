#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge-TTS 测试脚本
用于评估微软 Edge 云端 TTS 的语音合成效果。
特点：音色最自然（拟真度高），但需要连接外网，有一定网络延迟。

依赖:
  pip install edge-tts

用法：
  python tests/test_edge_tts.py
"""

import asyncio
import os
import time

import edge_tts

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "tts_output", "edge_tts")

# 测试文本：模拟智慧展厅的常见语音反馈
TEST_TEXTS = [
    "操作成功，正在为您执行。",
    "好的，已为您打开主屏幕。",
    "抱歉，未识别到有效指令，请重新尝试。",
    "正在为您播放智慧城市宣传片。",
    "音量已调高，当前音量百分之七十。",
    "欢迎来到中国移动智慧展厅。",
]

# Edge-TTS 的中文声线推荐 (Xiaoxiao 是最经典的甜美女声, Yunxi 是清爽男声)
VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-YunxiNeural"
]

async def generate_audio(text: str, voice: str, output_path: str):
    start = time.perf_counter()
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    elapsed = time.perf_counter() - start
    
    # 仅提供生成耗时，EdgeTTS不直接提供采样率，因此跳过时长/RTF计算
    print(f"      网络+生成耗时: {elapsed:.3f}s")
    print(f"      保存到: {output_path}")

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("  Edge-TTS (微软云端) 语音效果测试")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    for voice in VOICES:
        print(f"--- 说话人 {voice} ---")
        for i, text in enumerate(TEST_TEXTS):
            output_path = os.path.join(OUTPUT_DIR, f"{voice}_{i + 1}.mp3")
            print(f"  [{i + 1}] \"{text}\"")
            await generate_audio(text, voice, output_path)
        print()

    print("=" * 60)
    print("测试完成！请到以下目录试听生成的音频：")
    print(f"  {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
