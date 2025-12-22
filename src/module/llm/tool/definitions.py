"""
LLM函数调用工具定义 - Modern Structured Output Approach.
"""
import json
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field
from langchain_core.tools import tool


class CommandAction(str, Enum):
    """命令动作类型枚举"""
    OPEN_MEDIA = "open_media"
    SEEK = "seek"
    SET_VOLUME = "set_volume"
    ADJUST_VOLUME = "adjust_volume"
    UPDATE_LOCATION = "update_location"
    CONTROL_DOOR = "control_door"
    CONTROL_DEVICE = "control_device"
    ERROR = "error"


class ExhibitionCommand(BaseModel):
    """Smart exhibition hall command structure for structured output.
    
    包含所有 AEP API 所需的字段，工具函数内部负责从 DataService 补全信息。
    """
    action: str = Field(description="需要执行的具体命令动作，必须是预定义的合法动作之一")
    message: Optional[str] = Field(default=None, description="错误提示")
    device_name: Optional[str] = Field(default=None, description="命令的目标设备名称")
    device_type: str = Field(default="", description="设备类型 (player/led/control)")
    sub_type: str = Field(default="", description="设备子类型")
    view: str = Field(default="", description="视窗名称")
    command: str = Field(default="", description="设备的自定义命令名称")
    params: Optional[str | int] = Field(default=None, description="命令的具体参数值（字符串或整数）")
    resource: str = Field(default="", description="资源名称")


class OpenMediaInput(BaseModel):
    """Input for open media command."""
    device: str = Field(description="执行播放的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    view: Optional[str] = Field(default=None, description="视窗名称，必须是知识库中该设备 view 列表中的某个值，用户未指定时留空")
    value: str = Field(description="媒体资源名称，必须是知识库中 media 列表返回的精确 name 值")


class ControlDoorInput(BaseModel):
    """Input for control door command."""
    device: str = Field(description="目标门的名称，必须是知识库中 door 列表返回的精确 name 值")
    value: Literal["open", "close"] = Field(description="控制动作：'open' 表示打开，'close' 表示关闭")


class SeekVideoInput(BaseModel):
    """Input for seek video command."""
    device: str = Field(description="需要跳转进度的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    value: int = Field(description="目标时间点（单位：秒），由用户指定")


class SetVolumeInput(BaseModel):
    """Input for set volume command."""
    device: str = Field(description="要设置音量的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    value: int = Field(ge=0, le=100, description="音量值（0-100），由用户指定")


class AdjustVolumeInput(BaseModel):
    """Input for adjust volume command."""
    device: str = Field(description="要调整音量的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    value: Literal["up", "down"] = Field(description="音量调整方向：up（提高）或down（降低）")


class ControlDeviceInput(BaseModel):
    """Input for control device command."""
    name: str = Field(description="设备名称，必须是知识库中 device 列表返回的精确 name 值")
    type: str = Field(description="设备类型，必须是知识库中该设备对应的 type 字段值")
    command: str = Field(description="设备的自定义命令，必须是知识库中该设备 command 列表中的某个精确值")


class UpdateLocationInput(BaseModel):
    """Input for update location command."""
    value: str = Field(description="用户移动到的区域名称，必须是知识库中 area 列表返回的精确 name 值")


@tool(args_schema=OpenMediaInput)
def open_media(device: str, value: str, view: str | None = None) -> ExhibitionCommand:
    """在设备上播放指定的媒体资源，适用于用户请求播放视频、音频或展示其他内容时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.media_exists(value):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Media '{value}' not found."
        )
    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}
    view_list = device_info.get("view", [])

    # 校验 view 是否存在于设备的 view 列表中
    if view and view not in view_list:
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"View '{view}' not found in device '{device}'. Available views: {view_list}"
        )

    return ExhibitionCommand(
        action=CommandAction.OPEN_MEDIA.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        view=view or "",
        resource=value
    )


@tool(args_schema=ControlDoorInput)
def control_door(door: str, value: Literal["open", "close"]) -> ExhibitionCommand:
    """控制展厅门的开关状态，当用户请求打开或关闭某扇门时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.door_exists(door):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Door '{door}' not found."
        )

    door_info = ds.get_door_info(door) or {}

    return ExhibitionCommand(
        action=CommandAction.CONTROL_DOOR.value,
        device_name=door,
        device_type=door_info.get("type", ""),
        params=value
    )


@tool(args_schema=SeekVideoInput)
def seek_video(device: str, value: int) -> ExhibitionCommand:
    """跳转到视频的指定时间点，当用户请求快进、后退或跳到特定时间时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}

    return ExhibitionCommand(
        action=CommandAction.SEEK.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        params=value
    )


@tool(args_schema=SetVolumeInput)
def set_volume(device: str, value: int) -> ExhibitionCommand:
    """设置设备音量到指定的绝对值，当用户请求将音量设置为具体数值时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}

    return ExhibitionCommand(
        action=CommandAction.SET_VOLUME.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        params=value
    )


@tool(args_schema=AdjustVolumeInput)
def adjust_volume(device: str, value: Literal["up", "down"]) -> ExhibitionCommand:
    """相对调整设备音量，当用户请求调大、调小、增加或降低音量但未指定具体数值时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}

    return ExhibitionCommand(
        action=CommandAction.ADJUST_VOLUME.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        params=value
    )


@tool(args_schema=ControlDeviceInput)
def control_device(name: str, device_type: str, command: str) -> ExhibitionCommand:
    """控制设备执行预定义的自定义命令，如开机、关机、切换模式等，适用于非播放类的设备操作"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(name):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{name}' not found."
        )

    device_info = ds.get_device_info(name) or {}

    # 验证命令是否是该设备支持的命令
    supported_commands = device_info.get("command", [])
    if supported_commands and command not in supported_commands:
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Command '{command}' is not supported by device '{name}'. Supported commands: {supported_commands}"
        )

    return ExhibitionCommand(
        action=CommandAction.CONTROL_DEVICE.value,
        device_name=name,
        device_type=device_info.get("type", "") or device_type,
        sub_type=device_info.get("subType", ""),
        command=command,
    )


@tool(args_schema=UpdateLocationInput)
def update_location(value: str) -> ExhibitionCommand:
    """记录用户移动到新区域，当调用的设备包含区域信息时调用"""
    from src.core import dependencies
    if not dependencies.data_service.area_exists(value):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Area '{value}' not found."
        )

    return ExhibitionCommand(
        action=CommandAction.UPDATE_LOCATION.value,
        message=value
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
