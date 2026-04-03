"""
FAL Seedream Edit Node
Dedicated node for ByteDance Seedream image editing models.
Shows live status on the node: uploading → calling API → done/error.
"""

import time
import torch
from .fal_utils import run_fal, parse_images, upload_image, blank_image

SEEDREAM_MODELS = {
    "Seedream v5 Lite":  "fal-ai/bytedance/seedream/v5/lite/edit",
    "Seedream v4.5":     "fal-ai/bytedance/seedream/v4.5/edit",
}

# Friendly size presets → (image_size_enum_or_"custom", width, height)
SIZE_PRESETS = {
    "2048×2048  (1:1)":  ("custom", 2048, 2048),
    "1536×2048  (3:4)":  ("custom", 1536, 2048),
    "2048×1536  (4:3)":  ("custom", 2048, 1536),
    "1152×2048  (9:16)": ("custom", 1152, 2048),
    "2048×1152  (16:9)": ("custom", 2048, 1152),
    "1920×2560  (3:4)":  ("custom", 1920, 2560),
    "2560×1920  (4:3)":  ("custom", 2560, 1920),
    "2048×3072  (2:3)":  ("custom", 2048, 3072),
    "3072×2048  (3:2)":  ("custom", 3072, 2048),
    "Auto 2K":           ("auto_2K", None, None),
    "Auto 3K":           ("auto_3K", None, None),
    "Auto 4K":           ("auto_4K", None, None),
    "Custom":            ("custom",  None, None),
}

SEQUENTIAL_OPTIONS = ["disabled", "enabled"]


class FAL_SeedreamEdit:
    """
    ByteDance Seedream image editing node.
    Upload an image, describe your edit, and Seedream rewrites it.
    Status is displayed on the node during and after execution.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection": ("FAL_CONNECTION",),
                "image":          ("IMAGE",),
                "model":          (list(SEEDREAM_MODELS.keys()), {"default": "Seedream v5 Lite"}),
                "prompt":         ("STRING", {"default": "", "multiline": True,
                                              "placeholder": "Describe the edit you want..."}),
                "size_preset":    (list(SIZE_PRESETS.keys()), {"default": "2048×2048  (1:1)"}),
                "width":          ("INT", {"default": 2048, "min": 1024, "max": 4096, "step": 64}),
                "height":         ("INT", {"default": 2048, "min": 1024, "max": 4096, "step": 64}),
                "sequential_image_generation": (SEQUENTIAL_OPTIONS, {"default": "disabled"}),
                "max_images":     ("INT", {"default": 1, "min": 1, "max": 6}),
                "seed":           ("INT", {"default": 0,  "min": 0, "max": 2147483647}),
                "enable_safety_checker": ("BOOLEAN", {
                    "default": True,
                    "label_on": "Safety ON",
                    "label_off": "Safety OFF",
                }),
            },
        }

    RETURN_TYPES  = ("IMAGE", "STRING")
    RETURN_NAMES  = ("images", "status")
    OUTPUT_NODE   = True
    FUNCTION      = "edit"
    CATEGORY      = "FAL AI Suite/Seedream"

    def edit(
        self,
        fal_connection,
        image,
        model,
        prompt,
        size_preset,
        width,
        height,
        sequential_image_generation,
        max_images,
        seed,
        enable_safety_checker,
    ):
        t_start = time.time()

        def status_result(msg, tensor):
            print(f"[FAL_SeedreamEdit] {msg}")
            return {"ui": {"text": [msg]}, "result": (tensor, msg)}

        try:
            # ── Step 1: Upload ─────────────────────────────────────────────
            print("[FAL_SeedreamEdit] Uploading image to fal.ai...")
            t_upload = time.time()
            image_url = upload_image(image)
            upload_secs = round(time.time() - t_upload, 1)
            print(f"[FAL_SeedreamEdit] Upload done in {upload_secs}s")

            # ── Step 2: Resolve size ───────────────────────────────────────
            preset_val, preset_w, preset_h = SIZE_PRESETS[size_preset]
            if preset_val == "custom":
                w = preset_w if preset_w else width
                h = preset_h if preset_h else height
                image_size = {"width": w, "height": h}
                size_label = f"{w}x{h}"
            else:
                image_size = preset_val
                size_label = preset_val

            num_images = max_images if sequential_image_generation == "disabled" else 1

            args = {
                "prompt":                prompt,
                "image_urls":            [image_url],
                "image_size":            image_size,
                "num_images":            num_images,
                "max_images":            max_images,
                "seed":                  seed,
                "enable_safety_checker": enable_safety_checker,
            }

            # ── Step 3: Call API ───────────────────────────────────────────
            endpoint = SEEDREAM_MODELS[model]
            print(f"[FAL_SeedreamEdit] Calling {endpoint} | size={size_label} | max_images={max_images}")
            t_api = time.time()
            result = run_fal(endpoint, args)
            api_secs = round(time.time() - t_api, 1)

            print(f"[FAL_SeedreamEdit] API done in {api_secs}s | keys: {list(result.keys())}")

            # ── Step 4: Parse images ───────────────────────────────────────
            if sequential_image_generation == "enabled" and max_images > 1:
                all_tensors = [parse_images(result)]
                for i in range(max_images - 1):
                    args["seed"] = seed + i + 1
                    r = run_fal(endpoint, args)
                    all_tensors.append(parse_images(r))
                tensor = torch.cat(all_tensors, dim=0)
            else:
                tensor = parse_images(result)

            total_secs = round(time.time() - t_start, 1)
            n_imgs = tensor.shape[0]
            msg = f"Done  {n_imgs} image{'s' if n_imgs>1 else ''}  |  {size_label}  |  {api_secs}s API  |  {total_secs}s total"
            return status_result(msg, tensor)

        except Exception as e:
            total_secs = round(time.time() - t_start, 1)
            msg = f"Error after {total_secs}s: {str(e)[:120]}"
            print(f"[FAL_SeedreamEdit] {msg}")
            return {"ui": {"text": [msg]}, "result": (blank_image(), msg)}


NODE_CLASS_MAPPINGS = {
    "FAL_SeedreamEdit": FAL_SeedreamEdit,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_SeedreamEdit": "FAL Seedream Edit",
}
