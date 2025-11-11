from typing import Optional, Any

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