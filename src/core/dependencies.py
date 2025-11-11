from typing import Any, Optional
from src.api.context import Context
from src.module.llm.base_llm_handler import BaseLLMHandler
from src.module.rag.base_rag_processor import BaseRAGProcessor

# 这里只声明变量，初始化将在lifespan事件中
vad_core: Optional[Any] = None
asr_processor: Optional[Any] = None
rag_processor: Optional[BaseRAGProcessor] = None
llm_processor: Optional[BaseLLMHandler] = None

# 存储活跃的WebSocket连接上下文
active_contexts: dict[str, Context] = {}