"""desk atlas: procedural glossy cherry/mahogany wood made from scratch in GIMP (no photo
pixels). Base colour from the survey (LiDAR colour ~#3a2426, photos read a deep
red-brown with a high-gloss finish)."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "desk", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
BASE = (44, 18, 20)


def wood(a, region, vertical, base=BASE, streak=60.0, seed=11, bands=9):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    angle = 90.0 if vertical else 0.0
    for amt, length, op in ((0.45, streak * 3, 40), (0.7, streak, 26)):
        g = Gimp.Layer.new(a.img, "grain", a.size, a.size, Gimp.ImageType.RGB_IMAGE, op,
                           Gimp.LayerMode.OVERLAY)
        a.img.insert_layer(g, None, 0)
        fill_rect(a.img, g, (0, 0, a.size, a.size), (128, 128, 128))
        a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
        gegl(g, "gegl:noise-rgb", correlated=False, independent=False, red=amt, green=amt,
             blue=amt, gaussian=True, seed=seed)
        gegl(g, "gegl:motion-blur", length=length, angle=angle)
        Gimp.Selection.none(a.img)
        seed += 1
        a.lay = flatten(a.img)
    for i in range(bands):
        t = random.uniform(0, 1)
        wid = random.randint(3, 16)
        d = random.choice((-8, -5, 6, 9))
        c = (max(0, base[0] + d), max(0, base[1] + d // 2), max(0, base[2] + d // 2), 0.45)
        if vertical:
            fill_rect(a.img, a.lay, (x + int(t * (w - wid)), y, wid, h), c)
        else:
            fill_rect(a.img, a.lay, (x, y + int(t * (h - wid)), w, wid), c)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    s = 2.0
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=(0.6 if vertical else s), std_dev_y=(s if vertical else 0.6))
    Gimp.Selection.none(a.img)


def build():
    a = Atlas(ATLAS)
    wood(a, "wood_top", False, streak=50.0, seed=51)
    wood(a, "wood_v", True, streak=40.0, seed=61)
    wood(a, "wood_drawer", False, streak=40.0, seed=71)
    wood(a, "raised", False, base=(47, 19, 22), streak=30.0, seed=81, bands=4)
    for r in ("wood_top", "wood_v", "wood_drawer", "raised"):
        a.material(r, 0.0, 0.7)
    a.fill("pull", (178, 176, 170), 0.9, 0.55, noise=0.03)
    a.fill("shadow", (30, 16, 17), 0.0, 0.3)
    a.save()
