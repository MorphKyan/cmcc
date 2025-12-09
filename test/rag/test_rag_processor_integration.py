"""
Integration tests for RAG processor with realistic human speech queries.

These tests verify the RAG processor retrieval functionality based on the
actual document flow in audio_pipeline.py.
"""
import pytest

from src.module.rag.base_rag_processor import MetadataType, RAGStatus
from .conftest import DEVICE_QUERIES, VIDEO_QUERIES, DOOR_QUERIES, COMBINED_QUERIES


@pytest.mark.asyncio
class TestDeviceRetrieval:
    """Test device document retrieval with human speech queries."""

    @pytest.mark.parametrize("query,expected_keyword", DEVICE_QUERIES)
    async def test_query_device(self, rag_processor, query, expected_keyword):
        """Test: {query}"""
        docs = await rag_processor.retrieve_context(
            query, 
            metadata_types=[MetadataType.DEVICE],
            top_k=5
        )
        
        assert len(docs) > 0, f"Should retrieve at least one device for: {query}"
        
        # Check if expected keyword appears in any returned document
        found = any(
            expected_keyword in doc.page_content or 
            expected_keyword in str(doc.metadata)
            for doc in docs
        )
        assert found, f"Expected '{expected_keyword}' in results for query: {query}"


@pytest.mark.asyncio
class TestVideoRetrieval:
    """Test video/media document retrieval with human speech queries."""

    @pytest.mark.parametrize("query,expected_keywords", VIDEO_QUERIES)
    async def test_query_video(self, rag_processor, query, expected_keywords):
        """Test: {query}"""
        docs = await rag_processor.retrieve_context(
            query,
            metadata_types=[MetadataType.MEDIA],
            top_k=5
        )
        
        assert len(docs) > 0, f"Should retrieve at least one video for: {query}"
        
        # Check if any expected keyword appears in results
        all_content = " ".join([doc.page_content + str(doc.metadata) for doc in docs])
        found = any(kw in all_content for kw in expected_keywords)
        assert found, f"Expected one of {expected_keywords} in results for query: {query}"


@pytest.mark.asyncio
class TestDoorRetrieval:
    """Test door document retrieval with human speech queries."""

    @pytest.mark.parametrize("query,expected_keyword", DOOR_QUERIES)
    async def test_query_door(self, rag_processor, query, expected_keyword):
        """Test: {query}"""
        docs = await rag_processor.retrieve_context(
            query,
            metadata_types=[MetadataType.DOOR],
            top_k=5
        )
        
        assert len(docs) > 0, f"Should retrieve at least one door for: {query}"
        
        # Check if expected keyword appears in any returned document
        found = any(
            expected_keyword in doc.page_content or 
            expected_keyword in str(doc.metadata)
            for doc in docs
        )
        assert found, f"Expected '{expected_keyword}' in results for query: {query}"


@pytest.mark.asyncio
class TestCombinedQuery:
    """Test combined queries that should retrieve multiple types of documents."""

    @pytest.mark.parametrize("query,expected_keywords", COMBINED_QUERIES)
    async def test_combined_query(self, rag_processor, query, expected_keywords):
        """Test: {query}"""
        # Retrieve all types like audio_pipeline.py does
        door_docs = await rag_processor.retrieve_context(
            query, metadata_types=[MetadataType.DOOR], top_k=5
        )
        device_docs = await rag_processor.retrieve_context(
            query, metadata_types=[MetadataType.DEVICE], top_k=5
        )
        video_docs = await rag_processor.retrieve_context(
            query, metadata_types=[MetadataType.MEDIA], top_k=5
        )
        
        all_docs = door_docs + device_docs + video_docs
        assert len(all_docs) > 0, f"Should retrieve at least one document for: {query}"
        
        # Check if any expected keyword appears in results
        all_content = " ".join([doc.page_content + str(doc.metadata) for doc in all_docs])
        found = any(kw in all_content for kw in expected_keywords)
        assert found, f"Expected one of {expected_keywords} in results for query: {query}"


@pytest.mark.asyncio
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    async def test_empty_query(self, rag_processor):
        """Test handling of empty query string."""
        docs = await rag_processor.retrieve_context(
            "",
            metadata_types=[MetadataType.DEVICE],
            top_k=5
        )
        # Empty query may return results based on embedding behavior
        # Just verify no exception is raised
        assert isinstance(docs, list)

    async def test_query_no_match(self, rag_processor):
        """Test: 播放火星探索视频 (non-existent content)."""
        docs = await rag_processor.retrieve_context(
            "播放火星探索视频",
            metadata_types=[MetadataType.MEDIA],
            top_k=5
        )
        # RAG will still return results, but they may not be highly relevant
        # This tests that the system doesn't crash on unmatched queries
        assert isinstance(docs, list)


@pytest.mark.asyncio
class TestRAGProcessorStatus:
    """Test RAG processor status and initialization."""

    async def test_processor_ready(self, rag_processor):
        """Test that processor is in READY status after initialization."""
        assert rag_processor.status == RAGStatus.READY
        assert rag_processor.error_message is None
        assert rag_processor.vector_store is not None
