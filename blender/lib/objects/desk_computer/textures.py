"""desk_computer atlases, drawn from scratch in GIMP (no photo pixels, no logos, no screen
content). Black plastics, a tinted glass side with a faint pink interior glow, a thin
diagonal green-yellow LED strip on the tower front (emissive), keyboard key grid, a
pastel camouflage mouse pad, and six softly lit keys on the button pad. The screen
atlas is plain near-black glass."""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "desk_computer", "object.py")


def _get(name):
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise RuntimeError(name + " not found in object.py")


ATLAS = _get("ATLAS")
SCREEN_ATLAS = _get("SCREEN_ATLAS")


def line(img, lay, p0, p1, width, rgb):
    """Thick straight line from stacked small squares."""
    (x0, y0), (x1, y1) = p0, p1
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n):
        t = i / max(n - 1, 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        fill_rect(img, lay, (int(x - width / 2), int(y), max(1, int(width)), 2), rgb)


def build():
    a = Atlas(ATLAS)
    eimg, elay = a.glow_layer()
    fill_rect(eimg, elay, (0, 0, a.size, a.size), (0, 0, 0))

    a.fill("black", (20, 20, 22), 0.0, 0.35, noise=0.015)
    a.fill("grey", (40, 40, 43), 0.0, 0.3, noise=0.02)
    a.fill("laptop", (52, 53, 56), 0.2, 0.4, noise=0.02)
    a.fill("vent", (14, 14, 15), 0.0, 0.2)
    x, y, w, h = a.rect("vent")
    for i in range(0, w, 6):
        fill_rect(a.img, a.lay, (x + i, y, 2, h), (32, 32, 34))

    # tower front: matte black panel, LED strip from lower-left to upper-right
    x, y, w, h = a.rect("tower_front")
    a.fill("tower_front", (19, 19, 21), 0.0, 0.3, noise=0.012)
    p0, p1 = (x + w * 0.40, y + h - 6), (x + w * 0.80, y + 4)
    line(a.img, a.lay, p0, p1, 5, (200, 240, 90))
    line(eimg, elay, p0, p1, 6, (170, 255, 50))
    fill_ellipse(a.img, a.lay, (x + w - 22, y + 4, x + w - 16, y + 10), (80, 150, 255))
    fill_ellipse(eimg, elay, (x + w - 22, y + 4, x + w - 16, y + 10), (60, 130, 255))

    # glass side: dark smoked glass, faint glow of the parts inside
    x, y, w, h = a.rect("tower_glass")
    a.fill("tower_glass", (16, 15, 20), 0.0, 0.92)
    fill_rect(a.img, a.lay, (x + 14, y + h // 2 - 10, w - 40, 8), (30, 28, 34))   # GPU edge
    for (cx, cy, r, c) in ((0.45, 0.62, 7, (110, 35, 100)), (0.62, 0.3, 5, (30, 55, 110))):
        box = (x + int(cx * w) - r, y + int(cy * h) - r, x + int(cx * w) + r, y + int(cy * h) + r)
        fill_ellipse(a.img, a.lay, box, c)
        fill_ellipse(eimg, elay, box, tuple(v // 4 for v in c))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=3.0, std_dev_y=3.0)
    gegl(elay, "gegl:gaussian-blur", std_dev_x=6.0, std_dev_y=6.0)
    Gimp.Selection.none(a.img)

    # keyboard: key grid, front edge at the bottom of the region
    x, y, w, h = a.rect("keyboard")
    a.fill("keyboard", (14, 14, 15), 0.0, 0.3)
    rows = 6
    kh = (h - 10) // rows
    for r in range(rows):
        ky = y + 5 + r * kh
        n = 15 if r else 16
        main_w = int(w * 0.72)
        kw = main_w // n
        for k in range(n):
            fill_rect(a.img, a.lay, (x + 4 + k * kw, ky + 1, kw - 2, kh - 2), (26, 26, 28))
        for k in range(4):   # number pad
            fill_rect(a.img, a.lay, (x + main_w + 16 + k * 14, ky + 1, 12, kh - 2), (26, 26, 28))
    fill_rect(a.img, a.lay, (x, y + h - 3, w, 3), (150, 150, 155))   # light front edge (photo)

    # mouse pad: pastel camouflage blobs
    x, y, w, h = a.rect("mousepad")
    a.fill("mousepad", (112, 122, 140), 0.0, 0.1)
    random.seed(7)
    cols = ((70, 95, 150), (190, 120, 140), (170, 145, 105), (70, 72, 85), (200, 185, 170))
    for i in range(46):
        cx, cy = x + random.randint(0, w), y + random.randint(0, h)
        rx, ry = random.randint(6, 18), random.randint(4, 12)
        box = (max(x, cx - rx), max(y, cy - ry), min(x + w, cx + rx), min(y + h, cy + ry))
        if box[2] > box[0] and box[3] > box[1]:
            fill_ellipse(a.img, a.lay, box, random.choice(cols))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=1.5, std_dev_y=1.5)
    Gimp.Selection.none(a.img)
    fill_rect(a.img, a.lay, (x, y, w, 2), (40, 40, 45))
    fill_rect(a.img, a.lay, (x, y + h - 2, w, 2), (40, 40, 45))

    # button pad: six softly lit keys, 3 x 2
    x, y, w, h = a.rect("deck")
    a.fill("deck", (16, 16, 18), 0.0, 0.4)
    keyc = ((170, 190, 230), (230, 230, 235), (140, 200, 230), (230, 230, 235), (170, 190, 230), (200, 215, 235))
    kw, kh = w // 3, h // 2
    for i in range(6):
        c, r = i % 3, i // 3
        box = (x + c * kw + 8, y + r * kh + 10, kw - 16, kh - 20)
        fill_rect(a.img, a.lay, box, keyc[i])
        fill_rect(eimg, elay, box, tuple(v // 3 for v in keyc[i]))

    a.fill("screen", (8, 9, 11), 0.0, 0.85)
    a.save()
    s = Atlas(SCREEN_ATLAS)
    s.fill("screen", (8, 9, 11), 0.0, 0.88)
    s.save()
