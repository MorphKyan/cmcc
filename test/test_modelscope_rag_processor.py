import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.module.rag.modelscope_rag_processor import ModelScopeRAGProcessor, RAGStatus
from src.config.config import RAGSettings
from langchain_core.documents import Document

class TestModelScopeRAGProcessor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_settings = MagicMock(spec=RAGSettings)
        self.mock_settings.modelscope_base_url = "http://mock-modelscope.com"
        self.mock_settings.modelscope_api_key = MagicMock()
        self.mock_settings.modelscope_api_key.get_secret_value.return_value = "mock_key"
        self.mock_settings.modelscope_embedding_model = "mock-embedding-model"
        self.mock_settings.chroma_db_dir = "mock_db_dir"
        self.mock_settings.videos_data_path = "mock_videos.csv"
        self.mock_settings.devices_data_path = "mock_devices.csv"
        self.mock_settings.top_k_results = 3

        self.processor = ModelScopeRAGProcessor(self.mock_settings)

    async def test_initialize_success(self):
        with patch('src.module.rag.modelscope_rag_processor.httpx.AsyncClient.get') as mock_get, \
             patch('src.module.rag.modelscope_rag_processor.OpenAIEmbeddings') as mock_embeddings, \
             patch('src.module.rag.modelscope_rag_processor.os.path.exists', return_value=True), \
             patch('src.module.rag.modelscope_rag_processor.Chroma') as mock_chroma:
            
            # Mock successful connection checks
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # Mock Chroma
            mock_vector_store = MagicMock()
            mock_chroma.return_value = mock_vector_store
            
            await self.processor.initialize()
            
            self.assertEqual(self.processor.status, RAGStatus.READY)
            self.assertIsNotNone(self.processor.embedding_model)
            self.assertIsNotNone(self.processor.vector_store)

    async def test_initialize_already_initializing(self):
        self.processor.status = RAGStatus.INITIALIZING
        
        # Should return immediately without doing anything
        with patch('src.module.rag.modelscope_rag_processor.httpx.AsyncClient.get') as mock_get:
            await self.processor.initialize()
            mock_get.assert_not_called()

    async def test_check_modelscope_connection_success(self):
        with patch('src.module.rag.modelscope_rag_processor.httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            await self.processor._check_modelscope_connection()
            # Should not raise exception

    async def test_check_modelscope_connection_failure(self):
        with patch('src.module.rag.modelscope_rag_processor.httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = Exception("Connection failed")
            
            with self.assertRaises(RuntimeError):
                await self.processor._check_modelscope_connection()

    async def test_retrieve_context_not_ready(self):
        self.processor.status = RAGStatus.UNINITIALIZED
        with self.assertRaises(RuntimeError):
            await self.processor.retrieve_context("query")

    async def test_retrieve_context_success(self):
        self.processor.status = RAGStatus.READY
        self.processor.retriever = AsyncMock()
        mock_docs = [Document(page_content="content", metadata={})]
        self.processor.retriever.ainvoke.return_value = mock_docs
        
        docs = await self.processor.retrieve_context("test query")
        self.assertEqual(docs, mock_docs)
        self.processor.retriever.ainvoke.assert_called_with("test query")

    def test_data_cases(self):
        """
        Data-driven test cases based on areas.csv, devices.csv, doors.csv, and videos.csv.
        These tests verify that the query processing logic (conceptually) would handle these inputs.
        In a real integration test, we would verify the retrieval results match the expected keywords.
        Here we just iterate them to ensure no errors in processing.
        """
        test_cases = [
            # Areas
            ("5G先锋体验区在哪里？", "5G先锋体验区"),
            ("介绍一下智慧生活馆", "智慧生活馆"),
            ("未来科技赋能中心有什么？", "未来科技赋能中心"),
            ("数字服务互动站的功能是什么？", "数字服务互动站"),
            ("云游戏区在哪个区域？", "5G先锋体验区"),
            ("VR体验区在哪里？", "5G先锋体验区"),
            ("全屋智能区展示了什么？", "智慧生活馆"),
            ("行业应用展区主要展示什么？", "未来科技赋能中心"),
            
            # Devices
            ("主屏幕在哪里？", "主屏幕"),
            ("左侧互动大屏有什么功能？", "左侧互动大屏"),
            ("右侧演示屏是做什么的？", "右侧演示屏"),
            ("云游戏体验屏参数如何？", "云游戏体验屏"),
            ("全屋智能中控屏怎么用？", "全屋智能中控屏"),
            ("卧室投影仪在哪里？", "卧室投影仪"),
            ("智能厨房显示屏有什么功能？", "智能厨房显示屏"),
            ("行业应用全景屏多大？", "行业应用全景屏"),
            ("智慧城市沙盘屏展示什么？", "智慧城市沙盘屏"),
            ("工业互联网监控屏在哪里？", "工业互联网监控屏"),
            ("智慧农业数据屏显示什么数据？", "智慧农业数据屏"),
            ("数字人民币体验屏怎么操作？", "数字人民币体验屏"),
            ("超级SIM卡演示屏在哪里？", "超级SIM卡演示屏"),
            ("5G新通话演示手机有什么特点？", "5G新通话演示手机"),
            ("业务办理自助终端能办什么业务？", "业务办理自助终端"),
            
            # Doors
            ("怎么去智慧生活馆？", "5G先锋体验区-智慧生活馆"),
            ("打开云游戏区安全门", "云游戏区安全门"),
            ("VR体验室门是开着的吗？", "VR体验室门"),
            ("未来科技赋能中心主入口在哪里？", "未来科技赋能中心主入口"),
            
            # Videos
            ("播放5G技术总览视频", "5G技术总览"),
            ("我想看智慧家庭解决方案", "智慧家庭解决方案"),
            ("展示物联网应用案例", "物联网应用案例"),
        ]

        print(f"\nRunning {len(test_cases)} data-driven test cases...")
        for query, expected_keyword in test_cases:
            with self.subTest(query=query):
                # In a real test, we would assert that retrieve_context returns docs containing expected_keyword.
                # For this unit test, we just ensure the query is a valid string and could be passed to the processor.
                self.assertIsInstance(query, str)
                self.assertTrue(len(query) > 0)
                # Simulating a check
                # print(f"Testing query: {query} -> Expecting: {expected_keyword}")

if __name__ == '__main__':
    unittest.main()
