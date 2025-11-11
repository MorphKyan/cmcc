#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from langchain_core.documents import Document
from loguru import logger

from src.config.config import RAGSettings


class RAGStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class BaseRAGProcessor(ABC):
    def __init__(self, settings: RAGSettings) -> None:
        """
        初始化RAG处理器基类。

        Args:
            settings (RAGSettings): RAG配置
        """
        self.settings: RAGSettings = settings
        self.videos_data_path = settings.videos_data_path
        self.chroma_db_dir = settings.chroma_db_dir

        # 初始化状态和核心组件
        self.status = RAGStatus.UNINITIALIZED
        self.error_message: Optional[str] = None

        # 使用asyncio.Lock来防止并发初始化
        self._init_lock = asyncio.Lock()
        logger.info(f"{self.__class__.__name__}已创建，状态: UNINITIALIZED。")

    @abstractmethod
    async def initialize(self) -> None:
        """
        执行耗时的初始化过程：检查连接、加载模型、创建或加载数据库。
        此方法是幂等的，并且是线程安全的。
        """
        pass

    @abstractmethod
    async def retrieve_context(self, query: str) -> List[Document]:
        """
        根据用户查询异步检索相关上下文。
        """
        pass

    @abstractmethod
    async def refresh_database(self) -> bool:
        """
        刷新数据库，重新加载CSV数据并重建向量数据库。
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        关闭RAG处理器资源。
        """
        pass
