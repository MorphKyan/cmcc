import os
import shutil

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, status

from src.api.schemas import UploadResponse
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
        is_valid, message = validate_csv_structure(temp_file_path)
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

        # 刷新RAG数据库
        if dependencies.rag_processor is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="RAG处理器未初始化")

        success = await dependencies.rag_processor.refresh_database()
        if not success:
            # 如果刷新失败，恢复备份文件
            if os.path.exists(backup_path):
                shutil.move(backup_path, settings.rag.videos_data_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传成功但刷新RAG数据库失败，已恢复原文件")

        # 刷新csv内存
        CSVLoader.reload()

        # 删除备份文件
        if os.path.exists(backup_path):
            os.remove(backup_path)

        return UploadResponse(status="success", message="videos.csv文件上传成功，RAG数据库已更新")

    except Exception as e:
        # 删除可能存在的临时文件
        temp_file_path = os.path.join(os.path.dirname(settings.rag.videos_data_path), 'temp_videos.csv')
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传videos.csv文件时发生异常: {str(e)}")


def validate_csv_structure(file_path: str) -> tuple[bool, str]:
    """验证CSV文件结构是否正确"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['name', 'aliases', 'description', 'filename']

        # 检查是否包含所有必需的列
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"缺少必需的列: {missing_columns}"

        # 检查是否有空值
        if df.isnull().any().any():
            return False, "CSV文件中不能包含空值"

        return True, "CSV文件结构正确"
    except Exception as e:
        return False, f"验证CSV文件时发生错误: {str(e)}"
