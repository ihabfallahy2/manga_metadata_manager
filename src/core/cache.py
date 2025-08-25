"""
Cache management for the Manga Metadata Manager.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from config.settings import CACHE_FILE
from utils.file_manager import FileManager


logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of processed folders and metadata."""
    
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self._cache: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load cache from file."""
        try:
            self._cache = FileManager.load_json(self.cache_file, {})
            logger.debug(f"Loaded cache with {len(self._cache)} entries")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self._cache = {}
    
    def save(self) -> bool:
        """
        Save cache to file.
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            success = FileManager.save_json(self.cache_file, self._cache)
            if success:
                logger.debug(f"Saved cache with {len(self._cache)} entries")
            else:
                logger.error("Failed to save cache")
            return success
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = value
    
    def has(self, key: str) -> bool:
        """
        Check if a key exists in cache.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists in cache
        """
        return key in self._cache
    
    def is_processed(self, folder_path: str) -> bool:
        """
        Check if a folder has been processed.
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            True if folder has been processed
        """
        return self.get(folder_path) == "done"
    
    def mark_processed(self, folder_path: str) -> None:
        """
        Mark a folder as processed.
        
        Args:
            folder_path: Path to the folder
        """
        self.set(folder_path, "done")
    
    def mark_failed(self, folder_path: str, error: str = "failed") -> None:
        """
        Mark a folder as failed to process.
        
        Args:
            folder_path: Path to the folder
            error: Error description
        """
        self.set(folder_path, f"error: {error}")
    
    def remove(self, key: str) -> bool:
        """
        Remove a key from cache.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if key was removed, False if key didn't exist
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total = len(self._cache)
        processed = sum(1 for v in self._cache.values() if v == "done")
        errors = sum(1 for v in self._cache.values() if str(v).startswith("error:"))
        
        return {
            "total": total,
            "processed": processed,
            "errors": errors,
            "pending": total - processed - errors
        }
    
    def cleanup_invalid_paths(self) -> int:
        """
        Remove cache entries for paths that no longer exist.
        
        Returns:
            Number of entries removed
        """
        invalid_paths = []
        
        for path in self._cache.keys():
            if not Path(path).exists():
                invalid_paths.append(path)
        
        for path in invalid_paths:
            del self._cache[path]
        
        if invalid_paths:
            logger.info(f"Removed {len(invalid_paths)} invalid cache entries")
        
        return len(invalid_paths)