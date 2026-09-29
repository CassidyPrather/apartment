"""Top-freezer refrigerator: white case, freezer door over a fresh-food door with a fine
pebbled finish, short vertical pull grips near the left (west) edge (freezer grip low on the
freezer door, fresh-food grip high on the lower door), so the doors hinge on the right
against the center wall (white middle hinge bracket between the doors); black toe grille.

Source of truth: scripted. Size from the living-room/kitchen LiDAR survey, colour, door
split and hardware from the survey crops (fridge_2/3) and the capture frames
(wide_..._003938/003940 side-on, _004359 across the room). Wear, as seen: a grey-brown
scuff about a third of the way down the fresh-food door right of centre, faint grime
around both grips. The magnets and papers on the doors are not modelled (personal items). Origin on the floor at the centre of the footprint
(case, doors and handles); front faces -Y. Place at plan (116.25, 267.5), rotation 0:
x 102-130.5, handle front at y 250, back at y 285.
"""

import math

from mathutils import Vector

import common

IN = 0.0254


def m(v):
    return v * IN


W = 28.5            # SCAN
D = 35.0            # SCAN incl. doors and handles (case 31.5 + doors 2.5 + handles 1)
H = 66.0            # SCAN
DOOR_T = 2.5        # EST
GRILLE_H = 3.5      # EST
SPLIT = 45.5        # PHOTO freezer door bottom (freezer door ~20 in, about a third)
GAP = 0.3           # EST reveal between the doors
HANDLE = (1.2, 0.6, 0.4)   # PHOTO short grips on the left door edge; EST width, depth, standoff

NAME = "fridge"
ATLAS = {
    "name": "fridge",
    "size": 512,
    "regions": {
        "case": (0, 0, 256, 256),
        "door": (256, 0, 256, 512),
        "handle": (0, 256, 128, 128),
        "gasket": (128, 256, 128, 128),
        "grille": (0, 384, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"fridge": {"atlas": "fridge", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89, 1.0), ("photo", -20, 12, 0.8)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    hw, hd, hs = HANDLE
    y0 = y0 + hd + hs                              # door front (handles stick out past it)
    yc = y0 + DOOR_T                               # case front
    bx("case", (x0, yc, 0.0), (x1, y1, H), 0.6)
    bx("grille", (x0 + 0.5, y0 + 1.5, 0.3), (x1 - 0.5, yc, GRILLE_H))
    # gasket band behind the doors
    bx("gasket", (x0 + 0.4, yc - 0.6, GRILLE_H + 0.2), (x1 - 0.4, yc, H - 0.4))
    doors = [(GRILLE_H + 0.2, SPLIT - GAP / 2), (SPLIT + GAP / 2, H - 0.2)]
    for z0, z1 in doors:
        bx("door", (x0, y0, z0), (x1, yc - 0.6, z1), 0.8)
    # short C-shaped grips standing off the doors near the left edge
    hx = x0 + 1.2
    prof = [(m(0.3) * math.cos(a), m(0.5) * math.sin(a)) for a in [i * math.pi / 6 for i in range(12)]]
    for z0, z1 in ((SPLIT - 12.0, SPLIT - 3.0), (SPLIT + 2.0, SPLIT + 8.0)):
        pts = [(hx, y0 + 0.1, z0), (hx, y0 - hs - hd / 2 + 0.1, z0 + 1.0), (hx, y0 - hs - hd / 2 + 0.1, z1 - 1.0), (hx, y0 + 0.1, z1)]
        path = common.smooth_path([Vector(tuple(map(m, p))) for p in pts], samples=2)
        b.sweep("handle", path, prof, up=(1, 0, 0))
    # middle hinge bracket on the right, between the doors
    bx("handle", (x1 - 1.6, y0 + 0.2, SPLIT - 0.6), (x1 + 0.0, yc, SPLIT + 0.6), 0.1)
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS, planar={"door": ("-Y", (m(-W / 2), m(W / 2)), (0.0, m(H)))})
    common.collapse_materials(ob, {r: mat for r in REGIONS})
