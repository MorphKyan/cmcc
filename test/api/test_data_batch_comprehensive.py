"""
Comprehensive tests for all batch upload endpoints in the Data router.
"""
import pytest
from unittest.mock import AsyncMock


class TestBatchUploadComprehensive:
    """
    Comprehensive tests for:
    - POST /data/devices/batch
    - POST /data/areas/batch
    - POST /data/media/batch
    - POST /data/doors/batch
    """

    @pytest.mark.parametrize("endpoint,payload,mock_method", [
        ("/data/devices/batch", [{"name": "Device1", "type": "screen", "area": "Area1"}], "add_devices"),
        ("/data/areas/batch", [{"name": "Area1"}], "add_areas"),
        ("/data/media/batch", [{"name": "Media1", "type": "video"}], "add_media"),
        ("/data/doors/batch", [{"name": "Door1", "type": "passage", "area1": "A1", "area2": "A2", "location": ""}], "add_doors"),
    ])
    def test_batch_upload_success(self, client, mock_data_service, mock_rag_processor, endpoint, payload, mock_method):
        """Test successful batch upload for all endpoints."""
        response = client.post(endpoint, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "批量上传成功" in data["message"]
        
        # Verify both data_service and rag_processor were called
        getattr(mock_data_service, mock_method).assert_called_once()
        # RAG methods are named like batch_add_devices, batch_add_areas, etc.
        rag_method = f"batch_{mock_method}"
        getattr(mock_rag_processor, rag_method).assert_called_once()

    @pytest.mark.parametrize("endpoint,payload", [
        ("/data/devices/batch", [{"name": "D1", "type": "T1", "area": "A1"}]),
        ("/data/areas/batch", [{"name": "A1"}]),
        ("/data/media/batch", [{"name": "M1", "type": "V1"}]),
        ("/data/doors/batch", [{"name": "Door1", "type": "passage", "area1": "A1", "area2": "A2", "location": ""}]),
    ])
    def test_batch_upload_service_unavailable(self, client_no_service, endpoint, payload):
        """Test 503 error when DataService is not initialized."""
        response = client_no_service.post(endpoint, json=payload)
        
        assert response.status_code == 503
        assert "DataService未初始化" in response.json()["detail"]

    @pytest.mark.parametrize("endpoint,payload,mock_method,error_msg", [
        ("/data/devices/batch", [{"name": "D1", "type": "T1", "area": "A1"}], "add_devices", "批量上传设备数据失败"),
        ("/data/areas/batch", [{"name": "A1"}], "add_areas", "批量上传区域数据失败"),
        ("/data/media/batch", [{"name": "M1", "type": "V1"}], "add_media", "批量上传媒体数据失败"),
        ("/data/doors/batch", [{"name": "Door1", "type": "passage", "area1": "A1", "area2": "A2", "location": ""}], "add_doors", "批量上传门数据失败"),
    ])
    def test_batch_upload_error(self, client, mock_data_service, endpoint, payload, mock_method, error_msg):
        """Test 500 error when service throws an exception."""
        getattr(mock_data_service, mock_method).side_effect = Exception("Mocked Error")
        
        response = client.post(endpoint, json=payload)
        
        assert response.status_code == 500
        assert error_msg in response.json()["detail"]

    @pytest.mark.parametrize("endpoint,invalid_payload", [
        ("/data/devices/batch", [{"name": "D1"}]), # Missing 'type' and 'area'
        ("/data/areas/batch", [{"aliases": "A1"}]), # Missing 'name'
        ("/data/media/batch", [{"type": "video"}]), # Missing 'name'
        ("/data/doors/batch", [{"name": "Door1"}]), # Missing multiple fields
    ])
    def test_batch_upload_validation_error(self, client, endpoint, invalid_payload):
        """Test 422 error for invalid data structure."""
        response = client.post(endpoint, json=invalid_payload)
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert "校验不通过" in error_detail
        assert "源数据" in error_detail

    @pytest.mark.parametrize("endpoint", [
        "/data/devices/batch",
        "/data/areas/batch",
        "/data/media/batch",
        "/data/doors/batch",
    ])
    def test_batch_upload_empty_list(self, client, endpoint):
        """Test that sending an empty list is accepted by Pydantic (list[Item])."""
        response = client.post(endpoint, json=[])
        assert response.status_code == 200
        assert response.json()["status"] == "success"
