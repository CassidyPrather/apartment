"""Floor clutter under the TV: a black plastic toolbox with yellow lid panels and
latches (south), a carton of copy paper (north) with a black power strip on top.
No brand text: the carton gets a plain white/blue triangle print, no words.

Source of truth: scripted from the LiDAR survey (toolbox y 54-74 up to z ~11.5; carton
y 76-96 at z ~9.5; both against the wall) and the survey crops. Origin on the floor at
the footprint centre; front faces -Y, back (+Y) toward the wall; +X local is south
once placed. Place at plan (128, 75), rotation -90.
"""

import math

from mathutils import Matrix

import common

IN = 0.0254


def m(v):
    return v * IN


D = 12.0              # SCAN group depth off the wall
TB = (20.0, 10.5, 9.5)      # EST toolbox body L, D, H (typical 20 in box), SCAN L 20
TB_X = 11.0           # SCAN centre offset along the wall
CARTON = (17.5, 11.25, 9.5)   # SPEC-ish paper case, SCAN y 77.5-95, z 9.5
CARTON_X = -11.25
STRIP = (13.0, 2.2, 1.3)    # EST power strip

NAME = "toolboxes"
ATLAS = {
    "name": "toolboxes",
    "size": 512,
    "regions": {
        "black": (0, 0, 256, 256),
        "yellow": (256, 0, 128, 128),
        "strip": (384, 0, 128, 128),
        "carton_side": (0, 256, 256, 256),
        "carton_top": (256, 256, 256, 256),
        "carton_edge": (256, 128, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"toolboxes": {"atlas": "toolboxes", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_sw", 330, 35, 0.9)]


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    # toolbox
    L, d, h = TB
    x0, x1 = TB_X - L / 2, TB_X + L / 2
    y1 = D / 2 - 0.75
    y0 = y1 - d
    bx("black", (x0, y0, 0.0), (x1, y1, h - 2.5), 0.4)          # tub
    bx("black", (x0 - 0.2, y0 - 0.2, h - 2.6), (x1 + 0.2, y1 + 0.2, h), 0.5)   # lid
    for s in (-1, 1):
        cx = TB_X + s * (L / 2 - 3.5)
        bx("yellow", (cx - 3.0, y0 + 0.8, h - 0.05), (cx + 3.0, y1 - 0.8, h + 0.3), 0.15)
        bx("yellow", (cx - 1.1, y0 - 0.55, h - 3.4), (cx + 1.1, y0 - 0.1, h - 1.2), 0.1)   # latch
    # handle
    bx("black", (TB_X - 4.0, (y0 + y1) / 2 - 0.6, h), (TB_X + 4.0, (y0 + y1) / 2 + 0.6, h + 1.3), 0.3)
    # paper carton
    L, d, h = CARTON
    cx0, cx1 = CARTON_X - L / 2, CARTON_X + L / 2
    cy1 = D / 2 - 0.25
    cy0 = cy1 - d
    bx("carton_side", (cx0, cy0, 0.0), (cx1, cy1, h - 0.1))
    bx("carton_top", (cx0 + 0.02, cy0 + 0.02, h - 0.1), (cx1 - 0.02, cy1 - 0.02, h))
    # power strip lying across the carton, slightly skewed
    sl, sw, sh = STRIP
    rot = Matrix.Translation((m(CARTON_X), m(cy0 + 3.0), m(h))) @ Matrix.Rotation(math.radians(-8), 4, "Z")
    b.box("strip", (m(-sl / 2), m(-sw / 2), 0.0), (m(sl / 2), m(sw / 2), m(sh)), matrix=rot)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    L, d, h = CARTON
    planar = {"carton_top": ("+Z", (m(CARTON_X - L / 2), m(CARTON_X + L / 2)),
                             (m(D / 2 - 0.25 - d), m(D / 2 - 0.25)))}
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
