#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
import os
from abc import ABC, abstractmethod
from enum import Enum

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger

from src.api.schemas import AreaItem, DeviceItem, DoorItem, MediaItem
from src.config.config import RAGSettings
from src.module.rag.helper import (
    convert_areas_to_documents,
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
    """RAG处理器基类，提供通用的初始化、检索和数据库操作方法。
    
    子类只需实现 `_create_embedding_model()` 和可选的 `_pre_initialize()` 方法。
    """
    
    def __init__(self, settings: RAGSettings) -> None:
        self.settings = settings
        self.chroma_db_dir = settings.chroma_db_dir
        self.vector_store: Chroma | None = None
        self.retriever = None
        self.embedding_model: Embeddings | None = None
        self.status = RAGStatus.UNINITIALIZED
        self.error_message: str | None = None
        self._init_lock = asyncio.Lock()
        logger.info("{class_name}已创建", class_name=self.__class__.__name__)

    @abstractmethod
    def _create_embedding_model(self) -> Embeddings:
        """创建embedding模型实例，由子类实现。
        
        Returns:
            配置好的Embeddings实例
        """
        pass

    async def _pre_initialize(self) -> None:
        """初始化前的准备工作，子类可重写。
        
        例如：检查服务连接、验证API密钥等。
        默认实现为空操作。
        """
        pass

    async def initialize(self) -> None:
        """初始化RAG处理器：执行预检查、加载模型、创建或加载数据库。
        
        此方法支持重新初始化，且线程安全。
        """
        async with self._init_lock:
            if self.status == RAGStatus.INITIALIZING:
                logger.warning("初始化已在进行中，请等待。")
                return
            self.status = RAGStatus.INITIALIZING
            self.error_message = None
            logger.info("开始初始化{class_name}...", class_name=self.__class__.__name__)

            try:
                # 子类可重写的预初始化钩子
                await self._pre_initialize()
                
                # 创建embedding模型
                self.embedding_model = self._create_embedding_model()
                
                # 加载或创建向量数据库
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

                # 创建检索器
                self.retriever = self.vector_store.as_retriever(
                    search_kwargs={"k": self.settings.top_k_results}
                )
                
                self.status = RAGStatus.READY
                self.error_message = None
                logger.success("{class_name}初始化完成，状态: READY。", 
                             class_name=self.__class__.__name__)
            except Exception as e:
                self.status = RAGStatus.ERROR
                self.error_message = f"{self.__class__.__name__}初始化失败: {str(e)}"
                logger.exception(self.error_message)
                raise

    async def retrieve_context(
        self,
        query: str,
        metadata_types: list[MetadataType] | None = None,
        top_k: int | None = None
    ) -> list[Document]:
        """根据用户查询异步检索相关上下文。
        
        Args:
            query: 查询文本
            metadata_types: 可选的元数据类型过滤列表，为None时检索所有类型
            top_k: 返回的文档数量，为None时使用配置默认值
            
        Returns:
            检索到的Document列表
            
        Raises:
            RuntimeError: 当处理器未准备就绪时
        """
        if self.status != RAGStatus.READY:
            raise RuntimeError(f"RAG处理器未准备就绪，当前状态: {self.status}")
        
        k = top_k if top_k is not None else self.settings.top_k_results
        logger.info("正在为查询检索上下文: '{query}', 类型过滤: {types}, top_k: {k}", 
                    query=query, types=metadata_types, k=k)
        
        if metadata_types is None:
            # 无过滤
            docs_with_scores = await self.vector_store.asimilarity_search_with_score(query, k=k)
        else:
            # 使用metadata过滤
            type_values = [t.value for t in metadata_types]
            filter_dict = {"type": {"$in": type_values}}
            docs_with_scores = await self.vector_store.asimilarity_search_with_score(
                query, k=k, filter=filter_dict
            )
        
        logger.info("检索到 {num_docs} 个相关文档。", num_docs=len(docs_with_scores))
        
        # 输出检索结果关键信息
        if docs_with_scores:
            logger.info("=" * 60)
            logger.info("  RAG检索结果详情")
            logger.info("  返回数量: {count}", count=len(docs_with_scores))
            logger.info("-" * 60)
            
            for idx, (doc, score) in enumerate(docs_with_scores, 1):
                metadata = doc.metadata
                doc_type = metadata.get("type", "unknown")
                doc_name = metadata.get("name", metadata.get("title", "未知"))
                content_preview = doc.page_content[:80] + "..." if len(doc.page_content) > 80 else doc.page_content
                # Chroma返回的是距离(distance)，越小越相似
                similarity_pct = (1 / (1 + score)) * 100
                
                logger.info(
                    "  [{idx}] {doc_type} | {name} | 相似度: {similarity:.1f}% (距离: {distance:.4f})",
                    idx=idx, doc_type=doc_type, name=doc_name,
                    similarity=similarity_pct, distance=score
                )
                logger.debug("      内容: {content}", content=content_preview)
                logger.debug("      元数据: {metadata}", metadata=metadata)
            
            logger.info("=" * 60)
        
        # 只返回文档，不返回得分
        docs = [doc for doc, _ in docs_with_scores]
        return docs

    @abstractmethod
    async def close(self) -> None:
        """关闭RAG处理器资源，由子类实现。"""
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

    async def batch_add_areas(self, items: list[AreaItem]) -> None:
        """批量添加区域数据"""
        if not items or self.vector_store is None:
            return
        documents = convert_areas_to_documents([item.model_dump() for item in items])
        await asyncio.to_thread(self.vector_store.add_documents, documents)
        logger.info("已添加 {count} 个区域文档", count=len(documents))

    async def delete_by_type(self, doc_type: str) -> None:
        """按类型删除文档，不影响其他类型的数据
        
        Args:
            doc_type: 文档类型，如 "door", "media", "device", "area"
        """
        if self.vector_store is None:
            logger.warning("向量存储未初始化，无法删除文档")
            return
        
        try:
            collection = self.vector_store._collection
            await asyncio.to_thread(
                collection.delete,
                where={"type": doc_type}
            )
            logger.info("已删除所有类型为 '{type}' 的文档", type=doc_type)
        except Exception as e:
            logger.exception("删除类型为 '{type}' 的文档失败: {error}", type=doc_type, error=str(e))
            raise
