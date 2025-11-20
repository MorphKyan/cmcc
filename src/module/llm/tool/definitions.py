"""
LLM函数调用工具定义 - Modern Structured Output Approach.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class ExhibitionCommand(BaseModel):
    """Smart exhibition hall command structure for structured output."""
    action: str = Field(description="Command action to perform")
    target: Optional[str] = Field(default=None, description="Target device or screen name")
    device: Optional[str] = Field(default=None, description="Device identifier")
    value: Optional[str | int] = Field(default=None, description="Command value (string or integer)")


class PlayVideoInput(BaseModel):
    """Input for play video command."""
    target: str = Field(description="要播放的视频文件名filename")
    device: str = Field(description="要在其上播放视频的屏幕名称")


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


@tool(args_schema=PlayVideoInput)
def play_video(target: str, device: str) -> ExhibitionCommand:
    """播放指定的视频文件"""
    return ExhibitionCommand(
        action="play",
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
        play_video,
        control_door,
        seek_video,
        set_volume,
        adjust_volume,
        update_location
    ]


def get_exhibition_command_schema():
    """获取展览厅命令的Pydantic模型模式。"""
    return ExhibitionCommand