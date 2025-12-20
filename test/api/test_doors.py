"""
Unit tests for Door API endpoints.
"""
import pytest
from unittest.mock import AsyncMock


class TestUploadDoorsBatch:
    """Tests for POST /data/doors/batch endpoint."""

    def test_upload_doors_batch_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful batch upload of doors."""
        doors = [
            {"name": "5G先锋体验区-智慧生活馆", "type": "passage", "area1": "5G先锋体验区", "area2": "智慧生活馆", "location": ""},
            {"name": "5G先锋体验区-未来科技赋能中心", "type": "passage", "area1": "5G先锋体验区", "area2": "未来科技赋能中心", "location": ""}
        ]
        
        response = client.post("/data/doors/batch", json=doors)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "门数据批量上传成功" in data["message"]
        mock_data_service.add_doors.assert_called_once()
        mock_rag_processor.batch_add_doors.assert_called_once()

    def test_upload_doors_batch_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        doors = [{"name": "5G先锋体验区-智慧生活馆", "type": "passage", "area1": "5G先锋体验区", "area2": "智慧生活馆", "location": ""}]
        
        response = client_no_service.post("/data/doors/batch", json=doors)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_upload_doors_batch_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during upload."""
        mock_data_service.add_doors = AsyncMock(side_effect=Exception("Database error"))
        doors = [{"name": "5G先锋体验区-智慧生活馆", "type": "passage", "area1": "5G先锋体验区", "area2": "智慧生活馆", "location": ""}]
        
        response = client.post("/data/doors/batch", json=doors)
        
        assert response.status_code == 500
        assert "批量上传门数据失败" in response.json()["detail"]


class TestGetDoors:
    """Tests for GET /data/doors endpoint."""

    def test_get_doors_success(self, client, mock_data_service):
        """Test successful retrieval of all doors."""
        mock_data_service.get_all_doors_data.return_value = [
            {"name": "5G先锋体验区-智慧生活馆", "type": "passage", "area1": "5G先锋体验区", "area2": "智慧生活馆", "location": ""},
            {"name": "5G先锋体验区主入口", "type": "standalone", "area1": "", "area2": "", "location": "5G先锋体验区"}
        ]
        
        response = client.get("/data/doors")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "5G先锋体验区-智慧生活馆"
        assert data[1]["name"] == "5G先锋体验区主入口"

    def test_get_doors_empty(self, client, mock_data_service):
        """Test retrieval when no doors exist."""
        mock_data_service.get_all_doors_data.return_value = []
        
        response = client.get("/data/doors")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_doors_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.get("/data/doors")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]


class TestClearDoors:
    """Tests for DELETE /data/doors endpoint."""

    def test_clear_doors_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful clearing of all doors."""
        response = client.delete("/data/doors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "门数据已清空" in data["message"]
        mock_data_service.clear_doors.assert_called_once()
        mock_rag_processor.refresh_database.assert_called_once()

    def test_clear_doors_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.delete("/data/doors")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_clear_doors_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during clearing."""
        mock_data_service.clear_doors = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.delete("/data/doors")
        
        assert response.status_code == 500
        assert "清空门数据失败" in response.json()["detail"]
