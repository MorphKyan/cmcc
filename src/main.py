#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from component.speech_recognizer import RealTimeSpeechRecognizer
from component.ark_llm_handler import LLMHandler as ArkLLMHandler
from component.ollama_llm_handler import OllamaLLMHandler

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
             "如果你的 'data/screens.csv', 'data/doors.csv', 或 'data/videos.csv' 文件有更新，请使用此选项。"
    )
    
    parser.add_argument(
        "--record-seconds",
        type=int,
        default=5,
        help="每次识别处理的录音时长（秒）。默认为 5 秒。"
    )

    parser.add_argument(
        "--llm-provider",
        type=str,
        default="ark",
        choices=["ark", "ollama"],
        help="选择大语言模型提供商。\n"
             "  'ark': 使用火山引擎方舟大模型 (默认)。\n"
             "  'ollama': 使用本地部署的Ollama模型。"
    )
    
    args = parser.parse_args()
    
    try:
        # 根据provider选择并初始化LLM Handler
        if args.llm_provider == "ollama":
            llm_handler = OllamaLLMHandler()
        else: # 默认为 "ark"
            llm_handler = ArkLLMHandler()

        # 创建识别器实例，并传入LLM Handler
        recognizer = RealTimeSpeechRecognizer(
            llm_handler=llm_handler,
            device=args.device,
            force_rag_reload=args.force_rag_reload,
            record_seconds=args.record_seconds
        )
        
        # 开始识别
        recognizer.start()
        
    except Exception as e:
        print(f"\n[严重错误] 程序启动失败: {e}")
        # 在异常情况下，确保 sys 模块可用
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
