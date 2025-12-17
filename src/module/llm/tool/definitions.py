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
    CONTROL_DOOR = "control_door"
    CONTROL_DEVICE = "control_device"
    ERROR = "error"


class ExhibitionCommand(BaseModel):
    """Smart exhibition hall command structure for structured output."""
    action: str = Field(description="需要执行的具体命令动作，必须是预定义的合法动作之一")
    device: Optional[str] = Field(default=None, description="命令的目标设备标识符（如果适用）")
    value: Optional[str | int] = Field(default=None, description="命令的具体参数值（字符串或整数）")


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
    device: str = Field(description="媒体资源的名称或路径")
    value: str = Field(description="执行播放的设备标识符")


class ControlDoorInput(BaseModel):
    """Input for control door command."""
    device: str = Field(description="目标门的标识符")
    value: Literal["open", "close"] = Field(description="控制动作：'open' 表示打开，'close' 表示关闭")


class SeekVideoInput(BaseModel):
    """Input for seek video command."""
    device: str = Field(description="需要跳转进度的设备标识符")
    value: int = Field(description="目标时间点（单位：秒）")


class SetVolumeInput(BaseModel):
    """Input for set volume command."""
    device: str = Field(description="要设置音量的设备名称")
    value: int = Field(ge=0, le=100, description="音量值（0-100）")


class AdjustVolumeInput(BaseModel):
    """Input for adjust volume command."""
    device: str = Field(description="要调整音量的设备名称")
    value: Literal["up", "down"] = Field(description="音量调整方向：up（提高）或down（降低）")


class ControlDeviceInput(BaseModel):
    """Input for control device command."""
    name: str = Field(description="设备名称")
    type: str = Field(description="设备类型")
    command: str = Field(description="设备的自定义命令，必须是该设备的自定义命令之一")


class UpdateLocationInput(BaseModel):
    """Input for update location command."""
    value: str = Field(description="用户移动到的区域名称")


@tool(args_schema=OpenMediaInput)
def open_media(device: str, value: str) -> ExhibitionCommand:
    """打开指定的媒体资源"""
    from src.core import dependencies
    if not dependencies.data_service.media_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Media '{device}' not found."
        )
    if not dependencies.data_service.device_exists(value):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Device '{value}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.OPEN_MEDIA.value,
        device=device,
        value=value
    )


@tool(args_schema=ControlDoorInput)
def control_door(device: str, value: Literal["open", "close"]) -> ExhibitionCommand:
    """控制门的开关"""
    from src.core import dependencies
    if not dependencies.data_service.door_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Door '{device}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.CONTROL_DOOR.value,
        device=device,
        value=value
    )


@tool(args_schema=SeekVideoInput)
def seek_video(device: str, value: int) -> ExhibitionCommand:
    """跳转到视频的指定时间点"""
    from src.core import dependencies
    if not dependencies.data_service.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Device '{device}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.SEEK.value,
        device=device,
        value=value
    )


@tool(args_schema=SetVolumeInput)
def set_volume(device: str, value: int) -> ExhibitionCommand:
    """设置音量到指定的绝对值"""
    from src.core import dependencies
    if not dependencies.data_service.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Device '{device}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.SET_VOLUME.value,
        device=device,
        value=value
    )


@tool(args_schema=AdjustVolumeInput)
def adjust_volume(device: str, value: Literal["up", "down"]) -> ExhibitionCommand:
    """相对提高或降低音量"""
    from src.core import dependencies
    if not dependencies.data_service.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Device '{device}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.ADJUST_VOLUME.value,
        device=device,
        value=value
    )


@tool(args_schema=ControlDeviceInput)
def control_device(name: str, type: str, command: str) -> ExhibitionCommand:
    """控制设备执行特定命令"""
    from src.core import dependencies
    if not dependencies.data_service.device_exists(name):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Device '{name}' not found."
        )
    
    # 验证命令是否是该设备支持的命令
    device_info = dependencies.data_service.get_device_info(name)
    if device_info:
        supported_commands = device_info.get("command", [])
        if supported_commands and command not in supported_commands:
            return ExhibitionCommand(
                action=CommandAction.ERROR.value,
                value=f"Command '{command}' is not supported by device '{name}'. Supported commands: {supported_commands}"
            )

    return ExhibitionCommand(
        action=CommandAction.CONTROL_DEVICE.value,
        device=name,
        value=command
    )


@tool(args_schema=UpdateLocationInput)
def update_location(value: str) -> ExhibitionCommand:
    """更新用户当前的位置"""
    from src.core import dependencies
    if not dependencies.data_service.area_exists(value):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            value=f"Area '{value}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.UPDATE_LOCATION.value,
        device=None,
        value=value
    )


def get_tools():
    """获取LLM函数调用的工具列表（现代结构化输出方法）。"""
    return [
        open_media,
        control_door,
        control_device,
        seek_video,
        set_volume,
        adjust_volume,
        update_location
    ]


def get_exhibition_command_schema():
    """获取展览厅命令的Pydantic模型模式。"""
    return ExhibitionCommand