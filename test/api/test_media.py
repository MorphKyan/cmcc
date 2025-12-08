"""
Unit tests for Media API endpoints.
"""
import pytest
from unittest.mock import AsyncMock


class TestUploadMediaBatch:
    """Tests for POST /data/media/batch endpoint."""

    def test_upload_media_batch_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful batch upload of media."""
        media = [
            {"name": "Video1", "type": "video", "aliases": "v1", "description": "Test video 1"},
            {"name": "Audio1", "type": "audio"}
        ]
        
        response = client.post("/data/media/batch", json=media)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "媒体数据批量上传成功" in data["message"]
        mock_data_service.add_media.assert_called_once()
        mock_rag_processor.refresh_database.assert_called_once()

    def test_upload_media_batch_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        media = [{"name": "Video1", "type": "video"}]
        
        response = client_no_service.post("/data/media/batch", json=media)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_upload_media_batch_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during upload."""
        mock_data_service.add_media = AsyncMock(side_effect=Exception("Database error"))
        media = [{"name": "Video1", "type": "video"}]
        
        response = client.post("/data/media/batch", json=media)
        
        assert response.status_code == 500
        assert "批量上传媒体数据失败" in response.json()["detail"]


class TestGetMedia:
    """Tests for GET /data/media endpoint."""

    def test_get_media_success(self, client, mock_data_service):
        """Test successful retrieval of all media."""
        mock_data_service.get_all_media.return_value = ["Video1", "Audio1"]
        # Use a dict-based side_effect to handle multiple calls per media
        media_data = {
            "Video1": {"name": "Video1", "type": "video", "aliases": "v1", "description": "Test video 1"},
            "Audio1": {"name": "Audio1", "type": "audio", "aliases": "", "description": ""}
        }
        mock_data_service.get_media_info.side_effect = lambda name: media_data.get(name)
        
        response = client.get("/data/media")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Video1"
        assert data[1]["name"] == "Audio1"

    def test_get_media_empty(self, client, mock_data_service):
        """Test retrieval when no media exist."""
        mock_data_service.get_all_media.return_value = []
        
        response = client.get("/data/media")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_media_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.get("/data/media")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]


class TestClearMedia:
    """Tests for DELETE /data/media endpoint."""

    def test_clear_media_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful clearing of all media."""
        response = client.delete("/data/media")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "媒体数据已清空" in data["message"]
        mock_data_service.clear_media.assert_called_once()
        mock_rag_processor.refresh_database.assert_called_once()

    def test_clear_media_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.delete("/data/media")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_clear_media_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during clearing."""
        mock_data_service.clear_media = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.delete("/data/media")
        
        assert response.status_code == 500
        assert "清空媒体数据失败" in response.json()["detail"]
