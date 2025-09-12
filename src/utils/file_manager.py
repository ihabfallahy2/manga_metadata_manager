"""
File management utilities for the Manga Metadata Manager.
"""

import json
from pathlib import Path
from typing import Any, List, Optional


class FileManager:
    """Handles file operations for configuration and data persistence."""

    @staticmethod
    def load_json(file_path: str, default: Optional[Any] = None) -> Any:
        """
        Load JSON data from a file.

        Args:
            file_path: Path to the JSON file
            default: Default value if file doesn't exist or is invalid

        Returns:
            Loaded JSON data or default value
        """
        path = Path(file_path)
        if not path.exists():
            return default if default is not None else {}

        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default if default is not None else {}

    @staticmethod
    def save_json(file_path: str, data: Any) -> bool:
        """
        Save data to a JSON file.

        Args:
            file_path: Path to save the file
            data: Data to serialize and save

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except (IOError, TypeError):
            return False

    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory_path: Path to the directory

        Returns:
            True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False

    @staticmethod
    def is_directory(path: str) -> bool:
        """
        Check if a path is a directory.

        Args:
            path: Path to check

        Returns:
            True if path is a directory
        """
        return Path(path).is_dir()

    @staticmethod
    def list_directories(base_path: str) -> List[str]:
        """
        List all directories in a base path.

        Args:
            base_path: Base directory to scan

        Returns:
            List of directory paths
        """
        try:
            base = Path(base_path)
            if not base.exists() or not base.is_dir():
                return []

            return [str(item) for item in base.iterdir() if item.is_dir()]
        except OSError:
            return []
