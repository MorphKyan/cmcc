import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.module.llm.modelscope_llm_handler import ModelScopeLLMHandler, STATIC_SYSTEM_PROMPT
from src.config.config import LLMSettings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

async def verify_handler():
    print("Starting verification of ModelScopeLLMHandler...")
    
    # 1. Setup Settings
    settings = LLMSettings()
    # Mock API key to avoid validation errors if it checks format
    settings.modelscope_api_key = "ms-mock-key" 
    
    # 2. Initialize Handler
    handler = ModelScopeLLMHandler(settings)
    
    # 3. Verify Static System Prompt in Template
    print("\n[Check 1] Verifying System Prompt...")
    system_message_prompt = handler.prompt_template.messages[0]
    if system_message_prompt.prompt.template == STATIC_SYSTEM_PROMPT:
        print("PASS: System prompt is static and matches the constant.")
    else:
        print("FAIL: System prompt does not match.")
        print(f"Expected: {STATIC_SYSTEM_PROMPT[:50]}...")
        print(f"Actual: {system_message_prompt.prompt.template[:50]}...")

    # 4. Verify Chain Construction and Input Preparation
    print("\n[Check 2] Verifying Chain Input...")
    
    # Mock the chain and model to avoid actual API calls
    handler.chain = AsyncMock()
    handler.chain.ainvoke.return_value = AIMessage(content="", tool_calls=[])
    
    # Mock helper methods to return simple JSON
    handler._get_json_info = MagicMock(return_value="[]")
    # handler._get_prompt_from_documents = MagicMock(return_value="[]")
    
    # Test Data
    user_input = "Test Input"
    rag_docs = []
    chat_history = [
        HumanMessage(content="1"), AIMessage(content="1"),
        HumanMessage(content="2"), AIMessage(content="2"),
        HumanMessage(content="3"), AIMessage(content="3"),
        HumanMessage(content="4"), AIMessage(content="4"),
        HumanMessage(content="5"), AIMessage(content="5"),
        HumanMessage(content="6"), AIMessage(content="6"), # Should be trimmed
    ]
    
    # Call get_response
    await handler.get_response(user_input, rag_docs, chat_history=chat_history)
    
    # Inspect arguments passed to chain.ainvoke
    call_args = handler.chain.ainvoke.call_args
    if call_args:
        chain_input = call_args[0][0]
        
        # Verify Context in User Input
        if "context" in chain_input:
            print("PASS: 'context' is present in chain input.")
            if "用户当前位置" in chain_input["context"]:
                print("PASS: Context contains dynamic info (User Location).")
            else:
                print("FAIL: Context missing dynamic info.")
        else:
            print("FAIL: 'context' missing from chain input.")
            
        # Verify Chat History passed raw (Trimmer handles it)
        if len(chain_input["chat_history"]) == 12:
             print("PASS: Full chat history passed to chain (Trimmer will handle it).")
        else:
             print(f"FAIL: Chat history length unexpected: {len(chain_input['chat_history'])}")

    else:
        print("FAIL: chain.ainvoke was not called.")

    # 5. Verify Trimmer Configuration (Static Check)
    # We can't easily inspect the constructed chain object structure at runtime without complex introspection,
    # but we can verify the code logic by running this script and ensuring no errors.
    # To truly verify trimmer, we would need to run the actual chain, but that requires a real model or a complex mock of the LCEL pipeline.
    # For now, we rely on the fact that we passed the history to the chain.
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_handler())
