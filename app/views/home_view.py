# Home view file for Tkinter AI GUI
# This file defines the home view with task selection, inputs, output display, and info panels.
# It handles user interactions for running models and displaying results.

import os  # For file validation and size checks
import tkinter as tk  # Core Tkinter library
from tkinter import filedialog  # For file selection dialog
from tkinter import ttk  # Themed widgets
from PIL import Image, ImageTk  # For image handling and display
import json  # For JSON handling in history
import time  # For timestamps
from app.utils import ToolTip  # Shared ToolTip utility


class HomeView(ttk.Frame):
    """Home view class for the main interface, handling task inputs and outputs."""

    def __init__(self, parent, controller, app=None):
        """Initialize the home view components."""
        super().__init__(parent, padding=12)  # Initialize frame with padding
        self.controller = controller  # Model controller reference
        self.app = app  # App reference for status and logging
        self.selected_file = None  # Selected image file path
        self.preview_image = None  # PIL image for preview
        self.placeholder_text = "Type or paste text here — up to 3000 characters"  # Placeholder for text input
        self.running = False  # Track if task is running
        # Use shared history on the app so it survives navigation
        if self.app and hasattr(self.app, "history_items"):
            self.history_items = self.app.history_items
        else:
            self.history_items = []
        self._build_ui()  # Build UI elements
        self.bind("<Configure>", self._on_resize)  # Bind resize event

    def _card(self, master):
        """Create a card-like frame."""
        frm = ttk.Frame(master, padding=12, relief="groove")  # Frame with padding and relief
        frm.columnconfigure(0, weight=1)  # Configure column weight
        return frm  # Return frame

    def _build_ui(self):
        """Build the UI layout with columns for controls, output, and info."""
        for c in range(3):
            self.columnconfigure(c, weight=(1 if c == 1 else 0))  # Set column weights, center expands
        self.rowconfigure(0, weight=1)  # Row expands

        # Left column: Controls
        self.left_wrap = ttk.Frame(self)  # Wrapper frame for left column
        self.left_wrap.grid(row=0, column=0, sticky="nswe")  # Grid placement
        self.left_wrap.rowconfigure(0, weight=1)  # Row weight
        left = self._card(self.left_wrap)  # Create card
        left.pack(fill="both", expand=True)  # Pack card

        # Task selection
        ttk.Label(left, text="Select Task").pack(anchor="w")  # Label
        self.task_var = tk.StringVar(value="Image to Text")  # Task variable
        self.task_menu = ttk.Combobox(left, textvariable=self.task_var, state="readonly", values=["Image to Text", "Sentiment Analysis"], width=28)  # Combobox for tasks
        self.task_menu.pack(fill="x", pady=(4, 8))  # Pack
        self.task_menu.bind("<<ComboboxSelected>>", lambda e: [self._toggle_inputs(), self._update_info_panel()])  # Bind selection change

        # Execution mode display
        exec_row = ttk.Frame(left)  # Row frame
        exec_row.pack(fill="x", pady=(0, 8))  # Pack
        ttk.Label(exec_row, text="Execution Mode:").pack(side="left")  # Label
        self.exec_mode_entry = ttk.Entry(exec_row, width=20)  # Entry for mode
        self.exec_mode_entry.insert(0, "Local")  # Insert default
        self.exec_mode_entry.configure(state="readonly")  # Read-only
        self.exec_mode_entry.pack(side="left", padx=6)  # Pack
        ToolTip(self.exec_mode_entry, "Local downloads model weights on first run.")  # Tooltip

        # Preview card for inputs
        self.preview_card = self._card(left)  # Create preview card
        self.preview_card.pack(fill="x")  # Pack
        self.image_input_frame = ttk.Frame(self.preview_card)  # Frame for image input
        self.text_input_frame = ttk.Frame(self.preview_card)  # Frame for text input

        # Image input controls
        img_row = ttk.Frame(self.image_input_frame)  # Row for buttons
        img_row.pack(fill="x")  # Pack
        choose_btn = ttk.Button(img_row, text="Choose Image", width=16, command=self.choose_file)  # Choose button
        choose_btn.pack(side="left")  # Pack
        sample_img_btn = ttk.Button(img_row, text="Use Sample", command=self.use_sample_image)  # Sample button
        sample_img_btn.pack(side="left", padx=6)  # Pack
        self.preview_box = ttk.Label(self.image_input_frame, text="320×240 preview", relief="solid", borderwidth=2, anchor="center")  # Preview label
        self.preview_box.pack(fill="x", pady=8)  # Pack
        self.preview_box.configure(width=42)  # Set width
        self.preview_box.bind("<Button-1>", self._open_full_image)  # Bind click to open full image
        ToolTip(self.preview_box, "PNG, JPG, JPEG, BMP — up to 25 MB")  # Tooltip

        # Text input controls
        ttk.Label(self.text_input_frame, text="Text Input").pack(anchor="w", pady=(8, 4))  # Label
        self.text_input = tk.Text(self.text_input_frame, height=7, wrap="word")  # Text widget
        self.text_input.pack(fill="x")  # Pack
        self._set_placeholder()  # Set placeholder
        self.text_input.bind("<FocusIn>", self._clear_placeholder)  # Bind focus in
        self.text_input.bind("<FocusOut>", self._restore_placeholder)  # Bind focus out
        self.text_input.bind("<KeyRelease>", self._enforce_char_limit)  # Bind key release for limit
        txt_row = ttk.Frame(self.text_input_frame)  # Row for buttons
        txt_row.pack(fill="x", pady=6)  # Pack
        ttk.Button(txt_row, text="Paste from Clipboard", command=self.paste_clipboard).pack(side="left")  # Paste button
        ttk.Button(txt_row, text="Use Sample Text", command=self.use_sample_text).pack(side="left", padx=6)  # Sample button

        # Language selector
        lang_row = ttk.Frame(self.text_input_frame)  # Row for language
        lang_row.pack(fill="x", pady=(0, 6))  # Pack
        ttk.Label(lang_row, text="Language:").pack(side="left")  # Label
        self.lang_var = tk.StringVar(value="Auto-detect")  # Language variable
        ttk.Combobox(lang_row, textvariable=self.lang_var, state="readonly", values=["Auto-detect", "English", "Spanish", "French", "German"], width=18).pack(side="left", padx=6)  # Combobox

        # Controls row
        ctrl_row = ttk.Frame(left)  # Row for run/clear
        ctrl_row.pack(fill="x", pady=8)  # Pack
        self.run_btn = ttk.Button(ctrl_row, text="Run", command=self.run_task, width=14)  # Run button
        self.run_btn.pack(side="left")  # Pack
        ttk.Button(ctrl_row, text="Clear", command=self.clear_inputs, width=10).pack(side="left", padx=8)  # Clear button
        self.save_history_var = tk.BooleanVar(value=True)  # History save var
        ttk.Checkbutton(ctrl_row, text="Save to history", variable=self.save_history_var).pack(side="left")  # Checkbox

        # History card (populated from app.history_items to persist across navigation)
        hist_card = self._card(left)  # Create history card
        hist_card.pack(fill="both", expand=True, pady=(8, 0))  # Pack
        ttk.Label(hist_card, text="History").pack(anchor="w", pady=(0, 4))  # Label
        self.history_list = tk.Listbox(hist_card, height=10)  # Listbox for history
        self.history_list.pack(fill="both", expand=True)  # Pack
        self.history_list.bind("<<ListboxSelect>>", self._open_history_item)  # Bind selection
        # Populate listbox from shared history
        try:
            self.history_list.delete(0, "end")
            for it in self.history_items:
                self.history_list.insert("end", f"{it.get('ts','')} — {it.get('task','')}")
        except Exception:
            pass

        # Center column: Output
        self.center_wrap = ttk.Frame(self)  # Wrapper for center
        self.center_wrap.grid(row=0, column=1, sticky="nswe", padx=12)  # Grid
        self.rowconfigure(0, weight=1)  # Row weight
        center = self._card(self.center_wrap)  # Create card
        center.pack(fill="both", expand=True)  # Pack
        center.columnconfigure(0, weight=1)  # Column weight
        center.rowconfigure(1, weight=1)  # Row weight for output
        ttk.Label(center, text="Model Output", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")  # Label
        self.output_frame = ttk.Frame(center)  # Output frame
        self.output_frame.grid(row=1, column=0, sticky="nswe")  # Grid
        out_row = ttk.Frame(center)  # Row for output buttons
        out_row.grid(row=2, column=0, sticky="w", pady=6)  # Grid
        ttk.Button(out_row, text="Copy Result", command=self.copy_result).pack(side="left")  # Copy button

        # Right column: Info panels
        self.right_wrap = ttk.Frame(self)  # Wrapper for right
        self.right_wrap.grid(row=0, column=2, sticky="nswe")  # Grid
        self.right_wrap.rowconfigure(1, weight=1)  # Row weight
        right_top = self._card(self.right_wrap)  # Model info card
        right_top.grid(row=0, column=0, sticky="nsew")  # Grid
        ttk.Label(right_top, text="Model Info", font=("Segoe UI", 11, "bold")).pack(anchor="w")  # Label
        self.model_panel = tk.Text(right_top, height=12, width=40, wrap="word")  # Text for model info
        self.model_panel.pack(fill="both", expand=False)  # Pack
        self.model_panel.configure(state="disabled")  # Read-only
        self.model_panel.bind("<Button-1>", lambda e: self.model_panel.focus_set())  # Focusable
        right_bottom = self._card(self.right_wrap)  # OOP card
        right_bottom.grid(row=1, column=0, sticky="nsew", pady=(8, 0))  # Grid
        ttk.Label(right_bottom, text="OOP concepts used", font=("Segoe UI", 11, "bold")).pack(anchor="w")  # Label
        self.info_panel = ttk.Treeview(right_bottom, show="tree", selectmode="browse")  # Treeview for OOP
        self.info_panel.pack(fill="both", expand=True)  # Pack
        ttk.Button(right_bottom, text="Copy Panels", command=self.copy_panels).pack(anchor="e", pady=(6, 0))  # Copy button

        self._toggle_inputs()  # Toggle inputs based on task
        self._update_info_panel()  # Update info panels

    def _on_resize(self, _event=None):
        """Handle window resize for responsive layout."""
        w = self.winfo_width() or 1000  # Get width
        compact = w < 900  # Check if compact mode
        if compact:
            self.rowconfigure(0, weight=0)  # No weight for left
            self.rowconfigure(1, weight=1)  # Weight for center (output)
            self.rowconfigure(2, weight=0)  # No weight for right to ensure output visibility
            self.left_wrap.grid_configure(row=0, column=0, padx=0, pady=(0, 8), sticky="nswe", columnspan=3)  # Stack left
            self.center_wrap.grid_configure(row=1, column=0, padx=0, pady=(0, 8), sticky="nswe", columnspan=3)  # Stack center
            self.right_wrap.grid_configure(row=2, column=0, padx=0, pady=(0, 0), sticky="nswe", columnspan=3)  # Stack right
        else:
            self.rowconfigure(0, weight=1)  # Weight for row 0
            self.rowconfigure(1, weight=0)  # No weight
            self.rowconfigure(2, weight=0)  # No weight
            self.left_wrap.grid_configure(row=0, column=0, padx=0, pady=0, sticky="nswe", columnspan=1)  # Side by side
            self.center_wrap.grid_configure(row=0, column=1, padx=12, pady=0, sticky="nswe", columnspan=1)  # Center
            self.right_wrap.grid_configure(row=0, column=2, padx=0, pady=0, sticky="nswe", columnspan=1)  # Right

    def _set_placeholder(self):
        """Set placeholder text in text input."""
        self.text_input.delete("1.0", "end")  # Clear
        self.text_input.insert("1.0", self.placeholder_text)  # Insert placeholder
        self.text_input.configure(fg="#888")  # Gray color

    def _clear_placeholder(self, _event=None):
        """Clear placeholder on focus."""
        if self.text_input.get("1.0", "end").strip() == self.placeholder_text:
            self.text_input.delete("1.0", "end")  # Clear
            self.text_input.configure(fg="#000")  # Black color

    def _restore_placeholder(self, _event=None):
        """Restore placeholder if empty on blur."""
        if not self.text_input.get("1.0", "end").strip():
            self._set_placeholder()  # Restore

    def _enforce_char_limit(self, _event=None):
        """Enforce 3000 character limit on text input."""
        text = self.text_input.get("1.0", "end").strip()  # Get text
        if len(text) > 3000:
            self.text_input.delete("1.0", "end")  # Clear
            self.text_input.insert("1.0", text[:3000])  # Insert truncated
            self.text_input.configure(fg="#000")  # Black color

    def _on_drag_enter(self, _event=None):
        """Handle drag enter event for preview box."""
        try:
            self.preview_box.configure(text="➕ Drop image", foreground="#2C7BE5", relief="raised")  # Change appearance
        except Exception:
            pass  # Ignore

    def _on_drag_leave(self, _event=None):
        """Handle drag leave event for preview box."""
        try:
            if not hasattr(self, "_preview_img"):
                self.preview_box.configure(text="320×240 preview", foreground="", relief="solid")  # Reset
            else:
                self.preview_box.configure(foreground="", relief="solid")  # Reset
        except Exception:
            pass  # Ignore

    def paste_clipboard(self):
        """Paste text from clipboard to input."""
        try:
            import pyperclip  # Import pyperclip
            txt = pyperclip.paste()  # Get clipboard
            if txt:
                self.text_input.delete("1.0", "end")  # Clear
                self.text_input.insert("1.0", txt[:3000])  # Insert truncated
                self.text_input.configure(fg="#000")  # Black color
        except Exception:
            pass  # Ignore

    def use_sample_image(self):
        """Use the project's sample image for preview (assets\sample.jpg). Falls back to a generated placeholder if not found."""
        sample_path = os.path.join(os.getcwd(), "assets", "sample.jpg")
        if os.path.exists(sample_path):
            try:
                pil = Image.open(sample_path)
                self.preview_image = pil
                self.selected_file = sample_path
                self._set_preview(pil)
                return
            except Exception:
                pass
        # Fallback placeholder if file not available or fails to open
        img = Image.new("RGB", (320, 240), color=(220, 230, 240))  # Create sample image
        self.preview_image = img  # Set preview
        self.selected_file = None  # Clear file
        self._set_preview(img)  # Set preview

    def use_sample_text(self):
        """Use sample text for input."""
        sample = "I absolutely love this product. It exceeded my expectations!"  # Sample text
        self.text_input.delete("1.0", "end")  # Clear
        self.text_input.insert("1.0", sample)  # Insert
        self.text_input.configure(fg="#000")  # Black color

    def _set_preview(self, pil_image):
        """Set image preview in box."""
        pil = pil_image.copy()  # Copy image
        pil.thumbnail((320, 240))  # Resize
        self._preview_img = ImageTk.PhotoImage(pil)  # Create PhotoImage
        self.preview_box.configure(image=self._preview_img, text="")  # Set image

    def _open_full_image(self, _event=None):
        """Open full image in toplevel window."""
        if not hasattr(self, "_preview_img") or not self.preview_image:
            return  # No image
        top = tk.Toplevel(self)  # Create toplevel
        top.title("Image Preview")  # Title
        top.geometry("800x600")  # Fixed size: width=800, height=600
        top.resizable(False, False)
        # Resize/crop to fixed size for zoom view
        try:
            pil = self.preview_image.copy()
            pil = pil.resize((800, 600), Image.LANCZOS)
            full_img = ImageTk.PhotoImage(pil)
        except Exception:
            full_img = ImageTk.PhotoImage(self.preview_image)
        lbl = ttk.Label(top, image=full_img)  # Label with image
        lbl.image = full_img  # Keep reference
        lbl.pack(fill="both", expand=True)  # Pack and fill

    def _validate_image(self, path):
        """Validate image file format and size."""
        if not path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            self._handle_error("Invalid file format. Use PNG, JPG, JPEG, or BMP.")  # Error
            return False  # Invalid
        if os.path.getsize(path) > 25 * 1024 * 1024:
            self._handle_error("File too large. Maximum size is 25 MB.")  # Error
            return False  # Invalid
        return True  # Valid

    def clear_inputs(self):
        """Clear all inputs and outputs."""
        self.selected_file = None  # Clear file
        self.preview_image = None  # Clear preview
        self.preview_box.configure(image="", text="320×240 preview", relief="solid")  # Reset box
        self._set_placeholder()  # Reset text
        for w in self.output_frame.winfo_children():
            w.destroy()  # Clear output
        self.model_panel.configure(state="normal")  # Enable model panel
        self.model_panel.delete("1.0", "end")  # Clear
        self.model_panel.configure(state="disabled")  # Disable
        self.info_panel.delete(*self.info_panel.get_children())  # Clear info
        self._update_info_panel()  # Update panels
        self._reset_run_state()  # Reset run state

    def choose_file(self):
        """Choose image file using dialog."""
        f = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])  # Open dialog
        if f and self._validate_image(f):
            self.selected_file = f  # Set file
            try:
                pil = Image.open(f)  # Open image
                self.preview_image = pil  # Set preview
                self._set_preview(pil)  # Set preview
            except Exception:
                self._handle_error("Invalid image file")  # Error
                self.preview_box.configure(text=f)  # Show path

    def run_task(self):
        """Run the selected task / model."""
        # Disable task selector(s) while running and remember previous state(s)
        self._task_prev_state = {}
        for name in ("task_select", "task_cb", "task_menu", "task_option"):
            w = getattr(self, name, None)
            if w:
                try:
                    # remember previous state if available
                    self._task_prev_state[name] = w.cget("state")
                except Exception:
                    self._task_prev_state[name] = None
                try:
                    w.configure(state="disabled")
                except Exception:
                    try:
                        # fallback for some ttk widgets
                        w.state(["disabled"])
                    except Exception:
                        pass
        
        if self.running:
            return  # Already running
        
        # Add border effect on button click
        self._border_btn_effect()
        task_label = self.task_var.get()  # Get task
        task = "image" if task_label.lower().startswith("image") else "sentiment"  # Determine type
        for w in self.output_frame.winfo_children():
            w.destroy()  # Clear output
        self._update_info_panel()  # Update info
        loading_frame = ttk.Frame(self.output_frame)  # Loading frame
        loading_frame.pack(fill="both", expand=True)  # Pack
        ttk.Label(loading_frame, text="Processing...").pack(pady=10)  # Label
        prog = ttk.Progressbar(loading_frame, mode="indeterminate")  # Progress
        prog.pack(fill="x", padx=10)  # Pack
        prog.start(10)  # Start
        self.running = True  # Set running
        if self.app:
            self.app.set_status("Running…", running=True)  # Set status
        self.run_btn.configure(state="disabled", text="Running…")  # Disable button
        if task == "image":
            if not (self.selected_file or self.preview_image):
                self._handle_error("No image selected")  # Error
                loading_frame.destroy()  # Destroy loading
                return
            image_input = self.selected_file if self.selected_file else self.preview_image  # Get input
            self.controller.run_image_caption(image_input, self._on_result)  # Run task
        else:
            txt = self.text_input.get("1.0", "end").strip()  # Get text
            if not txt or txt == self.placeholder_text:
                self._handle_error("No text entered")  # Error
                loading_frame.destroy()  # Destroy loading
                return
            lang = self.lang_var.get()  # Get language
            if lang != "Auto-detect":
                txt = f"{txt} (in {lang})"  # Append language
            self.controller.run_sentiment(txt, self._on_result)  # Run task

    def _reset_run_state(self):
        """Reset running state and UI."""
        self.running = False  # Not running
        # Restore task selector(s) previous state(s) if we disabled them earlier
        prev = getattr(self, "_task_prev_state", None)
        if prev:
            for name, state in prev.items():
                w = getattr(self, name, None)
                if not w:
                    continue
                try:
                    if state is None:
                        w.configure(state="normal")
                    else:
                        w.configure(state=state)
                except Exception:
                    try:
                        w.state(["!disabled"])
                    except Exception:
                        pass
            self._task_prev_state = {}
        self.run_btn.configure(state="normal", text="Run")  # Enable button
        if self.app:
             self.app.set_status("Ready", running=False)  # Set status

    

    def _toggle_inputs(self):
        """Toggle input frames based on selected task."""
        task_label = self.task_var.get()  # Get task
        if task_label.lower().startswith("image"):
            self.text_input_frame.pack_forget()  # Hide text
            self.image_input_frame.pack(fill="x")  # Show image
            # Reset text input to default size when not in use
            self.text_input.configure(width=0, height=0)  # Reset to default (width=0 means auto-size)
        else:
            self.image_input_frame.pack_forget()  # Hide image
            self.text_input_frame.pack(fill="x")  # Show text
            # Adjust text input size for sentiment analysis - smaller and more compact
            self.text_input.configure(width=40, height=4)  # Smaller width and height for sentiment analysis