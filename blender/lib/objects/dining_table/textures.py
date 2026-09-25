"""dining_table atlas: procedural dark charcoal-stained wood grain, made from scratch in
GIMP (no photo pixels). Base colour sampled from the survey photos of the table top
(near-black brown, open grain showing a little lighter)."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dining_table", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
BASE = (40, 36, 34)      # charcoal stain, near-black brown in the photos


def wood(a, region, vertical, base=BASE, streak=60.0, seed=11):
    """Grain streaks: stretched noise overlaid on the base, plus a few long darker and
    lighter figure bands. `vertical` runs the grain along V (image rows)."""
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    angle = 90.0 if vertical else 0.0
    for amt, length, op in ((0.5, streak * 3, 45), (0.8, streak, 30)):
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
    # soft figure bands
    n = 7
    for i in range(n):
        t = random.uniform(0, 1)
        wid = random.randint(3, 14)
        d = random.choice((-9, -6, 7, 10))
        c = tuple(max(0, min(255, v + d)) for v in base) + (0.5,)
        if vertical:
            fill_rect(a.img, a.lay, (x + int(t * (w - wid)), y, wid, h), c)
        else:
            fill_rect(a.img, a.lay, (x, y + int(t * (h - wid)), w, wid), c)
    img = a.img
    img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    s = 2.0
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=(0.6 if vertical else s), std_dev_y=(s if vertical else 0.6))
    Gimp.Selection.none(img)


def build():
    a = Atlas(ATLAS)
    wood(a, "wood_v", True, seed=11)
    wood(a, "wood_h", False, seed=21)
    a.fill("end", (40, 36, 34), 0.0, 0.3, noise=0.1, blur=1.0)
    for r in ("wood_v", "wood_h"):
        a.material(r, 0.0, 0.42)
    fill_rect(a.img, a.lay, (768, 512, 256, 512), (128, 128, 128))
    fill_rect(a.img, a.lay, (512, 768, 256, 256), (128, 128, 128))
    a.save()
