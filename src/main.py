#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from app.voice_assistant import VoiceAssistant
from core.ark_llm_handler import LLMHandler as ArkLLMHandler
from core.ollama_llm_handler import OllamaLLMHandler
from config import ARK_API_KEY, ARK_BASE_URL, LLM_MODEL_NAME, SYSTEM_PROMPT_TEMPLATE

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
             "如果你的 'data/videos.csv' 文件有更新，请使用此选项。"
    )
    
    parser.add_argument(
        "--llm-provider",
        type=str,
        default="ollama",
        choices=["ark", "ollama"],
        help="选择大语言模型提供商。\n"
             "  'ark': 使用火山引擎方舟大模型。\n"
             "  'ollama': 使用本地部署的Ollama模型(默认)。"
    )
    
    args = parser.parse_args()
    
    try:
        # 根据provider选择并初始化LLM Handler
        if args.llm_provider == "ollama":
            llm_handler = OllamaLLMHandler(system_prompt_template=SYSTEM_PROMPT_TEMPLATE)
        else: # 默认为 "ark"
            llm_handler = ArkLLMHandler(
                ark_api_key=ARK_API_KEY,
                ark_base_url=ARK_BASE_URL,
                llm_model_name=LLM_MODEL_NAME,
                system_prompt_template=SYSTEM_PROMPT_TEMPLATE
            )

        # 创建识别器实例，并传入LLM Handler
        assistant = VoiceAssistant(
            llm_handler=llm_handler,
            device=args.device,
            force_rag_reload=args.force_rag_reload,
        )
        
        # 开始识别
        assistant.start()
        
    except Exception as e:
        print(f"\n程序启动失败: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
