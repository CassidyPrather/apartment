"""Exterior view textures, painted from scratch (no photos: the view must identify
nothing). Runs inside headless GIMP with the gimp_textures helpers in scope.

exterior_view (1024): painted sky backdrop (gradient, soft clouds, a hazy distant
treeline at the horizon), cutout tree and shrub cards (albedo alpha), a board fence
panel, a plain two-storey siding facade, roof shingles, and concrete. The emission map
carries the sky only. exterior_ground (1024): a seamless lawn tile.
"""

import math
import random

ATLAS = {
    "name": "exterior_view",
    "size": 1024,
    "regions": {
        "sky": (0, 0, 1024, 512),
        "tree_a": (0, 512, 256, 384),
        "tree_b": (256, 512, 256, 384),
        "tree_c": (512, 512, 256, 384),
        "shrub_a": (768, 512, 256, 192),
        "shrub_b": (768, 704, 256, 192),
        "fence": (0, 896, 256, 128),
        "facade": (256, 896, 256, 128),
        "roof": (512, 896, 128, 128),
        "path": (640, 896, 128, 128),
        "patio": (768, 896, 128, 128),
        "wall_plain": (896, 896, 128, 128),
    },
}
FOLIAGE = ["tree_a", "tree_b", "tree_c", "shrub_a", "shrub_b"]
SKY_Z = (-300.0, 1800.0)           # must match object.py
HORIZON_ROW = round(512 * SKY_Z[1] / (SKY_Z[1] - SKY_Z[0]))


def lerp(c0, c1, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))


def jitter(c, amt):
    k = random.uniform(-amt, amt)
    return tuple(max(0, min(255, round(v * (1 + k)))) for v in c)


def ellipse(img, lay, box, rgb, clip):
    """fill_ellipse clipped to `clip` (x, y, w, h); skipped when empty, because GIMP
    fills the whole layer when a selection comes out empty."""
    cx, cy, cw, ch = clip
    x0, y0 = max(box[0], cx), max(box[1], cy)
    x1, y1 = min(box[2], cx + cw), min(box[3], cy + ch)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    img.select_ellipse(Gimp.ChannelOps.REPLACE, box[0], box[1], box[2] - box[0], box[3] - box[1])
    img.select_rectangle(Gimp.ChannelOps.INTERSECT, x0, y0, x1 - x0, y1 - y0)
    if Gimp.Selection.is_empty(img):
        return
    Gimp.context_set_foreground(color(tuple(rgb[:3])))
    Gimp.context_set_opacity(100.0 * (rgb[3] if len(rgb) == 4 else 1.0))
    lay.edit_fill(Gimp.FillType.FOREGROUND)
    Gimp.context_set_opacity(100.0)
    Gimp.Selection.none(img)


def new_rgba_layer(img, name):
    lay = Gimp.Layer.new(img, name, img.get_width(), img.get_height(),
                         Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
    img.insert_layer(lay, None, 0)
    lay.fill(Gimp.FillType.TRANSPARENT)
    return lay


def paint_sky(a):
    x, y, w, h = a.rect("sky")
    top, hor = (78, 128, 196), (204, 220, 232)
    band = 4
    for r in range(0, HORIZON_ROW + band, band):
        t = min(1.0, r / HORIZON_ROW) ** 1.6
        fill_rect(a.img, a.lay, (x, y + r, w, band), lerp(top, hor, t))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, HORIZON_ROW)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=3.0, std_dev_y=3.0)
    Gimp.Selection.none(a.img)
    # Soft cumulus: overlapping translucent white blobs, then blurred with the sky.
    for i in range(9):
        cx = x + 50 + i * 110 + random.randint(-30, 30)
        cy = y + random.randint(110, 330)
        size = random.uniform(0.6, 1.3)
        for _ in range(16):
            rx = random.uniform(18, 46) * size
            ry = rx * random.uniform(0.45, 0.7)
            ox = random.gauss(0, 45 * size)
            oy = random.gauss(0, 10 * size) - abs(ox) * 0.08
            shade = random.choice([(255, 255, 255), (246, 248, 252), (236, 240, 247)])
            ellipse(a.img, a.lay, (cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry), shade + (0.35,), (x, y, w, HORIZON_ROW))
        ellipse(a.img, a.lay, (cx - 70 * size, cy + 4, cx + 70 * size, cy + 16 * size), (222, 228, 238, 0.3), (x, y, w, HORIZON_ROW))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, HORIZON_ROW - 20)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=8.0, std_dev_y=6.0)
    Gimp.Selection.none(a.img)
    # Hazy distant treeline sitting on the horizon, then hazy lawn below it.
    for i in range(160):
        cx = x + random.uniform(0, w)
        r = random.uniform(8, 22)
        cy = y + HORIZON_ROW - random.uniform(4, 30)
        ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, y + HORIZON_ROW + 2),
                jitter((104, 132, 118), 0.06), (x, y, w, h))
    fill_rect(a.img, a.lay, (x, y + HORIZON_ROW, w, h - HORIZON_ROW), (112, 134, 88))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y + HORIZON_ROW - 40, w, h - HORIZON_ROW + 40)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=1.5, std_dev_y=1.5)
    Gimp.Selection.none(a.img)
    a.material("sky", 0.0, 0.0)


