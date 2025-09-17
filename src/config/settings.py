"""
Configuration settings for the Manga Metadata Manager.
"""

from pathlib import Path

# File paths
CONFIG_FILE = "config.json"
CACHE_FILE = "cache.json"

# API settings
ANILIST_URL = "https://graphql.anilist.co"
REQUEST_TIMEOUT = 10

# Application settings
APP_TITLE = "Manga Metadata Manager"
APP_VERSION = "1.0.0"

# Paths
# Use the project's root directory for storing config and cache
# The project root is the parent of the 'src' directory
APP_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = APP_ROOT / "config"
CACHE_DIR = APP_ROOT / "cache"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# File extensions to consider as manga folders
MANGA_EXTENSIONS = {'.cbz', '.cbr', '.zip', '.rar', '.pdf'}

# Metadata folder name
METADATA_FOLDER = "metadata"
METADATA_FILE = "metadata.json"
COVER_FILE = "cover.jpg"