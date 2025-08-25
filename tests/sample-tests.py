# tests/test_utils.py
"""Tests for utility functions."""

import unittest
from src.utils.text_utils import TextProcessor
from src.utils.file_manager import FileManager


class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor."""
    
    def setUp(self):
        self.processor = TextProcessor()
    
    def test_clean_manga_title_basic(self):
        """Test basic title cleaning."""
        result = self.processor.clean_manga_title("One Piece")
        self.assertEqual(result, "One Piece")
    
    def test_clean_manga_title_with_brackets(self):
        """Test cleaning titles with brackets."""
        result = self.processor.clean_manga_title("Naruto [Digital]")
        self.assertEqual(result, "Naruto")
    
    def test_clean_manga_title_with_volume(self):
        """Test cleaning titles with volume numbers."""
        result = self.processor.clean_manga_title("Attack on Titan Vol 1")
        self.assertEqual(result, "Attack on Titan")
    
    def test_clean_manga_title_with_separators(self):
        """Test cleaning titles with separators."""
        result = self.processor.clean_manga_title("One-Piece_New.World")
        self.assertEqual(result, "One Piece New World")
    
    def test_truncate_text(self):
        """Test text truncation."""
        result = self.processor.truncate_text("This is a long text", 10)
        self.assertEqual(result, "This is...")
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        result = self.processor.sanitize_filename("file<name>")
        self.assertEqual(result, "file_name_")


class TestFileManager(unittest.TestCase):
    """Test cases for FileManager."""
    
    def test_load_nonexistent_json(self):
        """Test loading non-existent JSON file."""
        result = FileManager.load_json("nonexistent.json", {"default": True})
        self.assertEqual(result, {"default": True})
    
    def test_sanitize_filename_empty(self):
        """Test sanitizing empty filename."""
        result = TextProcessor.sanitize_filename("")
        self.assertEqual(result, "untitled")


# tests/test_metadata.py
"""Tests for metadata functionality."""

import unittest
from unittest.mock import Mock, patch
from src.core.metadata import MetadataManager


class TestMetadataManager(unittest.TestCase):
    """Test cases for MetadataManager."""
    
    def setUp(self):
        self.metadata_manager = MetadataManager()
    
    @patch('src.core.metadata.Path')
    def test_has_metadata_exists(self, mock_path):
        """Test checking if metadata exists."""
        mock_path.return_value.exists.return_value = True
        result = self.metadata_manager.has_metadata("/test/path")
        self.assertTrue(result)
    
    @patch('src.core.metadata.Path')
    def test_has_metadata_not_exists(self, mock_path):
        """Test checking if metadata doesn't exist."""
        mock_path.return_value.exists.return_value = False
        result = self.metadata_manager.has_metadata("/test/path")
        self.assertFalse(result)


# tests/test_scanner.py
"""Tests for scanner functionality."""

import unittest
from unittest.mock import Mock
from src.core.scanner import DirectoryScanner
from src.core.cache import CacheManager
from src.core.metadata import MetadataManager


class TestDirectoryScanner(unittest.TestCase):
    """Test cases for DirectoryScanner."""
    
    def setUp(self):
        self.cache_manager = Mock(spec=CacheManager)
        self.metadata_manager = Mock(spec=MetadataManager)
        self.scanner = DirectoryScanner(self.cache_manager, self.metadata_manager)
    
    def test_scanner_initialization(self):
        """Test scanner initialization."""
        self.assertIsNotNone(self.scanner.cache_manager)
        self.assertIsNotNone(self.scanner.metadata_manager)
        self.assertIsNotNone(self.scanner.text_processor)


if __name__ == '__main__':
    unittest.main()