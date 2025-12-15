from fastapi import APIRouter, HTTPException, status
from loguru import logger

from src.api.schemas import StatusResponse
from src.core import dependencies
from src.module.vad.base_vad_processor import VADStatus

router = APIRouter(
    prefix="/vad",
    tags=["VAD"]
)

@router.get("/status", response_model=StatusResponse)
async def vad_status() -> StatusResponse:
    """
    返回VAD处理器的当前状态。
    - UNINITIALIZED: 服务刚启动，尚未开始初始化。
    - INITIALIZING: 正在初始化中。
    - READY: 服务正常，可以接受请求。
    - ERROR: 初始化失败，附带错误信息。
    """
    try:
        if dependencies.vad_core is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VAD服务当前不可用，尚未初始化")

        status_value = dependencies.vad_core.status.value
        data = {
            "status": status_value,
            "initialized": dependencies.vad_core.status == VADStatus.READY,
            "error_message": dependencies.vad_core.error_message if dependencies.vad_core.status == VADStatus.ERROR else None
        }

        return StatusResponse(status="success", data=data)
    except Exception as e:
        logger.exception("获取VAD状态时发生异常")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取VAD状态时发生异常: {str(e)}")

@router.post("/reinitialize", response_model=StatusResponse)
async def vad_reinitialize() -> StatusResponse:
    """
    重新初始化VAD处理器，可用于从任何状态恢复。
    """
    try:
        if dependencies.vad_core is None:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="VAD服务当前不可用，尚未初始化")

        await dependencies.vad_core.initialize()

        return StatusResponse(
            status="success",
            data={
                "message": "VAD处理器重新初始化完成",
                "current_status": dependencies.vad_core.status.value
            }
        )
    except Exception as e:
        logger.exception("重新初始化VAD处理器时发生异常")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"重新初始化VAD处理器时发生异常: {str(e)}")