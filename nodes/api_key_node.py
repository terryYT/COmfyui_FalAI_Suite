"""
FAL API Key Node
Stores your fal.ai API key and passes a connection token to all other nodes.
Connect its output (FAL_CONNECTION) to any generation node.
"""

from .fal_utils import set_runtime_key

# Sentinel object passed between nodes to confirm the key is set
class FalConnection:
    def __init__(self, key: str):
        self.key = key

    def __repr__(self):
        return f"<FalConnection key=***{self.key[-4:]}>"


class FAL_APIKey:
    """
    Set your fal.ai API key once and wire it to every generation node.
    Get your key at: https://fal.ai/dashboard/keys
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "fal_key_xxxxxxxxxxxxxxxx",
                }),
            }
        }

    RETURN_TYPES = ("FAL_CONNECTION",)
    RETURN_NAMES = ("fal_connection",)
    FUNCTION = "set_key"
    CATEGORY = "FAL AI Suite"
    OUTPUT_NODE = False

    def set_key(self, api_key: str):
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("FAL API key cannot be empty.")
        set_runtime_key(api_key)
        return (FalConnection(api_key),)


NODE_CLASS_MAPPINGS = {
    "FAL_APIKey": FAL_APIKey,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_APIKey": "FAL API Key",
}
