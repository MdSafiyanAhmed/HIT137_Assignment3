## Selected models

### 1) Image → Text (Image Captioning)
**Model name:** nlpconnect/vit-gpt2-image-captioning  
**Model ID:** `nlpconnect/vit-gpt2-image-captioning`  
**Task:** Image captioning — produce a short descriptive caption for an input image.  
**Input:** PNG/JPG/BMP image file or PIL image object.  
**Output:** List of caption strings (e.g., `["a cat sleeping on a couch"]`), often with scoring metadata depending on the pipeline.  
**How to call (example):**
from transformers import pipeline
image_captioner = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning", device=-1)
res = image_captioner("path/to/my_image.jpg")
print(res) # usually a list of dicts with 'generated_text' or simple strings

**Notes & caveats:**
- This model works with `transformers.pipeline("image-to-text", ...)`. The first run will download model weights (hundreds of MB depending on variant).
- On CPU machines the inference can be slow for large images; the wrapper resizes images to a reasonable default to improve speed.
- Outputs may be short and generic; accuracy varies by image complexity.

---

### 2) Sentiment Analysis (Multilingual)
**Model name:** tabularisai/multilingual-sentiment-analysis  
**Model ID:** `tabularisai/multilingual-sentiment-analysis`  
**Task:** Text classification — sentiment (POSITIVE/NEGATIVE/NEUTRAL) for multiple languages.  
**Input:** Short to medium text (string) — supports many languages.  
**Output:** Label(s) with confidence scores (e.g., `[{ "label": "POSITIVE", "score": 0.92 }]`).  
**How to call (example):**
from transformers import pipeline
sentiment = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device=-1)
res = sentiment("I love this app!")
print(res)

**Notes & caveats:**
- This is a distilled/multilingual model tuned for reasonable CPU inference.
- For very long inputs, consider truncating or splitting text to avoid timeouts or excessive memory use.
- Always consider model biases and language coverage; results are best-effort.

---

## Common usage tips
- **Device:** In this application we default to CPU (`device=-1`). If you have multiple GPUs or a CUDA-enabled machine, change device accordingly.
- **First run / downloads:** The first time a model is used it will download model files to your HF cache (default: `~/.cache/huggingface/hub`). Expect disk use of several hundred MB per model. Set `HF_HOME` environment variable to relocate cache if needed.
- **Remote alternative:** If you prefer not to download weights locally, set the application to *Remote* mode and provide a Hugging Face API token — the app will call the HF Inference API instead (note: API limits may apply).

---

## Where to learn more
- Browse model catalog: https://huggingface.co/models  
- Transformers docs: https://huggingface.co/docs/transformers  
- Hugging Face Hub caching details: https://huggingface.co/docs/huggingface_hub/how-to-cache