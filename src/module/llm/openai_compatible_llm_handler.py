#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.base_llm_handler import BaseLLMHandler


class OpenAICompatibleLLMHandler(BaseLLMHandler):
    """
    通用的 OpenAI 兼容大语言模型处理器（支持 SiliconFlow、ModelScope、DeepSeek 等）。
    """

    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化 OpenAI 兼容大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)
        logger.info("OpenAI 兼容大语言模型处理器已创建，等待异步初始化...")

    def _create_model(self) -> BaseChatModel:
        """
        创建 OpenAI 兼容的 ChatOpenAI 模型实例。

        Returns:
            BaseChatModel: 初始化后的 ChatOpenAI 模型
        """
        # ModelScope 作为旧 provider 名保留，并继续读取旧配置字段。
        # 其他 OpenAI 兼容 provider 统一使用新的 openai_compatible_* 配置。
        if self.settings.provider.lower() == "modelscope":
            model_name = self.settings.modelscope_model
            base_url = self.settings.modelscope_base_url
            api_key = self.settings.modelscope_api_key
        else:
            model_name = self.settings.openai_compatible_model
            base_url = self.settings.openai_compatible_base_url
            api_key = self.settings.openai_compatible_api_key

        try:
            model = ChatOpenAI(
                model=model_name,
                base_url=base_url,
                api_key=api_key,
                temperature=0.7,
                top_p=0.8,
                timeout=self.settings.request_timeout,
                max_retries=0,
            )
            logger.info("OpenAI 兼容模型创建成功，使用模型: {model}, base_url: {base_url}", model=model_name, base_url=base_url)
            return model
        except Exception:
            logger.exception("初始化 OpenAI 兼容客户端失败，请检查 API 配置。")
            raise
