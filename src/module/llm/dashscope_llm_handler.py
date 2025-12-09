#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.base_llm_handler import BaseLLMHandler


class DashScopeLLMHandler(BaseLLMHandler):
    """
    使用 DashScope (阿里云百炼平台) API 的 LLM 处理器。
    
    通过 OpenAI Compatible API 方式调用百炼平台的大语言模型。
    """

    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化 DashScope 大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)
        logger.info("DashScope大语言模型处理器已创建，等待异步初始化...")

    def _create_model(self) -> BaseChatModel:
        """
        创建 DashScope ChatOpenAI 模型实例。
        
        使用 OpenAI Compatible API 方式连接到阿里云百炼平台。
        
        Returns:
            BaseChatModel: 初始化后的 ChatOpenAI 模型
        """
        try:
            model = ChatOpenAI(
                model=self.settings.dashscope_model,
                base_url=self.settings.dashscope_base_url,
                api_key=self.settings.dashscope_api_key,
                temperature=0.7,
                top_p=0.8,
                timeout=self.settings.request_timeout,
                max_retries=0,
            )
            logger.info("DashScope模型创建成功，使用模型: {model}", model=self.settings.dashscope_model)
            return model
        except Exception:
            logger.exception("初始化DashScope客户端失败，请检查API配置。")
            raise
