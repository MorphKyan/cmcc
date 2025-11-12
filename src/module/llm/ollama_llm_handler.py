#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from loguru import logger

from src.config.config import LLMSettings
from src.core.retry_strategies import exponential_backoff_retry
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

        # 3. 构建处理链 (Chain)
        self.chain = self.prompt_template | self.model_with_tools | self.output_parser

        logger.info("异步Ollama大语言模型处理器初始化完成，使用模型: {model}", model=self.settings.ollama_model)

    @exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0
    )
    async def get_response(self, user_input: str, rag_docs: list[Document]) -> str:
        """
        结合RAG上下文，异步获取大模型的响应。

        Args:
            user_input (str): 用户的原始输入文本。
            rag_docs (list[Document]): RAG检索器返回的文档列表。

        Returns:
            str: 大模型返回的JSON格式指令或错误信息。
        """
        # Ensure the handler is initialized before use
        if self.chain is None:
            await self.initialize()

        logger.info("用户指令: {user_input}", user_input=user_input)

        try:
            # 准备Prompt的输入变量
            chain_input = self._prepare_chain_input(user_input, rag_docs)

            # 异步调用链
            tool_calls = await self.chain.ainvoke(chain_input)

            # Validate and retry if necessary using the validation retry service
            return await self.validation_retry_service.validate_and_retry(
                tool_calls, user_input, rag_docs, self, 0
            )

        except Exception as api_error:
            logger.exception("调用Ollama API或处理链时出错: {error}", error=str(api_error))
            # Use the response mapper to create consistent error response
            error_response = self.response_mapper.create_error_response("api_failure")
            return json.dumps([error_response], ensure_ascii=False)