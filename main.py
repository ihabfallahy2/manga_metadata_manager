#!/usr/bin/env python3
"""
Manga Metadata Manager
A TUI application for managing manga metadata with AniList integration.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
# This allows the application to be run from the root directory
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from app import MangaMetadataApp


def main():
    """Main entry point for the application."""
    try:
        app = MangaMetadataApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplicación cerrada por el usuario.")
    except Exception as e:
        print(f"Error inesperado: {e}")
        # It's useful to see the traceback for debugging
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()