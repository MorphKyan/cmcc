from pydantic import BaseModel
from typing import Optional


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