"""dining_chair atlas: procedural dark charcoal-stained wood grain, made from scratch in
GIMP (no photo pixels). Base colour sampled from the survey photos of the chairs
(near-black brown, open grain showing a little lighter)."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dining_chair", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
BASE = (34, 31, 30)      # chairs read a shade darker than the table in the photos


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
    wood(a, "wood_v", True, streak=30.0, seed=31)
    wood(a, "wood_h", False, streak=30.0, seed=41)
    for r in ("wood_v", "wood_h"):
        a.material(r, 0.0, 0.38)
    # light grey upholstery: fine weave noise
    a.fill("cushion", (182, 178, 170), 0.0, 0.12)
    # faint woven tone stripes running parallel to the front edge (photo)
    x, y, w, h = a.rect("cushion")
    tones = (0, -8, 5, -14, 3, -6, 8, -10)
    n = 16
    for i in range(n):
        d = tones[i % len(tones)]
        fill_rect(a.img, a.lay, (x, y + i * h // n, w, h // n + 1), tuple(max(0, v + d) for v in (182, 178, 170)))
    grain(a.img, a.lay, (x, y, w, h), 0.12, 0.5)
    a.save()
