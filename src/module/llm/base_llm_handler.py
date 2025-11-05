#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from abc import ABC, abstractmethod
from typing import Dict, Any

from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from src.config.config import LLMSettings
from src.module.data_loader import format_docs_for_prompt


class BaseLLMHandler(ABC):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化LLM处理器基类。

        Args:
            settings (LLMSettings): LLM参数
        """
        self.settings = settings
        self.screens_info = settings.SCREENS_INFO
        self.doors_info = settings.DOORS_INFO

        # 定义tools (shared between all LLM handlers)
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "play_video",
                    "description": "播放指定的视频文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "要播放的视频文件名"},
                            "device": {"type": "string", "description": "要在其上播放视频的屏幕名称"}
                        },
                        "required": ["target", "device"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "control_door",
                    "description": "控制门的开关",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target": {"type": "string", "description": "门的全称"},
                            "action": {"type": "string", "enum": ["open", "close"], "description": "要执行的操作：open（打开）或close（关闭）"}
                        },
                        "required": ["target", "action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "seek_video",
                    "description": "跳转到视频的指定时间点",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {"type": "string", "description": "要跳转进度的屏幕名称"},
                            "value": {"type": "integer", "description": "跳转到的秒数"}
                        },
                        "required": ["device", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "set_volume",
                    "description": "设置音量到指定的绝对值",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {"type": "string", "description": "要设置音量的屏幕名称"},
                            "value": {"type": "integer", "minimum": 0, "maximum": 100, "description": "音量值（0-100）"}
                        },
                        "required": ["device", "value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "adjust_volume",
                    "description": "相对提高或降低音量",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "device": {"type": "string", "description": "要调整音量的屏幕名称"},
                            "value": {"type": "string", "enum": ["up", "down"], "description": "音量调整方向：up（提高）或down（降低）"}
                        },
                        "required": ["device", "value"]
                    }
                }
            }
        ]

        # 使用ChatPromptTemplate构建提示词
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", settings.SYSTEM_PROMPT_TEMPLATE),
            ("user", "{USER_INPUT}")
        ])

        # 定义输出解析器
        self.output_parser = JsonOutputToolsParser()

        logger.info("LLM处理器基类初始化完成")

    @staticmethod
    def _map_tool_calls_to_response(tool_calls: list[Dict[str, Any]]) -> str:
        """
        将LangChain解析出的工具调用列表映射到项目所需的最终JSON格式。
        """
        if not tool_calls:
            return '[]'

        results = []
        for tool_call in tool_calls:
            function_name = tool_call['type']
            arguments = tool_call['args']
            result = {}

            if function_name == "play_video":
                result = {
                    "action": "play",
                    "target": arguments.get("target"),
                    "device": arguments.get("device"),
                    "value": None
                }
            elif function_name == "control_door":
                result = {
                    "action": arguments.get("action"),
                    "target": arguments.get("target"),
                    "device": None,
                    "value": None
                }
            elif function_name == "seek_video":
                result = {
                    "action": "seek",
                    "target": None,
                    "device": arguments.get("device"),
                    "value": arguments.get("value")
                }
            elif function_name == "set_volume":
                result = {
                    "action": "set_volume",
                    "target": None,
                    "device": arguments.get("device"),
                    "value": arguments.get("value")
                }
            elif function_name == "adjust_volume":
                result = {
                    "action": "adjust_volume",
                    "target": None,
                    "device": arguments.get("device"),
                    "value": arguments.get("value")
                }
            else:
                result = {
                    "action": "error",
                    "reason": "unknown_function",
                    "target": None,
                    "device": None,
                    "value": None
                }
            results.append(result)

        return json.dumps(results, ensure_ascii=False)

    @abstractmethod
    async def get_response(self, user_input: str, rag_docs: list[Document]) -> str:
        """
        结合RAG上下文，异步获取大模型的响应。

        Args:
            user_input (str): 用户的原始输入文本。
            rag_docs (list[Document]): RAG检索器返回的文档列表。

        Returns:
            str: 大模型返回的JSON格式指令或错误信息。
        """
        pass

    def _prepare_chain_input(self, user_input: str, rag_docs: list[Document]) -> Dict[str, Any]:
        """
        准备Prompt的输入变量，供子类使用。
        """
        rag_context = format_docs_for_prompt(rag_docs)
        screens_info_json = json.dumps(self.screens_info, ensure_ascii=False, indent=2)
        doors_info_json = json.dumps(self.doors_info, ensure_ascii=False, indent=2)

        return {
            "SCREENS_INFO": screens_info_json,
            "DOORS_INFO": doors_info_json,
            "rag_context": rag_context,
            "USER_INPUT": user_input
        }