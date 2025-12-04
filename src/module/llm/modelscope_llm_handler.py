#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.base_llm_handler import BaseLLMHandler
from src.module.llm.helper import DocumentFormatter


class ModelScopeLLMHandler(BaseLLMHandler):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化使用LangChain的ModelScope大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)
        # Keep __init__ lightweight - defer heavy initialization to async initialize()
        self.model = None
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.settings.system_prompt_template),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{context}\n\n用户指令: {user_input}")
        ])
        
        logger.info("ModelScope大语言模型处理器已创建，等待异步初始化...")

    async def initialize(self) -> None:
        """
        异步初始化ModelScope模型和处理链。
        """
        if self.model is not None:
            return

        # 1. 初始化ChatOpenAI模型 for ModelScope
        try:
            # 处理 SecretStr 类型的 API key
            self.model = ChatOpenAI(
                model=self.settings.modelscope_model,
                base_url=self.settings.modelscope_base_url,
                api_key=self.settings.modelscope_api_key,
                temperature=0.7,
                top_p=0.8,
                timeout=self.settings.request_timeout,
                max_retries=0,
                extra_body={
                    "top_k": 20,
                    "min_p": 0,
                    "enable_thinking": False
                }
            )
        except Exception:
            logger.exception("初始化ModelScope客户端失败，请检查API配置。")
            raise

        # 2. 将工具绑定到模型
        self.model_with_tools = self.model.bind_tools(self.tools)
        
        # 3. 构建处理链
        self.chain = self.prompt_template | self.trimmer | self.model_with_tools

        logger.info("ModelScope大语言模型处理器初始化完成，使用模型: {model}", model=self.settings.modelscope_model)

    async def get_response(self, user_input: str, rag_docs: dict[str, list[Document]], user_location: str, chat_history: list) -> str:
        """
        结合RAG上下文，异步获取大模型的响应 - 现代结构化输出版本。

        Args:
            user_input (str): 用户的原始输入文本。
            rag_docs (dict[str, list[Document]]): 按类型分类的RAG文档字典 {"door": [...], "video": [...], "device": [...]}
            user_location (str): 用户当前位置。
            chat_history (list): 聊天记录。

        Returns:
            str: 大模型返回的JSON格式指令或错误信息。
        """
        # Ensure the handler is initialized before use
        if self.chain is None:
            await self.initialize()

        logger.info("用户指令: {user_input}", user_input=user_input)

        try:
            # 准备Prompt的输入变量
            # 1. 从分类文档中提取各类型信息
            video_docs = rag_docs.get("video", [])
            door_docs = rag_docs.get("door", [])
            device_docs = rag_docs.get("device", [])
            
            videos_info = DocumentFormatter.get_prompt_from_documents(self, video_docs)
            doors_info = DocumentFormatter.get_prompt_from_documents(self, door_docs)
            devices_info = DocumentFormatter.get_prompt_from_documents(self, device_docs)
            area_list = self.get_areas_info_for_prompt()
            areas_info_json = json.dumps(area_list, ensure_ascii=False, indent=2)
            
            context = self.settings.user_context_template.format(
                AREAS_INFO=areas_info_json,
                DEVICES_INFO=devices_info,
                DOORS_INFO=doors_info,
                VIDEOS_INFO=videos_info,
                USER_LOCATION=user_location
            )
            
            # 2. 构造Chain输入
            chain_input = {
                "context": context,
                "user_input": user_input,
                "chat_history": chat_history
            }

            # 异步调用现代化处理链 - 直接获得结构化输出
            response = await self.chain.ainvoke(chain_input)

            # 格式化结构化响应为JSON字符串
            return self._format_response(response)

        except Exception as api_error:
            logger.exception("调用ModelScope API或处理链时出错: {error}", error=str(api_error))
            # Use the modern error response method
            return self.create_error_response("api_failure", str(api_error))
