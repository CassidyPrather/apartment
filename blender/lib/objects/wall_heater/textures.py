"""wall_heater atlas: white enamel frame; louvres as horizontal white slats with dark
gaps (drawn, not photo)."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "wall_heater", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def build():
    a = Atlas(ATLAS)
    a.fill("frame", (236, 234, 228), 0.0, 0.45)
    a.fill("dark", (40, 40, 40), 0.0, 0.2)
    x, y, w, h = a.rect("louvres")
    fill_rect(a.img, a.lay, (x, y, w, h), (60, 60, 62))
    n = 22                                  # slats over the ~12 in opening
    p = h / n
    for i in range(n):
        yy = y + round(i * p)
        fill_rect(a.img, a.lay, (x, yy, w, max(2, round(p * 0.62))), (214, 212, 206))
    a.material("louvres", 0.3, 0.35)
    a.save()
