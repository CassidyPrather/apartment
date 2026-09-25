"""couch_blankets atlas, drawn in GIMP: chocolate fleece, a dark throw with scattered
beige leaves, a white blanket with a small cartoon-bunny print (simple heads and
ears, drawn from scratch), and a soft blue-violet tie-dye. Colours from the photo
crops, lifted from their dim exposure."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "couch_blankets", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
R = random.Random(77)


def soften(a, region, sigma):
    x, y, w, h = a.rect(region)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=sigma, std_dev_y=sigma)
    Gimp.Selection.none(a.img)


def build():
    a = Atlas(ATLAS)
    img, lay = a.img, a.lay

    # chocolate fleece
    a.fill("brown_fleece", (78, 52, 36), 0.0, 0.05, noise=0.06, blur=2.0)

    # dark throw with beige leaves
    x0, y0, w, h = a.rect("leaf_print")
    fill_rect(img, lay, (x0, y0, w, h), (62, 44, 32))
    for _ in range(26):          # sprays of long leaves
        sx, sy = x0 + R.randint(30, w - 30), y0 + R.randint(30, h - 30)
        vertical = R.random() < 0.5
        for k in range(R.randint(3, 6)):
            cx, cy = sx + R.randint(-34, 34), sy + R.randint(-34, 34)
            lw, lh = (R.randint(46, 80), R.randint(14, 22))
            if vertical:
                lw, lh = lh, lw
            col = R.choice([(206, 190, 154), (186, 168, 128), (222, 210, 180)])
            fill_ellipse(img, lay, (max(cx - lw // 2, x0), max(cy - lh // 2, y0),
                                    min(cx + lw // 2, x0 + w), min(cy + lh // 2, y0 + h)), col)
    grain(img, lay, (x0, y0, w, h), 0.04, 1.5)
    soften(a, "leaf_print", 0.8)
    a.material("leaf_print", 0.0, 0.08)

    # white bunny print
    x0, y0, w, h = a.rect("white_bunny")
    fill_rect(img, lay, (x0, y0, w, h), (230, 226, 218))
    step = 128
    k = 2.3                      # bunnies ~10 in apart, heads ~5 in across
    for gy in range(0, h, step):
        for gx in range(0, w, step):
            cx = x0 + gx + 64 + (32 if (gy // step) % 2 else 0) + R.randint(-10, 10)
            cy = y0 + gy + 74 + R.randint(-10, 10)
            if not (x0 + 34 < cx < x0 + w - 34 and y0 + 62 < cy < y0 + h - 30):
                continue
            grey = (160, 154, 160)
            E = lambda a, b, c, d, col: fill_ellipse(
                img, lay, (int(cx + a * k), int(cy + b * k), int(cx + c * k), int(cy + d * k)), col)
            for ex in (-6, 6):   # ears
                E(ex - 5, -26, ex + 5, -6, grey)
                E(ex - 3, -23, ex + 3, -8, (232, 176, 186))
            E(-13, -11, 13, 11, grey)
            E(-11.8, -9.8, 11.8, 9.8, (236, 232, 226))
            for ex in (-8, 8):   # cheeks and eyes
                E(ex - 3, 1, ex + 3, 5, (236, 178, 188))
                E(ex * 0.6 - 1, -3, ex * 0.6 + 1, -1, (120, 110, 115))
    grain(img, lay, (x0, y0, w, h), 0.03, 1.0)
    soften(a, "white_bunny", 0.6)
    a.material("white_bunny", 0.0, 0.08)

    # blue-violet tie-dye
    x0, y0, w, h = a.rect("blue_tiedye")
    fill_rect(img, lay, (x0, y0, w, h), (122, 132, 196))
    for _ in range(45):
        cx, cy = x0 + R.randint(0, w), y0 + R.randint(0, h)
        rad = R.randint(20, 60)
        col = R.choice([(156, 126, 196), (96, 156, 196), (190, 156, 206), (88, 104, 176),
                        (170, 196, 220)])
        fill_ellipse(img, lay, (max(cx - rad, x0), max(cy - rad, y0),
                                min(cx + rad, x0 + w), min(cy + rad, y0 + h)), col)
    soften(a, "blue_tiedye", 14.0)
    grain(img, lay, (x0, y0, w, h), 0.04, 1.5)
    a.material("blue_tiedye", 0.0, 0.08)
    a.save()
