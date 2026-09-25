"""dishwasher atlas: flat fills sampled by eye from the survey crops (white door, cream
control band). No text or badge."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dishwasher", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def build():
    a = Atlas(ATLAS)
    a.fill("white", (232, 233, 230), 0.0, 0.55)
    a.fill("cream", (234, 228, 208), 0.0, 0.5)
    a.fill("slot", (40, 40, 40), 0.0, 0.2)
    a.fill("tub", (150, 150, 150), 0.0, 0.3)
    a.fill("dial", (226, 218, 196), 0.0, 0.5)
    a.save()
