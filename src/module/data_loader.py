#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

import pandas as pd
from langchain_core.documents import Document
from loguru import logger


def load_documents_from_csvs(file_paths: list[str]) -> list[Document]:
    """
    从多个CSV文件加载数据并转换为LangChain的Document对象。

    支持以下CSV文件类型：
    - screens.csv: 屏幕设备信息（包含name, aliases, description列）
    - doors.csv: 门设备信息（包含name, aliases, description列）
    - videos.csv: 视频信息（包含name, aliases, description, filename列）

    Args:
        file_paths (list[str]): CSV文件路径的列表，支持多种类型的CSV文件。

    Returns:
        list[Document]: Document对象列表，每个文档包含适当的类型信息和内容。
    """
    documents = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"数据文件未找到: {file_path}")

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                continue

            # 根据文件名推断设备类型
            filename = os.path.basename(file_path).lower()
            if 'screens' in filename:
                device_type = 'screen'
                prefix = '屏幕名称'
            elif 'doors' in filename:
                device_type = 'door'
                prefix = '门名称'
            elif 'videos' in filename:
                device_type = 'video'
                prefix = '视频名称'
            else:
                # 默认处理为通用类型
                device_type = 'unknown'
                prefix = '项目名称'

            for _, row in df.iterrows():
                # 构建内容，使用适当的前缀
                content_parts = [f"{prefix}: {row['name']}"]
                if pd.notna(row.get('aliases')):
                    content_parts.append(f"也称为{row['aliases']}")
                if pd.notna(row.get('description')):
                    content_parts.append(f"内容描述了{row['description']}")

                content = "，".join(content_parts)

                # 构建metadata，包含所有可用字段
                metadata = {
                    "type": device_type,
                    "name": str(row.get("name", "")),
                    "aliases": str(row.get("aliases", "")),
                    "description": str(row.get("description", "")),
                    "filename": str(row.get("filename", "")) if 'filename' in row else "",
                }

                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)

        except Exception as e:
            logger.exception(f"读取CSV文件 '{file_path}' 失败")
            raise IOError(f"读取CSV文件 '{file_path}' 失败: {e}")

    return documents

def get_prompt_from_rag_documents(docs: list[Document]) -> str:
    """
    将检索到的Document对象格式化为可以插入到Prompt中的字符串。

    支持多种设备类型：
    - screen: 屏幕设备
    - door: 门设备
    - video: 视频内容

    Args:
        docs (list[Document]): 检索到的Document对象列表。

    Returns:
        str: 格式化后的知识库字符串，包含设备类型、名称、描述和文件名（如果适用）。
    """
    if not docs:
        return ""

    devices = []

    for doc in docs:
        meta = doc.metadata
        device_info = {
            "type": meta.get("type", "unknown"),
            "name": meta.get("name", ""),
            "description": meta.get("description", ""),
        }
        # 只有视频类型才有filename
        if meta.get("type") == "video" and meta.get("filename"):
            device_info["filename"] = meta.get("filename")

        devices.append(device_info)

    return json.dumps(devices, ensure_ascii=False, indent=2)
