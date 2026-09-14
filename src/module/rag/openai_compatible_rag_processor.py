#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.rag.base_rag_processor import BaseRAGProcessor


class OpenAICompatibleRAGProcessor(BaseRAGProcessor):
    """通用的 OpenAI 兼容 RAG 处理器（适用于 SiliconFlow、ModelScope 等）。"""

    def __init__(self, settings: RAGSettings) -> None:
        """初始化 OpenAI 兼容 RAG 处理器。

        Args:
            settings: RAG配置
        """
        super().__init__(settings)

    def _create_embedding_model(self) -> Embeddings:
        """创建 OpenAI 兼容的 Embedding 模型。"""
        # ModelScope 作为旧 provider 名保留，并继续读取旧配置字段。
        # ModelScope embedding 端点不支持批量请求，保留旧实现的单条批大小。
        if self.settings.provider.lower() == "modelscope":
            model = self.settings.modelscope_embedding_model
            base_url = self.settings.modelscope_base_url
            api_key = self.settings.modelscope_api_key
            chunk_size = 1
        else:
            model = self.settings.openai_compatible_embedding_model
            base_url = self.settings.openai_compatible_base_url
            api_key = self.settings.openai_compatible_api_key
            chunk_size = self.settings.openai_compatible_chunk_size

        logger.info(
            "创建 OpenAI 兼容 Embedding 模型: model={model}, base_url={base_url}, chunk_size={chunk_size}",
            model=model,
            base_url=base_url,
            chunk_size=chunk_size,
        )

        return OpenAIEmbeddings(
            model=model,
            base_url=base_url,
            api_key=api_key,
            check_embedding_ctx_length=False,
            chunk_size=chunk_size,
        )

    async def close(self) -> None:
        """关闭 OpenAI 兼容 RAG 处理器资源。"""
        logger.info("正在清理 OpenAI 兼容 RAG 资源...")
        # OpenAI Compatible API 无需特殊清理
