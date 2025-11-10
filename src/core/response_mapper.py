#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Response mapper for LLM tool calls.

This module handles the mapping of LangChain tool calls to the project's
required JSON response format.
"""

import json
from typing import List, Dict, Any, Optional


class ResponseMapper:
    """
    响应映射器。

    负责将LangChain解析出的工具调用列表映射到项目所需的最终JSON格式。
    """

    def __init__(self, tool_mappings: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        初始化响应映射器。

        Args:
            tool_mappings: 自定义工具映射配置，如果为None则使用默认映射
        """
        self.tool_mappings = tool_mappings or self._default_tool_mappings()

    def map_tool_calls_to_response(self, tool_calls: List[Dict[str, Any]]) -> str:
        """
        将LangChain解析出的工具调用列表映射到项目所需的最终JSON格式。

        Args:
            tool_calls: LangChain解析出的工具调用列表

        Returns:
            JSON格式的响应字符串
        """
        if not tool_calls:
            return '[]'

        results = []
        for tool_call in tool_calls:
            function_name = tool_call['type']
            arguments = tool_call['args']

            # 获取工具映射配置
            if function_name not in self.tool_mappings:
                # 未知函数，返回错误响应
                result = self._create_error_response("unknown_function")
            else:
                # 根据映射配置创建响应
                result = self._create_response_from_mapping(function_name, arguments)

            results.append(result)

        return json.dumps(results, ensure_ascii=False)

    def _create_response_from_mapping(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        根据映射配置创建响应对象。

        Args:
            function_name: 函数名称
            arguments: 函数参数

        Returns:
            响应对象字典
        """
        mapping = self.tool_mappings[function_name]

        # 处理action字段（可能需要从参数中获取）
        action_value = mapping["action"]
        if action_value.startswith("args."):
            arg_name = action_value[5:]  # 移除 "args." 前缀
            action_value = arguments.get(arg_name)

        # 创建基础响应结构
        result = {
            "action": action_value,
            "target": None,
            "device": None,
            "value": None
        }

        # 根据映射设置各个字段
        for field, source in mapping["fields"].items():
            if source == "function_name":
                result[field] = function_name
            elif source.startswith("args."):
                arg_name = source[5:]  # 移除 "args." 前缀
                result[field] = arguments.get(arg_name)
            elif source == "none":
                result[field] = None

        return result

    def _create_error_response(self, reason: str) -> Dict[str, Any]:
        """
        创建错误响应对象。

        Args:
            reason: 错误原因

        Returns:
            错误响应对象字典
        """
        return {
            "action": "error",
            "reason": reason,
            "target": None,
            "device": None,
            "value": None
        }

    def _default_tool_mappings(self) -> Dict[str, Dict[str, Any]]:
        """
        获取默认的工具映射配置。

        Returns:
            默认工具映射配置字典
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
                "action": "args.action",  # action来自参数
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
        动态添加工具映射。

        Args:
            function_name: 函数名称
            action: 对应的动作
            field_mappings: 字段映射配置
        """
        self.tool_mappings[function_name] = {
            "action": action,
            "fields": field_mappings
        }

    def remove_tool_mapping(self, function_name: str) -> None:
        """
        移除工具映射。

        Args:
            function_name: 函数名称
        """
        if function_name in self.tool_mappings:
            del self.tool_mappings[function_name]