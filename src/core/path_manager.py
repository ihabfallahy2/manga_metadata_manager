"""
Path management for the Manga Metadata Manager.
"""

import logging
from pathlib import Path
from typing import List

from ..config.settings import CONFIG_FILE
from ..utils.file_manager import FileManager

logger = logging.getLogger(__name__)


class PathManager:
    """Manages manga collection paths."""

    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self._paths: List[str] = []
        self.load_paths()

    def load_paths(self) -> None:
        """Load paths from configuration file."""
        config = FileManager.load_json(self.config_file, {})
        self._paths = config.get("paths", [])
        logger.info(f"Loaded {len(self._paths)} paths from config")

    def save_paths(self) -> bool:
        """Save paths to configuration file."""
        config = {"paths": self._paths}
        success = FileManager.save_json(self.config_file, config)
        if success:
            logger.info(f"Saved {len(self._paths)} paths to config")
        else:
            logger.error("Failed to save paths to config")
        return success

    def get_paths(self) -> List[str]:
        """Get list of configured paths."""
        return self._paths.copy()

    def add_path(self, path: str) -> bool:
        """Add a new path."""
        path = str(Path(path).resolve())
        if path not in self._paths:
            self._paths.append(path)
            return self.save_paths()
        return True

    def remove_path(self, path: str) -> bool:
        """Remove a path."""
        if path in self._paths:
            self._paths.remove(path)
            return self.save_paths()
        return False

    def remove_path_by_index(self, index: int) -> bool:
        """Remove a path by index."""
        if 0 <= index < len(self._paths):
            removed_path = self._paths.pop(index)
            logger.info(f"Removed path: {removed_path}")
            return self.save_paths()
        return False
