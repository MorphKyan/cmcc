import sys
import os
import unittest
import shutil

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.component.rag_processor import RAGProcessor
from src.config import CHROMA_DB_PATH

class TestRAGProcessor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """在所有测试开始前，清理旧的数据库（如果存在）"""
        if os.path.exists(CHROMA_DB_PATH):
            shutil.rmtree(CHROMA_DB_PATH)

    @classmethod
    def tearDownClass(cls):
        """在所有测试结束后，再次清理数据库"""
        if os.path.exists(CHROMA_DB_PATH):
            shutil.rmtree(CHROMA_DB_PATH)

    def test_1_initialization_and_creation(self):
        """
        测试RAG处理器的第一次初始化，这应该会创建数据库。
        """
        print("\n--- 测试RAG处理器：数据库创建 ---")
        # 使用 force_reload=True 来确保数据库被创建
        rag_processor = RAGProcessor(force_reload=True)
        self.assertTrue(os.path.exists(CHROMA_DB_PATH), "数据库目录应已创建")
        print("--- 数据库创建测试完成 ---")

    def test_2_loading_from_existing_db(self):
        """
        测试RAG处理器从现有数据库加载。
        """
        print("\n--- 测试RAG处理器：从本地加载 ---")
        # 确保数据库存在
        if not os.path.exists(CHROMA_DB_PATH):
            RAGProcessor(force_reload=True)
            
        rag_processor_load = RAGProcessor()
        self.assertIsNotNone(rag_processor_load.vector_store, "向量存储应已加载")
        print("--- 从本地加载测试完成 ---")

    def test_3_retrieval_functionality(self):
        """
        测试RAG处理器的检索功能。
        """
        print("\n--- 测试RAG处理器：检索功能 ---")
        rag_processor = RAGProcessor() # 加载现有DB

        # 测试查询1
        test_query_1 = "我想看关于5G的视频"
        retrieved_docs_1 = rag_processor.retrieve_context(test_query_1)
        self.assertIsInstance(retrieved_docs_1, list, "检索结果应为列表")
        self.assertTrue(len(retrieved_docs_1) > 0, "对于查询1，应至少检索到一个文档")
        print(f"查询 '{test_query_1}' 检索到 {len(retrieved_docs_1)} 个文档。")
        # 简单的内容检查
        self.assertIn("video", retrieved_docs_1.metadata.get("type", ""), "检索到的文档类型应为video")

        # 测试查询2
        test_query_2 = "打开智能家居区的门"
        retrieved_docs_2 = rag_processor.retrieve_context(test_query_2)
        self.assertIsInstance(retrieved_docs_2, list)
        self.assertTrue(len(retrieved_docs_2) > 0, "对于查询2，应至少检索到一个文档")
        print(f"查询 '{test_query_2}' 检索到 {len(retrieved_docs_2)} 个文档。")
        self.assertIn("door", retrieved_docs_2.metadata.get("type", ""), "检索到的文档类型应为door")
        
        print("--- 检索功能测试完成 ---")

if __name__ == '__main__':
    unittest.main()
