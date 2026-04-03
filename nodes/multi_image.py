"""
FAL Multi-Image Generation Nodes

FAL_MultiPromptImage  - Generate one image per prompt line (batch output).
FAL_MultiImageRefine  - Send multiple input images + one prompt, get refined batch.
"""

import torch
from .fal_utils import run_fal, parse_images, upload_image, blank_image, download_image

BATCH_MODELS = {
    "Flux Schnell (fast)": "fal-ai/flux/schnell",
    "Flux Dev":            "fal-ai/flux/dev",
    "Flux Pro":            "fal-ai/flux-pro",
    "Flux Pro 1.1":        "fal-ai/flux-pro/v1.1",
    "SDXL":                "fal-ai/stable-diffusion-xl",
    "Aura Flow":           "fal-ai/aura-flow",
}

IMAGE_SIZES = [
    "square_hd", "square",
    "portrait_4_3", "portrait_16_9",
    "landscape_4_3", "landscape_16_9",
    "custom",
]


class FAL_MultiPromptImage:
    """
    Generate one image per line of prompts.
    Each line in 'prompts' becomes a separate API call;
    all results are returned as a batched IMAGE tensor.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection":      ("FAL_CONNECTION",),
                "prompts":             ("STRING", {
                    "default": "A cat sitting on a cloud\nA dog on the moon\nA fish flying in the sky",
                    "multiline": True,
                    "placeholder": "One prompt per line",
                }),
                "model":               (list(BATCH_MODELS.keys()), {"default": "Flux Schnell (fast)"}),
                "image_size":          (IMAGE_SIZES, {"default": "landscape_16_9"}),
                "width":               ("INT",   {"default": 1280, "min": 256, "max": 4096, "step": 16}),
                "height":              ("INT",   {"default": 720,  "min": 256, "max": 4096, "step": 16}),
                "num_inference_steps": ("INT",   {"default": 4, "min": 1, "max": 50}),
                "guidance_scale":      ("FLOAT", {"default": 3.5, "min": 1.0, "max": 20.0, "step": 0.1}),
                "seed":                ("INT",   {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "generate"
    CATEGORY = "FAL AI Suite/Image"

    def generate(
        self,
        fal_connection,
        prompts,
        model,
        image_size,
        width,
        height,
        num_inference_steps,
        guidance_scale,
        seed,
    ):
        lines = [p.strip() for p in prompts.splitlines() if p.strip()]
        if not lines:
            return (blank_image(),)

        endpoint = BATCH_MODELS[model]
        all_tensors = []

        for i, prompt in enumerate(lines):
            try:
                print(f"[FAL_MultiPromptImage] Generating {i+1}/{len(lines)}: {prompt[:60]}")
                args = {
                    "prompt": prompt,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "num_images": 1,
                }
                if image_size == "custom":
                    args["image_size"] = {"width": width, "height": height}
                else:
                    args["image_size"] = image_size

                if seed != -1:
                    args["seed"] = seed + i  # different seed per image

                result = run_fal(endpoint, args)
                tensor = parse_images(result)
                all_tensors.append(tensor)
            except Exception as e:
                print(f"[FAL_MultiPromptImage] Error on prompt '{prompt[:40]}': {e}")
                all_tensors.append(blank_image())

        return (torch.cat(all_tensors, dim=0),)


class FAL_MultiImageRefine:
    """
    Feed multiple images (batch) + one prompt through an image-to-image model.
    Each image in the batch is processed separately; results are batched together.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection": ("FAL_CONNECTION",),
                "images":         ("IMAGE",),
                "prompt":         ("STRING", {"default": "", "multiline": True}),
                "strength":       ("FLOAT",  {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01}),
                "num_inference_steps": ("INT", {"default": 28, "min": 1, "max": 100}),
                "guidance_scale":      ("FLOAT", {"default": 3.5, "min": 1.0, "max": 20.0, "step": 0.1}),
                "seed":                ("INT",   {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("refined_images",)
    FUNCTION = "refine"
    CATEGORY = "FAL AI Suite/Image"

    def refine(self, fal_connection, images, prompt, strength, num_inference_steps, guidance_scale, seed):
        endpoint = "fal-ai/flux/dev/image-to-image"
        all_tensors = []

        # images is (B, H, W, C) — iterate over batch
        for i in range(images.shape[0]):
            single = images[i:i+1]
            try:
                print(f"[FAL_MultiImageRefine] Refining image {i+1}/{images.shape[0]}...")
                image_url = upload_image(single)
                args = {
                    "prompt": prompt,
                    "image_url": image_url,
                    "strength": strength,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "num_images": 1,
                }
                if seed != -1:
                    args["seed"] = seed + i
                result = run_fal(endpoint, args)
                all_tensors.append(parse_images(result))
            except Exception as e:
                print(f"[FAL_MultiImageRefine] Error on image {i+1}: {e}")
                all_tensors.append(single)

        return (torch.cat(all_tensors, dim=0),)


NODE_CLASS_MAPPINGS = {
    "FAL_MultiPromptImage": FAL_MultiPromptImage,
    "FAL_MultiImageRefine": FAL_MultiImageRefine,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_MultiPromptImage": "FAL Multi Prompt Image",
    "FAL_MultiImageRefine": "FAL Multi Image Refine",
}
