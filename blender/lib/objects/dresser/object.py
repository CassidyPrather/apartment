"""Dresser: a honey-oak five-drawer chest against the east wall at the SE corner of the
bedroom. Plain slab drawer fronts set between the side panels, each with a routed
finger-groove pull along its top edge (the photos show no knobs), a flush top and a
low recessed toe kick.

Source of truth: scripted from the LiDAR survey and the survey crops. Origin on the
floor at the footprint centre; front faces -Y. Place at plan (264.75, 18), rotation -90
(front faces west; local +X is south).

Dimensions (inches):
  width 34, depth 19.5, height 58.5     SCAN (survey box 254-274.5 x 0.5-36, top 58-59.7)
  side/top panel thickness 0.75          EST
  toe kick 2.0 tall, recessed 1.0        EST from photo
  5 equal drawers, 0.2 gaps              EST from photo (equal heights)
  drawer front proud 0.0, set back 0.1   EST
  finger groove 0.6 tall, 0.4 deep     EST from photo (dark line at each drawer top)
"""

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "dresser"
W, D, H = 34.0, 19.5, 58.5
T = 0.75
KICK, KICK_IN = 2.0, 1.0
N_DRAWERS = 5
GAP = 0.2
GROOVE_H, GROOVE_D = 0.6, 0.4

ATLAS = {
    "name": "dresser",
    "size": 512,
    "regions": {
        "front": (0, 0, 256, 256),       # horizontal grain
        "side": (256, 0, 256, 256),      # vertical grain
        "top": (0, 256, 256, 256),       # grain along X
        "dark": (256, 256, 128, 128),    # grooves, gaps, back, toe kick
        "edge": (384, 256, 128, 128),    # end grain / drawer edges
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dresser": {"atlas": "dresser", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front", 340, 15, 1.0), ("photo_left", 300, 15, 1.0)]


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, lo, hi, bev=0.0: b.box(r, tuple(map(m, lo)), tuple(map(m, hi)), bevel=m(bev))
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    # sides, top, back
    bx("side", (x0, y0, 0), (x0 + T, y1, H - T))
    bx("side", (x1 - T, y0, 0), (x1, y1, H - T))
    bx("top", (x0, y0, H - T), (x1, y1, H), 0.12)
    bx("dark", (x0 + T, y1 - 0.3, 0), (x1 - T, y1, H - T))
    # toe kick and the dark cavity behind the drawer fronts
    bx("dark", (x0 + T, y0 + KICK_IN, 0), (x1 - T, y0 + KICK_IN + 0.5, KICK))
    bx("dark", (x0 + T, y0 + 0.9, KICK), (x1 - T, y0 + 1.2, H - T))
    # drawer fronts, each with a routed groove along its top
    ih = (H - T - KICK - GAP * N_DRAWERS) / N_DRAWERS
    fx0, fx1 = x0 + T + GAP / 2, x1 - T - GAP / 2
    fy0, fy1 = y0 + 0.1, y0 + 0.9
    for i in range(N_DRAWERS):
        z0 = KICK + GAP / 2 + i * (ih + GAP)
        z1 = z0 + ih
        bx("front", (fx0, fy0, z0), (fx1, fy1, z1 - GROOVE_H), 0.08)
        bx("dark", (fx0, fy0 + GROOVE_D, z1 - GROOVE_H), (fx1, fy1, z1))
        bx("edge", (fx0, fy0, z1 - 0.12), (fx1, fy0 + GROOVE_D, z1))   # thin lip above the groove
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    planar = {"front": ("-Y", (m(-W / 2), m(W / 2)), (0.0, m(H)))}
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
