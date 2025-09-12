#!/usr/bin/env python3
"""
Manga Metadata Manager
A TUI application for managing manga metadata with AniList integration.
"""

import sys
from src.app import MangaMetadataApp

def main():
    """Main entry point for the application."""
    try:
        app = MangaMetadataApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by the user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()