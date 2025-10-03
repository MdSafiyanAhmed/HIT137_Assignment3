# Main application file for Tkinter AI GUI
# This file handles the main window, navigation, status bar, logging, and cache management.
# It integrates views and controllers for the app's functionality.

import os  # For file system operations like path handling and cache size calculation
import shutil  # For removing directories and files during cache clear
import tkinter as tk  # Core Tkinter library for GUI elements
from tkinter import ttk, filedialog  # ttk for themed widgets, filedialog for file selection
from app.views.home_view import HomeView  # Import the home view class
from app.controllers.model_controller import ModelController  # Import the model controller
from app.utils import ToolTip  # Import shared ToolTip utility


class MainApp(tk.Tk):
    """Main application class inheriting from tk.Tk, managing the entire GUI."""

    def __init__(self):
        """Initialize the main window and its components."""
        super().__init__()
        self.title("Tkinter AI GUI")  # Set window title
        self.geometry("1000x700")  # Set initial window size
        self.minsize(900, 600)  # Set minimum window size
        self.center_window()  # Center the window on the screen

        self.ttk_style = ttk.Style(self)  # Create ttk style object
        
        
        primary = "#2C7BE5"  # Primary accent color
        secondary = "#21C197"  # Secondary accent color
        self.ttk_style.configure("Accent.TButton", foreground="#ffffff", background=primary)  # Style for accent buttons
        self.ttk_style.map("Accent.TButton", background=[("active", primary)])  # Map active state for accent buttons
        self.ttk_style.configure("Nav.TButton", padding=6)  # Style for navigation buttons
        # Active navigation: blue font color (uses same primary color)
        self.ttk_style.configure("ActiveNav.TButton", foreground=primary, padding=6)
        self.ttk_style.map("ActiveNav.TButton", foreground=[("active", primary)])
        self.active_nav = "home"  # Track active navigation tab

        # Application state variables
        self.last_error = None  # Store last error message
        self.logs = []  # List to store log messages
        # Shared history items stored on the app so views can persist history across navigation
        self.history_items = []
        self.cache_path = os.environ.get("HF_HOME", os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))  # Hugging Face cache path

        # Configure grid for main layout
        self.rowconfigure(2, weight=1)  # Container row expands
        self.columnconfigure(0, weight=1)  # Column expands

        # Header frame
        self.header = ttk.Frame(self)  # Create header frame
        self.header.grid(row=0, column=0, sticky="ew")  # Grid at top
        title = ttk.Label(self.header, text="Tkinter AI GUI", font=("Segoe UI", 16, "bold"))  # Title label
        title.pack(expand=True, pady=10)  # Pack title centered

        # Navigation bar
        self.nav = ttk.Frame(self)  # Create navigation frame
        self.nav.grid(row=1, column=0, sticky="ew")  # Grid below header
        self.home_btn = ttk.Button(self.nav, text="🏠 Home", style="Nav.TButton", command=lambda: self.switch_nav("home"))  # Home button
        self.model_btn = ttk.Button(self.nav, text="📚 Models", style="Nav.TButton", command=lambda: self.switch_nav("model"))  # Models button
        self.help_btn = ttk.Button(self.nav, text="❓ Help", style="Nav.TButton", command=lambda: self.switch_nav("help"))  # Help button
        self.settings_btn = ttk.Button(self.nav, text="⚙ Settings", style="Nav.TButton", command=lambda: self.switch_nav("settings"))  # Settings button
        for b in (self.home_btn, self.model_btn, self.help_btn, self.settings_btn):
            b.pack(side="left", padx=6, pady=4)  # Pack all navigation buttons left-aligned

        # Main content container
        self.container = ttk.Frame(self)  # Create main content frame
        self.container.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)  # Grid in middle, expands

        # Status bar container (fixed at bottom)
        self.status_container = ttk.Frame(self)  # Frame for status bar and log panel
        self.status_container.grid(row=3, column=0, sticky="ew")  # Grid at bottom
        self.status_bar = ttk.Frame(self.status_container)  # Status bar frame
        self.status_bar.pack(fill="x")  # Pack to fill horizontally
        self.status_label = ttk.Label(self.status_bar, text="Ready")  # Status label
        self.status_label.pack(side="left", padx=8, pady=4)  # Pack left
        ToolTip(self.status_label, "Click to expand log")  # Add tooltip to status label
        self.status_prog = ttk.Progressbar(self.status_bar, mode="determinate", length=240)  # Progress bar
        self.status_prog.pack(side="left", padx=8)  # Pack left
        self.cache_label = ttk.Label(self.status_bar, text=self._cache_badge_text())  # Cache size label
        self.cache_label.pack(side="right", padx=8)  # Pack right
        self.clear_cache_btn = ttk.Button(self.status_bar, text="Clear cache", command=self.clear_cache)  # Clear cache button
        self.clear_cache_btn.pack(side="right", padx=8)  # Pack right

        # Collapsible log panel
        self.log_panel = ttk.Frame(self.status_container)  # Log panel frame
        self.log_text = tk.Text(self.log_panel, height=6, wrap="none")  # Text widget for logs
        self.log_text.pack(fill="both", expand=True, padx=8, pady=4)  # Pack to fill
        self.log_controls = ttk.Frame(self.log_panel)  # Controls for log panel
        self.log_controls.pack(fill="x", padx=8, pady=(0, 6))  # Pack to fill horizontally
        ttk.Button(self.log_controls, text="Clear logs", command=self.clear_logs).pack(side="right")  # Clear logs button
        self.log_visible = False  # Track if log panel is visible
        self.status_bar.bind("<Button-1>", self.toggle_log_panel)  # Bind click to toggle log panel

        # Model controller instance
        self.model_controller = ModelController()  # Initialize model controller
        self._current_view = None  # Track current view
        self.switch_nav("home")  # Switch to home view initially

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()  # Update window dimensions
        w = self.winfo_width() or 1000  # Get width or default
        h = self.winfo_height() or 700  # Get height or default
        x = (self.winfo_screenwidth() // 2) - (w // 2)  # Calculate x position
        y = (self.winfo_screenheight() // 2) - (h // 2)  # Calculate y position
        self.geometry(f"{w}x{h}+{x}+{y}")  # Set geometry

    def switch_nav(self, target: str):
        """Switch navigation tab and show corresponding view."""
        self.active_nav = target  # Update active navigation
        self._apply_nav_styles()  # Apply styles to navigation buttons
        if target == "home":
            self.show_home()  # Show home view
        elif target == "model":
            self.show_model()  # Show model info view
        elif target == "help":
            self.show_help()  # Show help view
        elif target == "settings":
            self.show_settings()  # Show settings view

    def _apply_nav_styles(self):
        """Apply styles to navigation buttons based on active tab."""
        mapping = {
            "home": self.home_btn,
            "model": self.model_btn,
            "help": self.help_btn,
            "settings": self.settings_btn,
        }
        for key, btn in mapping.items():
            if key == self.active_nav:
                btn.configure(style="ActiveNav.TButton")  # Active: blue font color
            else:
                btn.configure(style="Nav.TButton")  # Normal style for inactive

    def show_home(self):
        """Show the home view."""
        self._clear_container()  # Clear current content
        self._current_view = HomeView(self.container, self.model_controller, app=self)  # Create home view
        self._current_view.pack(fill="both", expand=True)  # Pack view

    def show_model(self):
        """Show the model information view."""
        self._clear_container()  # Clear current content
        frm = ttk.Frame(self.container, padding=12)  # Create frame
        frm.pack(fill="both", expand=True)  # Pack frame
        ttk.Label(frm, text="Model Information", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))  # Label
        text = tk.Text(frm, height=20, wrap="word")  # Text widget for model info
        text.pack(fill="both", expand=True)  # Pack text
        try:
            with open("app/model_info.md", "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())  # Insert model info from file
        except Exception as e:
            text.insert("1.0", f"Could not load model info: {e}")  # Error message if file not found
        text.configure(state="disabled")  # Make text read-only
        ttk.Button(frm, text="More Details", command=lambda: self._show_model_details(frm)).pack(anchor="w", pady=6)  # More details button
        self._current_view = frm  # Set current view

    def _show_model_details(self, parent):
        """Show additional model details in a frame."""
        details_frame = ttk.Frame(parent)  # Create details frame
        details_frame.pack(fill="both", expand=True, pady=6)  # Pack frame
        text = tk.Text(details_frame, height=10, wrap="word")  # Text widget
        text.pack(fill="both", expand=True)  # Pack text
        text.insert("1.0", (
            "Example Input/Output:\n"
            "Image to Text: Input: beach.jpg → Output: 'A sunny beach with waves.'\n"
            "Sentiment: Input: 'I love this!' → Output: POSITIVE (0.95)\n\n"
            "Limitations:\n"
            "- Image model may struggle with complex scenes.\n"
            "- Sentiment model limited to short texts, may miss sarcasm."
        ))  # Insert example details
        text.configure(state="disabled")  # Make read-only

    def show_help(self):
        """Show the help view."""
        self._clear_container()  # Clear current content
        frm = ttk.Frame(self.container, padding=12)  # Create frame
        frm.pack(fill="both", expand=True)  # Pack frame
        ttk.Label(frm, text="Help", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))  # Label
        text = tk.Text(frm, height=22, wrap="word")  # Text widget for help content
        text.pack(fill="both", expand=True)  # Pack text
        try:
            with open("app/help.md", "r", encoding="utf-8") as f:
                text.delete("1.0", "end")  # Clear text
                text.insert("1.0", f.read())  # Insert help from file
        except Exception:
            msg = (
                "If an error occurs during testing an input, it will appear here.\n"
                "Check your internet connection, requirements, or contact support."
            )
            text.insert("1.0", msg)  # Default message if file not found
        if self.last_error:
            text.insert("end", f"\n\nLast error:\n{self.last_error}")  # Append last error
        text.configure(state="disabled")  # Make read-only
        text.bind("<Button-1>", lambda e: text.focus_set())  # Make focusable for accessibility
        self._help_text = text  # Store reference
        self._current_view = frm  # Set current view

    def show_settings(self):
        """Show the settings view."""
        self._clear_container()  # Clear current content
        frm = ttk.Frame(self.container, padding=12)  # Create frame
        frm.pack(fill="both", expand=True)  # Pack frame
        ttk.Label(frm, text="Settings", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))  # Label
        cache_row = ttk.Frame(frm)  # Row for cache setting
        cache_row.pack(fill="x", pady=6)  # Pack row
        ttk.Label(cache_row, text="HF Cache folder:").pack(side="left")  # Label
        self.cache_entry = ttk.Entry(cache_row, width=60)  # Entry for cache path
        self.cache_entry.insert(0, self.cache_path)  # Insert current path
        self.cache_entry.pack(side="left", padx=8)  # Pack entry
        ttk.Button(cache_row, text="Change", command=self.choose_cache_dir).pack(side="left")  # Change button
        btn_row = ttk.Frame(frm)  # Row for save/cancel
        btn_row.pack(fill="x", pady=12)  # Pack row
        original_cache = self.cache_path  # Remember original in case of cancel

        def _show_saved_msg():
            self.set_status("Saved successfully", running=False)
            self.after(2000, lambda: self.set_status("Ready"))

        def _save_action():
            new_path = self.cache_entry.get().strip()
            if new_path:
                self.cache_path = new_path
                try:
                    self.save_settings()
                except Exception:
                    pass
                try:
                    self.cache_label.configure(text=self._cache_badge_text())
                except Exception:
                    pass
            _show_saved_msg()

        def _cancel_action():
            # Revert entry to previous path and keep previous cache_path unchanged
            self.cache_entry.delete(0, "end")
            self.cache_entry.insert(0, original_cache)
            self.set_status("Ready", running=False)

        ttk.Button(btn_row, text="Save", command=_save_action).pack(side="left")  # Save button
        ttk.Button(btn_row, text="Cancel", command=_cancel_action).pack(side="left", padx=8)  # Cancel button
        self._current_view = frm  # Set current view

    def switch_nav_to_current(self):
        """Re-render the current navigation page."""
        self.switch_nav(self.active_nav)  # Switch to current active nav

    def set_status(self, text: str, running: bool = False):
        """Set status bar text and progress mode."""
        self.status_label.configure(text=text, foreground=("#F87171" if text.startswith("Error") else ""))  # Set text and color
        if running:
            self.status_prog.configure(mode="indeterminate")  # Indeterminate mode for running
            self.status_prog.start(10)  # Start animation
        else:
            self.status_prog.stop()  # Stop animation
            self.status_prog.configure(mode="determinate", value=0)  # Reset to determinate

    def log(self, message: str):
        """Log a message to the logs list and update panel if visible."""
        ts = self._now()  # Get current time
        line = f"[{ts}] {message}"  # Format log line
        self.logs.append(line)  # Append to logs
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]  # Limit to 1000 logs
        if self.log_visible:
            try:
                self.log_text.configure(state="normal")  # Enable editing
                self.log_text.insert("end", line + "\n")  # Insert log
                self.log_text.see("end")  # Scroll to end
                self.log_text.configure(state="disabled")  # Disable editing
            except Exception:
                pass  # Ignore errors

    def clear_logs(self):
        """Clear the logs list and text widget."""
        self.logs.clear()  # Clear list
        try:
            self.log_text.configure(state="normal")  # Enable editing
            self.log_text.delete("1.0", "end")  # Delete content
            self.log_text.configure(state="disabled")  # Disable editing
        except Exception:
            pass  # Ignore errors

    def toggle_log_panel(self, _e=None):
        """Toggle visibility of the log panel."""
        self.log_visible = not self.log_visible  # Toggle visibility flag
        if self.log_visible:
            self.log_panel.pack(fill="x")  # Pack log panel
            try:
                self.log_text.configure(state="normal")  # Enable editing
                self.log_text.delete("1.0", "end")  # Clear
                self.log_text.insert("1.0", "\n".join(self.logs))  # Insert all logs
                self.log_text.configure(state="disabled")  # Disable editing
            except Exception:
                pass  # Ignore errors
        else:
            self.log_panel.pack_forget()  # Hide log panel

    def _cache_badge_text(self):
        """Get formatted cache size text."""
        size = self._folder_size(self.cache_path)  # Calculate size
        return f"Cache: {self._format_bytes(size)}"  # Format and return

    def _folder_size(self, path):
        """Calculate size of folder, targeting model cache."""
        total = 0  # Initialize total
        try:
            for root, _, files in os.walk(path):  # Walk directory
                for f in files:
                    if "hub" in root or "models" in root:  # Target specific dirs
                        fp = os.path.join(root, f)  # Full path
                        try:
                            total += os.path.getsize(fp)  # Add file size
                        except Exception:
                            pass  # Ignore errors
        except Exception:
            pass  # Ignore walk errors
        return total  # Return total size

    def _format_bytes(self, size):
        """Format bytes to human-readable string."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:  # Units loop
            if size < 1024.0:
                return f"{size:.1f} {unit}"  # Return formatted
            size /= 1024.0  # Divide for next unit
        return f"{size:.1f} PB"  # Fallback for large sizes

    def clear_cache(self):
        """Clear Hugging Face model cache."""
        try:
            if os.path.isdir(self.cache_path):  # Check if path exists
                for name in os.listdir(self.cache_path):  # List contents
                    p = os.path.join(self.cache_path, name)  # Full path
                    if "hub" in name or "models" in name:  # Target cache dirs
                        try:
                            if os.path.isdir(p):
                                shutil.rmtree(p, ignore_errors=True)  # Remove dir
                            else:
                                os.remove(p)  # Remove file
                        except Exception:
                            pass  # Ignore errors
            self.cache_label.configure(text=self._cache_badge_text())  # Update label
            self.log("Cache cleared")  # Log action
        except Exception as e:
            self.log(f"Cache clear error: {e}")  # Log error
            self.set_status(f"Error: {e}", running=False)  # Set status error

    def choose_cache_dir(self):
        """Choose a new cache directory using file dialog."""
        d = filedialog.askdirectory()  # Open directory dialog
        if d:
            self.cache_entry.delete(0, "end")  # Clear entry
            self.cache_entry.insert(0, d)  # Insert new path

    def save_settings(self):
        """Save settings, including new cache path."""
        new_cache = self.cache_entry.get().strip()  # Get new path
        if new_cache and os.path.isdir(new_cache):  # Check if valid
            os.environ["HF_HOME"] = new_cache  # Set environment variable
            self.cache_path = new_cache  # Update instance variable
            try:
                if os.name == "nt":  # Windows-specific
                    os.system(f'setx HF_HOME "{new_cache}" > NUL')  # Persist env var
            except Exception:
                pass  # Ignore errors
            self.cache_label.configure(text=self._cache_badge_text())  # Update label
            self.log(f"HF_HOME set to {new_cache}")  # Log change
        self.switch_nav("home")  # Switch back to home

    def _now(self):
        """Get current time string."""
        import time  # Import time module
        return time.strftime("%H:%M:%S")  # Format time

    def _clear_container(self):
        """Clear all children from the container frame."""
        for w in self.container.winfo_children():  # Loop children
            w.destroy()  # Destroy widget