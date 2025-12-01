# RAG Device Integration Testing Guide

This document outlines the steps to verify the integration of `devices.csv` into the RAG system.

## Prerequisites

1.  Ensure the virtual environment is activated.
2.  Ensure `data/devices.csv` exists and contains valid data.
3.  Ensure `src/config/config.py` has `devices_data_path` configured in `RAGSettings`.

## Testing Steps

### 1. Refresh RAG Database

The RAG database needs to be rebuilt to include the new device data. You can do this via the API or by restarting the application (if it refreshes on startup).

**Via API:**
```bash
curl -X POST http://localhost:5000/api/rag/refresh
```
Expected Output: `{"status": "success", "message": "RAG database refreshed successfully"}`

### 2. Verify Device Indexing

Create a temporary python script `verify_rag_devices.py` to check if devices are indexed:

```python
import asyncio
from src.config.config import get_settings
from src.module.rag.modelscope_rag_processor import ModelScopeRAGProcessor # Or OllamaRAGProcessor

async def verify():
    settings = get_settings()
    # Initialize appropriate processor based on your config
    processor = ModelScopeRAGProcessor(settings.rag) 
    await processor.initialize()
    
    # Query for a known device
    query = "主屏幕"
    docs = await processor.retrieve_context(query)
    
    print(f"Query: {query}")
    found = False
    for doc in docs:
        print(f"Document: {doc.metadata.get('name')} (Type: {doc.metadata.get('type')})")
        if doc.metadata.get('type') == 'device' or doc.metadata.get('type') == 'screen':
             if '主屏幕' in doc.page_content:
                 found = True
    
    if found:
        print("SUCCESS: Device '主屏幕' found in RAG context.")
    else:
        print("FAILURE: Device '主屏幕' NOT found in RAG context.")

    await processor.close()

if __name__ == "__main__":
    asyncio.run(verify())
```

Run the script:
```bash
python verify_rag_devices.py
```

### 3. Verify LLM Response (End-to-End)

Start the main application:
```bash
python main.py
```

Send a voice or text command asking about a device:
- "主屏幕是干什么的？"
- "5G体验区有哪些屏幕？"

Check the logs to see if the RAG context includes the device information and if the LLM uses it in its response (even if it just acknowledges it).

## Troubleshooting

- **Database not updating**: Check `chroma_db` directory permissions or try deleting the directory to force a full rebuild.
- **Import errors**: Ensure you are running python from the project root.
