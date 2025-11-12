import os
import shutil
from typing import Tuple

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, status, BackgroundTasks
from loguru import logger

from src.api.schemas import RefreshResponse, StatusResponse, QueryResponse, UploadResponse, QueryRequest
from src.config.config import settings
from src.core import dependencies
from src.module.rag.ollama_rag_processor import RAGStatus

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


async def reinitialize_task():
    """后台任务，用于重新初始化。"""
    try:
        await dependencies.rag_processor.initialize()
    except Exception as e:
        logger.exception("后台RAG重新初始化任务失败")


@router.post("/reinitialize", status_code=status.HTTP_202_ACCEPTED, summary="触发RAG处理器的重新初始化")
async def reinitialize_rag(background_tasks: BackgroundTasks):
    """
    异步触发RAG处理器的重新初始化。
    这在解决外部依赖（如Ollama服务或数据文件）问题后非常有用。
    立即返回202 Accepted，初始化在后台进行。
    """
    if dependencies.rag_processor.status == RAGStatus.INITIALIZING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Reinitialization is already in progress."
        )

    background_tasks.add_task(reinitialize_task)
    return {"message": "RAG reinitialization process has been started in the background."}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_rag() -> RefreshResponse:
    """刷新RAG数据库端点。"""
    success, message = refresh_rag_database()
    if not success:
        # 将内部错误转换为对客户端友好的HTTP错误
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    return RefreshResponse(status="success", message=message)


@router.get("/status", response_model=StatusResponse)
async def rag_status() -> StatusResponse:
    """
    返回RAG处理器的当前状态。
    - UNINITIALIZED: 服务刚启动，尚未开始初始化。
    - INITIALIZING: 正在初始化中。
    - READY: 服务正常，可以接受请求。
    - ERROR: 初始化失败，附带错误信息。
    """
    if dependencies.rag_processor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RAG服务当前不可用，尚未初始化")
    if dependencies.rag_processor.status == RAGStatus.ERROR:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": dependencies.rag_processor.status.value, "message": dependencies.rag_processor.error_message}
        )
    try:
        # 从单例实例中获取配置信息来构建响应
        db_exists = os.path.exists(dependencies.rag_processor.chroma_db_dir)
        data = {
            "initialized": True,
            "database_exists": db_exists,
            "database_path": dependencies.rag_processor.settings.chroma_db_dir,
        }
        return StatusResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取RAG状态时发生异常: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest) -> QueryResponse:
    """查询RAG数据库。"""
    # 1. 安全检查
    if dependencies.rag_processor is None or dependencies.rag_processor.status != RAGStatus.READY:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"RAG服务当前不可用，当前状态{dependencies.rag_processor.status.value}")

    query_text = request.query
    if not query_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="查询参数 'query' 不能为空")

    try:
        # 2. 将核心任务委托给单例处理器
        retrieved_docs = await dependencies.rag_processor.retrieve_context(query_text)

        # 3. 格式化响应
        results = [{"content": doc.page_content, "metadata": doc.metadata} for doc in retrieved_docs]
        data = {"query": query_text, "results": results, "count": len(results)}

        return QueryResponse(status="success", data=data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"查询RAG数据库时发生异常: {str(e)}")


@router.post("/upload-videos", response_model=UploadResponse)
async def upload_videos_csv(file: UploadFile = File(...)) -> UploadResponse:
    """上传videos.csv文件并更新RAG数据库"""
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
        success, _ = refresh_rag_database()

        if not success:
            # 如果刷新失败，恢复备份文件
            if os.path.exists(backup_path):
                shutil.move(backup_path, settings.rag.videos_data_path)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传成功但刷新RAG数据库失败，已恢复原文件")

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


def refresh_rag_database() -> Tuple[bool, str]:
    """刷新RAG数据库"""
    try:
        if dependencies.rag_processor is None:
            return False, "RAG处理器未初始化"
        success = dependencies.rag_processor.refresh_database()
        if success:
            return True, "RAG数据库已成功刷新"
        else:
            return False, "刷新RAG数据库失败"
    except Exception as e:
        return False, f"刷新RAG数据库时发生异常: {str(e)}"


def validate_csv_structure(file_path: str) -> Tuple[bool, str]:
    """验证CSV文件结构是否正确"""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['type', 'name', 'aliases', 'description', 'filename']

        # 检查是否包含所有必需的列
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"缺少必需的列: {missing_columns}"

        # 检查type列是否都是'video'
        if not all(df['type'] == 'video'):
            return False, "type列必须全部为'video'"

        # 检查是否有空值
        if df.isnull().any().any():
            return False, "CSV文件中不能包含空值"

        return True, "CSV文件结构正确"
    except Exception as e:
        return False, f"验证CSV文件时发生错误: {str(e)}"
