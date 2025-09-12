"""
Directory scanner for manga folders.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..utils.text_utils import TextProcessor
from .cache import CacheManager
from .metadata import MetadataManager

logger = logging.getLogger(__name__)


class DirectoryScanner:
    """Scans directories for manga folders and manages metadata."""

    def __init__(self, cache_manager: CacheManager, metadata_manager: MetadataManager):
        self.cache_manager = cache_manager
        self.metadata_manager = metadata_manager
        self.text_processor = TextProcessor()

        # Statistics
        self.stats = {
            "total_folders": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "found_metadata": 0,
        }

    def scan_paths(
        self,
        paths: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Scan multiple paths for manga folders.

        Args:
            paths: List of base paths to scan
            progress_callback: Callback for progress updates (current, total, message)
            log_callback: Callback for log messages (level, message)

        Returns:
            Dictionary with scan results
        """
        self._reset_stats()
        folders_to_process = self._collect_folders(paths, log_callback)

        if not folders_to_process:
            self._log(log_callback, "info", "No folders found to process")
            return self.stats

        self.stats["total_folders"] = len(folders_to_process)

        # Process folders
        for i, folder_info in enumerate(folders_to_process, 1):
            folder_path = folder_info["path"]
            folder_name = folder_info["name"]

            # Update progress
            if progress_callback:
                progress_callback(
                    i, len(folders_to_process), f"Processing: {folder_name}"
                )

            try:
                success = self._process_folder(folder_path, folder_name, log_callback)
                if success:
                    self.stats["processed"] += 1
                    self.stats["found_metadata"] += 1
                else:
                    self.stats["errors"] += 1
            except Exception as e:
                # Log as warning instead of error to avoid notifications
                logger.warning(f"Error processing {folder_path}: {e}")
                self.stats["errors"] += 1
                self.cache_manager.mark_failed(folder_path, str(e))
                self._log(
                    log_callback, "warning", f"Error processing {folder_name}: {e}"
                )

        # Save cache after processing
        self.cache_manager.save()

        return self.stats

    def _collect_folders(
        self,
        paths: List[str],
        log_callback: Optional[Callable[[str, str], None]] = None,
    ) -> List[Dict[str, str]]:
        """
        Collect all folders that need processing.

        Args:
            paths: List of base paths to scan
            log_callback: Callback for log messages

        Returns:
            List of folder information dictionaries
        """
        folders_to_process = []

        for base_path in paths:
            if not Path(base_path).exists():
                self._log(log_callback, "warning", f"Path does not exist: {base_path}")
                continue

            try:
                for item in Path(base_path).iterdir():
                    if not item.is_dir():
                        continue

                    folder_path = str(item)
                    folder_name = item.name

                    # Check if already processed
                    if self._should_skip_folder(folder_path, folder_name, log_callback):
                        self.stats["skipped"] += 1
                        continue

                    folders_to_process.append(
                        {"path": folder_path, "name": folder_name}
                    )

            except Exception as e:
                # Log error but don't show as notification
                self._log(log_callback, "warning", f"Error scanning {base_path}: {e}")

        return folders_to_process

    def _should_skip_folder(
        self,
        folder_path: str,
        folder_name: str,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ) -> bool:
        """
        Check if a folder should be skipped.

        Args:
            folder_path: Path to the folder
            folder_name: Name of the folder
            log_callback: Callback for log messages

        Returns:
            True if folder should be skipped
        """
        # Check cache
        if self.cache_manager.is_processed(folder_path):
            self._log(log_callback, "info", f"Skipping cached: {folder_name}")
            return True

        # Check if metadata already exists
        if self.metadata_manager.has_metadata(folder_path):
            self._log(
                log_callback, "info", f"Skipping existing metadata: {folder_name}"
            )
            self.cache_manager.mark_processed(folder_path)
            return True

        return False

    def _process_folder(
        self,
        folder_path: str,
        folder_name: str,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ) -> bool:
        """
        Process a single folder to get metadata.

        Args:
            folder_path: Path to the folder
            folder_name: Name of the folder
            log_callback: Callback for log messages

        Returns:
            True if processed successfully
        """
        # Clean the folder name for searching
        cleaned_title = self.text_processor.clean_manga_title(folder_name)

        if not cleaned_title:
            self._log(log_callback, "warning", f"Could not clean title: {folder_name}")
            self.cache_manager.mark_failed(folder_path, "empty_title")
            return False

        self._log(log_callback, "info", f"Searching metadata for: {folder_name}")

        # Search and save metadata
        success = self.metadata_manager.search_and_save_metadata(
            folder_path, cleaned_title
        )

        if success:
            self.cache_manager.mark_processed(folder_path)
            self._log(log_callback, "success", f"Metadata saved: {folder_name}")
            return True
        else:
            self.cache_manager.mark_failed(folder_path, "not_found")
            self._log(log_callback, "warning", f"No metadata found: {folder_name}")
            return False

    def _reset_stats(self) -> None:
        """Reset scan statistics."""
        self.stats = {
            "total_folders": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "found_metadata": 0,
        }

    def _log(
        self,
        log_callback: Optional[Callable[[str, str], None]],
        level: str,
        message: str,
    ) -> None:
        """
        Send log message to callback only.

        Args:
            log_callback: Callback function for logs
            level: Log level (info, warning, error, success)
            message: Log message
        """
        if log_callback:
            log_callback(level, message)

        # Only log errors to Python logger to avoid notifications
        if level == "error":
            logger.error(message)

    def get_folder_summary(self, paths: List[str]) -> Dict[str, Any]:
        """
        Get a summary of folders in the given paths.

        Args:
            paths: List of paths to analyze

        Returns:
            Summary dictionary
        """
        summary = {
            "total_folders": 0,
            "with_metadata": 0,
            "without_metadata": 0,
            "cached_processed": 0,
            "folders_by_path": {},
        }

        for base_path in paths:
            if not Path(base_path).exists():
                continue

            path_summary = {"folders": 0, "with_metadata": 0, "cached": 0}

            try:
                for item in Path(base_path).iterdir():
                    if not item.is_dir():
                        continue

                    folder_path = str(item)
                    path_summary["folders"] += 1
                    summary["total_folders"] += 1

                    if self.metadata_manager.has_metadata(folder_path):
                        path_summary["with_metadata"] += 1
                        summary["with_metadata"] += 1
                    else:
                        summary["without_metadata"] += 1

                    if self.cache_manager.is_processed(folder_path):
                        path_summary["cached"] += 1
                        summary["cached_processed"] += 1

                summary["folders_by_path"][base_path] = path_summary

            except Exception as e:
                # Log as warning instead of error to avoid notifications
                logger.warning(f"Error analyzing {base_path}: {e}")

        return summary
