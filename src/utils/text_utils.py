"""
Text processing utilities for the Manga Metadata Manager.
"""

import re


class TextProcessor:
    """Handles text cleaning and processing operations."""

    # Patterns for cleaning manga titles
    BRACKETS_PATTERN = re.compile(r"[\(\[\{].*?[\)\]\}]")
    VOLUME_PATTERN = re.compile(
        r"(\bvol(?:ume)?|\btomo|\bcap|\bch|\bchapter)\s*\d+", flags=re.IGNORECASE
    )
    SEPARATOR_PATTERN = re.compile(r"[-_.]")
    WHITESPACE_PATTERN = re.compile(r"\s+")

    @classmethod
    def clean_manga_title(cls, title: str) -> str:
        """
        Clean a manga title for better search results.

        Removes:
        - Content in brackets/parentheses
        - Volume/chapter numbers
        - Special separators
        - Extra whitespace

        Args:
            title: Raw manga title

        Returns:
            Cleaned title suitable for searching
        """
        if not title:
            return ""

        # Remove content in brackets
        title = cls.BRACKETS_PATTERN.sub("", title)

        # Remove volume/chapter information
        title = cls.VOLUME_PATTERN.sub("", title)

        # Replace separators with spaces
        title = cls.SEPARATOR_PATTERN.sub(" ", title)

        # Normalize whitespace
        title = cls.WHITESPACE_PATTERN.sub(" ", title)

        return title.strip()

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to a maximum length with optional suffix.

        Args:
            text: Text to truncate
            max_length: Maximum length including suffix
            suffix: Suffix to add if text is truncated

        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text

        return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a string to be used as a filename.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename safe for filesystem use
        """
        # Remove invalid characters for most filesystems
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")

        # Remove leading/trailing spaces and dots
        filename = filename.strip(". ")

        return filename if filename else "untitled"
