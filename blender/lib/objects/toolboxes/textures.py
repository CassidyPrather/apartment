"""toolboxes atlas: black plastic, safety-yellow lid panels with ribs, a plain white
paper carton with a blue triangle print (no words, no logo)."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "toolboxes", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
BLUES = [(30, 90, 190), (60, 120, 210), (20, 60, 150), (120, 160, 225), (240, 244, 248)]


def triangles(a, region, frac):
    """White card with a band of blue tiles split into triangles over `frac` of it."""
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), (240, 242, 244))
    t = 24
    for j in range(int(h * frac) // t):
        for i in range(w // t):
            fill_rect(a.img, a.lay, (x + i * t, y + j * t, t, t), random.choice(BLUES))
            # diagonal split: darker lower triangle drawn as a stair of thin rects
            c2 = random.choice(BLUES)
            for k in range(0, t, 3):
                fill_rect(a.img, a.lay, (x + i * t, y + j * t + k, k + 3, 3), c2)
    a.material(region, 0.0, 0.2)


def build():
    random.seed(11)
    a = Atlas(ATLAS)
    a.fill("black", (22, 22, 24), 0.0, 0.35, noise=0.03, blur=0.8)
    x, y, w, h = a.rect("yellow")
    fill_rect(a.img, a.lay, (x, y, w, h), (238, 196, 20))
    for i in range(0, w, 16):
        fill_rect(a.img, a.lay, (x + i, y, 5, h), (205, 165, 10))
    a.material("yellow", 0.0, 0.4)
    a.fill("strip", (18, 18, 20), 0.0, 0.4)
    triangles(a, "carton_side", 0.55)
    triangles(a, "carton_top", 0.45)
    a.fill("carton_edge", (236, 238, 240), 0.0, 0.2)
    a.save()
