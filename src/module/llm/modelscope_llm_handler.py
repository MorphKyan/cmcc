#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config.config import LLMSettings
from src.core.retry_strategies import exponential_backoff_retry
from src.module.llm.base_llm_handler import BaseLLMHandler


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
        self.model_with_tools = None
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
                max_retries=0,  # Disable LangChain's built-in retry, we'll handle it ourselves
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
        self.chain = self.prompt_template | self.model_with_tools | self.tool_strategy

        logger.info("ModelScope大语言模型处理器初始化完成，使用模型: {model}", model=self.settings.modelscope_model)

    @exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        max_delay=10.0
    )
    async def get_response(self, user_input: str, rag_docs: list[Document]) -> str:
        """
        结合RAG上下文，异步获取大模型的响应 - 现代结构化输出版本。

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

            # 异步调用现代化处理链 - 直接获得结构化输出
            structured_response = await self.chain.ainvoke(chain_input)

            # 格式化结构化响应为JSON字符串
            return self._format_structured_response(structured_response)

        except Exception as api_error:
            logger.exception("调用ModelScope API或处理链时出错: {error}", error=str(api_error))
            # Use the modern error response method
            return self.create_error_response("api_failure", str(api_error))