"""fridge atlas (headless GIMP, gimp_textures.py helpers in scope).

"door" is a planar decal over the whole front (both doors): white with a fine pebbled
grain, a grey-brown scuff about a third of the way down the fresh-food door right of
centre, faint finger grime around the two grips and a few dark specks near the freezer
grip, as in the survey crops (fridge_2/3) and capture frames (wide_..._003938/003940).
The rest are flat fills sampled by eye; the toe grille gets dark slots.
"""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "fridge", "object.py")


def _consts():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    out = {}
    for node in tree.body:     # plain constant assignments, evaluated in order
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = eval(compile(ast.Expression(node.value), _OBJ, "eval"), {}, out)
            except Exception:
                pass
    return out


C = _consts()
ATLAS = C["ATLAS"]
W, H, SPLIT = C["W"], C["H"], C["SPLIT"]
rnd = random.Random(11)


def blot(img, lay, cx, cy, rx, ry, rgb, alpha, feather=0.0):
    img.select_ellipse(Gimp.ChannelOps.REPLACE, cx - rx, cy - ry, 2 * rx, 2 * ry)
    if feather:
        Gimp.Selection.feather(img, feather)
    if not Gimp.Selection.is_empty(img):
        _fill(lay, tuple(rgb) + (alpha,))
    Gimp.Selection.none(img)


def build():
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("door")
    sx, sz = w / W, h / H
    px = lambda X: x + (X + W / 2) * sx
    pz = lambda Z: y + (H - Z) * sz
    a.fill("door", (236, 236, 232), 0.0, 0.5, noise=0.025, blur=0.6)   # pebbled finish
    # scuff: a cluster of small grey-brown marks with a couple of scratch lines
    cx, cz = 5.5, 38.0
    for _ in range(9):
        blot(a.img, a.lay, px(cx + rnd.uniform(-0.6, 0.6)), pz(cz + rnd.uniform(-0.4, 0.4)), rnd.uniform(1.5, 4),
             rnd.uniform(1, 2.5), (128, 120, 108), rnd.uniform(0.35, 0.65), 1)
    Gimp.context_set_foreground(color((140, 134, 124)))
    Gimp.context_set_brush_size(1)
    for _ in range(3):
        X0, Z0 = cx + rnd.uniform(-0.8, 0.2), cz + rnd.uniform(-0.4, 0.4)
        Gimp.pencil(a.lay, [float(px(X0)), float(pz(Z0)), float(px(X0 + rnd.uniform(0.6, 1.2))), float(pz(Z0 + rnd.uniform(-0.3, 0.3)))])
    # finger grime around the grips (left edge), and a few specks near the freezer grip
    hx = -W / 2 + 1.2
    for z0, z1 in ((SPLIT - 12.0, SPLIT - 3.0), (SPLIT + 2.0, SPLIT + 8.0)):
        a.img.select_ellipse(Gimp.ChannelOps.REPLACE, px(hx - 1.2), pz(z1 + 1.0), 3.4 * sx, (z1 - z0 + 2.0) * sz)
        Gimp.Selection.feather(a.img, 8)
        _fill(a.lay, (196, 192, 182, 0.22))
        Gimp.Selection.none(a.img)
    for _ in range(8):
        blot(a.img, a.lay, px(hx + rnd.uniform(0.5, 3.0)), pz(SPLIT + rnd.uniform(1.0, 9.0)), 1.0, 1.0, (110, 100, 90),
             rnd.uniform(0.3, 0.6))
    a.fill("case", (230, 230, 226), 0.0, 0.5, noise=0.02, blur=0.6)
    a.fill("handle", (238, 238, 234), 0.0, 0.55)
    a.fill("gasket", (150, 150, 150), 0.0, 0.2)
    a.fill("grille", (26, 26, 28), 0.0, 0.3)
    gx, gy, gw, gh = a.rect("grille")
    for i in range(10):
        fill_rect(a.img, a.lay, (gx + 6 + i * 12, gy + 20, 6, gh - 40), (8, 8, 9))
    fill_rect(a.img, a.lay, (128, 384, 128, 128), (128, 128, 128))
    a.save()
