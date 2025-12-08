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
from src.module.rag.helper import convert_doors_to_documents, convert_media_to_documents, convert_devices_to_documents
from src.api.schemas import DoorItem, MediaItem, DeviceItem


class RAGStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class MetadataType(Enum):
    """RAG文档的元数据类型"""
    DOOR = "door"
    MEDIA = "media"
    DEVICE = "device"


class BaseRAGProcessor(ABC):
    def __init__(self, settings: RAGSettings) -> None:
        """初始化RAG处理器基类。

        Args:
            settings: RAG配置
        """
        self.settings: RAGSettings = settings
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
    async def retrieve_context(
        self, 
        query: str, 
        metadata_types: list[MetadataType] | None = None,
        top_k: int | None = None
    ) -> list[Document]:
        """根据查询检索相关上下文。
        
        Args:
            query: 查询文本
            metadata_types: 可选的元数据类型过滤列表，为None时检索所有类型
            top_k: 返回的文档数量，为None时使用配置默认值
        """
        pass

    async def refresh_database(self) -> bool:
        """刷新数据库，重新加载CSV数据并重建向量数据库。"""
        logger.info("正在刷新RAG数据库...")
        try:
            self.status = RAGStatus.UNINITIALIZED
            self.vector_store.reset_collection()

            data_service = DataService()
            doors_data = data_service.get_all_doors_data()
            media_data = data_service.get_all_media_data()
            devices_data = data_service.get_all_devices_data()

            documents = []
            documents.extend(convert_doors_to_documents(doors_data))
            documents.extend(convert_media_to_documents(media_data))
            documents.extend(convert_devices_to_documents(devices_data))

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
            # 加载media和devices数据
            data_service = DataService()
            doors_data = data_service.get_all_doors_data()
            media_data = data_service.get_all_media_data()
            devices_data = data_service.get_all_devices_data()

            documents = []
            documents.extend(convert_doors_to_documents(doors_data))
            documents.extend(convert_media_to_documents(media_data))
            documents.extend(convert_devices_to_documents(devices_data))

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

    async def batch_add_doors(self, items: list[DoorItem]) -> None:
        """批量添加门数据并更新向量数据库"""
        new_doors_data = [item.model_dump() for item in items]
        documents = convert_doors_to_documents(new_doors_data)
        if self.vector_store:
            self.vector_store.add_documents(documents)
            logger.info(f"已向向量数据库添加 {len(documents)} 个门文档")

    async def batch_add_media(self, items: list[MediaItem]) -> None:
        """批量添加媒体数据并更新向量数据库"""
        new_media_data = [item.model_dump() for item in items]
        documents = convert_media_to_documents(new_media_data)
        if self.vector_store:
            self.vector_store.add_documents(documents)
            logger.info(f"已向向量数据库添加 {len(documents)} 个媒体文档")

    async def batch_add_devices(self, items: list[DeviceItem]) -> None:
        """批量添加设备数据并更新向量数据库"""
        new_devices_data = [item.model_dump() for item in items]
        documents = convert_devices_to_documents(new_devices_data)
        if self.vector_store:
            self.vector_store.add_documents(documents)
            logger.info(f"已向向量数据库添加 {len(documents)} 个设备文档")
