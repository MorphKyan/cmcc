from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.api.schemas import LLMHealthResponse
from src.core import dependencies

router = APIRouter(
    prefix="/api/llm",
    tags=["LLM"]
)


@router.get("/health", response_model=LLMHealthResponse)
async def llm_health() -> LLMHealthResponse:
    """
    检查LLM服务的健康状态。
    """
    try:
        if dependencies.llm_processor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM服务当前不可用，尚未初始化"
            )

        # 异步检查LLM健康状态
        is_healthy = await dependencies.llm_processor.check_health()

        if is_healthy:
            return LLMHealthResponse(
                status="healthy",
                message="LLM服务正常",
                provider=dependencies.llm_processor.settings.provider
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM服务不健康"
            )

    except Exception as e:
        logger.exception("检查LLM健康状态时发生错误")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查LLM健康状态时发生错误: {str(e)}"
        )