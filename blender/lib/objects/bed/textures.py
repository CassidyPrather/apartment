"""bed atlas (headless GIMP, gimp_textures.py helpers in scope).

Light aqua fleece with soft lighter/darker mottling (the pile catches light unevenly in
the photos) and fine grain; cool grey pillowcase; white sheet; dark grey skirt with
soft vertical pleat streaks; espresso frame; black casters. Colours from the survey
crops, lifted from their dim exposure (blanket ~#9cc0c4)."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "bed", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
R = random.Random(23)


def blur_region(a, region, sigma):
    x, y, w, h = a.rect(region)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=sigma, std_dev_y=sigma)
    Gimp.Selection.none(a.img)


def mottle(a, region, base, cols, n, rmin, rmax, sigma):
    x0, y0, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x0, y0, w, h), base)
    for _ in range(n):
        cx, cy = x0 + R.randint(0, w), y0 + R.randint(0, h)
        rx, ry = R.randint(rmin, rmax), R.randint(rmin, rmax)
        fill_ellipse(a.img, a.lay, (max(cx - rx, x0), max(cy - ry, y0),
                                    min(cx + rx, x0 + w), min(cy + ry, y0 + h)), R.choice(cols))
    blur_region(a, region, sigma)


def build():
    random.seed(23)
    a = Atlas(ATLAS)
    img, lay = a.img, a.lay

    # aqua fleece
    mottle(a, "blanket", (140, 180, 192),
           [(154, 192, 202, 0.6), (126, 166, 180, 0.6), (160, 198, 206, 0.5), (118, 158, 174, 0.5)],
           140, 18, 60, 16.0)
    grain(img, lay, a.rect("blanket"), 0.05, 1.2)
    a.material("blanket", 0.0, 0.06)

    # grey pillowcase with a few soft creases
    mottle(a, "pillow", (122, 124, 130), [(136, 138, 144, 0.5), (108, 110, 116, 0.5)], 30, 8, 30, 6.0)
    x, y, w, h = a.rect("pillow")
    for _ in range(7):
        cx = x + R.randint(20, w - 20)
        fill_rect(img, lay, (cx, y, R.randint(2, 4), h), (118, 120, 124, 0.5))
    blur_region(a, "pillow", 3.0)
    grain(img, lay, a.rect("pillow"), 0.03, 0.8)
    a.material("pillow", 0.0, 0.1)

    # white sheet
    mottle(a, "sheet", (214, 214, 212), [(226, 226, 224, 0.5), (196, 196, 196, 0.5)], 30, 8, 30, 5.0)
    grain(img, lay, a.rect("sheet"), 0.02, 0.8)
    a.material("sheet", 0.0, 0.12)

    # dark grey skirt with pleat streaks
    x, y, w, h = a.rect("skirt")
    fill_rect(img, lay, (x, y, w, h), (62, 62, 64))
    for k in range(0, w, 12):
        fill_rect(img, lay, (x + k + R.randint(0, 4), y, R.randint(3, 6), h),
                  R.choice([(52, 52, 54, 0.7), (74, 74, 76, 0.6)]))
    blur_region(a, "skirt", 2.5)
    grain(img, lay, (x, y, w, h), 0.03, 0.8)
    a.material("skirt", 0.0, 0.08)

    a.fill("frame", (40, 30, 24), 0.2, 0.35, noise=0.04, blur=1.0)
    a.fill("caster", (20, 20, 21), 0.0, 0.45, noise=0.02, blur=0.6)
    a.save()
