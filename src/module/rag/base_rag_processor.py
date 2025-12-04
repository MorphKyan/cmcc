#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
from abc import ABC, abstractmethod
from enum import Enum

from langchain_chroma import Chroma
from langchain_core.documents import Document
from loguru import logger

from src.config.config import RAGSettings
from src.services.data_service import DataService


class RAGStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class BaseRAGProcessor(ABC):
    def __init__(self, settings: RAGSettings) -> None:
        """初始化RAG处理器基类。

        Args:
            settings: RAG配置
        """
        self.settings: RAGSettings = settings
        self.videos_data_path = settings.videos_data_path
        self.devices_data_path = settings.devices_data_path
        self.chroma_db_dir = settings.chroma_db_dir
        self.vector_store: Chroma | None = None
        self.retriever = None

        self.status = RAGStatus.UNINITIALIZED
        self.error_message: str | None = None

        self._init_lock = asyncio.Lock()
        logger.info(f"{self.__class__.__name__}已创建，状态: UNINITIALIZED。")

    @abstractmethod
    async def initialize(self) -> None:
        """初始化RAG处理器（幂等且线程安全）。"""
        pass

    @abstractmethod
    async def retrieve_context(self, query: str) -> list[Document]:
        """根据查询检索相关上下文。"""
        pass

    async def refresh_database(self) -> bool:
        """刷新数据库，重新加载CSV数据并重建向量数据库。"""
        logger.info("正在刷新RAG数据库...")
        try:
            self.status = RAGStatus.UNINITIALIZED
            self.vector_store.reset_collection()

            documents = await asyncio.to_thread(
                DataService().get_rag_documents
            )

            if not documents:
                raise ValueError("从CSV加载的文档为空，无法创建数据库。")

            logger.info("加载 {num_docs} 个文档，正在创建向量嵌入...", num_docs=len(documents))
            self.vector_store.add_documents(documents)

            self.status = RAGStatus.READY
            logger.info("RAG数据库刷新完成。")
            return True
        except Exception as e:
            logger.exception("刷新数据库失败: {error}", error=str(e))
            self.status = RAGStatus.ERROR
            self.error_message = str(e)
            return False

    @abstractmethod
    async def close(self) -> None:
        """
        关闭RAG处理器资源。
        """
        pass

    async def _create_and_persist_db(self, embedding_model) -> None:
        """
        从CSV加载文档，创建向量数据库并持久化到磁盘。
        """
        try:
            # 加载videos和devices数据
            documents = await asyncio.to_thread(
                DataService().get_rag_documents
            )

            if not documents:
                raise ValueError("从CSV加载的文档为空，无法创建数据库。")

            logger.info("加载 {num_docs} 个文档，正在创建向量嵌入...", num_docs=len(documents))

            create_db_call = functools.partial(
                Chroma.from_documents,
                documents=documents,
                embedding=embedding_model,
                persist_directory=self.chroma_db_dir
            )
            self.vector_store = await asyncio.to_thread(create_db_call)

            logger.info("数据库已成功创建并保存在 '{db_dir}'。", db_dir=self.chroma_db_dir)
        except (FileNotFoundError, ValueError) as e:
            raise IOError(f"创建数据库失败: {e}") from e