def blobs(a, rect, cx, cy, rw, rh, n, rmin, rmax, colors, bias=(0, 0)):
    x, y, w, h = rect
    for c in colors:
        for _ in range(n):
            ang = random.uniform(0, 6.283)
            d = random.random() ** 0.6
            px = cx + math.cos(ang) * rw * d + bias[0] * (colors.index(c))
            py = cy + math.sin(ang) * rh * d + bias[1] * (colors.index(c))
            r = random.uniform(rmin, rmax)
            ellipse(a.img, a.lay, (px - r, py - r, px + r, py + r), jitter(c, 0.08), (x + 1, y + 1, w - 2, h - 2))


def trunk(a, rect, width_f, top_f):
    x, y, w, h = rect
    tw = w * width_f
    fill_rect(a.img, a.lay, (round(x + w / 2 - tw / 2), round(y + h * top_f), round(tw), round(h * (1 - top_f)) - 1),
              (84, 66, 50))
    fill_rect(a.img, a.lay, (round(x + w / 2 - tw / 2), round(y + h * top_f), max(2, round(tw * 0.35)),
                             round(h * (1 - top_f)) - 1), (64, 50, 40))


def paint_foliage(a):
    a.lay.add_alpha()
    for r in FOLIAGE:
        x, y, w, h = a.rect(r)
        a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
        a.lay.edit_clear()
    Gimp.Selection.none(a.img)
    dark, mid, light = (46, 70, 34), (68, 98, 44), (100, 130, 58)
    # tree_a: broad deciduous crown
    rect = a.rect("tree_a")
    x, y, w, h = rect
    trunk(a, rect, 0.07, 0.5)
    blobs(a, rect, x + w / 2, y + h * 0.36, w * 0.36, h * 0.28, 55, 16, 34, [dark, mid, light], bias=(-5, -6))
    # tree_b: taller oval crown, a bluer green
    rect = a.rect("tree_b")
    x, y, w, h = rect
    trunk(a, rect, 0.06, 0.6)
    blobs(a, rect, x + w / 2, y + h * 0.40, w * 0.30, h * 0.34, 55, 14, 30,
          [(40, 66, 44), (58, 90, 58), (86, 118, 76)], bias=(-4, -6))
    # tree_c: conifer, rows of blobs narrowing upward
    rect = a.rect("tree_c")
    x, y, w, h = rect
    trunk(a, rect, 0.05, 0.84)
    rows = 16
    for i in range(rows):
        t = i / (rows - 1)
        cy = y + h * (0.86 - 0.80 * t)
        half = w * 0.42 * (1 - t) + 6
        for c in [(34, 58, 40), (48, 76, 50), (66, 96, 62)]:
            for _ in range(5):
                px = x + w / 2 + random.uniform(-half, half) * (0.9 if c[0] > 40 else 1.0)
                r = random.uniform(8, 16)
                ellipse(a.img, a.lay, (px - r, cy - r * 0.8, px + r, cy + r * 0.8), jitter(c, 0.08),
                        (x + 1, y + 1, w - 2, h - 2))
    # shrubs: low mounds
    for r, cols in (("shrub_a", [dark, mid, light]), ("shrub_b", [(52, 76, 36), (80, 108, 46), (116, 140, 64)])):
        rect = a.rect(r)
        x, y, w, h = rect
        blobs(a, rect, x + w / 2, y + h * 0.62, w * 0.40, h * 0.36, 45, 12, 26, cols, bias=(-3, -4))
    for r in FOLIAGE:
        a.material(r, 0.0, 0.10)


