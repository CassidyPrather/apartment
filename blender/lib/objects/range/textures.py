"""range atlas: flat fills sampled by eye from the survey crops (white enamel, black coils
and drip pans, mid-grey oven window). No text or badge."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "range", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def build():
    a = Atlas(ATLAS)
    a.fill("enamel", (236, 236, 232), 0.0, 0.7)
    a.fill("cooktop", (230, 230, 226), 0.0, 0.75)
    a.fill("glass", (70, 72, 76), 0.0, 0.9)
    x, y, w, h = a.rect("glass")
    fill_rect(a.img, a.lay, (x + 8, y + 8, w - 16, h - 16), (104, 106, 110))   # PHOTO: mid-grey window pane in its frame
    a.fill("chrome", (196, 198, 200), 0.6, 0.6, noise=0.03, blur=0.5)
    a.fill("coil", (38, 38, 40), 0.3, 0.3, noise=0.06, blur=0.5)
    a.fill("knob", (232, 232, 228), 0.0, 0.5)
    a.fill("trim_black", (28, 28, 30), 0.0, 0.4)
    a.save()
