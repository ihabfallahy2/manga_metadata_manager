"""
Screen for scanning manga directories and fetching metadata.
"""

from pathlib import Path
from typing import Any, Dict

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, ProgressBar, Static

from ...core.scanner import DirectoryScanner


class LogWidget(ScrollableContainer):
    """Custom log widget that scrolls to bottom automatically."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_lines = []

    def compose(self) -> ComposeResult:
        """Compose the log widget."""
        self.log_content = Static("", id="log-content")
        yield self.log_content

    def write(self, message: str) -> None:
        """Write a message to the log."""
        self.log_lines.append(message)
        self.log_content.update("\n".join(self.log_lines))
        # Auto-scroll to bottom
        self.call_after_refresh(self.scroll_end)

    def clear(self) -> None:
        """Clear the log."""
        self.log_lines.clear()
        self.log_content.update("")


class ScanScreen(Screen):
    """Screen for scanning manga directories."""

    # Inherit bindings from main app
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

    def __init__(self, scanner: DirectoryScanner, paths: list[str]):
        super().__init__()
        self.scanner = scanner
        self.paths = paths
        self.is_scanning = False
        self.scan_results: Dict[str, Any] = {}
        self.current_folder = ""
        self.total_folders = 0
        self.processed_folders = 0

    def compose(self) -> ComposeResult:
        """Compose the scan screen layout."""
        with Vertical(id="scan-container"):
            yield Label("Scanning Manga Directories", id="scan-title")

            # Progress section
            with Vertical(id="progress-section"):
                yield Label("Ready to scan", id="status-label")
                yield ProgressBar(total=100, show_eta=True, id="progress-bar")
                yield Label("0 / 0 folders processed", id="progress-text")
                yield Label("", id="current-folder")

            # Log section
            with Vertical(id="log-section"):
                yield Label("Scan Log:", id="log-title")
                self.log_widget = LogWidget(id="scan-log")
                yield self.log_widget

            # Control buttons
            with Horizontal(id="control-buttons"):
                yield Button("Start Scan", variant="primary", id="start-scan")
                yield Button(
                    "Stop Scan", variant="default", id="stop-scan", disabled=True
                )
                yield Button("Clear Log", variant="default", id="clear-log")
                yield Button("Back", variant="default", id="back")

            # Results section (initially hidden)
            with Vertical(id="results-section"):
                yield Label("Scan Results:", id="results-title")
                yield Label("", id="results-summary")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self._update_status("Ready to scan")
        self._log_info(f"Configured to scan {len(self.paths)} path(s):")
        for i, path in enumerate(self.paths, 1):
            self._log_info(f"  {i}. {path}")

        # Initialize progress bar
        self._update_progress(0, 0, "Ready")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "start-scan":
            self._start_scan()
        elif event.button.id == "stop-scan":
            self._stop_scan()
        elif event.button.id == "clear-log":
            self._clear_log()
        elif event.button.id == "back":
            if not self.is_scanning:
                self.app.pop_screen()

    def _start_scan(self) -> None:
        """Start the scanning process."""
        if self.is_scanning:
            return

        self.is_scanning = True
        self.processed_folders = 0
        self.current_folder = ""
        self._update_scan_buttons(scanning=True)
        self._update_status("Starting scan...")
        self._clear_log()
        self._log_info("Starting manga directory scan...")

        # Start scanning in background thread
        self.scan_worker()

    def _stop_scan(self) -> None:
        """Stop the scanning process."""
        if not self.is_scanning:
            return

        self.is_scanning = False
        self._update_scan_buttons(scanning=False)
        self._update_status("Scan stopped by user")
        self._log_warning("Scan interrupted by user")

        # Cancel any running workers
        self.workers.cancel_all()

    @work(exclusive=True, thread=True)
    def scan_worker(self) -> None:
        """Worker for scanning directories."""
        try:
            # Perform the scan
            results = self.scanner.scan_paths(
                self.paths,
                progress_callback=self._progress_callback,
                log_callback=self._log_callback,
            )

            # Update UI with results
            self.call_after_refresh(self._scan_completed, results)

        except Exception as e:
            self.call_after_refresh(self._scan_error, str(e))

    def _progress_callback(self, current: int, total: int, message: str) -> None:
        """Callback for progress updates."""
        if not self.is_scanning:
            return

        self.call_after_refresh(self._update_progress, current, total, message)

    def _log_callback(self, level: str, message: str) -> None:
        """Callback for log messages."""
        self.call_after_refresh(self._log_message, level, message)

    def _update_progress(self, current: int, total: int, message: str) -> None:
        """Update progress display."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_text = self.query_one("#progress-text", Label)
        current_folder_label = self.query_one("#current-folder", Label)

        # Update progress bar
        if total > 0:
            progress_bar.total = total
            progress_bar.progress = current
            progress_text.update(f"{current} / {total} folders processed")

            # Calculate percentage
            percentage = (current / total) * 100
            self._update_status(f"Scanning... {percentage:.1f}% - {message}")
        else:
            progress_bar.total = 100
            progress_bar.progress = 0
            progress_text.update("Preparing scan...")
            self._update_status(message)

        # Update current folder display
        if message and "Processing:" in message:
            folder_name = message.replace("Processing: ", "")
            current_folder_label.update(f"Current: {folder_name}")
        else:
            current_folder_label.update("")

    def _log_message(self, level: str, message: str) -> None:
        """Add a message to the log."""
        if level == "success":
            self._log_success(message)
        elif level == "warning":
            self._log_warning(message)
        elif level == "error":
            self._log_error(message)
        else:
            self._log_info(message)

    def _scan_completed(self, results: Dict[str, Any]) -> None:
        """Handle scan completion."""
        self.is_scanning = False
        self.scan_results = results
        self._update_scan_buttons(scanning=False)

        # Update progress to 100%
        total = results.get("total_folders", 0)
        if total > 0:
            progress_bar = self.query_one("#progress-bar", ProgressBar)
            progress_bar.progress = total

        # Update status and results
        self._update_status("Scan completed!")
        self._show_results(results)
        self._log_success("Scan completed successfully!")

        # Clear current folder display
        current_folder_label = self.query_one("#current-folder", Label)
        current_folder_label.update("")

    def _scan_error(self, error: str) -> None:
        """Handle scan error."""
        self.is_scanning = False
        self._update_scan_buttons(scanning=False)
        self._update_status(f"Scan failed: {error}")
        self._log_error(f"Scan failed: {error}")

        # Clear current folder display
        current_folder_label = self.query_one("#current-folder", Label)
        current_folder_label.update("")

    def _show_results(self, results: Dict[str, Any]) -> None:
        """Display scan results."""
        total = results.get("total_folders", 0)
        processed = results.get("processed", 0)
        skipped = results.get("skipped", 0)
        errors = results.get("errors", 0)
        found = results.get("found_metadata", 0)

        summary = (
            f"Processed: {processed}/{total} folders\n"
            f"Found metadata: {found}\n"
            f"Skipped: {skipped}\n"
            f"Errors: {errors}"
        )

        results_label = self.query_one("#results-summary", Label)
        results_label.update(summary)

        # Show results section
        results_section = self.query_one("#results-section")
        results_section.display = True

    def _update_scan_buttons(self, scanning: bool) -> None:
        """Update scan button states."""
        start_button = self.query_one("#start-scan", Button)
        stop_button = self.query_one("#stop-scan", Button)
        back_button = self.query_one("#back", Button)

        start_button.disabled = scanning
        stop_button.disabled = not scanning
        back_button.disabled = scanning

    def _update_status(self, message: str) -> None:
        """Update status message."""
        status_label = self.query_one("#status-label", Label)
        status_label.update(message)

    def _clear_log(self) -> None:
        """Clear the log display."""
        self.log_widget.clear()

    def _log_info(self, message: str) -> None:
        """Log an info message."""
        self.log_widget.write(f"INFO: {message}")

    def _log_success(self, message: str) -> None:
        """Log a success message."""
        self.log_widget.write(f"SUCCESS: {message}")

    def _log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.log_widget.write(f"WARNING: {message}")

    def _log_error(self, message: str) -> None:
        """Log an error message."""
        self.log_widget.write(f"ERROR: {message}")

    # Action methods for bindings
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_add_path(self) -> None:
        """Go to add path screen."""
        from .add_path import AddPathScreen

        add_path_screen = AddPathScreen()
        self.app.push_screen(add_path_screen)

    def action_delete_path(self) -> None:
        """Go back to main screen to delete paths."""
        self.app.pop_screen()

    def action_scan(self) -> None:
        """Already on scan screen."""
        pass

    def action_refresh(self) -> None:
        """Refresh the current screen."""
        self.refresh()

    def action_clear_cache(self) -> None:
        """Clear the cache."""
        if hasattr(self.app, "cache_manager"):
            self.app.cache_manager.clear()
            self._log_info("Cache cleared")

    def action_validate_paths(self) -> None:
        """Validate configured paths."""
        if hasattr(self.app, "path_manager"):
            paths = self.app.path_manager.get_paths()
            valid_paths = []
            invalid_paths = []

            for path in paths:
                if Path(path).exists() and Path(path).is_dir():
                    valid_paths.append(path)
                else:
                    invalid_paths.append(path)

            if invalid_paths:
                self._log_warning(f"Found {len(invalid_paths)} invalid paths")
            else:
                self._log_info(f"All {len(valid_paths)} paths are valid")

    def action_show_cache_info(self) -> None:
        """Show cache information."""
        if hasattr(self.app, "cache_manager"):
            info = self.app.cache_manager.get_cache_info()
            self._log_info(
                f"Cache: {info['total_entries']} entries, {info['size_mb']:.1f} MB"
            )

    def action_export_cache(self) -> None:
        """Export cache information."""
        if hasattr(self.app, "cache_manager"):
            try:
                export_path = self.app.cache_manager.export_cache_info()
                self._log_info(f"Cache exported to: {export_path}")
            except Exception as e:
                self._log_error(f"Export failed: {e}")

    def action_retry_failed(self) -> None:
        """Retry failed cache entries."""
        if hasattr(self.app, "cache_manager"):
            try:
                retried = self.app.cache_manager.retry_failed_entries()
                self._log_info(f"Retried {retried} failed entries")
            except Exception as e:
                self._log_error(f"Retry failed: {e}")
