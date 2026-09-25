"""dresser atlas (512): honey-oak veneer with open oak grain (horizontal on the drawer
fronts and top, vertical on the sides), dark grooves, lighter edges. Procedural."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dresser", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
OAK = (146, 98, 58)
OAK_DARK = (110, 72, 40)
OAK_LIGHT = (166, 118, 72)


def oak(a, region, vertical, seed):
    random.seed(seed)
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), OAK)
    # grain lines: long thin streaks of darker and lighter wood
    along, across = (h, w) if vertical else (w, h)
    for _ in range(int(across * 0.9)):
        c = random.choice([OAK_DARK, OAK_DARK, OAK_LIGHT, (138, 90, 48)])
        p = random.randint(0, across - 2)
        t = random.choice([1, 1, 2, 3])
        s = random.randint(-along // 2, along // 2)
        L = random.randint(along // 3, along)
        s0, s1 = max(0, s), min(along, s + L)
        if s1 <= s0:
            continue
        if vertical:
            fill_rect(a.img, a.lay, (x + p, y + s0, t, s1 - s0), c)
        else:
            fill_rect(a.img, a.lay, (x + s0, y + p, s1 - s0, t), c)
    grain(a.img, a.lay, (x, y, w, h), 0.06, 1.0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=18.0, angle=90.0 if vertical else 0.0)
    Gimp.Selection.none(a.img)
    a.material(region, 0.0, 0.42)


def build():
    a = Atlas(ATLAS)
    oak(a, "front", False, 1)
    oak(a, "side", True, 2)
    oak(a, "top", False, 3)
    a.fill("dark", (52, 34, 20), 0.0, 0.2, noise=0.03)
    a.fill("edge", (170, 118, 68), 0.0, 0.4, noise=0.05)
    a.save()
