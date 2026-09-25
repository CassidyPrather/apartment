"""dresser_items atlas (512): flat plush colours with a soft fuzz, white plastic, a
clear-plastic tint, dark drawer contents, and an antique-style globe (tan land blobs on a
dark ocean). Procedural, no text."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dresser_items", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
FUZZ = {
    "green": (92, 110, 44), "green_light": (150, 162, 70), "dark": (48, 48, 54),
    "white": (228, 226, 220), "grey": (150, 148, 146), "pink": (222, 140, 160),
    "purple": (140, 105, 190), "yellow": (240, 204, 80), "cream": (212, 200, 168),
    "red": (200, 60, 50), "black": (22, 22, 24), "blue": (40, 110, 200),
    "orange": (232, 140, 50),
}


def build():
    random.seed(5)
    a = Atlas(ATLAS)
    for r, c in FUZZ.items():
        a.fill(r, c, 0.0, 0.08, noise=0.06, blur=1.2)
    a.material("blue", 0.0, 0.45)
    a.fill("brass", (176, 140, 70), 1.0, 0.55, noise=0.04)
    a.fill("plastic", (236, 236, 232), 0.0, 0.55, noise=0.01)
    a.fill("clear", (220, 226, 228), 0.0, 0.8)
    x, y, w, h = a.rect("stuff")
    fill_rect(a.img, a.lay, (x, y, w, h), (70, 64, 60))
    for _ in range(40):
        c = random.choice([(40, 40, 44), (120, 90, 80), (190, 170, 150), (80, 100, 140), (160, 60, 70)])
        rx, ry = random.randint(0, w - 20), random.randint(0, h - 20)
        fill_rect(a.img, a.lay, (x + rx, y + ry, random.randint(8, 40), random.randint(6, 24)), c)
    a.material("stuff", 0.0, 0.2)
    x, y, w, h = a.rect("globe")
    fill_rect(a.img, a.lay, (x, y, w, h), (34, 36, 40))
    for _ in range(30):
        cx, cy = random.randint(x, x + w), random.randint(y + 10, y + h - 10)
        for _ in range(5):
            ox, oy = random.randint(-12, 12), random.randint(-8, 8)
            rx, ry = random.randint(4, 10), random.randint(3, 7)
            fill_ellipse(a.img, a.lay, (cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry),
                         random.choice([(198, 170, 110), (180, 150, 96), (210, 186, 130)]))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 1.0)
    a.material("globe", 0.0, 0.6)
    a.save()
