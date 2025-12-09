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

def convert_media_to_documents(media_data: List[Dict[str, Any]]) -> List[Document]:
    documents = []
    for media in media_data:
        content_parts = [f"{media.get('name', '')}"]
        if media.get('aliases'):
            content_parts.append(f"也称为{media['aliases']}")
        if media.get('description'):
            content_parts.append(f"内容描述了{media['description']}")

        content = "，".join(content_parts)
        metadata = {
            "type": "media",
            "name": media.get("name", ""),
            "aliases": media.get("aliases", ""),
            "description": media.get("description", ""),
            "filename": media.get("name", "")  # Backward compatibility or just use name
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents

def convert_areas_to_documents(areas_data: List[Dict[str, Any]]) -> List[Document]:
    documents = []
    for area in areas_data:
        content_parts = [f"{area.get('name', '')}"]
        if area.get('aliases'):
            content_parts.append(f"也称为{area['aliases']}")
        if area.get('description'):
            content_parts.append(f"描述为{area['description']}")

        content = "，".join(content_parts)
        metadata = {
            "type": "area",
            "name": area.get("name", ""),
            "aliases": area.get("aliases", ""),
            "description": area.get("description", ""),
            "filename": ""
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents
