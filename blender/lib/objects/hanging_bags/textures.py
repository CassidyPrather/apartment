"""hanging_bags atlas (512), painted from scratch in GIMP; colours sampled from the capture
frames (wide_20260925_012131_927) and lifted a little for the dim room.

The tan bag's all-over print is a parody: a from-scratch repeat of little crescent moons
and dots ("Moonpouch"), not the real monogram. No letters, no logo.

    python blender/lib/textures/gimp_headless.py --object hanging_bags
"""

import random

ATLAS = {
    "name": "hanging_bags",
    "size": 512,
    "regions": {
        "black_body": (0, 0, 128, 128),
        "black_trim": (128, 0, 128, 128),
        "webbing": (256, 0, 128, 128),
        "silver": (384, 0, 128, 128),
        "hook_white": (0, 128, 128, 128),
        "cognac": (128, 128, 128, 128),
        "dark_strap": (256, 128, 128, 128),
        "belt_brown": (384, 128, 128, 128),
        "tan_print": (0, 256, 256, 256),
        "braid": (256, 256, 64, 256),
        "lanyard": (320, 256, 64, 256),
        "tan_trim": (384, 256, 128, 128),
    },
}

TAN = (172, 146, 110)
MOTIF = (86, 62, 44)


def mottle(a, region, rgb, n, rmin, rmax, k=(0.9, 1.1), alpha=0.3):
    x, y, w, h = a.rect(region)
    for _ in range(n):
        r = random.uniform(rmin, rmax)
        cx, cy = x + random.uniform(r, w - r), y + random.uniform(r, h - r)
        kk = random.choice(k)
        fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r),
                     tuple(min(255, int(c * kk)) for c in rgb) + (alpha,))


def moon_print(a):
    x0, y0, w, h = a.rect("tan_print")
    fill_rect(a.img, a.lay, (x0, y0, w, h), TAN)
    grain(a.img, a.lay, (x0, y0, w, h), 0.05, 0.7)
    step = 22                               # ~1.3 in repeat on the bag
    for j in range(-1, h // step + 2):
        for i in range(-1, w // step + 2):
            cx = x0 + i * step + (step / 2 if j % 2 else 0)
            cy = y0 + j * step
            if j % 2 == 0:
                # crescent: a dark disc bitten by a tan disc
                r = 6.5
                fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r), MOTIF)
                fill_ellipse(a.img, a.lay, (cx - r + 3.5, cy - r - 1.5, cx + r + 3.5, cy + r - 1.5), TAN)
            else:
                r = 2.6
                fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r), MOTIF)
    # clip the overspill back into the region: repaint neighbours' edges is unnecessary
    # because the region sits at the atlas edge (x0 = 0) and the braid/lanyard strips
    # are painted afterwards.
    a.material("tan_print", 0.0, 0.2)


def braid(a):
    x, y, w, h = a.rect("braid")
    fill_rect(a.img, a.lay, (x, y, w, h), (58, 36, 30))
    for j in range(0, h, 6):                 # chevron plaits, two columns
        for col, shade in ((x + w * 0.3, (104, 62, 48)), (x + w * 0.7, (92, 52, 42))):
            off = 3 if (j // 6) % 2 else 0
            fill_ellipse(a.img, a.lay, (col - 9, y + j + off - 2, col + 9, y + j + off + 3), shade)
    grain(a.img, a.lay, (x, y, w, h), 0.04, 0.8)
    a.material("braid", 0.0, 0.3)


def lanyard(a):
    x, y, w, h = a.rect("lanyard")
    cols = [(92, 120, 196), (236, 236, 240), (226, 120, 150), (120, 180, 220), (60, 70, 140),
            (240, 200, 90)]
    j, k = 0, 0
    while j < h:
        s = random.randint(10, 22)
        fill_rect(a.img, a.lay, (x, y + j, w, min(s, h - j)), cols[k % len(cols)])
        j += s
        k += 1
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.6)
    a.material("lanyard", 0.0, 0.15)


def build():
    random.seed(11)
    a = Atlas(ATLAS)
    moon_print(a)
    a.fill("black_body", (27, 27, 30), 0.0, 0.28, noise=0.05, blur=0.6)          # coated canvas
    mottle(a, "black_body", (27, 27, 30), 12, 8, 24)
    a.fill("black_trim", (20, 20, 22), 0.0, 0.5, noise=0.03)                      # smooth leather
    a.fill("webbing", (28, 29, 33), 0.0, 0.12)
    x, y, w, h = a.rect("webbing")
    for i in range(0, w, 4):                                                       # weave ribs
        fill_rect(a.img, a.lay, (x + i, y, 1, h), (36, 37, 42))
    a.fill("silver", (178, 178, 182), 1.0, 0.7, noise=0.03)
    a.fill("hook_white", (240, 236, 228), 0.0, 0.45, noise=0.02)
    a.fill("cognac", (138, 74, 38), 0.0, 0.62, noise=0.05, blur=1.5)              # glossy leather
    mottle(a, "cognac", (138, 74, 38), 14, 10, 30, k=(0.85, 1.15), alpha=0.35)
    a.fill("dark_strap", (74, 44, 32), 0.0, 0.4, noise=0.05)
    a.fill("belt_brown", (104, 64, 38), 0.0, 0.4, noise=0.05)
    a.fill("tan_trim", (116, 80, 52), 0.0, 0.35, noise=0.05)
    braid(a)
    lanyard(a)
    a.save()
