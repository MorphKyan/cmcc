#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation and retry service for LLM handlers.

This module handles the validation of LLM tool calls and implements retry logic
when validation fails, using the context from validation errors to guide retries.
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from src.config.config import LLMSettings
from src.core.validation_service import ValidationService
from src.module.data_loader import format_docs_for_prompt


class BaseValidationRetryService(ABC):
    """验证重试服务基类"""

    def __init__(self, validation_service: ValidationService, settings: LLMSettings):
        self.validation_service = validation_service
        self.settings = settings

    @abstractmethod
    async def validate_and_retry(
            self,
            tool_calls: list[dict[str, Any]],
            user_input: str,
            rag_docs: list[Document],
            llm_handler,
            retry_count: int = 0
    ) -> str:
        """
        验证工具调用并根据需要重试。

        Args:
            tool_calls: LLM返回的工具调用列表
            user_input: 原始用户输入
            rag_docs: RAG文档列表
            llm_handler: LLM处理器实例
            retry_count: 当前重试次数

        Returns:
            JSON格式的响应字符串
        """
        pass

    @abstractmethod
    async def _retry_with_validation_context(
            self,
            user_input: str,
            rag_docs: list[Document],
            validation_context: str,
            validation_errors: list[str],
            retry_count: int,
            llm_handler
    ) -> str:
        """
        使用验证上下文进行重试。

        Args:
            user_input: 用户输入
            rag_docs: RAG文档
            validation_context: 验证上下文
            validation_errors: 验证错误列表
            retry_count: 重试次数
            llm_handler: LLM处理器实例

        Returns:
            JSON格式的响应字符串
        """
        pass


class ValidationRetryService(BaseValidationRetryService):
    """
    验证重试服务实现。

    这个服务封装了验证和重试的完整逻辑，可以被不同的LLM处理器复用。
    """

    async def validate_and_retry(
            self,
            tool_calls: list[dict[str, Any]],
            user_input: str,
            rag_docs: list[Document],
            llm_handler,
            retry_count: int = 0
    ) -> str:
        """
        验证工具调用并根据需要重试。

        Args:
            tool_calls: LLM返回的工具调用列表
            user_input: 原始用户输入
            rag_docs: RAG文档列表
            llm_handler: LLM处理器实例
            retry_count: 当前重试次数

        Returns:
            JSON格式的响应字符串
        """
        if not tool_calls:
            return '[]'

        # Validate the tool calls
        is_valid, errors = self.validation_service.validate_function_calls(tool_calls)

        if is_valid:
            # Validation passed, return mapped response
            return llm_handler.response_mapper.map_tool_calls_to_response(tool_calls)

        # Validation failed, check if we should retry
        max_retries = self.settings.max_validation_retries
        if retry_count < max_retries:
            logger.warning(f"Validation failed (attempt {retry_count + 1}/{max_retries + 1}): {errors}")

            # Add delay before retry
            await asyncio.sleep(self.settings.retry_delay)

            # Get validation context for the retry prompt
            validation_context = self.validation_service.get_validation_context()

            # Retry with modified prompt that includes validation errors
            retry_response = await self._retry_with_validation_context(
                user_input, rag_docs, validation_context, errors, retry_count + 1, llm_handler
            )
            return retry_response

        # Max retries exceeded, return error response
        logger.error(f"Max validation retries ({max_retries}) exceeded. Errors: {errors}")
        error_response = llm_handler.response_mapper.create_error_response(
            reason="validation_failed",
            message="Requested resources not found. Please specify valid videos, doors, or screens.",
            details=errors
        )
        return json.dumps([error_response], ensure_ascii=False)

    async def _retry_with_validation_context(
            self,
            user_input: str,
            rag_docs: list[Document],
            validation_context: str,
            validation_errors: list[str],
            retry_count: int,
            llm_handler
    ) -> str:
        """
        使用验证上下文进行重试。

        Args:
            user_input: 用户输入
            rag_docs: RAG文档
            validation_context: 验证上下文
            validation_errors: 验证错误列表
            retry_count: 重试次数
            llm_handler: LLM处理器实例

        Returns:
            JSON格式的响应字符串
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
            screens_info_json = json.dumps(llm_handler.get_screens_info_for_prompt(), ensure_ascii=False, indent=2)
            doors_info_json = json.dumps(llm_handler.get_doors_info_for_prompt(), ensure_ascii=False, indent=2)
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

            # Get the model with tools and output parser from the LLM handler
            _, model_with_tools, output_parser = llm_handler.get_retry_chain_components()
            retry_chain = retry_prompt | model_with_tools | output_parser

            # Call retry chain
            tool_calls = await retry_chain.ainvoke(retry_chain_input)

            # Validate again (this will handle further retries if needed)
            return await self.validate_and_retry(tool_calls, user_input, rag_docs, llm_handler, retry_count)

        except Exception as retry_error:
            logger.exception(f"Retry attempt {retry_count} failed: {retry_error}")
            # If retry fails, return validation error
            error_response = llm_handler.response_mapper.create_error_response(
                reason="retry_failure",
                message=f"Retry attempt {retry_count} failed",
                details=[str(retry_error)]
            )
            return json.dumps([error_response], ensure_ascii=False)
