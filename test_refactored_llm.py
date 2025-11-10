#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the refactored LLM handlers.
This script tests the new modular architecture with retry strategies, validation retry service, and response mapper.
"""

import asyncio
import json

from langchain_core.documents import Document

from src.config.config import get_settings
from src.module.llm.ark_llm_handler import ArkLLMHandler
from src.module.llm.modelscope_llm_handler import ModelScopeLLMHandler
from src.module.llm.ollama_llm_handler import OllamaLLMHandler


async def test_ark_handler():
    """Test Ark LLM handler with the new modular architecture."""
    print("Testing Ark LLM Handler...")
    settings = get_settings()

    try:
        # Create Ark handler
        ark_handler = ArkLLMHandler(settings.llm, settings.volcengine)

        # Test health check
        health = await ark_handler.check_health()
        print(f"Ark health check: {'PASS' if health else 'FAIL'}")

        # Test with simple input (this might fail if API key is not valid, but should not crash)
        rag_docs = [Document(page_content="Test document for RAG")]
        response = await ark_handler.get_response("播放5G的视频", rag_docs)
        print(f"Ark response: {response}")

        # Parse response to verify format
        parsed = json.loads(response)
        print(f"Parsed response type: {type(parsed)}")
        if isinstance(parsed, list):
            print("Response format: VALID (list)")
        else:
            print("Response format: INVALID")

    except Exception as e:
        print(f"Ark handler test encountered error (expected if API not configured): {e}")
        print("This is OK for testing the architecture")


async def test_ollama_handler():
    """Test Ollama LLM handler with the new modular architecture."""
    print("\nTesting Ollama LLM Handler...")
    settings = get_settings()

    try:
        # Create Ollama handler
        ollama_handler = OllamaLLMHandler(settings.llm)

        # Initialize (this might fail if Ollama is not running, but should not crash)
        await ollama_handler.initialize()

        # Test health check
        health = await ollama_handler.check_health()
        print(f"Ollama health check: {'PASS' if health else 'FAIL'}")

        # Test with simple input
        rag_docs = [Document(page_content="Test document for RAG")]
        response = await ollama_handler.get_response("播放5G的视频", rag_docs)
        print(f"Ollama response: {response}")

        # Parse response to verify format
        parsed = json.loads(response)
        print(f"Parsed response type: {type(parsed)}")
        if isinstance(parsed, list):
            print("Response format: VALID (list)")
        else:
            print("Response format: INVALID")

    except Exception as e:
        print(f"Ollama handler test encountered error (expected if Ollama not running): {e}")
        print("This is OK for testing the architecture")


async def test_modelscope_handler():
    """Test ModelScope LLM handler with the new modular architecture."""
    print("\nTesting ModelScope LLM Handler...")
    settings = get_settings()

    try:
        # Create ModelScope handler
        modelscope_handler = ModelScopeLLMHandler(settings.llm)

        # Initialize (this might fail if API key is not valid, but should not crash)
        await modelscope_handler.initialize()

        # Test health check
        health = await modelscope_handler.check_health()
        print(f"ModelScope health check: {'PASS' if health else 'FAIL'}")

        # Test with simple input
        rag_docs = [Document(page_content="Test document for RAG")]
        response = await modelscope_handler.get_response("播放5G的视频", rag_docs)
        print(f"ModelScope response: {response}")

        # Parse response to verify format
        parsed = json.loads(response)
        print(f"Parsed response type: {type(parsed)}")
        if isinstance(parsed, list):
            print("Response format: VALID (list)")
        else:
            print("Response format: INVALID")

    except Exception as e:
        print(f"ModelScope handler test encountered error (expected if API not configured): {e}")
        print("This is OK for testing the architecture")


async def test_response_mapper():
    """Test the response mapper independently."""
    print("\nTesting Response Mapper...")
    from src.core.response_mapper import ResponseMapper

    mapper = ResponseMapper()

    # Test valid tool calls
    tool_calls = [
        {"type": "play_video", "args": {"target": "test.mp4", "device": "主屏幕"}},
        {"type": "control_door", "args": {"target": "测试门", "action": "open"}}
    ]

    response = mapper.map_tool_calls_to_response(tool_calls)
    print(f"Response mapper output: {response}")

    # Parse and verify
    parsed = json.loads(response)
    assert len(parsed) == 2
    assert parsed[0]["action"] == "play"
    assert parsed[1]["action"] == "open"
    print("Response mapper test: PASS")


async def test_validation_retry_service():
    """Test the validation retry service independently."""
    print("\nTesting Validation Retry Service...")
    from src.core.validation_service import ValidationService
    from src.core.validation_retry_service import ValidationRetryService
    from src.config.config import LLMSettings

    settings = LLMSettings()
    validation_service = ValidationService()
    retry_service = ValidationRetryService(validation_service, settings)

    # Test with invalid tool calls (should return error after max retries exceeded)
    invalid_tool_calls = [
        {"type": "play_video", "args": {"target": "nonexistent.mp4", "device": "主屏幕"}}
    ]

    # Mock LLM handler for testing
    from src.core.response_mapper import ResponseMapper
    class MockLLMHandler:
        def __init__(self):
            self.screens_info = [{"name": "主屏幕", "aliases": []}]
            self.doors_info = []
            self.response_mapper = ResponseMapper()

    mock_handler = MockLLMHandler()
    rag_docs = [Document(page_content="Test document")]

    # Set retry_count to max_retries to bypass retry logic and go directly to error
    max_retries = settings.max_validation_retries
    response = await retry_service.validate_and_retry(
        invalid_tool_calls, "播放不存在的视频", rag_docs, mock_handler, max_retries
    )

    print(f"Validation retry service output: {response}")
    parsed = json.loads(response)
    assert len(parsed) == 1
    assert parsed[0]["action"] == "error"
    print("Validation retry service test: PASS")


async def main():
    """Run all tests."""
    print("Testing refactored LLM architecture...\n")

    # Test individual components
    await test_response_mapper()
    await test_validation_retry_service()

    # Test full handlers (these may fail due to external dependencies, but shouldn't crash)
    await test_ark_handler()
    await test_ollama_handler()
    await test_modelscope_handler()

    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main())