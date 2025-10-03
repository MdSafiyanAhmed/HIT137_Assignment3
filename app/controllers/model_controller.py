# Model controller file for Tkinter AI GUI
# This file manages model execution in background threads to keep UI responsive.

import threading  # For background threads
from app.models.hf_wrapper import ImageCaptionWrapper, SentimentWrapper  # Import wrappers


class ModelController:
    """Controller for running models in threads."""

    def __init__(self):
        """Initialize wrappers."""
        self.image_wrapper = ImageCaptionWrapper()  # Image wrapper
        self.sentiment_wrapper = SentimentWrapper()  # Sentiment wrapper

    def run_image_caption(self, image_input, callback):
        """Run image caption in thread."""
        def worker():
            try:
                res = self.image_wrapper.process(image_input)  # Process
                callback(None, res)  # Callback success
            except Exception as e:
                callback(e, None)  # Callback error
        t = threading.Thread(target=worker, daemon=True)  # Create daemon thread
        t.start()  # Start thread

    def run_sentiment(self, text, callback):
        """Run sentiment analysis in thread."""
        def worker():
            try:
                res = self.sentiment_wrapper.process(text)  # Process
                callback(None, res)  # Callback success
            except Exception as e:
                callback(e, None)  # Callback error
        t = threading.Thread(target=worker, daemon=True)  # Create daemon thread
        t.start()  # Start thread