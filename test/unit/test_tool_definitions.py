
import pytest
from unittest.mock import MagicMock, patch
from src.module.llm.tool.definitions import (
    open_media, control_door, seek_video, set_volume, 
    adjust_volume, update_location, CommandAction
)

@pytest.fixture
def mock_dependencies():
    with patch('src.core.dependencies.data_service') as mock_ds:
        yield mock_ds

class TestToolValidation:
    
    def test_open_media_success(self, mock_dependencies):
        mock_dependencies.media_exists.return_value = True
        mock_dependencies.device_exists.return_value = True
        
        result = open_media.invoke({"device": "song.mp3", "value": "screen1"})
        
        assert result.action == CommandAction.OPEN_MEDIA.value
        assert result.device == "song.mp3"
        assert result.value == "screen1"

    def test_open_media_fail_media(self, mock_dependencies):
        mock_dependencies.media_exists.return_value = False
        
        result = open_media.invoke({"device": "unknown.mp3", "value": "screen1"})
        
        assert result.action == CommandAction.ERROR.value
        assert "Media 'unknown.mp3' not found" in result.value

    def test_control_door_fail(self, mock_dependencies):
        mock_dependencies.door_exists.return_value = False
        
        result = control_door.invoke({"device": "door999", "value": "open"})
        
        assert result.action == CommandAction.ERROR.value
        assert "Door 'door999' not found" in result.value

    def test_update_location_success(self, mock_dependencies):
        mock_dependencies.area_exists.return_value = True
        
        result = update_location.invoke({"value": "kitchen"})
        
        assert result.action == CommandAction.UPDATE_LOCATION.value
        assert result.value == "kitchen"

    def test_update_location_fail(self, mock_dependencies):
        mock_dependencies.area_exists.return_value = False
        
        result = update_location.invoke({"value": "mars"})
        
        assert result.action == CommandAction.ERROR.value
        assert "Area 'mars' not found" in result.value
