from typing import Dict
from src.api.context import Context

# 这里只声明变量，初始化将在lifespan事件中
vad_core = None
asr_processor = None
rag_processor = None
llm_processor = None

# 存储活跃的WebSocket连接上下文
active_contexts: Dict[str, Context] = {}