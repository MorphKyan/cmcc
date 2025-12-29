from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class RefreshResponse(BaseModel):
    status: str
    message: str


class StatusResponse(BaseModel):
    status: str
    data: dict | None = None
    message: str | None = None


class QueryRequest(BaseModel):
    query: str


class QueryResult(BaseModel):
    content: str
    metadata: dict


class QueryResponse(BaseModel):
    status: str
    data: dict | None = None
    message: str | None = None


class UploadResponse(BaseModel):
    status: str
    message: str

class WebSocketConfig(BaseModel):
    type: str
    format: str | None = None
    sampleRate: int | None = None
    sampleSize: int | None = None
    channelCount: int | None = None
    mimeType: str | None = None


class LLMHealthResponse(BaseModel):
    status: str
    message: str
    provider: str


class ConfigResponse(BaseModel):
    status: str
    data: dict[str, Any]
    message: str | None = None


class DeviceItem(BaseModel):
    name: str
    type: str
    subType: str | None = None
    command: list[str] | None = None
    area: str
    view: list[str] | None = None
    aliases: str | None = None
    description: str | None = None


class AreaItem(BaseModel):
    name: str
    aliases: str | None = None
    description: str | None = None


class MediaItem(BaseModel):
    name: str
    type: str
    aliases: str | None = None
    description: str | None = None


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