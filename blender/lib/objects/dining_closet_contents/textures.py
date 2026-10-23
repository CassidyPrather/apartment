"""dining_closet_contents atlas (1024): what's stored in the small closet off the dining
room (photo 16 of the 2026-10-23 cupboards set). Painted from scratch, no photo pixels,
no text:
  - the game map draped over the shelf: a made-up landmass (a long ragged continent of
    ochre, olive and dark-green patches on a dark slate sea, pale region lines, small
    white town marks, a misty pale band along the bottom) inside a mottled pale frame,
    with a red top band edged in gold. Not a copy of any real map.
  - a grey paisley-ish throw, the orange duffel's end (black centre band, blank black
    patch where the logo was, grey handles), the fan grille (white rings and spokes)
  - a 64 px swatch per flat colour.
Runs inside headless GIMP with the gimp_textures helpers in scope; the top level is
plain Python so object.py can read ATLAS from this file.
"""

import math
import random

SWATCHES = [
    ("shelf_paint", (224, 222, 216), 0.0, 0.35), ("toolbox_red", (188, 28, 30), 0.3, 0.65),
    ("chrome", (205, 205, 210), 1.0, 0.75), ("fan_white", (232, 232, 226), 0.0, 0.45),
    ("handvac_white", (236, 236, 236), 0.0, 0.55), ("handvac_teal", (62, 132, 172), 0.0, 0.6),
    ("handvac_black", (26, 26, 28), 0.0, 0.5), ("charger_grey", (58, 58, 62), 0.0, 0.4),
    ("mop_grey", (150, 156, 164), 0.3, 0.5), ("mop_black", (30, 30, 32), 0.0, 0.4),
    ("vac_dark", (44, 44, 48), 0.0, 0.4), ("vac_cup", (84, 76, 98), 0.0, 0.75),
    ("vac_purple", (108, 58, 150), 0.0, 0.55), ("vac_black", (22, 22, 24), 0.0, 0.35),
    ("cloth_black", (28, 28, 30), 0.0, 0.1), ("cleaner_green", (156, 176, 132), 0.0, 0.45),
    ("cleaner_lime", (156, 200, 84), 0.0, 0.5), ("cleaner_white", (226, 232, 226), 0.0, 0.7),
    ("cleaner_hose", (128, 170, 94), 0.0, 0.45), ("pole_black", (22, 22, 22), 0.0, 0.5),
    ("red_plastic", (212, 32, 52), 0.0, 0.6), ("pink_cloth", (212, 156, 176), 0.0, 0.05),
    ("duffel_orange", (234, 98, 42), 0.0, 0.2), ("strap_grey", (118, 118, 122), 0.0, 0.2),
    ("map_back", (70, 64, 58), 0.0, 0.2), ("map_red", (180, 40, 36), 0.0, 0.25),
]

BIG = {
    "map": (0, 0, 768, 512),
    "duffel_end": (768, 0, 256, 256),
    "throw": (768, 256, 256, 256),
    "fan_grille": (0, 512, 192, 192),
}


