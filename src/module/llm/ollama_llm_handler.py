#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from loguru import logger

from src.config.config import LLMSettings
from src.module.data_loader import format_docs_for_prompt
from src.module.llm.base_llm_handler import BaseLLMHandler


class OllamaLLMHandler(BaseLLMHandler):
    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化使用LangChain的异步Ollama大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)

        # 1. 初始化ChatOllama模型
        # ChatOllama原生支持异步操作
        try:
            self.model = ChatOllama(model=settings.model)
        except Exception as e:
            logger.exception("初始化ChatOllama客户端失败，请确保Ollama服务正在运行。")
            exit(1)

        # 2. 将工具绑定到模型
        self.model_with_tools = self.model.bind_tools(self.tools)

        # 3. 构建处理链 (Chain)
        self.chain = self.prompt_template | self.model_with_tools | self.output_parser

        logger.info("异步Ollama大语言模型处理器初始化完成，使用模型: {model}", model=self.settings.model)

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

            # Validate and retry if necessary
            return await self._validate_and_retry_tool_calls(tool_calls, user_input, rag_docs, 0)

        except Exception as api_error:
            logger.exception("调用Ollama API或处理链时出错: {error}", error=str(api_error))
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

    async def _retry_with_validation_context(
            self,
            user_input: str,
            rag_docs: List[Document],
            validation_context: str,
            validation_errors: List[str],
            retry_count: int
    ) -> str:
        """
        Retry LLM call with validation context included in the prompt.
        """
        logger.info(f"Retrying LLM call with validation context (attempt {retry_count})")

        try:
            # Create a modified system prompt that includes validation context
            retry_prompt_template = self.settings.system_prompt_template + """

# 验证上下文 (Validation Context)
你之前的响应包含无效的资源引用。请只使用以下可用资源：

{validation_context}

# 验证错误 (Validation Errors)
之前的响应有以下问题：
{validation_errors_str}

请重新生成响应，确保只使用上述可用资源。
"""
            # Prepare retry chain input
            rag_context = format_docs_for_prompt(rag_docs)
            screens_info_json = json.dumps(self.screens_info, ensure_ascii=False, indent=2)
            doors_info_json = json.dumps(self.doors_info, ensure_ascii=False, indent=2)
            validation_errors_str = "\n".join([f"- {error}" for error in validation_errors])

            retry_chain_input = {
                "SCREENS_INFO": screens_info_json,
                "DOORS_INFO": doors_info_json,
                "rag_context": rag_context,
                "validation_context": validation_context,
                "validation_errors_str": validation_errors_str,
                "USER_INPUT": user_input
            }

            # Create retry chain with modified prompt
            retry_prompt = ChatPromptTemplate.from_messages([
                ("system", retry_prompt_template),
                ("user", "{USER_INPUT}")
            ])
            retry_chain = retry_prompt | self.model_with_tools | self.output_parser

            # Call retry chain
            tool_calls = await retry_chain.ainvoke(retry_chain_input)

            # Validate again (this will handle further retries if needed)
            return await self._validate_and_retry_tool_calls(tool_calls, user_input, rag_docs, retry_count)

        except Exception as retry_error:
            logger.exception(f"Retry attempt {retry_count} failed: {retry_error}")
            # If retry fails, return validation error
            error_response = {
                "action": "error",
                "reason": "retry_failure",
                "message": f"Retry attempt {retry_count} failed",
                "details": [str(retry_error)]
            }
            return json.dumps([error_response], ensure_ascii=False)
