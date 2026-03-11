import os
from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.api.schemas import UploadResponse, HotwordsRequest
from src.core import dependencies

router = APIRouter(
    prefix="/data/hotwords",
    tags=["Data", "Hotwords"]
)

@router.get("", response_model=list[str])
async def get_hotwords() -> list[str]:
    """获取所有自定义热词"""
    logger.info("收到获取所有自定义热词请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    result = dependencies.data_service.get_custom_hotwords()
    logger.info(f"获取自定义热词成功，数量: {len(result)}")
    return result

@router.post("", response_model=UploadResponse)
async def add_hotwords(request: HotwordsRequest) -> UploadResponse:
    """批量添加自定义热词"""
    logger.info(f"收到批量添加自定义热词请求，数量: {len(request.words)}")
    
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_hotwords(request.words)
        logger.info("自定义热词批量添加成功")
        return UploadResponse(status="success", message="自定义热词批量添加成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"添加自定义热词失败: {str(e)}")

@router.delete("", response_model=UploadResponse)
async def clear_hotwords() -> UploadResponse:
    """清空所有自定义热词"""
    logger.info("收到清空自定义热词请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_hotwords()
        logger.info("自定义热词已清空")
        return UploadResponse(status="success", message="自定义热词已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空自定义热词失败: {str(e)}")

@router.delete("/batch", response_model=UploadResponse)
async def remove_hotwords_batch(request: HotwordsRequest) -> UploadResponse:
    """批量移除指定的自定义热词"""
    logger.info(f"收到批量移除自定义热词请求，数量: {len(request.words)}")
    
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.remove_hotwords(request.words)
        logger.info("自定义热词批量移除成功")
        return UploadResponse(status="success", message="自定义热词批量移除成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量移除自定义热词失败: {str(e)}")
