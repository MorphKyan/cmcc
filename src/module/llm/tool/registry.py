"""
LLM函数调用工具注册中心。
"""
import json
from .definitions import get_tool_definitions
from .validator import ToolValidator
from .mapper import ToolResponseMapper
from .types import ToolDefinition, ToolCall, ValidationResult


class ToolRegistry:
    """LLM函数调用工具注册中心，统一管理工具定义、验证和响应映射。"""

    def __init__(self):
        """初始化工具注册中心。"""
        self._tool_definitions = get_tool_definitions()
        self._validator = ToolValidator()
        self._mapper = ToolResponseMapper()

    @property
    def tool_definitions(self) -> list[ToolDefinition]:
        """获取工具定义列表。"""
        return self._tool_definitions

    @property
    def validator(self) -> ToolValidator:
        """获取工具验证器实例。"""
        return self._validator

    @property
    def mapper(self) -> ToolResponseMapper:
        """获取工具响应映射器实例。"""
        return self._mapper

    def validate_function_calls(self, tool_calls: list[ToolCall]) -> ValidationResult:
        """验证函数调用。"""
        return self._validator.validate_function_calls(tool_calls)

    def map_tool_calls_to_response(self, tool_calls: list[ToolCall]) -> str:
        """将工具调用映射为响应。"""
        return self._mapper.map_tool_calls_to_response(tool_calls)

    def create_error_response(self, reason: str, message: str | None = None, details: list[str] | None = None) -> str:
        """创建错误响应。"""
        error_response = self._mapper.create_error_response(reason, message, details)
        return json.dumps([error_response], ensure_ascii=False)

    def get_validation_context(self) -> str:
        """获取验证上下文。"""
        return self._validator.get_validation_context()