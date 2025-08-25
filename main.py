#!/usr/bin/env python3
"""
Manga Metadata Manager
A TUI application for managing manga metadata with AniList integration.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to src directory for relative imports
os.chdir(src_path)

try:
    from app import MangaMetadataApp
except ImportError as e:
    print(f"Error importing app: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
    sys.exit(1)


def main():
    """Main entry point for the application."""
    try:
        app = MangaMetadataApp()
        app.run()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()