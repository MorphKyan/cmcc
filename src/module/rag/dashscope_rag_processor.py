#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.rag.base_rag_processor import BaseRAGProcessor


class DashScopeRAGProcessor(BaseRAGProcessor):
    """使用阿里云百炼（DashScope）平台的RAG处理器。"""
    
    def __init__(self, settings: RAGSettings) -> None:
        """初始化百炼（DashScope）RAG处理器。

        Args:
            settings: RAG配置
        """
        super().__init__(settings)

    def _create_embedding_model(self) -> Embeddings:
        """创建百炼平台Embedding模型（使用OpenAI兼容API）。"""
        return OpenAIEmbeddings(
            model=self.settings.dashscope_embedding_model,
            base_url=self.settings.dashscope_base_url,
            api_key=self.settings.dashscope_api_key,
            check_embedding_ctx_length=False,
            chunk_size=10  # API doesn't handle batching correctly
        )

    async def close(self) -> None:
        """关闭百炼 RAG处理器资源。"""
        logger.info("正在清理百炼 RAG资源...")
        # OpenAI Compatible API 无需特殊清理
