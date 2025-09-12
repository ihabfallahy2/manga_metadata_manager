"""Tests for metadata functionality."""

import unittest
from unittest.mock import patch

from src.core.metadata import MetadataManager


class TestMetadataManager(unittest.TestCase):
    """Test cases for MetadataManager."""

    def setUp(self):
        self.metadata_manager = MetadataManager()

    @patch("src.core.metadata.Path")
    def test_has_metadata_exists(self, mock_path):
        """Test checking if metadata exists."""
        # Setup the mock to return True from the final .exists() call
        mock_path.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = (
            True
        )
        result = self.metadata_manager.has_metadata("/test/path")
        self.assertTrue(result)

    @patch("src.core.metadata.Path")
    def test_has_metadata_not_exists(self, mock_path):
        """Test checking if metadata doesn't exist."""
        # Setup the mock to return False from the final .exists() call
        mock_path.return_value.__truediv__.return_value.__truediv__.return_value.exists.return_value = (
            False
        )
        result = self.metadata_manager.has_metadata("/test/path")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
