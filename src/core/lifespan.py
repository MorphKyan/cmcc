from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core import dependencies
from src.module.rag.rag_processor import RAGProcessor
from src.module.asr.asr_processor import ASRProcessor
from src.module.llm.ollama_llm_handler import OllamaLLMHandler
from src.config.config import settings
from src.module.vad.vad_core import VADCore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 应用启动时执行 ---
    print("应用启动... 正在初始化处理器...")

    vad_config = settings.vad
    asr_config = settings.asr
    rag_config = settings.rag
    llm_config = settings.llm

    try:
        dependencies.vad_core = VADCore(vad_config)
        # dependencies.rag_processor = RAGProcessor(rag_config)
        # dependencies.asr_processor = ASRProcessor(asr_config, device="auto")
        # dependencies.llm_processor = OllamaLLMHandler(llm_config)
        print("所有处理器初始化成功。")
    except Exception as e:
        print(f"错误: 处理器初始化失败: {e}")
        # 在这里可以选择是否要阻止应用启动

    yield  # lifespan的核心，yield之前是启动逻辑，之后是关闭逻辑

    # --- 应用关闭时执行 ---
    print("应用关闭... 正在清理资源...")
    dependencies.active_contexts.clear()
    print("资源清理完毕。")
