"""
Screen for adding new manga paths.
"""

import os
from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import Button, Input, Label, ListView, ListItem, Footer
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from ...core.scanner import DirectoryScanner
from .scan import ScanScreen

try:
    import tkinter as tk
    from tkinter import filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class DirectoryBrowserScreen(Screen):
    """Screen for browsing directories natively in Textual."""
    
    def __init__(self, initial_path: str = None):
        super().__init__()
        self.current_path = Path(initial_path or Path.cwd())
        self.selected_path = None
    
    def compose(self) -> ComposeResult:
        """Compose the directory browser screen."""
        with Vertical(id="browser-container"):
            yield Label("Select Directory", id="browser-title")
            yield Label(f"Current: {self.current_path}", id="current-path")
            
            # Directory list
            self.dir_list = ListView(id="dir-list")
            yield self.dir_list
            
            # Navigation buttons
            with Horizontal(id="nav-buttons"):
                yield Button("Go Up", variant="default", id="go-up")
                yield Button("Select Current", variant="primary", id="select-current")
                yield Button("Cancel", variant="default", id="cancel")
    
    def on_mount(self) -> None:
        """Initialize the browser when mounted."""
        self._load_directory_contents()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "go-up":
            self._go_up()
        elif event.button.id == "select-current":
            self._select_current()
        elif event.button.id == "cancel":
            self.app.pop_screen()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle directory selection."""
        if event.index is not None:
            self._navigate_to_directory(event.index)
    
    def _load_directory_contents(self) -> None:
        """Load and display directory contents."""
        self.dir_list.clear()
        
        try:
            # Add parent directory option
            if self.current_path.parent != self.current_path:
                self.dir_list.append(ListItem(Label("📁 .. (Parent Directory)")))
            
            # List directories in current path
            for item in sorted(self.current_path.iterdir()):
                if item.is_dir():
                    # Try to get a readable name
                    try:
                        display_name = item.name
                    except (OSError, UnicodeDecodeError):
                        display_name = str(item)
                    
                    self.dir_list.append(ListItem(Label(f"📁 {display_name}")))
            
            # Update current path display
            current_path_label = self.query_one("#current-path", Label)
            current_path_label.update(f"Current: {self.current_path}")
            
        except PermissionError:
            self.dir_list.append(ListItem(Label("❌ Permission denied")))
        except Exception as e:
            self.dir_list.append(ListItem(Label(f"❌ Error: {e}")))
    
    def _go_up(self) -> None:
        """Navigate to parent directory."""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self._load_directory_contents()
    
    def _navigate_to_directory(self, index: int) -> None:
        """Navigate to selected directory."""
        try:
            # Skip parent directory option
            if self.current_path.parent != self.current_path:
                index -= 1
            
            if index >= 0:
                dirs = [item for item in self.current_path.iterdir() if item.is_dir()]
                if 0 <= index < len(dirs):
                    self.current_path = dirs[index]
                    self._load_directory_contents()
        except Exception as e:
            # Handle navigation errors
            pass
    
    def _select_current(self) -> None:
        """Select the current directory."""
        self.selected_path = str(self.current_path)
        self.app.pop_screen()


class AddPathScreen(Screen):
    """Screen for adding new manga collection paths."""
    
    DEFAULT_HELP = "Enter the full path to your manga collection directory"
    
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
    
    def compose(self) -> ComposeResult:
        """Compose the add path screen layout."""
        with Vertical(id="add-path-container"):
            yield Label("Add New Manga Path", id="title")
            yield Label(self.DEFAULT_HELP, id="help-text")
            
            self.path_input = Input(
                placeholder="C:\\manga or /home/user/manga",
                id="path-input"
            )
            yield self.path_input
            
            # Show current directory as suggestion
            current_dir = str(Path.cwd())
            yield Label(f"Current directory: {current_dir}", id="current-dir")
            
            with Horizontal(id="button-container"):
                yield Button("Add Path", variant="primary", id="add")
                yield Button("Browse", variant="default", id="browse")
                yield Button("Cancel", variant="default", id="cancel")
            
            # Status message area (hidden by default)
            self.status_label = Label("", id="status-message")
            self.status_label.display = False
            yield self.status_label
        
        # Create a custom footer with all bindings visible
        with Horizontal(id="custom-footer"):
            yield Label("q: Quit", classes="footer-item")
            yield Label("a: Add Path", classes="footer-item")
            yield Label("d: Delete Path", classes="footer-item")
            yield Label("s: Scan", classes="footer-item")
            yield Label("r: Refresh", classes="footer-item")
            yield Label("c: Clear Cache", classes="footer-item")
            yield Label("v: Validate Paths", classes="footer-item")
            yield Label("i: Cache Info", classes="footer-item")
            yield Label("x: Export Cache", classes="footer-item")
            yield Label("t: Retry Failed", classes="footer-item")
            yield Label("p: Palette", classes="footer-item")
    
    def on_mount(self) -> None:
        """Set focus to input when screen mounts."""
        self.path_input.focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id == "path-input":
            self._handle_add_path()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add":
            self._handle_add_path()
        elif event.button.id == "browse":
            self._handle_browse()
        elif event.button.id == "cancel":
            self.app.pop_screen()
    
    def on_screen_resume(self) -> None:
        """Called when returning from another screen."""
        # Check if we're returning from directory browser
        if hasattr(self, 'browser_result'):
            if self.browser_result:
                self.path_input.value = self.browser_result
                self._show_status(f"Selected: {self.browser_result}", "success")
            delattr(self, 'browser_result')
    
    def _handle_add_path(self) -> None:
        """Handle adding a new path."""
        raw_path = self.path_input.value.strip()
        
        if not raw_path:
            self._show_status("Please enter a path", "error")
            return
        
        # Expand user directory and resolve path
        expanded_path = os.path.expanduser(raw_path)
        try:
            resolved_path = str(Path(expanded_path).resolve())
        except Exception:
            self._show_status("Invalid path format", "error")
            return
        
        # Validate path exists
        if not Path(resolved_path).exists():
            self._show_status("Path does not exist", "error")
            return
        
        # Validate it's a directory
        if not Path(resolved_path).is_dir():
            self._show_status("Path is not a directory", "error")
            return
        
        # Check if path already exists in the app
        app = self.app
        if hasattr(app, 'path_manager') and resolved_path in app.path_manager.get_paths():
            self._show_status("Path already added", "warning")
            return
        
        # Add the path
        try:
            if hasattr(app, 'path_manager'):
                app.path_manager.add_path(resolved_path)
                app.refresh_path_list()
                self._show_status(f"Added: {resolved_path}", "success")
                # Close screen after successful addition
                self.call_after_refresh(self._close_after_delay)
            else:
                # Fallback for old interface
                if resolved_path not in app.paths:
                    app.paths.append(resolved_path)
                    app.save_paths()
                    app.refresh_list()
                self.app.pop_screen()
        except Exception as e:
            self._show_status(f"Error adding path: {e}", "error")
    
    def _handle_browse(self) -> None:
        """Handle browse button - use native Textual browser."""
        try:
            # Use native directory browser
            browser_screen = DirectoryBrowserScreen()
            self.app.push_screen(browser_screen)
            
            # Store reference to get result later
            self.browser_result = None
            
            # Set up callback for when browser closes
            def on_browser_close():
                if hasattr(browser_screen, 'selected_path'):
                    self.browser_result = browser_screen.selected_path
            
            # This is a simplified approach - in practice, you'd use a more robust method
            # For now, we'll rely on the screen resume method
            
        except Exception as e:
            self._show_status(f"Error opening directory browser: {e}", "error")
    
    def _show_status(self, message: str, level: str = "info") -> None:
        """
        Show status message to user.
        
        Args:
            message: Message to show
            level: Message level (info, warning, error, success)
        """
        if message:
            # Show the status area and update with message
            self.status_label.display = True
            
            # Apply styling based on level
            if level == "error":
                self.status_label.update(f"❌ {message}")
            elif level == "warning":
                self.status_label.update(f"⚠️  {message}")
            elif level == "success":
                self.status_label.update(f"✅ {message}")
            else:
                self.status_label.update(f"ℹ️  {message}")
            
            # Hide after a delay
            self.set_timer(3, self._hide_status)
        else:
            self._hide_status()
    
    def _hide_status(self) -> None:
        """Hide the status message area."""
        self.status_label.display = False
        self.status_label.update("")
    
    def _close_after_delay(self) -> None:
        """Close the screen after a short delay."""
        self.set_timer(1.5, self.app.pop_screen)
    
    def _validate_manga_directory(self, path: Path) -> tuple[bool, str]:
        """
        Validate if a directory looks like a manga collection.
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not path.exists():
            return False, "Directory does not exist"
        
        if not path.is_dir():
            return False, "Path is not a directory"
        
        try:
            # Check if directory is readable
            list(path.iterdir())
        except PermissionError:
            return False, "Permission denied to read directory"
        except Exception as e:
            return False, f"Cannot access directory: {e}"
        
        # Count subdirectories (potential manga folders)
        try:
            subdirs = [item for item in path.iterdir() if item.is_dir()]
            if len(subdirs) == 0:
                return True, f"Empty directory (0 subdirectories)"
            else:
                return True, f"Found {len(subdirs)} subdirectories"
        except Exception:
            return True, "Directory accessible"
    
    # Action methods for bindings
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def action_add_path(self) -> None:
        """Go to add path screen (already here)."""
        pass
    
    def action_delete_path(self) -> None:
        """Go back to main screen to delete paths."""
        self.app.pop_screen()
    
    def action_scan(self) -> None:
        """Go to scan screen."""
        if hasattr(self.app, 'path_manager') and self.app.path_manager.get_paths():
            scanner = DirectoryScanner()
            scan_screen = ScanScreen(scanner, self.app.path_manager.get_paths())
            self.app.push_screen(scan_screen)
        else:
            self._show_status("No paths configured for scanning", "warning")
    
    def action_refresh(self) -> None:
        """Refresh the current screen."""
        self.refresh()
    
    def action_clear_cache(self) -> None:
        """Clear the cache."""
        if hasattr(self.app, 'cache_manager'):
            self.app.cache_manager.clear()
            self._show_status("Cache cleared", "success")
    
    def action_validate_paths(self) -> None:
        """Validate configured paths."""
        if hasattr(self.app, 'path_manager'):
            paths = self.app.path_manager.get_paths()
            valid_paths = []
            invalid_paths = []
            
            for path in paths:
                if Path(path).exists() and Path(path).is_dir():
                    valid_paths.append(path)
                else:
                    invalid_paths.append(path)
            
            if invalid_paths:
                self._show_status(f"Found {len(invalid_paths)} invalid paths", "warning")
            else:
                self._show_status(f"All {len(valid_paths)} paths are valid", "success")
    
    def action_show_cache_info(self) -> None:
        """Show cache information."""
        if hasattr(self.app, 'cache_manager'):
            info = self.app.cache_manager.get_cache_info()
            self._show_status(f"Cache: {info['total_entries']} entries, {info['size_mb']:.1f} MB", "info")
    
    def action_export_cache(self) -> None:
        """Export cache information."""
        if hasattr(self.app, 'cache_manager'):
            try:
                export_path = self.app.cache_manager.export_cache_info()
                self._show_status(f"Cache exported to: {export_path}", "success")
            except Exception as e:
                self._show_status(f"Export failed: {e}", "error")
    
    def action_retry_failed(self) -> None:
        """Retry failed cache entries."""
        if hasattr(self.app, 'cache_manager'):
            try:
                retried = self.app.cache_manager.retry_failed_entries()
                self._show_status(f"Retried {retried} failed entries", "success")
            except Exception as e:
                self._show_status(f"Retry failed: {e}", "error")