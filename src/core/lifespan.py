import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.config.config import get_settings
from src.core import dependencies
from src.core.feature_flags import FeatureFlags
from src.module.asr.asr_processor import ASRProcessor
from src.module.vad.vad_core import VADCore
from src.services.data_service import DataService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 应用启动时执行 ---
    logger.info("应用启动... 正在初始化处理器...")

    # 记录功能开关状态
    FeatureFlags.log_feature_status()

    settings = get_settings()
    vad_config = settings.vad
    asr_config = settings.asr
    rag_config = settings.rag
    llm_config = settings.llm

    try:
        dependencies.data_service = DataService()
        dependencies.vad_core = VADCore(vad_config)
        dependencies.asr_processor = ASRProcessor(asr_config, device="cpu")

        # Initialize RAG processor based on provider configuration
        rag_provider = rag_config.provider.lower()
        if rag_provider == "modelscope":
            from src.module.rag.modelscope_rag_processor import ModelScopeRAGProcessor
            dependencies.rag_processor = ModelScopeRAGProcessor(rag_config)
            logger.info("使用ModelScope RAG处理器")
        elif rag_provider == "dashscope":
            from src.module.rag.dashscope_rag_processor import DashScopeRAGProcessor
            dependencies.rag_processor = DashScopeRAGProcessor(rag_config)
            logger.info("使用百炼RAG处理器")
        elif rag_provider == "ollama":
            # 验证 Ollama 功能是否启用
            FeatureFlags.validate_ollama_config()
            from src.module.rag.ollama_rag_processor import OllamaRAGProcessor
            dependencies.rag_processor = OllamaRAGProcessor(rag_config)
            logger.info("使用Ollama RAG处理器")
        else:
            raise RuntimeError(f"未知的 RAG provider: {rag_provider}")

        # Initialize LLM processor based on provider configuration
        llm_provider = llm_config.provider.lower()
        if llm_provider == "modelscope":
            from src.module.llm.modelscope_llm_handler import ModelScopeLLMHandler
            dependencies.llm_processor = ModelScopeLLMHandler(llm_config)
            logger.info("使用ModelScope LLM处理器")
        elif llm_provider == "dashscope":
            from src.module.llm.dashscope_llm_handler import DashScopeLLMHandler
            dependencies.llm_processor = DashScopeLLMHandler(llm_config)
            logger.info("使用DashScope LLM处理器")
        elif llm_provider == "ollama":
            # 验证 Ollama 功能是否启用
            FeatureFlags.validate_ollama_config()
            from src.module.llm.ollama_llm_handler import OllamaLLMHandler
            dependencies.llm_processor = OllamaLLMHandler(llm_config)
            logger.info("使用Ollama LLM处理器")
        else:
            raise RuntimeError(f"未知的 LLM provider: {llm_provider}")

        # Start async initialization for VAD, RAG, LLM and ASR processors
        asyncio.create_task(dependencies.rag_processor.initialize())
        asyncio.create_task(dependencies.llm_processor.initialize())
        asyncio.create_task(dependencies.vad_core.initialize())
        asyncio.create_task(dependencies.asr_processor.initialize())

        logger.info("应用启动序列已开始，VAD、RAG和LLM处理器正在后台初始化。")
    except Exception as e:
        logger.exception(f"错误: 处理器初始化失败: {e}")
        # 在这里可以选择是否要阻止应用启动

    yield  # lifespan的核心，yield之前是启动逻辑，之后是关闭逻辑

    # --- 应用关闭时执行 ---
    logger.info("应用关闭... 正在清理资源...")
    dependencies.active_contexts.clear()
    logger.info("资源清理完毕.")

