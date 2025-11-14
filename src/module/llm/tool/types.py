"""
LLM函数调用类型定义。
"""
from typing import Any


# 工具调用表示
ToolCall = dict[str, Any]

# 验证结果
ValidationResult = tuple[bool, list[str]]

# 工具定义结构
ToolDefinition = dict[str, Any]

# 响应映射配置
ResponseMapping = dict[str, Any]

# 工具注册条目
ToolRegistryEntry = dict[str, Any]