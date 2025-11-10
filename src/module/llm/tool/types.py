"""
Shared type definitions for LLM function calling.
"""
from typing import Any, Dict, List, Optional, Tuple


# Tool call representation from LangChain
ToolCall = Dict[str, Any]

# Validation result
ValidationResult = Tuple[bool, List[str]]

# Tool definition structure
ToolDefinition = Dict[str, Any]

# Response mapping configuration
ResponseMapping = Dict[str, Any]

# Tool registry entry
ToolRegistryEntry = Dict[str, Any]