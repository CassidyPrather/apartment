"""Freestanding 30 in electric coil range: white enamel body, backguard with knobs,
four coil burners on chrome drip pans, oven door with window and bar handle, storage
drawer at the bottom.

Source of truth: scripted. Coarse block-in; no model-specific reference yet (the
colour and control layout are guesses: the photo doesn't show the range, the plan
illustration shows a white coil-top range). Origin on the floor at the centre of the
body footprint (backguard included, handle excluded); front faces -Y.
Place at plan (71.0, 275.4), rotation 0: centred in the 56-86 in gap on the north wall,
0.5 in off the wall.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 29.875          # EST standard 30 in slot range
D = 28.0            # EST body incl. backguard, door front to back
H = 36.0            # EST cooktop height (matches the counters)
GUARD_H = 10.0      # EST backguard rises to 46
GUARD_D = 3.0       # EST
DRAWER = (1.0, 7.0)     # EST storage drawer z
DOOR = (7.5, 30.5)      # EST oven door z
WINDOW = (14.0, 25.5, 7.0)   # EST window z0, z1 and side inset
HANDLE_Z = 28.8         # EST
BURNERS = [(-7.0, -5.5, 4.0), (7.0, -5.5, 3.0), (-7.0, 6.0, 3.0), (7.0, 6.0, 4.0)]  # EST x, y, radius (8/6 in coils)

NAME = "range"
ATLAS = {
    "name": "range",
    "size": 512,
    "regions": {
        "enamel": (0, 0, 256, 256),
        "cooktop": (256, 0, 256, 256),
        "glass": (0, 256, 256, 128),
        "chrome": (256, 256, 128, 128),
        "coil": (384, 256, 128, 128),
        "knob": (0, 384, 128, 128),
        "trim_black": (128, 384, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"range": {"atlas": "range", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89, 1.0)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    # body (behind the door and drawer fronts) and toe recess
    bx("enamel", (x0, y0 + 1.0, 1.0), (x1, y1, H - 0.6))
    bx("trim_black", (x0 + 1.0, y0 + 3.0, 0.0), (x1 - 1.0, y1 - 1.0, 1.0))
    # cooktop plate, backguard
    bx("cooktop", (x0, y0 + 0.5, H - 0.6), (x1, y1 - GUARD_D, H), 0.3)
    bx("enamel", (x0, y1 - GUARD_D, H - 0.6), (x1, y1, H + GUARD_H), 0.3)
    bx("trim_black", (x0 + 1.5, y1 - GUARD_D - 0.05, H + 2.5), (x1 - 1.5, y1 - GUARD_D + 0.2, H + GUARD_H - 2.0))
    for i, kx in enumerate((-11.5, -6.5, 0.0, 6.5, 11.5)):
        b.cylinder("knob", (m(kx), m(y1 - GUARD_D - 0.6), m(H + 5.5)), m(1.0), m(1.2), axis="Y", segments=12)
    # burners: drip pan (chrome) and coil (a thin dark ring disc)
    for bxp, byp, r in BURNERS:
        b.cylinder("chrome", (m(bxp), m(byp), m(H + 0.05)), m(r + 1.0), m(0.2), segments=16)
        b.cylinder("coil", (m(bxp), m(byp), m(H + 0.35)), m(r), m(0.35), segments=16)
    # oven door with window, handle; storage drawer
    dy = y0
    bx("enamel", (x0 + 0.1, dy, DOOR[0]), (x1 - 0.1, dy + 1.2, DOOR[1]), 0.35)
    wi = WINDOW[2]
    bx("glass", (x0 + wi, dy - 0.05, WINDOW[0]), (x1 - wi, dy + 0.3, WINDOW[1]))
    bx("trim_black", (x0 + 0.1, dy + 0.2, DOOR[1]), (x1 - 0.1, y0 + 1.2, DOOR[1] + 1.2))   # vent gap
    b.cylinder("chrome", (0, m(dy - 1.6), m(HANDLE_Z)), m(0.45), m(W - 5.0), axis="X", segments=10)
    for hx in (-(W - 6.0) / 2, (W - 6.0) / 2):
        bx("chrome", (hx - 0.4, dy - 1.6, HANDLE_Z - 0.4), (hx + 0.4, dy, HANDLE_Z + 0.4))
    bx("enamel", (x0 + 0.1, dy, DRAWER[0]), (x1 - 0.1, dy + 1.0, DRAWER[1]), 0.3)
    bx("trim_black", (-4.0, dy - 0.3, DRAWER[1] - 1.8), (4.0, dy, DRAWER[1] - 1.1))
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
