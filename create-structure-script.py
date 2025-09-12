#!/usr/bin/env python3
"""
Script to create the project directory structure and __init__.py files
"""

from pathlib import Path

# Define the project structure
directories = [
    "src",
    "src/config",
    "src/core",
    "src/services",
    "src/ui",
    "src/ui/screens",
    "src/ui/styles",
    "src/utils",
    "tests",
]

# __init__.py content for each package
init_contents = {
    "src/__init__.py": '"""Manga Metadata Manager - A TUI application for managing manga metadata."""\n\n__version__ = "1.0.0"\n__author__ = "Your Name"\n__description__ = "A TUI application for managing manga metadata with AniList integration"',
    "src/config/__init__.py": '"""Configuration package for the Manga Metadata Manager."""',
    "src/core/__init__.py": '"""Core functionality package for the Manga Metadata Manager."""',
    "src/services/__init__.py": '"""External services package for the Manga Metadata Manager."""',
    "src/ui/__init__.py": '"""User interface package for the Manga Metadata Manager."""',
    "src/ui/screens/__init__.py": '"""Screens package for the Manga Metadata Manager UI."""',
    "src/ui/styles/__init__.py": '"""Styles package for the Manga Metadata Manager UI."""',
    "src/utils/__init__.py": '"""Utilities package for the Manga Metadata Manager."""',
    "tests/__init__.py": '"""Tests package for the Manga Metadata Manager."""',
}


def create_structure():
    """Create the directory structure and __init__.py files"""
    base_dir = Path.cwd()

    print(f"Creating project structure in: {base_dir}")

    # Create directories
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

    # Create __init__.py files
    for file_path, content in init_contents.items():
        full_path = base_dir / file_path
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content + "\n")
        print(f"Created file: {file_path}")

    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Copy your Python files to the appropriate src/ subdirectories")
    print("2. Run: python main.py")


if __name__ == "__main__":
    create_structure()
