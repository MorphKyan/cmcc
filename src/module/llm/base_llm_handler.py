#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from langchain.agents.structured_output import ToolStrategy
from loguru import logger

from src.config.config import LLMSettings
from src.core.csv_loader import CSVLoader
from src.module.rag.data_loader import get_prompt_from_rag_documents
from src.module.llm.tool.definitions import get_tools, get_exhibition_command_schema


class BaseLLMHandler(ABC):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化LLM处理器基类。

        Args:
            settings (LLMSettings): LLM参数
        """
        self.settings = settings
        self.csv_loader = CSVLoader()
        self.model_with_tools = None
        self.chain: RunnableSerializable[dict, Any] | None = None

        # Get modern tools and structured output schema
        self.tools = get_tools()
        self.exhibition_command_schema = get_exhibition_command_schema()

        # Create tool strategy for structured output
        self.tool_strategy = ToolStrategy(self.exhibition_command_schema)

        # 使用ChatPromptTemplate构建提示词
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", settings.system_prompt_template),
            ("user", "{USER_INPUT}")
        ])

        logger.info("LLM处理器基类初始化完成")

    def get_network_retry_config(self) -> dict:
        """
        获取网络重试配置。

        Returns:
            dict: 包含重试配置的字典
        """
        return {
            'max_retries': getattr(self.settings, 'max_network_retries', 3),
            'base_delay': getattr(self.settings, 'base_retry_delay', 1.0),
            'max_delay': getattr(self.settings, 'max_retry_delay', 10.0)
        }

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

    async def check_health(self) -> bool:
        """
        检查服务的健康状态。
        通过发送一个简单的健康检查请求来验证服务是否可用。
        """
        try:
            # 确保已初始化
            if self.chain is None:
                await self.initialize()

            # 使用简单的健康检查提示
            health_check_input = {
                "SCREENS_INFO": json.dumps(self.get_screens_info_for_prompt(), ensure_ascii=False, indent=2),
                "DOORS_INFO": json.dumps(self.get_doors_info_for_prompt(), ensure_ascii=False, indent=2),
                "rag_context": "",
                "USER_INPUT": "健康检查"
            }

            # 使用较短的超时进行健康检查
            import asyncio
            await asyncio.wait_for(self.chain.ainvoke(health_check_input), timeout=5.0)

            return True
        except Exception as e:
            logger.warning(f"LLM健康检查失败: {e}")
            return False

    async def initialize(self) -> None:
        """
        Optional async initialization method for LLM handlers.
        Subclasses can override this method to perform async setup operations
        like model loading, client initialization, or connection establishment.

        This method is called after __init__ during application startup.
        """
        pass

    def _prepare_chain_input(self, user_input: str, rag_docs: list[Document]) -> dict[str, Any]:
        """
        准备Prompt的输入变量，供子类使用。
        """
        rag_context = get_prompt_from_rag_documents(rag_docs)
        screens_info_json = json.dumps(self.get_screens_info_for_prompt(), ensure_ascii=False, indent=2)
        doors_info_json = json.dumps(self.get_doors_info_for_prompt(), ensure_ascii=False, indent=2)

        return {
            "SCREENS_INFO": screens_info_json,
            "DOORS_INFO": doors_info_json,
            "rag_context": rag_context,
            "USER_INPUT": user_input
        }

    def get_screens_info_for_prompt(self) -> list[dict[str, Any]]:
        """
        获取用于Prompt的屏幕信息列表
        """
        screens_info = []
        all_screens = self.csv_loader.get_all_screens()
        for screen_name in all_screens:
            screen_info = self.csv_loader.get_screen_info(screen_name)
            if screen_info:
                # Parse aliases from the stored string
                aliases_str = screen_info.get("aliases", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                screens_info.append({
                    "name": screen_name,
                    "aliases": aliases
                })
        return screens_info

    def get_doors_info_for_prompt(self) -> list[dict[str, Any]]:
        """
        获取用于Prompt的门信息列表
        """
        doors_info = []
        all_doors = self.csv_loader.get_all_doors()
        for door_name in all_doors:
            door_info = self.csv_loader.get_door_info(door_name)
            if door_info:
                # Parse aliases from the stored string
                aliases_str = door_info.get("aliases", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                doors_info.append({
                    "name": door_name,
                    "aliases": aliases
                })
        return doors_info

    def _format_structured_response(self, structured_response) -> str:
        """
        将结构化响应格式化为JSON字符串。

        Args:
            structured_response: 结构化响应对象

        Returns:
            JSON格式的响应字符串
        """
        if isinstance(structured_response, list):
            # Handle multiple commands
            commands = []
            for response in structured_response:
                commands.append(response.model_dump())
            return json.dumps(commands, ensure_ascii=False)
        else:
            # Handle single command
            command = structured_response.model_dump()
            return json.dumps([command], ensure_ascii=False)

    def create_error_response(self, reason: str, message: str | None = None, details: list[str] | None = None) -> str:
        """
        创建错误响应。

        Args:
            reason: 错误原因
            message: 可选错误消息
            details: 可选详细信息列表

        Returns:
            JSON格式的错误响应字符串
        """
        error_command = self.exhibition_command_schema(
            action="error",
            target=None,
            device=None,
            value=reason
        )

        error_dict = error_command.model_dump()

        if message:
            error_dict["message"] = message
        if details:
            error_dict["details"] = details

        return json.dumps([error_dict], ensure_ascii=False)