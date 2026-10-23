"""Shared data for bedroom_closet_contents: the atlas layout and the flat colour palette.
Pure Python (no bpy, no GIMP), read by object.py (import) and textures.py (exec), so the
regions and colours are defined once.

Colours are sRGB albedo picked from Reference/cupboards_drawers photos 19 (north half) and
20 (south half) at well-lit spots, lifted a little where the photo is in shadow."""

# Flat colours: region name -> (rgb, metallic, smoothness)
FLAT = {
    # closet joinery
    "shelf_white": ((226, 223, 216), 0.0, 0.30),
    "cleat_white": ((216, 213, 206), 0.0, 0.25),
    # hangers
    "hanger_white": ((228, 228, 224), 0.0, 0.45),
    "hanger_teal": ((32, 168, 192), 0.0, 0.45),
    "chrome": ((190, 190, 196), 1.0, 0.70),
    # garments, north half (photo 19), north -> south
    "grey_trousers": ((122, 118, 120), 0.0, 0.10),
    "black": ((24, 24, 27), 0.0, 0.12),
    "black_warm": ((30, 27, 27), 0.0, 0.10),
    "taupe": ((92, 86, 82), 0.0, 0.10),
    "charcoal": ((48, 50, 56), 0.0, 0.12),
    "pink": ((214, 162, 180), 0.0, 0.10),
    "white_shirt": ((222, 220, 214), 0.0, 0.10),
    "navy": ((40, 46, 64), 0.0, 0.10),
    "crimson": ((152, 10, 50), 0.0, 0.18),
    "maroon": ((86, 24, 36), 0.0, 0.08),
    "grey_denim": ((112, 114, 120), 0.0, 0.10),
    "tan_blazer": ((204, 176, 144), 0.0, 0.12),
    "button_black": ((18, 18, 20), 0.0, 0.50),
    "grey_puffy": ((70, 72, 76), 0.0, 0.25),
    "beige_jacket": ((196, 180, 156), 0.0, 0.10),
    # garments, south half (photo 20)
    "cream_jacket": ((200, 194, 184), 0.0, 0.12),
    "puffer_white": ((216, 208, 194), 0.0, 0.30),
    "magenta": ((150, 42, 118), 0.0, 0.10),
    "dark_grey": ((52, 52, 56), 0.0, 0.10),
    "mauve": ((150, 112, 132), 0.0, 0.08),
    "slate_blue": ((54, 66, 90), 0.0, 0.12),
    "light_grey": ((176, 178, 176), 0.0, 0.10),
    "cream_blouse": ((228, 212, 176), 0.0, 0.15),
    "beige_knit": ((198, 162, 140), 0.0, 0.06),
    "grey_tee": ((128, 130, 128), 0.0, 0.08),
    "navy_dark": ((28, 32, 48), 0.0, 0.10),
    "navy_jacket": ((34, 44, 60), 0.0, 0.15),
    # top shelf
    "orange": ((214, 84, 40), 0.0, 0.15),
    "towel_beige": ((190, 166, 132), 0.0, 0.04),
    "leather_brown": ((140, 96, 60), 0.0, 0.35),
    "denim_light": ((128, 156, 186), 0.0, 0.08),
    "fleece_blue": ((126, 150, 174), 0.0, 0.04),
    "grey_fabric": ((112, 110, 112), 0.0, 0.06),
    "red_fabric": ((120, 30, 44), 0.0, 0.08),
    "navy_stripe": ((40, 48, 72), 0.0, 0.08),
    "white_fabric": ((214, 212, 206), 0.0, 0.08),
    "brown_print": ((122, 84, 60), 0.0, 0.10),
    "bamboo": ((206, 178, 126), 0.0, 0.25),
    "cap_white": ((220, 220, 220), 0.0, 0.10),
    # floor
    "shoe_black": ((22, 22, 24), 0.0, 0.35),
    "shoe_brown": ((128, 74, 40), 0.0, 0.40),
    "sneaker_grey": ((120, 124, 130), 0.0, 0.15),
    "sneaker_dark": ((60, 64, 70), 0.0, 0.15),
    "sneaker_pink": ((200, 120, 140), 0.0, 0.15),
    "sole_light": ((200, 198, 192), 0.0, 0.15),
    "hamper_grey": ((134, 128, 122), 0.0, 0.10),
    "hamper_trim": ((168, 164, 158), 0.0, 0.20),
    "hamper_inside": ((60, 58, 56), 0.0, 0.08),
    "jeans_dark": ((38, 50, 72), 0.0, 0.08),
    "plastic_bag": ((200, 214, 222), 0.0, 0.40),
}

CELL = 32
COLS = 1024 // CELL

# Pattern regions (x, y, w, h). Garment prints map u across the garment's width and v
# down its length, so each region's aspect matches its garment.
PRINTS = {
    "leaf_print": (0, 256, 256, 512),      # white dress with black leaf sprays
    "sequin": (256, 256, 128, 384),        # long crimson dress, gold glitter swirls
    "plaid": (384, 256, 128, 256),         # red/black flannel
    "denim": (512, 256, 128, 256),         # mid-blue denim (jacket, jeans)
    "gingham": (640, 256, 128, 256),       # blue/white check shirt
    "floral": (768, 256, 128, 256),        # cream shirt with pink/green flowers
    "stripe": (896, 256, 128, 256),        # black/white breton stripe
    "knit_multi": (384, 512, 128, 128),    # pink/yellow/teal/black knit
    "puffer": (512, 512, 128, 256),        # quilted white puffer (stitch lines)
    "umbrella": (640, 512, 128, 256),      # closed paper parasol, green/beige with ribs
    "pine": (768, 512, 256, 64),           # hanging rod, grain along u
    "cap_black": (768, 576, 128, 128),     # black cap crown (plain, no text)
    "hamper": (896, 576, 128, 128),        # grey woven polyester
}


def regions():
    out = {}
    for i, name in enumerate(FLAT):
        out[name] = ((i % COLS) * CELL, (i // COLS) * CELL, CELL, CELL)
    out.update(PRINTS)
    return out


ATLAS = {"name": "bedroom_closet_contents", "size": 1024, "regions": regions()}
