"""AEP Central Control System API Client.

This module provides an HTTP client for sending voice commands to the AEP 
central control system via POST /aep/voice/command endpoint.
"""

import hashlib
import uuid

import httpx
from loguru import logger
from pydantic import BaseModel

from src.config.config import get_settings


class AEPVoiceCommandRequest(BaseModel):
    """Request model for /aep/voice/command endpoint."""
    cmdId: str
    name: str
    type: str
    subType: str = ""
    command: str = ""
    param: str = ""
    view: str = ""
    resource: str = ""
    sign: str = ""


class AEPVoiceCommandResponse(BaseModel):
    """Response model from /aep/voice/command endpoint."""
    success: bool
    message: str
    code: int
    result: str | None = None
    timestamp: int
    device_name: str | None = None


class AEPClient:
    """Client for AEP Central Control System API."""

    def __init__(self):
        settings = get_settings()
        self._base_url = settings.aep.base_url.rstrip("/")
        self._salt = settings.aep.sign_salt
        self._timeout = settings.aep.request_timeout

    def _calculate_sign(self, params: dict) -> str:
        """Calculate MD5 sign from sorted params with salt.
        
        按Key字母顺序以key1=value1&key2=value2格式拼接为字符串，再取加盐的MD5。
        """
        # Exclude 'sign' field, sort by key alphabetically
        sorted_items = sorted(
            ((k, v) for k, v in params.items() if k != "sign"),
            key=lambda x: x[0]
        )
        # Build key1=value1&key2=value2 string
        sign_string = "&".join(f"{k}={v}" for k, v in sorted_items)
        # Add salt and calculate MD5
        sign_string_with_salt = sign_string + self._salt
        return hashlib.md5(sign_string_with_salt.encode()).hexdigest().upper()

    async def send_voice_command(
            self,
            name: str,
            type_: str,
            sub_type: str = "",
            command: str = "",
            view: str = "",
            resource: str = "",
            param: str | int | None = ""
    ) -> AEPVoiceCommandResponse:
        """Send voice command to AEP central control system.

        Returns:
            AEPVoiceCommandResponse with success status and device_name
        """
        request_id = str(uuid.uuid4())

        # Build request params (without sign)
        params = {
            "cmdId": request_id,
            "name": name,
            "type": type_,
            "subType": sub_type,
            "command": command,
            "param": param if param is not None else "",
            "view": view,
            "resource": resource
        }

        # Calculate sign
        sign = self._calculate_sign(params)
        params["sign"] = sign

        logger.info("[AEP] 发送语音命令: {params}", params=params)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._base_url,
                    json=params
                )
                response.raise_for_status()
                data = response.json()
            logger.info("[AEP] 返回: {data}", data=data)
            result = AEPVoiceCommandResponse(**data)

            if result.success:
                if result.result and not result.device_name:
                    result.device_name = result.result
                
                logger.info("[AEP] 命令发送成功: device_name={device_name}", device_name=result.result)
            else:
                logger.warning("[AEP] 命令发送失败: code={code}, message={message}", code=result.code, message=result.message)

            return result

        except httpx.HTTPStatusError as e:
            logger.error("[AEP] HTTP错误: {status} - {text}", status=e.response.status_code, text=e.response.text)
            return AEPVoiceCommandResponse(
                success=False,
                message=f"HTTP错误: {e.response.status_code}",
                code=e.response.status_code,
                result=None,
                timestamp=0
            )
        except httpx.RequestError as e:
            logger.error("[AEP] 网络请求错误: {error}", error=str(e))
            return AEPVoiceCommandResponse(
                success=False,
                message=f"网络请求错误: {str(e)}",
                code=500,
                result=None,
                timestamp=0
            )
        except Exception as e:
            logger.exception("[AEP] 未知错误")
            return AEPVoiceCommandResponse(
                success=False,
                message=f"未知错误: {str(e)}",
                code=500,
                result=None,
                timestamp=0
            )


# Singleton instance
_aep_client: AEPClient | None = None


def get_aep_client() -> AEPClient:
    """Get or create AEP client singleton."""
    global _aep_client
    if _aep_client is None:
        _aep_client = AEPClient()
    return _aep_client
