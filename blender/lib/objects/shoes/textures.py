"""shoes atlas (512), painted from scratch in GIMP; colours sampled from the capture frames
(wide_20260925_012252_927, 012314_928) and lifted for the dark corner. No logos.

    python blender/lib/textures/gimp_headless.py --object shoes
"""

import random

ATLAS = {
    "name": "shoes",
    "size": 512,
    "regions": {
        "knit_black": (0, 0, 128, 128),
        "knit_side": (128, 0, 128, 128),
        "sole_grey": (256, 0, 128, 128),
        "insole_dark": (384, 0, 128, 128),
        "laces_black": (0, 128, 128, 128),
        "suede_tan": (128, 128, 128, 128),
        "leather_white": (256, 128, 128, 128),
        "sole_white": (384, 128, 128, 128),
        "laces_white": (0, 256, 128, 128),
        "insole_tan": (128, 256, 128, 128),
    },
}

KNIT = (30, 30, 36)
TAN = (176, 138, 96)


def knit(a, region):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), KNIT)
    for j in range(0, h, 3):                                  # knit courses
        fill_rect(a.img, a.lay, (x, y + j, w, 1), (40, 40, 48))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.5)


def laces(a, region, base, lace, eyelet):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    # lace bars run across the shoe (along u = x); ~0.6 in apart (128 px over 17 in)
    for j in range(2, h, 5):
        fill_rect(a.img, a.lay, (x, y + j, w, 2), lace)
    for i in range(0, w, 16):                                 # eyelet rows, faint
        fill_rect(a.img, a.lay, (x + i, y, 1, h), eyelet)
    grain(a.img, a.lay, (x, y, w, h), 0.03, 0.5)


def build():
    random.seed(5)
    a = Atlas(ATLAS)
    knit(a, "knit_black")
    a.material("knit_black", 0.0, 0.12)
    knit(a, "knit_side")
    x, y, w, h = a.rect("knit_side")                          # orange-red flecks low on the sides
    for _ in range(70):
        cx, cy = x + random.uniform(3, w - 3), y + h * random.uniform(0.25, 0.95)
        rw, rh = random.uniform(2, 7), random.uniform(0.8, 2)
        fill_ellipse(a.img, a.lay, (cx - rw, cy - rh, cx + rw, cy + rh),
                     random.choice([(214, 86, 44), (190, 52, 40), (230, 120, 60)]))
    a.material("knit_side", 0.0, 0.12)
    a.fill("sole_grey", (196, 194, 186), 0.0, 0.2, noise=0.03)
    a.fill("insole_dark", (18, 18, 20), 0.0, 0.05)
    laces(a, "laces_black", KNIT, (14, 14, 16), (50, 50, 56))
    a.material("laces_black", 0.0, 0.12)
    a.fill("suede_tan", TAN, 0.0, 0.1, noise=0.06, blur=0.8)
    a.fill("leather_white", (232, 228, 218), 0.0, 0.35, noise=0.02)
    a.fill("sole_white", (226, 222, 212), 0.0, 0.25, noise=0.02)
    laces(a, "laces_white", TAN, (238, 236, 230), (150, 116, 80))
    a.material("laces_white", 0.0, 0.15)
    a.fill("insole_tan", (70, 52, 38), 0.0, 0.05)
    a.save()
