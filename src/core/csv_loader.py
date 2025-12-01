#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from src.config.config import get_settings


class CSVLoader:
    """线程安全的CSV数据加载器。"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CSVLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self._data_lock = threading.Lock()
        self._videos_cache: dict[str, dict[str, Any]] = {}
        self._doors_cache: dict[str, dict[str, Any]] = {}
        self._devices_cache: dict[str, dict[str, Any]] = {}
        self._areas_cache: dict[str, dict[str, Any]] = {}
        self._initialized = True

        self.reload()

    def _load_csv_file(self, file_path: str) -> pd.DataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logger.exception(f"Failed to read CSV file '{file_path}'")
            raise IOError(f"Failed to read CSV file '{file_path}': {e}")

    def _process_videos_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        videos_dict = {}
        for _, row in df.iterrows():
            filename = str(row.get("filename", "")).strip()
            if not filename:
                continue

            video_info = {
                "type": str(row.get("type", "video")),
                "name": str(row.get("name", "")),
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", "")),
                "filename": filename
            }
            videos_dict[filename] = video_info

        return videos_dict

    def _process_doors_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        doors_dict = {}
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            door_type = str(row.get("type", "")).strip()
            door_info = {
                "name": name,
                "type": door_type,
                "area1": str(row.get("area1", "")).strip(),
                "area2": str(row.get("area2", "")).strip(),
                "location": str(row.get("location", "")).strip()
            }
            doors_dict[name] = door_info

        return doors_dict



    def _process_areas_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        areas_dict = {}
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            area_info = {
                "name": name,
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
            areas_dict[name] = area_info

        return areas_dict

    def _process_devices_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        devices_dict = {}
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            device_info = {
                "name": name,
                "type": str(row.get("type", "")),
                "area": str(row.get("area", "")),
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
            devices_dict[name] = device_info

        return devices_dict

    def reload(self) -> bool:
        try:
            settings = get_settings()
            data_dir = settings.data_dir
            if not (os.path.exists(os.path.join(data_dir, "videos.csv")) and
                    os.path.exists(os.path.join(data_dir, "doors.csv")) and
                    os.path.exists(os.path.join(data_dir, "devices.csv")) and
                    os.path.exists(os.path.join(data_dir, "areas.csv"))):
                raise FileNotFoundError("CSV files not found in settings directory")
        except Exception:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            data_dir = project_root / "data"

        videos_path = os.path.join(data_dir, "videos.csv")
        doors_path = os.path.join(data_dir, "doors.csv")
        devices_path = os.path.join(data_dir, "devices.csv")
        areas_path = os.path.join(data_dir, "areas.csv")

        try:
            with self._data_lock:
                videos_df = self._load_csv_file(videos_path)
                self._videos_cache = self._process_videos_data(videos_df)
                logger.info(f"Loaded {len(self._videos_cache)} videos from {videos_path}")

                doors_df = self._load_csv_file(doors_path)
                self._doors_cache = self._process_doors_data(doors_df)
                logger.info(f"Loaded {len(self._doors_cache)} doors from {doors_path}")

                devices_df = self._load_csv_file(devices_path)
                self._devices_cache = self._process_devices_data(devices_df)
                logger.info(f"Loaded {len(self._devices_cache)} devices from {devices_path}")

                areas_df = self._load_csv_file(areas_path)
                self._areas_cache = self._process_areas_data(areas_df)
                logger.info(f"Loaded {len(self._areas_cache)} areas from {areas_path}")

            return True

        except Exception as e:
            logger.exception(f"Failed to reload CSV data: {e}")
            return False

    def video_exists(self, filename: str) -> bool:
        with self._data_lock:
            return filename in self._videos_cache

    def door_exists(self, name: str) -> bool:
        with self._data_lock:
            return name in self._doors_cache

    def get_video_info(self, filename: str) -> dict[str, Any] | None:
        with self._data_lock:
            return self._videos_cache.get(filename)

    def get_door_info(self, name: str) -> dict[str, Any] | None:
        with self._data_lock:
            return self._doors_cache.get(name)

    def get_all_videos(self) -> list[str]:
        with self._data_lock:
            return list(self._videos_cache.keys())

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
