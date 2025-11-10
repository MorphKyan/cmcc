#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config.config import LLMSettings, VolcEngineSettings
from src.core.retry_strategies import exponential_backoff_retry
from src.module.llm.base_llm_handler import BaseLLMHandler


class ArkLLMHandler(BaseLLMHandler):
    def __init__(self, settings: LLMSettings, volcengine_settings: VolcEngineSettings) -> None:
        """
        初始化使用LangChain的火山引擎Ark大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
            volcengine_settings (VolcEngineSettings): 火山引擎参数
        """
        super().__init__(settings)

        # 1. 初始化ChatOpenAI模型 for VolcEngine Ark
        # VolcEngine Ark API is compatible with OpenAI API
        try:
            self.model = ChatOpenAI(
                model=volcengine_settings.llm_model_name,
                base_url=volcengine_settings.ark_base_url,
                api_key=volcengine_settings.ark_api_key,
                temperature=0.7,
                top_p=0.8,
                timeout=volcengine_settings.request_timeout,
                max_retries=0,  # Disable LangChain's built-in retry, we'll handle it ourselves
                extra_body={
                    "top_k": 20,
                    "min_p": 0,
                    "enable_thinking": False
                }
            )
        except Exception as e:
            logger.exception("初始化火山引擎Ark客户端失败，请检查API配置。")
            exit(1)

        # 2. 将工具绑定到模型
        self.model_with_tools = self.model.bind_tools(self.tools)

        # 3. 构建处理链 (Chain)
        self.chain = self.prompt_template | self.model_with_tools | self.output_parser

        logger.info("火山引擎Ark大语言模型处理器初始化完成，使用模型: {model}", model=volcengine_settings.llm_model_name)

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
            logger.exception("调用火山引擎Ark API或处理链时出错: {error}", error=str(api_error))
            # Use the response mapper to create consistent error response
            error_response = self.response_mapper.create_error_response("api_failure")
            return json.dumps([error_response], ensure_ascii=False)

    async def check_health(self) -> bool:
        """
        检查火山引擎Ark服务的健康状态。
        通过发送一个简单的健康检查请求来验证服务是否可用。
        """
        try:
            # 使用简单的健康检查提示
            health_check_input = {
                "SCREENS_INFO": json.dumps(self.screens_info, ensure_ascii=False),
                "DOORS_INFO": json.dumps(self.doors_info, ensure_ascii=False),
                "rag_context": "",
                "USER_INPUT": "健康检查"
            }

            # 使用较短的超时进行健康检查
            health_chain = self.prompt_template | self.model_with_tools | self.output_parser

            # 设置较短的超时
            import asyncio
            await asyncio.wait_for(health_chain.ainvoke(health_check_input), timeout=5.0)

            return True
        except Exception as e:
            logger.warning(f"Ark健康检查失败: {e}")
            return False