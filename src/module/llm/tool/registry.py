"""
Tool registry for LLM function calling.

This module provides a centralized registry that manages all function calling
components: definitions, validation, and response mapping.
"""
import json
from typing import List, Optional

from .definitions import get_tool_definitions
from .validator import ToolValidator
from .mapper import ToolResponseMapper
from .types import ToolDefinition, ToolCall, ValidationResult


class ToolRegistry:
    """
    Centralized registry for LLM function calling components.

    This class provides a unified interface to access all function calling
    functionality: tool definitions, validation, and response mapping.
    """

    def __init__(self):
        """Initialize the tool registry with all components."""
        self._tool_definitions = get_tool_definitions()
        self._validator = ToolValidator()
        self._mapper = ToolResponseMapper()

    @property
    def tool_definitions(self) -> List[ToolDefinition]:
        """Get the list of available tool definitions."""
        return self._tool_definitions

    @property
    def validator(self) -> ToolValidator:
        """Get the tool validator instance."""
        return self._validator

    @property
    def mapper(self) -> ToolResponseMapper:
        """Get the tool response mapper instance."""
        return self._mapper

    def validate_function_calls(self, tool_calls: List[ToolCall]) -> ValidationResult:
        """
        Validate function calls using the internal validator.

        Args:
            tool_calls: List of tool calls to validate

        Returns:
            Validation result tuple (is_valid, errors)
        """
        return self._validator.validate_function_calls(tool_calls)

    def map_tool_calls_to_response(self, tool_calls: List[ToolCall]) -> str:
        """
        Map tool calls to response using the internal mapper.

        Args:
            tool_calls: List of tool calls to map

        Returns:
            JSON formatted response string
        """
        return self._mapper.map_tool_calls_to_response(tool_calls)

    def create_error_response(self, reason: str, message: Optional[str] = None, details: Optional[List[str]] = None) -> str:
        """
        Create error response using the internal mapper.

        Args:
            reason: Error reason
            message: Optional error message
            details: Optional error details

        Returns:
            JSON formatted error response string
        """
        error_response = self._mapper.create_error_response(reason, message, details)
        return json.dumps([error_response], ensure_ascii=False)

    def get_validation_context(self) -> str:
        """
        Get validation context from the internal validator.

        Returns:
            JSON string containing available resources
        """
        return self._validator.get_validation_context()