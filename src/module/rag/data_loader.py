#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import pandas as pd
from langchain_core.documents import Document
from loguru import logger


def load_documents_from_csvs(file_paths: list[str]) -> list[Document]:
    """
    从多个CSV文件加载数据并转换为LangChain的Document对象。

    支持以下CSV文件类型：
    - screens.csv: 屏幕设备信息（包含name, aliases, description列）
    - doors.csv: 门设备信息（包含name, type, area1, area2, location列）
    - videos.csv: 视频信息（包含name, aliases, description, filename列）

    Args:
        file_paths (list[str]): CSV文件路径的列表，支持多种类型的CSV文件。

    Returns:
        list[Document]: Document对象列表，每个文档包含适当的类型信息和内容。
    """
    documents = []

    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                continue

            # 根据文件名推断设备类型
            filename = os.path.basename(file_path).lower()
            if 'screens' in filename:
                device_type = 'screen'
            elif 'doors' in filename:
                device_type = 'door'
            elif 'videos' in filename:
                device_type = 'video'
            elif 'devices' in filename:
                device_type = 'device'
            else:
                # 默认处理为通用类型
                device_type = 'unknown'

            for _, row in df.iterrows():
                # 构建内容，使用适当的前缀
                if device_type == 'door':
                    # 门设备处理
                    content_parts = [f"{row['name']}"]
                    door_type = str(row.get('type', '')).strip()
                    
                    if door_type == 'passage':
                        # 通道门
                        area1 = row.get('area1', '')
                        area2 = row.get('area2', '')
                        if pd.notna(area1) and pd.notna(area2):
                            content_parts.append(f"连接{area1}和{area2}")
                    elif door_type == 'standalone':
                        # 独立门
                        location = row.get('location', '')
                        if pd.notna(location):
                            content_parts.append(f"位于{location}")
                    
                    content = "，".join(content_parts)
                    
                    # 构建metadata
                    metadata = {
                        "type": device_type,
                        "name": str(row.get("name", "")),
                        "door_type": door_type,
                        "area1": str(row.get("area1", "")),
                        "area2": str(row.get("area2", "")),
                        "location": str(row.get("location", "")),
                        "filename": ""
                    }
                elif device_type == 'device':
                    # 设备处理
                    content_parts = [f"{row['name']}"]
                    if pd.notna(row.get('type')):
                        content_parts.append(f"类型为{row['type']}")
                    if pd.notna(row.get('area')):
                        content_parts.append(f"位于{row['area']}")
                    if pd.notna(row.get('aliases')):
                        content_parts.append(f"也称为{row['aliases']}")
                    if pd.notna(row.get('description')):
                        content_parts.append(f"内容描述了{row['description']}")

                    content = "，".join(content_parts)

                    # 构建metadata，包含所有可用字段
                    metadata = {
                        "type": device_type,
                        "name": str(row.get("name", "")),
                        "device_type": str(row.get("type", "")),
                        "area": str(row.get("area", "")),
                        "aliases": str(row.get("aliases", "")),
                        "description": str(row.get("description", "")),
                        "filename": ""
                    }
                else:
                    # 其他设备类型（screens, videos）
                    content_parts = [f"{row['name']}"]
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
