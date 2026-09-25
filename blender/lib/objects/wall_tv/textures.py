"""wall_tv atlases (headless GIMP): flat black plastics, and a separate near-black
screen texture (the video player replaces it at runtime). No logo, no screen content."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "wall_tv", "object.py")


def _get(name):
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise RuntimeError(name + " not found in object.py")


ATLAS = _get("ATLAS")
SCREEN_ATLAS = _get("SCREEN_ATLAS")


def build():
    a = Atlas(ATLAS)
    a.fill("bezel", (18, 18, 20), 0.0, 0.55)
    a.fill("back", (28, 28, 30), 0.0, 0.3, noise=0.03, blur=0.8)
    a.fill("mount", (36, 36, 38), 0.6, 0.35)
    a.fill("led", (200, 30, 20), 0.0, 0.6)
    a.fill("panel_edge", (22, 22, 24), 0.0, 0.4)
    a.save()
    s = Atlas(SCREEN_ATLAS)
    s.fill("screen", (8, 9, 11), 0.0, 0.85)
    s.save()
