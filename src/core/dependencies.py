from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional

from src.api.context import Context
from src.services.data_service import DataService
from src.services.performance_metrics_manager import PerformanceMetricsManager

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from src.module.llm.base_llm_handler import BaseLLMHandler
    from src.module.rag.base_rag_processor import BaseRAGProcessor
    from src.module.vad.base_vad_processor import BaseVADProcessor

# 这里只声明变量，初始化将在lifespan事件中
vad_core: Optional[BaseVADProcessor] = None
asr_processor: Optional[Any] = None
rag_processor: Optional[BaseRAGProcessor] = None
llm_processor: Optional[BaseLLMHandler] = None
data_service: Optional[DataService] = None

# 性能指标管理器
metrics_manager: PerformanceMetricsManager = PerformanceMetricsManager()

# 存储活跃的WebSocket连接上下文
active_contexts: dict[str, Context] = {}