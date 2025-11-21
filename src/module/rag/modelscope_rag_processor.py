#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
from urllib.parse import urljoin

import httpx
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.rag.base_rag_processor import BaseRAGProcessor, RAGStatus


class ModelScopeRAGProcessor(BaseRAGProcessor):
    def __init__(self, settings: RAGSettings) -> None:
        """初始化ModelScope RAG处理器。

        Args:
            settings: RAG配置
        """
        super().__init__(settings)
        self.embedding_model: OpenAIEmbeddings | None = None
        self._init_lock = asyncio.Lock()
        self._http_client = httpx.AsyncClient(timeout=10.0)
        logger.info("ModelScopeRAGProcessor已创建，状态: UNINITIALIZED。")

    async def initialize(self) -> None:
        """初始化ModelScope RAG处理器：检查连接、加载模型、创建或加载数据库。"""
        async with self._init_lock:
            if self.status == RAGStatus.INITIALIZING:
                logger.warning("初始化已在进行中，请等待。")
                return
            self.status = RAGStatus.INITIALIZING
            logger.info("开始初始化ModelScope RAG处理器...")

            try:
                await self._check_modelscope_connection()
                self.embedding_model = OpenAIEmbeddings(
                    model=self.settings.modelscope_embedding_model,
                    base_url=self.settings.modelscope_base_url,
                    api_key=self.settings.modelscope_api_key
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
                logger.success("ModelScope RAG处理器初始化完成，状态: READY。")
            except Exception as e:
                self.status = RAGStatus.ERROR
                self.error_message = f"ModelScope RAG初始化失败: {str(e)}"
                logger.exception(self.error_message)
                raise

    async def _check_modelscope_connection(self) -> None:
        logger.info("正在检查ModelScope服务连接: {url}", url=self.settings.modelscope_base_url)
        try:
            response = await self._http_client.get(self.settings.modelscope_base_url)
            response.raise_for_status()

            api_url = urljoin(self.settings.modelscope_base_url, "models")
            headers = {
                "Authorization": f"Bearer {self.settings.modelscope_api_key.get_secret_value()}"
            }
            response = await self._http_client.get(api_url, headers=headers)
            response.raise_for_status()

            logger.info("ModelScope服务连接成功，API密钥验证通过。")

        except httpx.RequestError as e:
            raise ConnectionError(f"无法连接到ModelScope服务: {self.settings.modelscope_base_url}。请确保服务地址正确。") from e
        except Exception as e:
            raise RuntimeError(f"检查ModelScope时发生未知错误: {e}") from e

    async def retrieve_context(self, query: str) -> list[Document]:
        """根据用户查询异步检索相关上下文。"""
        if self.status != RAGStatus.READY:
            raise RuntimeError(f"RAG处理器未准备就绪，当前状态: {self.status}")
        logger.info("正在为查询检索上下文: '{query}'", query=query)
        docs = await self.retriever.ainvoke(query)
        logger.info("检索到 {num_docs} 个相关文档。", num_docs=len(docs))
        return docs

    async def close(self) -> None:
        await self._http_client.aclose()
