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

   