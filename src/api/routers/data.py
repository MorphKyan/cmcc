import os
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import UploadResponse, DeviceItem, AreaItem, MediaItem, DoorItem, LocationUpdateRequest, StatusResponse
from src.core import dependencies

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)


@router.post("/devices/batch", response_model=UploadResponse)
async def upload_devices_batch(items: List[DeviceItem]) -> UploadResponse:
    """批量上传设备数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.add_devices(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_devices(items)
        return UploadResponse(status="success", message="设备数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传设备数据失败: {str(e)}")


@router.post("/areas/batch", response_model=UploadResponse)
async def upload_areas_batch(items: List[AreaItem]) -> UploadResponse:
    """批量上传区域数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_areas(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_areas(items)
        return UploadResponse(status="success", message="区域数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传区域数据失败: {str(e)}")


@router.post("/media/batch", response_model=UploadResponse)
async def upload_media_batch(items: List[MediaItem]) -> UploadResponse:
    """批量上传媒体数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_media(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_media(items)
        return UploadResponse(status="success", message="媒体数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传媒体数据失败: {str(e)}")


@router.get("/devices", response_model=List[Dict[str, Any]])
async def get_devices() -> List[Dict[str, Any]]:
    """获取所有设备数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    return dependencies.data_service.get_all_devices_data()


@router.get("/areas", response_model=List[Dict[str, Any]])
async def get_areas() -> List[Dict[str, Any]]:
    """获取所有区域数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    return dependencies.data_service.get_all_areas_data()


@router.get("/media", response_model=List[Dict[str, Any]])
async def get_media() -> List[Dict[str, Any]]:
    """获取所有媒体数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    return dependencies.data_service.get_all_media_data()


@router.delete("/devices", response_model=UploadResponse)
async def clear_devices() -> UploadResponse:
    """清空所有设备数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_devices()
        if dependencies.rag_processor:
             await dependencies.rag_processor.refresh_database()
        return UploadResponse(status="success", message="设备数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空设备数据失败: {str(e)}")


@router.delete("/areas", response_model=UploadResponse)
async def clear_areas() -> UploadResponse:
    """清空所有区域数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_areas()
        if dependencies.rag_processor:
             await dependencies.rag_processor.refresh_database()
        return UploadResponse(status="success", message="区域数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空区域数据失败: {str(e)}")


@router.delete("/media", response_model=UploadResponse)
async def clear_media() -> UploadResponse:
    """清空所有媒体数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_media()
        if dependencies.rag_processor:
             await dependencies.rag_processor.refresh_database()
        return UploadResponse(status="success", message="媒体数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空媒体数据失败: {str(e)}")


@router.post("/doors/batch", response_model=UploadResponse)
async def upload_doors_batch(items: List[DoorItem]) -> UploadResponse:
    """批量上传门数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_doors(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.batch_add_doors(items)
        return UploadResponse(status="success", message="门数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传门数据失败: {str(e)}")


@router.get("/doors", response_model=List[Dict[str, Any]])
async def get_doors() -> List[Dict[str, Any]]:
    """获取所有门数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    return dependencies.data_service.get_all_doors_data()


@router.delete("/doors", response_model=UploadResponse)
async def clear_doors() -> UploadResponse:
    """清空所有门数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    try:
        await dependencies.data_service.clear_doors()
        if dependencies.rag_processor:
             await dependencies.rag_processor.refresh_database()
        return UploadResponse(status="success", message="门数据已清空")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"清空门数据失败: {str(e)}")


@router.post("/location", response_model=StatusResponse)
async def update_user_location(request: LocationUpdateRequest) -> StatusResponse:
    """
    更新用户位置信息。
    将传入的位置信息存储到对应 client_id 的 context 的 location 字段中。
    """
    client_id = request.client_id
    location = request.location

    if client_id not in dependencies.active_contexts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到客户端连接: {client_id}"
        )

    context = dependencies.active_contexts[client_id]
    context.location = location

    return StatusResponse(
        status="success",
        data={"client_id": client_id, "location": location},
        message=f"用户位置已更新为: {location}"
    )
