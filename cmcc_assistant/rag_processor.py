#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from langchain.vectorstores import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from cmcc_assistant.data_loader import load_documents_from_excel
from cmcc_assistant.config import (
    EXCEL_DATA_PATH, 
    CHROMA_DB_PATH, 
    EMBEDDING_MODEL,
    TOP_K_RESULTS
)

class RAGProcessor:
    def __init__(self, force_reload=False):
        """
        初始化RAG处理器。
        
        Args:
            force_reload (bool): 是否强制重新加载数据并重建数据库。
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        if force_reload and os.path.exists(CHROMA_DB_PATH):
            print(f"强制重新加载：正在删除旧的数据库 '{CHROMA_DB_PATH}'...")
            shutil.rmtree(CHROMA_DB_PATH)
            
        if not os.path.exists(CHROMA_DB_PATH):
            print("未找到本地向量数据库，正在创建...")
            self._create_and_persist_db()
        else:
            print("正在从本地加载向量数据库...")
            self.vector_store = Chroma(
                persist_directory=CHROMA_DB_PATH,
                embedding_function=self.embedding_model
            )
        
        self.retriever = self.vector_store.as_retriever(
            search_kwargs={"k": TOP_K_RESULTS}
        )
        print("RAG处理器初始化完成。")

    def _create_and_persist_db(self):
        """
        从Excel加载文档，创建向量数据库并持久化到磁盘。
        """
        try:
            documents = load_documents_from_excel(EXCEL_DATA_PATH)
            if not documents:
                raise ValueError("从Excel加载的文档为空，无法创建数据库。")
            
            print(f"成功加载 {len(documents)} 个文档，正在创建向量嵌入...")
            
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=CHROMA_DB_PATH
            )
            print(f"数据库已成功创建并保存在 '{CHROMA_DB_PATH}'。")
            
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
        docs = self.retriever.get_relevant_documents(query)
        print(f"检索到 {len(docs)} 个相关文档。")
        return docs

if __name__ == '__main__':
    # 测试代码
    print("--- 测试RAG处理器 ---")
    
    # 第一次初始化，应该会创建数据库
    print("\n[1] 第一次初始化（或强制重新加载）...")
    rag_processor = RAGProcessor(force_reload=True)
    
    # 第二次初始化，应该会从本地加载
    print("\n[2] 第二次初始化（从本地加载）...")
    rag_processor_load = RAGProcessor()

    # 测试检索功能
    print("\n[3] 测试检索功能...")
    test_query_1 = "我想看关于5G的视频"
    retrieved_docs_1 = rag_processor.retrieve_context(test_query_1)
    for i, doc in enumerate(retrieved_docs_1):
        print(f"  文档 {i+1}: {doc.page_content}")
        print(f"  元数据: {doc.metadata}\n")

    test_query_2 = "打开智能家居区的门"
    retrieved_docs_2 = rag_processor.retrieve_context(test_query_2)
    for i, doc in enumerate(retrieved_docs_2):
        print(f"  文档 {i+1}: {doc.page_content}")
        print(f"  元数据: {doc.metadata}\n")
        
    print("--- RAG处理器测试完成 ---")
