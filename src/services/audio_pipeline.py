import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from src.api.context import Context
from src.core import dependencies  # 从中心依赖文件导入全局处理器


async def run_vad_processor(context: Context):
    # ... VAD处理逻辑代码 ...
    print(f"[{context.context_id}] VAD处理器已启动。")
    # (将main.py中的代码复制到这里)


async def run_asr_processor(context: Context):
    # ... ASR处理逻辑代码 ...
    print(f"[{context.context_id}] ASR处理器已启动。")
    # (将main.py中的代码复制到这里，并使用 dependencies.asr_processor)


async def run_llm_rag_processor(context: Context):
    # ... LLM/RAG处理逻辑代码 ...
    print(f"[{context.context_id}] LLM/RAG处理器已启动。")
    # (将main.py中的代码复制到这里，并使用 dependencies.rag_processor 和 dependencies.llm_processor)
