# Utils file for shared utilities
# This file contains the ToolTip class for hover tooltips.

import tkinter as tk  # Core Tkinter
from tkinter import ttk  # Themed widgets


class ToolTip:
    """Class for creating hover tooltips."""

    def __init__(self, widget, text):
        """Initialize tooltip."""
        self.widget = widget  # Widget reference
        self.text = text  # Tooltip text
        self.tip = None  # Toplevel reference
        widget.bind("<Enter>", self.show)  # Bind enter
        widget.bind("<Leave>", self.hide)  # Bind leave

    def show(self, _e=None):
        """Show tooltip."""
        if self.tip is not None:
            return  # Already shown
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)  # Get position
        x += self.widget.winfo_rootx() + 20  # Adjust x
        y += self.widget.winfo_rooty() + 20  # Adjust y
        self.tip = tk.Toplevel(self.widget)  # Create toplevel
        self.tip.wm_overrideredirect(True)  # No window decorations
        self.tip.wm_geometry(f"+{x}+{y}")  # Set position
        lbl = ttk.Label(self.tip, text=self.text, relief="solid", borderwidth=1, padding=4)  # Label
        lbl.pack()  # Pack label

    def hide(self, _e=None):
        """Hide tooltip."""
        if self.tip is not None:
            self.tip.destroy()  # Destroy toplevel
            self.tip = None  # Reset reference