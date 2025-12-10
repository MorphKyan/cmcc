#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from loguru import logger

class ToolValidator:
    """
    Tool Parameter Validator (Singleton)
    Validates arguments for tool calls against the data service.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ToolValidator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def validate_open_media_args(self, media_name: str, device_id: str) -> tuple[bool, str | None]:
        from src.core import dependencies
        if not dependencies.data_service.media_exists(media_name):
            return False, f"Media '{media_name}' not found."

        if not dependencies.data_service.device_exists(device_id):
            return False, f"Device '{device_id}' not found."

        return True, None

    def validate_control_door_args(self, door_id: str, action: str) -> tuple[bool, str | None]:
        from src.core import dependencies
        if not dependencies.data_service.door_exists(door_id):
            return False, f"Door '{door_id}' not found."

        if action not in ["open", "close"]:
            return False, f"Invalid door action '{action}'. Must be 'open' or 'close'."

        return True, None

    def validate_device_args(self, device_id: str, tool_name: str) -> tuple[bool, str | None]:
        from src.core import dependencies
        if not dependencies.data_service.device_exists(device_id):
            return False, f"Device '{device_id}' not found for tool '{tool_name}'."

        return True, None

    def validate_update_location_args(self, area_name: str) -> tuple[bool, str | None]:
        from src.core import dependencies
        if not dependencies.data_service.area_exists(area_name):
            return False, f"Area '{area_name}' not found."

        return True, None

    def validate_tool_args(self, tool_name: str, tool_args: dict) -> tuple[bool, str | None]:
        """
        Validates tool arguments based on the schema defined in definitions.py.
        """
        try:
            # Map tool names to validation logic
            if tool_name == "open_media":
                # args: device (media_name), value (device_id)
                return self.validate_open_media_args(
                    media_name=tool_args.get("device", ""),
                    device_id=tool_args.get("value", "")
                )

            elif tool_name == "control_door":
                # args: device (door_id), value (action)
                return self.validate_control_door_args(
                    door_id=tool_args.get("device", ""),
                    action=tool_args.get("value", "")
                )

            elif tool_name in ["seek_video", "set_volume", "adjust_volume"]:
                # args: device, value (value not validated against DB)
                return self.validate_device_args(
                    device_id=tool_args.get("device", ""),
                    tool_name=tool_name
                )

            elif tool_name == "update_location":
                # args: value (area_name)
                return self.validate_update_location_args(
                    area_name=tool_args.get("value", "")
                )

            else:
                # Unknown tool, assume valid (or log warning)
                return True, None

        except Exception as e:
            logger.error(f"Error validating tool '{tool_name}' arguments: {e}")
            return False, f"Validation error: {str(e)}"
