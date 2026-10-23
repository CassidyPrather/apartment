"""bedroom_closet_contents atlas (1024), painted from scratch in GIMP: a grid of flat
colour cells (closet_data.FLAT, picked from photos 19 and 20) and a few pattern regions
for the printed garments, the pine rod, the parasol and the hamper fabric. No text, no
logos anywhere.

    python blender/lib/textures/gimp_headless.py --object bedroom_closet_contents
"""

import math
import os
import random

_G = {}
exec(open(os.path.join(ROOT, "blender", "lib", "objects", "bedroom_closet_contents", "closet_data.py"),
          encoding="utf-8").read(), _G)
ATLAS, FLAT = _G["ATLAS"], _G["FLAT"]
R = random.Random(23)


def soften(a, region, sigma):
    x, y, w, h = a.rect(region)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=sigma, std_dev_y=sigma)
    Gimp.Selection.none(a.img)


def clip_ellipse(a, region, cx, cy, rx, ry, col):
    x0, y0, w, h = a.rect(region)
    box = (max(cx - rx, x0), max(cy - ry, y0), min(cx + rx, x0 + w), min(cy + ry, y0 + h))
    if box[2] > box[0] and box[3] > box[1]:
        fill_ellipse(a.img, a.lay, box, col)


def leaf_spray(a, region, cx, cy, ang, length, col, size=1.0):
    """A thin stem with paired narrow pointed leaves; each leaf is a chain of dots that
    swell and taper along it (fill_ellipse is axis-aligned only)."""
    n = max(3, int(length / (7 * size)))
    for i in range(int(length / 2)):
        t = i / max(int(length / 2) - 1, 1)
        clip_ellipse(a, region, cx + math.cos(ang) * length * t, cy + math.sin(ang) * length * t,
                     0.5 * size, 0.5 * size, col)
    for i in range(1, n):
        t = i / (n - 1)
        px, py = cx + math.cos(ang) * length * t, cy + math.sin(ang) * length * t
        for side in (-1, 1):
            la = ang + side * R.uniform(0.5, 0.8)
            for j, rad in enumerate((0.5, 0.9, 1.1, 1.0, 0.7, 0.35)):
                d = (j + 0.5) * 1.5 * size
                clip_ellipse(a, region, px + math.cos(la) * d, py + math.sin(la) * d,
                             rad * 1.3 * size, rad * 1.3 * size, col)


