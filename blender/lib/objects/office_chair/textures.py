"""office_chair atlas, drawn from scratch in GIMP (no photo pixels): navy woven fabric,
tan cotton cloth with soft vertical fold shading, black plastics, dark chrome, and a
pale clear-plastic tint for the chair mat, black perforated back mesh, brown microsuede
seat cushion with black piping. Colours sampled by eye from the survey crops and the
scan's close-up keyframes. Wear, only what the close-ups show: lint and pilling on the
navy seat fabric, flattened darker sitting marks on the cushion, dusty specks on the arm
pads and base, and a cloudy scuffed ring on the mat where the casters roll."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "office_chair", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()


def specks(a, lay, region, n, rgb, alpha, seed, size=(1, 2), area=(0, 0, 1, 1)):
    rnd = random.Random(seed)
    x, y, w, h = a.rect(region)
    ax, ay, aw, ah = area
    for _ in range(n):
        cx = int(x + w * (ax + aw * rnd.random()))
        cy = int(y + h * (ay + ah * rnd.random()))
        sz = rnd.randint(*size)
        fill_ellipse(a.img, lay, (cx, cy, cx + sz, cy + sz), rgb + (rnd.uniform(*alpha),))


def build():
    a = Atlas(ATLAS)
    # navy woven seat fabric: fine weave, pilled mottling, lint specks
    a.fill("fabric", (24, 32, 58), 0.0, 0.08, noise=0.025, blur=1.0)
    x, y, w, h = a.rect("fabric")
    for i in range(0, h, 3):                                   # weave rows
        fill_rect(a.img, a.lay, (x, y + i, w, 1), (18, 25, 48, 0.35))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 2.5)               # pilling mottle
    specks(a, a.lay, "fabric", 140, (120, 124, 140), (0.15, 0.4), 21)
    # the seat's front band reads a touch faded and fuzzier where legs rub
    fill_rect(a.img, a.lay, (x, y + int(h * 0.72), w, int(h * 0.12)), (70, 80, 110, 0.12))
    # tan jacket
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
    # black plastics with a little dust on the base
    a.fill("plastic", (22, 22, 24), 0.0, 0.3, noise=0.015)
    specks(a, a.lay, "plastic", 60, (90, 88, 86), (0.1, 0.3), 22)
    a.fill("metal", (60, 60, 64), 0.9, 0.6)
    # arm pads: black soft-touch, dusty with lint, rubbed lighter along the edges
    a.fill("pad", (18, 18, 20), 0.0, 0.2, noise=0.02)
    x, y, w, h = a.rect("pad")
    for bx0, bw in ((x, 10), (x + w - 10, 10)):
        fill_rect(a.img, a.lay, (bx0, y, bw, h), (60, 60, 64, 0.35))
    specks(a, a.lay, "pad", 90, (120, 120, 122), (0.12, 0.35), 23)
    # back mesh: black, staggered perforations
    a.fill("mesh", (40, 40, 44), 0.0, 0.15)
    x, y, w, h = a.rect("mesh")
    for j, yy in enumerate(range(y, y + h, 3)):
        off = 1 if j % 2 else 0
        for xx in range(x + off, x + w - 1, 3):
            fill_rect(a.img, a.lay, (xx, yy, 2, 2), (8, 8, 10))
    # brown microsuede seat cushion (planar: rect = the cushion's top), black piping
    x, y, w, h = a.rect("cushion")
    a.fill("cushion", (74, 52, 46), 0.0, 0.12, noise=0.03, blur=1.5)
    for i in range(10):                                         # nap direction streaks
        yy = y + random.randint(8, h - 12)
        fill_rect(a.img, a.lay, (x + 6, yy, w - 12, random.randint(2, 6)), (64, 44, 39, 0.35))
    # flattened, darker sitting marks in the middle (photo: darker creases)
    fill_ellipse(a.img, a.lay, (x + w * 0.2, y + h * 0.25, x + w * 0.8, y + h * 0.85), (70, 46, 38, 0.35))
    for k in range(5):
        cx = x + w * (0.3 + 0.1 * k)
        fill_rect(a.img, a.lay, (int(cx), y + int(h * 0.3), 2, int(h * 0.45)), (58, 38, 32, 0.4))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x + 4, y + 4, w - 8, h - 8)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=3.0, std_dev_y=3.0)
    Gimp.Selection.none(a.img)
    # piping: a dark ring ~0.35 in inside the edge, where the crown steps in (the
    # outermost px stay brown for the sides, which sample the rect's border)
    for (px, py, pw, ph) in ((x + 6, y + 5, w - 12, 3), (x + 6, y + h - 8, w - 12, 3),
                             (x + 5, y + 6, 3, h - 12), (x + w - 8, y + 6, 3, h - 12)):
        fill_rect(a.img, a.lay, (px, py, pw, ph), (22, 16, 14))
    # chair mat: pale clear plastic, cloudy scuffed ring where the casters roll
    a.fill("mat", (215, 222, 226), 0.0, 0.8)
    x, y, w, h = a.rect("mat")
    cx, cy = x + w * 0.47, y + h * 0.45
    fill_ellipse(a.img, a.lay, (cx - 34, cy - 30, cx + 34, cy + 30), (240, 240, 238, 0.5))
    fill_ellipse(a.img, a.lay, (cx - 20, cy - 18, cx + 20, cy + 18), (225, 228, 230, 0.6))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=6.0, std_dev_y=6.0)
    Gimp.Selection.none(a.img)
    specks(a, a.lay, "mat", 50, (150, 146, 140), (0.2, 0.5), 24)
    x2 = a.rect("mat")
    a.mimg.select_ellipse(Gimp.ChannelOps.REPLACE, cx - 34, cy - 30, 68, 60)
    a.mlay.edit_clear()                                       # scuffed: less glossy
    _fill(a.mlay, (0, 0, 0, 0.45))
    Gimp.Selection.none(a.mimg)
    a.save()
