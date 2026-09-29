"""plastic_drawers atlas (512): white plastic, a faint clear tint, folded clothes seen
through the drawers, a dark grey-brown board, black nylon, nickel zip pulls, a
blue-grey basket and a plain yellow/orange tissue box (no text).

Wear, from the survey frames: the white plastic has gone slightly cream with faint grey
scuffs; the board's dark top is scratched and dusty (a faint
printed mark on the real board is left out); the nylon bag is crinkled."""

import random

ATLAS = {
    "name": "plastic_drawers",
    "size": 512,
    "regions": {
        "white": (0, 0, 128, 128),
        "clear": (128, 0, 128, 128),
        "clothes": (256, 0, 256, 128),
        "board": (0, 128, 128, 128),
        "bag": (128, 128, 128, 128),
        "zip": (256, 128, 64, 64),
        "caster": (320, 128, 64, 64),
        "tissue": (384, 128, 128, 128),
        "basket": (0, 256, 128, 128),
        "box_lid": (128, 256, 128, 128),
    },
}


def soften(a, rect, sigma):
    x, y, w, h = rect
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=sigma, std_dev_y=sigma)
    Gimp.Selection.none(a.img)


def build():
    random.seed(3)
    a = Atlas(ATLAS)
    a.fill("white", (230, 228, 219), 0.0, 0.5, noise=0.012)
    x, y, w, h = a.rect("white")
    for _ in range(40):                      # faint scuffs
        fill_rect(a.img, a.lay, (x + random.randint(0, w - 20), y + random.randint(0, h - 3),
                                 random.randint(6, 24), random.randint(1, 2)),
                  random.choice([(196, 194, 186, 0.35), (210, 208, 198, 0.4)]))
    for _ in range(18):                      # soft grime blotches
        cx, cy = x + random.randint(0, w), y + random.randint(0, h)
        r = random.randint(4, 12)
        fill_ellipse(a.img, a.lay, (max(cx - r, x), max(cy - r, y), min(cx + r, x + w), min(cy + r, y + h)),
                     (205, 200, 186, 0.25))
    soften(a, (x, y, w, h), 4.0)
    grain(a.img, a.lay, (x, y, w, h), 0.01, 0.8)
    a.fill("clear", (225, 230, 232), 0.0, 0.85)
    x, y, w, h = a.rect("clothes")
    fill_rect(a.img, a.lay, (x, y, w, h), (60, 56, 58))
    for _ in range(50):
        c = random.choice([(30, 30, 34), (90, 70, 72), (120, 60, 70), (70, 80, 100), (150, 140, 130),
                           (200, 196, 190)])
        fill_rect(a.img, a.lay, (x + random.randint(0, w - 30), y + random.randint(0, h - 16),
                                 random.randint(20, 70), random.randint(8, 30)), c)
    grain(a.img, a.lay, (x, y, w, h), 0.05, 2.0)
    a.material("clothes", 0.0, 0.1)
    a.fill("board", (72, 66, 62), 0.0, 0.35, noise=0.02)
    x, y, w, h = a.rect("board")
    for _ in range(26):                      # fine scratches, lighter than the dark top
        L = random.randint(10, 50)
        fill_rect(a.img, a.lay, (x + random.randint(0, w - L), y + random.randint(0, h - 1), L, 1),
                  (98, 92, 88, random.uniform(0.3, 0.6)))
    for _ in range(12):                      # dust / rubbed patches
        cx, cy = x + random.randint(0, w), y + random.randint(0, h)
        r = random.randint(8, 20)
        fill_ellipse(a.img, a.lay, (max(cx - r, x), max(cy - r, y), min(cx + r, x + w), min(cy + r, y + h)),
                     (92, 86, 82, 0.25))
    soften(a, (x, y, w, h), 1.2)
    a.material("board", 0.0, 0.3)
    a.fill("bag", (26, 26, 28), 0.0, 0.3, noise=0.05, blur=1.5)
    x, y, w, h = a.rect("bag")
    for _ in range(30):                      # crinkles in the nylon
        fill_rect(a.img, a.lay, (x + random.randint(0, w - 30), y + random.randint(0, h - 2),
                                 random.randint(10, 40), random.randint(1, 3)),
                  random.choice([(44, 44, 48, 0.6), (16, 16, 18, 0.6)]))
    grain(a.img, a.lay, (x, y, w, h), 0.03, 1.0)
    a.fill("zip", (184, 184, 180), 1.0, 0.55, noise=0.04)
    a.fill("caster", (30, 30, 30), 0.0, 0.3)
    x, y, w, h = a.rect("tissue")
    fill_rect(a.img, a.lay, (x, y, w, h), (236, 196, 90))
    fill_rect(a.img, a.lay, (x, y + h // 2, w, h // 2), (232, 130, 60))
    a.material("tissue", 0.0, 0.3)
    a.fill("basket", (36, 62, 120), 0.0, 0.45, noise=0.02)   # photos: deep royal blue
    a.fill("box_lid", (240, 240, 236), 0.0, 0.55)
    a.save()
