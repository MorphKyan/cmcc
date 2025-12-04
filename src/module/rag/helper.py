from typing import List, Dict, Any
from langchain_core.documents import Document

def convert_doors_to_documents(doors_data: List[Dict[str, Any]]) -> List[Document]:
    documents = []
    for door in doors_data:
        content_parts = [f"{door.get('name', '')}"]
        door_type = door.get('type', '')
        
        if door_type == 'passage':
            area1 = door.get('area1', '')
            area2 = door.get('area2', '')
            if area1 and area2:
                content_parts.append(f"连接{area1}和{area2}")
        elif door_type == 'standalone':
            location = door.get('location', '')
            if location:
                content_parts.append(f"位于{location}")
        
        content = "，".join(content_parts)
        metadata = {
            "type": "door",
            "name": door.get("name", ""),
            "door_type": door_type,
            "area1": door.get("area1", ""),
            "area2": door.get("area2", ""),
            "location": door.get("location", ""),
            "filename": ""
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

def convert_devices_to_documents(devices_data: List[Dict[str, Any]]) -> List[Document]:
    documents = []
    for device in devices_data:
        content_parts = [f"{device.get('name', '')}"]
        if device.get('type'):
            content_parts.append(f"类型为{device['type']}")
        if device.get('area'):
            content_parts.append(f"位于{device['area']}")
        if device.get('aliases'):
            content_parts.append(f"也称为{device['aliases']}")
        if device.get('description'):
            content_parts.append(f"内容描述了{device['description']}")

        content = "，".join(content_parts)
        metadata = {
            "type": "device",
            "name": device.get("name", ""),
            "device_type": device.get("type", ""),
            "area": device.get("area", ""),
            "aliases": device.get("aliases", ""),
            "description": device.get("description", ""),
            "filename": ""
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

def convert_videos_to_documents(videos_data: List[Dict[str, Any]]) -> List[Document]:
    documents = []
    for video in videos_data:
        content_parts = [f"{video.get('name', '')}"]
        if video.get('aliases'):
            content_parts.append(f"也称为{video['aliases']}")
        if video.get('description'):
            content_parts.append(f"内容描述了{video['description']}")

        content = "，".join(content_parts)
        metadata = {
            "type": "video",
            "name": video.get("name", ""),
            "aliases": video.get("aliases", ""),
            "description": video.get("description", ""),
            "filename": video.get("filename", "")
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents
