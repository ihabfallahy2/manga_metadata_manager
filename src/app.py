"""
Main application class for the Manga Metadata Manager.
"""

import logging
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView

from .config.settings import APP_TITLE, APP_VERSION
from .core.cache import CacheManager
from .core.metadata import MetadataManager
from .core.path_manager import PathManager
from .core.scanner import DirectoryScanner
from .ui.screens.add_path import AddPathScreen
from .ui.screens.scan import ScanScreen
from .utils.file_manager import FileManager

# Configure logging
logging.basicConfig(
    level=logging.ERROR,  # Only show ERROR level messages to reduce console output
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
        ("c", "clear_cache", "Clear Cache"),
        ("v", "validate_paths", "Validate Paths"),
        ("i", "show_cache_info", "Cache Info"),
        ("x", "export_cache", "Export Cache"),
        ("t", "retry_failed", "Retry Failed"),
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

            stats_text = (
                f"Folders: {total} | With metadata: {with_metadata} | Cached: {cached}"
            )
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

    def show_info(self, message: str, level: str = "info", timeout: int = 5) -> None:
        """
        Show information as a pop-up notification.

        Args:
            message: Message to display
            level: Level (info, warning, error, success)
            timeout: Time to show the message in seconds
        """
        # Use Textual's native notifications with custom styling
        if level == "error":
            self.notify(f"❌ {message}", severity="error", timeout=timeout)
        elif level == "warning":
            self.notify(f"⚠️  {message}", severity="warning", timeout=timeout)
        elif level == "success":
            self.notify(f"✅ {message}", severity="information", timeout=timeout)
        else:
            self.notify(f"ℹ️  {message}", severity="information", timeout=timeout)

    def clear_info(self) -> None:
        """Clear the info area (no longer needed)."""
        pass

    def action_clear_cache(self) -> None:
        """Action to clear the cache."""
        self.cache_manager.clear()
        self.cache_manager.save(force=True)
        self.show_info("✅ Cache cleared successfully", "success", 3)
        logger.info("Cache cleared by user")

    def action_validate_paths(self) -> None:
        """Action to validate all configured paths."""
        paths = self.path_manager.get_paths()
        valid_paths = []
        invalid_paths = []

        for path in paths:
            if Path(path).exists():
                valid_paths.append(path)
            else:
                invalid_paths.append(path)

        if invalid_paths:
            message = f"⚠️  Path Validation: {len(valid_paths)} valid, {len(invalid_paths)} invalid"
            self.show_info(message, "warning", 5)
        else:
            message = f"✅ All {len(valid_paths)} paths are valid"
            self.show_info(message, "success", 3)

        logger.info(
            f"Path validation: {len(valid_paths)} valid, {len(invalid_paths)} invalid"
        )

    def action_show_cache_info(self) -> None:
        """Action to show cache statistics."""
        stats = self.cache_manager.get_stats()
        message = f"📊 Cache: {stats['total']} total, {stats['processed']} processed, {stats['errors']} errors"
        self.show_info(message, "info", 4)
        logger.info("Cache statistics displayed")

    def action_export_cache(self) -> None:
        """Action to export cache information."""
        try:
            cache_info = self.cache_manager.export_cache_info()
            output_file = "cache_info.json"
            FileManager.save_json(output_file, cache_info)
            self.show_info(f"💾 Cache info exported to {output_file}", "success", 3)
            logger.info(f"Cache info exported to {output_file}")
        except Exception as e:
            self.show_info(f"❌ Failed to export cache info: {e}", "error", 5)
            logger.error(f"Failed to export cache info: {e}")

    def action_retry_failed(self) -> None:
        """Action to retry failed cache entries."""
        retried = self.cache_manager.retry_failed_entries()
        self.cache_manager.save(force=True)
        if retried:
            self.show_info(
                f"🔄 Reset {len(retried)} failed entries for retry", "success", 3
            )
        else:
            self.show_info("ℹ️  No failed entries to retry", "info", 2)
        logger.info(f"Reset {len(retried)} failed entries for retry")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle path selection in the list."""
        # Could be used for path-specific actions in the future
        pass

    def on_screen_resume(self) -> None:
        """Called when returning from a screen."""
        # Refresh display when returning from other screens
        self.refresh_path_list()
        self.update_status()


def main():
    """Main entry point for running the application directly."""
    app = MangaMetadataApp()
    app.run()


if __name__ == "__main__":
    main()
