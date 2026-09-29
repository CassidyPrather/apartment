"""Shared "doors" atlas (512 px) for every door_* package: flat finishes, plus the "leaf"
region that doorkit.leaf_uvs() maps over each whole leaf (u from the hinge/far edge to the
handle edge, v from the leaf bottom to its top) with the wear seen in the photos: faint hand
smudges around the handle (IMG_1523, IMG_1498) and scuffs and small dings along the bottom
(IMG_1523 lower rail, living frame 48). Runs inside headless GIMP via
gimp_headless.py --object door_bedroom (other door packages exec this file)."""

import random

ATLAS = {
    "name": "doors",
    "size": 512,
    "regions": {
        "paint": (0, 0, 256, 256),
        "nickel": (256, 0, 128, 128),
        "bronze": (384, 0, 128, 128),
        "vinyl": (256, 128, 128, 128),
        "dark": (384, 128, 128, 128),
        "glass": (0, 256, 128, 128),
        "aluminum": (128, 256, 128, 128),
        "leaf": (256, 256, 256, 256),
        "brass": (0, 384, 128, 128),
        "slat": (128, 384, 64, 128),
        "lite": (192, 384, 64, 128),
    },
}

PAINT = (234, 233, 228)
HANDLE_V = (36.0 - 0.75) / 78.6      # handle centre height as a fraction of the leaf


def leaf_wear(a):
    """Paint + wear over the leaf region. (u, v) -> pixel: x + u*w, y + (1 - v)*h."""
    x, y, w, h = a.rect("leaf")
    rnd = random.Random(7)
    px = lambda u: x + u * w                                    # noqa: E731
    py = lambda v: y + (1.0 - v) * h                            # noqa: E731
    a.fill("leaf", PAINT, 0.0, 0.55, noise=0.015, blur=1.5)
    # hand smudges: many faint soft blots clustered around the handle edge at handle height,
    # a little more above it (where a hand pushes) than below
    for i in range(90):
        du = abs(rnd.gauss(0.0, 0.06))
        dv = rnd.gauss(0.03, 0.065)
        u, v = min(0.995, 0.95 - du * 0.9 + rnd.uniform(-0.02, 0.04)), HANDLE_V + dv
        r = rnd.uniform(3.0, 8.0)
        fill_ellipse(a.img, a.lay, (px(u) - r, py(v) - r * 1.3, px(u) + r, py(v) + r * 1.3),
                     (140, 132, 118, 0.022))
    # scuffs along the bottom: short horizontal streaks and a faint grey band (shoes, mop)
    for i in range(34):
        u, v = rnd.uniform(0.05, 0.99), abs(rnd.gauss(0.0, 0.035)) + 0.004
        ln, th = rnd.uniform(3.0, 16.0), rnd.choice((1, 1, 2))
        fill_rect(a.img, a.lay, (round(px(u) - ln / 2), round(py(v)), round(ln), th),
                  (118, 112, 102, rnd.uniform(0.07, 0.16)))
    fill_rect(a.img, a.lay, (x, round(py(0.03)), w, round(0.03 * h)), (150, 144, 134, 0.06))
    # soften the smudges and scuffs, then the dings stay crisp on top
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x + 2, y + 2, w - 4, h - 4)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=2.2, std_dev_y=2.2)
    Gimp.Selection.none(a.img)
    for i in range(16):
        u, v = rnd.uniform(0.15, 0.97), rnd.uniform(0.02, 0.32)
        fill_rect(a.img, a.lay, (round(px(u)), round(py(v)), 1, 1), (96, 90, 84, 0.45))


def build():
    a = Atlas(ATLAS)
    a.fill("paint", PAINT, 0.0, 0.55, noise=0.015, blur=1.5)     # semi-gloss white
    x, y, w, h = a.rect("nickel")
    a.fill("nickel", (172, 170, 164), 1.0, 0.55, noise=0.08, blur=0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=30.0, angle=0.0)                 # brushed streaks
    Gimp.Selection.none(a.img)
    a.fill("bronze", (72, 68, 64), 0.85, 0.5, noise=0.04, blur=0)          # dark lever set
    a.fill("vinyl", (228, 228, 222), 0.0, 0.4, noise=0.01)
    a.fill("dark", (38, 38, 38), 0.0, 0.2)
    a.fill("glass", (196, 212, 212), 0.0, 0.92)
    a.fill("aluminum", (190, 192, 194), 0.9, 0.5, noise=0.03)
    a.fill("brass", (212, 184, 118), 1.0, 0.78, noise=0.03, blur=0.5)       # polished brass
    a.fill("slat", (238, 236, 229), 0.0, 0.35, noise=0.01)                 # white 2 in slats
    a.fill("lite", (62, 72, 80), 0.0, 0.9)                                 # dark glass
    leaf_wear(a)
    a.save()