def paint_structures(a):
    # Fence panel: 96 x 72 in of vertical boards, weathered cedar.
    x, y, w, h = a.rect("fence")
    n = 17
    for i in range(n):
        bx0, bx1 = x + round(i * w / n), x + round((i + 1) * w / n)
        fill_rect(a.img, a.lay, (bx0, y, bx1 - bx0, h), jitter((146, 118, 88), 0.07))
        fill_rect(a.img, a.lay, (bx0, y, 1, h), (92, 72, 54))
    grain(a.img, a.lay, (x, y, w, h), 0.06, 1.0)
    for fy in (0.12, 0.88):
        fill_rect(a.img, a.lay, (x, y + round(h * fy), w, 2), (118, 94, 70))
    a.material("fence", 0.0, 0.08)
    # Facade: one ~31 ft wide, two-storey unit of beige lap siding with four windows.
    x, y, w, h = a.rect("facade")
    fill_rect(a.img, a.lay, (x, y, w, h), (198, 188, 166))
    for r in range(0, h, 4):
        fill_rect(a.img, a.lay, (x, y + r, w, 1), (176, 166, 146))
    fill_rect(a.img, a.lay, (x, y + 60, w, 4), (226, 222, 212))            # floor band
    fill_rect(a.img, a.lay, (x, y + h - 6, w, 6), (150, 146, 138))         # foundation
    for fx in (0.14, 0.62):
        for wy in (16, 76):
            wx = x + round(fx * w)
            fill_rect(a.img, a.lay, (wx - 3, y + wy - 3, 46, 36), (236, 234, 228))
            fill_rect(a.img, a.lay, (wx, y + wy, 40, 30), (72, 84, 98))
            fill_rect(a.img, a.lay, (wx, y + wy, 40, 8), (110, 122, 134))   # sky glint
            fill_rect(a.img, a.lay, (wx + 19, y + wy, 2, 30), (236, 234, 228))
    a.material("facade", 0.0, 0.1)
    # Roof shingles.
    x, y, w, h = a.rect("roof")
    fill_rect(a.img, a.lay, (x, y, w, h), (82, 80, 78))
    for r in range(0, h, 8):
        fill_rect(a.img, a.lay, (x, y + r, w, 2), (60, 58, 58))
    grain(a.img, a.lay, (x, y, w, h), 0.08, 0.8)
    a.material("roof", 0.0, 0.05)
    # Concrete.
    for r, base in (("path", (182, 180, 172)), ("patio", (170, 168, 160))):
        x, y, w, h = a.rect(r)
        fill_rect(a.img, a.lay, (x, y, w, h), base)
        grain(a.img, a.lay, (x, y, w, h), 0.05, 1.2)
        a.material(r, 0.0, 0.12)
    a.fill("wall_plain", (198, 188, 166), 0.0, 0.1, noise=0.03)


def ground_tile():
    img, lay = new_image(1024, 1024, "exterior_ground")
    fill_rect(img, lay, (0, 0, 1024, 1024), (88, 116, 52))
    for _ in range(90):
        cx, cy, r = random.uniform(0, 1024), random.uniform(0, 1024), random.uniform(40, 140)
        c = random.choice([(104, 132, 60), (74, 100, 44), (112, 124, 66)])
        ellipse(img, lay, (cx - r, cy - r * 0.8, cx + r, cy + r * 0.8), c + (0.25,), (0, 0, 1024, 1024))
    gegl(lay, "gegl:gaussian-blur", std_dev_x=18.0, std_dev_y=18.0)
    gegl(lay, "gegl:noise-rgb", correlated=False, independent=False, red=0.16, green=0.16,
         blue=0.16, gaussian=True, seed=random.randint(0, 99999))
    gegl(lay, "gegl:gaussian-blur", std_dev_x=0.8, std_dev_y=0.8)
    gegl(lay, "gegl:tile-seamless")
    _tile_save(img, "exterior_ground", 0.05)


def build():
    random.seed(20260925)
    a = Atlas(ATLAS)
    paint_sky(a)
    paint_structures(a)
    paint_foliage(a)
    # Emission: the sky only (bright backdrop regardless of baked light).
    eimg, elay = a.glow_layer()
    x, y, w, h = a.rect("sky")
    src = a.img.duplicate()
    src.crop(w, h, x, y)
    lay = add_layer_from(eimg, src, "sky_glow", x, y)
    src.delete()
    a.eimg.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    a.save()
    ground_tile()
