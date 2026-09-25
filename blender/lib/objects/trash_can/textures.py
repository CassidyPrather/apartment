"""trash_can atlas (512), painted from scratch in GIMP: vertically brushed dark
stainless (the photos show a warm grey 'champagne' steel), a slightly lighter lid,
black plastic trim and the pedal steel.

    python blender/lib/textures/gimp_headless.py --object trash_can
"""

import random

ATLAS = {
    "name": "trash_can",
    "size": 512,
    "regions": {
        "steel": (0, 0, 256, 512),
        "lid": (256, 0, 256, 256),
        "plastic": (256, 256, 256, 128),
        "pedal": (256, 384, 256, 128),
    },
}


def brushed(a, region, base, metal, smooth):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    for _ in range(90):
        sx = x + random.randint(0, w - 2)
        k = random.uniform(-0.03, 0.03)
        c = tuple(max(0, min(255, round(v * (1 + k)))) for v in base)
        fill_rect(a.img, a.lay, (sx, y, random.randint(1, 3), h), c + (0.7,))
    grain(a.img, a.lay, (x, y, w, h), 0.02, 0.6)
    a.material(region, metal, smooth)


def build():
    random.seed(1221)
    a = Atlas(ATLAS)
    brushed(a, "steel", (128, 124, 118), 0.85, 0.6)
    brushed(a, "lid", (140, 136, 130), 0.85, 0.65)
    a.fill("plastic", (26, 26, 27), 0.0, 0.3, noise=0.02)
    brushed(a, "pedal", (150, 148, 144), 0.9, 0.6)
    a.save()
