"""
LLM函数调用工具定义 - Modern Structured Output Approach.
"""
import json
from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field
from langchain_core.tools import tool


class CommandAction(str, Enum):
    """命令动作类型枚举"""
    OPEN = "open"
    OPEN_MEDIA = "open_media"
    CLOSE = "close"
    SEEK = "seek"
    SET_VOLUME = "set_volume"
    ADJUST_VOLUME = "adjust_volume"
    UPDATE_LOCATION = "update_location"
    ERROR = "error"


class ExhibitionCommand(BaseModel):
    """Smart exhibition hall command structure for structured output."""
    action: str = Field(description="Command action to perform")
    target: Optional[str] = Field(default=None, description="Target device or screen name")
    device: Optional[str] = Field(default=None, description="Device identifier")
    value: Optional[str | int] = Field(default=None, description="Command value (string or integer)")


class ExecutableCommand(BaseModel):
    """可执行的命令包，包含完整上下文"""
    user_id: str = Field(description="执行命令的用户ID")
    commands: list[ExhibitionCommand] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def get_local_commands(self) -> list[ExhibitionCommand]:
        """获取需要本地执行的命令（如更新位置）"""
        return [cmd for cmd in self.commands if cmd.action == CommandAction.UPDATE_LOCATION.value]
    
    def get_remote_commands(self) -> list[ExhibitionCommand]:
        """获取需要发送到前端的命令"""
        return [cmd for cmd in self.commands if cmd.action != CommandAction.UPDATE_LOCATION.value]
    
    def to_websocket_payload(self) -> str:
        """转换为 WebSocket 发送的 JSON 格式"""
        remote_cmds = self.get_remote_commands()
        return json.dumps({
            "user_id": self.user_id,
            "commands": [cmd.model_dump() for cmd in remote_cmds]
        }, ensure_ascii=False)


class OpenMediaInput(BaseModel):
    """Input for open media command."""
    target: str = Field(description="要打开的媒体资源名称")
    device: str = Field(description="要在其上打开媒体的屏幕名称")


class ControlDoorInput(BaseModel):
    """Input for control door command."""
    target: str = Field(description="门的全称")
    action: Literal["open", "close"] = Field(description="要执行的操作：open（打开）或close（关闭）")


class SeekVideoInput(BaseModel):
    """Input for seek video command."""
    device: str = Field(description="要跳转进度的屏幕名称")
    value: int = Field(description="跳转到的秒数")


class SetVolumeInput(BaseModel):
    """Input for set volume command."""
    device: str = Field(description="要设置音量的屏幕名称")
    value: int = Field(
        ge=0,
        le=100,
        description="音量值（0-100）"
    )


class AdjustVolumeInput(BaseModel):
    """Input for adjust volume command."""
    device: str = Field(description="要调整音量的屏幕名称")
    value: Literal["up", "down"] = Field(description="音量调整方向：up（提高）或down（降低）")


class UpdateLocationInput(BaseModel):
    """Input for update location command."""
    target: str = Field(description="用户移动到的目标区域名称")


@tool(args_schema=OpenMediaInput)
def open_media(target: str, device: str) -> ExhibitionCommand:
    """打开指定的媒体资源"""
    return ExhibitionCommand(
        action="open_media",
        target=target,
        device=device,
        value=None
    )


@tool(args_schema=ControlDoorInput)
def control_door(target: str, action: Literal["open", "close"]) -> ExhibitionCommand:
    """控制门的开关"""
    return ExhibitionCommand(
        action=action,
        target=target,
        device=None,
        value=None
    )


@tool(args_schema=SeekVideoInput)
def seek_video(device: str, value: int) -> ExhibitionCommand:
    """跳转到视频的指定时间点"""
    return ExhibitionCommand(
        action="seek",
        target=None,
        device=device,
        value=value
    )


@tool(args_schema=SetVolumeInput)
def set_volume(device: str, value: int) -> ExhibitionCommand:
    """设置音量到指定的绝对值"""
    return ExhibitionCommand(
        action="set_volume",
        target=None,
        device=device,
        value=value
    )


@tool(args_schema=AdjustVolumeInput)
def adjust_volume(device: str, value: Literal["up", "down"]) -> ExhibitionCommand:
    """相对提高或降低音量"""
    return ExhibitionCommand(
        action="adjust_volume",
        target=None,
        device=device,
        value=value
    )


@tool(args_schema=UpdateLocationInput)
def update_location(target: str) -> ExhibitionCommand:
    """更新用户当前的位置"""
    return ExhibitionCommand(
        action="update_location",
        target=target,
        device=None,
        value=None
    )


def get_tools():
    """获取LLM函数调用的工具列表（现代结构化输出方法）。"""
    return [
        open_media,
        control_door,
        seek_video,
        set_volume,
        adjust_volume,
        update_location
    ]


def get_exhibition_command_schema():
    """获取展览厅命令的Pydantic模型模式。"""
    return ExhibitionCommand