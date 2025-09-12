"""Tests for scanner functionality."""

import unittest
from unittest.mock import Mock

from src.core.cache import CacheManager
from src.core.metadata import MetadataManager
from src.core.scanner import DirectoryScanner


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


if __name__ == "__main__":
    unittest.main()
