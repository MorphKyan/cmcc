import os
import shutil
from typing import List

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

from src.api.schemas import UploadResponse, DeviceItem, AreaItem, VideoItem
from src.config.config import get_settings
from src.core import dependencies
from src.core.csv_loader import CSVLoader

router = APIRouter(
    prefix="/data",
    tags=["Data"]
)


@router.post("/upload-videos", response_model=UploadResponse)
async def upload_videos_csv(file: UploadFile = File(...)) -> UploadResponse:
    """上传videos.csv文件并更新RAG数据库"""
    settings = get_settings()
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
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

        # 备份原文件
        backup_path = settings.rag.videos_data_path + '.backup'
        if os.path.exists(settings.rag.videos_data_path):
            shutil.copy2(settings.rag.videos_data_path, backup_path)

        # 替换原文件
        shutil.move(temp_file_path, settings.rag.videos_data_path)

        # 刷新系统
        await refresh_system(backup_path, settings.rag.videos_data_path)

        return UploadResponse(status="success", message="videos.csv文件上传成功，RAG数据库已更新")

    except Exception as e:
        # 删除可能存在的临时文件
        temp_file_path = os.path.join(os.path.dirname(settings.rag.videos_data_path), 'temp_videos.csv')
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传videos.csv文件时发生异常: {str(e)}")


@router.post("/devices/batch", response_model=UploadResponse)
async def upload_devices_batch(items: List[DeviceItem]) -> UploadResponse:
    """批量上传设备数据"""
    return await process_batch_upload(items, "devices")


@router.post("/areas/batch", response_model=UploadResponse)
async def upload_areas_batch(items: List[AreaItem]) -> UploadResponse:
    """批量上传区域数据"""
    return await process_batch_upload(items, "areas")


@router.post("/videos/batch", response_model=UploadResponse)
async def upload_videos_batch(items: List[VideoItem]) -> UploadResponse:
    """批量上传视频数据"""
    return await process_batch_upload(items, "videos")


async def process_batch_upload(items: List[BaseModel], data_type: str) -> UploadResponse:
    settings = get_settings()
    
    if data_type == "devices":
        file_path = settings.rag.devices_data_path
        required_columns = ['name', 'type', 'area', 'aliases', 'description']
    elif data_type == "areas":
        file_path = settings.rag.areas_data_path
        required_columns = ['name', 'aliases', 'description']
    elif data_type == "videos":
        file_path = settings.rag.videos_data_path
        required_columns = ['name', 'aliases', 'description', 'filename']
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未知的数据类型")

    try:
        # 将items转换为DataFrame
        new_data = [item.model_dump() for item in items]
        new_df = pd.DataFrame(new_data)
        
        # 确保列顺序和存在性
        for col in required_columns:
            if col not in new_df.columns:
                new_df[col] = None # 或者空字符串，视情况而定
        
        new_df = new_df[required_columns] # 重排并过滤列

        # 备份原文件
        backup_path = file_path + '.backup'
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            # 读取现有数据并追加
            existing_df = pd.read_csv(file_path)
            # 这里简单追加，不进行去重
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df

        # 保存到文件
        combined_df.to_csv(file_path, index=False, quoting=1) # quoting=1 (QUOTE_ALL) or default? csv.QUOTE_MINIMAL is usually safer. pandas default is minimal.

        # 刷新系统
        await refresh_system(backup_path, file_path)

        return UploadResponse(status="success", message=f"{data_type}数据批量上传成功")

    except Exception as e:
        if os.path.exists(backup_path) and os.path.exists(file_path):
             # 恢复备份 (如果出错且备份存在)
             # 注意：refresh_system 内部也有恢复逻辑，这里是在 process_batch_upload 发生其他错误时的处理
             pass 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"批量上传{data_type}数据时发生异常: {str(e)}")


async def refresh_system(backup_path: str, target_path: str):
    """刷新RAG数据库和CSV加载器"""
    # 刷新RAG数据库
    if dependencies.rag_processor is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RAG处理器未初始化")

    success = await dependencies.rag_processor.refresh_database()
    if not success:
        # 如果刷新失败，恢复备份文件
        if os.path.exists(backup_path):
            shutil.move(backup_path, target_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="数据保存成功但刷新RAG数据库失败，已恢复原文件")

    # 刷新csv内存
    CSVLoader().reload()

    # 删除备份文件
    if os.path.exists(backup_path):
        os.remove(backup_path)


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
