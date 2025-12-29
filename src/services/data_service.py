import os
import shutil
import threading
import pandas as pd
from typing import Any
from loguru import logger
from pydantic import BaseModel
from langchain_core.documents import Document

from src.config.config import get_settings
from src.api.schemas import DeviceItem, AreaItem, MediaItem, DoorItem

class DataService:
    """
    Data Service for managing exhibition data (media, devices, areas, doors).
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
        self._media_cache: dict[str, dict[str, Any]] = {}
        self._doors_cache: dict[str, dict[str, Any]] = {}
        self._devices_cache: dict[str, dict[str, Any]] = {}
        self._areas_cache: dict[str, dict[str, Any]] = {}
        self._initialized = True
        
        self.reload()

    def reload(self) -> bool:
        """Reload data from CSV files."""
        try:
            settings = get_settings()
            # Use settings paths directly from DataSettings
            media_path = settings.data.media_data_path
            devices_path = settings.data.devices_data_path
            areas_path = settings.data.areas_data_path
            doors_path = settings.data.doors_data_path

            with self._data_lock:
                if os.path.exists(media_path):
                    media_df = self._load_csv_file(media_path)
                    self._media_cache = self._process_media_data(media_df)
                    logger.info(f"Loaded {len(self._media_cache)} media items from {media_path}")

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

    def _process_media_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        media_dict = {}
        if df.empty: return media_dict
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name: continue
            media_dict[name] = {
                "name": name,
                "type": str(row.get("type", "video")),
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
        return media_dict

    def _process_doors_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
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

    def _process_areas_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
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

    def _process_devices_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        import json
        devices_dict = {}
        if df.empty: return devices_dict
        
        def get_str_value(row, key, default=""):
            """获取字符串值，处理NaN情况"""
            val = row.get(key, default)
            if pd.isna(val):
                return default
            return str(val).strip()
        
        def parse_list_field(raw_value, field_name=""):
            """解析列表字段：仅支持JSON格式，非JSON格式会报错"""
            if not raw_value or pd.isna(raw_value):
                return []
            if isinstance(raw_value, list):
                return raw_value
            if isinstance(raw_value, str) and raw_value.strip():
                try:
                    parsed = json.loads(raw_value)
                    if isinstance(parsed, list):
                        return parsed
                    raise ValueError(f"字段 '{field_name}' 解析结果不是列表: {raw_value}")
                except json.JSONDecodeError as e:
                    raise ValueError(f"字段 '{field_name}' 不是有效的JSON格式: {raw_value}") from e
            return []
        
        for _, row in df.iterrows():
            name = get_str_value(row, "name")
            if not name: continue
            
            devices_dict[name] = {
                "name": name,
                "type": get_str_value(row, "type"),
                "subType": get_str_value(row, "subType"),
                "command": parse_list_field(row.get("command", ""), "command"),
                "area": get_str_value(row, "area"),
                "view": parse_list_field(row.get("view", ""), "view"),
                "aliases": get_str_value(row, "aliases"),
                "description": get_str_value(row, "description")
            }
        return devices_dict

    # --- Read Methods ---

    def media_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._media_cache

    def door_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._doors_cache

    def get_media_info(self, name: str) -> dict[str, Any] | None:
        with self._data_lock:
            return self._media_cache.get(name)

    def get_door_info(self, name: str) -> dict[str, Any] | None:
        with self._data_lock:
            return self._doors_cache.get(name)

    def get_all_media(self) -> list[str]:
        with self._data_lock:
            return list(self._media_cache.keys())

    def get_all_doors(self) -> list[str]:
        with self._data_lock:
            return list(self._doors_cache.keys())

    def area_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._areas_cache

    def get_area_info(self, name: str) -> dict[str, Any] | None:
        with self._data_lock:
            return self._areas_cache.get(name)

    def get_all_areas(self) -> list[str]:
        with self._data_lock:
            return list(self._areas_cache.keys())

    def device_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._devices_cache

    def get_device_info(self, name: str) -> dict[str, Any] | None:
        with self._data_lock:
            return self._devices_cache.get(name)

    def get_all_devices(self) -> list[str]:
        with self._data_lock:
            return list(self._devices_cache.keys())

    def get_all_doors_data(self) -> list[dict[str, Any]]:
        with self._data_lock:
            return list(self._doors_cache.values())

    def get_all_media_data(self) -> list[dict[str, Any]]:
        with self._data_lock:
            return list(self._media_cache.values())

    def get_all_devices_data(self) -> list[dict[str, Any]]:
        with self._data_lock:
            return list(self._devices_cache.values())

    def get_all_areas_data(self) -> list[dict[str, Any]]:
        with self._data_lock:
            return list(self._areas_cache.values())

    # --- Write Methods ---

    async def add_devices(self, items: list[DeviceItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.devices_data_path, items, ['name', 'type', 'subType', 'command', 'area', 'view', 'aliases', 'description'])
        self.reload()

    async def add_areas(self, items: list[AreaItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.areas_data_path, items, ['name', 'aliases', 'description'])
        self.reload()

    async def add_media(self, items: list[MediaItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.media_data_path, items, ['name', 'type', 'aliases', 'description'])
        self.reload()

    async def add_doors(self, items: list[DoorItem]) -> None:
        settings = get_settings()
        await self._append_to_csv(settings.data.doors_data_path, items, ['name', 'type', 'area1', 'area2', 'location'])
        self.reload()

    async def _append_to_csv(self, file_path: str, items: list[BaseModel], columns: list[str]) -> None:
        import json as json_module
        try:
            new_data = [item.model_dump() for item in items]
            new_df = pd.DataFrame(new_data)
            
            # 将列表字段序列化为JSON格式
            for col in new_df.columns:
                new_df[col] = new_df[col].apply(
                    lambda x: json_module.dumps(x, ensure_ascii=False) if isinstance(x, list) else x
                )
            
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

    async def clear_devices(self) -> None:
        """Clear all device data."""
        settings = get_settings()
        await self._clear_csv_file(settings.data.devices_data_path, ['name', 'type', 'subType', 'command', 'area', 'view', 'aliases', 'description'])
        self.reload()

    async def clear_areas(self) -> None:
        """Clear all area data."""
        settings = get_settings()
        await self._clear_csv_file(settings.data.areas_data_path, ['name', 'aliases', 'description'])
        self.reload()

    async def clear_media(self) -> None:
        """Clear all media data."""
        settings = get_settings()
        await self._clear_csv_file(settings.data.media_data_path, ['name', 'type', 'aliases', 'description'])
        self.reload()

    async def clear_doors(self) -> None:
        """Clear all door data."""
        settings = get_settings()
        await self._clear_csv_file(settings.data.doors_data_path, ['name', 'type', 'area1', 'area2', 'location'])
        self.reload()

    async def _clear_csv_file(self, file_path: str, columns: list[str]) -> None:
        """Clear a CSV file by writing only headers."""
        backup_path = file_path + '.backup'
        try:
            # Backup existing file
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
            
            # Write empty DataFrame with headers
            empty_df = pd.DataFrame(columns=columns)
            empty_df.to_csv(file_path, index=False, quoting=1)
            
            # Remove backup if successful
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
        except Exception as e:
            logger.error(f"Error clearing CSV file {file_path}: {e}")
            # Restore backup if exists
            if os.path.exists(backup_path):
                shutil.move(backup_path, file_path)
            raise e
