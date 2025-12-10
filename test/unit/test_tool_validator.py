import pytest
from unittest.mock import MagicMock, patch
from src.module.llm.tool.validator import ToolValidator
from src.core import dependencies

@pytest.fixture
def mock_data_service():
    """Mock the global data_service dependency."""
    mock_service = MagicMock()
    # Setup default return values for existence checks to be False by default
    # so we can selectively enable them in tests
    mock_service.media_exists.return_value = False
    mock_service.device_exists.return_value = False
    mock_service.door_exists.return_value = False
    mock_service.area_exists.return_value = False
    
    # Patch the dependencies.data_service
    with patch("src.core.dependencies.data_service", mock_service):
        yield mock_service

@pytest.fixture
def validator():
    """Get the singleton instance of ToolValidator."""
    # Reset instance to ensure fresh state if needed (though it's stateless mostly)
    ToolValidator._instance = None
    return ToolValidator.get_instance()

class TestToolValidator:

    def test_open_media_validation(self, validator, mock_data_service):
        """Test open_media command validation."""
        # Setup mock behavior
        mock_data_service.media_exists.side_effect = lambda x: x == "test_media"
        mock_data_service.device_exists.side_effect = lambda x: x == "test_device"

        # Case 1: Valid
        valid, msg = validator.validate_tool_args("open_media", {"device": "test_media", "value": "test_device"})
        assert valid is True
        assert msg is None

        # Case 2: Invalid media
        valid, msg = validator.validate_tool_args("open_media", {"device": "wrong_media", "value": "test_device"})
        assert valid is False
        assert "Media 'wrong_media' not found" in msg

        # Case 3: Invalid device
        valid, msg = validator.validate_tool_args("open_media", {"device": "test_media", "value": "wrong_device"})
        assert valid is False
        assert "Device 'wrong_device' not found" in msg

    def test_control_door_validation(self, validator, mock_data_service):
        """Test control_door command validation."""
        mock_data_service.door_exists.side_effect = lambda x: x == "test_door"

        # Case 1: Valid open
        valid, msg = validator.validate_tool_args("control_door", {"device": "test_door", "value": "open"})
        assert valid is True
        assert msg is None

        # Case 2: Valid close
        valid, msg = validator.validate_tool_args("control_door", {"device": "test_door", "value": "close"})
        assert valid is True

        # Case 3: Invalid door
        valid, msg = validator.validate_tool_args("control_door", {"device": "wrong_door", "value": "open"})
        assert valid is False
        assert "Door 'wrong_door' not found" in msg

        # Case 4: Invalid action
        valid, msg = validator.validate_tool_args("control_door", {"device": "test_door", "value": "break"})
        assert valid is False
        assert "Invalid door action" in msg

    def test_device_tools_validation(self, validator, mock_data_service):
        """Test seek_video, set_volume, adjust_volume validation."""
        mock_data_service.device_exists.side_effect = lambda x: x == "test_device"

        for tool in ["seek_video", "set_volume", "adjust_volume"]:
            # Case 1: Valid device
            valid, msg = validator.validate_tool_args(tool, {"device": "test_device", "value": 50})
            assert valid is True

            # Case 2: Invalid device
            valid, msg = validator.validate_tool_args(tool, {"device": "wrong_device", "value": 50})
            assert valid is False
            assert f"Device 'wrong_device' not found for tool '{tool}'" in msg

    def test_update_location_validation(self, validator, mock_data_service):
        """Test update_location validation."""
        mock_data_service.area_exists.side_effect = lambda x: x == "test_area"

        # Case 1: Valid area
        valid, msg = validator.validate_tool_args("update_location", {"value": "test_area"})
        assert valid is True

        # Case 2: Invalid area
        valid, msg = validator.validate_tool_args("update_location", {"value": "wrong_area"})
        assert valid is False
        assert "Area 'wrong_area' not found" in msg

    def test_unknown_tool(self, validator):
        """Test behavior for unknown tools."""
        valid, msg = validator.validate_tool_args("unknown_tool", {})
        assert valid is True
        assert msg is None
