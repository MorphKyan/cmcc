#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sherpa-ONNX VITS TTS 测试脚本
用于评估不同中文 VITS 模型的语音合成效果。

使用前请先下载模型：
  运行 tests/download_tts_models.py

用法：
  python tests/test_tts.py
"""

import os
import sys
import time

import sherpa_onnx
import soundfile as sf

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "tts_output")

# 测试文本：模拟智慧展厅的常见语音反馈
TEST_TEXTS = [
    "操作成功，正在为您执行。",
    "好的，已为您打开主屏幕。",
    "抱歉，未识别到有效指令，请重新尝试。",
    "正在为您播放智慧城市宣传片。",
    "音量已调高，当前音量百分之七十。",
    "欢迎来到中国移动智慧展厅。",
]


def test_model_melo_tts():
    """测试 vits-melo-tts-zh_en 模型（MeloTTS 转换版，中英文，1个说话人）"""
    model_dir = os.path.join(MODELS_DIR, "vits-melo-tts-zh_en")
    model_path = os.path.join(model_dir, "model.onnx")

    if not os.path.exists(model_path):
        print(f"[跳过] vits-melo-tts-zh_en 模型不存在: {model_path}")
        print(f"       请先运行: python tests/download_tts_models.py")
        return

    print("=" * 60)
    print("模型: vits-melo-tts-zh_en (MeloTTS 转换版)")
    print("=" * 60)

    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=model_path,
                lexicon=os.path.join(model_dir, "lexicon.txt"),
                tokens=os.path.join(model_dir, "tokens.txt"),
                dict_dir=os.path.join(model_dir, "dict"),
            ),
            num_threads=2,
        ),
        rule_fsts=",".join([
            os.path.join(model_dir, "date.fst"),
            os.path.join(model_dir, "number.fst"),
        ]),
    )

    tts = sherpa_onnx.OfflineTts(tts_config)
    output_subdir = os.path.join(OUTPUT_DIR, "melo_tts")
    os.makedirs(output_subdir, exist_ok=True)

    for i, text in enumerate(TEST_TEXTS):
        output_path = os.path.join(output_subdir, f"melo_{i + 1}.wav")
        start = time.perf_counter()
        audio = tts.generate(text, sid=0, speed=1.0)
        elapsed = time.perf_counter() - start
        # 计算音频时长
        duration = len(audio.samples) / audio.sample_rate
        rtf = elapsed / duration if duration > 0 else 0

        sf.write(output_path, audio.samples, audio.sample_rate)
        print(f"  [{i + 1}] \"{text}\"")
        print(f"      音频时长: {duration:.2f}s | 生成耗时: {elapsed:.3f}s | RTF: {rtf:.3f}")
        print(f"      保存到: {output_path}")

    print()


def test_model_zh_ll():
    """测试 sherpa-onnx-vits-zh-ll 模型（中文，5个说话人）"""
    model_dir = os.path.join(MODELS_DIR, "sherpa-onnx-vits-zh-ll")
    model_path = os.path.join(model_dir, "model.onnx")

    if not os.path.exists(model_path):
        print(f"[跳过] sherpa-onnx-vits-zh-ll 模型不存在: {model_path}")
        print(f"       请先运行: python tests/download_tts_models.py")
        return

    print("=" * 60)
    print("模型: sherpa-onnx-vits-zh-ll (中文，5个说话人)")
    print("=" * 60)

    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=model_path,
                lexicon=os.path.join(model_dir, "lexicon.txt"),
                tokens=os.path.join(model_dir, "tokens.txt"),
                dict_dir=os.path.join(model_dir, "dict"),
            ),
            num_threads=2,
        ),
        rule_fsts=",".join([
            os.path.join(model_dir, "number.fst"),
            os.path.join(model_dir, "phone.fst"),
        ]),
    )

    tts = sherpa_onnx.OfflineTts(tts_config)
    output_subdir = os.path.join(OUTPUT_DIR, "zh_ll")
    os.makedirs(output_subdir, exist_ok=True)

    # 测试不同的说话人 (sid 0~4)
    test_sids = [0, 1, 2]  # 只测试前3个说话人
    for sid in test_sids:
        print(f"\n  --- 说话人 {sid} ---")
        for i, text in enumerate(TEST_TEXTS):
            output_path = os.path.join(output_subdir, f"zh_ll_sid{sid}_{i + 1}.wav")
            start = time.perf_counter()
            audio = tts.generate(text, sid=sid, speed=1.0)
            elapsed = time.perf_counter() - start
            duration = len(audio.samples) / audio.sample_rate
            rtf = elapsed / duration if duration > 0 else 0

            sf.write(output_path, audio.samples, audio.sample_rate)
            print(f"  [{i + 1}] \"{text}\"")
            print(f"      音频时长: {duration:.2f}s | 生成耗时: {elapsed:.3f}s | RTF: {rtf:.3f}")
            print(f"      保存到: {output_path}")

    print()


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("  Sherpa-ONNX VITS TTS 语音效果测试")
    print("=" * 60)
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    test_model_melo_tts()
    test_model_zh_ll()

    print("=" * 60)
    print("测试完成！请到以下目录试听生成的音频：")
    print(f"  {OUTPUT_DIR}")
    print("=" * 60)
