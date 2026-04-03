"""
ComfyUI FAL AI Suite
A comprehensive fal.ai API node pack for ComfyUI.

Nodes included:
  FAL API Key          — Set your API key, wire to all generation nodes
  FAL Text to Image    — T2I with Flux, SDXL, Aura Flow, Recraft, Ideogram, SANA
  FAL Image to Image   — I2I with Flux Dev/Pro, SDXL, ControlNet Canny/Depth, Upscalers
  FAL Multi Prompt Image   — Generate one image per prompt line (batch)
  FAL Multi Image Refine   — Refine each image in a batch through I2I
  FAL Text to Video    — T2V with Kling v1.5/v2, MiniMax, WAN, LTX, Hunyuan
  FAL Image to Video   — I2V with Kling v1.5/v2, MiniMax, WAN, LTX, SVD
  FAL Image to Video (Start+End Frame) — Kling end-frame animation
  FAL Video Download   — Save any video URL to output folder
  FAL Video URL Preview — Display / pass-through video URL
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
__version__ = "1.0.0"
__author__  = "ComfyUI FAL AI Suite"
