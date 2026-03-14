"""RAG Document构建辅助函数。

针对不同实体类型优化文档内容，增强语义匹配能力。
"""
import json
from typing import Any
from langchain_core.documents import Document


def _is_valid_field(val: Any) -> bool:
    """检查值是否有效，过滤空值"""
    if val is None:
        return False
    if isinstance(val, str) and not val.strip():
        return False
    if isinstance(val, (list, dict, set, tuple)) and not val:
        return False
    return bool(val)


def convert_doors_to_documents(doors_data: list[dict[str, Any]]) -> list[Document]:
    """转换门数据为文档"""
    documents = []
    for door in doors_data:
        name = door.get('name', '')
        door_type = door.get('type', '')
        
        content_parts = []
        
        # 门名称
        if _is_valid_field(name):
            content_parts.append(f"门名称：{name}")
        
        if door_type == 'passage':
            area1 = door.get('area1', '')
            area2 = door.get('area2', '')
            if _is_valid_field(area1) and _is_valid_field(area2):
                # 添加双向导航语义
                content_parts.append(f"连接区域：{area1}和{area2}")
                content_parts.append(f"通行路径：从{area1}到{area2} 从{area2}到{area1}")
                content_parts.append(f"位置：{area1}与{area2}之间的通道")
        elif door_type == 'standalone':
            location = door.get('location', '')
            if _is_valid_field(location):
                content_parts.append(f"所在区域：{location}")
                content_parts.append(f"位置：{location}内的门 进入{location}")
        
        content = " | ".join(content_parts)
        
        metadata = {
            "type": "door",
            "name": name,
            "door_type": door_type,
            "area1": door.get("area1", ""),
            "area2": door.get("area2", ""),
            "location": door.get("location", "")
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents


def convert_devices_to_documents(devices_data: list[dict[str, Any]]) -> list[Document]:
    """转换设备数据为文档"""
    documents = []
    for device in devices_data:
        name = device.get('name', '')
        device_type = device.get('type', '')
        sub_type = device.get('subType', '')
        area = device.get('area', '')
        aliases = device.get('aliases', '')
        description = device.get('description', '')
        
        content_parts = []
        
        # 设备名称和别名
        if _is_valid_field(name):
            content_parts.append(f"设备的名称是{name}")
        if _is_valid_field(aliases):
            # 将逗号分隔的别名展开
            alias_list = [a.strip() for a in str(aliases).split(',') if a.strip()]
            content_parts.append(f"也叫做{'、'.join(alias_list)}")
        
        # 设备类型和操作语义
        if _is_valid_field(device_type):
            content_parts.append(f"是{device_type}类型的设备")
        
        if _is_valid_field(sub_type):
            content_parts.append(f"子类型为{sub_type}")
        
        # 位置信息
        if _is_valid_field(area):
            content_parts.append(f"位于{area}区域")
        
        # 视窗区域
        views = device.get('view', [])
        if isinstance(views, list) and _is_valid_field(views):
            views_list = [v for v in views if _is_valid_field(v)]
            if views_list:
                content_parts.append(f"包含{'、'.join(views_list)}视窗view")
        
        # 支持的命令
        commands = device.get('command', [])
        if isinstance(commands, list) and _is_valid_field(commands):
            commands_list = [c for c in commands if _is_valid_field(c)]
            if commands_list:
                content_parts.append(f"支持的操作包括：{'、'.join(commands_list)}")
        
        # 连接：前面是基础属性，用逗号连接
        base_info = "，".join(content_parts)
        
        # 描述放在最后，用句号分隔
        if _is_valid_field(description):
            final_content = f"{base_info}。详细描述：{description}" if base_info else f"详细描述：{description}"
        else:
            final_content = base_info
        
        # 构建metadata
        command_list = device.get("command", [])
        command_json = json.dumps(command_list if isinstance(command_list, list) else [], ensure_ascii=False)
        
        view_list = device.get("view", [])
        view_json = json.dumps(view_list if isinstance(view_list, list) else [], ensure_ascii=False)
        
        metadata = {
            "type": "device",
            "name": name,
            "device_type": device_type,
            "sub_type": sub_type,
            "command": command_json,
            "area": area,
            "view": view_json,
            "aliases": aliases,
            "description": description
        }
        documents.append(Document(page_content=final_content, metadata=metadata))
    return documents

def convert_media_to_documents(media_data: list[dict[str, Any]]) -> list[Document]:
    """转换媒体数据为文档"""
    documents = []
    for media in media_data:
        name = media.get('name', '')
        media_type = media.get('type', '')
        aliases = media.get('aliases', '')
        description = media.get('description', '')
        
        content_parts = []
        
        # 媒体名称
        if _is_valid_field(name):
            content_parts.append(f"媒体名称是{name}")
        
        # 媒体类型
        if _is_valid_field(media_type):
            content_parts.append(f"是{media_type}类型的")
        
        # 别名展开
        if _is_valid_field(aliases):
            alias_list = [a.strip() for a in str(aliases).split(',') if a.strip()]
            content_parts.append(f"关键词包括{'、'.join(alias_list)}")

        base_info = "，".join(content_parts)
        
        # 内容描述
        if _is_valid_field(description):
            final_content = f"{base_info}。内容简介：{description}" if base_info else f"内容简介：{description}"
        else:
            final_content = base_info
        
        metadata = {
            "type": "media",
            "name": name,
            "media_type": media_type,
            "aliases": aliases,
            "description": description
        }
        documents.append(Document(page_content=final_content, metadata=metadata))
    return documents


def convert_areas_to_documents(areas_data: list[dict[str, Any]]) -> list[Document]:
    """转换区域数据为文档"""
    documents = []
    for area in areas_data:
        name = area.get('name', '')
        aliases = area.get('aliases', '')
        description = area.get('description', '')
        
        content_parts = []
        
        # 区域名称
        if _is_valid_field(name):
            content_parts.append(f"区域叫做{name}")
        
        # 别名展开
        if _is_valid_field(aliases):
            alias_list = [a.strip() for a in str(aliases).split(',') if a.strip()]
            content_parts.append(f"也叫{'、'.join(alias_list)}")
        
        # 区域描述
        if _is_valid_field(description):
            content_parts.append(str(description))
        
        content = "，".join(content_parts)
        
        metadata = {
            "type": "area",
            "name": name,
            "aliases": aliases,
            "description": description,
        }
        documents.append(Document(page_content=content, metadata=metadata))
    return documents
