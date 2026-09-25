"""microwave atlas: flat fills sampled by eye from the survey crops (white case, grey
screened window). Keypad is a light panel with a grid of button outlines, no text."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "microwave", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def build():
    a = Atlas(ATLAS)
    a.fill("white", (236, 237, 235), 0.0, 0.6)
    a.fill("window", (196, 198, 198), 0.0, 0.7, noise=0.02, blur=1.0)   # PHOTO: pale screened window
    x, y, w, h = a.rect("window")
    fill_rect(a.img, a.lay, (x, y, w, 6), (215, 216, 214))
    fill_rect(a.img, a.lay, (x, y + h - 6, w, 6), (215, 216, 214))
    a.fill("keypad", (228, 229, 228), 0.0, 0.5)
    x, y, w, h = a.rect("keypad")
    for i in range(3):
        for j in range(5):
            fill_rect(a.img, a.lay, (x + 14 + i * 36, y + 10 + j * 24, 28, 14), (200, 202, 204))
    a.fill("display", (20, 22, 24), 0.0, 0.8)
    a.fill("vent", (205, 207, 207), 0.0, 0.4)   # PHOTO: grille barely visible
    a.fill("under", (200, 200, 198), 0.0, 0.3)
    a.fill("lens", (245, 245, 238), 0.0, 0.8)
    a.save()
