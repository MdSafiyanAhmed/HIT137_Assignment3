----------------------------------------
Accessibility & UI behavior notes (short)
----------------------------------------
- Read-only text panels (Model Info, Bottom Info, Output) should still accept keyboard focus (so screen readers can read their content). Ensure they are focusable and have visible focus outlines.
- Add hover tooltips for clickable elements (e.g., collapsed error summary: "Click to expand log").
- In error panels, ensure color is not the only way of communicating errors — include icons or bold text (for color-blind users).

----------------------------------------------------
Help & Troubleshooting — Common errors and what to do
====================================================

If something goes wrong, read the relevant section below and follow the suggested steps.
If the problem persists, copy the error logs (Use the "Copy full log" button in the error panel) and include them when seeking help from your instructor or teammate.

----------------------------------------
1) Internet / unstable connection during model download
----------------------------------------
Symptoms:
- Model download fails partway or repeatedly times out.
- The app stalls while "Downloading model" and later shows network-related exceptions.

Suggested fixes:
- Ensure your internet connection is stable (use wired Ethernet if possible).
- Retry the action; do not interrupt the download — allow the model to finish downloading.
- Set the HF cache to a fast drive with enough space (environment variable: HF_HOME).
- Optionally: enable the "Remote" execution mode and provide an HF API token so inference is performed in the cloud (no local download).
- If persistent failures occur, try at a different time (network congestion can impact large downloads).

Helpful commands:
- Check network connectivity:
  - `ping huggingface.co`
- If download aborts, rerun the specific test script (e.g., `python tests/test_text_model.py`) and allow it to finish.

----------------------------------------
2) Insufficient disk space for HF cache
----------------------------------------
Symptoms:
- Errors indicating write failures, disk full, or failed to save model files.
- Partial downloads and repeated downloads due to insufficient space.

Suggested fixes:
- Free disk space on the drive used by the HF cache.
- Move HF cache to a drive with more space:
  - Windows PowerShell: `setx HF_HOME "D:\hf_cache"`
  - Then restart the terminal and re-run the app.
- Check current cache usage: inspect the folder `%USERPROFILE%\.cache\huggingface\hub` (or your HF_HOME).

----------------------------------------
3) Missing Python libraries or virtual environment not activated
----------------------------------------
Symptoms:
- `ModuleNotFoundError: No module named 'transformers'` or `pillow`, `torch`, etc.
- Running the app uses system Python without necessary packages.

Suggested fixes:
- Activate the virtual environment before running the app:
  - PowerShell: `.\venv\Scripts\Activate.ps1`
- Install required packages in the active venv:
  - `python -m pip install -r requirements.txt`
  - Or individually: `python -m pip install transformers torch pillow requests huggingface_hub`
- Verify packages:
  - `python -m pip show transformers`
  - `python -c "import transformers; print(transformers.__version__)"`

----------------------------------------
4) tkinter not available in current Python installation
----------------------------------------
Symptoms:
- `ModuleNotFoundError: No module named 'tkinter'` or the test `python -m tkinter` fails to open a window.

Suggested fixes:
- On Windows, install Python from python.org which includes Tcl/Tk (tkinter). Reinstall/modify Python and ensure "tcl/tk and IDLE" is checked.
- Ensure you are running the same Python that has tkinter in the venv:
  - `python -c "import sys; print(sys.executable); import tkinter; print(tkinter.TkVersion)"`
- If using WSL or a headless container, use a local Windows Python installation or configure an X server (advanced).

Reference:
- Python tkinter docs: https://docs.python.org/3/library/tkinter.html

----------------------------------------
Useful links
----------------------------------------
- Hugging Face Models catalog: https://huggingface.co/models  
- Transformers documentation: https://huggingface.co/docs/transformers  
- Hugging Face Hub caching: https://huggingface.co/docs/huggingface_hub/how-to-cache  
- Python tkinter docs: https://docs.python.org/3/library/tkinter.html