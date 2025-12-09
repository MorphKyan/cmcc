"""
性能指标管理器

收集并保留最近 N 分钟的音频处理管道各阶段耗时数据。
支持线程安全的并发写入和读取。
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
from typing import Optional, Union
import threading


class MetricType(str, Enum):
    """
    性能指标类型枚举
    
    命名规范: {阶段}_{操作}
    """
    # 音频输入阶段
    AUDIO_DECODE = "audio_decode"           # 音频解码耗时
    
    # VAD 阶段
    VAD_INPUT = "vad_input"                 # VAD 输入处理耗时
    VAD_PROCESS = "vad_process"             # VAD 处理耗时
    
    # ASR 阶段
    ASR_RECOGNIZE = "asr_recognize"         # ASR 语音识别耗时
    
    # LLM/RAG 阶段
    RAG_RETRIEVE = "rag_retrieve"           # RAG 检索耗时
    LLM_GENERATE = "llm_generate"           # LLM 生成耗时
    
    # 命令执行阶段
    CMD_EXECUTE = "cmd_execute"             # 命令执行耗时
    
    @property
    def label(self) -> str:
        """获取指标的中文显示名称"""
        labels = {
            MetricType.AUDIO_DECODE: "音频解码",
            MetricType.VAD_INPUT: "VAD输入",
            MetricType.VAD_PROCESS: "VAD处理",
            MetricType.ASR_RECOGNIZE: "ASR识别",
            MetricType.RAG_RETRIEVE: "RAG检索",
            MetricType.LLM_GENERATE: "LLM生成",
            MetricType.CMD_EXECUTE: "命令执行",
        }
        return labels.get(self, self.value)


@dataclass
class MetricDataPoint:
    """单个性能指标数据点"""
    timestamp: datetime
    duration: float  # 耗时（秒）
    context_id: Optional[str] = None


class PerformanceMetricsManager:
    """
    性能指标管理器
    
    收集并保留最近 5 分钟的各阶段处理耗时数据。
    线程安全设计，支持并发写入和读取。
    """
    
    RETENTION_MINUTES = 5
    MAX_POINTS_PER_METRIC = 1000  # 防止内存溢出
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics: dict[str, deque[MetricDataPoint]] = {
            metric.value: deque(maxlen=self.MAX_POINTS_PER_METRIC)
            for metric in MetricType
        }
    
    def record(self, metric_type: Union[MetricType, str], duration: float, context_id: Optional[str] = None) -> None:
        """
        记录一个性能指标数据点
        
        Args:
            metric_type: 指标类型（MetricType 枚举或字符串值）
            duration: 耗时（秒）
            context_id: 可选的上下文ID（用于关联到特定用户连接）
        """
        # 支持传入枚举或字符串
        key = metric_type.value if isinstance(metric_type, MetricType) else metric_type
        
        if key not in self._metrics:
            return
        
        data_point = MetricDataPoint(
            timestamp=datetime.now(),
            duration=duration,
            context_id=context_id
        )
        
        with self._lock:
            self._metrics[key].append(data_point)
    
    def get_metrics(self, minutes: int = 5) -> dict:
        """
        获取最近 N 分钟的所有指标数据
        
        Args:
            minutes: 获取最近多少分钟的数据，默认5分钟
            
        Returns:
            包含各指标时序数据的字典
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        # 从枚举生成 labels
        labels = {m.value: m.label for m in MetricType}
        
        result = {
            "labels": labels,
            "metrics": {}
        }
        
        with self._lock:
            for metric_key, points in self._metrics.items():
                # 过滤出时间范围内的数据点
                filtered_points = [
                    {
                        "timestamp": p.timestamp.isoformat(),
                        "duration": round(p.duration, 4),
                        "context_id": p.context_id
                    }
                    for p in points
                    if p.timestamp >= cutoff_time
                ]
                result["metrics"][metric_key] = filtered_points
        
        return result
    
    def get_stats(self) -> dict:
        """
        获取统计摘要（平均值、最大值、最小值、计数）
        
        Returns:
            各指标的统计信息
        """
        cutoff_time = datetime.now() - timedelta(minutes=self.RETENTION_MINUTES)
        stats = {}
        
        # 从枚举获取 label
        labels = {m.value: m.label for m in MetricType}
        
        with self._lock:
            for metric_key, points in self._metrics.items():
                # 过滤出时间范围内的数据点
                durations = [
                    p.duration for p in points
                    if p.timestamp >= cutoff_time
                ]
                
                label = labels.get(metric_key, metric_key)
                
                if durations:
                    stats[metric_key] = {
                        "label": label,
                        "count": len(durations),
                        "avg": round(sum(durations) / len(durations), 4),
                        "max": round(max(durations), 4),
                        "min": round(min(durations), 4),
                        "latest": round(durations[-1], 4) if durations else None
                    }
                else:
                    stats[metric_key] = {
                        "label": label,
                        "count": 0,
                        "avg": None,
                        "max": None,
                        "min": None,
                        "latest": None
                    }
        
        return stats
    
    def clear(self) -> None:
        """清空所有指标数据"""
        with self._lock:
            for metric in MetricType:
                self._metrics[metric.value].clear()

