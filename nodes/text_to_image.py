"""
FAL Text-to-Image Node
Supports Flux Schnell, Flux Dev, Flux Pro, SDXL, Aura Flow, Recraft V3, Ideogram V2,
Nano Banana Pro, Nano Banana 2, Seedream v4.5.
"""

import time
import torch
from .fal_utils import run_fal, parse_images, parse_single_image, blank_image

# Model registry: display name -> (endpoint, uses_images_list, param_style)
# param_style:
#   "flux"   — image_size / guidance_scale / num_inference_steps
#   "gemini" — aspect_ratio / resolution / safety_tolerance (Nano Banana models)
#   "single" — image_size / guidance_scale / num_inference_steps, returns result["image"]
T2I_MODELS = {
    "Flux Schnell (fast)":    ("fal-ai/flux/schnell",           True,  "flux"),
    "Flux Dev":               ("fal-ai/flux/dev",               True,  "flux"),
    "Flux Pro":               ("fal-ai/flux-pro",               True,  "flux"),
    "Flux Pro 1.1":           ("fal-ai/flux-pro/v1.1",          True,  "flux"),
    "Flux Pro 1.1 Ultra":     ("fal-ai/flux-pro/v1.1-ultra",    True,  "flux"),
    "Stable Diffusion XL":    ("fal-ai/stable-diffusion-xl",    True,  "flux"),
    "Aura Flow":              ("fal-ai/aura-flow",              True,  "flux"),
    "Recraft V3":             ("fal-ai/recraft-v3",             True,  "flux"),
    "Ideogram V2":            ("fal-ai/ideogram/v2",            False, "single"),
    "SANA":                   ("fal-ai/sana",                   True,  "flux"),
    # Google / Gemini-backed models
    "Nano Banana Pro":        ("fal-ai/nano-banana-pro",        True,  "gemini"),
    "Nano Banana 2":          ("fal-ai/nano-banana-2",          True,  "gemini"),
}

IMAGE_SIZES = [
    "square_hd", "square",
    "portrait_4_3", "portrait_16_9",
    "landscape_4_3", "landscape_16_9",
    "custom",
]

ASPECT_RATIOS = [
    "1:1", "16:9", "9:16", "4:3", "3:4",
    "3:2", "2:3", "5:4", "4:5", "21:9", "auto",
]

RESOLUTIONS = ["1K", "2K", "4K"]

SAFETY_TOLERANCES = ["1", "2", "3", "4", "5", "6"]

THINKING_LEVELS = ["none", "minimal", "high"]


class FAL_TextToImage:
    """Generate images from a text prompt using fal.ai models."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection":      ("FAL_CONNECTION",),
                "model":               (list(T2I_MODELS.keys()), {"default": "Flux Schnell (fast)"}),
                "prompt":              ("STRING", {"default": "", "multiline": True}),
                # --- Flux-style params ---
                "image_size":          (IMAGE_SIZES, {"default": "landscape_16_9"}),
                "width":               ("INT",   {"default": 1280, "min": 256, "max": 4096, "step": 16}),
                "height":              ("INT",   {"default": 720,  "min": 256, "max": 4096, "step": 16}),
                "num_inference_steps": ("INT",   {"default": 28,   "min": 1,   "max": 100}),
                "guidance_scale":      ("FLOAT", {"default": 3.5,  "min": 1.0, "max": 20.0, "step": 0.1}),
                # --- Gemini-style params (Nano Banana) ---
                "aspect_ratio":        (ASPECT_RATIOS, {"default": "16:9"}),
                "resolution":          (RESOLUTIONS,   {"default": "1K"}),
                "safety_tolerance":    (SAFETY_TOLERANCES, {"default": "4"}),
                # --- Shared ---
                "num_images":          ("INT",   {"default": 1, "min": 1, "max": 4}),
                "seed":                ("INT",   {"default": -1, "min": -1, "max": 2147483647}),
            },
            "optional": {
                "negative_prompt":  ("STRING", {"default": "", "multiline": True}),
                "thinking_level":   (THINKING_LEVELS, {"default": "none"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "status")
    OUTPUT_NODE  = True
    FUNCTION     = "generate"
    CATEGORY     = "FAL AI Suite/Image"

    def generate(
        self,
        fal_connection,
        model,
        prompt,
        image_size,
        width,
        height,
        num_inference_steps,
        guidance_scale,
        aspect_ratio,
        resolution,
        safety_tolerance,
        num_images,
        seed,
        negative_prompt="",
        thinking_level="none",
    ):
        t_start = time.time()
        try:
            endpoint, uses_images, param_style = T2I_MODELS[model]

            if param_style == "gemini":
                args = _build_gemini_args(
                    prompt, num_images, seed,
                    aspect_ratio, resolution, safety_tolerance, thinking_level,
                )
            else:
                args = _build_flux_args(
                    prompt, num_images, seed,
                    image_size, width, height,
                    num_inference_steps, guidance_scale,
                    negative_prompt,
                )

            print(f"[FAL_TextToImage] Calling {endpoint}...")
            t_api = time.time()
            result = run_fal(endpoint, args)
            api_secs = round(time.time() - t_api, 1)
            total_secs = round(time.time() - t_start, 1)

            if param_style == "single":
                tensor = parse_single_image(result)
            else:
                tensor = parse_images(result)

            n = tensor.shape[0]
            msg = f"Done  {n} image{'s' if n>1 else ''}  |  {api_secs}s API  |  {total_secs}s total"
            print(f"[FAL_TextToImage] {msg}")
            return {"ui": {"text": [msg]}, "result": (tensor, msg)}

        except Exception as e:
            total_secs = round(time.time() - t_start, 1)
            msg = f"Error after {total_secs}s: {str(e)[:120]}"
            print(f"[FAL_TextToImage] {msg}")
            return {"ui": {"text": [msg]}, "result": (blank_image(), msg)}


def _build_flux_args(prompt, num_images, seed, image_size, width, height,
                     num_inference_steps, guidance_scale, negative_prompt):
    args = {
        "prompt": prompt,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "num_images": num_images,
    }
    if image_size == "custom":
        args["image_size"] = {"width": width, "height": height}
    else:
        args["image_size"] = image_size
    if negative_prompt:
        args["negative_prompt"] = negative_prompt
    if seed != -1:
        args["seed"] = seed
    return args


def _build_gemini_args(prompt, num_images, seed, aspect_ratio,
                       resolution, safety_tolerance, thinking_level):
    args = {
        "prompt": prompt,
        "num_images": num_images,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "safety_tolerance": safety_tolerance,
    }
    if seed != -1:
        args["seed"] = seed
    if thinking_level and thinking_level != "none":
        args["thinking_level"] = thinking_level
    return args


NODE_CLASS_MAPPINGS = {
    "FAL_TextToImage": FAL_TextToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_TextToImage": "FAL Text to Image",
}
