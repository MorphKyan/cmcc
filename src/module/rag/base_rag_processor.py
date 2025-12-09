#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
from abc import ABC, abstractmethod
from enum import Enum

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger

from src.api.schemas import DeviceItem, DoorItem, MediaItem
from src.config.config import RAGSettings
from src.module.rag.helper import (
    convert_devices_to_documents,
    convert_doors_to_documents,
    convert_media_to_documents,
)
from src.services.data_service import DataService


class RAGStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class MetadataType(Enum):
    DOOR = "door"
    MEDIA = "media"
    DEVICE = "device"


class BaseRAGProcessor(ABC):
    def __init__(self, settings: RAGSettings) -> None:
        self.settings = settings
        self.chroma_db_dir = settings.chroma_db_dir
        self.vector_store: Chroma | None = None
        self.status = RAGStatus.UNINITIALIZED
        self.error_message: str | None = None
        self._init_lock = asyncio.Lock()
        logger.info("{class_name}已创建", class_name=self.__class__.__name__)

    @abstractmethod
    async def initialize(self) -> None:
        """初始化RAG处理器（幂等且线程安全）"""
        pass

    @abstractmethod
    async def retrieve_context(
        self,
        query: str,
        metadata_types: list[MetadataType] | None = None,
        top_k: int | None = None
    ) -> list[Document]:
        """根据查询检索相关上下文"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭RAG处理器资源"""
        pass

    def _load_all_documents(self) -> list[Document]:
        """从数据服务加载所有文档"""
        data_service = DataService()
        documents: list[Document] = []
        documents.extend(convert_doors_to_documents(data_service.get_all_doors_data()))
        documents.extend(convert_media_to_documents(data_service.get_all_media_data()))
        documents.extend(convert_devices_to_documents(data_service.get_all_devices_data()))

        if not documents:
            raise ValueError("从CSV加载的文档为空")

        logger.info("已加载 {num_docs} 个文档", num_docs=len(documents))
        return documents

    async def refresh_database(self) -> bool:
        """刷新数据库，重新加载CSV数据并重建向量数据库"""
        logger.info("正在刷新RAG数据库...")

        if self.vector_store is None:
            logger.error("向量存储未初始化")
            self.status = RAGStatus.ERROR
            self.error_message = "向量存储未初始化"
            return False

        try:
            self.status = RAGStatus.INITIALIZING
            await asyncio.to_thread(self.vector_store.reset_collection)
            documents = self._load_all_documents()
            await asyncio.to_thread(self.vector_store.add_documents, documents)
            self.status = RAGStatus.READY
            self.error_message = None
            logger.info("RAG数据库刷新完成")
            return True
        except Exception as e:
            logger.exception("刷新数据库失败: {error}", error=str(e))
            self.status = RAGStatus.ERROR
            self.error_message = str(e)
            return False

    async def _create_and_persist_db(self, embedding_model: Embeddings) -> None:
        """从CSV加载文档，创建向量数据库并持久化到磁盘"""
        try:
            documents = self._load_all_documents()
            logger.info("正在创建向量嵌入...")
            create_db_call = functools.partial(
                Chroma.from_documents,
                documents=documents,
                embedding=embedding_model,
                persist_directory=self.chroma_db_dir
            )
            self.vector_store = await asyncio.to_thread(create_db_call)
            logger.info("数据库已保存在 '{db_dir}'", db_dir=self.chroma_db_dir)
        except (FileNotFoundError, ValueError) as e:
            raise IOError(f"创建数据库失败: {e}") from e

    async def batch_add_doors(self, items: list[DoorItem]) -> None:
        """批量添加门数据"""
        if not items or self.vector_store is None:
            return
        documents = convert_doors_to_documents([item.model_dump() for item in items])
        await asyncio.to_thread(self.vector_store.add_documents, documents)
        logger.info("已添加 {count} 个门文档", count=len(documents))

    async def batch_add_media(self, items: list[MediaItem]) -> None:
        """批量添加媒体数据"""
        if not items or self.vector_store is None:
            return
        documents = convert_media_to_documents([item.model_dump() for item in items])
        await asyncio.to_thread(self.vector_store.add_documents, documents)
        logger.info("已添加 {count} 个媒体文档", count=len(documents))

    async def batch_add_devices(self, items: list[DeviceItem]) -> None:
        """批量添加设备数据"""
        if not items or self.vector_store is None:
            return
        documents = convert_devices_to_documents([item.model_dump() for item in items])
        await asyncio.to_thread(self.vector_store.add_documents, documents)
        logger.info("已添加 {count} 个设备文档", count=len(documents))
