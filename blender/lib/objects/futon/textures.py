"""futon atlas (256): the coffee-coloured cover, a soft brushed microfibre painted from
scratch in GIMP (flat colour, a fine grain and a faint mottle). Colour matched to the
listing's "coffee".

    python blender/lib/textures/gimp_headless.py --object futon
"""

import random

COFFEE = (102, 72, 52)
ATLAS = {
    "name": "futon",
    "size": 256,
    "regions": {"coffee": (0, 0, 256, 256)},
}


def build():
    random.seed(11)
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("coffee")
    fill_rect(a.img, a.lay, (x, y, w, h), COFFEE)
    for _ in range(14):                                       # faint mottle
        cx, cy, r = x + random.uniform(0, w), y + random.uniform(0, h), random.uniform(16, 48)
        k = random.choice((0.94, 1.05))
        fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r),
                     tuple(min(255, int(c * k)) for c in COFFEE) + (0.3,))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.6)              # brushed microfibre
    a.material("coffee", 0.0, 0.12)
    a.save()
