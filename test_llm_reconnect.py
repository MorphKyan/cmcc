#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试LLM处理器的重连机制
"""

import asyncio
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.config import get_settings
from src.module.llm.ark_llm_handler import ArkLLMHandler
from src.module.llm.ollama_llm_handler import OllamaLLMHandler
from src.module.llm.modelscope_llm_handler import ModelScopeLLMHandler
from langchain_core.documents import Document


async def test_ark_handler():
    """测试ArkLLMHandler的重连机制"""
    print("=== 测试 ArkLLMHandler ===")
    settings = get_settings()

    try:
        handler = ArkLLMHandler(settings.llm, settings.volcengine)

        # 测试健康检查
        print("健康检查:", await handler.check_health())

        # 测试正常响应
        docs = [Document(page_content="测试文档")]
        response = await handler.get_response("播放5G的视频", docs)
        print("正常响应:", response[:100] + "..." if len(response) > 100 else response)

    except Exception as e:
        print(f"Ark测试失败: {e}")


async def test_ollama_handler():
    """测试OllamaLLMHandler的重连机制"""
    print("\n=== 测试 OllamaLLMHandler ===")
    settings = get_settings()

    try:
        handler = OllamaLLMHandler(settings.llm)

        # 测试健康检查
        print("健康检查:", await handler.check_health())

        # 测试正常响应
        docs = [Document(page_content="测试文档")]
        response = await handler.get_response("播放5G的视频", docs)
        print("正常响应:", response[:100] + "..." if len(response) > 100 else response)

    except Exception as e:
        print(f"Ollama测试失败: {e}")


async def test_modelscope_handler():
    """测试ModelScopeLLMHandler的重连机制"""
    print("\n=== 测试 ModelScopeLLMHandler ===")
    settings = get_settings()

    try:
        handler = ModelScopeLLMHandler(settings.llm)

        # 测试健康检查
        print("健康检查:", await handler.check_health())

        # 测试正常响应
        docs = [Document(page_content="测试文档")]
        response = await handler.get_response("播放5G的视频", docs)
        print("正常响应:", response[:100] + "..." if len(response) > 100 else response)

    except Exception as e:
        print(f"ModelScope测试失败: {e}")


async def main():
    """主测试函数"""
    print("LLM处理器重连机制测试")
    print("=" * 50)

    # 测试所有处理器
    await test_ark_handler()
    await test_ollama_handler()
    await test_modelscope_handler()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n注意：")
    print("1. 如果Ollama服务未运行，Ollama测试会失败")
    print("2. 如果API密钥无效，Ark和ModelScope测试会失败")
    print("3. 健康检查失败表示服务不可用")
    print("4. 正常响应应该包含JSON格式的指令")


if __name__ == "__main__":
    asyncio.run(main())