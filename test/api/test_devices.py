"""
Unit tests for Device API endpoints.
"""
import pytest
from unittest.mock import AsyncMock


class TestUploadDevicesBatch:
    """Tests for POST /data/devices/batch endpoint."""

    def test_upload_devices_batch_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful batch upload of devices."""
        devices = [
            {"name": "主屏幕", "type": "screen", "area": "5G先锋体验区", "aliases": "中央大屏,迎宾屏,展厅巨幕", "description": "位于展厅正中央，通常播放欢迎视频或整体宣传片。"},
            {"name": "左侧互动大屏", "type": "screen", "area": "5G先锋体验区", "aliases": "互动体验屏,业务查询屏,左边屏幕", "description": "位于入口左侧，提供触摸互动功能。"}
        ]
        
        response = client.post("/data/devices/batch", json=devices)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "设备数据批量上传成功" in data["message"]
        mock_data_service.add_devices.assert_called_once()
        mock_rag_processor.batch_add_devices.assert_called_once()

    def test_upload_devices_batch_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        devices = [{"name": "主屏幕", "type": "screen", "area": "5G先锋体验区"}]
        
        response = client_no_service.post("/data/devices/batch", json=devices)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_upload_devices_batch_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during upload."""
        mock_data_service.add_devices = AsyncMock(side_effect=Exception("Database error"))
        devices = [{"name": "主屏幕", "type": "screen", "area": "5G先锋体验区"}]
        
        response = client.post("/data/devices/batch", json=devices)
        
        assert response.status_code == 500
        assert "批量上传设备数据失败" in response.json()["detail"]


class TestGetDevices:
    """Tests for GET /data/devices endpoint."""

    def test_get_devices_success(self, client, mock_data_service):
        """Test successful retrieval of all devices."""
        mock_data_service.get_all_devices_data.return_value = [
            {"name": "主屏幕", "type": "screen", "area": "5G先锋体验区"},
            {"name": "左侧互动大屏", "type": "screen", "area": "5G先锋体验区"}
        ]
        
        response = client.get("/data/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "主屏幕"
        assert data[1]["name"] == "左侧互动大屏"

    def test_get_devices_empty(self, client, mock_data_service):
        """Test retrieval when no devices exist."""
        mock_data_service.get_all_devices_data.return_value = []
        
        response = client.get("/data/devices")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_devices_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.get("/data/devices")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]


class TestClearDevices:
    """Tests for DELETE /data/devices endpoint."""

    def test_clear_devices_success(self, client, mock_data_service, mock_rag_processor):
        """Test successful clearing of all devices."""
        response = client.delete("/data/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "设备数据已清空" in data["message"]
        mock_data_service.clear_devices.assert_called_once()
        mock_rag_processor.refresh_database.assert_called_once()

    def test_clear_devices_service_unavailable(self, client_no_service):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.delete("/data/devices")
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    def test_clear_devices_error(self, client, mock_data_service):
        """Test 500 error when an exception occurs during clearing."""
        mock_data_service.clear_devices = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.delete("/data/devices")
        
        assert response.status_code == 500
        assert "清空设备数据失败" in response.json()["detail"]
