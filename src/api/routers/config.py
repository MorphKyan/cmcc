from typing import Any

from fastapi import APIRouter, HTTPException, status
from loguru import logger
from pydantic import BaseModel

from src.api.schemas import ConfigResponse
from src.config.config import get_settings

router = APIRouter(
    prefix="/api/config",
    tags=["Configuration"]
)


class ConfigItem(BaseModel):
    key: str
    value: Any
    category: str
    description: str


@router.get("/current", response_model=ConfigResponse)
async def get_current_config() -> ConfigResponse:
    """
    获取当前后端服务的配置。
    """
    try:
        settings = get_settings()

        # 组织配置数据按类别分组
        config_data = {
            "vad": {},
            "asr": {},
            "rag": {},
            "llm": {},
            "volcengine": {}
        }

        # VAD 配置
        config_data["vad"] = {
            "chunk_size": settings.vad.chunk_size,
            "sample_rate": settings.vad.sample_rate,
            "model": settings.vad.model,
            "max_single_segment_time": settings.vad.max_single_segment_time
        }

        # ASR 配置
        config_data["asr"] = {
            "model": settings.asr.model,
            "language": settings.asr.language,
            "use_itn": settings.asr.use_itn,
            "batch_size_s": settings.asr.batch_size_s,
            "merge_vad": settings.asr.merge_vad,
            "merge_length_s": settings.asr.merge_length_s
        }

        # RAG 配置
        config_data["rag"] = {
            "videos_data_path": settings.rag.videos_data_path,
            "chroma_db_dir": settings.rag.chroma_db_dir,
            "ollama_base_url": settings.rag.ollama_base_url,
            "ollama_embedding_model": settings.rag.ollama_embedding_model,
            "top_k_results": settings.rag.top_k_results
        }

        # LLM 配置
        config_data["llm"] = {
            "provider": settings.llm.provider,
            "ollama_model": settings.llm.ollama_model,
            "ollama_base_url": settings.llm.ollama_base_url,
            "modelscope_model": settings.llm.modelscope_model,
            "modelscope_base_url": settings.llm.modelscope_base_url,
            "max_validation_retries": settings.llm.max_validation_retries,
            "retry_delay": settings.llm.retry_delay,
            "request_timeout": settings.llm.request_timeout,
            "connection_timeout": settings.llm.connection_timeout,
            "max_network_retries": settings.llm.max_network_retries,
            "base_retry_delay": settings.llm.base_retry_delay,
            "max_retry_delay": settings.llm.max_retry_delay
        }

        # 火山引擎配置
        config_data["volcengine"] = {
            "ark_api_key": "[REDACTED]",  # 不显示API密钥
            "ark_base_url": settings.volcengine.ark_base_url,
            "llm_model_name": settings.volcengine.llm_model_name,
            "request_timeout": settings.volcengine.request_timeout,
            "connection_timeout": settings.volcengine.connection_timeout,
            "max_network_retries": settings.volcengine.max_network_retries,
            "base_retry_delay": settings.volcengine.base_retry_delay,
            "max_retry_delay": settings.volcengine.max_retry_delay
        }

        return ConfigResponse(
            status="success",
            data=config_data,
            message="成功获取当前配置"
        )

    except Exception as e:
        logger.exception("获取配置时发生错误")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配置时发生错误: {str(e)}"
        )