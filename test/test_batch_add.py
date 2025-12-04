import unittest
import asyncio
from unittest.mock import MagicMock, patch
from src.api.schemas import DoorItem, VideoItem, DeviceItem
from src.module.rag.base_rag_processor import BaseRAGProcessor
from src.services.data_service import DataService
from src.config.config import RAGSettings

class MockRAGProcessor(BaseRAGProcessor):
    async def initialize(self): pass
    async def retrieve_context(self, query): return []
    async def close(self): pass

class TestBatchAdd(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.settings = MagicMock(spec=RAGSettings)
        self.settings.videos_data_path = "videos.csv"
        self.settings.devices_data_path = "devices.csv"
        self.settings.chroma_db_dir = "chroma_db"
        self.processor = MockRAGProcessor(self.settings)
        self.processor.vector_store = MagicMock()

    @patch('src.module.rag.base_rag_processor.DataService')
    async def test_batch_add_doors(self, MockDataService):
        mock_service = MockDataService.return_value
        mock_service.add_doors = MagicMock()
        mock_service.add_doors.return_value = asyncio.Future()
        mock_service.add_doors.return_value.set_result(None)

        items = [DoorItem(name="D1", type="passage", area1="A", area2="B")]
        await self.processor.batch_add_doors(items)

        mock_service.add_doors.assert_called_once()
        self.processor.vector_store.add_documents.assert_called_once()

    @patch('src.module.rag.base_rag_processor.DataService')
    async def test_batch_add_videos(self, MockDataService):
        mock_service = MockDataService.return_value
        mock_service.add_videos = MagicMock()
        mock_service.add_videos.return_value = asyncio.Future()
        mock_service.add_videos.return_value.set_result(None)

        items = [VideoItem(name="V1", filename="v1.mp4")]
        await self.processor.batch_add_videos(items)

        mock_service.add_videos.assert_called_once()
        self.processor.vector_store.add_documents.assert_called_once()

    @patch('src.module.rag.base_rag_processor.DataService')
    async def test_batch_add_devices(self, MockDataService):
        mock_service = MockDataService.return_value
        mock_service.add_devices = MagicMock()
        mock_service.add_devices.return_value = asyncio.Future()
        mock_service.add_devices.return_value.set_result(None)

        items = [DeviceItem(name="Dev1", type="T1", area="A1")]
        await self.processor.batch_add_devices(items)

        mock_service.add_devices.assert_called_once()
        self.processor.vector_store.add_documents.assert_called_once()

if __name__ == '__main__':
    unittest.main()
