#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from .data_loader import load_documents_from_csvs

class RAGProcessor:
    def __init__(self, screens_data_path, doors_data_path, videos_data_path, 
                 chroma_db_path, embedding_model, top_k_results, force_reload=False):
        """
        初始化RAG处理器。
        
        Args:
            screens_data_path (str): 屏幕数据CSV文件路径。
            doors_data_path (str): 门数据CSV文件路径。
            videos_data_path (str): 视频数据CSV文件路径。
            chroma_db_path (str): Chroma数据库存储路径。
            embedding_model (str): 嵌入模型名称。
            top_k_results (int): 检索返回的文档数量。
            force_reload (bool): 是否强制重新加载数据并重建数据库。
        """
        self.screens_data_path = screens_data_path
        self.doors_data_path = doors_data_path
        self.videos_data_path = videos_data_path
        self.chroma_db_path = chroma_db_path
        self.embedding_model_name = embedding_model
        self.top_k_results = top_k_results
        
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model)
        
        if force_reload and os.path.exists(chroma_db_path):
            print(f"强制重新加载：正在删除旧的数据库 '{chroma_db_path}'...")
            shutil.rmtree(chroma_db_path)
            
        if not os.path.exists(chroma_db_path):
            print("未找到本地向量数据库，正在创建...")
            self._create_and_persist_db()
        else:
            print("正在从本地加载向量数据库...")
            self.vector_store = Chroma(
                persist_directory=chroma_db_path,
                embedding_function=self.embedding_model
            )
        
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": top_k_results}
        )
        print("RAG处理器初始化完成。")

    def _create_and_persist_db(self):
        """
        从CSV加载文档，创建向量数据库并持久化到磁盘。
        """
        try:
            data_paths = [self.screens_data_path, self.doors_data_path, self.videos_data_path]
            documents = load_documents_from_csvs(data_paths)
            if not documents:
                raise ValueError("从CSV加载的文档为空，无法创建数据库。")
            
            print(f"成功加载 {len(documents)} 个文档，正在创建向量嵌入...")
            
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=self.chroma_db_path
            )
            print(f"数据库已成功创建并保存在 '{self.chroma_db_path}'。")
            
        except (FileNotFoundError, IOError, ValueError) as e:
            print(f"[错误] 创建数据库失败: {e}")
            # 如果创建失败，则退出程序，因为后续流程无法进行
            exit(1)

    def retrieve_context(self, query):
        """
        根据用户查询检索相关上下文。
        
        Args:
            query (str): 用户输入的文本。
            
        Returns:
            list[Document]: 检索到的相关Document对象列表。
        """
        print(f"正在为查询检索上下文: '{query}'")
        docs = self.retriever.invoke(query)
        print(f"检索到 {len(docs)} 个相关文档。")
        return docs
