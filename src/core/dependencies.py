from typing import Dict, Any, Optional
from src.api.context import Context

# 这里只声明变量，初始化将在lifespan事件中
vad_core: Optional[Any] = None
asr_processor: Optional[Any] = None
rag_processor: Optional[Any] = None
llm_processor: Optional[Any] = None

# 存储活跃的WebSocket连接上下文
active_contexts: Dict[str, Context] = {}