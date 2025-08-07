#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import os

# 将项目根目录添加到Python路径中，以便可以正确导入模块
# 这使得我们可以从任何地方运行 `python main.py`
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cmcc_assistant.speech_recognizer import RealTimeSpeechRecognizer

def main():
    """
    主函数，解析命令行参数并启动语音识别服务。
    """
    parser = argparse.ArgumentParser(
        description="中国移动智慧展厅 - 实时语音控制中心",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        choices=["auto", "cpu", "cuda:0"],
        help="选择用于推理的设备。\n"
             "  'auto': 自动检测CUDA，如果可用则使用GPU，否则使用CPU (默认)。\n"
             "  'cpu': 强制使用CPU。\n"
             "  'cuda:0': 强制使用第一个GPU设备。"
    )
    
    parser.add_argument(
        "--force-rag-reload",
        action="store_true",
        help="强制重新加载数据源并重建向量数据库。\n"
             "如果你的 'data/data.xlsx' 文件有更新，请使用此选项。"
    )
    
    args = parser.parse_args()
    
    try:
        # 创建识别器实例
        recognizer = RealTimeSpeechRecognizer(
            device=args.device,
            force_rag_reload=args.force_rag_reload
        )
        
        # 开始识别
        recognizer.start()
        
    except Exception as e:
        print(f"\n[严重错误] 程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
