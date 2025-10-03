# Tkinter AI GUI Project

A professional desktop application built with Python Tkinter that provides an intuitive interface for AI-powered image captioning and sentiment analysis using Hugging Face transformer models.

## Features

### Core Functionality
- **Image-to-Text Captioning**: Shows a clear, concise caption for the uploaded image (ViT encoder + GPT‑2 decoder)
- **Sentiment Analysis**: Shows the sentence sentiment with color-coded labels (e.g., green for POSITIVE, red for NEGATIVE, amber for NEUTRAL)
- **Real-time Processing**: Background threading ensures responsive UI during model inference
- **History Management**: Track and revisit previous analysis results
- **Cache Management**: Built-in Hugging Face model cache management with size monitoring
 - **First Run Model Download**: The first run will download model weights automatically to the local Hugging Face cache

### User Interface Features
- **Modern GUI**: Clean, professional interface with themed widgets using ttk
- **Responsive Layout**: Adaptive layout that works on different screen sizes
- **Visual Feedback**: Progress indicators, status updates, and success animations
- **Interactive Elements**: Click-to-edit captions, expandable log panels, tooltips
- **Multi-panel Design**: Organized workspace with separate areas for input, output, and information
- **Accessibility**: Keyboard navigation support and screen reader friendly

### Technical Features
- **Local Processing**: Models run locally with automatic CPU/GPU detection
- **Performance Monitoring**: Built-in timing and performance tracking
- **Error Handling**: Comprehensive error management with detailed logging
- **Clipboard Integration**: Copy results and panel contents to clipboard
- **File Validation**: Input validation for image formats and file sizes
- **Settings Management**: Configurable cache directory and execution preferences

## Feature Walkthrough

- **Task Selector (Dynamic Input Panel)**: Choose between `Image to Text` and `Sentiment Analysis`. The input area adapts automatically:
  - Image task shows image selection and preview
  - Text task shows a focused text area with character limit and language selector

- **Image Selection **: Pick images using the file dialog. Supported: PNG/JPG/JPEG/BMP (≤25MB).

- **Sample Inputs for Quick Run**:
  - Image: Use the provided sample in `assets/sample.jpg`
  - Text: Insert a ready-made sample sentence via the `Use Sample Text` button

- **Image Zoom (Preview Click)**: Click the preview to open a fixed-size zoom window for a closer look at the uploaded image.

- **Run Button**: Starts model inference in the background. UI stays responsive, with progress indication in both the output area and bottom status bar.

- **Output Display**:
  - Image to Text: Shows a `Caption:` heading followed by the generated caption; click the caption to edit it inline
  - Sentiment Analysis: Shows a color-coded sentiment badge and confidence score, plus the analyzed text

- **Copy Options**:
  - `Copy Result`: Copies the current model output (caption or sentiment summary) to clipboard
  - `Copy Panels`: Copies model info and OOP details from the right-side panels

- **Clear Button**: Resets inputs and outputs—clears image preview, text area, output widgets, and info panels.

- **Save to History Checkbox**: When enabled, the app appends each result to the History list with a timestamp.

- **History Panel**: Shows a running list of completed tasks. Selecting an entry reopens its details for review.

- **Bottom Bar**:
  - Status text (ready/running/errors)
  - Progress indicator
  - Cache usage badge (shows total space used by HF cache)
  - `Clear cache` button (removes downloaded models/files from HF cache folders)
  - Click the bar to expand a log panel with detailed messages and errors

- **Model Page**: Summarizes model purpose, IDs, usage notes, and limitations; includes an extra details section with examples.

- **Help Page**: Lists common errors (e.g., missing dependencies, network issues, tkinter availability) and actionable fixes.

- **Settings Page**: Lets you select a custom Hugging Face cache directory; changes are persisted and reflected in the cache usage badge.

## Transformer Models Used

