
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock dependencies before importing service
from src.core import dependencies
from src.module.llm.tool.definitions import ExhibitionCommand, CommandAction
from langchain_core.messages import AIMessage

# Mock DataService
dependencies.data_service = MagicMock()
dependencies.data_service.get_device_info.return_value = {"area": "TestArea", "type": "light"}

# Mock VADCore (needed for Context init)
dependencies.vad_core = MagicMock()

# Mock RAGProcessor
dependencies.rag_processor = AsyncMock()
dependencies.rag_processor.settings = MagicMock()
dependencies.rag_processor.settings.door_top_k = 1
dependencies.rag_processor.settings.media_top_k = 1
dependencies.rag_processor.settings.device_top_k = 1
dependencies.rag_processor.retrieve_context.return_value = [] # Return empty list for docs

# Mock LLMProcessor
dependencies.llm_processor = AsyncMock()
dependencies.llm_processor.get_response_with_retries.return_value = (
    AIMessage(content="Test Response"),
    [ExhibitionCommand(action="update_location", params="NewLocation", device_name="system")],
    []
)

# Mock Active Contexts
dependencies.active_contexts = {}

# Import Service
from src.services.text_pipeline import TextPipelineService
from src.api.context import Context

async def test_pipeline():
    print("Testing TextPipelineService...")
    
    # 1. Test process_text
    print("Input: 'Test Command'")
    result = await TextPipelineService.process_text("Test Command", client_id="test_pipeline")
    
    print("Result:", result)
    
    # Assertions
    assert result["success"] is True
    assert result["ai_response"] == "Test Response"
    assert len(result["commands"]) == 1
    assert result["commands"][0]["action"] == "update_location"
    assert result["results"][0]["success"] is True
    
    # Verify Context was created
    assert "test_pipeline" in dependencies.active_contexts
    ctx = dependencies.active_contexts["test_pipeline"]
    assert isinstance(ctx, Context)
    
    print("Verification Passed!")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_pipeline())
