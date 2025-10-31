#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
import os
import shutil
from enum import Enum
from typing import List, Optional

import requests
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from loguru import logger
from requests import ConnectionError, Timeout

from src.config.config import RAGSettings
from src.module.data_loader import load_documents_from_csvs


class RAGStatus(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"


class RAGProcessor:
    def __init__(self, settings: RAGSettings) -> None:
        """
        初始化RAG处理器。

        Args:
            settings (RAGSettings): RAG配置
        """
        self.settings = settings
        self.videos_data_path = settings.VIDEOS_DATA_PATH
        self.chroma_db_dir = settings.CHROMA_DB_DIR
        self.top_k_results = settings.TOP_K_RESULTS

        # 初始化状态和核心组件
        self.status = RAGStatus.UNINITIALIZED
        self.error_message: Optional[str] = None
        self.embedding_model: Optional[OllamaEmbeddings] = None
        self.vector_store: Optional[Chroma] = None
        self.retriever = None

        # 3. 使用asyncio.Lock来防止并发初始化
        self._init_lock = asyncio.Lock()
        logger.info("RAGProcessor已创建，状态: UNINITIALIZED。")

        self._check_ollama_connection()
        self.embedding_model = OllamaEmbeddings(
            model=self.settings.EMBEDDING_MODEL,
            base_url=self.settings.BASE_URL
        )
        if not os.path.exists(self.chroma_db_dir):
            logger.info("未找到本地向量数据库，正在创建...")
            self._create_and_persist_db()
        else:
            logger.info("正在从本地加载向量数据库...")
            self.vector_store = Chroma(
                persist_directory=self.chroma_db_dir,
                embedding_function=self.embedding_model
            )
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.top_k_results}
        )
        logger.info("RAG处理器初始化完成。")

    async def initialize(self) -> None:
        """
        执行耗时的初始化过程：检查连接、加载模型、创建或加载数据库。
        这个方法现在是异步的，并且会抛出异常而不是退出。
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
                    model=self.settings.EMBEDDING_MODEL,
                    base_url=self.settings.BASE_URL
                )
                # 步骤 3: 创建或加载向量数据库
                if not os.path.exists(self.chroma_db_dir):
                    logger.info("未找到本地向量数据库，正在创建...")
                    await self._create_and_persist_db()
                else:
                    logger.info("正在从本地加载向量数据库...")
                    self.vector_store = Chroma(
                        persist_directory=self.chroma_db_dir,
                        embedding_function=self.embedding_model
                    )

                # 步骤 4: 创建Retriever
                self.retriever = self.vector_store.as_retriever(
                    search_kwargs={"k": self.top_k_results}
                )
                self.status = RAGStatus.READY
                self.error_message = None
                logger.success("RAG处理器初始化完成，状态: READY。")
            except Exception as e:
                self.status = RAGStatus.ERROR
                self.error_message = f"RAG初始化失败: {e}"
                logger.exception(self.error_message)
                # 4. 向上抛出异常，让调用者知道失败了
                raise

    async def _check_ollama_connection(self) -> None:
        """
        检查与Ollama服务的连接和模型可用性。
        """
        logger.info("正在检查Ollama服务连接: {url}", url=self.settings.OLLAMA_BASE_URL)
        loop = asyncio.get_running_loop()
        available_models = await loop.run_in_executor(None, self._sync_check_connection)
        if self.settings.OLLAMA_EMBEDDING_MODEL not in available_models:
            error_msg = (
                f"Ollama服务中未找到所需模型: '{self.settings.OLLAMA_EMBEDDING_MODEL}'. "
                f"可用模型: {available_models}. "
                f"请先执行: ollama pull {self.settings.OLLAMA_EMBEDDING_MODEL}"
            )
            raise RuntimeError(error_msg)
        logger.info("所需Embedding模型 '{model}' 在Ollama中可用。", model=self.settings.OLLAMA_EMBEDDING_MODEL)

    def _sync_check_connection(self) -> List[str]:
        logger.info("正在线程池中执行同步的Ollama连接检查...")
        try:
            # 检查Ollama服务是否在线
            response = requests.get(self.settings.OLLAMA_BASE_URL, timeout=5)
            response.raise_for_status()
            # 检查所需模型是否已拉取
            api_url = f"{self.settings.OLLAMA_BASE_URL.strip('/')}/api/tags"
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()

            logger.info("Ollama服务连接成功。")
            return [m['name'] for m in response.json().get('models', [])]
        except (ConnectionError, Timeout) as e:
            raise ConnectionError(f"无法连接到Ollama服务: {self.settings.OLLAMA_BASE_URL}。请确保Ollama正在运行。") from e
        except Exception as e:
            raise RuntimeError(f"检查Ollama时发生未知错误: {e}") from e

    async def _create_and_persist_db(self) -> None:
        """
        从CSV加载文档，创建向量数据库并持久化到磁盘。
        """
        try:
            # 只加载videos数据
            data_paths = [self.videos_data_path]
            loop = asyncio.get_running_loop()
            documents = load_documents_from_csvs(data_paths)
            if not documents:
                raise ValueError("从CSV加载的文档为空，无法创建数据库。")
            logger.info("加载 {num_docs} 个文档，正在创建向量嵌入...", num_docs=len(documents))
            create_db_call = functools.partial(
                Chroma.from_documents,
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=self.chroma_db_dir
            )
            self.vector_store = await loop.run_in_executor(None, create_db_call)
            logger.info("数据库已成功创建并保存在 '{db_dir}'。", db_dir=self.chroma_db_dir)
        except (FileNotFoundError, IOError, ValueError) as e:
            raise IOError(f"创建数据库失败: {e}") from e

    def retrieve_context(self, query: str) -> List[Document]:
        """
        根据用户查询检索相关上下文。
        
        Args:
            query (str): 用户输入的文本。
            
        Returns:
            list[Document]: 检索到的相关Document对象列表。
        """
        logger.info("正在为查询检索上下文: '{query}'", query=query)
        docs = self.retriever.invoke(query)
        logger.info("检索到 {num_docs} 个相关文档。", num_docs=len(docs))
        # 打印检索到的内容，方便调试
        # for i, doc in enumerate(docs):
        #     logger.info("文档 {doc_num}:", doc_num=i+1)
        #     logger.info("  内容: {content}", content=doc.page_content)
        #     logger.info("  元数据: {metadata}", metadata=doc.metadata)
        return docs

    async def refresh_database(self) -> bool:
        """
        刷新数据库，重新加载CSV数据并重建向量数据库。
        """
        logger.info("正在刷新RAG数据库...")
        try:
            # 删除旧的数据库
            if os.path.exists(self.chroma_db_dir):
                logger.info("正在删除旧的数据库 '{db_dir}'...", db_dir=self.chroma_db_dir)
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, shutil.rmtree, self.chroma_db_dir)
            # 重新创建数据库
            await self.initialize()
            logger.info("RAG数据库刷新完成。")
            return True
        except Exception as e:
            logger.exception("刷新数据库失败: {error}", error=str(e))
            self.status = RAGStatus.ERROR
            self.error_message = str(e)
            return False
