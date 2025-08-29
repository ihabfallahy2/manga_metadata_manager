"""
Cache management for the Manga Metadata Manager.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

from config.settings import CACHE_FILE
from utils.file_manager import FileManager


logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of processed folders and metadata."""
    
    def __init__(self, cache_file: str = CACHE_FILE):
        self.cache_file = cache_file
        self._cache: Dict[str, Any] = {}
        self._cache_metadata: Dict[str, Any] = {}
        self.last_save = time.time()
        self.auto_save_interval = 30  # Save every 30 seconds
        self.load()
    
    def load(self) -> None:
        """Load cache from file."""
        try:
            data = FileManager.load_json(self.cache_file, {})
            self._cache = data.get("entries", {})
            self._cache_metadata = data.get("metadata", {})
            
            # Clean up old cache entries
            self._cleanup_old_entries()
            
            logger.debug(f"Loaded cache with {len(self._cache)} entries")
        except Exception as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Failed to load cache: {e}")
            self._cache = {}
            self._cache_metadata = {}
    
    def save(self, force: bool = False) -> bool:
        """
        Save cache to file.
        
        Args:
            force: Force save even if auto-save interval hasn't passed
            
        Returns:
            True if saved successfully, False otherwise
        """
        current_time = time.time()
        
        # Auto-save logic
        if not force and (current_time - self.last_save) < self.auto_save_interval:
            return True
        
        try:
            data = {
                "entries": self._cache,
                "metadata": self._cache_metadata,
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            success = FileManager.save_json(self.cache_file, data)
            if success:
                self.last_save = current_time
                logger.debug(f"Saved cache with {len(self._cache)} entries")
            else:
                # Log as warning instead of error to avoid notifications
                logger.warning("Failed to save cache")
            return success
        except Exception as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Error saving cache: {e}")
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
    
    def set(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            metadata: Optional metadata about the cache entry
        """
        self._cache[key] = value
        
        if metadata:
            self._cache_metadata[key] = {
                **metadata,
                "cached_at": datetime.now().isoformat()
            }
        
        # Auto-save periodically
        self.save()
    
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
    
    def mark_processed(self, folder_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark a folder as processed.
        
        Args:
            folder_path: Path to the folder
            metadata: Optional metadata about the processing
        """
        processing_metadata = {
            "status": "processed",
            "processed_at": datetime.now().isoformat()
        }
        
        if metadata:
            processing_metadata.update(metadata)
        
        self.set(folder_path, "done", processing_metadata)
    
    def mark_failed(self, folder_path: str, error: str = "failed", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark a folder as failed to process.
        
        Args:
            folder_path: Path to the folder
            error: Error description
            metadata: Optional metadata about the failure
        """
        failure_metadata = {
            "status": "failed",
            "error": error,
            "failed_at": datetime.now().isoformat()
        }
        
        if metadata:
            failure_metadata.update(metadata)
        
        self.set(folder_path, f"error: {error}", failure_metadata)
    
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
            if key in self._cache_metadata:
                del self._cache_metadata[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._cache_metadata.clear()
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
            self.remove(path)
        
        if invalid_paths:
            logger.info(f"Removed {len(invalid_paths)} invalid cache entries")
        
        return len(invalid_paths)
    
    def _cleanup_old_entries(self, max_age_days: int = 30) -> int:
        """
        Clean up cache entries older than specified days.
        
        Args:
            max_age_days: Maximum age in days for cache entries
            
        Returns:
            Number of entries removed
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        old_entries = []
        
        for key, metadata in self._cache_metadata.items():
            cached_at_str = metadata.get("cached_at")
            if cached_at_str:
                try:
                    cached_at = datetime.fromisoformat(cached_at_str)
                    if cached_at < cutoff_date:
                        old_entries.append(key)
                except ValueError:
                    # Invalid date format, keep entry
                    pass
        
        for key in old_entries:
            self.remove(key)
        
        if old_entries:
            logger.info(f"Removed {len(old_entries)} old cache entries")
        
        return len(old_entries)
    
    def get_failed_entries(self) -> List[Dict[str, Any]]:
        """
        Get list of failed cache entries.
        
        Returns:
            List of failed entries with their metadata
        """
        failed_entries = []
        
        for key, value in self._cache.items():
            if str(value).startswith("error:"):
                metadata = self._cache_metadata.get(key, {})
                failed_entries.append({
                    "path": key,
                    "error": str(value).replace("error: ", ""),
                    "metadata": metadata
                })
        
        return failed_entries
    
    def retry_failed_entries(self) -> List[str]:
        """
        Reset failed entries to allow retry.
        
        Returns:
            List of paths that were reset
        """
        failed_paths = []
        
        # Create a copy of keys to avoid modification during iteration
        keys_to_remove = []
        for key, value in self._cache.items():
            if str(value).startswith("error:"):
                keys_to_remove.append(key)
        
        # Remove the failed entries
        for key in keys_to_remove:
            failed_paths.append(key)
            self.remove(key)
        
        if failed_paths:
            logger.info(f"Reset {len(failed_paths)} failed entries for retry")
        
        return failed_paths
    
    def export_cache_info(self) -> Dict[str, Any]:
        """
        Export cache information for debugging.
        
        Returns:
            Dictionary with cache information
        """
        return {
            "cache_file": self.cache_file,
            "total_entries": len(self._cache),
            "stats": self.get_stats(),
            "failed_entries": self.get_failed_entries(),
            "last_save": datetime.fromtimestamp(self.last_save).isoformat(),
            "cache_size": len(str(self._cache))
        }