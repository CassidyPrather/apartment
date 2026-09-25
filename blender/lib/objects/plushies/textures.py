"""plushies atlas (512): one soft plush-fabric swatch per colour, painted from scratch in
GIMP (flat colour, fine fuzz grain, a soft mottle). Colours matched by eye to the bedroom
photos.

    python blender/lib/textures/gimp_headless.py --object plushies
"""

import random

COLOURS = {
    "green": (78, 122, 48), "green_light": (140, 176, 84), "red": (190, 58, 46), "black": (22, 22, 24),
    "dark": (52, 52, 58), "white": (232, 230, 224), "cream": (214, 202, 172), "grey": (140, 140, 146),
    "pink": (238, 164, 184), "purple": (160, 128, 214), "yellow": (246, 214, 90), "orange": (238, 136, 44),
}
ATLAS = {
    "name": "plushies",
    "size": 512,
    "regions": {name: ((i % 4) * 128, (i // 4) * 128, 128, 128) for i, name in enumerate(COLOURS)},
}


def build():
    random.seed(7)
    a = Atlas(ATLAS)
    for name, rgb in COLOURS.items():
        x, y, w, h = a.rect(name)
        fill_rect(a.img, a.lay, (x, y, w, h), rgb)
        for _ in range(10):                                   # soft mottle
            cx, cy, r = x + random.uniform(0, w), y + random.uniform(0, h), random.uniform(10, 30)
            k = random.choice((0.92, 1.06))
            fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r),
                         tuple(min(255, int(c * k)) for c in rgb) + (0.35,))
        grain(a.img, a.lay, (x, y, w, h), 0.06, 0.6)          # plush fuzz
        a.material(name, 0.0, 0.08)
    a.save()