def _regions():
    r = dict(BIG)
    for i, (name, _, _, _) in enumerate(SWATCHES):
        r[name] = ((i % 16) * 64, 704 + (i // 16) * 64, 64, 64)
    return r


ATLAS = {"name": "dining_closet_contents", "size": 1024, "regions": _regions()}


def blobs(a, rng, cx, cy, n, rx, ry, spread_x, spread_y, col, clip):
    x0, y0, x1, y1 = clip
    for _ in range(n):
        px = cx + rng.gauss(0, spread_x)
        py = cy + rng.gauss(0, spread_y)
        w, h = rng.uniform(0.5, 1.0) * rx, rng.uniform(0.5, 1.0) * ry
        e = (max(x0, int(px - w)), max(y0, int(py - h)), min(x1, int(px + w)), min(y1, int(py + h)))
        if e[2] > e[0] + 2 and e[3] > e[1] + 2:
            fill_ellipse(a.img, a.lay, e, col)


def paint_map(a, rng):
    x, y, w, h = a.rect("map")
    # mottled pale frame
    fill_rect(a.img, a.lay, (x, y, w, h), (150, 166, 168))
    grain(a.img, a.lay, (x, y, w, h), 0.3, 1.5)
    # red top band with gold edges and two gold chevrons
    band = 50
    fill_rect(a.img, a.lay, (x, y, w, band), (176, 40, 36))
    fill_rect(a.img, a.lay, (x, y, w, 4), (214, 176, 70))
    fill_rect(a.img, a.lay, (x, y + band - 6, w, 6), (214, 176, 70))
    for cx in (x + 180, x + 520):
        for i in range(16):
            fill_rect(a.img, a.lay, (cx - 16 + i, y + band - 22 + i, 32 - 2 * i, 2), (214, 176, 70))
    # sea
    sx0, sy0, sx1, sy1 = x + 26, y + band + 18, x + w - 26, y + h - 22
    fill_rect(a.img, a.lay, (sx0, sy0, sx1 - sx0, sy1 - sy0), (40, 54, 66))
    grain(a.img, a.lay, (sx0, sy0, sx1 - sx0, sy1 - sy0), 0.2, 2.0)
    fill_rect(a.img, a.lay, (sx0 - 4, sy0 - 4, sx1 - sx0 + 8, 2), (210, 214, 210))
    fill_rect(a.img, a.lay, (sx0 - 4, sy1 + 2, sx1 - sx0 + 8, 2), (210, 214, 210))
    fill_rect(a.img, a.lay, (sx0 - 4, sy0 - 4, 2, sy1 - sy0 + 8), (210, 214, 210))
    fill_rect(a.img, a.lay, (sx1 + 2, sy0 - 4, 2, sy1 - sy0 + 8), (210, 214, 210))
    clip = (sx0, sy0, sx1, sy1)
    # one big ragged continent filling most of the sheet: two wandering spines of large
    # soft blobs, the sea showing along the top and in the upper-left corner
    spines = []
    for yb in (0.42, 0.66):
        px, py = sx0 + 70, sy0 + (sy1 - sy0) * yb
        while px < sx1 - 30:
            spines.append((px, py))
            px += rng.uniform(16, 26)
            py = min(sy1 - 60, max(sy0 + 80, py + rng.uniform(-10, 10)))
    for px, py in spines:
        blobs(a, rng, px, py, 3, 70, 58, 18, 24, (80, 98, 72), clip)               # green-grey land
    for px, py in spines[::2]:
        blobs(a, rng, px, py, 2, 46, 40, 24, 24, (50, 66, 50, 0.7), clip)           # dark forest
    for px, py in spines[1::3]:
        blobs(a, rng, px, py - 20, 2, 40, 30, 20, 16, (100, 126, 78, 0.75), clip)    # green
    for px, py in spines:
        f = (px - sx0) / (sx1 - sx0)
        if (f < 0.5 and py > sy0 + (sy1 - sy0) * 0.5) or (0.6 < f < 0.85 and rng.random() < 0.5):
            blobs(a, rng, px, py + 10, 2, 36, 26, 16, 12, (170, 142, 86, 0.85), clip)  # ochre lowlands
    for _ in range(40):
        px, py = rng.choice(spines)
        blobs(a, rng, px, py, 1, 14, 12, 10, 10, (96, 90, 74, 0.6), clip)              # hills
    for _ in range(6):
        ix, iy = rng.uniform(sx0 + 30, sx0 + 260), rng.uniform(sy0 + 14, sy0 + 50)
        blobs(a, rng, ix, iy, 3, 12, 8, 8, 5, (70, 84, 64), clip)
    grain(a.img, a.lay, (sx0, sy0, sx1 - sx0, sy1 - sy0), 0.18, 1.2)
    pts = spines
    # pale region lines wandering over the land
    for _ in range(30):
        px, py = rng.choice(pts)
        ang = rng.uniform(0, 2 * math.pi)
        for _ in range(40):
            ang += rng.uniform(-0.5, 0.5)
            px += 3 * math.cos(ang)
            py += 3 * math.sin(ang)
            if sx0 < px < sx1 - 3 and sy0 < py < sy1 - 3:
                fill_rect(a.img, a.lay, (int(px), int(py), 2, 2), (150, 184, 196))
    # town marks: little white squares with dark centres
    for _ in range(40):
        px, py = rng.choice(pts)
        px, py = int(px + rng.uniform(-30, 30)), int(py + rng.uniform(-50, 70))
        if sx0 < px < sx1 - 8 and sy0 < py < sy1 - 10:
            fill_rect(a.img, a.lay, (px, py, 5, 6), (228, 228, 222))
            fill_rect(a.img, a.lay, (px + 1, py + 1, 3, 3), (50, 50, 50))
    # misty pale band along the bottom with dark speckled trees
    my0 = sy1 - 70
    for i in range(70):
        al = 0.6 * i / 70
        fill_rect(a.img, a.lay, (sx0, my0 + i, sx1 - sx0, 1), (186, 196, 198, al))
    for _ in range(500):
        px, py = rng.uniform(sx0, sx1 - 3), rng.uniform(my0 + 20, sy1 - 3)
        fill_rect(a.img, a.lay, (int(px), int(py), 2, 3), (60, 70, 72))
    a.material("map", 0.0, 0.3)


def build():
    rng = random.Random(16)
    a = Atlas(ATLAS)
    for name, rgb, met, sm in SWATCHES:
        a.fill(name, rgb, met, sm, noise=0.012)
    paint_map(a, rng)

    # throw: grey-white with darker grey paisley-ish swirls, a few pink/purple flecks
    x, y, w, h = a.rect("throw")
    fill_rect(a.img, a.lay, (x, y, w, h), (196, 198, 198))
    for _ in range(40):
        px, py = rng.randint(x, x + w - 30), rng.randint(y, y + h - 30)
        r = rng.randint(10, 22)
        fill_ellipse(a.img, a.lay, (px, py, px + r * 2, py + int(r * 1.4)), (92, 98, 106))
        fill_ellipse(a.img, a.lay, (px + 5, py + 4, px + r * 2 - 6, py + int(r * 1.4) - 5), (176, 180, 184))
        fill_ellipse(a.img, a.lay, (px + r - 3, py + 6, px + r + 4, py + 13), (92, 98, 106))
    for _ in range(25):
        px, py = rng.randint(x, x + w - 8), rng.randint(y, y + h - 8)
        fill_rect(a.img, a.lay, (px, py, 6, 6), rng.choice([(206, 140, 170), (150, 110, 170)]))
    grain(a.img, a.lay, (x, y, w, h), 0.08, 1.0)
    a.material("throw", 0.0, 0.03)

    # duffel end: orange, black centre band, a blank black patch, grey handles
    x, y, w, h = a.rect("duffel_end")
    fill_rect(a.img, a.lay, (x, y, w, h), (234, 98, 42))
    fill_rect(a.img, a.lay, (x + int(w * 0.38), y + int(h * 0.3), int(w * 0.24), int(h * 0.7)), (28, 28, 30))
    fill_rect(a.img, a.lay, (x + int(w * 0.40), y + 22, int(w * 0.2), 44), (20, 20, 22))
    fill_rect(a.img, a.lay, (x + int(w * 0.43), y + 34, int(w * 0.14), 10), (150, 40, 40))   # no letters
    for gx in (0.22, 0.72):
        fill_rect(a.img, a.lay, (x + int(w * gx), y + 30, 14, int(h * 0.4)), (118, 118, 122))
    fill_rect(a.img, a.lay, (x + int(w * 0.22), y + int(h * 0.5), int(w * 0.5) + 14, 12), (118, 118, 122))
    fill_rect(a.img, a.lay, (x + int(w * 0.49), y + int(h * 0.52), 4, int(h * 0.3)), (190, 190, 190))
    for e in ((x, y, w, 6), (x, y + h - 6, w, 6), (x, y, 6, h), (x + w - 6, y, 6, h)):
        fill_rect(a.img, a.lay, e, (30, 30, 32))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 1.0)
    a.material("duffel_end", 0.0, 0.2)

    # fan grille: white rings and spokes over a dark see-through look, blank centre badge
    x, y, w, h = a.rect("fan_grille")
    cx, cy = x + w // 2, y + h // 2
    fill_rect(a.img, a.lay, (x, y, w, h), (232, 232, 226))
    R = w // 2 - 2
    fill_ellipse(a.img, a.lay, (cx - R, cy - R, cx + R, cy + R), (232, 232, 226))
    fill_ellipse(a.img, a.lay, (cx - R + 4, cy - R + 4, cx + R - 4, cy + R - 4), (96, 96, 98))
    for r in range(R - 14, 30, -14):
        fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r), (226, 226, 222))
        fill_ellipse(a.img, a.lay, (cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), (96, 96, 98))
    for k in range(48):
        ang = 2 * math.pi * k / 48
        for s in range(32, R - 4, 3):
            fill_rect(a.img, a.lay, (int(cx + s * math.cos(ang)), int(cy + s * math.sin(ang)), 2, 2),
                      (226, 226, 222))
    fill_ellipse(a.img, a.lay, (cx - 30, cy - 30, cx + 30, cy + 30), (236, 236, 232))
    a.material("fan_grille", 0.0, 0.45)
    a.save()
