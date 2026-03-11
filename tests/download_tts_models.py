#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 Sherpa-ONNX VITS TTS 中文预训练模型到 models/ 目录。

下载的模型:
  1. vits-melo-tts-zh_en (163MB) - MeloTTS 转换版，中英文，1个说话人，音质最好
  2. sherpa-onnx-vits-zh-ll (115MB) - 中文，5个说话人

用法:
  python tests/download_tts_models.py
"""

import os
import sys
import tarfile
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

MODELS = [
    {
        "name": "vits-melo-tts-zh_en",
        "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2",
        "description": "MeloTTS 转换版 (中英文, 1 说话人, 163MB)",
    },
    {
        "name": "sherpa-onnx-vits-zh-ll",
        "url": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-vits-zh-ll.tar.bz2",
        "description": "中文多说话人 (5 说话人, 115MB)",
    },
]


def download_and_extract(url: str, name: str, description: str):
    """下载并解压模型"""
    target_dir = os.path.join(MODELS_DIR, name)
    if os.path.exists(target_dir) and os.path.exists(os.path.join(target_dir, "model.onnx")):
        print(f"  [已存在] {name} — 跳过下载")
        return

    archive_path = os.path.join(MODELS_DIR, f"{name}.tar.bz2")

    print(f"  [下载中] {description}")
    print(f"           URL: {url}")

    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\r           进度: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, archive_path, reporthook=report_progress)
        print()  # 换行
    except Exception as e:
        print(f"\n  [错误] 下载失败: {e}")
        if os.path.exists(archive_path):
            os.remove(archive_path)
        return

    print(f"  [解压中] {archive_path}")
    try:
        with tarfile.open(archive_path, "r:bz2") as tar:
            tar.extractall(path=MODELS_DIR)
        print(f"  [完成] 模型已解压到: {target_dir}")
    except Exception as e:
        print(f"  [错误] 解压失败: {e}")
    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)
            print(f"  [清理] 已删除压缩包")


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("=" * 60)
    print("  下载 Sherpa-ONNX VITS TTS 中文模型")
    print("=" * 60)
    print(f"目标目录: {MODELS_DIR}")
    print()

    for model in MODELS:
        print(f"--- {model['name']} ---")
        download_and_extract(model["url"], model["name"], model["description"])
        print()

    print("=" * 60)
    print("全部下载完成！现在可以运行测试：")
    print("  python tests/test_tts.py")
    print("=" * 60)
