from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Any

from src.services.text_pipeline import TextPipelineService

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"]
)

class TextPipelineRequest(BaseModel):
    text: str = Field(..., description="要处理的文本指令")
    # client_id is hidden/fixed as per requirements

class TextPipelineResponse(BaseModel):
    success: bool
    ai_response: str
    commands: list[dict[str, Any]]
    results: list[dict[str, Any]]
    message: str | None = None

@router.post("/text", response_model=TextPipelineResponse)
async def process_text_pipeline(request: TextPipelineRequest) -> TextPipelineResponse:
    """
    通过文本直接驱动处理管道（Test Only）。
    
    该接口用于测试 RAG -> LLM -> Command 流程，不涉及音频处理。
    使用固定的 Context (client_id='text_pipeline')。
    """
    try:
        result = await TextPipelineService.process_text(request.text)
        return TextPipelineResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline processing failed: {str(e)}"
        )
