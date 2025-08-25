"""
Screen for adding new manga paths.
"""

import os
from pathlib import Path
from textual.app import ComposeResult
from textual.widgets import Button, Input, Label
from textual.containers import Horizontal, Vertical
from textual.screen import Screen


class AddPathScreen(Screen):
    """Screen for adding new manga collection paths."""
    
    DEFAULT_HELP = "Enter the full path to your manga collection directory"
    
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
            
            yield Label("", id="status-message")
    
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
        """Handle browse button (placeholder for future file dialog)."""
        # For now, just show a helpful message
        # In the future, this could open a file dialog
        self._show_status("File browser not implemented yet. Please type path manually.", "info")
    
    def _show_status(self, message: str, level: str = "info") -> None:
        """
        Show status message to user.
        
        Args:
            message: Message to show
            level: Message level (info, warning, error, success)
        """
        status_label = self.query_one("#status-message", Label)
        
        # Apply styling based on level
        if level == "error":
            status_label.update(f"❌ {message}")
        elif level == "warning":
            status_label.update(f"⚠️  {message}")
        elif level == "success":
            status_label.update(f"✅ {message}")
        else:
            status_label.update(f"ℹ️  {message}")
    
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