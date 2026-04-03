"""
FAL Text-to-Video Node
Supports Kling v1/v2, MiniMax, WAN, Hailuo, LTX Video.
Returns a video URL string + saves the video to ComfyUI output folder.
"""

import os
import requests
import folder_paths
from .fal_utils import run_fal, parse_video_url

T2V_MODELS = {
    "Kling v1.5 Standard":  ("fal-ai/kling-video/v1.5/standard/text-to-video", 5),
    "Kling v1.5 Pro":       ("fal-ai/kling-video/v1.5/pro/text-to-video",      10),
    "Kling v2 Standard":    ("fal-ai/kling-video/v2/standard/text-to-video",    5),
    "Kling v2 Pro":         ("fal-ai/kling-video/v2/pro/text-to-video",        10),
    "MiniMax (Hailuo)":     ("fal-ai/minimax/video-01",                         6),
    "WAN Text-to-Video":    ("fal-ai/wan-t2v",                                  5),
    "LTX Video":            ("fal-ai/ltx-video",                                5),
    "Hunyuan Video":        ("fal-ai/hunyuan-video",                            5),
}

DURATIONS = ["5", "10"]
ASPECT_RATIOS = ["16:9", "9:16", "1:1", "4:3", "3:4"]


class FAL_TextToVideo:
    """Generate a video from a text prompt using fal.ai models."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fal_connection": ("FAL_CONNECTION",),
                "model":          (list(T2V_MODELS.keys()), {"default": "Kling v1.5 Standard"}),
                "prompt":         ("STRING", {"default": "", "multiline": True}),
                "duration":       (DURATIONS, {"default": "5"}),
                "aspect_ratio":   (ASPECT_RATIOS, {"default": "16:9"}),
                "save_video":     ("BOOLEAN", {"default": True}),
                "filename_prefix":("STRING",  {"default": "fal_video"}),
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
            endpoint, max_dur = T2V_MODELS[model]
            dur = min(int(duration), max_dur)

            args = {
                "prompt": prompt,
                "duration": str(dur),
                "aspect_ratio": aspect_ratio,
            }

            if negative_prompt:
                args["negative_prompt"] = negative_prompt
            if seed != -1:
                args["seed"] = seed

            print(f"[FAL_TextToVideo] Generating with {model}... (may take 1-3 min)")
            result = run_fal(endpoint, args)
            video_url = parse_video_url(result)

            if not video_url:
                print(f"[FAL_TextToVideo] No video URL in result: {result}")
                return ("", "")

            saved_path = ""
            if save_video and video_url:
                saved_path = _save_video(video_url, filename_prefix)

            return (video_url, saved_path)

        except Exception as e:
            print(f"[FAL_TextToVideo] Error: {e}")
            return ("", "")


def _save_video(url: str, prefix: str) -> str:
    """Download video URL and save to ComfyUI output folder."""
    try:
        output_dir = folder_paths.get_output_directory()
        os.makedirs(output_dir, exist_ok=True)

        # Find next available filename
        idx = 1
        while True:
            ext = url.split("?")[0].rsplit(".", 1)[-1] if "." in url.rsplit("/", 1)[-1] else "mp4"
            filename = f"{prefix}_{idx:04d}.{ext}"
            filepath = os.path.join(output_dir, filename)
            if not os.path.exists(filepath):
                break
            idx += 1

        print(f"[FAL Video] Downloading to {filepath}...")
        resp = requests.get(url, timeout=120, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[FAL Video] Saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"[FAL Video] Save error: {e}")
        return ""


NODE_CLASS_MAPPINGS = {
    "FAL_TextToVideo": FAL_TextToVideo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_TextToVideo": "FAL Text to Video",
}
