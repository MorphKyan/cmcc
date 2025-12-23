"""
LLM函数调用工具定义 - Modern Structured Output Approach.
"""
from enum import Enum
from typing import Literal, Optional

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class CommandAction(str, Enum):
    """命令动作类型枚举"""
    OPEN_MEDIA = "open_media"
    SEEK = "seek"
    SET_VOLUME = "set_volume"
    ADJUST_VOLUME = "adjust_volume"
    UPDATE_LOCATION = "update_location"
    CONTROL_DOOR = "control_door"
    DEVICE_CUSTOM_COMMAND = "device_custom_command"
    CONTROL_VIDEO = "control_video"
    CONTROL_PPT = "control_ppt"
    POWER_CONTROL = "power_control"
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
    command: Literal["open", "close"] = Field(description="控制动作：'open' 表示打开，'close' 表示关闭")


class SeekVideoInput(BaseModel):
    """Input for seek video command."""
    device: str = Field(description="需要跳转进度的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    value: int = Field(description="目标时间点（单位：秒），由用户指定")


class SetVolumeInput(BaseModel):
    """Input for set volume command."""
    device: str = Field(description="要设置音量的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    value: int = Field(ge=0, le=100, description="音量值（0-100），由用户指定。如果用户请求静音，则 value=0")


class AdjustVolumeInput(BaseModel):
    """Input for adjust volume command."""
    device: str = Field(description="要调整音量的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    param: Literal["up", "down"] = Field(description="音量调整方向：up（提高）或down（降低）")


class ControlDeviceInput(BaseModel):
    """Input for control device command."""
    device: str = Field(description="设备名称，必须是知识库中 device 列表返回的精确 name 值")
    device_type: str = Field(description="设备类型，必须是知识库中该设备对应的 type 字段值")
    command: str = Field(description="设备的自定义命令，必须是知识库中该设备 command 列表中的某个精确值")


class ControlVideoInput(BaseModel):
    """Input for video playback control command."""
    device: str = Field(description="需要控制播放的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    command: Literal["暂停", "继续"] = Field(description="播放控制动作：'暂停' 表示暂停，'继续' 表示继续播放")


class ControlPPTInput(BaseModel):
    """Input for PPT control command."""
    device: str = Field(description="需要控制PPT的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    command: Literal["首页", "上一页", "下一页", "末页", "PPT跳转"] = Field(description="PPT控制动作，'PPT跳转'指跳转到指定页")
    param: Optional[int] = Field(default=None, description="跳转的目标页码，仅当 value='PPT跳转' 时需要指定")


class ControlPowerInput(BaseModel):
    """Input for power control command."""
    device: str = Field(description="需要控制开关机的设备名称，必须是知识库中 device 列表返回的精确 name 值")
    command: Literal["开机", "关机"] = Field(description="电源控制动作：'开机' 表示启动设备，'关机' 表示关闭设备")


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
        command="播放",
        resource=value
    )


@tool(args_schema=ControlDoorInput)
def control_door(door: str, command: Literal["open", "close"]) -> ExhibitionCommand:
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
        command=command
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
        command="视频跳转",
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
        command="音量",
        params=value
    )


@tool(args_schema=AdjustVolumeInput)
def adjust_volume(device: str, param: Literal["up", "down"]) -> ExhibitionCommand:
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
        command="音量",
        params=param
    )


@tool(args_schema=ControlDeviceInput)
def device_custom_command(device: str, device_type: str, command: str) -> ExhibitionCommand:
    """控制设备执行定义在其 command 列表中的自定义命令。仅当设备有特定的自定义命令时使用。注意：设备的"打开/关闭"、"开机/关机"操作请使用 control_power 函数。"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}

    # 验证命令是否是该设备支持的命令
    supported_commands = device_info.get("command", [])
    if supported_commands and command not in supported_commands:
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Command '{command}' is not supported by device '{device}'. Supported commands: {supported_commands}"
        )

    return ExhibitionCommand(
        action=CommandAction.DEVICE_CUSTOM_COMMAND.value,
        device_name=device,
        device_type=device_info.get("type", "") or device_type,
        sub_type=device_info.get("subType", ""),
        command=command,
    )


@tool(args_schema=ControlVideoInput)
def control_video(device: str, command: Literal["暂停", "继续"]) -> ExhibitionCommand:
    """控制视频播放状态，当用户请求暂停或继续播放视频时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}

    return ExhibitionCommand(
        action=CommandAction.CONTROL_VIDEO.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        command=command
    )


@tool(args_schema=ControlPPTInput)
def control_ppt(device: str, command: Literal["首页", "上一页", "下一页", "末页", "PPT跳转"], param: int | None = None) -> ExhibitionCommand:
    """控制PPT演示文稿的翻页，当用户请求翻页、跳转到首页、末页或特定页时调用"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    # 如果是跳转操作，必须提供页码
    if command == "PPT跳转" and param is None:
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message="PPT跳转操作需要指定目标页码（param）"
        )

    device_info = ds.get_device_info(device) or {}

    # 对于 PPT跳转 操作，params 为页码；其他操作 params 为动作名称
    params_value = param if command == "PPT跳转" else None

    return ExhibitionCommand(
        action=CommandAction.CONTROL_PPT.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        command=command,
        params=params_value
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


@tool(args_schema=ControlPowerInput)
def control_power(device: str, command: Literal["开机", "关机"]) -> ExhibitionCommand:
    """控制设备的电源开关状态。当用户请求"打开电源"、"关闭电源"、"打开设备"、"关闭设备"、"开机"、"关机"、"启动"、"关掉"、"关(设备名)电源"、"(设备名)开机/关机"等操作时调用此函数。注意：设备的自定义命令不包括电源操作，所有涉及"电源"、"开机"、"关机"的请求都应使用此函数。"""
    from src.core import dependencies
    ds = dependencies.data_service

    if not ds.device_exists(device):
        return ExhibitionCommand(
            action=CommandAction.ERROR.value,
            message=f"Device '{device}' not found."
        )

    device_info = ds.get_device_info(device) or {}

    return ExhibitionCommand(
        action=CommandAction.POWER_CONTROL.value,
        device_name=device,
        device_type=device_info.get("type", ""),
        command=command
    )


def get_tools():
    """获取LLM函数调用的工具列表（现代结构化输出方法）。"""
    return [
        open_media,
        control_door,
        device_custom_command,
        seek_video,
        set_volume,
        adjust_volume,
        control_video,
        control_ppt,
        control_power,
        update_location
    ]


def get_exhibition_command_schema():
    """获取展览厅命令的Pydantic模型模式。"""
    return ExhibitionCommand
