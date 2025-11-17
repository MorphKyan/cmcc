#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable
from loguru import logger

from src.config.config import LLMSettings
from src.core.csv_loader import CSVLoader
from src.module.llm.tool.definitions import get_tools, ExhibitionCommand


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
        self._tool_map = {tool.name: tool for tool in self.tools}

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
        rag_context = self._get_prompt_from_documents(rag_docs)
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
                aliases_str = screen_info.get("aliases", "")
                description_str = screen_info.get("description", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                screens_info.append({
                    "name": screen_name,
                    "description": f"{description_str}，也称为{aliases}"
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
                aliases_str = door_info.get("aliases", "")
                description_str = door_info.get("description", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                doors_info.append({
                    "name": door_name,
                    "description": f"{description_str}，也称为{aliases}"
                })
        return doors_info

    def _format_response(self, response) -> str:
        """
        将结构化响应格式化为JSON字符串。

        Args:
            response: 结构化响应对象

        Returns:
            JSON格式的响应字符串
        """
        commands = []
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args")

            if tool_function := self._tool_map.get(tool_name):
                try:
                    # 预执行验证：在执行工具前验证参数
                    is_valid, error_message = self._validate_tool_args(tool_name, tool_args)
                    if not is_valid:
                        logger.warning("工具 '{name}' 参数验证失败: {error}", name=tool_name, error=error_message)
                        # 创建验证错误响应而不是执行无效工具
                        error_command = ExhibitionCommand(
                            action="error",
                            target=tool_args.get("target"),
                            device=tool_args.get("device"),
                            value=f"validation_failed: {error_message}"
                        )
                        commands.append(error_command.model_dump())
                        continue

                    # 直接调用工具函数
                    command_result: ExhibitionCommand = tool_function.invoke(tool_args)
                    commands.append(command_result.model_dump())
                except Exception as e:
                    logger.error("执行工具 '{name}' 时出错: {error}", name=tool_name, error=e)
                    # 创建执行错误响应
                    error_command = ExhibitionCommand(
                        action="error",
                        target=tool_args.get("target") if tool_args else None,
                        device=tool_args.get("device") if tool_args else None,
                        value=f"execution_failed: {str(e)}"
                    )
                    commands.append(error_command.model_dump())
            else:
                logger.warning("使用了未知的工具: {name}", name=tool_name)
                # 创建未知工具错误响应
                error_command = ExhibitionCommand(
                    action="error",
                    target=tool_args.get("target") if tool_args else None,
                    device=tool_args.get("device") if tool_args else None,
                    value=f"unknown_tool: {tool_name}"
                )
                commands.append(error_command.model_dump())

        return json.dumps(commands, ensure_ascii=False, indent=2)

    def _validate_play_video_args(self, target: str, device: str) -> tuple[bool, str | None]:
        if not self.csv_loader.video_exists(target):
            return False, f"Video '{target}' not found in videos.csv"

        if not self.csv_loader.screen_exists(device):
            return False, f"Screen '{device}' not found in screens.csv"

        return True, None

    def _validate_control_door_args(self, target: str, action: str) -> tuple[bool, str | None]:
        if not self.csv_loader.door_exists(target):
            return False, f"Door '{target}' not found in doors.csv"

        if action not in ["open", "close"]:
            return False, f"Invalid door action '{action}'. Must be 'open' or 'close'"

        return True, None

    def _validate_device_args(self, device: str, tool_name: str) -> tuple[bool, str | None]:
        if not self.csv_loader.screen_exists(device):
            return False, f"Screen '{device}' not found in screens.csv for {tool_name} tool"

        return True, None

    def _validate_tool_args(self, tool_name: str, tool_args: dict) -> tuple[bool, str | None]:
        try:
            if tool_name == "play_video":
                target = tool_args.get("target", "")
                device = tool_args.get("device", "")
                return self._validate_play_video_args(target, device)

            elif tool_name == "control_door":
                target = tool_args.get("target", "")
                action = tool_args.get("action", "")
                return self._validate_control_door_args(target, action)

            elif tool_name in ["seek_video", "set_volume", "adjust_volume"]:
                device = tool_args.get("device", "")
                return self._validate_device_args(device, tool_name)

            else:
                return True, None

        except Exception as e:
            logger.error(f"Error validating tool '{tool_name}' arguments: {e}")
            return False, f"Validation error: {str(e)}"

    def create_error_response(self, reason: str, message: str | None = None) -> str:
        """
        创建错误响应。

        Args:
            reason: 错误原因
            message: 可选错误消息

        Returns:
            JSON格式的错误响应字符串
        """
        error_command = ExhibitionCommand(
            action="error",
            target=None,
            device=None,
            value=reason
        )

        error_dict = error_command.model_dump()

        if message:
            error_dict["message"] = message

        return json.dumps([error_dict], ensure_ascii=False)

    @staticmethod
    def _get_prompt_from_documents(docs: list[Document]) -> str:
        """
        将检索到的Videos Document对象格式化为可以插入到Prompt中的字符串。

        Args:
            docs (list[Document]): 检索到的Document对象列表。

        Returns:
            str: 格式化后的知识库字符串，包含设备类型、名称、描述和文件名。
        """
        if not docs:
            return ""

        videos = []

        for doc in docs:
            meta = doc.metadata
            filename = meta.get("filename", "")
            description = meta.get("description", "")
            aliases = meta.get("aliases", "")
            video = {
                "name": filename,
                "description": f"{description}，也称为{aliases}",
            }
            videos.append(video)

        return json.dumps(videos, ensure_ascii=False, indent=2)
