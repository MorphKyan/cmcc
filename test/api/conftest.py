"""
Shared pytest fixtures for data router API tests.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient

from main import app
from src.core import dependencies
from src.api.context import Context


@pytest.fixture
def mock_data_service():
    """Create a mock DataService instance."""
    mock = MagicMock()
    # Setup async methods
    mock.add_devices = AsyncMock()
    mock.add_areas = AsyncMock()
    mock.add_media = AsyncMock()
    mock.add_doors = AsyncMock()
    mock.clear_devices = AsyncMock()
    mock.clear_areas = AsyncMock()
    mock.clear_media = AsyncMock()
    mock.clear_doors = AsyncMock()
    # Setup sync methods
    mock.get_all_devices = MagicMock(return_value=[])
    mock.get_all_areas = MagicMock(return_value=[])
    mock.get_all_media = MagicMock(return_value=[])
    mock.get_all_doors = MagicMock(return_value=[])
    mock.get_all_devices_data = MagicMock(return_value=[])
    mock.get_all_areas_data = MagicMock(return_value=[])
    mock.get_all_media_data = MagicMock(return_value=[])
    mock.get_all_doors_data = MagicMock(return_value=[])
    mock.get_device_info = MagicMock(return_value=None)
    mock.get_area_info = MagicMock(return_value=None)
    mock.get_media_info = MagicMock(return_value=None)
    mock.get_door_info = MagicMock(return_value=None)
    return mock


@pytest.fixture
def mock_rag_processor():
    """Create a mock RAG processor instance."""
    mock = MagicMock()
    mock.refresh_database = AsyncMock()
    mock.batch_add_devices = AsyncMock()
    mock.batch_add_areas = AsyncMock()
    mock.batch_add_media = AsyncMock()
    mock.batch_add_doors = AsyncMock()
    return mock


@pytest.fixture
def client(mock_data_service, mock_rag_processor):
    """Create a FastAPI TestClient with mocked dependencies."""
    # Store original values
    original_data_service = dependencies.data_service
    original_rag_processor = dependencies.rag_processor
    
    # Set mocked dependencies
    dependencies.data_service = mock_data_service
    dependencies.rag_processor = mock_rag_processor
    
    yield TestClient(app)
    
    # Restore original values
    dependencies.data_service = original_data_service
    dependencies.rag_processor = original_rag_processor


@pytest.fixture
def client_no_service():
    """Create a FastAPI TestClient with data_service set to None."""
    original_data_service = dependencies.data_service
    dependencies.data_service = None
    
    yield TestClient(app)
    
    dependencies.data_service = original_data_service


@pytest.fixture
def mock_context():
    """Create a mock Context instance."""
    context = MagicMock(spec=Context)
    context.location = None
    return context
