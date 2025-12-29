import os
from typing import Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.api.schemas import UploadResponse, DeviceItem, AreaItem, MediaItem, DoorItem, LocationUpdateRequest, StatusResponse
from src.core import dependencies

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)


@router.post("/devices/batch", response_model=UploadResponse)
async def upload_devices_batch(items: list[DeviceItem]) -> UploadResponse:
    """批量上传设备数据"""
    logger.info(f"收到批量上传设备请求，数量: {len(items)}, 数据: {items}")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.add_devices(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_devices(items)
        logger.info("设备数据批量上传成功")
        return UploadResponse(status="success", message="设备数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传设备数据失败: {str(e)}")


@router.post("/areas/batch", response_model=UploadResponse)
async def upload_areas_batch(items: list[AreaItem]) -> UploadResponse:
    """批量上传区域数据"""
    logger.info(f"收到批量上传区域请求，数量: {len(items)}, 数据: {items}")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_areas(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_areas(items)
        logger.info("区域数据批量上传成功")
        return UploadResponse(status="success", message="区域数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传区域数据失败: {str(e)}")


@router.post("/media/batch", response_model=UploadResponse)
async def upload_media_batch(items: list[MediaItem]) -> UploadResponse:
    """批量上传媒体数据"""
    logger.info(f"收到批量上传媒体请求，数量: {len(items)}, 数据: {items}")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_media(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_media(items)
        logger.info("媒体数据批量上传成功")
        return UploadResponse(status="success", message="媒体数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传媒体数据失败: {str(e)}")


@router.get("/devices", response_model=list[dict[str, Any]])
async def get_devices() -> list[dict[str, Any]]:
    """获取所有设备数据"""
    logger.info("收到获取所有设备数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    result = dependencies.data_service.get_all_devices_data()
    logger.info(f"获取设备数据成功，数量: {len(result)}")
    return result


@router.get("/areas", response_model=list[dict[str, Any]])
async def get_areas() -> list[dict[str, Any]]:
    """获取所有区域数据"""
    logger.info("收到获取所有区域数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    result = dependencies.data_service.get_all_areas_data()
    logger.info(f"获取区域数据成功，数量: {len(result)}")
    return result


@router.get("/media", response_model=list[dict[str, Any]])
async def get_media() -> list[dict[str, Any]]:
    """获取所有媒体数据"""
    logger.info("收到获取所有媒体数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    result = dependencies.data_service.get_all_media_data()
    logger.info(f"获取媒体数据成功，数量: {len(result)}")
    return result


@router.delete("/devices", response_model=UploadResponse)
async def clear_devices() -> UploadResponse:
    """清空所有设备数据"""
    logger.info("收到清空设备数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_devices()
        if dependencies.rag_processor:
             await dependencies.rag_processor.delete_by_type("device")
        logger.info("设备数据已清空")
        return UploadResponse(status="success", message="设备数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空设备数据失败: {str(e)}")


@router.delete("/areas", response_model=UploadResponse)
async def clear_areas() -> UploadResponse:
    """清空所有区域数据"""
    logger.info("收到清空区域数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_areas()
        if dependencies.rag_processor:
             await dependencies.rag_processor.delete_by_type("area")
        logger.info("区域数据已清空")
        return UploadResponse(status="success", message="区域数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空区域数据失败: {str(e)}")


@router.delete("/media", response_model=UploadResponse)
async def clear_media() -> UploadResponse:
    """清空所有媒体数据"""
    logger.info("收到清空媒体数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_media()
        if dependencies.rag_processor:
             await dependencies.rag_processor.delete_by_type("media")
        logger.info("媒体数据已清空")
        return UploadResponse(status="success", message="媒体数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空媒体数据失败: {str(e)}")


@router.post("/doors/batch", response_model=UploadResponse)
async def upload_doors_batch(items: list[DoorItem]) -> UploadResponse:
    """批量上传门数据"""
    logger.info(f"收到批量上传门数据请求，数量: {len(items)}, 数据: {items}")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_doors(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_doors(items)
        logger.info("门数据批量上传成功")
        return UploadResponse(status="success", message="门数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传门数据失败: {str(e)}")


@router.get("/doors", response_model=list[dict[str, Any]])
async def get_doors() -> list[dict[str, Any]]:
    """获取所有门数据"""
    logger.info("收到获取所有门数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    result = dependencies.data_service.get_all_doors_data()
    logger.info(f"获取门数据成功，数量: {len(result)}")
    return result


@router.delete("/doors", response_model=UploadResponse)
async def clear_doors() -> UploadResponse:
    """清空所有门数据"""
    logger.info("收到清空门数据请求")
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_doors()
        if dependencies.rag_processor:
             await dependencies.rag_processor.delete_by_type("door")
        logger.info("门数据已清空")
        return UploadResponse(status="success", message="门数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空门数据失败: {str(e)}")


@router.post("/location", response_model=StatusResponse)
async def update_user_location(request: LocationUpdateRequest) -> StatusResponse:
    """
    更新用户位置信息。
    将传入的位置信息存储到对应 client_id 的 context 的 location 字段中。
    """
    logger.info(f"收到更新用户位置请求: {request}")
    client_id = request.client_id
    location = request.location

    if client_id not in dependencies.active_contexts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到客户端连接: {client_id}"
        )

    context = dependencies.active_contexts[client_id]
    context.location = location

    message = f"用户位置已更新为: {location}"
    logger.info(message)
    return StatusResponse(
        status="success",
        data={"client_id": client_id, "location": location},
        message=message
    )
