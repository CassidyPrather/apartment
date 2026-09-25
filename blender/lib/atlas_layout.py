"""Texture atlas layouts shared by the Blender build scripts and the texture generators.

Pure Python (no bpy) so both Blender's interpreter and the system Python can import it.
Rects are in pixels, origin top-left (PIL convention): (x, y, w, h). The Blender side
converts them to UV space with `uv_rect`.
"""

ATLAS_SIZE = {
    "cabinet_hardware": 512,
    "router": 1024,
    "modem": 1024,
    "vr_headset": 1024,
}

# Regions per atlas. "fill" regions are flat colors; everything else is drawn by the
# matching texture generator in blender/lib/textures/.
LAYOUT = {
    "cabinet_hardware": {
        "nickel": (0, 0, 256, 256),
        "blue_anodized": (256, 0, 256, 256),
        "lock_face": (0, 256, 256, 256),
        "guard_plastic": (256, 256, 256, 128),
        "slide_steel": (256, 384, 256, 128),
    },
    "router": {
        "top": (0, 0, 1024, 676),
        "front": (0, 676, 1024, 100),
        "back": (0, 776, 1024, 100),
        "body": (0, 876, 512, 148),
        "antenna": (512, 876, 256, 148),
        "plug_white": (768, 876, 128, 148),
        "cable_black": (896, 876, 128, 148),
    },
    "modem": {
        "side": (0, 0, 512, 660),
        "top_vent": (512, 0, 512, 208),
        "led_panel": (512, 208, 160, 504),
        "port_panel": (672, 208, 160, 504),
        "body": (832, 208, 192, 192),
        "foot": (832, 400, 192, 192),
        "side_b": (0, 660, 512, 364),
    },
    "vr_headset": {
        "visor_front": (0, 0, 1024, 350),
        "visor_top": (0, 350, 1024, 200),
        "strap": (0, 550, 512, 474),
        "foam": (512, 550, 256, 250),
        "badge": (768, 550, 256, 256),
        "cable": (512, 800, 256, 224),
        "dial": (768, 806, 256, 218),
    },
}


def uv_rect(atlas, region, inset=2):
    """Return (u0, v0, u1, v1) in UV space for a region, inset by a few pixels to avoid bleed."""
    size = ATLAS_SIZE[atlas]
    x, y, w, h = LAYOUT[atlas][region]
    u0 = (x + inset) / size
    u1 = (x + w - inset) / size
    v1 = 1.0 - (y + inset) / size
    v0 = 1.0 - (y + h - inset) / size
    return u0, v0, u1, v1
