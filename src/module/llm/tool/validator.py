"""LLM函数调用参数验证模块。

根据CSV数据中的可用资源验证函数调用参数。
"""
import json
from typing import Any

from .types import ToolCall, ValidationResult
from src.core.csv_loader import CSVLoader


class ToolValidator:
    """LLM函数调用参数验证器。

    验证请求的资源（视频、门、屏幕）是否在CSV数据中存在。
    """

    def __init__(self):
        """初始化验证器。"""
        self.csv_loader = CSVLoader()

    def validate_function_calls(self, tool_calls: list[ToolCall]) -> ValidationResult:
        """验证函数调用列表。

        Args:
            tool_calls: LLM输出的函数调用列表

        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []

        for i, tool_call in enumerate(tool_calls):
            function_name = tool_call.get('type')
            arguments = tool_call.get('args', {})

            if function_name == "play_video":
                is_valid, error = self._validate_play_video(arguments)
                if not is_valid:
                    errors.append(f"Function call {i+1} (play_video): {error}")
            elif function_name == "control_door":
                is_valid, error = self._validate_control_door(arguments)
                if not is_valid:
                    errors.append(f"Function call {i+1} (control_door): {error}")
            elif function_name == "seek_video":
                is_valid, error = self._validate_seek_video(arguments)
                if not is_valid:
                    errors.append(f"Function call {i+1} (seek_video): {error}")
            elif function_name == "set_volume":
                is_valid, error = self._validate_set_volume(arguments)
                if not is_valid:
                    errors.append(f"Function call {i+1} (set_volume): {error}")
            elif function_name == "adjust_volume":
                is_valid, error = self._validate_adjust_volume(arguments)
                if not is_valid:
                    errors.append(f"Function call {i+1} (adjust_volume): {error}")

        return len(errors) == 0, errors

    def _validate_play_video(self, args: dict[str, Any]) -> tuple[bool, str]:
        """验证play_video函数参数。

        Args:
            args: 函数参数字典

        Returns:
            (是否有效, 错误消息)
        """
        target = args.get("target")
        device = args.get("device")

        if not target:
            return False, "缺少必需的'target'参数"

        if not device:
            return False, "缺少必需的'device'参数"

        if not self.csv_loader.video_exists(target):
            available_videos = self.csv_loader.get_all_videos()
            return False, f"视频'{target}'不存在。可用视频: {', '.join(available_videos)}"

        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"屏幕'{device}'不存在。可用屏幕: {', '.join(available_screens)}"

        return True, ""

    def _validate_control_door(self, args: dict[str, Any]) -> tuple[bool, str]:
        """验证control_door函数参数。

        Args:
            args: 函数参数字典

        Returns:
            (是否有效, 错误消息)
        """
        target = args.get("target")
        action = args.get("action")

        if not target:
            return False, "缺少必需的'target'参数"

        if not action:
            return False, "缺少必需的'action'参数"

        if action not in ["open", "close"]:
            return False, f"无效操作'{action}'，必须是'open'或'close'"

        if not self.csv_loader.door_exists(target):
            available_doors = self.csv_loader.get_all_doors()
            return False, f"门'{target}'不存在。可用门: {', '.join(available_doors)}"

        return True, ""

    def _validate_seek_video(self, args: dict[str, Any]) -> tuple[bool, str]:
        """验证seek_video函数参数。

        Args:
            args: 函数参数字典

        Returns:
            (是否有效, 错误消息)
        """
        device = args.get("device")
        value = args.get("value")

        if not device:
            return False, "缺少必需的'device'参数"

        if value is None:
            return False, "缺少必需的'value'参数"

        if not isinstance(value, int) or value < 0:
            return False, f"无效的'value'参数: {value}，必须是非负整数"

        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"屏幕'{device}'不存在。可用屏幕: {', '.join(available_screens)}"

        return True, ""

    def _validate_set_volume(self, args: dict[str, Any]) -> tuple[bool, str]:
        """验证set_volume函数参数。

        Args:
            args: 函数参数字典

        Returns:
            (是否有效, 错误消息)
        """
        device = args.get("device")
        value = args.get("value")

        if not device:
            return False, "缺少必需的'device'参数"

        if value is None:
            return False, "缺少必需的'value'参数"

        if not isinstance(value, int) or value < 0 or value > 100:
            return False, f"无效的'value'参数: {value}，必须是0-100之间的整数"

        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"屏幕'{device}'不存在。可用屏幕: {', '.join(available_screens)}"

        return True, ""

    def _validate_adjust_volume(self, args: dict[str, Any]) -> tuple[bool, str]:
        """验证adjust_volume函数参数。

        Args:
            args: 函数参数字典

        Returns:
            (是否有效, 错误消息)
        """
        device = args.get("device")
        value = args.get("value")

        if not device:
            return False, "缺少必需的'device'参数"

        if not value:
            return False, "缺少必需的'value'参数"

        if value not in ["up", "down"]:
            return False, f"无效的'value'参数: {value}，必须是'up'或'down'"

        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"屏幕'{device}'不存在。可用屏幕: {', '.join(available_screens)}"

        return True, ""

    def get_validation_context(self) -> str:
        """获取验证上下文用于重试提示。

        Returns:
            包含可用资源的JSON字符串
        """
        context = {
            "available_videos": self.csv_loader.get_all_videos(),
            "available_doors": self.csv_loader.get_all_doors(),
            "available_screens": self.csv_loader.get_all_screens()
        }
        return json.dumps(context, ensure_ascii=False, indent=2)