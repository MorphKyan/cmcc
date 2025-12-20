"""
Unit tests for Area API endpoints.
"""
import pytest
from unittest.mock import AsyncMock


class TestUploadAreasBatch:
    """Tests for POST /data/areas/batch endpoint."""

    def test_upload_areas_batch_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful batch upload of areas."""
        areas = [
            {"name": "5G先锋体验区", "aliases": "云游戏区,VR体验区,未来网络世界", "description": "这里是体验5G网络超高速率和超低延迟魅力的核心区域。"},
            {"name": "智慧生活馆", "aliases": "全屋智能区,智能家居展厅,未来家", "description": "这个展区将向您全方位展示家的未来形态。"}
        ]
        
        response = client.post("/data/areas/batch", json=areas)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "区域数据批量上传成功" in data["message"]
        mock_data_service.add_areas.assert_called_once()
        mock_rag_processor.batch_add_areas.assert_called_once()

    def test_upload_areas_batch_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        areas = [{"name": "5G先锋体验区"}]
        
        response = client_no_service.post("/data/areas/batch", json=areas)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_upload_areas_batch_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during upload."""
        mock_data_service.add_areas = AsyncMock(side_effect=Exception("Database error"))
        areas = [{"name": "Area1"}]
        
        response = client.post("/data/areas/batch", json=areas)
        
        assert response.status_code == 500
        assert "批量上传区域数据失败" in response.json()["detail"]


class TestGetAreas:
    """Tests for GET /data/areas endpoint."""

    def test_get_areas_success(self, client, mock_data_service):
        """Test successful retrieval of all areas."""
        mock_data_service.get_all_areas_data.return_value = [
            {"name": "5G先锋体验区", "aliases": "云游戏区,VR体验区,未来网络世界", "description": "这里是体验5G网络超高速率和超低延迟魅力的核心区域。"},
            {"name": "智慧生活馆", "aliases": "全屋智能区,智能家居展厅,未来家", "description": "这个展区将向您全方位展示家的未来形态。"}
        ]
        
        response = client.get("/data/areas")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "5G先锋体验区"
        assert data[1]["name"] == "智慧生活馆"

    def test_get_areas_empty(self, client, mock_data_service):
        """Test retrieval when no areas exist."""
        mock_data_service.get_all_areas_data.return_value = []
        
        response = client.get("/data/areas")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_areas_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.get("/data/areas")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]


class TestClearAreas:
    """Tests for DELETE /data/areas endpoint."""

    def test_clear_areas_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful clearing of all areas."""
        response = client.delete("/data/areas")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "区域数据已清空" in data["message"]
        mock_data_service.clear_areas.assert_called_once()
        mock_rag_processor.refresh_database.assert_called_once()

    def test_clear_areas_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.delete("/data/areas")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_clear_areas_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during clearing."""
        mock_data_service.clear_areas = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.delete("/data/areas")
        
        assert response.status_code == 500
        assert "清空区域数据失败" in response.json()["detail"]
