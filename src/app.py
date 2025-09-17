"""
Main application class for the Manga Metadata Manager.
"""

import logging
from pathlib import Path
from typing import List

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, ListView, ListItem, Label
from textual.containers import Horizontal, Vertical

from config.settings import CONFIG_DIR, CONFIG_FILE, APP_TITLE, APP_VERSION
from utils.file_manager import FileManager
from core.cache import CacheManager
from core.metadata import MetadataManager
from core.scanner import DirectoryScanner
from ui.screens.add_path import AddPathScreen
from ui.screens.scan import ScanScreen


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PathManager:
    """Manages manga collection paths."""
    
    def __init__(self):
        self.config_file = CONFIG_DIR / CONFIG_FILE
        self._paths: List[str] = []
        self.load_paths()
    
    def load_paths(self) -> None:
        """Load paths from configuration file."""
        config = FileManager.load_json(str(self.config_file), {})
        self._paths = config.get("paths", [])
        logger.info(f"Loaded {len(self._paths)} paths from {self.config_file}")
    
    def save_paths(self) -> bool:
        """Save paths to configuration file."""
        config = {"paths": self._paths}
        success = FileManager.save_json(str(self.config_file), config)
        if success:
            logger.info(f"Saved {len(self._paths)} paths to {self.config_file}")
        else:
            logger.error("Failed to save paths to config")
        return success
    
    def get_paths(self) -> List[str]:
        """Get list of configured paths."""
        return self._paths.copy()
    
    def add_path(self, path: str) -> bool:
        """Add a new path."""
        path = str(Path(path).resolve())
        if path not in self._paths:
            self._paths.append(path)
            return self.save_paths()
        return True
    
    def remove_path(self, path: str) -> bool:
        """Remove a path."""
        if path in self._paths:
            self._paths.remove(path)
            return self.save_paths()
        return False
    
    def remove_path_by_index(self, index: int) -> bool:
        """Remove a path by index."""
        if 0 <= index < len(self._paths):
            removed_path = self._paths.pop(index)
            logger.info(f"Removed path: {removed_path}")
            return self.save_paths()
        return False


class MangaMetadataApp(App):
    """Main application for Manga Metadata Manager."""
    
    CSS_PATH = Path(__file__).parent / "ui" / "styles" / "app.css"
    TITLE = APP_TITLE
    SUB_TITLE = f"Version {APP_VERSION}"
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("a", "add_path", "Add Path"),
        ("d", "delete_path", "Delete Path"),
        ("s", "scan", "Scan"),
        ("r", "refresh", "Refresh"),
    ]
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.path_manager = PathManager()
        self.cache_manager = CacheManager()
        self.metadata_manager = MetadataManager()
        self.scanner = DirectoryScanner(self.cache_manager, self.metadata_manager)
        
        logger.info("Application initialized")
    
    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()
        
        with Vertical(id="main-container"):
            yield Label("Manga Collection Paths", id="paths-title")
            
            # Path list
            self.path_list = ListView(id="path-list")
            yield self.path_list
            
            # Status information
            with Horizontal(id="status-container"):
                self.status_label = Label("Ready", id="status")
                yield self.status_label
                
                self.stats_label = Label("", id="stats")
                yield self.stats_label
            
            # Action buttons
            with Horizontal(id="button-container"):
                yield Button("Add Path", variant="primary", id="add-path")
                yield Button("Remove Path", variant="default", id="remove-path")
                yield Button("Scan All", variant="success", id="scan")
                yield Button("Refresh", variant="default", id="refresh")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        self.refresh_path_list()
        self.update_status()
    
    def refresh_path_list(self) -> None:
        """Refresh the path list display."""
        self.path_list.clear()
        
        paths = self.path_manager.get_paths()
        if not paths:
            self.path_list.append(ListItem(Label("No paths configured")))
            return
        
        for path in paths:
            path_obj = Path(path)
            
            # Check if path exists
            if path_obj.exists():
                status = "✅"
                style = "path-valid"
            else:
                status = "❌"
                style = "path-invalid"
            
            label_text = f"{status} {path}"
            label = Label(label_text)
            label.add_class(style)
            
            self.path_list.append(ListItem(label))
        
        logger.debug(f"Refreshed path list with {len(paths)} paths")
    
    def update_status(self) -> None:
        """Update status and statistics display."""
        paths = self.path_manager.get_paths()
        valid_paths = [p for p in paths if Path(p).exists()]
        
        if not paths:
            self.status_label.update("No paths configured")
        elif not valid_paths:
            self.status_label.update("No valid paths found")
        else:
            self.status_label.update(f"Ready - {len(valid_paths)} path(s) configured")
        
        # Update statistics
        self._update_stats()
    
    def _update_stats(self) -> None:
        """Update statistics display."""
        try:
            valid_paths = [p for p in self.path_manager.get_paths() if Path(p).exists()]
            
            if not valid_paths:
                self.stats_label.update("")
                return
            
            # Get folder summary
            summary = self.scanner.get_folder_summary(valid_paths)
            
            total = summary.get("total_folders", 0)
            with_metadata = summary.get("with_metadata", 0)
            cached = summary.get("cached_processed", 0)
            
            stats_text = f"Folders: {total} | With metadata: {with_metadata} | Cached: {cached}"
            self.stats_label.update(stats_text)
            
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            self.stats_label.update("Stats unavailable")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-path":
            self.action_add_path()
        elif event.button.id == "remove-path":
            self.action_delete_path()
        elif event.button.id == "scan":
            self.action_scan()
        elif event.button.id == "refresh":
            self.action_refresh()
    
    def action_add_path(self) -> None:
        """Action to add a new path."""
        self.push_screen(AddPathScreen())
    
    def action_delete_path(self) -> None:
        """Action to delete selected path."""
        if self.path_list.index is not None:
            paths = self.path_manager.get_paths()
            if 0 <= self.path_list.index < len(paths):
                removed_path = paths[self.path_list.index]
                success = self.path_manager.remove_path_by_index(self.path_list.index)
                
                if success:
                    self.refresh_path_list()
                    self.update_status()
                    logger.info(f"Removed path: {removed_path}")
                else:
                    logger.error(f"Failed to remove path: {removed_path}")
    
    def action_scan(self) -> None:
        """Action to start scanning."""
        valid_paths = [p for p in self.path_manager.get_paths() if Path(p).exists()]
        
        if not valid_paths:
            logger.warning("No valid paths to scan")
            return
        
        self.push_screen(ScanScreen(self.scanner, valid_paths))
    
    def action_refresh(self) -> None:
        """Action to refresh the display."""
        self.path_manager.load_paths()
        self.refresh_path_list()
        self.update_status()
        logger.info("Display refreshed")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle path selection in the list."""
        # Could be used for path-specific actions in the future
        pass
    
    def on_screen_resume(self) -> None:
        """Called when returning from a screen."""
        # Refresh display when returning from other screens
        self.refresh_path_list()
        self.update_status()


if __name__ == "__main__":
    app = MangaMetadataApp()
    app.run()