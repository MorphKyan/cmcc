#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSerializable
from langchain_core.messages import ToolMessage, AIMessage, trim_messages
from loguru import logger

from src.config.config import LLMSettings
from src.core import dependencies
from src.module.llm.tool.definitions import get_tools, ExhibitionCommand
from src.module.llm.tool.dynamic_tool_manager import DynamicToolManager
from src.module.llm.tool.validator import ToolValidator
from src.module.llm.helper import DocumentFormatter


class BaseLLMHandler(ABC):
    """
    LLM处理器基类，定义了与大语言模型交互的通用流程。
    
    子类只需实现 _create_model() 方法来返回具体的模型实例。
    """
    
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化LLM处理器基类。

        Args:
            settings (LLMSettings): LLM参数
        """
        self.settings = settings
        self.model: BaseChatModel | None = None
        self.model_with_tools = None
        self.chain: RunnableSerializable[dict, Any] | None = None

        # 初始化动态工具管理器并注册更新回调
        self._dynamic_manager = DynamicToolManager()
        self._dynamic_manager.on_update(self._on_tools_updated)
        
        # 合并原生工具和动态工具
        self._native_tools = get_tools()
        self.tools = self._native_tools + self._dynamic_manager.get_langchain_tools()
        self._tool_map = {tool.name: tool for tool in self.tools}

        # 使用ChatPromptTemplate构建提示词
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", settings.system_prompt_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", settings.user_context_template)
        ])

        # 创建消息修剪器 (Trimmer)
        self.trimmer = trim_messages(
            strategy="last",
            max_tokens=5,
            token_counter=len,
            include_system=False,
            allow_partial=False,
            start_on="human"
        )

        logger.info("LLM处理器基类初始化完成，工具数: {} (原生: {}, 动态: {})", 
                    len(self.tools), len(self._native_tools), 
                    len(self._dynamic_manager.get_langchain_tools()))

    @abstractmethod
    def _create_model(self) -> BaseChatModel:
        """
        创建并返回具体的LLM模型实例。
        
        子类必须实现此方法以返回对应的模型（如 ChatOpenAI, ChatOllama 等）。
        
        Returns:
            BaseChatModel: 初始化后的模型实例
        """
        pass

    def _build_chain(self) -> None:
        """
        构建处理链：绑定工具并创建运行链。
        
        在子类的 initialize() 方法创建模型后调用此方法。
        """
        if self.model is None:
            raise ValueError("Model must be created before building chain")
        
        # 将工具绑定到模型
        self.model_with_tools = self.model.bind_tools(self.tools)
        
        # 构建处理链
        self.chain = self.prompt_template | self.trimmer | self.model_with_tools
        
        logger.debug("处理链构建完成")

    def _on_tools_updated(self) -> None:
        """
        工具更新回调 - 当动态工具发生变化时重建工具列表和处理链。
        
        此方法由 DynamicToolManager 在工具增删时自动调用。
        """
        # 重新合并工具列表
        self.tools = self._native_tools + self._dynamic_manager.get_langchain_tools()
        self._tool_map = {tool.name: tool for tool in self.tools}
        
        # 如果模型已初始化，重建处理链
        if self.model is not None:
            self.model_with_tools = self.model.bind_tools(self.tools)
            self.chain = self.prompt_template | self.trimmer | self.model_with_tools
            logger.info("LLM工具热重载完成，当前工具数: {} (原生: {}, 动态: {})",
                        len(self.tools), len(self._native_tools),
                        len(self._dynamic_manager.get_langchain_tools()))
        else:
            logger.debug("工具列表已更新，但模型尚未初始化，跳过重建处理链")

    async def initialize(self) -> None:
        """
        异步初始化模型和处理链。
        
        子类可以覆盖此方法以添加额外的初始化逻辑，但应调用 super().initialize()。
        """
        if self.model is not None:
            return
        
        # 创建模型（由子类实现）
        self.model = self._create_model()
        
        # 构建处理链
        self._build_chain()
        
        logger.info(f"{self.__class__.__name__} 初始化完成")

    async def check_health(self) -> bool:
        """
        检查服务的健康状态。
        """
        try:
            if self.chain is None:
                await self.initialize()

            health_check_input = {
                "DEVICES_INFO": "",
                "DOORS_INFO": "",
                "AREAS_INFO": "",
                "VIDEOS_INFO": "",
                "USER_INPUT": "健康检查",
                "USER_LOCATION": ""
            }

            import asyncio
            await asyncio.wait_for(self.chain.ainvoke(health_check_input), timeout=5.0)

            return True
        except Exception as e:
            logger.warning(f"LLM健康检查失败: {e}")
            return False

    def get_network_retry_config(self) -> dict:
        """
        获取网络重试配置。
        """
        return {
            'max_retries': getattr(self.settings, 'max_network_retries', 3),
            'base_delay': getattr(self.settings, 'base_retry_delay', 1.0),
            'max_delay': getattr(self.settings, 'max_retry_delay', 10.0)
        }

    async def get_response(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> list[ExhibitionCommand]:
        """
        结合RAG上下文，异步获取大模型的响应。
        
        Args:
            user_input: 用户输入
            rag_docs: 按类型分类的RAG文档字典 {"door": [...], "video": [...], "device": [...]}
            user_location: 用户当前位置
            chat_history: 聊天历史
            
        Returns:
            list[ExhibitionCommand]: 命令列表
        """
        if self.chain is None:
            await self.initialize()

        logger.info("用户指令: {user_input}", user_input=user_input)

        try:
            chain_input = self._prepare_chain_input(user_input, rag_docs, user_location, chat_history)
            response = await self.chain.ainvoke(chain_input)
            return self._format_response(response)
        except Exception as api_error:
            logger.exception("调用LLM API时出错: {error}", error=str(api_error))
            return self.create_error_response("api_failure", str(api_error))

    async def get_response_with_retries(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> tuple[AIMessage, list[ExhibitionCommand]]:
        """
        带重试机制的响应获取方法。
        使用LangChain的bind_tools和自定义循环来处理工具调用和错误恢复。
        
        Args:
            user_input: 用户输入
            rag_docs: 按类型分类的RAG文档字典 {"door": [...], "video": [...], "device": [...]}
            user_location: 用户当前位置
            chat_history: 聊天历史
            
        Returns:
            tuple[AIMessage, list[ExhibitionCommand]]: (AI消息用于历史记录, 命令列表用于执行)
        """
        # 1. 准备输入
        chain_input = self._prepare_chain_input(user_input, rag_docs, user_location, chat_history)
        
        # 2. 确保模型已初始化
        if not self.model_with_tools:
            await self.initialize()
            if not self.model_with_tools:
                raise ValueError("Model with tools not initialized.")

        messages = []
        
        # 初始调用
        try:
            ai_msg = await self.chain.ainvoke(chain_input)
        except Exception as e:
            logger.error(f"Initial LLM call failed: {e}")
            error_msg = AIMessage(content=f"错误: {e}")
            return error_msg, self.create_error_response("llm_error", str(e))

        messages.append(ai_msg)
        
        # 3. 进入重试/执行循环
        max_retries = getattr(self.settings, 'max_validation_retries', 3)
        
        for attempt in range(max_retries):
            if not ai_msg.tool_calls:
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
                    error_msg = f"Error executing {tool_name}: {str(e)}. Please correct the arguments."
                    tool_outputs.append(ToolMessage(content=error_msg, tool_call_id=tool_call_id))
                    has_error = True
            
            if not has_error:
                # 所有工具执行成功，返回 AI消息和命令列表
                return ai_msg, self._format_response(ai_msg)
                
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
                error_msg = AIMessage(content=f"重试错误: {e}")
                return error_msg, self.create_error_response("llm_retry_error", str(e))

        # 循环结束（达到最大重试次数或最后一次仍有错）        
        return ai_msg, self._format_response(ai_msg)

    def _prepare_chain_input(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> dict[str, Any]:
        """
        准备Prompt的输入变量。
        """
        video_docs = rag_docs.get("video", [])
        door_docs = rag_docs.get("door", [])
        device_docs = rag_docs.get("device", [])
        
        videos_info = DocumentFormatter.format_video_documents(video_docs)
        doors_info = DocumentFormatter.format_door_documents(door_docs)
        devices_info = DocumentFormatter.format_device_documents(device_docs)
        areas_info = DocumentFormatter.format_area_info(self.data_service.get_all_areas_data())

        return {
            "DEVICES_INFO": devices_info,
            "DOORS_INFO": doors_info,
            "AREAS_INFO": areas_info,
            "VIDEOS_INFO": videos_info,
            "USER_INPUT": user_input,
            "USER_LOCATION": user_location,
            "chat_history": chat_history
        }

    def _format_response(self, response) -> list[ExhibitionCommand]:
        """
        将AI响应转换为命令列表。
        """
        if isinstance(response, AIMessage) and response.tool_calls:
            commands = []
            for tool_call in response.tool_calls:
                cmd = ExhibitionCommand(
                    action=tool_call["name"],
                    target=tool_call["args"].get("target"),
                    device=tool_call["args"].get("device"),
                    value=tool_call["args"].get("value")
                )
                commands.append(cmd)
            return commands
            
        return []

    @property
    def data_service(self):
        if dependencies.data_service is None:
            raise RuntimeError("DataService not initialized")
        return dependencies.data_service

    def create_error_response(self, reason: str, message: str | None = None) -> list[ExhibitionCommand]:
        """
        创建错误响应。
        """
        error_value = f"{reason}: {message}" if message else reason
        error_command = ExhibitionCommand(
            action="error",
            target=None,
            device=None,
            value=error_value
        )
        return [error_command]
