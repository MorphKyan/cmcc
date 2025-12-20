"""LLM Helper - 将 Document 格式化为 LLM Prompt"""

import json
from langchain_core.documents import Document


class DocumentFormatter:
    """将检索到的 Document 转换为 LLM Prompt 字符串"""

    @staticmethod
    def format_media_documents(docs: list[Document]) -> str:
        """格式化媒体文档列表"""
        if not docs:
            return "[]"
        
        result = []
        for doc in docs:
            meta = doc.metadata
            result.append({
                "name": meta.get("name", ""),
                "description": meta.get("description", ""),
            })
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def format_door_documents(docs: list[Document]) -> str:
        """格式化门文档列表"""
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
        """格式化设备文档列表"""
        if not docs:
            return "[]"
        
        result = []
        for doc in docs:
            meta = doc.metadata
            
            device_info = {
                "name": meta.get("name", ""),
                "type": meta.get("device_type", ""),
                "area": meta.get("area", ""),
                "description": meta.get("description", "")
            }
            
            if meta.get("sub_type"):
                device_info["subType"] = meta.get("sub_type")
            if meta.get("command"):
                device_info["command"] = meta.get("command")
            if meta.get("view"):
                device_info["view"] = meta.get("view")
                
            result.append(device_info)
        return json.dumps(result, ensure_ascii=False, indent=2)

    @staticmethod
    def format_area_info(areas: list[dict]) -> str:
        """格式化区域信息列表"""
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
