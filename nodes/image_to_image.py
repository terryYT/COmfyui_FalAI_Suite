"""
FAL Image-to-Image Node
Takes an input image + prompt and generates a new image via fal.ai.
Supports Flux Dev/Pro I2I, SDXL I2I, Flux ControlNet, Upscalers,
Nano Banana Pro Edit (Gemini), Seedream v4.5 / v5 Lite Edit (ByteDance).
"""

import time
import torch
from .fal_utils import run_fal, parse_images, parse_single_image, upload_image, blank_image

# param_style:
#   "flux"     — image_url (single), strength, guidance_scale, steps
#   "gemini"   — image_urls (list), aspect_ratio, resolution, safety_tolerance 1-6 (Nano Banana)
#   "seedream" — image_urls (list), image_size, enable_safety_checker bool (ByteDance)
#   "upscaler" — image_url (single), prompt only
I2I_MODELS = {
    "Flux Dev Image-to-Image":   ("fal-ai/flux/dev/image-to-image",            True,  "flux"),
    "Flux Pro Image-to-Image":   ("fal-ai/flux-pro/v1.1/image-to-image",       True,  "flux"),
    "SDXL Image-to-Image":       ("fal-ai/stable-diffusion-xl/image-to-image", True,  "flux"),
    "Flux Canny (ControlNet)":   ("fal-ai/flux-controlnet-canny",              True,  "flux"),
    "Flux Depth (ControlNet)":   ("fal-ai/flux-controlnet-depth",              True,  "flux"),
    "Creative Upscaler":         ("fal-ai/creative-upscaler",                  False, "upscaler"),
    "Clarity Upscaler":          ("fal-ai/clarity-upscaler",                   False, "upscaler"),
    "Nano Banana Pro Edit":      ("fal-ai/nano-banana-pro/edit",               True,  "gemini"),
    "Seedream v4.5 Edit":        ("fal-ai/bytedance/seedream/v4.5/edit",       True,  "seedream"),
    "Seedream v5 Lite Edit":     ("fal-ai/bytedance/seedream/v5/lite/edit",    True,  "seedream"),
}

IMAGE_SIZES = [
    "square_hd", "square",
    "portrait_4_3", "portrait_16_9",
    "landscape_4_3", "landscape_16_9",
    "auto_2K", "auto_3K", "auto_4K",
]

ASPECT_RATIOS = [
    "1:1", "16:9", "9:16", "4:3", "3:4",
    "3:2", "2:3", "5:4", "4:5", "21:9", "auto",
]

RESOLUTIONS        = ["1K", "2K", "4K"]
SAFETY_TOLERANCES  = ["1", "2", "3", "4", "5", "6"]   # Nano Banana only (1=strictest)


class FAL_ImageToImage:
    """Transform an existing image with a prompt using fal.ai models."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection": ("FAL_CONNECTION",),
                "image":          ("IMAGE",),
                "model":          (list(I2I_MODELS.keys()), {"default": "Flux Dev Image-to-Image"}),
                "prompt":         ("STRING", {"default": "", "multiline": True}),

                # --- Flux-style ---
                "strength":            ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.01}),
                "num_inference_steps": ("INT",   {"default": 28,   "min": 1,   "max": 100}),
                "guidance_scale":      ("FLOAT", {"default": 3.5,  "min": 1.0, "max": 20.0, "step": 0.1}),

                # --- Gemini-style (Nano Banana) ---
                "aspect_ratio":       (ASPECT_RATIOS,     {"default": "1:1"}),
                "resolution":         (RESOLUTIONS,        {"default": "1K"}),
                "safety_tolerance":   (SAFETY_TOLERANCES,  {"default": "4"}),

                # --- Seedream-style (ByteDance) ---
                "image_size":          (IMAGE_SIZES, {"default": "square_hd"}),
                # ON = safe, OFF = allow more content
                "enable_safety_checker": ("BOOLEAN", {"default": True, "label_on": "Safety ON", "label_off": "Safety OFF"}),

                # --- Shared ---
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "seed":       ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
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
        image,
        model,
        prompt,
        strength,
        num_inference_steps,
        guidance_scale,
        aspect_ratio,
        resolution,
        safety_tolerance,
        image_size,
        enable_safety_checker,
        num_images,
        seed,
        negative_prompt="",
    ):
        t_start = time.time()
        try:
            endpoint, uses_images, param_style = I2I_MODELS[model]

            print(f"[FAL_ImageToImage] Uploading image...")
            image_url = upload_image(image)

            if param_style == "gemini":
                args = {
                    "prompt":           prompt,
                    "image_urls":       [image_url],
                    "num_images":       num_images,
                    "aspect_ratio":     aspect_ratio,
                    "resolution":       resolution,
                    "safety_tolerance": safety_tolerance,
                }
                if seed != -1:
                    args["seed"] = seed

            elif param_style == "seedream":
                args = {
                    "prompt":                 prompt,
                    "image_urls":             [image_url],
                    "image_size":             image_size,
                    "num_images":             num_images,
                    "max_images":             num_images,
                    "enable_safety_checker":  enable_safety_checker,
                }
                if seed != -1:
                    args["seed"] = seed

            elif param_style == "upscaler":
                args = {
                    "prompt":    prompt,
                    "image_url": image_url,
                }
                if seed != -1:
                    args["seed"] = seed

            else:  # flux
                args = {
                    "prompt":              prompt,
                    "image_url":           image_url,
                    "strength":            strength,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale":      guidance_scale,
                    "num_images":          num_images,
                }
                if negative_prompt:
                    args["negative_prompt"] = negative_prompt
                if seed != -1:
                    args["seed"] = seed

            print(f"[FAL_ImageToImage] Calling {endpoint} | args: { {k:v for k,v in args.items() if k != 'image_urls'} }")
            t_api = time.time()
            result = run_fal(endpoint, args)
            api_secs = round(time.time() - t_api, 1)
            total_secs = round(time.time() - t_start, 1)
            print(f"[FAL_ImageToImage] Result keys: {list(result.keys())}")

            tensor = parse_images(result) if uses_images else parse_single_image(result)
            n = tensor.shape[0]
            msg = f"Done  {n} image{'s' if n>1 else ''}  |  {api_secs}s API  |  {total_secs}s total"
            print(f"[FAL_ImageToImage] {msg}")
            return {"ui": {"text": [msg]}, "result": (tensor, msg)}

        except Exception as e:
            total_secs = round(time.time() - t_start, 1)
            msg = f"Error after {total_secs}s: {str(e)[:120]}"
            print(f"[FAL_ImageToImage] {msg}")
            return {"ui": {"text": [msg]}, "result": (blank_image(), msg)}


NODE_CLASS_MAPPINGS = {
    "FAL_ImageToImage": FAL_ImageToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_ImageToImage": "FAL Image to Image",
}
