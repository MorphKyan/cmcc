#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from loguru import logger
from src.core import dependencies

class ToolValidator:
    """
    工具参数验证器（单例模式）
    负责验证各种工具调用的参数是否有效
    直接从 dependencies 获取 data_service
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ToolValidator":
        """
        获取ToolValidator的单例实例

        Returns:
            ToolValidator单例实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_open_media_args(self, target: str, device: str) -> tuple[bool, str | None]:
        """
        验证打开媒体工具的参数

        Args:
            target: 媒体资源名称
            device: 设备名称

        Returns:
            (是否有效, 错误信息)
        """
        if not dependencies.data_service.media_exists(target):
            return False, f"Media '{target}' not found in media.csv"

        if not dependencies.data_service.device_exists(device):
            return False, f"Device '{device}' not found in devices.csv"

        return True, None

    def validate_control_door_args(self, target: str, action: str) -> tuple[bool, str | None]:
        """
        验证控制门工具的参数

        Args:
            target: 门名称
            action: 动作 (open/close)

        Returns:
            (是否有效, 错误信息)
        """
        if not dependencies.data_service.door_exists(target):
            return False, f"Door '{target}' not found in doors.csv"

        if action not in ["open", "close"]:
            return False, f"Invalid door action '{action}'. Must be 'open' or 'close'"

        return True, None

    def validate_device_args(self, device: str, tool_name: str) -> tuple[bool, str | None]:
        """
        验证需要设备参数的工具

        Args:
            device: 设备名称
            tool_name: 工具名称（用于错误信息）

        Returns:
            (是否有效, 错误信息)
        """
        if not dependencies.data_service.device_exists(device):
            return False, f"Device '{device}' not found in devices.csv for {tool_name} tool"

        return True, None

    def validate_update_location_args(self, target: str) -> tuple[bool, str | None]:
        """
        验证更新位置工具的参数

        Args:
            target: 区域名称

        Returns:
            (是否有效, 错误信息)
        """
        if not dependencies.data_service.area_exists(target):
            return False, f"Area '{target}' not found in areas.csv"

        return True, None

    def validate_tool_args(self, tool_name: str, tool_args: dict) -> tuple[bool, str | None]:
        """
        根据工具名称验证工具参数

        Args:
            tool_name: 工具名称
            tool_args: 工具参数字典

        Returns:
            (是否有效, 错误信息)
        """
        try:
            if tool_name == "open_media":
                target = tool_args.get("target", "")
                device = tool_args.get("device", "")
                return self.validate_open_media_args(target, device)

            elif tool_name == "control_door":
                target = tool_args.get("target", "")
                action = tool_args.get("action", "")
                return self.validate_control_door_args(target, action)

            elif tool_name in ["seek_video", "set_volume", "adjust_volume"]:
                device = tool_args.get("device", "")
                return self.validate_device_args(device, tool_name)

            elif tool_name == "update_location":
                target = tool_args.get("target", "")
                return self.validate_update_location_args(target)

            else:
                # 未知工具，默认通过验证
                return True, None

        except Exception as e:
            logger.error(f"Error validating tool '{tool_name}' arguments: {e}")
            return False, f"Validation error: {str(e)}"
