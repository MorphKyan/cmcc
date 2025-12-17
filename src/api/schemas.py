from typing import Optional, Any, List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class RefreshResponse(BaseModel):
    status: str
    message: str


class StatusResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None


class QueryRequest(BaseModel):
    query: str


class QueryResult(BaseModel):
    content: str
    metadata: dict


class QueryResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None


class UploadResponse(BaseModel):
    status: str
    message: str

class WebSocketConfig(BaseModel):
    type: str
    format: Optional[str] = None
    sampleRate: Optional[int] = None
    sampleSize: Optional[int] = None
    channelCount: Optional[int] = None
    mimeType: Optional[str] = None


class LLMHealthResponse(BaseModel):
    status: str
    message: str
    provider: str


class ConfigResponse(BaseModel):
    status: str
    data: dict[str, Any]
    message: Optional[str] = None


class DeviceItem(BaseModel):
    name: str
    type: str
    subType: Optional[str] = None
    command: Optional[List[str]] = None
    area: str
    view: Optional[List[str]] = None
    aliases: Optional[str] = None
    description: Optional[str] = None


class AreaItem(BaseModel):
    name: str
    aliases: Optional[str] = None
    description: Optional[str] = None


class MediaItem(BaseModel):
    name: str
    type: str
    aliases: Optional[str] = None
    description: Optional[str] = None


class DoorItem(BaseModel):
    name: str
    type: str
    area1: str
    area2: str
    location: str


class LocationUpdateRequest(BaseModel):
    """用户位置更新请求"""
    client_id: str
    location: str