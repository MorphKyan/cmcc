import os
from typing import List, Dict, Any

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
import pandas as pd

from src.api.schemas import UploadResponse, DeviceItem, AreaItem, VideoItem
from src.config.config import get_settings
from src.core import dependencies

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)


@router.post("/upload-videos", response_model=UploadResponse)
async def upload_videos_csv(file: UploadFile = File(...)) -> UploadResponse:
    """上传videos.csv文件并更新RAG数据库"""
    settings = get_settings()
    if dependencies.data_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="DataService未初始化")

    try:
        # 检查文件类型
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持上传CSV文件")

        # 保存上传的文件到临时位置
        temp_file_path = os.path.join(os.path.dirname(settings.rag.videos_data_path), 'temp_videos.csv')

        # 读取上传的文件内容
        contents = await file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(contents)

        # 验证CSV文件结构
        is_valid, message = validate_csv_structure(temp_file_path, ['name', 'aliases', 'description', 'filename'])
        if not is_valid:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

        # Use DataService to replace file
        await dependencies.data_service.replace_data_file(settings.rag.videos_data_path, temp_file_path)

        # 刷新RAG数据库
        if dependencies.rag_processor:
             await dependencies.rag_processor.refresh_database()

        return UploadResponse(status="success", message="videos.csv文件上传成功，RAG数据库已更新")

    except Exception as e:
        # Cleanup temp file if it still exists
        temp_file_path = os.path.join(os.path.dirname(settings.rag.videos_data_path), 'temp_videos.csv')
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传videos.csv文件时发生异常: {str(e)}")


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


def validate_csv_structure(file_path: str, required_columns: List[str]) -> tuple[bool, str]:
    """验证CSV文件结构是否正确"""
    try:
        df = pd.read_csv(file_path)
        
        # 检查是否包含所有必需的列
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"缺少必需的列: {missing_columns}"

        return True, "CSV文件结构正确"
    except Exception as e:
        return False, f"验证CSV文件时发生错误: {str(e)}"
