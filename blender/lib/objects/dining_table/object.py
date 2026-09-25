"""Dining table: dark charcoal-stained wood, a plain rectangular top on four square legs
joined by a deep apron. Long axis runs along local Y (north-south in the room).

Source of truth: scripted. Sizes from the living-room survey scan (LiDAR + splat
registered to the plan) and the survey photos. Origin on the floor at the footprint
centre; front faces -Y. Place at plan (85, 205), rotation 0.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 38.0            # SCAN top x extent 66.1-104.0
D = 61.0            # SCAN top y extent (inventory box)
H = 29.5            # SCAN top surface median 29.5
TOP_T = 1.25        # EST photo: thin slab edge
LEG = 2.5           # EST photo; scan leg clusters ~2-3 in wide
LEG_INSET = 1.5     # SCAN leg centres ~3 in in from the top edges
APRON_H = 3.5       # EST photo
APRON_T = 0.9       # EST
APRON_INSET = 0.4   # EST apron face set back from the leg face

NAME = "dining_table"
ATLAS = {
    "name": "dining_table",
    "size": 1024,
    "regions": {
        "wood_v": (0, 0, 512, 1024),     # grain along V
        "wood_h": (512, 0, 512, 512),    # grain along U
        "end": (512, 512, 256, 256),     # end grain / undersides
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dining_table": {"atlas": "dining_table", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89, 1.0), ("photo_nw", 215, 30, 0.9), ("low_se", 35, 8, 0.9)]


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0, seg=1: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg)
    x1, y1 = W / 2, D / 2
    zt = H - TOP_T
    bx("wood_v", (-x1, -y1, zt), (x1, y1, H), 0.25, 2)
    lx = x1 - LEG_INSET
    ly = y1 - LEG_INSET
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (lx - LEG / 2), sy * (ly - LEG / 2)
            bx("wood_v", (cx - LEG / 2, cy - LEG / 2, 0.0), (cx + LEG / 2, cy + LEG / 2, zt), 0.12)
    za = zt - APRON_H
    ax = lx - APRON_INSET
    ay = ly - APRON_INSET
    # long aprons (along Y) and short aprons (along X), between the legs
    for s in (-1, 1):
        bx("wood_h", (s * ax - APRON_T / 2 - s * APRON_T / 2, -ly + LEG, za),
           (s * ax + APRON_T / 2 - s * APRON_T / 2, ly - LEG, zt))
        bx("wood_h", (-lx + LEG, s * ay - APRON_T / 2 - s * APRON_T / 2, za),
           (lx - LEG, s * ay + APRON_T / 2 - s * APRON_T / 2, zt))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
