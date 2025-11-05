#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.base_llm_handler import BaseLLMHandler


class ModelScopeLLMHandler(BaseLLMHandler):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化使用LangChain的ModelScope大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)

        # 1. 初始化ChatOpenAI模型 for ModelScope
        # ModelScope API is compatible with OpenAI API
        try:
            # 处理 SecretStr 类型的 API key
            self.model = ChatOpenAI(
                model=settings.model,
                base_url=settings.modelscope_base_url,
                api_key=settings.modelscope_api_key,
                temperature=0.7,
                top_p=0.8,
                extra_body={
                    "top_k": 20,
                    "min_p": 0,
                    "enable_thinking": False
                }
            )
        except Exception as e:
            logger.exception("初始化ModelScope客户端失败，请检查API配置。")
            exit(1)

        # 2. 将工具绑定到模型
        self.model_with_tools = self.model.bind_tools(self.tools)

        # 3. 构建处理链 (Chain)
        self.chain = self.prompt_template | self.model_with_tools | self.output_parser

        logger.info("ModelScope大语言模型处理器初始化完成，使用模型: {model}", model=self.settings.model)

    async def get_response(self, user_input: str, rag_docs: list[Document]) -> str:
        """
        结合RAG上下文，异步获取大模型的响应。

        Args:
            user_input (str): 用户的原始输入文本。
            rag_docs (list[Document]): RAG检索器返回的文档列表。

        Returns:
            str: 大模型返回的JSON格式指令或错误信息。
        """
        logger.info("用户指令: {user_input}", user_input=user_input)

        try:
            # 准备Prompt的输入变量
            chain_input = self._prepare_chain_input(user_input, rag_docs)

            # 异步调用链
            tool_calls = await self.chain.ainvoke(chain_input)

            # 将解析后的工具调用映射到最终的输出格式
            return self._map_tool_calls_to_response(tool_calls)

        except Exception as api_error:
            logger.exception("调用ModelScope API或处理链时出错: {error}", error=str(api_error))
            # 保持错误返回格式的一致性
            error_response = {
                "action": "error",
                "reason": "api_failure",
                "target": None,
                "device": None,
                "value": None
            }
            # 返回一个包含单个错误对象的JSON数组字符串
            return str(error_response).replace("'", '"')
