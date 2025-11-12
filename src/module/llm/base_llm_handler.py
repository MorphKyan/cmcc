#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from src.config.config import LLMSettings
from src.core.csv_loader import CSVLoader
from src.core.validation_retry_service import ValidationRetryService
from src.module.data_loader import get_prompt_from_rag_documents
from src.module.llm.tool.registry import ToolRegistry


class BaseLLMHandler(ABC):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化LLM处理器基类。

        Args:
            settings (LLMSettings): LLM参数
        """
        self.settings = settings
        self.csv_loader = CSVLoader()
        self.tool_registry = ToolRegistry()
        self.validation_retry_service = ValidationRetryService(self.tool_registry.validator, settings)
        self.model_with_tools = None

        # Get tools from the centralized registry
        self.tools = self.tool_registry.tool_definitions

        # 使用ChatPromptTemplate构建提示词
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", settings.system_prompt_template),
            ("user", "{USER_INPUT}")
        ])

        # 定义输出解析器
        self.output_parser = JsonOutputToolsParser()

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

    @abstractmethod
    async def check_health(self) -> bool:
        """
        检查LLM服务的健康状态。

        Returns:
            bool: True if service is healthy, False otherwise
        """
        pass

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

    def get_retry_chain_components(self):
        """
        获取重试链所需的组件。

        Returns:
            tuple: (model_with_tools, output_parser, prompt_template)
        """
        return self.prompt_template, self.model_with_tools, self.output_parser

    @property
    def response_mapper(self):
        """
        Get the response mapper from the tool registry.

        This maintains backward compatibility with ValidationRetryService.
        """
        return self.tool_registry.mapper
