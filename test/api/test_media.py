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
            {"name": "5G_Overview_Intro.mp4", "type": "video", "aliases": "5G技术总览,5G的视频,5G技术介绍", "description": "中国移动5G演进之路、核心优势、网络覆盖及6G展望。"},
            {"name": "Smart_Home_Solutions.mp4", "type": "video", "aliases": "智慧家庭解决方案,智慧家庭的视频,智能家居", "description": "全屋智能解决方案，APP实现安防、照明、家电全场景联动。"}
        ]
        
        response = client.post("/data/media/batch", json=media)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "媒体数据批量上传成功" in data["message"]
        mock_data_service.add_media.assert_called_once()
        mock_rag_processor.batch_add_media.assert_called_once()

    def test_upload_media_batch_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        media = [{"name": "5G_Overview_Intro.mp4", "type": "video"}]
        
        response = client_no_service.post("/data/media/batch", json=media)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_upload_media_batch_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during upload."""
        mock_data_service.add_media = AsyncMock(side_effect=Exception("Database error"))
        media = [{"name": "5G_Overview_Intro.mp4", "type": "video"}]
        
        response = client.post("/data/media/batch", json=media)
        
        assert response.status_code == 500
        assert "批量上传媒体数据失败" in response.json()["detail"]


class TestGetMedia:
    """Tests for GET /data/media endpoint."""

    def test_get_media_success(self, client, mock_data_service):
        """Test successful retrieval of all media."""
        mock_data_service.get_all_media_data.return_value = [
            {"name": "5G_Overview_Intro.mp4", "type": "video", "aliases": "5G技术总览,5G的视频,5G技术介绍", "description": "中国移动5G演进之路、核心优势、网络覆盖及6G展望。"},
            {"name": "Smart_Home_Solutions.mp4", "type": "video", "aliases": "智慧家庭解决方案,智慧家庭的视频,智能家居", "description": "全屋智能解决方案，APP实现安防、照明、家电全场景联动。"}
        ]
        
        response = client.get("/data/media")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "5G_Overview_Intro.mp4"
        assert data[1]["name"] == "Smart_Home_Solutions.mp4"

    def test_get_media_empty(self, client, mock_data_service):
        """Test retrieval when no media exist."""
        mock_data_service.get_all_media_data.return_value = []
        
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
