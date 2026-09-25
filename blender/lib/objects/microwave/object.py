"""Over-the-range microwave: white case, drop-down vent grille band across the top front,
a door with a large grey-screened window and a tall curved pull handle on its right, and
a control column on the right with a small black display and a light keypad. Dark vent
and light lens on the underside. No badge (plain appliance front).

Source of truth: scripted. Size from the living-room/kitchen LiDAR survey, layout and
colour from the survey photo crops. ORIGIN AT THE BOTTOM of the case, centre of the
footprint; front faces -Y.
Place at plan (64, 276.5), rotation 0, origin height Z 58.5 in (top at 76, under the short
uppers): footprint x 50-78, y 268.5-284.5.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 28.0            # SCAN
D = 16.0            # SCAN (incl. the door and handle)
H = 17.5            # SCAN
DOOR_T = 1.0        # EST
VENT_H = 3.2        # PHOTO top grille band
CTRL_W = 6.0        # PHOTO control column width
WIN = (2.0, 2.5, 5.5, 3.5)   # PHOTO window inset: left, bottom, right, top (from the door edges)
GAP = 0.15          # EST

NAME = "microwave"
ATLAS = {
    "name": "microwave",
    "size": 512,
    "regions": {
        "white": (0, 0, 256, 256),
        "window": (256, 0, 256, 128),
        "keypad": (256, 128, 128, 128),
        "display": (384, 128, 128, 64),
        "vent": (384, 192, 128, 64),
        "under": (0, 256, 256, 128),
        "lens": (256, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"microwave": {"atlas": "microwave", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 330, 8, 0.9)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    yf = y0 + DOOR_T + 0.8                       # case front (behind door and handle)
    bx("white", (x0, yf, 0.3), (x1, y1, H), 0.3)
    bx("under", (x0 + 1.0, yf + 0.5, 0.0), (x1 - 1.0, y1 - 1.0, 0.3))
    for lx in (-8.0, 8.0):
        bx("lens", (lx - 1.5, yf + 1.5, -0.05), (lx + 1.5, yf + 4.0, 0.05))
    # vent band on top, full width
    zt = H - VENT_H
    bx("white", (x0, y0 + 0.8, zt + GAP), (x1, yf, H), 0.25)
    bx("vent", (x0 + 3.0, y0 + 0.75, zt + 0.9), (x1 - 3.0, y0 + 0.85, zt + 2.2))
    # door (left) and control column (right)
    dx1 = x1 - CTRL_W
    bx("white", (x0, y0 + 0.8, 0.3), (dx1 - GAP, yf, zt - GAP), 0.3)
    l, bt, r, t = WIN
    bx("window", (x0 + l, y0 + 0.75, bt + 0.3), (dx1 - r, y0 + 0.85, zt - t))
    bx("white", (dx1 + GAP, y0 + 0.8, 0.3), (x1, yf, zt - GAP), 0.2)
    bx("display", (dx1 + 1.2, y0 + 0.75, zt - 3.2), (x1 - 1.6, y0 + 0.85, zt - 2.0))
    bx("keypad", (dx1 + 0.8, y0 + 0.75, 1.5), (x1 - 0.8, y0 + 0.85, zt - 4.0))
    # curved pull handle near the door's right edge
    hx = dx1 - 2.4
    path = common.smooth_path([(m(hx), m(y0 + 0.8), m(2.5)), (m(hx), m(y0), m(4.0)),
                               (m(hx), m(y0), m(zt - 4.0)), (m(hx), m(y0 + 0.8), m(zt - 2.5))], samples=3)
    b.sweep("white", path, common.rect_profile(m(1.1), m(0.6)), up=(1, 0, 0))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
