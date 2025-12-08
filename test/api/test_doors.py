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
            {"name": "Door1", "type": "passage", "area1": "AreaA", "area2": "AreaB", "location": "Floor1"},
            {"name": "Door2", "type": "emergency", "area1": "AreaB", "area2": "AreaC", "location": "Floor2"}
        ]
        
        response = client.post("/data/doors/batch", json=doors)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "门数据批量上传成功" in data["message"]
        mock_data_service.add_doors.assert_called_once()
        mock_rag_processor.refresh_database.assert_called_once()

    def test_upload_doors_batch_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        doors = [{"name": "Door1", "type": "passage", "area1": "AreaA", "area2": "AreaB", "location": "Floor1"}]
        
        response = client_no_service.post("/data/doors/batch", json=doors)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_upload_doors_batch_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during upload."""
        mock_data_service.add_doors = AsyncMock(side_effect=Exception("Database error"))
        doors = [{"name": "Door1", "type": "passage", "area1": "AreaA", "area2": "AreaB", "location": "Floor1"}]
        
        response = client.post("/data/doors/batch", json=doors)
        
        assert response.status_code == 500
        assert "批量上传门数据失败" in response.json()["detail"]


class TestGetDoors:
    """Tests for GET /data/doors endpoint."""

    def test_get_doors_success(self, client, mock_data_service):
        """Test successful retrieval of all doors."""
        mock_data_service.get_all_doors.return_value = ["Door1", "Door2"]
        # Use a dict-based side_effect to handle multiple calls per door
        door_data = {
            "Door1": {"name": "Door1", "type": "passage", "area1": "AreaA", "area2": "AreaB", "location": "Floor1"},
            "Door2": {"name": "Door2", "type": "emergency", "area1": "AreaB", "area2": "AreaC", "location": "Floor2"}
        }
        mock_data_service.get_door_info.side_effect = lambda name: door_data.get(name)
        
        response = client.get("/data/doors")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Door1"
        assert data[1]["name"] == "Door2"

    def test_get_doors_empty(self, client, mock_data_service):
        """Test retrieval when no doors exist."""
        mock_data_service.get_all_doors.return_value = []
        
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
