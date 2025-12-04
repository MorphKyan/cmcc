#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSerializable
from langchain_core.messages import ToolMessage, AIMessage, trim_messages
from loguru import logger

from src.config.config import LLMSettings
from src.core import dependencies
from src.module.llm.tool.definitions import get_tools, ExhibitionCommand
from src.module.llm.tool.validator import ToolValidator
from src.module.llm.helper import DocumentFormatter


class BaseLLMHandler(ABC):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化LLM处理器基类。

        Args:
            settings (LLMSettings): LLM参数
        """
        self.settings = settings
        self.model_with_tools = None
        self.chain: RunnableSerializable[dict, Any] | None = None

        self.tools = get_tools()
        self._tool_map = {tool.name: tool for tool in self.tools}

        # 使用ChatPromptTemplate构建提示词
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", settings.system_prompt_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{USER_INPUT}")
        ])

        # 创建消息修剪器 (Trimmer)
        # strategy="last": 保留最后的消息
        # max_tokens=5: 保留5条消息 (token_counter=len 表示按消息数量计数)
        # include_system=False: 不修剪系统消息 (保持系统提示词静态)
        # start_on="human": 确保保留的消息从用户消息开始
        self.trimmer = trim_messages(
            strategy="last",
            max_tokens=5,
            token_counter=len,
            include_system=False,
            allow_partial=False,
            start_on="human"
        )

        logger.info("LLM处理器基类初始化完成")

    @abstractmethod
    async def initialize(self) -> None:
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
                "DEVICES_INFO": "",
                "DOORS_INFO": "",
                "AREAS_INFO": "",
                "VIDEOS_INFO": "",
                "USER_INPUT": "健康检查"
            }

            # 使用较短的超时进行健康检查
            import asyncio
            await asyncio.wait_for(self.chain.ainvoke(health_check_input), timeout=5.0)

            return True
        except Exception as e:
            logger.warning(f"LLM健康检查失败: {e}")
            return False

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
    async def get_response(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> str:
        """
        结合RAG上下文，异步获取大模型的响应。
        
        Args:
            user_input: 用户输入
            rag_docs: 按类型分类的RAG文档字典 {"door": [...], "video": [...], "device": [...]}
            user_location: 用户当前位置
            chat_history: 聊天历史
        """
        pass

    async def get_response_with_retries(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> str:
        """
        带重试机制的响应获取方法。
        使用LangChain的bind_tools和自定义循环来处理工具调用和错误恢复。
        
        Args:
            user_input: 用户输入
            rag_docs: 按类型分类的RAG文档字典 {"door": [...], "video": [...], "device": [...]}
            user_location: 用户当前位置
            chat_history: 聊天历史
        """
        # 1. 准备输入
        chain_input = self._prepare_chain_input(user_input, rag_docs, user_location, chat_history)
        
        # 2. 绑定工具到模型
        if not self.model_with_tools:
             raise ValueError("Model with tools not initialized. Subclasses must set self.model_with_tools.")

        # 构建运行链：Prompt -> Trimmer -> ModelWithTools
        runnable = self.prompt_template | self.trimmer | self.model_with_tools
        
        messages = [] # 这里的messages主要用于在循环中累积工具交互，实际prompt template会处理chat_history
        
        # 初始调用
        try:
            ai_msg = await runnable.ainvoke(chain_input)
        except Exception as e:
            logger.error(f"Initial LLM call failed: {e}")
            return self.create_error_response("llm_error", str(e))

        messages.append(ai_msg)
        
        # 3. 进入重试/执行循环
        max_retries = getattr(self.settings, 'max_validation_retries', 3)
        
        for attempt in range(max_retries):
            if not ai_msg.tool_calls:
                # 没有工具调用，直接结束（可能是闲聊或无法处理）
                break
                
            # 执行工具
            tool_outputs = []
            has_error = False
            
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                tool_function = self._tool_map.get(tool_name)
                if not tool_function:
                    # 未知工具
                    error_msg = f"Error: Unknown tool '{tool_name}'"
                    tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                    has_error = True
                    continue
                    
                try:
                    # Semantic Validation
                    is_valid, error_message = ToolValidator.get_instance().validate_tool_args(tool_name, tool_args)
                    if not is_valid:
                        raise ValueError(f"Validation failed: {error_message}")

                    # Execute tool
                    result = tool_function.invoke(tool_args)
                    
                    if isinstance(result, ExhibitionCommand) and result.action == "error":
                         tool_outputs.append(ToolMessage(content=f"Error: {result.value}", tool_call_id=tool_call_id))
                         has_error = True
                    else:
                        tool_outputs.append(ToolMessage(content=f"Success: {result}", tool_call_id=tool_call_id))
                        
                except Exception as e:
                    # Catch execution/validation errors
                    error_msg = f"Error executing {tool_name}: {str(e)}. Please correct the arguments."
                    tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                    has_error = True
            
            if not has_error:
                # 所有工具执行成功，返回当前的 ai_msg (包含正确的 tool_calls)
                return self._format_response(ai_msg)
                
            # 如果有错误，我们需要把 tool_outputs 反馈给模型，让其修正
            # 更新 chain_input 中的 chat_history 或者 messages            
            # 将 ai_msg 和 tool_outputs 追加到 messages
            # 然后再次调用模型

            current_history = chain_input.get("chat_history", [])
            current_history.append(ai_msg)
            current_history.extend(tool_outputs)
            
            chain_input["chat_history"] = current_history
            
            logger.info(f"Retry attempt {attempt + 1}/{max_retries} due to tool errors.")
            
            try:
                ai_msg = await runnable.ainvoke(chain_input)
                messages.append(ai_msg)
            except Exception as e:
                logger.error(f"LLM retry call failed: {e}")
                return self.create_error_response("llm_retry_error", str(e))

        # 循环结束（达到最大重试次数或最后一次仍有错）        
        return self._format_response(ai_msg)

    def _prepare_chain_input(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> dict[str, Any]:
        """
        准备Prompt的输入变量，供子类使用。
        
        Args:
            user_input: 用户输入
            rag_docs: 按类型分类的RAG文档字典 {"door": [...], "video": [...], "device": [...]}
            user_location: 用户当前位置
            chat_history: 聊天历史
        """
        # 从分类文档字典中提取各类型的文档
        video_docs = rag_docs.get("video", [])
        door_docs = rag_docs.get("door", [])
        device_docs = rag_docs.get("device", [])
        
        # 格式化各类型信息
        videos_info = DocumentFormatter.get_prompt_from_documents(self, video_docs)
        doors_info = DocumentFormatter.get_prompt_from_documents(self, door_docs)
        devices_info = DocumentFormatter.get_prompt_from_documents(self, device_docs)
        areas_info_json = json.dumps(self.get_areas_info_for_prompt(), ensure_ascii=False, indent=2)

        return {
            "DEVICES_INFO": devices_info,
            "DOORS_INFO": doors_info,
            "AREAS_INFO": areas_info_json,
            "VIDEOS_INFO": videos_info,
            "USER_INPUT": user_input,
            "USER_LOCATION": user_location,
            "chat_history": chat_history
        }

    def _format_response(self, response) -> str:
        """
        将结构化响应格式化为JSON字符串。
        
        Args:
            response: 结构化响应对象
            
        Returns:
            JSON格式的响应字符串
        """
        if isinstance(response, AIMessage) and response.tool_calls:
            commands = []
            for tool_call in response.tool_calls:
                # 这里的tool_call已经是执行后的结果或者是模型生成的调用意图
                # 在新的流程中，我们实际上是在get_response_with_retries中处理执行
                # 这里主要用于最后格式化给前端
                
                # 从tool_call中提取信息
                cmd = ExhibitionCommand(
                    action=tool_call["name"], # 假设工具名即动作名，或者需要映射
                    target=tool_call["args"].get("target"),
                    device=tool_call["args"].get("device"),
                    value=tool_call["args"].get("value")
                )
                commands.append(cmd.model_dump())
            return json.dumps(commands, ensure_ascii=False, indent=2)
            
        return json.dumps([], ensure_ascii=False)

    @property
    def data_service(self):
        if dependencies.data_service is None:
            raise RuntimeError("DataService not initialized")
        return dependencies.data_service

    def get_doors_info_for_prompt(self) -> list[dict[str, Any]]:
        """
        获取用于Prompt的门信息列表
        """
        doors_info = []
        all_doors = self.data_service.get_all_doors()
        for door_name in all_doors:
            door_info = self.data_service.get_door_info(door_name)
            if door_info:
                door_type = door_info.get("type", "")
                if door_type == "passage":
                    # 通道门
                    area1 = door_info.get("area1", "")
                    area2 = door_info.get("area2", "")
                    description = f"连接{area1}和{area2}的通道门"
                elif door_type == "standalone":
                    # 独立门
                    location = door_info.get("location", "")
                    description = f"位于{location}的独立门"
                else:
                    description = "门"
                
                doors_info.append({
                    "name": door_name,
                    "type": door_type,
                    "description": description
                })
        return doors_info

    def get_areas_info_for_prompt(self) -> list[dict[str, Any]]:
        """
        获取用于Prompt的区域信息列表
        """
        areas_info = []
        all_areas = self.data_service.get_all_areas()
        for area_name in all_areas:
            area_info = self.data_service.get_area_info(area_name)
            if area_info:
                aliases_str = area_info.get("aliases", "")
                description_str = area_info.get("description", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                areas_info.append({
                    "name": area_name,
                    "description": f"{description_str}，也称为{aliases}"
                })
        return areas_info

    def get_devices_info_for_prompt(self) -> list[dict[str, Any]]:
        """
        获取用于Prompt的设备信息列表
        """
        devices_info = []
        all_devices = self.data_service.get_all_devices()
        for device_name in all_devices:
            device_info = self.data_service.get_device_info(device_name)
            if device_info:
                aliases_str = device_info.get("aliases", "")
                description_str = device_info.get("description", "")
                device_type = device_info.get("type", "")
                area = device_info.get("area", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                devices_info.append({
                    "name": device_name,
                    "type": device_type,
                    "area": area,
                    "description": f"{description_str}，也称为{aliases}"
                })
        return devices_info

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
