import unittest
from src.module.rag.helper import convert_doors_to_documents, convert_videos_to_documents, convert_devices_to_documents

class TestRAGHelper(unittest.TestCase):
    def test_convert_doors(self):
        doors_data = [
            {"name": "Door1", "type": "passage", "area1": "A", "area2": "B"},
            {"name": "Door2", "type": "standalone", "location": "L"}
        ]
        docs = convert_doors_to_documents(doors_data)
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0].metadata["type"], "door")
        self.assertIn("连接A和B", docs[0].page_content)
        self.assertIn("位于L", docs[1].page_content)

    def test_convert_videos(self):
        videos_data = [
            {"name": "Video1", "aliases": "V1", "description": "Desc1", "filename": "f1.mp4"}
        ]
        docs = convert_videos_to_documents(videos_data)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["type"], "video")
        self.assertIn("也称为V1", docs[0].page_content)

    def test_convert_devices(self):
        devices_data = [
            {"name": "Device1", "type": "Type1", "area": "Area1"}
        ]
        docs = convert_devices_to_documents(devices_data)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].metadata["type"], "device")
        self.assertIn("类型为Type1", docs[0].page_content)

if __name__ == '__main__':
    unittest.main()
