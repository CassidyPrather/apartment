"""headboard_bookcase atlas (headless GIMP, gimp_textures.py helpers in scope).

Honey-oak laminate: a golden fill with streaked grain (noise + linear motion blur) and a
few darker figure bands; edge banding a touch lighter; the back panel darker. Plain
white power strip, matte black plastics and cables, a white cable, a muted green strap,
and flat cloth colours for the clothes in the bays. No markings anywhere."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "headboard_bookcase", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
R = random.Random(9)


def oak(a, region, rgb, noise=0.16, bands=True):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), rgb)
    if bands:
        for _ in range(max(4, w // 40)):
            by = y + R.randint(0, h - 8)
            dark = tuple(max(0, v - R.randint(14, 26)) for v in rgb) + (0.55,)
            fill_rect(a.img, a.lay, (x, by, w, R.randint(3, 10)), dark)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:noise-rgb", correlated=False, independent=False, red=noise, green=noise,
         blue=noise, gaussian=True, seed=random.randint(0, 99999))
    gegl(a.lay, "gegl:motion-blur-linear", length=70.0, angle=0.0)
    Gimp.Selection.none(a.img)


def build():
    random.seed(9)
    a = Atlas(ATLAS)
    oak(a, "oak", (164, 104, 48))
    a.material("oak", 0.0, 0.45)
    oak(a, "oak_edge", (176, 116, 56), 0.12)
    a.material("oak_edge", 0.0, 0.45)
    oak(a, "interior", (104, 66, 34), 0.10, bands=False)
    a.material("interior", 0.0, 0.3)
    a.fill("strip", (226, 224, 216), 0.0, 0.45, noise=0.02, blur=0.6)
    a.fill("plastic", (30, 30, 33), 0.0, 0.4, noise=0.03, blur=0.6)
    a.fill("cable", (22, 22, 24), 0.0, 0.5)
    a.fill("cable_white", (220, 220, 214), 0.0, 0.5)
    a.fill("accent", (120, 150, 60), 0.0, 0.2, noise=0.05, blur=0.8)
    a.fill("cloth_mauve", (150, 118, 124), 0.0, 0.08, noise=0.08, blur=2.0)
    a.fill("cloth_maroon", (92, 28, 34), 0.0, 0.08, noise=0.08, blur=2.0)
    a.fill("cloth_dark", (34, 32, 36), 0.0, 0.08, noise=0.06, blur=2.0)
    a.fill("strap", (36, 38, 40), 0.0, 0.15, noise=0.06, blur=1.0)
    a.fill("cushion", (48, 48, 52), 0.0, 0.08, noise=0.06, blur=1.0)
    a.save()
