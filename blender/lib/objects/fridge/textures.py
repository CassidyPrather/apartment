"""fridge atlas: flat fills (white refrigerator; every colour is a guess, no photo yet)."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "fridge", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def build():
    a = Atlas(ATLAS)
    a.fill("case", (230, 230, 226), 0.0, 0.55)
    a.fill("door", (238, 238, 234), 0.0, 0.7)
    a.fill("handle", (222, 222, 218), 0.0, 0.6)
    a.fill("gasket", (150, 150, 150), 0.0, 0.2)
    a.fill("grille", (26, 26, 28), 0.0, 0.3)
    a.save()
