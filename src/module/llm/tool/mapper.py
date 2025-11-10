"""
Response mapping for LLM tool calls.

This module handles the mapping of LangChain tool calls to the project's
required JSON response format.
"""
import json
from typing import Any, Dict, List, Optional

from .types import ToolCall


class ToolResponseMapper:
    """
    Response mapper for LLM tool calls.

    Responsible for mapping LangChain tool calls to the project's required
    JSON response format.
    """

    def __init__(self, tool_mappings: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize the response mapper.

        Args:
            tool_mappings: Custom tool mapping configuration, uses default if None
        """
        self.tool_mappings = tool_mappings or self._default_tool_mappings()

    def map_tool_calls_to_response(self, tool_calls: List[ToolCall]) -> str:
        """
        Map LangChain tool calls to project's JSON response format.

        Args:
            tool_calls: LangChain parsed tool calls list

        Returns:
            JSON formatted response string
        """
        if not tool_calls:
            return '[]'

        results = []
        for tool_call in tool_calls:
            function_name = tool_call['type']
            arguments = tool_call['args']

            # Get tool mapping configuration
            if function_name not in self.tool_mappings:
                # Unknown function, return error response
                result = self.create_error_response("unknown_function")
            else:
                # Create response based on mapping configuration
                result = self._create_response_from_mapping(function_name, arguments)

            results.append(result)

        return json.dumps(results, ensure_ascii=False)

    def create_error_response(self, reason: str, message: Optional[str] = None, details: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create error response object.

        Args:
            reason: Error reason
            message: Optional error message
            details: Optional detailed error information list

        Returns:
            Error response object dictionary
        """
        response = {
            "action": "error",
            "reason": reason,
            "target": None,
            "device": None,
            "value": None
        }

        if message is not None:
            response["message"] = message
        if details is not None:
            response["details"] = details

        return response

    def _create_response_from_mapping(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create response object based on mapping configuration.

        Args:
            function_name: Function name
            arguments: Function arguments

        Returns:
            Response object dictionary
        """
        mapping = self.tool_mappings[function_name]

        # Handle action field (may need to get from arguments)
        action_value = mapping["action"]
        if action_value.startswith("args."):
            arg_name = action_value[5:]  # Remove "args." prefix
            action_value = arguments.get(arg_name)

        # Create base response structure
        result = {
            "action": action_value,
            "target": None,
            "device": None,
            "value": None
        }

        # Set fields based on mapping
        for field, source in mapping["fields"].items():
            if source == "function_name":
                result[field] = function_name
            elif source.startswith("args."):
                arg_name = source[5:]  # Remove "args." prefix
                result[field] = arguments.get(arg_name)
            elif source == "none":
                result[field] = None

        return result

    def _default_tool_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default tool mapping configuration.

        Returns:
            Default tool mapping configuration dictionary
        """
        return {
            "play_video": {
                "action": "play",
                "fields": {
                    "target": "args.target",
                    "device": "args.device",
                    "value": "none"
                }
            },
            "control_door": {
                "action": "args.action",  # action comes from argument
                "fields": {
                    "target": "args.target",
                    "device": "none",
                    "value": "none"
                }
            },
            "seek_video": {
                "action": "seek",
                "fields": {
                    "target": "none",
                    "device": "args.device",
                    "value": "args.value"
                }
            },
            "set_volume": {
                "action": "set_volume",
                "fields": {
                    "target": "none",
                    "device": "args.device",
                    "value": "args.value"
                }
            },
            "adjust_volume": {
                "action": "adjust_volume",
                "fields": {
                    "target": "none",
                    "device": "args.device",
                    "value": "args.value"
                }
            }
        }

    def add_tool_mapping(
        self,
        function_name: str,
        action: str,
        field_mappings: Dict[str, str]
    ) -> None:
        """
        Dynamically add tool mapping.

        Args:
            function_name: Function name
            action: Corresponding action
            field_mappings: Field mapping configuration
        """
        self.tool_mappings[function_name] = {
            "action": action,
            "fields": field_mappings
        }

    def remove_tool_mapping(self, function_name: str) -> None:
        """
        Remove tool mapping.

        Args:
            function_name: Function name
        """
        if function_name in self.tool_mappings:
            del self.tool_mappings[function_name]