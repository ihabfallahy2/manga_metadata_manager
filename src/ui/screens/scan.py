"""
Screen for scanning manga directories and fetching metadata.
"""

import asyncio
from typing import Dict, Any
from textual.app import ComposeResult
from textual.widgets import Button, Label, ProgressBar, RichLog
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.worker import work_thread

from core.scanner import DirectoryScanner


class ScanScreen(Screen):
    """Screen for scanning manga directories."""
    
    def __init__(self, scanner: DirectoryScanner, paths: list[str]):
        super().__init__()
        self.scanner = scanner
        self.paths = paths
        self.is_scanning = False
        self.scan_results: Dict[str, Any] = {}
    
    def compose(self) -> ComposeResult:
        """Compose the scan screen layout."""
        with Vertical(id="scan-container"):
            yield Label("Scanning Manga Directories", id="scan-title")
            
            # Progress section
            with Vertical(id="progress-section"):
                yield Label("Preparing scan...", id="status-label")
                yield ProgressBar(total=100, show_eta=True, id="progress-bar")
                yield Label("0 / 0 folders processed", id="progress-text")
            
            # Log section
            with Vertical(id="log-section"):
                yield Label("Scan Log:", id="log-title")
                self.log_widget = Log(id="scan-log", auto_scroll=True)
                yield self.log_widget
            
            # Control buttons
            with Horizontal(id="control-buttons"):
                yield Button("Start Scan", variant="primary", id="start-scan")
                yield Button("Stop Scan", variant="default", id="stop-scan", disabled=True)
                yield Button("Clear Log", variant="default", id="clear-log")
                yield Button("Back", variant="default", id="back")
            
            # Results section (initially hidden)
            with Vertical(id="results-section"):
                yield Label("Scan Results:", id="results-title")
                yield Label("", id="results-summary")
    
    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self._update_status("Ready to scan")
        self._log_info(f"Configured to scan {len(self.paths)} path(s):")
        for i, path in enumerate(self.paths, 1):
            self._log_info(f"  {i}. {path}")
    
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
        self._update_scan_buttons(scanning=True)
        self._update_status("Starting scan...")
        self._clear_log()
        
        # Start scanning in background thread
        self.run_worker(self._scan_worker, exclusive=True)
    
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
    
    @work_thread
    def _scan_worker(self) -> None:
        """Worker thread for scanning directories."""
        try:
            # Perform the scan
            results = self.scanner.scan_paths(
                self.paths,
                progress_callback=self._progress_callback,
                log_callback=self._log_callback
            )
            
            # Update UI with results
            self.call_from_thread(self._scan_completed, results)
            
        except Exception as e:
            self.call_from_thread(self._scan_error, str(e))
    
    def _progress_callback(self, current: int, total: int, message: str) -> None:
        """Callback for progress updates."""
        if not self.is_scanning:
            return
        
        self.call_from_thread(self._update_progress, current, total, message)
    
    def _log_callback(self, level: str, message: str) -> None:
        """Callback for log messages."""
        self.call_from_thread(self._log_message, level, message)
    
    def _update_progress(self, current: int, total: int, message: str) -> None:
        """Update progress display."""
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_text = self.query_one("#progress-text", Label)
        
        progress_bar.total = total
        progress_bar.progress = current
        
        progress_text.update(f"{current} / {total} folders processed")
        self._update_status(message)
    
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
        
        # Update status and results
        self._update_status("Scan completed!")
        self._show_results(results)
        self._log_success("Scan completed successfully!")
    
    def _scan_error(self, error: str) -> None:
        """Handle scan error."""
        self.is_scanning = False
        self._update_scan_buttons(scanning=False)
        self._update_status(f"Scan failed: {error}")
        self._log_error(f"Scan failed: {error}")
    
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
        self.log_widget.write(f"[cyan]INFO[/]: {message}")
    
    def _log_success(self, message: str) -> None:
        """Log a success message."""
        self.log_widget.write(f"[green]SUCCESS[/]: {message}")
    
    def _log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.log_widget.write(f"[yellow]WARNING[/]: {message}")
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        self.log_widget.write(f"[red]ERROR[/]: {message}")