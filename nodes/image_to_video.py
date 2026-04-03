"""
FAL Image-to-Video Node
Animate a still image into a video using fal.ai models.
Supports Kling v1/v2, MiniMax, WAN, Stable Video Diffusion, LTX Video.
"""

import os
import requests
import folder_paths
from .fal_utils import run_fal, parse_video_url, upload_image
from .text_to_video import _save_video

I2V_MODELS = {
    "Kling v1.5 Standard": "fal-ai/kling-video/v1.5/standard/image-to-video",
    "Kling v1.5 Pro":      "fal-ai/kling-video/v1.5/pro/image-to-video",
    "Kling v2 Standard":   "fal-ai/kling-video/v2/standard/image-to-video",
    "Kling v2 Pro":        "fal-ai/kling-video/v2/pro/image-to-video",
    "MiniMax (Hailuo)":    "fal-ai/minimax/video-01-live/image-to-video",
    "WAN Image-to-Video":  "fal-ai/wan-i2v",
    "LTX Video I2V":       "fal-ai/ltx-video/image-to-video",
    "Stable Video Diff.":  "fal-ai/stable-video-diffusion",
}

DURATIONS   = ["5", "10"]
ASPECT_RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4"]


class FAL_ImageToVideo:
    """Animate an image into a video using fal.ai models."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection": ("FAL_CONNECTION",),
                "image":          ("IMAGE",),
                "model":          (list(I2V_MODELS.keys()), {"default": "Kling v1.5 Standard"}),
                "prompt":         ("STRING", {"default": "", "multiline": True}),
                "duration":       (DURATIONS, {"default": "5"}),
                "aspect_ratio":   (ASPECT_RATIOS, {"default": "16:9"}),
                "save_video":     ("BOOLEAN", {"default": True}),
                "filename_prefix":("STRING",  {"default": "fal_i2v"}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "seed":            ("INT",    {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "saved_path")
    FUNCTION = "generate"
    CATEGORY = "FAL AI Suite/Video"
    OUTPUT_NODE = True

    def generate(
        self,
        fal_connection,
        image,
        model,
        prompt,
        duration,
        aspect_ratio,
        save_video,
        filename_prefix,
        negative_prompt="",
        seed=-1,
    ):
        try:
            endpoint = I2V_MODELS[model]

            print(f"[FAL_ImageToVideo] Uploading image...")
            image_url = upload_image(image)

            args = {
                "image_url":    image_url,
                "prompt":       prompt,
                "duration":     duration,
                "aspect_ratio": aspect_ratio,
            }

            if negative_prompt:
                args["negative_prompt"] = negative_prompt
            if seed != -1:
                args["seed"] = seed

            print(f"[FAL_ImageToVideo] Animating with {model}... (may take 1-3 min)")
            result = run_fal(endpoint, args)
            video_url = parse_video_url(result)

            if not video_url:
                print(f"[FAL_ImageToVideo] No video URL in result: {result}")
                return ("", "")

            saved_path = ""
            if save_video and video_url:
                saved_path = _save_video(video_url, filename_prefix)

            return (video_url, saved_path)

        except Exception as e:
            print(f"[FAL_ImageToVideo] Error: {e}")
            return ("", "")


class FAL_ImageToVideoEndFrame:
    """
    Animate between a start image and an end image (supported by some Kling models).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection": ("FAL_CONNECTION",),
                "start_image":    ("IMAGE",),
                "end_image":      ("IMAGE",),
                "prompt":         ("STRING", {"default": "", "multiline": True}),
                "duration":       (DURATIONS, {"default": "5"}),
                "save_video":     ("BOOLEAN", {"default": True}),
                "filename_prefix":("STRING",  {"default": "fal_i2v_endframe"}),
            },
            "optional": {
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_url", "saved_path")
    FUNCTION = "generate"
    CATEGORY = "FAL AI Suite/Video"
    OUTPUT_NODE = True

    def generate(self, fal_connection, start_image, end_image, prompt, duration, save_video, filename_prefix, seed=-1):
        try:
            endpoint = "fal-ai/kling-video/v1.5/pro/image-to-video"

            print("[FAL_ImageToVideoEndFrame] Uploading start + end images...")
            start_url = upload_image(start_image)
            end_url   = upload_image(end_image)

            args = {
                "image_url":     start_url,
                "tail_image_url": end_url,
                "prompt":        prompt,
                "duration":      duration,
            }
            if seed != -1:
                args["seed"] = seed

            print("[FAL_ImageToVideoEndFrame] Generating...")
            result = run_fal(endpoint, args)
            video_url = parse_video_url(result)

            saved_path = _save_video(video_url, filename_prefix) if save_video and video_url else ""
            return (video_url, saved_path)

        except Exception as e:
            print(f"[FAL_ImageToVideoEndFrame] Error: {e}")
            return ("", "")


NODE_CLASS_MAPPINGS = {
    "FAL_ImageToVideo":          FAL_ImageToVideo,
    "FAL_ImageToVideoEndFrame":  FAL_ImageToVideoEndFrame,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_ImageToVideo":          "FAL Image to Video",
    "FAL_ImageToVideoEndFrame":  "FAL Image to Video (Start+End Frame)",
}
