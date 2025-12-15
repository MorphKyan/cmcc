import os

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from loguru import logger

from src.api.schemas import RefreshResponse, StatusResponse, QueryResponse, QueryRequest
from src.core import dependencies
from src.module.rag.base_rag_processor import RAGStatus

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
    success = await dependencies.rag_processor.refresh_database()
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="刷新RAG数据库失败")
    return RefreshResponse(status="success", message="刷新RAG数据库失败")


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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"RAG服务当前不可用，当前状态{dependencies.rag_processor.status.value}")

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