def build():
    a = Atlas(ATLAS)
    img, lay = a.img, a.lay
    for name, (rgb, metal, smooth) in FLAT.items():
        a.fill(name, rgb, metal, smooth, noise=0.03, blur=1.0)

    # white dress with black leaf sprays (photo 19): cream ground, sprays every ~5 in
    r = "leaf_print"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (230, 227, 220))
    for _ in range(80):
        cx, cy = x0 + R.uniform(0, w), y0 + R.uniform(0, h)
        leaf_spray(a, r, cx, cy, R.uniform(0, 6.28), R.uniform(50, 100),
                   R.choice([(22, 22, 26), (34, 34, 40), (60, 60, 68)]), R.uniform(1.8, 2.4))
    grain(img, lay, (x0, y0, w, h), 0.04, 1.0)
    a.material(r, 0.0, 0.15)

    # long crimson dress with gold glitter swirls low on the skirt
    r = "sequin"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (150, 10, 50))
    grain(img, lay, (x0, y0, w, h), 0.05, 1.0)
    for k in range(3):
        sx, sy = x0 + 25 + k * 35, y0 + h * 0.62 + R.uniform(-20, 20)
        for i in range(60):
            t = i / 60
            px = sx + 14 * math.sin(t * 12) + t * 10
            py = sy + t * 110
            clip_ellipse(a, r, px, py, 1.6, 1.6, R.choice([(222, 176, 70), (240, 206, 110)]))
    a.material(r, 0.3, 0.45)

    # red/black flannel plaid
    r = "plaid"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (160, 22, 36))
    for i in range(0, w, 32):
        fill_rect(img, lay, (x0 + i + 10, y0, 10, h), (30, 20, 24, 0.75))
        fill_rect(img, lay, (x0 + i + 24, y0, 2, h), (220, 210, 200, 0.5))
    for j in range(0, h, 32):
        fill_rect(img, lay, (x0, y0 + j + 10, w, 10), (30, 20, 24, 0.75))
        fill_rect(img, lay, (x0, y0 + j + 24, w, 2), (220, 210, 200, 0.5))
    grain(img, lay, (x0, y0, w, h), 0.05, 1.0)
    a.material(r, 0.0, 0.06)

    # denim: mid blue with faded vertical twill noise and lighter wear down the middle
    r = "denim"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (52, 74, 108))
    for _ in range(30):
        cx, cy = x0 + R.uniform(0, w), y0 + R.uniform(0, h)
        clip_ellipse(a, r, cx, cy, R.uniform(8, 20), R.uniform(20, 50), (86, 112, 148, 0.35))
    grain(img, lay, (x0, y0, w, h), 0.10, 0.8)
    a.material(r, 0.0, 0.08)

    # blue gingham: 4 px checks
    r = "gingham"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (232, 234, 238))
    for i in range(0, w, 8):
        fill_rect(img, lay, (x0 + i, y0, 4, h), (60, 100, 180, 0.6))
    for j in range(0, h, 8):
        fill_rect(img, lay, (x0, y0 + j, w, 4), (60, 100, 180, 0.6))
    a.material(r, 0.0, 0.08)

    # cream shirt with small pink and green flowers
    r = "floral"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (214, 204, 176))
    for _ in range(90):
        cx, cy = x0 + R.uniform(0, w), y0 + R.uniform(0, h)
        clip_ellipse(a, r, cx + 4, cy + 3, 4, 2.5, (110, 140, 90))
        clip_ellipse(a, r, cx, cy, 4, 4, R.choice([(214, 120, 140), (200, 90, 110), (230, 170, 120)]))
    soften(a, r, 0.8)
    a.material(r, 0.0, 0.10)

    # breton stripe: black and white bands
    r = "stripe"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (226, 224, 220))
    for j in range(0, h, 14):
        fill_rect(img, lay, (x0, y0 + j, w, 7), (24, 24, 28))
    a.material(r, 0.0, 0.08)

    # multicolour knit: pink, yellow, teal and black patches
    r = "knit_multi"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (30, 28, 34))
    for _ in range(40):
        clip_ellipse(a, r, x0 + R.uniform(0, w), y0 + R.uniform(0, h), R.uniform(8, 18), R.uniform(5, 10),
                     R.choice([(220, 120, 170), (230, 200, 70), (60, 170, 190), (200, 90, 150)]))
    grain(img, lay, (x0, y0, w, h), 0.08, 1.2)
    a.material(r, 0.0, 0.04)

    # white puffer: horizontal stitch lines between the baffles
    r = "puffer"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (218, 210, 196))
    for j in range(0, h, 26):
        fill_rect(img, lay, (x0, y0 + j, w, 3), (160, 152, 140))
    soften(a, r, 1.5)
    a.material(r, 0.0, 0.30)

    # closed paper parasol: green and tan folds with dark rib lines along v
    r = "umbrella"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (120, 128, 96))
    for i in range(0, w, 16):
        fill_rect(img, lay, (x0 + i, y0, 8, h), (176, 160, 118))
        fill_rect(img, lay, (x0 + i + 14, y0, 2, h), (70, 56, 40))
    grain(img, lay, (x0, y0, w, h), 0.06, 1.0)
    a.material(r, 0.0, 0.15)

    # pine rod: light pine with grain along u
    r = "pine"
    x0, y0, w, h = a.rect(r)
    fill_rect(img, lay, (x0, y0, w, h), (222, 184, 138))
    for _ in range(26):
        yy = y0 + R.uniform(2, h - 4)
        fill_rect(img, lay, (x0, int(yy), w, R.choice([1, 2])), (196, 150, 100, 0.55))
    grain(img, lay, (x0, y0, w, h), 0.05, 1.5)
    a.material(r, 0.0, 0.40)

    # black cap crown: plain (the real caps' white print is left out)
    a.fill("cap_black", (28, 28, 32), 0.0, 0.10, noise=0.05, blur=1.0)

    # grey hamper fabric: fine woven noise
    r = "hamper"
    a.fill(r, (134, 128, 122), 0.0, 0.12, noise=0.08, blur=0.7)
    a.save()
