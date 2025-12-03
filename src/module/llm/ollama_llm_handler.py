#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.base_llm_handler import BaseLLMHandler


class OllamaLLMHandler(BaseLLMHandler):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化使用LangChain的异步Ollama大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)
        # Keep __init__ lightweight - defer heavy initialization to async initialize()
        self.model = None
        self.model_with_tools = None
        logger.info("异步Ollama大语言模型处理器已创建，等待异步初始化...")

    async def initialize(self) -> None:
        """
        异步初始化Ollama模型和处理链。
        """
        if self.model is not None:
            return

        # 1. 初始化ChatOllama模型
        try:
            self.model = ChatOllama(
                model=self.settings.ollama_model,
                base_url=self.settings.ollama_base_url,
            )
        except Exception as e:
            logger.exception("初始化ChatOllama客户端失败，请确保Ollama服务正在运行。")
            raise

        # 2. 将工具绑定到模型
        self.model_with_tools = self.model.bind_tools(self.tools)

        # 3. 构建处理链
        self.chain = self.prompt_template | self.model_with_tools

        logger.info("异步Ollama大语言模型处理器初始化完成，使用模型: {model}", model=self.settings.ollama_model)

    async def get_response(self, user_input: str, rag_docs: list[Document], user_location: str, chat_history: list) -> str:
        """
        结合RAG上下文，异步获取大模型的响应。
        """
        # Ensure the handler is initialized before use
        if self.chain is None:
            await self.initialize()

        logger.info("用户指令: {user_input}", user_input=user_input)

        try:
            # 准备Prompt的输入变量
            chain_input = self._prepare_chain_input(user_input, rag_docs, user_location=user_location, chat_history=chat_history)

            # 异步调用现代化处理链 - 直接获得结构化输出
            response = await self.chain.ainvoke(chain_input)

            # 格式化结构化响应为JSON字符串
            return self._format_response(response)

        except Exception as api_error:
            logger.exception("调用Ollama API或处理链时出错: {error}", error=str(api_error))
            # Use the modern error response method
            return self.create_error_response("api_failure", str(api_error))