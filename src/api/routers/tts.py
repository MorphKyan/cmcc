from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from loguru import logger

from src.core import dependencies

router = APIRouter(
    prefix="/tts",
    tags=["Text to Speech"]
)

class TTSRequest(BaseModel):
    """TTS 请求模型"""
    text: str


@router.post("/generate", summary="生成文字语音反馈")
async def generate_speech(request: TTSRequest):
    """
    接收文字，使用本地的 TTS 引擎生成语音，并直接返回 WAV 音频二进制流。
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    if dependencies.tts_service is None:
        logger.error("TTS Service is not initialized.")
        raise HTTPException(status_code=503, detail="TTS service unavailable")

    # 执行同步方法，如果是真正的异步框架建议搭配 asyncio.to_thread 避免阻塞主事件循环
    # 但考虑到生成非常快 (0.x秒) 这里也可以直接调用
    import asyncio
    audio_bytes = await asyncio.to_thread(dependencies.tts_service.generate_audio_bytes, request.text)
    
    if not audio_bytes:
        logger.error(f"Failed to generate TTS audio for text: {request.text}")
        raise HTTPException(status_code=500, detail="Audio generation failed")
        
    # 直接返回 WAV 数据
    return Response(content=audio_bytes, media_type="audio/wav")
