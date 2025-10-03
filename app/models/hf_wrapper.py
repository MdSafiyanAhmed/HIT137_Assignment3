# HF wrapper file for model wrappers
# This file provides OOP wrappers for Hugging Face models, demonstrating concepts like multiple inheritance, decorators, etc.
# It handles device detection, timing, caching, logging, and preprocessing.

import os  # For environment variables
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Suppress TensorFlow oneDNN warning
import functools  # For decorators
import time  # For timing
from abc import ABC, abstractmethod  # For abstract base class
from transformers import pipeline  # For Hugging Face pipelines
from PIL import Image  # For image processing
import torch  # For device detection


def get_device_for_transformers():
    """Detect device for transformers pipeline (CPU preferred if no CUDA)."""
    return -1 if not torch.cuda.is_available() else 0  # -1 for CPU, 0 for GPU


def timing(func):
    """Decorator to time function execution."""
    @functools.wraps(func)  # Preserve function metadata
    def wrapper(*a, **kw):
        t0 = time.time()  # Start time
        result = func(*a, **kw)  # Call function
        elapsed = time.time() - t0  # Calculate elapsed
        try:
            a[0]._last_time = elapsed  # Store in instance if possible
        except Exception:
            pass  # Ignore
        return result  # Return result
    return wrapper  # Return wrapped function


def simple_cache(func):
    """Simple cache decorator for function results."""
    cache = {}  # Cache dict
    @functools.wraps(func)  # Preserve metadata
    def wrapper(*a, **kw):
        key = (func.__name__, str(a[1]) if len(a) > 1 else None, tuple(sorted(kw.items())))  # Create key
        if key in cache:
            return cache[key]  # Return cached
        res = func(*a, **kw)  # Call function
        cache[key] = res  # Cache result
        return res  # Return
    return wrapper  # Return wrapped


class LoggingMixin:
    """Mixin for logging."""
    def log(self, msg):
        print("[LOG]", msg)  # Print log


class PreprocessMixin:
    """Mixin for image preprocessing."""
    def pil_to_rgb(self, pil_image):
        return pil_image.convert("RGB")  # Convert to RGB


class BaseModelWrapper(ABC, LoggingMixin):
    """Abstract base class for model wrappers."""
    def __init__(self, model_name):
        self._model_name = model_name  # Encapsulated model name
        self._pipeline = None  # Pipeline reference
        self._loaded = False  # Loaded flag
        self._last_time = None  # Last execution time

    @abstractmethod
    def load(self):
        """Abstract method to load model."""
        pass

    @abstractmethod
    def process(self, data):
        """Abstract method to process data."""
        pass

    def info(self):
        """Get model info."""
        return {
            "model_name": self._model_name,
            "loaded": self._loaded,
            "last_time": self._last_time,
        }


class ImageCaptionWrapper(BaseModelWrapper, PreprocessMixin):
    """Wrapper for image captioning model."""
    def __init__(self, model_name="nlpconnect/vit-gpt2-image-captioning"):
        super().__init__(model_name)  # Call super init
        self._device = get_device_for_transformers()  # Get device

    def load(self):
        """Load the image model if not loaded."""
        if self._loaded:
            return  # Already loaded
        self.log(f"Loading image model {self._model_name} (may download weights)...")  # Log
        self._pipeline = pipeline("image-to-text", model=self._model_name, device=self._device)  # Create pipeline
        self._loaded = True  # Set loaded

    @timing  # Time decorator
    @simple_cache  # Cache decorator
    def process(self, image_input):
        """Process image input for caption."""
        if not self._loaded:
            self.load()  # Load if needed
        if isinstance(image_input, str):
            pil = Image.open(image_input)  # Open from path
        else:
            pil = image_input  # Use PIL
        pil = self.pil_to_rgb(pil)  # Convert to RGB
        out = self._pipeline(pil)  # Run pipeline
        return out  # Return output


class SentimentWrapper(BaseModelWrapper):
    """Wrapper for sentiment analysis model."""
    def __init__(self, model_name="tabularisai/multilingual-sentiment-analysis"):
        super().__init__(model_name)  # Call super init
        self._device = get_device_for_transformers()  # Get device

    def load(self):
        """Load the text model if not loaded."""
        if self._loaded:
            return  # Already loaded
        self.log(f"Loading text model {self._model_name} ...")  # Log
        self._pipeline = pipeline("text-classification", model=self._model_name, device=self._device)  # Create pipeline
        self._loaded = True  # Set loaded

    @timing  # Time decorator
    def process(self, text):
        """Process text for sentiment."""
        if not self._loaded:
            self.load()  # Load if needed
        return self._pipeline(text)  # Run pipeline