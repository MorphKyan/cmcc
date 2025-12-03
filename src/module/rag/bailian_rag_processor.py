#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.rag.base_rag_processor import BaseRAGProcessor, RAGStatus


class BailianRAGProcessor(BaseRAGProcessor):
    def __init__(self, settings: RAGSettings) -> None:
        """初始化百炼（Bailian）RAG处理器。

        Args:
            settings: RAG配置
        """
        super().__init__(settings)
        self.embedding_model: OpenAIEmbeddings | None = None
        self._init_lock = asyncio.Lock()
        logger.info("BailianRAGProcessor已创建，状态: UNINITIALIZED。")

    async def initialize(self) -> None:
        """初始化百炼 RAG处理器：加载模型、创建或加载数据库。"""
        async with self._init_lock:
            if self.status == RAGStatus.INITIALIZING:
                logger.warning("初始化已在进行中，请等待。")
                return
            self.status = RAGStatus.INITIALIZING
            logger.info("开始初始化百炼 RAG处理器...")

            try:
                # 使用 OpenAI Compatible API 方式调用百炼平台
                self.embedding_model = OpenAIEmbeddings(
                    model=self.settings.bailian_embedding_model,
                    base_url=self.settings.bailian_base_url,
                    api_key=self.settings.bailian_api_key.get_secret_value(),
                    check_embedding_ctx_length=False,
                    chunk_size=10  # API doesn't handle batching correctly
                )
                if not os.path.exists(self.chroma_db_dir):
                    logger.info("未找到本地向量数据库，正在创建...")
                    await self._create_and_persist_db(self.embedding_model)
                else:
                    logger.info("正在从本地加载向量数据库...")
                    self.vector_store = await asyncio.to_thread(
                        Chroma,
                        persist_directory=self.settings.chroma_db_dir,
                        embedding_function=self.embedding_model
                    )

                self.retriever = self.vector_store.as_retriever(
                    search_kwargs={"k": self.settings.top_k_results}
                )
                self.status = RAGStatus.READY
                self.error_message = None
                logger.success("百炼 RAG处理器初始化完成，状态: READY。")
            except Exception as e:
                self.status = RAGStatus.ERROR
                self.error_message = f"百炼 RAG初始化失败: {str(e)}"
                logger.exception(self.error_message)
                raise

    async def retrieve_context(self, query: str) -> list[Document]:
        """根据用户查询异步检索相关上下文。"""
        if self.status != RAGStatus.READY:
            raise RuntimeError(f"RAG处理器未准备就绪，当前状态: {self.status}")
        logger.info("正在为查询检索上下文: '{query}'", query=query)
        docs = await self.retriever.ainvoke(query)
        logger.info("检索到 {num_docs} 个相关文档。", num_docs=len(docs))
        return docs

    async def close(self) -> None:
        """关闭百炼 RAG处理器资源。"""
        logger.info("正在清理百炼 RAG资源...")
        # OpenAI Compatible API 无需特殊清理
        pass
