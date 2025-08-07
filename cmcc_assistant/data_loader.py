#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from langchain.docstore.document import Document
import os

def load_documents_from_excel(file_path):
    """
    从Excel文件加载数据并转换为LangChain的Document对象。
    
    Args:
        file_path (str): Excel文件的路径。
        
    Returns:
        list[Document]: Document对象列表。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件未找到: {file_path}")
        
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise IOError(f"读取Excel文件失败: {e}")

    documents = []
    for _, row in df.iterrows():
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

if __name__ == '__main__':
    # 测试代码
    from config import EXCEL_DATA_PATH
    
    try:
        docs = load_documents_from_excel(EXCEL_DATA_PATH)
        print(f"成功加载 {len(docs)} 个文档。")
        
        # 打印第一个文档的内容和元数据
        if docs:
            print("\n--- 第一个文档示例 ---")
            print(f"内容: {docs[0].page_content}")
            print(f"元数据: {docs[0].metadata}")
            print("---------------------\n")
        
        # 测试格式化函数
        formatted_context = format_docs_for_prompt(docs[:3]) # 取前3个测试
        print("--- 格式化后的上下文示例 ---")
        print(formatted_context)
        print("--------------------------\n")

    except (FileNotFoundError, IOError) as e:
        print(f"错误: {e}")
