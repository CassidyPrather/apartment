"""Top-freezer refrigerator: white case, freezer door over a fresh-food door, vertical
handles on the left (west) edge per the plan illustration, so the doors hinge on the
right against the center wall; black toe grille.

Source of truth: scripted. Coarse block-in; size and colour are EST (no photo of it
yet). Origin on the floor at the centre of the footprint (case plus doors, handles
excluded); front faces -Y. Place at plan (117.125, 273.4), rotation 0: in the 100-134 in
alcove on the north wall, 0.5 in off the center wall and 1 in off the back wall.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 32.75           # EST
D = 31.0            # EST case 28.5 + doors 2.5
H = 67.25           # EST (clears the 70 in over-fridge cabinet)
DOOR_T = 2.5        # EST
GRILLE_H = 3.5      # EST
SPLIT = 49.0        # EST freezer door bottom (freezer ~18 in tall)
GAP = 0.3           # EST reveal between the doors
HANDLE = (1.2, 1.0, 0.9)   # EST handle width, depth off the door, standoff

NAME = "fridge"
ATLAS = {
    "name": "fridge",
    "size": 512,
    "regions": {
        "case": (0, 0, 256, 256),
        "door": (256, 0, 256, 256),
        "handle": (0, 256, 128, 128),
        "gasket": (128, 256, 128, 128),
        "grille": (256, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"fridge": {"atlas": "fridge", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89, 1.0)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    yc = y0 + DOOR_T                               # case front
    bx("case", (x0, yc, 0.0), (x1, y1, H), 0.6)
    bx("grille", (x0 + 0.5, y0 + 1.5, 0.3), (x1 - 0.5, yc, GRILLE_H))
    # gasket band behind the doors
    bx("gasket", (x0 + 0.4, yc - 0.6, GRILLE_H + 0.2), (x1 - 0.4, yc, H - 0.4))
    doors = [(GRILLE_H + 0.2, SPLIT - GAP / 2), (SPLIT + GAP / 2, H - 0.2)]
    for z0, z1 in doors:
        bx("door", (x0, y0, z0), (x1, yc - 0.6, z1), 0.8)
    hw, hd, hs = HANDLE
    hx = x0 + 2.0
    # fridge handle on the upper part of the lower door, freezer handle low on the top door
    for z0, z1 in ((SPLIT - 16.0, SPLIT - 3.0), (SPLIT + 2.0, SPLIT + 11.0)):
        bx("handle", (hx - hw / 2, y0 - hs - hd, z0), (hx + hw / 2, y0 - hs, z1), 0.3)
        for zz in (z0 + 0.6, z1 - 1.6):
            bx("handle", (hx - hw / 2 + 0.2, y0 - hs - 0.1, zz), (hx + hw / 2 - 0.2, y0 + 0.1, zz + 1.0))
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
