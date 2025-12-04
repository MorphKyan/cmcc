import os
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import UploadResponse, DeviceItem, AreaItem, VideoItem
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
             await dependencies.rag_processor.refresh_database()
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
             await dependencies.rag_processor.refresh_database()
        return UploadResponse(status="success", message="区域数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传区域数据失败: {str(e)}")


@router.post("/videos/batch", response_model=UploadResponse)
async def upload_videos_batch(items: List[VideoItem]) -> UploadResponse:
    """批量上传视频数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        await dependencies.data_service.add_videos(items)
        if dependencies.rag_processor:
             await dependencies.rag_processor.refresh_database()
        return UploadResponse(status="success", message="视频数据批量上传成功")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传视频数据失败: {str(e)}")


@router.get("/devices", response_model=List[Dict[str, Any]])
async def get_devices() -> List[Dict[str, Any]]:
    """获取所有设备数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    devices = dependencies.data_service.get_all_devices()
    return [dependencies.data_service.get_device_info(d) for d in devices if dependencies.data_service.get_device_info(d)]


@router.get("/areas", response_model=List[Dict[str, Any]])
async def get_areas() -> List[Dict[str, Any]]:
    """获取所有区域数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    areas = dependencies.data_service.get_all_areas()
    return [dependencies.data_service.get_area_info(a) for a in areas if dependencies.data_service.get_area_info(a)]


@router.get("/videos", response_model=List[Dict[str, Any]])
async def get_videos() -> List[Dict[str, Any]]:
    """获取所有视频数据"""
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")
    
    videos = dependencies.data_service.get_all_videos()
    return [dependencies.data_service.get_video_info(v) for v in videos if dependencies.data_service.get_video_info(v)]
