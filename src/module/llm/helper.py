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
    def format_video_document(doc: Document) -> dict:
        """
        格式化视频类型的文档。

        Args:
            doc: 视频 Document 对象

        Returns:
            格式化后的字典
        """
        meta = doc.metadata
        return {
            "name": meta.get("filename", ""),
            "description": f"{meta.get('description', '')}，也称为{meta.get('aliases', '')}",
        }

    @staticmethod
    def format_door_document(doc: Document) -> dict:
        """
        格式化门类型的文档。

        Args:
            doc: 门 Document 对象

        Returns:
            格式化后的字典
        """
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
        
        return {
            "name": meta.get("name", ""),
            "type": door_type,
            "description": description
        }

    @staticmethod
    def format_device_document(doc: Document) -> dict:
        """
        格式化设备类型的文档。

        Args:
            doc: 设备 Document 对象

        Returns:
            格式化后的字典
        """
        meta = doc.metadata
        return {
            "name": meta.get("name", ""),
            "type": meta.get("device_type", ""),
            "area": meta.get("area", ""),
            "description": f"{meta.get('description', '')}，也称为{meta.get('aliases', '')}"
        }

    @staticmethod
    def format_default_document(doc: Document) -> dict:
        """
        默认的文档格式化方法。

        Args:
            doc: Document 对象

        Returns:
            格式化后的字典
        """
        return {"content": doc.page_content}

    @classmethod
    def get_prompt_from_documents(cls, docs: list[Document], doc_type: str = "video") -> str:
        """
        将检索到的 Document 对象格式化为可以插入到 Prompt 中的字符串。

        Args:
            docs: 检索到的 Document 对象列表
            doc_type: 文档类型，可选值为 "video", "door", "device"

        Returns:
            格式化后的 JSON 字符串
        """
        if not docs:
            return "[]"

        # 根据类型选择对应的格式化函数
        formatter_map = {
            "video": cls.format_video_document,
            "door": cls.format_door_document,
            "device": cls.format_device_document,
        }

        formatter = formatter_map.get(doc_type, cls.format_default_document)
        result = [formatter(doc) for doc in docs]

        return json.dumps(result, ensure_ascii=False, indent=2)
