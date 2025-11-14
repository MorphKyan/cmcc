"""
Shared type definitions for LLM function calling.
"""
from typing import Any


# Tool call representation from LangChain
ToolCall = dict[str, Any]

# Validation result
ValidationResult = tuple[bool, list[str]]

# Tool definition structure
ToolDefinition = dict[str, Any]

# Response mapping configuration
ResponseMapping = dict[str, Any]

# Tool registry entry
ToolRegistryEntry = dict[str, Any]