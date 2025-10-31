#!/usr/bin/env python3

# -*- coding: utf-8 -*-

import os
import shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from loguru import logger

from src.config.config import RAGSettings
from src.module.data_loader import load_documents_from_csvs
from langchain_core.documents import Document


class RAGProcessor:
    def __init__(self, settings: RAGSettings) -> None:
        """
        初始化RAG处理器。

        Args:
            settings (RAGSettings): RAG配置
        """
        self.videos_data_path = settings.VIDEOS_DATA_PATH
        self.chroma_db_dir = settings.CHROMA_DB_DIR
        self.top_k_results = settings.TOP_K_RESULTS
        self.embedding_model = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
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

    def _create_and_persist_db(self) -> None:
        """
        从CSV加载文档，创建向量数据库并持久化到磁盘。
        """
        try:
            # 只加载videos数据
            data_paths = [self.videos_data_path]
            documents = load_documents_from_csvs(data_paths)
            if not documents:
                raise ValueError("从CSV加载的文档为空，无法创建数据库。")
            logger.info("加载 {num_docs} 个文档，正在创建向量嵌入...", num_docs=len(documents))
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=self.chroma_db_dir
            )
            logger.info("数据库已成功创建并保存在 '{db_dir}'。", db_dir=self.chroma_db_dir)
        except (FileNotFoundError, IOError, ValueError) as e:
            logger.exception("创建数据库失败: {error}", error=str(e))
            exit(1)

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

    def refresh_database(self) -> bool:
        """
        刷新数据库，重新加载CSV数据并重建向量数据库。
        """
        logger.info("正在刷新RAG数据库...")
        try:
            # 删除旧的数据库
            if os.path.exists(self.chroma_db_dir):
                logger.info("正在删除旧的数据库 '{db_dir}'...", db_dir=self.chroma_db_dir)
                shutil.rmtree(self.chroma_db_dir)
            # 重新创建数据库
            logger.info("正在重新创建数据库...")
            self._create_and_persist_db()
            # 重新初始化retriever
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": self.top_k_results}
            )
            logger.info("RAG数据库刷新完成。")
            return True
        except Exception as e:
            logger.exception("刷新数据库失败: {error}", error=str(e))
            return False
