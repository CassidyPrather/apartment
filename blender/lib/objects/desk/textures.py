"""desk atlas: procedural glossy cherry/mahogany wood made from scratch in GIMP (no photo
pixels). Wear from the capture close-ups: fine hairline scratches and swirl scuffs in
the gloss of the top and panels (one long S-shaped scratch on the end panel), a dusty,
hazier patch on the top behind the pedestal where the PC stands, and tiny pale chips in
the edge banding. Base colour from the survey (LiDAR colour ~#3a2426, photos read a deep
red-brown with a high-gloss finish)."""

import ast
import math
import os
import random

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


def _line(lay, pts, size, rgb, opacity):
    Gimp.context_set_foreground(color(rgb))
    Gimp.context_set_brush_size(size)
    Gimp.context_set_opacity(opacity)
    Gimp.paintbrush_default(lay, [c for p in pts for c in p])
    Gimp.context_set_opacity(100.0)


def scratches(a, region, n, seed, area=None, maxlen=60, rgb=(120, 78, 74), op=(5, 13)):
    """Hairline scratches: short, slightly curved light strokes at low opacity."""
    rnd = random.Random(seed)
    x, y, w, h = a.rect(region)
    ax, ay, aw, ah = area or (0, 0, 1, 1)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    for _ in range(n):
        px = x + w * (ax + aw * rnd.random())
        py = y + h * (ay + ah * rnd.random())
        ang = rnd.uniform(0, math.pi)
        L = rnd.uniform(maxlen * 0.2, maxlen)
        bend = rnd.uniform(-0.15, 0.15)
        pts = []
        for i in range(6):
            t = i / 5
            aa = ang + bend * t
            pts.append((px + math.cos(aa) * L * t, py + math.sin(aa) * L * t))
        _line(a.lay, pts, rnd.choice((1.0, 1.0, 1.5)), rgb, rnd.uniform(*op))
    Gimp.Selection.none(a.img)


def s_scratch(a, region, cx, cy, size, seed):
    """The one long S-shaped scratch (end panel close-up)."""
    x, y, w, h = a.rect(region)
    pts = [(x + w * cx + size * 0.5 * math.sin(t * 2 * math.pi) * 0.4, y + h * cy + size * (t - 0.5))
           for t in [i / 12 for i in range(13)]]
    _line(a.lay, pts, 1.5, (150, 104, 96), 45)


def chips(a, region, rows, n, seed):
    """Tiny pale chips in the edge banding (the pinkish-tan substrate shows through)."""
    rnd = random.Random(seed)
    x, y, w, h = a.rect(region)
    r0, r1 = rows
    for _ in range(n):
        cx = x + rnd.randint(2, w - 4)
        cy = y + rnd.randint(r0, r1)
        s = rnd.choice((1, 1, 2))
        fill_ellipse(a.img, a.lay, (cx, cy, cx + s + rnd.randint(0, 2), cy + s), (150, 110, 96, rnd.uniform(0.35, 0.6)))


def dust(a, region, box, seed):
    """Hazy greyish dust/wear patch: soft light speckle, blurred."""
    x, y, w, h = a.rect(region)
    bx, by, bw, bh = box
    X, Y, W, H = int(x + w * bx), int(y + h * by), int(w * bw), int(h * bh)
    g = Gimp.Layer.new(a.img, "dust", a.size, a.size, Gimp.ImageType.RGBA_IMAGE, 100, Gimp.LayerMode.NORMAL)
    a.img.insert_layer(g, None, 0)
    rnd = random.Random(seed)
    for _ in range(260):
        cx, cy = X + rnd.randint(0, W), Y + rnd.randint(0, H)
        # denser toward the centre of the patch
        if rnd.random() > 1.0 - (abs(cx - X - W / 2) / (W / 2) + abs(cy - Y - H / 2) / (H / 2)) / 2.2:
            continue
        s = rnd.randint(2, 9)
        fill_ellipse(a.img, g, (cx, cy, cx + s, cy + s * rnd.uniform(0.5, 1.2)), (104, 86, 86, rnd.uniform(0.06, 0.16)))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(g, "gegl:gaussian-blur", std_dev_x=3.0, std_dev_y=3.0)
    Gimp.Selection.none(a.img)
    a.lay = flatten(a.img)


def build():
    a = Atlas(ATLAS)
    wood(a, "wood_top", False, streak=50.0, seed=51)
    wood(a, "wood_v", True, streak=40.0, seed=61)
    wood(a, "wood_drawer", False, streak=40.0, seed=71)
    wood(a, "raised", False, base=(47, 19, 22), streak=30.0, seed=81, bands=4)
    # wear (photo close-ups): the top's rows 0-18 double as its front edge band
    scratches(a, "wood_top", 45, 5, area=(0.05, 0.35, 0.7, 0.6), maxlen=60)       # where you sit
    scratches(a, "wood_top", 25, 6, area=(0.0, 0.05, 1.0, 0.9), maxlen=40)
    scratches(a, "wood_v", 45, 7, maxlen=50)
    s_scratch(a, "wood_v", 0.3, 0.55, 60, 8)
    scratches(a, "wood_drawer", 25, 9, maxlen=30, op=(5, 12))
    dust(a, "wood_top", (0.72, 0.06, 0.27, 0.4), 10)     # behind the pedestal, under the PC
    chips(a, "wood_top", (1, 16), 5, 11)                 # front edge band
    chips(a, "wood_v", (0, 640), 5, 12)
    for r in ("wood_top", "wood_v", "wood_drawer", "raised"):
        a.material(r, 0.0, 0.7)
    a.fill("pull", (178, 176, 170), 0.9, 0.55, noise=0.03)
    # brushed nickel: horizontal brushing, darker lower lip where fingers go
    x, y, w, h = a.rect("pull")
    grain(a.img, a.lay, (x, y, w, h), 0.08, 0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=30.0, angle=0.0)
    Gimp.Selection.none(a.img)
    a.fill("shadow", (30, 16, 17), 0.0, 0.3)
    a.save()
