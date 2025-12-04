import os
import shutil
import threading
import pandas as pd
from typing import Any, List, Dict, Optional
from loguru import logger
from pydantic import BaseModel

from src.config.config import get_settings
from src.api.schemas import DeviceItem, AreaItem, VideoItem

class DataService:
    """
    Data Service for managing exhibition data (videos, devices, areas, doors).
    Replaces CSVLoader and provides write capabilities.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DataService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._data_lock = threading.Lock()
        self._videos_cache: Dict[str, Dict[str, Any]] = {}
        self._doors_cache: Dict[str, Dict[str, Any]] = {}
        self._devices_cache: Dict[str, Dict[str, Any]] = {}
        self._areas_cache: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
        
        self.reload()

    def reload(self) -> bool:
        """Reload data from CSV files."""
        try:
            settings = get_settings()
            # Use settings paths directly from DataSettings
            videos_path = settings.data.videos_data_path
            devices_path = settings.data.devices_data_path
            areas_path = settings.data.areas_data_path
            doors_path = settings.data.doors_data_path

            with self._data_lock:
                if os.path.exists(videos_path):
                    videos_df = self._load_csv_file(videos_path)
                    self._videos_cache = self._process_videos_data(videos_df)
                    logger.info(f"Loaded {len(self._videos_cache)} videos from {videos_path}")

                if os.path.exists(doors_path):
                    doors_df = self._load_csv_file(doors_path)
                    self._doors_cache = self._process_doors_data(doors_df)
                    logger.info(f"Loaded {len(self._doors_cache)} doors from {doors_path}")

                if os.path.exists(devices_path):
                    devices_df = self._load_csv_file(devices_path)
                    self._devices_cache = self._process_devices_data(devices_df)
                    logger.info(f"Loaded {len(self._devices_cache)} devices from {devices_path}")

                if os.path.exists(areas_path):
                    areas_df = self._load_csv_file(areas_path)
                    self._areas_cache = self._process_areas_data(areas_df)
                    logger.info(f"Loaded {len(self._areas_cache)} areas from {areas_path}")

            return True

        except Exception as e:
            logger.exception(f"Failed to reload data: {e}")
            return False

    def _load_csv_file(self, file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV file '{file_path}': {e}")
            return pd.DataFrame()

    def _process_videos_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        videos_dict = {}
        if df.empty: return videos_dict
        for _, row in df.iterrows():
            filename = str(row.get("filename", "")).strip()
            if not filename: continue
            videos_dict[filename] = {
                "type": str(row.get("type", "video")),
                "name": str(row.get("name", "")),
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", "")),
                "filename": filename
            }
        return videos_dict

    def _process_doors_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        doors_dict = {}
        if df.empty: return doors_dict
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name: continue
            doors_dict[name] = {
                "name": name,
                "type": str(row.get("type", "")).strip(),
                "area1": str(row.get("area1", "")).strip(),
                "area2": str(row.get("area2", "")).strip(),
                "location": str(row.get("location", "")).strip()
            }
        return doors_dict

    def _process_areas_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        areas_dict = {}
        if df.empty: return areas_dict
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name: continue
            areas_dict[name] = {
                "name": name,
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
        return areas_dict

    def _process_devices_data(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        devices_dict = {}
        if df.empty: return devices_dict
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name: continue
            devices_dict[name] = {
                "name": name,
                "type": str(row.get("type", "")),
                "area": str(row.get("area", "")),
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
        return devices_dict

    # --- Read Methods ---

    def video_exists(self, filename: str) -> bool:
        with self._data_lock:
            return filename in self._videos_cache

    def door_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._doors_cache

    def get_video_info(self, filename: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._videos_cache.get(filename)

    def get_door_info(self, name: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._doors_cache.get(name)

    def get_all_videos(self) -> List[str]:
        with self._data_lock:
            return list(self._videos_cache.keys())

    def get_all_doors(self) -> List[str]:
        with self._data_lock:
            return list(self._doors_cache.keys())

    def area_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._areas_cache

    def get_area_info(self, name: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._areas_cache.get(name)

    def get_all_areas(self) -> List[str]:
        with self._data_lock:
            return list(self._areas_cache.keys())

    def device_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._devices_cache

    def get_device_info(self, name: str) -> Optional[Dict[str, Any]]:
        with self._data_lock:
            return self._devices_cache.get(name)

    def get_all_devices(self) -> List[str]:
        with self._data_lock:
            return list(self._devices_cache.keys())

    # --- Write Methods ---

    async def add_devices(self, items: List[DeviceItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.devices_data_path, items, ['name', 'type', 'area', 'aliases', 'description'])
        self.reload()

    async def add_areas(self, items: List[AreaItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.areas_data_path, items, ['name', 'aliases', 'description'])
        self.reload()

    async def add_videos(self, items: List[VideoItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.videos_data_path, items, ['name', 'aliases', 'description', 'filename'])
        self.reload()

    async def _append_to_csv(self, file_path: str, items: List[BaseModel], columns: List[str]) -> None:
        try:
            new_data = [item.model_dump() for item in items]
            new_df = pd.DataFrame(new_data)
            
            # Ensure columns
            for col in columns:
                if col not in new_df.columns:
                    new_df[col] = None
            new_df = new_df[columns]

            # Backup
            backup_path = file_path + '.backup'
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
                existing_df = pd.read_csv(file_path)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df

            combined_df.to_csv(file_path, index=False, quoting=1)
            
            # Remove backup if successful
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
        except Exception as e:
            logger.error(f"Error appending to CSV {file_path}: {e}")
            # Restore backup if exists
            if os.path.exists(file_path + '.backup'):
                shutil.move(file_path + '.backup', file_path)
            raise e
