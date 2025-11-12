#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from loguru import logger

from src.config.config import get_settings


class CSVLoader:
    """
    Async-safe CSV loader class for loading and validating resource data.

    This class provides thread-safe operations for loading CSV files containing
    video, door, and screen information. It supports caching, reloading, and
    validation of resources against the loaded data.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CSVLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the CSV loader with empty caches."""
        # Prevent re-initialization in singleton pattern
        if hasattr(self, '_initialized'):
            return

        self._data_lock = threading.Lock()
        self._videos_cache: dict[str, dict[str, Any]] = {}
        self._doors_cache: dict[str, dict[str, Any]] = {}
        self._screens_cache: dict[str, dict[str, Any]] = {}
        self._initialized = True

        # Load data on first initialization
        self.reload()

    def _load_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        Load a CSV file safely with error handling.

        Args:
            file_path: Path to the CSV file

        Returns:
            DataFrame containing the CSV data

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logger.exception(f"Failed to read CSV file '{file_path}'")
            raise IOError(f"Failed to read CSV file '{file_path}': {e}")

    def _process_videos_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        """
        Process videos DataFrame into a dictionary keyed by filename.

        Args:
            df: DataFrame containing video data

        Returns:
            Dictionary mapping filenames to video metadata
        """
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
        """
        Process doors DataFrame into a dictionary keyed by door name.

        Args:
            df: DataFrame containing door data

        Returns:
            Dictionary mapping door names to door metadata
        """
        doors_dict = {}
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            door_info = {
                "name": name,
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
            doors_dict[name] = door_info

        return doors_dict

    def _process_screens_data(self, df: pd.DataFrame) -> dict[str, dict[str, Any]]:
        """
        Process screens DataFrame into a dictionary keyed by screen name.

        Args:
            df: DataFrame containing screen data

        Returns:
            Dictionary mapping screen names to screen metadata
        """
        screens_dict = {}
        for _, row in df.iterrows():
            name = str(row.get("name", "")).strip()
            if not name:
                continue

            screen_info = {
                "name": name,
                "aliases": str(row.get("aliases", "")),
                "description": str(row.get("description", ""))
            }
            screens_dict[name] = screen_info

        return screens_dict

    def reload(self) -> bool:
        """
        Reload all CSV data from files.

        This method is thread-safe and can be called from any thread.
        It updates the internal caches with fresh data from the CSV files.

        Returns:
            True if reload was successful, False otherwise
        """
        # Try to get data directory from settings first
        try:
            settings = get_settings()
            data_dir = Path(settings.rag.videos_data_path).parent
            # Verify that the files exist in this directory
            if not (os.path.exists(os.path.join(data_dir, "videos.csv")) and
                    os.path.exists(os.path.join(data_dir, "doors.csv")) and
                    os.path.exists(os.path.join(data_dir, "screens.csv"))):
                raise FileNotFoundError("CSV files not found in settings directory")
        except Exception:
            # Fallback: calculate data directory relative to this file
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent  # src/core/csv_loader.py -> project root
            data_dir = project_root / "data"

        videos_path = os.path.join(data_dir, "videos.csv")
        doors_path = os.path.join(data_dir, "doors.csv")
        screens_path = os.path.join(data_dir, "screens.csv")

        try:
            with self._data_lock:
                # Load videos
                videos_df = self._load_csv_file(videos_path)
                self._videos_cache = self._process_videos_data(videos_df)
                logger.info(f"Loaded {len(self._videos_cache)} videos from {videos_path}")

                # Load doors
                doors_df = self._load_csv_file(doors_path)
                self._doors_cache = self._process_doors_data(doors_df)
                logger.info(f"Loaded {len(self._doors_cache)} doors from {doors_path}")

                # Load screens
                screens_df = self._load_csv_file(screens_path)
                self._screens_cache = self._process_screens_data(screens_df)
                logger.info(f"Loaded {len(self._screens_cache)} screens from {screens_path}")

            return True

        except Exception as e:
            logger.exception(f"Failed to reload CSV data: {e}")
            return False

    def video_exists(self, filename: str) -> bool:
        """
        Check if a video with the given filename exists.

        Args:
            filename: Video filename to check

        Returns:
            True if video exists, False otherwise
        """
        with self._data_lock:
            return filename in self._videos_cache

    def door_exists(self, name: str) -> bool:
        """
        Check if a door with the given name exists.

        Args:
            name: Door name to check

        Returns:
            True if door exists, False otherwise
        """
        with self._data_lock:
            return name in self._doors_cache

    def screen_exists(self, name: str) -> bool:
        """
        Check if a screen with the given name exists.

        Args:
            name: Screen name to check

        Returns:
            True if screen exists, False otherwise
        """
        with self._data_lock:
            return name in self._screens_cache

    def get_video_info(self, filename: str) -> Optional[dict[str, Any]]:
        """
        Get video information by filename.

        Args:
            filename: Video filename

        Returns:
            Video metadata dictionary or None if not found
        """
        with self._data_lock:
            return self._videos_cache.get(filename)

    def get_door_info(self, name: str) -> Optional[dict[str, Any]]:
        """
        Get door information by name.

        Args:
            name: Door name

        Returns:
            Door metadata dictionary or None if not found
        """
        with self._data_lock:
            return self._doors_cache.get(name)

    def get_screen_info(self, name: str) -> Optional[dict[str, Any]]:
        """
        Get screen information by name.

        Args:
            name: Screen name

        Returns:
            Screen metadata dictionary or None if not found
        """
        with self._data_lock:
            return self._screens_cache.get(name)

    def get_all_videos(self) -> list[str]:
        """
        Get list of all available video filenames.

        Returns:
            list of video filenames
        """
        with self._data_lock:
            return list(self._videos_cache.keys())

    def get_all_doors(self) -> list[str]:
        """
        Get list of all available door names.

        Returns:
            list of door names
        """
        with self._data_lock:
            return list(self._doors_cache.keys())

    def get_all_screens(self) -> list[str]:
        """
        Get list of all available screen names.

        Returns:
            list of screen names
        """
        with self._data_lock:
            return list(self._screens_cache.keys())