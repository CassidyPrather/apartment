"""plant_broadleaf atlas, painted from scratch in GIMP (no photo pixels): three long
pointed variegated leaves on transparent ground (albedo alpha = cutout; petiole at the
bottom of each region), a dark wicker basket weave, soil and green cane.
Colours matched by eye to the south-window crop.

    python blender/lib/textures/gimp_headless.py --object plant_broadleaf
"""

import math
import random

ATLAS = {
    "name": "plant_broadleaf",
    "size": 1024,
    "regions": {
        "leaf_a": (0, 0, 256, 512),
        "leaf_b": (256, 0, 256, 512),
        "leaf_c": (512, 0, 256, 512),
        "basket": (768, 0, 256, 256),
        "soil": (768, 256, 256, 128),
        "cane": (768, 384, 256, 128),
    },
}
LEAVES = ["leaf_a", "leaf_b", "leaf_c"]
EDGE = (36, 72, 30)
MID = (58, 104, 42)
CREAM = (196, 204, 150)
PALE = (132, 162, 88)


def poly(img, lay, pts, rgb, clip):
    flat = []
    for x, y in pts:
        flat += [float(x), float(y)]
    img.select_polygon(Gimp.ChannelOps.REPLACE, flat)
    cx, cy, cw, ch = clip
    img.select_rectangle(Gimp.ChannelOps.INTERSECT, cx, cy, cw, ch)
    if not Gimp.Selection.is_empty(img):
        Gimp.context_set_foreground(color(tuple(rgb[:3])))
        Gimp.context_set_opacity(100.0 * (rgb[3] if len(rgb) == 4 else 1.0))
        lay.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.context_set_opacity(100.0)
    Gimp.Selection.none(img)


def blade(cx, y0, y1, half_w, scale=1.0, n=14, sway=0.0):
    """Outline of a long pointed leaf from y0 (base, bottom) to y1 (tip, top)."""
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        y = y0 + (y1 - y0) * t
        w = half_w * scale * math.sin(math.pi * min(1.0, t ** 0.7)) ** 0.7
        x = cx + sway * math.sin(math.pi * t)
        left.append((x - w, y))
        right.append((x + w, y))
    return left + list(reversed(right))


def paint_leaf(a, region, variant):
    x, y, w, h = a.rect(region)
    clip = (x + 2, y + 2, w - 4, h - 4)
    cx = x + w / 2
    base = y + h - 2
    pet_top = y + h * (0.74 if variant != 1 else 0.70)
    tip = y + 6
    sway = (-10, 8, 4)[variant]
    # petiole: pale green stalk
    poly(a.img, a.lay, [(cx - 5, base), (cx + 5, base), (cx + 3, pet_top), (cx - 3, pet_top)], (96, 130, 64), clip)
    # blade: dark edge, then mid green, then cream variegation along the midrib
    hw = w * 0.34
    poly(a.img, a.lay, blade(cx, pet_top + 4, tip, hw, 1.0, sway=sway), EDGE, clip)
    poly(a.img, a.lay, blade(cx, pet_top - 4, tip + 12, hw, 0.84, sway=sway), MID, clip)
    # cream blotches: random feathered patches near the midrib
    L = pet_top - tip
    for i in range(60 + variant * 15):
        t = random.uniform(0.08, 0.85)
        yy = pet_top - L * t
        env = math.sin(math.pi * min(1.0, t ** 0.7)) ** 0.7
        spread = hw * 0.55 * env
        xx = cx + sway * math.sin(math.pi * t) + max(-spread, min(spread, random.gauss(0, spread * 0.45)))
        r = random.uniform(3, 9) * (0.6 + env)
        c = CREAM if random.random() < 0.55 else PALE
        ang = random.uniform(-0.6, 0.6)
        pts = [(xx + math.cos(k * 0.785 + ang) * r * (1.0 if k % 2 else 0.6),
                yy + math.sin(k * 0.785 + ang) * r * 1.6) for k in range(8)]
        poly(a.img, a.lay, pts, c + (0.85,), clip)
    # a few dark green speckles over the cream
    for i in range(50):
        t = random.uniform(0.1, 0.85)
        yy = pet_top - L * t
        xx = cx + sway * math.sin(math.pi * t) + max(-0.4 * hw, min(0.4 * hw, random.gauss(0, hw * 0.2)))
        r = random.uniform(1.5, 3.5)
        poly(a.img, a.lay, [(xx - r, yy), (xx, yy - r), (xx + r, yy), (xx, yy + r)], MID, clip)
    # midrib and side veins
    pts = [(cx + sway * math.sin(math.pi * t), pet_top - L * t) for t in [i / 12 for i in range(13)]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        poly(a.img, a.lay, [(x0 - 1.6, y0), (x0 + 1.6, y0), (x1 + 1.0, y1), (x1 - 1.0, y1)], (210, 214, 172), clip)
    a.material(region, 0.0, 0.32)


def build():
    random.seed(3125)
    a = Atlas(ATLAS)
    a.lay.add_alpha()
    for r in LEAVES:
        x, y, w, h = a.rect(r)
        a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
        a.lay.edit_clear()
    Gimp.Selection.none(a.img)
    for i, r in enumerate(LEAVES):
        paint_leaf(a, r, i)
    # Wicker basket: dark reddish-brown weave (rows of offset stakes and strands).
    x, y, w, h = a.rect("basket")
    fill_rect(a.img, a.lay, (x, y, w, h), (74, 42, 26))
    row = 12
    for j in range(0, h, row):
        off = (j // row) % 2 * 8
        for i in range(-16, w, 16):
            if min(w, i + off + 14) - max(0, i + off) < 10:
                continue
            fill_round_rect(a.img, a.lay, (x + max(0, i + off), y + j + 1, x + min(w, i + off + 14), y + j + row - 1),
                            4, (118, 70, 42) if random.random() < 0.8 else (132, 82, 50))
    fill_rect(a.img, a.lay, (x, y, w, 18), (96, 56, 34))
    grain(a.img, a.lay, (x, y, w, h), 0.08, 0.8)
    a.material("basket", 0.0, 0.12)
    a.fill("soil", (52, 40, 32), 0.0, 0.05, noise=0.12)
    a.fill("cane", (104, 132, 70), 0.0, 0.2, noise=0.04)
    a.save()
