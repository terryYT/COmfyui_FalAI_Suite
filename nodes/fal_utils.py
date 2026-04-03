"""
Shared utilities for ComfyUI_FalAI_Suite
Handles API key management, image/video processing.
"""

import io
import os
import tempfile

import numpy as np
import requests
import torch
from PIL import Image

# Runtime key store — set by the API Key node at execution time
_RUNTIME_KEY = {"key": None}


def set_runtime_key(key: str):
    _RUNTIME_KEY["key"] = key
    os.environ["FAL_KEY"] = key


def get_fal_key() -> str:
    """Return API key: runtime > env > config.ini"""
    if _RUNTIME_KEY["key"]:
        return _RUNTIME_KEY["key"]
    env_key = os.environ.get("FAL_KEY", "")
    if env_key and env_key != "<your_fal_api_key_here>":
        return env_key
    # Try config.ini next to this package
    import configparser
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")
    config = configparser.ConfigParser()
    config.read(cfg_path)
    try:
        return config["API"]["FAL_KEY"]
    except KeyError:
        return ""


def get_client():
    """Return a fal SyncClient with the current key."""
    from fal_client.client import SyncClient
    key = get_fal_key()
    if not key:
        raise RuntimeError(
            "FAL API key not set. Connect a FAL_APIKey node or set FAL_KEY in config.ini."
        )
    return SyncClient(key=key)


# ── Image helpers ─────────────────────────────────────────────────────────────

def tensor_to_pil(image: torch.Tensor) -> Image.Image:
    """ComfyUI IMAGE tensor (B,H,W,C float32 0-1) → PIL RGB."""
    if image.ndim == 4:
        image = image[0]
    arr = (image.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def pil_to_tensor(img: Image.Image) -> torch.Tensor:
    """PIL RGB → ComfyUI IMAGE tensor (1,H,W,C float32 0-1)."""
    arr = np.array(img.convert("RGB")).astype(np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)


def upload_image(image: torch.Tensor) -> str:
    """Upload a ComfyUI IMAGE tensor to fal storage, return URL."""
    pil = tensor_to_pil(image)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        pil.save(f, format="PNG")
        tmp = f.name
    try:
        client = get_client()
        url = client.upload_file(tmp)
        return url
    finally:
        os.unlink(tmp)


def download_image(url: str) -> torch.Tensor:
    """Download image URL → ComfyUI IMAGE tensor."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ComfyUI-FalAI-Suite/1.0)"}
    resp = requests.get(url, timeout=120, headers=headers)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    return pil_to_tensor(img)


def blank_image(w=512, h=512) -> torch.Tensor:
    return pil_to_tensor(Image.new("RGB", (w, h), 0))


# ── API call helper ────────────────────────────────────────────────────────────

def run_fal(endpoint: str, arguments: dict):
    """Submit job to fal endpoint synchronously and return result dict."""
    client = get_client()
    handler = client.submit(endpoint, arguments=arguments)
    return handler.get()


# ── Result parsers ─────────────────────────────────────────────────────────────

def parse_images(result: dict) -> torch.Tensor:
    """Parse result['images'] list into a batched IMAGE tensor."""
    print(f"[FAL] Raw result: {result}")

    # Handle list-wrapped result (some endpoints return a list)
    if isinstance(result, list):
        result = result[0] if result else {}

    images_data = result.get("images", [])
    if not images_data:
        print(f"[FAL] No 'images' key found. Available keys: {list(result.keys())}")
        return blank_image()

    tensors = []
    for i, img_info in enumerate(images_data):
        try:
            # img_info can be a dict {"url": ...} or a plain string URL
            url = img_info["url"] if isinstance(img_info, dict) else img_info
            print(f"[FAL] Downloading image {i+1}: {url[:80]}...")
            tensors.append(download_image(url))
        except Exception as e:
            print(f"[FAL] Failed to download image {i+1}: {e}")

    if not tensors:
        return blank_image()
    return torch.cat(tensors, dim=0)


def parse_single_image(result: dict) -> torch.Tensor:
    """Parse result['image'] single item into IMAGE tensor."""
    url = result.get("image", {}).get("url", "")
    if not url:
        return blank_image()
    return download_image(url)


def parse_video_url(result: dict) -> str:
    """Extract video URL from result."""
    return result.get("video", {}).get("url", "")
