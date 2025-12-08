#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Helper 模块

提供将不同类型的 Document 对象格式化为 Prompt 字符串的工具函数。
"""

import json
from langchain_core.documents import Document


class DocumentFormatter:
    """
    Document 格式化器，负责将检索到的 Document 对象转换为可用于 LLM Prompt 的字符串。
    """

    @staticmethod
    def format_media_documents(docs: list[Document]) -> str:
        """
        格式化媒体类型的文档列表。

        Args:
            docs: 媒体 Document 对象列表

        Returns:
            格式化后的 JSON 字符串
        """
        if not docs:
            return "[]"
        
        result = []
        for doc in docs:
            meta = doc.metadata
            result.append({
                "name": meta.get("filename", ""),
                "description": f"{meta.get('description', '')}，也称为{meta.get('aliases', '')}",
            })
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def format_door_documents(docs: list[Document]) -> str:
        """
        格式化门类型的文档列表。

        Args:
            docs: 门 Document 对象列表

        Returns:
            格式化后的 JSON 字符串
        """
        if not docs:
            return "[]"
        
        result = []
        for doc in docs:
            meta = doc.metadata
            door_type = meta.get("door_type", "")
            
            if door_type == "passage":
                area1 = meta.get("area1", "")
                area2 = meta.get("area2", "")
                description = f"连接{area1}和{area2}的通道门"
            elif door_type == "standalone":
                location = meta.get("location", "")
                description = f"位于{location}的独立门"
            else:
                description = "门"
            
            result.append({
                "name": meta.get("name", ""),
                "type": door_type,
                "description": description
            })
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def format_device_documents(docs: list[Document]) -> str:
        """
        格式化设备类型的文档列表。

        Args:
            docs: 设备 Document 对象列表

        Returns:
            格式化后的 JSON 字符串
        """
        if not docs:
            return "[]"
        
        result = []
        for doc in docs:
            meta = doc.metadata
            result.append({
                "name": meta.get("name", ""),
                "type": meta.get("device_type", ""),
                "area": meta.get("area", ""),
                "description": f"{meta.get('description', '')}，也称为{meta.get('aliases', '')}"
            })
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def format_area_info(areas: list[dict]) -> str:
        """
        格式化区域信息列表。

        Args:
            areas: 区域信息字典列表，每个字典包含 name, aliases, description 字段

        Returns:
            格式化后的 JSON 字符串
        """
        if not areas:
            return "[]"

        result = []
        for area_info in areas:
            if area_info:
                name = area_info.get("name", "")
                aliases_str = area_info.get("aliases", "")
                description_str = area_info.get("description", "")
                aliases = [alias.strip() for alias in aliases_str.split(",")] if aliases_str else []
                result.append({
                    "name": name,
                    "description": f"{description_str}，也称为{aliases}"
                })
        return json.dumps(result, ensure_ascii=False, indent=2)