### 1. Image Captioning Model
- **Model ID**: `nlpconnect/vit-gpt2-image-captioning`
- **Architecture**: Vision Transformer (ViT) encoder + GPT-2 decoder
- **Task**: Image-to-text generation
- **Input**: PNG, JPG, JPEG, BMP images (up to 25MB)
- **Output**: Descriptive text captions
- **Use Case**: Automatic image description, accessibility, content indexing

### 2. Sentiment Analysis Model  
- **Model ID**: `tabularisai/multilingual-sentiment-analysis`
- **Architecture**: Multilingual transformer for text classification
- **Task**: Sentiment analysis with multilingual support
- **Input**: Text input (up to 3000 characters)
- **Output**: Sentiment labels (POSITIVE/NEGATIVE/NEUTRAL) with confidence scores
- **Use Case**: Text sentiment analysis, emotion detection, feedback analysis

## Implementation Overview

### Architecture Pattern
The application follows a **Model-View-Controller (MVC)** architecture:

- **Model Layer** (`app/models/`): Handles AI model integration and data processing
- **View Layer** (`app/views/`): Manages UI components and user interactions  
- **Controller Layer** (`app/controllers/`): Coordinates between models and views
- **Main Application** (`app/gui.py`): Central application management and navigation

### Key Implementation Features

#### Background Processing
- **Threading**: Model inference runs in daemon threads to prevent UI blocking
- **Callbacks**: Asynchronous result handling with error management
- **Progress Tracking**: Real-time status updates and progress indicators

#### Model Management
- **Lazy Loading**: Models are loaded only when first used
- **Device Detection**: Automatic CPU/GPU selection based on hardware availability
- **Caching**: Intelligent result caching to avoid redundant processing
- **Performance Monitoring**: Execution time tracking for optimization

#### Data Flow
1. User selects task (Image Captioning or Sentiment Analysis)
2. Input validation and preprocessing
3. Model controller spawns background thread
4. Model wrapper processes input using Hugging Face pipeline
5. Results are formatted and displayed in UI
6. Optional history saving and clipboard integration

## OOP Concepts Implementation

This project demonstrates advanced Object-Oriented Programming concepts:

### 1. Multiple Inheritance
```python
class ImageCaptionWrapper(BaseModelWrapper, PreprocessMixin):
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Combines model management with image preprocessing capabilities
- **Benefits**: Code reuse and separation of concerns

### 2. Abstract Base Classes (ABC)
```python
class BaseModelWrapper(ABC, LoggingMixin):
    @abstractmethod
    def load(self): pass
    
    @abstractmethod  
    def process(self, data): pass
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Defines consistent interface for all model wrappers
- **Benefits**: Enforces implementation contracts and standardizes model integration

### 3. Method Decorators
```python
@timing
@simple_cache
def process(self, image_input):
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Performance monitoring and caching without modifying core logic
- **Benefits**: Clean separation of cross-cutting concerns

### 4. Encapsulation
- **Private Attributes**: `_model_name`, `_pipeline`, `_loaded`, `_last_time`
- **Controlled Access**: Public methods provide controlled access to internal state
- **Benefits**: Data integrity and controlled modification patterns

### 5. Polymorphism
- **Method Overriding**: Each model wrapper implements `process()` differently
- **Consistent Interface**: Same method signature with task-specific implementations
- **Benefits**: Uniform usage pattern across different model types

### 6. Mixins
```python
class LoggingMixin:
    def log(self, msg): pass

class PreprocessMixin:
    def pil_to_rgb(self, pil_image): pass
```
- **Location**: `app/models/hf_wrapper.py`
- **Purpose**: Reusable functionality across multiple classes
- **Benefits**: Avoid code duplication and promote consistency

### 7. Composition
- **Model Controller**: Composes different model wrappers
- **View Components**: GUI components composed of multiple widgets
- **Benefits**: Flexible object relationships and modular design

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for model processing)
- **Storage**: At least 2GB free space for model cache
- **Network**: Internet connection for initial model downloads

### Python Dependencies
- `tkinter` - GUI framework (included with Python)
- `transformers>=4.30.0` - Hugging Face transformers library
- `torch>=2.0.0` - PyTorch for model inference
- `pillow>=9.0.0` - Image processing library
- `huggingface_hub>=0.15.0` - Model hub integration
- `pyperclip>=1.8.0` - Clipboard functionality
- `tkinterdnd2>=0.3.0` 
- `ttkbootstrap>=1.10.0` - Enhanced tkinter themes

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Tkinter_AI_GUI_Project
```

