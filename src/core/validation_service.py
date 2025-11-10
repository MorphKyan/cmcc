#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, List, Tuple

from src.core.csv_loader import CSVLoader


class ValidationService:
    """
    Centralized validation service for LLM function call parameters.

    This service validates function call parameters against the loaded CSV data
    to ensure that requested resources (videos, doors, screens) actually exist.
    """

    def __init__(self):
        """Initialize the validation service with CSV loader."""
        self.csv_loader = CSVLoader()

    def validate_function_calls(self, tool_calls: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate a list of function calls against available resources.

        Args:
            tool_calls: List of function call dictionaries from LLM output

        Returns:
            Tuple of (is_valid, error_messages)
            - is_valid: True if all function calls are valid, False otherwise
            - error_messages: List of error messages for invalid calls
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

    def _validate_play_video(self, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate play_video function arguments.

        Args:
            args: Function arguments dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        target = args.get("target")
        device = args.get("device")

        if not target:
            return False, "Missing required 'target' parameter"

        if not device:
            return False, "Missing required 'device' parameter"

        # Validate video filename
        if not self.csv_loader.video_exists(target):
            available_videos = self.csv_loader.get_all_videos()
            return False, f"Video '{target}' not found. Available videos: {', '.join(available_videos)}"

        # Validate screen name
        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"Screen '{device}' not found. Available screens: {', '.join(available_screens)}"

        return True, ""

    def _validate_control_door(self, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate control_door function arguments.

        Args:
            args: Function arguments dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        target = args.get("target")
        action = args.get("action")

        if not target:
            return False, "Missing required 'target' parameter"

        if not action:
            return False, "Missing required 'action' parameter"

        if action not in ["open", "close"]:
            return False, f"Invalid action '{action}'. Must be 'open' or 'close'"

        # Validate door name
        if not self.csv_loader.door_exists(target):
            available_doors = self.csv_loader.get_all_doors()
            return False, f"Door '{target}' not found. Available doors: {', '.join(available_doors)}"

        return True, ""

    def _validate_seek_video(self, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate seek_video function arguments.

        Args:
            args: Function arguments dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        device = args.get("device")
        value = args.get("value")

        if not device:
            return False, "Missing required 'device' parameter"

        if value is None:
            return False, "Missing required 'value' parameter"

        if not isinstance(value, int) or value < 0:
            return False, f"Invalid 'value' parameter: {value}. Must be a non-negative integer"

        # Validate screen name
        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"Screen '{device}' not found. Available screens: {', '.join(available_screens)}"

        return True, ""

    def _validate_set_volume(self, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate set_volume function arguments.

        Args:
            args: Function arguments dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        device = args.get("device")
        value = args.get("value")

        if not device:
            return False, "Missing required 'device' parameter"

        if value is None:
            return False, "Missing required 'value' parameter"

        if not isinstance(value, int) or value < 0 or value > 100:
            return False, f"Invalid 'value' parameter: {value}. Must be an integer between 0 and 100"

        # Validate screen name
        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"Screen '{device}' not found. Available screens: {', '.join(available_screens)}"

        return True, ""

    def _validate_adjust_volume(self, args: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate adjust_volume function arguments.

        Args:
            args: Function arguments dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        device = args.get("device")
        value = args.get("value")

        if not device:
            return False, "Missing required 'device' parameter"

        if not value:
            return False, "Missing required 'value' parameter"

        if value not in ["up", "down"]:
            return False, f"Invalid 'value' parameter: {value}. Must be 'up' or 'down'"

        # Validate screen name
        if not self.csv_loader.screen_exists(device):
            available_screens = self.csv_loader.get_all_screens()
            return False, f"Screen '{device}' not found. Available screens: {', '.join(available_screens)}"

        return True, ""

    def get_validation_context(self) -> str:
        """
        Get validation context for retry prompts.

        Returns:
            JSON string containing available resources for prompt context
        """
        context = {
            "available_videos": self.csv_loader.get_all_videos(),
            "available_doors": self.csv_loader.get_all_doors(),
            "available_screens": self.csv_loader.get_all_screens()
        }
        return json.dumps(context, ensure_ascii=False, indent=2)