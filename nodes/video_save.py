"""
FAL Video Save / Preview Nodes

FAL_VideoDownload  - Download a video URL and save to ComfyUI output folder.
FAL_VideoURLPreview - Pass-through node that prints the URL (for wiring).
"""

import os
import requests
import folder_paths
from .text_to_video import _save_video


class FAL_VideoDownload:
    """
    Download a video from a URL and save it to the ComfyUI output folder.
    Useful when you have a video URL from any FAL video node.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url":       ("STRING", {"default": "", "forceInput": True}),
                "filename_prefix": ("STRING", {"default": "fal_video"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "download"
    CATEGORY = "FAL AI Suite/Video"
    OUTPUT_NODE = True

    def download(self, video_url: str, filename_prefix: str):
        if not video_url.strip():
            print("[FAL_VideoDownload] No URL provided.")
            return ("",)
        saved = _save_video(video_url.strip(), filename_prefix)
        return (saved,)


class FAL_VideoURLPreview:
    """
    Displays the video URL in the console and passes it through.
    Useful for debugging or chaining nodes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_url": ("STRING", {"default": "", "forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_url",)
    FUNCTION = "preview"
    CATEGORY = "FAL AI Suite/Video"
    OUTPUT_NODE = True

    def preview(self, video_url: str):
        print(f"[FAL Video URL] {video_url}")
        return {"ui": {"text": [video_url]}, "result": (video_url,)}


NODE_CLASS_MAPPINGS = {
    "FAL_VideoDownload":    FAL_VideoDownload,
    "FAL_VideoURLPreview":  FAL_VideoURLPreview,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_VideoDownload":    "FAL Video Download",
    "FAL_VideoURLPreview":  "FAL Video URL Preview",
}