### 2. Create Virtual Environment
```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux  
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Run the Application
```powershell
python main.py
```

## Usage Guide

### Getting Started
1. **Launch Application**: Run `python main.py`
2. **Select Task**: Choose between "Image to Text" or "Sentiment Analysis"
3. **Provide Input**: 
   - For images: Click "Choose Image", or use sample
   - For text: Type/paste text or use sample text
4. **Run Analysis**: Click "Run" button
5. **View Results**: Results appear in the center panel with additional details

### Navigation
- **🏠 Home**: Main interface for running AI tasks
- **📚 Models**: Information about the transformer models used
- **❓ Help**: Troubleshooting guide and common issues
- **⚙ Settings**: Configure cache directory and application settings

### Advanced Features
- **History**: Previous results are saved and accessible in the history panel
- **Cache Management**: Monitor and clear model cache from settings
- **Copy Results**: Use "Copy Result" to copy outputs to clipboard
- **Edit Captions**: Click on generated captions to edit them inline
- **Log Panel**: Click status bar to expand detailed logs

## Project Structure

```
Tkinter_AI_GUI_Project/
├── app/
│   ├── __init__.py
│   ├── gui.py                 # Main application window and navigation
│   ├── utils.py               # Shared utilities (ToolTip class)
│   ├── controllers/
│   │   └── model_controller.py # Threading and model coordination
│   ├── models/
│   │   └── hf_wrapper.py      # AI model wrappers with OOP concepts
│   ├── views/
│   │   └── home_view.py       # Main interface components
│   ├── help.md               # Help documentation
│   ├── model_info.md         # Model information
│   └── oop_docs.txt          # OOP concepts documentation
├── assets/
│   └── sample.jpg            # Sample image for testing
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── verify_installation.py   # Installation verification script
└── README.md                # This file
```

## Configuration

### Environment Variables
- `HF_HOME`: Set custom Hugging Face cache directory
  ```bash
  # Windows
  set HF_HOME=D:\hf_cache
  
  # macOS/Linux
  export HF_HOME=/path/to/cache
  ```

### Model Cache
- **Default Location**: `~/.cache/huggingface/hub`
- **Size**: Approximately 500MB-1GB per model
- **Management**: Use built-in cache management tools in Settings

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
**Problem**: Missing Python packages
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. tkinter Not Available
**Problem**: tkinter not included with Python installation
**Solution**: Install Python from python.org with tkinter support

#### 3. Model Download Failures
**Problem**: Network issues during model download
**Solution**: 
- Check internet connection
- Retry the operation
- Clear cache and try again

#### 4. Out of Memory Errors
**Problem**: Insufficient RAM for model processing
**Solution**:
- Close other applications
- Use smaller images
- Enable CPU-only processing

### Getting Help
1. Check the **Help** tab in the application for detailed troubleshooting
2. Review error logs in the expandable log panel
3. Use "Copy Panels" to share configuration details when seeking help

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Hugging Face** for the transformers library and pre-trained models
- **nlpconnect** for the ViT-GPT2 image captioning model
- **tabularisai** for the multilingual sentiment analysis model
- **Python Software Foundation** for the tkinter GUI framework

## Support

For questions, issues, or suggestions:
- Open an issue in the repository
- Check the built-in Help documentation
- Review the troubleshooting guide in the application

---

*Built with using Python, Tkinter, and Hugging Face Transformers*

# Tkinter AI GUI — Setup Guide (Windows, reproducible)

This document gives a procedure to set up this project on another Windows PC and run it with `python main.py`. Follow steps exactly. Commands below assume you run them in Project root (the folder that contains `main.py` ).

---

## 1) Recommended Python versions
- Prefer Python 3.10, 3.11 or 3.12 (64-bit). These are tested and stable for typical ML libs.
- Avoid system Python from Microsoft Store if unsure; use the official python.org installer.

## 2) Install Python (if not installed)
- Download the installer from https://www.python.org/downloads/
- Run the installer and **check "Add Python X.Y to PATH"** during installation.
- Install the full "tcl/tk and IDLE" component so `tkinter` is available.

Verify:
- PowerShell / CMD:
  - python --version
  - python -c "import tkinter; print('tkinter OK')"

If either command fails, re-run installer and enable PATH + tcl/tk when installing python.

---

## 3) Open a terminal in project folder
- Use PowerShell or CMD
- Navigate to the project root (where `main.py` is):
  - cd "project\directory\Tkinter_AI_GUI"

---

## 4) Create and activate a virtual environment (per-project)
PowerShell (recommended)
- Create:
  - python -m venv venv
- Allow activation for this session (temporary): optional
  - Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
- Activate:
  - .\venv\Scripts\Activate.ps1

CMD
- Create:
  - python -m venv venv
- Activate:
  - venv\Scripts\activate.bat

After activation the prompt should show `(venv)`.

---

## 5) Upgrade pip and build tools
- python -m pip install --upgrade pip setuptools wheel

---

## 6) Install PyTorch (choose appropriate command)
PyTorch installation varies by CUDA/CPU. Use the official selector at https://pytorch.org/get-started/locally to copy the correct command.

Common CPU-only command (works on any machine, deterministic, recommended):
- pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio --upgrade

If you have an NVIDIA GPU and want GPU support:
- Visit https://pytorch.org/get-started/locally, select your OS, package "pip", language "python", compute platform (CUDA version), and copy the provided command.

---

## 7) Install other Python dependencies
If the project has a `requirements.txt`, run:
- pip install -r requirements.txt

If not, install the common packages used by this project:
- pip install transformers==4.35.0 Pillow==10.0.0 accelerate

Notes:
- `transformers` requires a compatible `torch` — ensure step 6 installed torch first.
- If you get an SSL or permission error, retry `python -m pip install <pkg>` or run terminal as user with network access.

---

## 8) Set Hugging Face cache (optional, recommended)
Set a fixed cache folder so model downloads are consistent across machines.

PowerShell (persistent):
- setx HF_HOME "C:\hf_cache"

CMD (persistent):
- setx HF_HOME "C:\hf_cache"

For current session only:
- PowerShell: $env:HF_HOME = "C:\hf_cache"
- CMD: set HF_HOME=C:\hf_cache

Create the folder if needed:
- mkdir C:\hf_cache

---

## 9) Ensure assets and sample image exist
Project expects `assets/sample.jpg`. If missing, copy a sample file there:
- mkdir assets
- copy C:\path\to\your\sample.jpg assets\sample.jpg

---

## 10) Run the app
- python main.py

If errors occur, read the Troubleshooting section below.

---

## 11) Troubleshooting (common issues)
- "tkinter" import error:
  - Reinstall Python from python.org and ensure "tcl/tk" selected.
- Import errors for torch/transformers:
  - Re-run the PyTorch command from step 6 that matches your CUDA version, or use the CPU-only command.
- Permission / ExecutionPolicy when activating venv in PowerShell:
  - Use: Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
- Model download slow or fails:
  - Check HF_HOME environment, ensure enough disk space and network access. Use `setx` so downloads persist.
- App layout issues after image selection:
  - Ensure you're running with the correct Python and Pillow installed (step 7).

---

## 12) Reproducing environment exactly (optional)
To capture exact installed packages on the working machine:
- pip freeze > pinned-requirements.txt

On target machine:
- pip install -r pinned-requirements.txt

---

## Notes & guarantees
- These steps are Windows-specific and aim to be deterministic and minimal.
- Use the exact commands shown, especially for venv creation/activation and PyTorch install.
- If you need instructions for macOS/Linux, request them and they will be provided.

---

End of setup guide.
