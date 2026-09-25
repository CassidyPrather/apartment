"""Bedroom fixtures atlas (2048). The wall art is the real pictures, rectified from the
bedroom capture frames by Reference/bedroom_fixtures_work/final.py (local-only) and pasted
into their regions. The flower print, the moon print and the holiday tree come from Cassidy's
close-up photos / the artist's original file via Reference/living_wall_art_work/v2/photo_prep.py.
Signatures are kept. The keychain faces are crops of IMG_1520 (Reference/bedroom_fixtures_work/v3/
charms_data.py), balanced off the wall.
Plus blinds, base stations, smoke detector and thermostat swatches. Runs inside headless GIMP."""

import os
import random

exec(open(os.path.join(ROOT, "blender", "lib", "objects", "bedroom_fixtures", "layout.py"),
          encoding="utf-8").read())
FINAL = os.path.join(REF, "bedroom_fixtures_work", "final")


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
    # keychain charms: clear acrylic, metals, wall pins, and the plain pink heart that stands in
    # for the brand charm (a soft glossy pink with a highlight)
    a.fill("ch_clear", (236, 240, 242), 0.0, 0.9)
    a.fill("nickel", (196, 198, 202), 1.0, 0.75)
    a.fill("rose_gold", (214, 150, 128), 1.0, 0.7)
    a.fill("gold", (222, 186, 96), 1.0, 0.7)
    a.fill("pin", (200, 200, 204), 1.0, 0.6)
    hx, hy, hw, hh = a.rect("ch_pinkheart")
    a.fill("ch_pinkheart", (238, 150, 190), 0.0, 0.85)
    fill_ellipse(a.img, a.lay, (hx + 8, hy + 10, hx + 30, hy + 28), (252, 206, 226))
    a.save()
