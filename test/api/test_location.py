"""
Unit tests for Location API endpoints.
"""
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app
from src.core import dependencies
from src.api.context import Context


class TestUpdateLocation:
    """Tests for POST /data/location endpoint."""

    def test_update_location_success(self):
        """Test successful update of user location."""
        # Create a mock context
        mock_context = MagicMock(spec=Context)
        mock_context.location = None
        
        # Store original and set mock
        original_contexts = dependencies.active_contexts.copy()
        test_client_id = "test-client-123"
        dependencies.active_contexts[test_client_id] = mock_context
        
        try:
            client = TestClient(app)
            request_data = {
                "client_id": test_client_id,
                "location": "展厅A"
            }
            
            response = client.post("/data/location", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["client_id"] == test_client_id
            assert data["data"]["location"] == "展厅A"
            assert "用户位置已更新" in data["message"]
            assert mock_context.location == "展厅A"
        finally:
            # Restore original contexts
            dependencies.active_contexts.clear()
            dependencies.active_contexts.update(original_contexts)

    def test_update_location_client_not_found(self):
        """Test 404 error when client_id is not found."""
        # Store original contexts
        original_contexts = dependencies.active_contexts.copy()
        dependencies.active_contexts.clear()
        
        try:
            client = TestClient(app)
            request_data = {
                "client_id": "non-existent-client",
                "location": "展厅A"
            }
            
            response = client.post("/data/location", json=request_data)
            
            assert response.status_code == 404
            assert "未找到客户端连接" in response.json()["detail"]
        finally:
            # Restore original contexts
            dependencies.active_contexts.clear()
            dependencies.active_contexts.update(original_contexts)

    def test_update_location_missing_fields(self):
        """Test 422 error when required fields are missing."""
        client = TestClient(app)
        
        # Missing location
        response = client.post("/data/location", json={"client_id": "test"})
        assert response.status_code == 422
        
        # Missing client_id
        response = client.post("/data/location", json={"location": "展厅A"})
        assert response.status_code == 422
        
        # Empty body
        response = client.post("/data/location", json={})
        assert response.status_code == 422
