"""couch atlas: sage grey-green woven fabric drawn in GIMP (noise streaked along two
axes for a fine basket weave, plus a soft low-frequency mottle), darker deck fabric,
dark wood feet. Colour from the photo crops, lifted from their dim exposure."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "couch", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
SAGE = (118, 130, 117)


def weave(a, region, base, amount=0.2):
    img, lay = a.img, a.lay
    x, y, w, h = a.rect(region)
    fill_rect(img, lay, (x, y, w, h), base)
    img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    for ang in (0.0, 90.0):
        gegl(lay, "gegl:noise-rgb", correlated=False, independent=False, red=amount,
             green=amount, blue=amount, gaussian=True, seed=random.randint(0, 99999))
        gegl(lay, "gegl:motion-blur-linear", length=5.0, angle=ang)
    Gimp.Selection.none(img)
    grain(img, lay, (x, y, w, h), 0.05, 10.0)      # soft mottle / slub
    grain(img, lay, (x, y, w, h), 0.025, 0.6)      # fibre fuzz


def build():
    a = Atlas(ATLAS)
    weave(a, "fabric", SAGE)
    a.material("fabric", 0.0, 0.12)
    weave(a, "fabric_shade", (92, 102, 92))
    a.material("fabric_shade", 0.0, 0.1)
    a.fill("leg", (46, 36, 28), 0.0, 0.35, noise=0.04, blur=1.0)
    a.save()
