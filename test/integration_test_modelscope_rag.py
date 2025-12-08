import unittest
import asyncio
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.module.rag.modelscope_rag_processor import ModelScopeRAGProcessor, RAGStatus
from src.config.config import RAGSettings
from langchain_core.documents import Document

class TestModelScopeRAGIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Use real settings from config
        self.settings = RAGSettings()
        # Override any necessary settings here if needed
        
        self.processor = ModelScopeRAGProcessor(self.settings)

    async def asyncSetUp(self):
        # Initialize the processor with real ModelScope API
        await self.processor.initialize()
        self.assertEqual(self.processor.status, RAGStatus.READY, "Processor should be ready after initialization")

    async def asyncTearDown(self):
        # Close the processor
        await self.processor.close()

    async def test_integration_retrieve_context(self):
        """
        Integration test cases for ModelScope RAG Processor.
        These tests call the actual ModelScope API to retrieve context.
        """
        
        # Test cases based on data files: areas.csv, devices.csv, doors.csv, media.csv
        # 15 test cases covering different data types and query scenarios
        test_cases = [
            # Areas test cases
            {
                "query": "5G先锋体验区在哪里？",
                "description": "Query about area location",
                "expected_keywords": ["5G先锋体验区", "云游戏区", "VR体验区"]
            },
            {
                "query": "介绍一下智慧生活馆",
                "description": "Query about area introduction",
                "expected_keywords": ["智慧生活馆", "全屋智能", "智能家居"]
            },
            {
                "query": "未来科技赋能中心有什么？",
                "description": "Query about area features",
                "expected_keywords": ["未来科技赋能中心", "行业应用", "科技赋能"]
            },
            {
                "query": "数字服务互动站的功能是什么？",
                "description": "Query about area functions",
                "expected_keywords": ["数字服务互动站", "移动业务办理", "数字化服务"]
            },
            
            # Devices test cases
            {
                "query": "主屏幕在哪里？",
                "description": "Query about device location",
                "expected_keywords": ["主屏幕", "5G先锋体验区", "展厅正中央"]
            },
            {
                "query": "左侧互动大屏有什么功能？",
                "description": "Query about device functions",
                "expected_keywords": ["左侧互动大屏", "触摸互动", "业务查询"]
            },
            {
                "query": "云游戏体验屏参数如何？",
                "description": "Query about device specifications",
                "expected_keywords": ["云游戏体验屏", "高刷新率", "5G云游戏"]
            },
            {
                "query": "全屋智能中控屏怎么用？",
                "description": "Query about device usage",
                "expected_keywords": ["全屋智能中控屏", "智慧生活馆", "家庭控制中心"]
            },
            
            # Doors test cases
            {
                "query": "怎么去智慧生活馆？",
                "description": "Query about path to area",
                "expected_keywords": ["5G先锋体验区-智慧生活馆", "passage"]
            },
            {
                "query": "打开云游戏区安全门",
                "description": "Query about door operation",
                "expected_keywords": ["云游戏区安全门", "5G先锋体验区"]
            },
            {
                "query": "未来科技赋能中心主入口在哪里？",
                "description": "Query about entrance location",
                "expected_keywords": ["未来科技赋能中心主入口", "standalone"]
            },
            
            # Media test cases
            {
                "query": "播放5G技术总览视频",
                "description": "Query about specific video",
                "expected_keywords": ["5G技术总览", "中国移动5G演进之路"]
            },
            {
                "query": "我想看智慧家庭解决方案",
                "description": "Query about video category",
                "expected_keywords": ["智慧家庭解决方案", "全屋智能"]
            },
            {
                "query": "展示物联网应用案例",
                "description": "Query about video content",
                "expected_keywords": ["物联网应用案例", "智慧城市", "工业互联网"]
            },
            {
                "query": "5G-Advanced技术解析",
                "description": "Query about technical video",
                "expected_keywords": ["5G-Advanced技术解析", "5.5G网络", "技术突破"]
            }
        ]

        print(f"\nRunning {len(test_cases)} integration test cases...")
        
        for i, test_case in enumerate(test_cases, 1):
            # Rate limiting: 2s per request
            if i > 1:
                print("Waiting 2s for rate limiting...")
                await asyncio.sleep(2)

            with self.subTest(case=f"Case {i}: {test_case['description']}"):
                query = test_case["query"]
                expected_keywords = test_case["expected_keywords"]
                
                print(f"\n--- Test Case {i}: {test_case['description']} ---")
                print(f"Query: {query}")
                print(f"Expected keywords: {expected_keywords}")
                
                # Call actual retrieve_context method
                retrieved_docs = await self.processor.retrieve_context(query)
                
                # Verify results
                self.assertIsInstance(retrieved_docs, list, "Should return a list of documents")
                self.assertGreater(len(retrieved_docs), 0, "Should retrieve at least one document")
                
                # Combine all retrieved content for keyword checking
                all_content = " ".join([doc.page_content for doc in retrieved_docs])
                
                # Check if expected keywords are present
                found_keywords = [keyword for keyword in expected_keywords if keyword in all_content]
                print(f"Found keywords: {found_keywords}")
                print(f"Retrieved docs: {len(retrieved_docs)}")
                
                # For integration test, we expect at least 50% of expected keywords to be found
                self.assertGreaterEqual(len(found_keywords), len(expected_keywords) * 0.5, 
                                     f"Should find at least 50% of expected keywords. Expected: {expected_keywords}, Found: {found_keywords}")
                
                # Print the first document content for debugging
                if retrieved_docs:
                    print(f"First document: {retrieved_docs[0].page_content[:100]}...")

if __name__ == '__main__':
    unittest.main()
