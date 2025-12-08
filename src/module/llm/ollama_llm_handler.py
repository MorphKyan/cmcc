#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from loguru import logger

from src.config.config import LLMSettings
from src.module.llm.base_llm_handler import BaseLLMHandler


class OllamaLLMHandler(BaseLLMHandler):
    """
    使用 Ollama 本地模型的 LLM 处理器。
    """

    def __init__(self, settings: LLMSettings) -> None:
        """
        初始化 Ollama 大语言模型处理器。

        Args:
            settings (LLMSettings): LLM参数
        """
        super().__init__(settings)
        logger.info("Ollama大语言模型处理器已创建，等待异步初始化...")

    def _create_model(self) -> BaseChatModel:
        """
        创建 Ollama ChatOllama 模型实例。
        
        Returns:
            BaseChatModel: 初始化后的 ChatOllama 模型
        """
        try:
            model = ChatOllama(
                model=self.settings.ollama_model,
                base_url=self.settings.ollama_base_url,
            )
            logger.info("Ollama模型创建成功，使用模型: {model}", model=self.settings.ollama_model)
            return model
        except Exception:
            logger.exception("初始化ChatOllama客户端失败，请确保Ollama服务正在运行。")
            raise