#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.rag.base_rag_processor import BaseRAGProcessor


class ModelScopeRAGProcessor(BaseRAGProcessor):
    """使用ModelScope平台的RAG处理器。"""
    
    def __init__(self, settings: RAGSettings) -> None:
        """初始化ModelScope RAG处理器。

        Args:
            settings: RAG配置
        """
        super().__init__(settings)

    def _create_embedding_model(self) -> Embeddings:
        """创建ModelScope Embedding模型（使用OpenAI兼容API）。"""
        return OpenAIEmbeddings(
            model=self.settings.modelscope_embedding_model,
            base_url=self.settings.modelscope_base_url,
            api_key=self.settings.modelscope_api_key,
            check_embedding_ctx_length=False,
            chunk_size=1  # ModelScope API doesn't handle batching correctly
        )

    async def close(self) -> None:
        """关闭ModelScope RAG处理器资源。"""
        logger.info("正在清理ModelScope RAG资源...")
        # OpenAI Compatible API 无需特殊清理