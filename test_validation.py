#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
import locale

# Set UTF-8 encoding to handle Unicode characters
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.csv_loader import CSVLoader
from src.core.validation_service import ValidationService
from src.config.config import get_settings


async def test_csv_loader():
    """Test CSVLoader functionality"""
    print("Testing CSVLoader...")

    loader = CSVLoader()

    # Test video existence
    assert loader.video_exists("5G_Revolution.mp4"), "5G_Revolution.mp4 should exist"
    assert not loader.video_exists("nonexistent.mp4"), "nonexistent.mp4 should not exist"

    # Test door existence
    assert loader.door_exists("5G先锋体验区的门"), "5G先锋体验区的门 should exist"
    assert not loader.door_exists("nonexistent door"), "nonexistent door should not exist"

    # Test screen existence
    assert loader.screen_exists("主屏幕"), "主屏幕 should exist"
    assert not loader.screen_exists("nonexistent screen"), "nonexistent screen should not exist"

    print("[PASS] CSVLoader tests passed")


async def test_validation_service():
    """Test ValidationService functionality"""
    print("Testing ValidationService...")

    service = ValidationService()

    # Test valid play_video call
    valid_play_call = {
        'type': 'play_video',
        'args': {
            'target': '5G_Revolution.mp4',
            'device': '主屏幕'
        }
    }
    is_valid, errors = service.validate_function_calls([valid_play_call])
    assert is_valid, f"Valid play_video should pass validation: {errors}"

    # Test invalid play_video call (nonexistent video)
    invalid_play_call = {
        'type': 'play_video',
        'args': {
            'target': 'nonexistent.mp4',
            'device': '主屏幕'
        }
    }
    is_valid, errors = service.validate_function_calls([invalid_play_call])
    assert not is_valid, "Invalid play_video should fail validation"
    assert len(errors) == 1, f"Should have exactly 1 error, got {len(errors)}"

    # Test invalid play_video call (nonexistent screen)
    invalid_play_call2 = {
        'type': 'play_video',
        'args': {
            'target': '5G_Revolution.mp4',
            'device': 'nonexistent screen'
        }
    }
    is_valid, errors = service.validate_function_calls([invalid_play_call2])
    assert not is_valid, "Invalid play_video should fail validation"
    assert len(errors) == 1, f"Should have exactly 1 error, got {len(errors)}"

    # Test valid control_door call
    valid_door_call = {
        'type': 'control_door',
        'args': {
            'target': '5G先锋体验区的门',
            'action': 'open'
        }
    }
    is_valid, errors = service.validate_function_calls([valid_door_call])
    assert is_valid, f"Valid control_door should pass validation: {errors}"

    # Test invalid control_door call (nonexistent door)
    invalid_door_call = {
        'type': 'control_door',
        'args': {
            'target': 'nonexistent door',
            'action': 'open'
        }
    }
    is_valid, errors = service.validate_function_calls([invalid_door_call])
    assert not is_valid, "Invalid control_door should fail validation"
    assert len(errors) == 1, f"Should have exactly 1 error, got {len(errors)}"

    print("[PASS] ValidationService tests passed")


async def test_reload_functionality():
    """Test CSVLoader reload functionality"""
    print("Testing CSVLoader reload functionality...")

    loader = CSVLoader()
    original_video_count = len(loader.get_all_videos())

    # Test reload
    success = loader.reload()
    assert success, "Reload should succeed"

    # Count should be the same
    new_video_count = len(loader.get_all_videos())
    assert original_video_count == new_video_count, "Video count should remain the same after reload"

    print("[PASS] CSVLoader reload tests passed")


async def main():
    """Run all tests"""
    print("Running validation implementation tests...\n")

    try:
        await test_csv_loader()
        await test_validation_service()
        await test_reload_functionality()

        print("\n[SUCCESS] All tests passed! The implementation is working correctly.")
        return True

    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)