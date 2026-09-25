"""Bedroom fixtures atlas (2048). The wall art is the real pictures, rectified from the
bedroom capture frames by Reference/bedroom_fixtures_work/final.py (local-only) and pasted
into their regions; the back-wall photo strip stays an abstract painted strip (privacy).
Plus blinds, base stations, smoke detector and thermostat swatches. Runs inside headless GIMP."""

import os
import random

exec(open(os.path.join(ROOT, "blender", "lib", "objects", "bedroom_fixtures", "layout.py"),
          encoding="utf-8").read())
FINAL = os.path.join(REF, "bedroom_fixtures_work", "final")

WHITE = (240, 238, 232)


def lerp(c0, c1, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))


def vgrad(a, rect, c0, c1, band=3):
    x, y, w, h = rect
    for r in range(0, h, band):
        fill_rect(a.img, a.lay, (x, y + r, w, min(band, h - r)), lerp(c0, c1, r / max(1, h - 1)))


CLIP = [None]


def clip(a, region):
    CLIP[0] = a.rect(region)


def _fill_sel(a, rgb):
    if CLIP[0] is not None:
        x, y, w, h = CLIP[0]
        a.img.select_rectangle(Gimp.ChannelOps.INTERSECT, x, y, w, h)
    if not Gimp.Selection.is_empty(a.img):
        Gimp.context_set_foreground(color(tuple(rgb[:3])))
        Gimp.context_set_opacity(100.0 * (rgb[3] if len(rgb) == 4 else 1.0))
        a.lay.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.context_set_opacity(100.0)
    Gimp.Selection.none(a.img)


def blur(a, rect, s):
    x, y, w, h = rect
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=s, std_dev_y=s)
    Gimp.Selection.none(a.img)


def strip(a):
    clip(a, "art_strip")
    # abstract stand-in for a strip of photos: six soft colour panels on white card
    r = a.rect("art_strip")
    x, y, w, h = r
    fill_rect(a.img, a.lay, r, WHITE)
    cols = [((150, 200, 150), (230, 170, 190)), ((230, 180, 200), (140, 190, 140)), ((120, 180, 130), (200, 230, 190)),
            ((240, 190, 200), (170, 210, 160)), ((160, 210, 170), (230, 160, 180)), ((210, 230, 190), (130, 180, 140))]
    pw = (w - 14) / 6
    for i, (c0, c1) in enumerate(cols):
        px = round(x + 7 + i * pw + 2)
        vgrad(a, (px, y + 10, round(pw - 4), h - 20), c0, c1)
    blur(a, (x + 6, y + 9, w - 12, h - 18), 1.5)
    a.material("art_strip", 0.0, 0.3)


def photo(a, region, smooth):
    x, y, w, h = a.rect(region)
    src = load(os.path.join(FINAL, region + ".png"))
    src.scale(w, h)
    lay = add_layer_from(a.img, src, region, x, y)
    src.delete()
    a.material(region, 0.0, smooth)


GLAZED = {"art_center": 0.7, "art_south": 0.6, "art_tree": 0.6}


def build():
    random.seed(7)
    a = Atlas(ATLAS)
    for r in PHOTOS:
        photo(a, r, GLAZED.get(r, 0.25))
    strip(a)
    CLIP[0] = None
    a.fill("vane", (232, 231, 224), 0.0, 0.25, noise=0.025, blur=3.0)
    a.fill("rail", (236, 236, 231), 0.0, 0.4, noise=0.015, blur=1.5)
    a.fill("carrier", (60, 60, 58), 0.0, 0.2)
    a.fill("wand", (214, 218, 216), 0.0, 0.7)
    a.fill("frame_black", (20, 20, 22), 0.0, 0.45)
    a.fill("frame_white", (238, 237, 232), 0.0, 0.4)
    a.fill("mat_white", (242, 241, 236), 0.0, 0.2, noise=0.01)
    a.fill("paper", (244, 243, 238), 0.0, 0.2)
    a.fill("bs_body", (28, 28, 30), 0.0, 0.3, noise=0.015)
    a.fill("bs_face", (12, 12, 14), 0.0, 0.85)
    a.fill("bracket", (26, 26, 28), 0.0, 0.35)
    a.fill("cable", (40, 40, 42), 0.0, 0.3)
    a.fill("smoke", (238, 237, 232), 0.0, 0.35, noise=0.01)
    rx, ry, rw, rh = a.rect("smoke")
    for k in range(4):
        fill_rect(a.img, a.lay, (rx + 20, ry + 30 + k * 18, rw - 40, 4), (210, 209, 204))
    a.fill("thermo", (236, 235, 230), 0.0, 0.35)
    a.fill("thermo_face", (236, 235, 230), 0.0, 0.4)
    tx, ty, tw, th = a.rect("thermo_face")
    fill_rect(a.img, a.lay, (tx + 30, ty + 30, tw - 60, 36), (120, 132, 128))
    for k in range(3):
        fill_rect(a.img, a.lay, (tx + 30 + k * 26, ty + 86, 16, 10), (200, 200, 196))
    a.save()
