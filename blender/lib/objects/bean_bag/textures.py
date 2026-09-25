"""bean_bag atlas (512), painted from scratch in GIMP: brushed brown suede (soft
mottling, a few creases) and the beige patterned base panel. Colours matched by eye to
the south-window crop.

    python blender/lib/textures/gimp_headless.py --object bean_bag
"""

import random

ATLAS = {
    "name": "bean_bag",
    "size": 512,
    "regions": {
        "suede": (0, 0, 512, 320),
        "panel": (0, 320, 512, 192),
    },
}


def build():
    random.seed(2524)
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("suede")
    fill_rect(a.img, a.lay, (x, y, w, h), (94, 74, 46))
    for _ in range(40):
        cx, cy, r = x + random.uniform(0, w), y + random.uniform(0, h), random.uniform(20, 70)
        c = random.choice([(108, 86, 54), (80, 62, 38), (100, 82, 50)])
        fill_ellipse(a.img, a.lay, (cx - r, cy - r * 0.6, cx + r, cy + r * 0.6), c + (0.35,))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=14.0, std_dev_y=14.0)
    Gimp.Selection.none(a.img)
    for _ in range(9):
        cx, cy = x + random.uniform(20, w - 60), y + random.uniform(20, h - 20)
        fill_ellipse(a.img, a.lay, (cx, cy, cx + random.uniform(40, 110), cy + 5), (76, 56, 36, 0.5))
    grain(a.img, a.lay, (x, y, w, h), 0.04, 1.0)
    a.material("suede", 0.0, 0.12)
    # Base panel: beige with a soft darker leaf-like print.
    x, y, w, h = a.rect("panel")
    fill_rect(a.img, a.lay, (x, y, w, h), (176, 164, 128))
    for _ in range(70):
        cx, cy, r = x + random.uniform(0, w), y + random.uniform(0, h), random.uniform(6, 16)
        fill_ellipse(a.img, a.lay, (cx - r, cy - r * 0.5, cx + r, cy + r * 0.5), (140, 128, 96, 0.6))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 1.0)
    a.material("panel", 0.0, 0.1)
    a.save()
