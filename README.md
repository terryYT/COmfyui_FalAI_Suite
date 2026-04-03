# ComfyUI FAL AI Suite

A comprehensive [fal.ai](https://fal.ai) API node pack for ComfyUI.  
Generate images and videos from text or existing images — all via the fal.ai cloud API, no local GPU required for generation.

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Your FAL API Key](#getting-your-fal-api-key)
- [Setting Up Your API Key in ComfyUI](#setting-up-your-api-key-in-comfyui)
- [Nodes Reference](#nodes-reference)
  - [FAL API Key](#fal-api-key)
  - [FAL Text to Image](#fal-text-to-image)
  - [FAL Image to Image](#fal-image-to-image)
  - [FAL Multi Prompt Image](#fal-multi-prompt-image)
  - [FAL Multi Image Refine](#fal-multi-image-refine)
  - [FAL Seedream Edit](#fal-seedream-edit)
  - [FAL Text to Video](#fal-text-to-video)
  - [FAL Image to Video](#fal-image-to-video)
  - [FAL Image to Video (Start+End Frame)](#fal-image-to-video-startend-frame)
  - [FAL Video Download](#fal-video-download)
  - [FAL Video URL Preview](#fal-video-url-preview)
- [Supported Models](#supported-models)
- [Tips](#tips)

---

## Requirements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (any recent version)
- Python 3.9+
- A [fal.ai](https://fal.ai) account with an API key
- Internet connection (all generation happens on fal.ai servers)

---

## Installation

### Option 1 — ComfyUI Manager (Recommended)

1. Open ComfyUI and go to **Manager → Install Custom Nodes**.
2. Search for **ComfyUI FAL AI Suite**.
3. Click **Install** and restart ComfyUI.

### Option 2 — Manual (Git Clone)

1. Open a terminal and navigate to your ComfyUI `custom_nodes` folder:

```bash
cd ComfyUI/custom_nodes
```

2. Clone the repository:

```bash
git clone https://github.com/terryYT/COmfyui_FalAI_Suite.git ComfyUI_FalAI_Suite
```

3. Install the required Python packages.

**Windows (ComfyUI portable):**
```bash
..\..\..\python_embeded\python.exe -m pip install -r ComfyUI_FalAI_Suite/requirements.txt
```

**Standard Python / venv:**
```bash
pip install -r ComfyUI_FalAI_Suite/requirements.txt
```

4. Restart ComfyUI.

---

## Getting Your FAL API Key

You need a fal.ai API key to use any node in this pack. Here is how to get one:

1. Go to [https://fal.ai](https://fal.ai) and click **Sign Up** (top right).
2. Create a free account using your email, Google, or GitHub.
3. After logging in, open the [API Keys dashboard](https://fal.ai/dashboard/keys).
4. Click **Add key** and give it a name (e.g. `ComfyUI`).
5. Copy the key — it looks like `fal_key_xxxxxxxxxxxxxxxxxxxxxxxx`.

> **Keep your key private.** Do not share it publicly or commit it to git.

fal.ai offers free credits for new accounts. Pricing for each model can be found on the [fal.ai pricing page](https://fal.ai/pricing).

---

## Setting Up Your API Key in ComfyUI

There are two ways to provide your key:

### Method 1 — FAL API Key Node (Recommended)

Add the **FAL API Key** node to your workflow:

1. Right-click the canvas → **Add Node → FAL AI Suite → FAL API Key**.
2. Paste your key into the `api_key` field.
3. Connect the `fal_connection` output to the `fal_connection` input of any generation node.

Every generation node requires this connection. Wire one key node to all your generation nodes.

### Method 2 — config.ini

Edit the `config.ini` file inside the node folder:

```ini
[API]
FAL_KEY = fal_key_xxxxxxxxxxxxxxxxxxxxxxxx
```

Save the file and restart ComfyUI. The key will be loaded automatically on startup, but you still need to add a **FAL API Key** node to your workflow.

---

## Nodes Reference

### FAL API Key

**Category:** `FAL AI Suite`

The root node. Set your fal.ai API key here and wire its output to every other node.

| Input | Type | Description |
|-------|------|-------------|
| `api_key` | STRING | Your fal.ai API key |

| Output | Type | Description |
|--------|------|-------------|
| `fal_connection` | FAL_CONNECTION | Pass this to all generation nodes |

---

### FAL Text to Image

**Category:** `FAL AI Suite / Image`

Generate images from a text prompt using a wide range of fal.ai models.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `model` | Dropdown | Model to use (see [Supported Models](#supported-models)) |
| `prompt` | STRING | What to generate |
| `image_size` | Dropdown | Preset size: `square_hd`, `landscape_16_9`, `portrait_4_3`, etc. Use `custom` to set width/height manually |
| `width` / `height` | INT | Custom dimensions (only used when `image_size` is `custom`) |
| `num_inference_steps` | INT | Number of denoising steps (default: 28) |
| `guidance_scale` | FLOAT | How closely to follow the prompt (default: 3.5) |
| `num_images` | INT | Number of images to generate (1–4) |
| `seed` | INT | Set to `-1` for random, or any value for reproducibility |
| `negative_prompt` | STRING | *(optional)* What to avoid |
| `aspect_ratio` | Dropdown | For Nano Banana models: `1:1`, `16:9`, `9:16`, etc. |
| `resolution` | Dropdown | For Nano Banana models: `1K`, `2K`, `4K` |
| `safety_tolerance` | Dropdown | For Nano Banana models: `1` (strictest) – `6` (most open) |
| `thinking_level` | Dropdown | For Nano Banana models: `none`, `minimal`, `high` |

| Output | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | Generated image tensor |
| `status` | STRING | Timing and status message |

---

### FAL Image to Image

**Category:** `FAL AI Suite / Image`

Transform an existing image using a prompt.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `image` | IMAGE | Input image |
| `model` | Dropdown | I2I model to use |
| `prompt` | STRING | Describe the desired output |
| `strength` | FLOAT | How much to change the image (0.0 = no change, 1.0 = full change) |
| `num_inference_steps` | INT | Denoising steps |
| `guidance_scale` | FLOAT | Prompt adherence |
| `num_images` | INT | Number of outputs (1–4) |
| `seed` | INT | `-1` for random |
| `negative_prompt` | STRING | *(optional)* What to avoid |
| `aspect_ratio` | Dropdown | For Nano Banana Edit |
| `resolution` | Dropdown | For Nano Banana Edit: `1K`, `2K`, `4K` |
| `safety_tolerance` | Dropdown | For Nano Banana Edit: `1`–`6` |
| `image_size` | Dropdown | For Seedream models |
| `enable_safety_checker` | BOOLEAN | For Seedream models |

| Output | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | Transformed image tensor |
| `status` | STRING | Timing and status message |

---

### FAL Multi Prompt Image

**Category:** `FAL AI Suite / Image`

Generate one image per line of prompts in a single batch. Each line becomes a separate API call and all results are returned as a batched IMAGE tensor.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `prompts` | STRING (multiline) | One prompt per line |
| `model` | Dropdown | Model to use (Flux variants, SDXL, Aura Flow) |
| `image_size` | Dropdown | Output size preset |
| `width` / `height` | INT | Custom size (when `image_size` is `custom`) |
| `num_inference_steps` | INT | Denoising steps |
| `guidance_scale` | FLOAT | Prompt adherence |
| `seed` | INT | Base seed — each image gets seed + index |

| Output | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | All generated images as a batch tensor |

---

### FAL Multi Image Refine

**Category:** `FAL AI Suite / Image`

Feed a batch of images through an image-to-image model with one shared prompt. Each image is processed separately and results are returned as a new batch.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `images` | IMAGE | Batch of images to refine |
| `prompt` | STRING | Describe the refinement |
| `strength` | FLOAT | How much to change each image |
| `num_inference_steps` | INT | Denoising steps |
| `guidance_scale` | FLOAT | Prompt adherence |
| `seed` | INT | Base seed — each image gets seed + index |

| Output | Type | Description |
|--------|------|-------------|
| `refined_images` | IMAGE | Refined images as a batch tensor |

---

### FAL Seedream Edit

**Category:** `FAL AI Suite / Seedream`

Dedicated node for ByteDance Seedream image editing. Provides fine-grained size presets and live status on the node during generation.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `image` | IMAGE | Input image to edit |
| `model` | Dropdown | `Seedream v5 Lite` or `Seedream v4.5` |
| `prompt` | STRING | Describe the edit |
| `size_preset` | Dropdown | Output size — many aspect ratios up to 4K, or `Custom` |
| `width` / `height` | INT | Used when `size_preset` is `Custom` |
| `sequential_image_generation` | Dropdown | `enabled` runs each image one by one for variety; `disabled` batches them |
| `max_images` | INT | How many images to generate (1–6) |
| `seed` | INT | Seed for reproducibility |
| `enable_safety_checker` | BOOLEAN | Enable or disable the safety filter |

| Output | Type | Description |
|--------|------|-------------|
| `images` | IMAGE | Edited image tensor |
| `status` | STRING | Timing and status message |

---

### FAL Text to Video

**Category:** `FAL AI Suite / Video`

Generate a video from a text prompt. Videos are automatically saved to your ComfyUI output folder.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `model` | Dropdown | Video model to use |
| `prompt` | STRING | Describe the video |
| `duration` | Dropdown | `5` or `10` seconds (model-dependent) |
| `aspect_ratio` | Dropdown | `16:9`, `9:16`, `1:1`, `4:3`, `3:4` |
| `save_video` | BOOLEAN | Auto-save to ComfyUI output folder |
| `filename_prefix` | STRING | Prefix for saved files (e.g. `fal_video`) |
| `negative_prompt` | STRING | *(optional)* What to avoid |
| `seed` | INT | *(optional)* `-1` for random |

| Output | Type | Description |
|--------|------|-------------|
| `video_url` | STRING | Direct URL to the generated video on fal.ai |
| `saved_path` | STRING | Local file path if `save_video` is enabled |

> Video generation typically takes **1–3 minutes** depending on the model.

---

### FAL Image to Video

**Category:** `FAL AI Suite / Video`

Animate a still image into a video.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `image` | IMAGE | Input image to animate |
| `model` | Dropdown | I2V model to use |
| `prompt` | STRING | Describe the motion or scene |
| `duration` | Dropdown | `5` or `10` seconds |
| `aspect_ratio` | Dropdown | `16:9`, `9:16`, `1:1`, `4:3`, `3:4` |
| `save_video` | BOOLEAN | Auto-save to ComfyUI output folder |
| `filename_prefix` | STRING | Prefix for saved files |
| `negative_prompt` | STRING | *(optional)* What to avoid |
| `seed` | INT | *(optional)* `-1` for random |

| Output | Type | Description |
|--------|------|-------------|
| `video_url` | STRING | Direct URL to the generated video |
| `saved_path` | STRING | Local file path if `save_video` is enabled |

---

### FAL Image to Video (Start+End Frame)

**Category:** `FAL AI Suite / Video`

Animate between a start frame and an end frame using Kling v1.5 Pro. The model generates the in-between motion automatically.

| Input | Type | Description |
|-------|------|-------------|
| `fal_connection` | FAL_CONNECTION | From the API Key node |
| `start_image` | IMAGE | First frame of the video |
| `end_image` | IMAGE | Last frame of the video |
| `prompt` | STRING | Describe the transition or motion |
| `duration` | Dropdown | `5` or `10` seconds |
| `save_video` | BOOLEAN | Auto-save to ComfyUI output folder |
| `filename_prefix` | STRING | Prefix for saved files |
| `seed` | INT | *(optional)* `-1` for random |

| Output | Type | Description |
|--------|------|-------------|
| `video_url` | STRING | Direct URL to the generated video |
| `saved_path` | STRING | Local file path if `save_video` is enabled |

---

### FAL Video Download

**Category:** `FAL AI Suite / Video`

Download any video URL to your ComfyUI output folder. Useful when you want to re-save a URL from a previous run.

| Input | Type | Description |
|-------|------|-------------|
| `video_url` | STRING | The video URL to download |
| `filename_prefix` | STRING | Prefix for the saved file |

| Output | Type | Description |
|--------|------|-------------|
| `saved_path` | STRING | Local file path of the downloaded video |

---

### FAL Video URL Preview

**Category:** `FAL AI Suite / Video`

Displays the video URL in the ComfyUI console and passes it through unchanged. Useful for debugging or inspecting URLs mid-workflow.

| Input | Type | Description |
|-------|------|-------------|
| `video_url` | STRING | The video URL to preview |

| Output | Type | Description |
|--------|------|-------------|
| `video_url` | STRING | Same URL, passed through |

---

## Supported Models

### Text to Image

| Model | Notes |
|-------|-------|
| Flux Schnell (fast) | Fastest Flux model, great for iteration |
| Flux Dev | Higher quality, slower |
| Flux Pro | Production-quality |
| Flux Pro 1.1 | Updated Pro version |
| Flux Pro 1.1 Ultra | Highest quality Flux |
| Stable Diffusion XL | Classic SDXL |
| Aura Flow | High-quality artistic model |
| Recraft V3 | Great for design and illustration |
| Ideogram V2 | Excellent text in images |
| SANA | Fast high-resolution model |
| Nano Banana Pro | Google Gemini-backed, supports thinking modes |
| Nano Banana 2 | Google Gemini-backed v2 |

### Image to Image

| Model | Notes |
|-------|-------|
| Flux Dev Image-to-Image | Flux Dev I2I |
| Flux Pro Image-to-Image | Flux Pro v1.1 I2I |
| SDXL Image-to-Image | Classic SDXL I2I |
| Flux Canny (ControlNet) | Edge-guided generation |
| Flux Depth (ControlNet) | Depth-guided generation |
| Creative Upscaler | AI-enhanced upscaling with creativity |
| Clarity Upscaler | Sharp detail upscaling |
| Nano Banana Pro Edit | Gemini-backed image editing |
| Seedream v4.5 Edit | ByteDance Seedream editing |
| Seedream v5 Lite Edit | ByteDance Seedream v5 editing |

### Text to Video

| Model | Max Duration | Notes |
|-------|-------------|-------|
| Kling v1.5 Standard | 5s | Fast and affordable |
| Kling v1.5 Pro | 10s | Higher quality |
| Kling v2 Standard | 5s | Improved motion |
| Kling v2 Pro | 10s | Best Kling quality |
| MiniMax (Hailuo) | 6s | Smooth cinematic motion |
| WAN Text-to-Video | 5s | Open-source WAN model |
| LTX Video | 5s | Fast latent video model |
| Hunyuan Video | 5s | Tencent Hunyuan model |

### Image to Video

| Model | Notes |
|-------|-------|
| Kling v1.5 Standard | Animate images, 5s |
| Kling v1.5 Pro | Higher quality, up to 10s |
| Kling v2 Standard | Improved Kling v2 |
| Kling v2 Pro | Best quality Kling |
| MiniMax (Hailuo) | Cinematic animation |
| WAN Image-to-Video | Open-source WAN |
| LTX Video I2V | Fast latent model |
| Stable Video Diffusion | Classic SVD model |

---

## Tips

- **Always wire the FAL API Key node first.** Every generation node needs a `fal_connection` input.
- **Use seed `-1`** for random results, or set a fixed seed to reproduce a generation.
- **Video generation takes time** — Kling and MiniMax can take 1–3 minutes. Be patient.
- **Save your API key securely.** Do not paste it into shared workflows or screenshots.
- **Check your fal.ai credit balance** at [fal.ai/dashboard](https://fal.ai/dashboard) before running expensive models.
- **Multi Prompt Image** is great for comparing many concepts at once — put one idea per line.
- **Start+End Frame** is powered by Kling v1.5 Pro and works best when start and end images share a consistent subject.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Made with fal.ai · [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys)
