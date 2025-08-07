#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from langchain.docstore.document import Document
import os

def load_documents_from_csvs(file_paths):
    """
    从多个CSV文件加载数据并转换为LangChain的Document对象。
    
    Args:
        file_paths (list[str]): CSV文件路径的列表。
        
    Returns:
        list[Document]: Document对象列表。
    """
    dfs = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"数据文件未找到: {file_path}")
        try:
            df = pd.read_csv(file_path)
            dfs.append(df)
        except Exception as e:
            raise IOError(f"读取CSV文件 '{file_path}' 失败: {e}")
    
    combined_df = pd.concat(dfs, ignore_index=True)

    documents = []
    for _, row in combined_df.iterrows():
        # 将每一行转换为一个文本内容，用于向量化
        # 我们将所有相关信息合并，以便语义搜索能捕捉到
        content = f"类型: {row['type']}, 名称: {row['name']}"
        if pd.notna(row['aliases']):
            content += f", 别名: {row['aliases']}"
        if pd.notna(row['description']):
            content += f", 描述: {row['description']}"
        
        # metadata存储了原始的、结构化的信息
        metadata = {
            "type": str(row.get("type", "")),
            "name": str(row.get("name", "")),
            "aliases": str(row.get("aliases", "")),
            "description": str(row.get("description", "")),
            "filename": str(row.get("filename", "")),
        }
        
        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)
        
    return documents

def format_docs_for_prompt(docs):
    """
    将检索到的Document对象格式化为可以插入到Prompt中的字符串。
    
    Args:
        docs (list[Document]): 检索到的Document对象列表。
        
    Returns:
        str: 格式化后的知识库字符串。
    """
    if not docs:
        return "没有在知识库中找到相关信息。"

    knowledge_base = {
        "screens": [],
        "doors": [],
        "videos": []
    }

    for doc in docs:
        meta = doc.metadata
        item_type = meta.get("type")
        
        if item_type == "screen":
            knowledge_base["screens"].append({
                "name": meta.get("name"),
                "aliases": meta.get("aliases", "").split(',')
            })
        elif item_type == "door":
            knowledge_base["doors"].append({
                "name": meta.get("name"),
                "aliases": meta.get("aliases", "").split(',')
            })
        elif item_type == "video":
            knowledge_base["videos"].append({
                "filename": meta.get("filename"),
                "description": meta.get("description")
            })
            
    # 为了可读性，进行简单的JSON格式化
    import json
    return json.dumps(knowledge_base, ensure_ascii=False, indent=2)
