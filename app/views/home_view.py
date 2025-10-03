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

    def _on_result(self, err, result):
        """Handle task result or error."""
        for w in self.output_frame.winfo_children():
            w.destroy()  # Clear output (including loading)
        self._reset_run_state()  # Reset state
        if err:
            self._handle_error(str(err))  # Handle error
            return
        task_label = self.task_var.get()  # Get task
        output_frame = ttk.Frame(self.output_frame)  # New output frame
        output_frame.pack(fill="both", expand=True)  # Pack
        output_frame.columnconfigure(0, weight=1)  # Column weight
        output_frame.columnconfigure(1, weight=1)  # Column weight

        if task_label.lower().startswith("image"):
            # Show image first (top), then caption and metadata below
            if self.preview_image:
                try:
                    thumb = self.preview_image.copy()  # Copy image

                    # Calculate a safe max size so the image won't overflow the output panel.
                    # If widget width isn't available yet, fall back to sensible defaults.
                    frame_w = self.output_frame.winfo_width() or 800
                    frame_h = self.output_frame.winfo_height() or 600
                    max_w = max(100, min(760, frame_w - 20))
                    max_h = max(80, min(560, frame_h - 80))

                    # Resize thumbnail to fit inside the output area
                    thumb.thumbnail((int(max_w), int(max_h)), Image.LANCZOS)
                    thumb_img = ImageTk.PhotoImage(thumb)  # PhotoImage
                    thumb_label = ttk.Label(output_frame, image=thumb_img)  # Label for image
                    thumb_label.image = thumb_img  # Reference
                    thumb_label.grid(row=0, column=0, columnspan=2, pady=6, sticky="nsew")  # Place at top spanning columns
                    thumb_label.bind("<Button-1>", self._open_full_image)  # Bind open
                except Exception:
                    pass

            # Add "Caption:" label before the actual caption text
            caption = result[0].get("generated_text", "")  # Get caption
            caption_tag = ttk.Label(output_frame, text="Caption:", font=("Segoe UI", 12, "bold"))
            caption_tag.grid(row=1, column=0, sticky="nw", padx=(4, 8), pady=5)

            # Ensure caption wraps within the output panel width
            wrap_len = int(min(760, (self.output_frame.winfo_width() or 800) - 40))
            # Show generated text on the next row, with smaller font
            caption_label = ttk.Label(output_frame, text=caption, font=("Segoe UI", 12), wraplength=wrap_len, justify="left")
            caption_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)  # Put on the row after the "Caption:" tag
            caption_label.bind("<Button-1>", lambda e: self._edit_caption(output_frame, caption_label, caption))  # Bind edit

            ttk.Label(output_frame, text=f"Generated at: {time.strftime('%H:%M:%S')}", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w")  # Timestamp moved down

            # Success animation / checkmark (moved down)
            check = ttk.Label(output_frame, text="✔", font=("Segoe UI", 14), foreground="#21C197")  # Checkmark
            check.grid(row=3, column=1, sticky="e")  # Grid
            self.after(1000, check.destroy)  # Destroy after 1s

        else:
            label = result[0]["label"]  # Get label
            score = result[0]["score"]  # Get score
            color = "#21C197" if label == "POSITIVE" else "#F87171" if label == "NEGATIVE" else "#FBBF24"  # Color based on label
            badge = ttk.Label(output_frame, text=label, background=color, foreground="#fff", padding=6, relief="raised")  # Badge label
            badge.grid(row=0, column=0, sticky="w", pady=5)  # Grid
            ttk.Label(output_frame, text=f"Score: {score:.2f}", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")  # Score label
            prog = ttk.Progressbar(output_frame, value=score*100, length=200)  # Progress bar
            prog.grid(row=2, column=0, sticky="w", pady=5, columnspan=2)  # Grid spanning
            input_text_label = ttk.Label(output_frame, text=self.text_input.get("1.0", "end").strip(), wraplength=200)  # Input text label
            input_text_label.grid(row=3, column=0, sticky="w", columnspan=2)  # Grid spanning
            # Success animation
            check = ttk.Label(output_frame, text="✔", font=("Segoe UI", 14), foreground="#21C197")  # Checkmark
            check.grid(row=1, column=1, sticky="e")  # Grid
            self.after(1000, check.destroy)  # Destroy

        if self.save_history_var.get():
            item = {  # Create history item
                "ts": time.strftime("%H:%M:%S"),  # Timestamp
                "task": task_label,  # Task
                "result": result,  # Result
            }
            # Append to shared history on the app when available
            try:
                if self.app and hasattr(self.app, "history_items"):
                    self.app.history_items.append(item)
                else:
                    self.history_items.append(item)
                self.history_list.insert("end", f"{item['ts']} — {item['task']}")
            except Exception:
                pass

    def _edit_caption(self, output_frame, caption_label, initial_caption):
        """Edit image caption inline."""
        # Place the edit entry in the same grid cell as the caption_label
        info = caption_label.grid_info()
        row = info.get("row", 0)
        col = info.get("column", 0)
        colspan = info.get("columnspan", 1)
        entry = ttk.Entry(output_frame, font=("Segoe UI", 12))  # Entry for edit (smaller font to match)
        entry.insert(0, initial_caption)  # Insert initial
        caption_label.grid_remove()  # Remove label
        entry.grid(row=row, column=col, columnspan=colspan, sticky="w", pady=5)  # Grid in same spot

        def save_caption(_e=None):
            new_caption = entry.get()  # Get new
            new_label = ttk.Label(output_frame, text=new_caption, font=("Segoe UI", 12), wraplength=400, justify="left")  # New label (smaller)
            new_label.grid(row=row, column=col, columnspan=colspan, sticky="w", pady=5)  # Grid in same spot
            entry.grid_remove()  # Remove entry
            new_label.bind("<Button-1>", lambda e: self._edit_caption(output_frame, new_label, new_caption))  # Bind edit
        entry.bind("<Return>", save_caption)  # Bind return to save

    def _open_history_item(self, _event=None):
        """Open selected history item in output."""
        idxs = self.history_list.curselection()  # Get selection
        if not idxs:
            return  # No selection
        idx = idxs[0]  # Get index
        item = self.history_items[idx]  # Get item
        for w in self.output_frame.winfo_children():
            w.destroy()  # Clear output
        output_frame = ttk.Frame(self.output_frame)  # New frame
        output_frame.pack(fill="both", expand=True)  # Pack
        ttk.Label(output_frame, text=json.dumps(item, indent=2, default=str), font=("Segoe UI", 12), wraplength=400).pack(anchor="w")  # Display JSON

    def _handle_error(self, message):
        """Handle and display error."""
        for w in self.output_frame.winfo_children():
            w.destroy()  # Clear output
        error_label = ttk.Label(self.output_frame, text=f"Error: {message}", foreground="#F87171", font=("Segoe UI", 12))  # Error label
        error_label.pack(anchor="w", pady=5)  # Pack
        self._reset_run_state()  # Reset state
        if self.app:
            self.app.last_error = message  # Set last error
            self.app.log(f"Error: {message}")  # Log
            self.app.set_status(f"Error: {message}", running=False)  # Set status
        self._border_btn_effect()  # Border effect on button

    def _border_btn_effect(self, button=None):
        """Add border effect on button click."""
        if button is None:
            button = self.run_btn  # Default to run button
            
        # Get current style and add border effect
        original_style = button.cget('style') or 'TButton'
        
        # Create a temporary style with border
        style = ttk.Style()
        style.configure('BorderEffect.TButton', borderwidth=3, relief='solid')
        
        # Apply border effect
        button.configure(style='BorderEffect.TButton')
        
        # Reset after 200ms
        self.after(200, lambda: button.configure(style=original_style))

    def copy_result(self):
        """Copy result to clipboard."""
        try:
            import pyperclip  # Import pyperclip
            
            # Find the nested output frame that contains the actual widgets
            output_children = self.output_frame.winfo_children()
            if not output_children:
                print("No output to copy")
                return
                
            nested_frame = output_children[0]  # The nested output_frame
            
            if self.task_var.get().lower().startswith("image"):
                # For image tasks, get the caption label at row=0, column=0
                widgets = nested_frame.grid_slaves(row=2, column=0)
                if widgets:
                    caption_label = widgets[0]
                    caption_text = caption_label.cget("text")
                    pyperclip.copy(caption_text)
                    print(f"Copied image caption: {caption_text}")
                else:
                    print("No caption found to copy")
            else:
                # For sentiment analysis, get badge, score, and text
                try:
                    badge_widgets = nested_frame.grid_slaves(row=0, column=0)
                    score_widgets = nested_frame.grid_slaves(row=1, column=0)
                    text_widgets = nested_frame.grid_slaves(row=3, column=0)
                    
                    if badge_widgets and score_widgets and text_widgets:
                        badge_text = badge_widgets[0].cget("text")
                        score_text = score_widgets[0].cget("text")
                        input_text = text_widgets[0].cget("text")
                        
                        formatted_result = f"{badge_text} ({score_text})\nText: {input_text}"
                        pyperclip.copy(formatted_result)
                        print(f"Copied sentiment result: {formatted_result}")
                    else:
                        print("Missing widgets for sentiment analysis copy")
                except Exception as e:
                    print(f"Error copying sentiment result: {e}")
                    
        except ImportError:
            print("pyperclip not available - cannot copy to clipboard")
        except Exception as e:
            print(f"Error copying result: {e}")

    def copy_panels(self):
        """Copy model and OOP panels to clipboard."""
        txt = "Model Info:\n" + self.model_panel.get("1.0", "end") + "\nOOP:\n"  # Start text
        for item in self.info_panel.get_children():  # Loop parents
            txt += self.info_panel.item(item)["text"] + "\n"  # Add parent
            for child in self.info_panel.get_children(item):  # Loop children
                txt += "  " + self.info_panel.item(child)["text"] + "\n"  # Add child
        try:
            import pyperclip  # Import pyperclip
            pyperclip.copy(txt)  # Copy
        except Exception:
            pass  # Ignore

    def _update_info_panel(self):
        """Update model and OOP info panels based on task."""
        task_label = self.task_var.get()
        self.model_panel.configure(state="normal")
        self.model_panel.delete("1.0", "end")
        self.info_panel.delete(*self.info_panel.get_children())
    
        if task_label.lower().startswith("image"):
            # Image to Text Model Information
            model_id = "nlpconnect/vit-gpt2-image-captioning"
            model_info = (
                "Task: Image → Text (Captioning)\n"
                f"Model ID: {model_id}\n"
                "Library: Transformers pipeline(image-to-text)\n"
                "Description: Vision Transformer (ViT) encoder with GPT-2 decoder\n"
                "Input: Image files (PNG, JPG, JPEG, BMP)\n"
                "Output: Text captions describing image content\n"
                "Use Case: Automatic image description and accessibility"
            )
        
            # OOP Concepts for Image Model
            oop = [
                ("Multiple Inheritance", "ImageCaptionWrapper → BaseModelWrapper + PreprocessMixin", [
                    "Location: hf_wrapper.py, Class: ImageCaptionWrapper",
                    "Implementation: class ImageCaptionWrapper(BaseModelWrapper, PreprocessMixin)",
                    "Why Used: Combines model management logic with image preprocessing functionality",
                    "Benefit: Code reuse and separation of concerns"
                ]),
                ("Multiple Decorators", "@timing + @simple_cache on process() method", [
                    "Location: hf_wrapper.py, Method: ImageCaptionWrapper.process",
                    "@timing: Measures inference execution time for performance monitoring",
                    "@simple_cache: Prevents redundant processing of identical images",
                    "Why Used: Performance optimization and resource management",
                    "Benefit: Faster repeated requests and performance tracking"
                ]),
                ("Encapsulation", "Private attributes and controlled access", [
                    "Location: hf_wrapper.py, Class: BaseModelWrapper",
                    "Attributes: _model_name, _pipeline, _loaded, _last_time",
                    "Why Used: Protect internal model state from external modification",
                    "Benefit: Data integrity and controlled access patterns"
                ]),
                ("Polymorphism", "process() method overridden for image-specific logic", [
                    "Location: hf_wrapper.py, Method: ImageCaptionWrapper.process",
                    "Implementation: Overrides abstract process() from BaseModelWrapper",
                    "Why Used: Custom image preprocessing (PIL conversion, RGB format)",
                    "Benefit: Consistent interface with task-specific implementation"
                ]),
                ("Abstract Base Class", "BaseModelWrapper defines interface", [
                    "Location: hf_wrapper.py, Class: BaseModelWrapper (ABC)",
                    "Methods: load(), process() marked as @abstractmethod",
                    "Why Used: Enforce consistent interface across all model wrappers",
                    "Benefit: Standardized model integration pattern"
                ]),
                ("Mixins", "PreprocessMixin for reusable image utilities", [
                    "Location: hf_wrapper.py, Class: PreprocessMixin",
                    "Method: pil_to_rgb() for image format standardization",
                    "Why Used: Share common image processing across multiple classes",
                    "Benefit: Avoid code duplication and promote consistency"
                ])
            ]
        else:
            # Sentiment Analysis Model Information
            model_id = "tabularisai/multilingual-sentiment-analysis"
            model_info = (
                "Task: Sentiment Analysis\n"
                f"Model ID: {model_id}\n"
                "Library: Transformers pipeline(text-classification)\n"
                "Description: Multilingual sentiment classification model\n"
                "Input: Text input (up to 3000 characters)\n"
                "Output: Sentiment label (POSITIVE/NEGATIVE) with confidence score\n"
                "Use Case: Text sentiment analysis and emotion detection"
            )
        
            # OOP Concepts for Sentiment Model
            oop = [
                ("Method Overriding", "SentimentWrapper.process() custom implementation", [
                    "Location: hf_wrapper.py, Method: SentimentWrapper.process",
                    "Implementation: Overrides abstract process() from BaseModelWrapper",
                    "Why Used: Text-specific processing without image preprocessing",
                    "Benefit: Tailored implementation for text classification"
                ]),
                ("Single Decorator", "@timing on process() method", [
                    "Location: hf_wrapper.py, Method: SentimentWrapper.process",
                    "Function: Measures inference time for text processing",
                    "Why Used: Performance monitoring without caching (text varies more)",
                    "Benefit: Track model performance without storage overhead"
                ]),
                ("Encapsulation", "Model state management through base class", [
                    "Location: hf_wrapper.py, Class: BaseModelWrapper",
                    "Attributes: _model_name, _pipeline, _loaded, _last_time",
                    "Why Used: Centralized state management for all model types",
                    "Benefit: Consistent model lifecycle management"
                ]),
                ("Inheritance Hierarchy", "Single inheritance from BaseModelWrapper", [
                    "Location: hf_wrapper.py, Class: SentimentWrapper",
                    "Implementation: class SentimentWrapper(BaseModelWrapper)",
                    "Why Used: Inherit common model functionality without image processing",
                    "Benefit: Simpler class structure for text-only models"
                ]),
                ("Abstract Method Implementation", "Concrete load() and process() methods", [
                    "Location: hf_wrapper.py, Class: SentimentWrapper",
                    "Implementation: Provides actual implementation for abstract methods",
                    "Why Used: Fulfill interface contract defined by BaseModelWrapper",
                    "Benefit: Ensures all model wrappers have required functionality"
                ]),
                ("Device Management", "Automatic CPU/GPU detection", [
                    "Location: hf_wrapper.py, Function: get_device_for_transformers()",
                    "Usage: Both models use same device detection logic",
                    "Why Used: Cross-platform compatibility and performance optimization",
                    "Benefit: Automatic hardware optimization without user configuration"
                ])
            ]
    
        # Update model information panel
        self.model_panel.insert("end", model_info)
        self.model_panel.configure(state="disabled")
        
        # Update OOP concepts panel
        for title, desc, details in oop:
            parent = self.info_panel.insert("", "end", text=f"{title}: {desc}")
            for detail in details:
                self.info_panel.insert(parent, "end", text=detail)

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