#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
import os
import shutil
from typing import Optional
from urllib.parse import urljoin

import httpx
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from loguru import logger

from src.config.config import RAGSettings
from src.module.data_loader import load_documents_from_csvs
from src.module.rag.base_rag_processor import BaseRAGProcessor, RAGStatus


class RAGProcessor(BaseRAGProcessor):
    def __init__(self, settings: RAGSettings) -> None:
        """
        初始化RAG处理器。

        Args:
            settings (RAGSettings): RAG配置
        """
        super().__init__(settings)

        # 初始化状态和核心组件
        self.embedding_model: Optional[OllamaEmbeddings] = None
        self.vector_store: Optional[Chroma] = None
        self.retriever = None

        # 3. 使用asyncio.Lock来防止并发初始化
        self._http_client = httpx.AsyncClient(timeout=10.0)
        logger.info("RAGProcessor已创建，状态: UNINITIALIZED。")

    async def initialize(self) -> None:
        """
        执行耗时的初始化过程：检查连接、加载模型、创建或加载数据库。
        此方法是幂等的，并且是线程安全的。
        """
        async with self._init_lock:
            if self.status == RAGStatus.INITIALIZING:
                logger.warning("初始化已在进行中，请等待。")
                return
            self.status = RAGStatus.INITIALIZING
            logger.info("开始初始化RAG处理器...")

            try:
                # 步骤 1: 检查Ollama连接和模型
                await self._check_ollama_connection()
                # 步骤 2: 初始化Embedding模型
                self.embedding_model = OllamaEmbeddings(
                    model=self.settings.ollama_embedding_model,
                    base_url=self.settings.ollama_base_url
                )
                # 步骤 3: 创建或加载向量数据库
                if not os.path.exists(self.chroma_db_dir):
                    logger.info("未找到本地向量数据库，正在创建...")
                    await self._create_and_persist_db()
                else:
                    logger.info("正在从本地加载向量数据库...")
                    self.vector_store = await asyncio.to_thread(
                        Chroma,
                        persist_directory=self.settings.chroma_db_dir,
                        embedding_function=self.embedding_model
                    )

                # 步骤 4: 创建Retriever
                self.retriever = self.vector_store.as_retriever(
                    search_kwargs={"k": self.settings.top_k_results}
                )
                self.status = RAGStatus.READY
                self.error_message = None
                logger.success("RAG处理器初始化完成，状态: READY。")
            except Exception as e:
                self.status = RAGStatus.ERROR
                self.error_message = f"RAG初始化失败: {e}"
                logger.exception(self.error_message)
                raise

    async def _check_ollama_connection(self) -> None:
        logger.info("正在检查Ollama服务连接: {url}", url=self.settings.ollama_base_url)
        try:
            # 检查Ollama服务是否在线
            response = await self._http_client.get(self.settings.ollama_base_url)
            response.raise_for_status()
            # 检查所需模型是否已拉取
            api_url = urljoin(self.settings.ollama_base_url, "api/tags")
            response = await self._http_client.get(api_url)
            response.raise_for_status()

            available_models = [m['name'] for m in response.json().get('models', [])]
            logger.info("Ollama服务连接成功。可用模型: {models}", models=available_models)
            if self.settings.ollama_embedding_model not in available_models:
                error_msg = (
                    f"Ollama服务中未找到所需模型: '{self.settings.ollama_embedding_model}'. "
                    f"请先执行: ollama pull {self.settings.ollama_embedding_model}"
                )
                raise RuntimeError(error_msg)

            logger.info("所需Embedding模型 '{model}' 在Ollama中可用。", model=self.settings.ollama_embedding_model)

        except httpx.RequestError as e:
            raise ConnectionError(f"无法连接到Ollama服务: {self.settings.ollama_base_url}。请确保Ollama正在运行。") from e
        except Exception as e:
            raise RuntimeError(f"检查Ollama时发生未知错误: {e}") from e

    async def _create_and_persist_db(self) -> None:
        """
        从CSV加载文档，创建向量数据库并持久化到磁盘。
        """
        try:
            # 只加载videos数据
            documents = await asyncio.to_thread(load_documents_from_csvs, [self.settings.videos_data_path])

            if not documents:
                raise ValueError("从CSV加载的文档为空，无法创建数据库。")

            logger.info("加载 {num_docs} 个文档，正在创建向量嵌入...", num_docs=len(documents))

            create_db_call = functools.partial(
                Chroma.from_documents,
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=self.chroma_db_dir
            )
            self.vector_store = await asyncio.to_thread(create_db_call)

            logger.info("数据库已成功创建并保存在 '{db_dir}'。", db_dir=self.chroma_db_dir)
        except (FileNotFoundError, ValueError) as e:
            raise IOError(f"创建数据库失败: {e}") from e

    async def retrieve_context(self, query: str) -> list[Document]:
        """
        根据用户查询异步检索相关上下文。
        """
        if self.status != RAGStatus.READY:
            raise RuntimeError(f"RAG处理器未准备就绪，当前状态: {self.status}")
        logger.info("正在为查询检索上下文: '{query}'", query=query)
        docs = await self.retriever.ainvoke(query)
        logger.info("检索到 {num_docs} 个相关文档。", num_docs=len(docs))
        return docs

    async def refresh_database(self) -> bool:
        """
        刷新数据库，重新加载CSV数据并重建向量数据库。
        """
        logger.info("正在刷新RAG数据库...")
        try:
            db_dir = self.settings.chroma_db_dir
            if os.path.exists(db_dir):
                logger.info("正在删除旧的数据库 '{db_dir}'...", db_dir=db_dir)
                await asyncio.to_thread(shutil.rmtree, db_dir)

            self.status = RAGStatus.UNINITIALIZED
            await self.initialize()

            logger.info("RAG数据库刷新完成。")
            return True
        except Exception as e:
            logger.exception("刷新数据库失败: {error}", error=str(e))
            self.status = RAGStatus.ERROR
            self.error_message = str(e)
            return False

    async def close(self) -> None:
        logger.info("正在关闭RAG处理器资源...")
        await self._http_client.aclose()
        logger.info("HTTP客户端已关闭。")
