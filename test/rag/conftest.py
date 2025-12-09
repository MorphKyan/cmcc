"""
Shared pytest fixtures for RAG processor integration tests.
"""
import os
import pytest
import pytest_asyncio
import tempfile
import shutil
import uuid

from src.config.config import RAGSettings
from src.module.rag.dashscope_rag_processor import DashScopeRAGProcessor


@pytest.fixture(scope="module")
def test_rag_settings():
    """Create RAG settings for testing with a non-existent database directory.
    
    The directory path is created but NOT the directory itself - this allows
    the RAG processor to detect it doesn't exist and create fresh DB from CSV data.
    """
    # Create a unique temp directory path that doesn't exist yet
    temp_base = tempfile.gettempdir()
    temp_dir = os.path.join(temp_base, f"rag_test_db_{uuid.uuid4().hex[:8]}")
    
    settings = RAGSettings(
        chroma_db_dir=temp_dir,
        top_k_results=5,
        provider="dashscope",
        dashscope_embedding_model=os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v3"),
        dashscope_base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", "sk-5d29b7ca2f074ffea3b7de63c9348ee5"),
    )
    
    yield settings
    
    # Cleanup: remove temporary directory if created
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            pass  # Ignore if DB is still locked


@pytest_asyncio.fixture(scope="module")
async def rag_processor(test_rag_settings):
    """Initialize a real RAG processor with test data."""
    processor = DashScopeRAGProcessor(test_rag_settings)
    await processor.initialize()
    
    yield processor
    
    await processor.close()


# Realistic human speech queries based on test data
DEVICE_QUERIES = [
    ("帮我打开主屏幕", "主屏幕"),
    ("我想看云游戏体验屏上播放的内容", "云游戏体验屏"),
    ("把右边屏幕打开", "右侧演示屏"),
]

VIDEO_QUERIES = [
    ("给我放一个关于5G的宣传视频", ["5G", "视频"]),
    ("我想看智慧家庭的介绍", ["智慧家庭", "智能家居"]),
    ("有没有人工智能方面的视频", ["人工智能", "AI"]),
]

DOOR_QUERIES = [
    ("智慧生活馆到数字服务互动站的门在哪", "智慧生活馆-数字服务互动站"),
    ("5G体验区入口怎么走", "5G先锋体验区主入口"),
]

COMBINED_QUERIES = [
    ("在行业应用全景屏上播放智慧城市的视频", ["行业应用全景屏", "智慧城市"]),
    ("未来科技赋能中心有哪些屏幕可以用", ["未来科技赋能中心", "屏幕"]),
]

