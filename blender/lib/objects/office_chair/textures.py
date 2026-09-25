"""office_chair atlas, drawn from scratch in GIMP (no photo pixels): navy woven fabric,
tan cotton cloth with soft vertical fold shading, black plastics, dark chrome, and a
pale clear-plastic tint for the chair mat. Colours sampled by eye from the survey crops."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "office_chair", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def build():
    a = Atlas(ATLAS)
    a.fill("fabric", (24, 32, 58), 0.0, 0.08, noise=0.025, blur=1.0)
    x, y, w, h = a.rect("cloth")
    a.fill("cloth", (172, 130, 92), 0.0, 0.1)
    random.seed(3)
    for i in range(14):                      # soft fold streaks
        cx = x + random.randint(0, w - 12)
        wid = random.randint(4, 14)
        d = random.choice((-18, -12, 10, 14))
        fill_rect(a.img, a.lay, (cx, y, wid, h), tuple(max(0, v + d) for v in (172, 130, 92)) + (0.6,))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=5.0, std_dev_y=1.0)
    Gimp.Selection.none(a.img)
    grain(a.img, a.lay, (x, y, w, h), 0.04, 0.6)
    a.fill("plastic", (22, 22, 24), 0.0, 0.3, noise=0.015)
    a.fill("metal", (60, 60, 64), 0.9, 0.6)
    a.fill("pad", (18, 18, 20), 0.0, 0.2, noise=0.02)
    a.fill("mat", (215, 222, 226), 0.0, 0.8)
    a.save()
