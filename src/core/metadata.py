"""
Metadata management for manga folders.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import METADATA_FOLDER, METADATA_FILE, COVER_FILE
from utils.file_manager import FileManager
from services.anilist import AniListService


logger = logging.getLogger(__name__)


class MetadataManager:
    """Manages metadata operations for manga folders."""
    
    def __init__(self):
        self.anilist_service = AniListService()
    
    def has_metadata(self, folder_path: str) -> bool:
        """
        Check if a folder already has metadata.
        
        Args:
            folder_path: Path to the manga folder
            
        Returns:
            True if metadata exists
        """
        metadata_path = Path(folder_path) / METADATA_FOLDER / METADATA_FILE
        return metadata_path.exists()
    
    def get_metadata_path(self, folder_path: str) -> Path:
        """
        Get the metadata directory path for a folder.
        
        Args:
            folder_path: Path to the manga folder
            
        Returns:
            Path to the metadata directory
        """
        return Path(folder_path) / METADATA_FOLDER
    
    def load_metadata(self, folder_path: str) -> Optional[Dict[str, Any]]:
        """
        Load existing metadata from a folder.
        
        Args:
            folder_path: Path to the manga folder
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_file = self.get_metadata_path(folder_path) / METADATA_FILE
        
        if not metadata_file.exists():
            return None
        
        try:
            return FileManager.load_json(str(metadata_file))
        except Exception as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
            return None
    
    def save_metadata(self, folder_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata to a folder.
        
        Args:
            folder_path: Path to the manga folder
            metadata: Metadata dictionary to save
            
        Returns:
            True if saved successfully
        """
        metadata_dir = self.get_metadata_path(folder_path)
        
        # Ensure metadata directory exists
        try:
            metadata_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Failed to create metadata directory {metadata_dir}: {e}")
            return False
        
        # Save metadata JSON
        metadata_file = metadata_dir / METADATA_FILE
        success = FileManager.save_json(str(metadata_file), metadata)
        
        if not success:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Failed to save metadata to {metadata_file}")
            return False
        
        # Download and save cover image
        self._save_cover_image(metadata_dir, metadata)
        
        logger.info(f"Saved metadata for {Path(folder_path).name}")
        return True
    
    def _save_cover_image(self, metadata_dir: Path, metadata: Dict[str, Any]) -> bool:
        """
        Download and save cover image.
        
        Args:
            metadata_dir: Path to metadata directory
            metadata: Metadata containing cover image URL
            
        Returns:
            True if cover was saved successfully
        """
        cover_url = metadata.get("coverImage", {}).get("extraLarge")
        if not cover_url:
            logger.debug("No cover image URL found in metadata")
            return False
        
        try:
            image_data = self.anilist_service.download_image(cover_url)
            if image_data:
                cover_path = metadata_dir / COVER_FILE
                with cover_path.open("wb") as f:
                    f.write(image_data)
                logger.debug(f"Saved cover image to {cover_path}")
                return True
            else:
                logger.warning(f"Failed to download cover image from {cover_url}")
                return False
        except Exception as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Error saving cover image: {e}")
            return False
    
    def search_and_save_metadata(self, folder_path: str, search_title: str) -> bool:
        """
        Search for metadata and save it to a folder.
        
        Args:
            folder_path: Path to the manga folder
            search_title: Title to search for
            
        Returns:
            True if metadata was found and saved
        """
        if not search_title.strip():
            logger.warning(f"Empty search title for folder: {folder_path}")
            return False
        
        # Search for metadata
        metadata = self.anilist_service.search_manga(search_title)
        
        if not metadata:
            logger.info(f"No metadata found for: {search_title}")
            return False
        
        # Add additional information
        metadata["search_title"] = search_title
        metadata["folder_name"] = Path(folder_path).name
        metadata["created_at"] = self._get_current_timestamp()
        
        # Save metadata
        return self.save_metadata(folder_path, metadata)
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            Current timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def update_metadata(self, folder_path: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing metadata with new information.
        
        Args:
            folder_path: Path to the manga folder
            updates: Dictionary of updates to apply
            
        Returns:
            True if updated successfully
        """
        existing_metadata = self.load_metadata(folder_path)
        
        if not existing_metadata:
            logger.warning(f"No existing metadata found for: {folder_path}")
            return False
        
        # Apply updates
        existing_metadata.update(updates)
        existing_metadata["updated_at"] = self._get_current_timestamp()
        
        return self.save_metadata(folder_path, existing_metadata)
    
    def delete_metadata(self, folder_path: str) -> bool:
        """
        Delete metadata from a folder.
        
        Args:
            folder_path: Path to the manga folder
            
        Returns:
            True if deleted successfully
        """
        metadata_dir = self.get_metadata_path(folder_path)
        
        if not metadata_dir.exists():
            return True  # Already deleted
        
        try:
            # Remove all files in metadata directory
            for file_path in metadata_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            
            # Remove directory if empty
            if not any(metadata_dir.iterdir()):
                metadata_dir.rmdir()
            
            logger.info(f"Deleted metadata for {Path(folder_path).name}")
            return True
        except Exception as e:
            # Log as warning instead of error to avoid notifications
            logger.warning(f"Failed to delete metadata from {metadata_dir}: {e}")
            return False
    
    def get_metadata_summary(self, folder_path: str) -> Dict[str, Any]:
        """
        Get a summary of metadata for a folder.
        
        Args:
            folder_path: Path to the manga folder
            
        Returns:
            Dictionary with metadata summary
        """
        metadata = self.load_metadata(folder_path)
        
        if not metadata:
            return {
                "has_metadata": False,
                "folder_name": Path(folder_path).name
            }
        
        title = metadata.get("title", {})
        
        return {
            "has_metadata": True,
            "folder_name": Path(folder_path).name,
            "title_romaji": title.get("romaji"),
            "title_english": title.get("english"),
            "status": metadata.get("status"),
            "chapters": metadata.get("chapters"),
            "volumes": metadata.get("volumes"),
            "score": metadata.get("averageScore"),
            "genres": metadata.get("genres", []),
            "created_at": metadata.get("created_at"),
            "updated_at": metadata.get("updated_at")
        }