"""Dresser: a solid honey-oak five-drawer chest against the east wall at the SE corner of
the bedroom. Slab drawer fronts set back between the side panels; there are no knobs:
each front has a chamfered top edge and a bevelled underside that together read as the
dark finger-pull gap between drawers. Flush top, bottom drawer almost on the floor over
a shallow shadow recess.

Source of truth: scripted from the LiDAR survey and the survey crops, refined from the
sharp capture frames wide_..011937 (front) and wide_..012006 (left side) copied to
Reference/dresser_work/src_front.jpg and src_side.jpg. Origin on the floor at the
footprint centre; front faces -Y. Place at plan (264.75, 18), rotation -90 (front faces
west; local +X is south).

Dimensions (inches):
  width 34, depth 19.5, height 58.5     SCAN (survey box 254-274.5 x 0.5-36, top 58-59.7)
  side/top panel thickness 0.75          EST (photo: edge ~ 1/45 of the width)
  base recess 0.75 tall, 0.4 deep        EST from photo (bottom drawer nearly on the floor)
  5 equal drawers, 0.25 gaps             EST from photo (equal heights)
  drawer fronts 0.8 thick, set back 0.35 EST from photo (shadow line inside the sides)
  top chamfer 0.25, underside bevel 0.55 EST from photo (light line over a dark gap)
"""

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "dresser"
W, D, H = 34.0, 19.5, 58.5
T = 0.75
KICK, KICK_IN = 0.75, 0.4
N_DRAWERS = 5
GAP = 0.25
FRONT_T, FRONT_SET = 0.8, 0.35
CHAMFER, UNDERCUT = 0.25, 0.55

ATLAS = {
    "name": "dresser",
    "size": 1024,
    "regions": {
        "front": (0, 0, 512, 1024),      # photo drawer fronts, planar over the whole front
        "top": (512, 0, 512, 320),       # photo grain along X
        "side": (512, 320, 256, 704),    # photo side panel, vertical grain
        "dark": (768, 320, 128, 128),    # gaps, back, cavity, base recess
        "edge": (896, 320, 128, 128),    # panel front edges (worn, lighter)
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dresser": {"atlas": "dresser", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front", 340, 15, 1.0), ("photo_left", 300, 15, 1.0),
         ("photo_high", 330, 30, 0.75)]


def drawer_rows():
    ih = (H - T - KICK - GAP * N_DRAWERS) / N_DRAWERS
    return [(KICK + GAP / 2 + i * (ih + GAP), KICK + GAP / 2 + i * (ih + GAP) + ih)
            for i in range(N_DRAWERS)]


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, lo, hi, bev=0.0, seg=2: b.box(r, tuple(map(m, lo)), tuple(map(m, hi)),
                                                 bevel=m(bev), segments=seg)
    x0, x1, y0, y1 = -W / 2, W / 2, -D / 2, D / 2
    # sides (slightly eased front edges), top, back
    bx("side", (x0, y0, 0), (x0 + T, y1, H - T), 0.06, 1)
    bx("side", (x1 - T, y0, 0), (x1, y1, H - T), 0.06, 1)
    bx("top", (x0, y0, H - T), (x1, y1, H), 0.12)
    bx("dark", (x0 + T, y1 - 0.3, 0), (x1 - T, y1, H - T))
    # shallow base recess and the dark cavity behind the drawer fronts
    bx("dark", (x0 + T, y0 + FRONT_SET + KICK_IN, 0), (x1 - T, y0 + FRONT_SET + KICK_IN + 0.5, KICK))
    fy1 = y0 + FRONT_SET + FRONT_T
    bx("dark", (x0 + T, fy1, KICK), (x1 - T, fy1 + 0.3, H - T))
    # thin rail under the top, set back like the fronts
    bx("edge", (x0 + T, y0 + FRONT_SET - 0.05, H - T - 0.1), (x1 - T, fy1, H - T))
    # drawer fronts: a slab profile swept along X, chamfered on top, bevelled underneath
    fx0, fx1 = x0 + T + GAP / 2, x1 - T - GAP / 2
    for z0, z1 in drawer_rows():
        h = z1 - z0
        prof = [(0.0, 0.0), (FRONT_T - UNDERCUT, 0.0), (FRONT_T, UNDERCUT * 0.8),
                (FRONT_T, h - CHAMFER), (FRONT_T - CHAMFER, h), (0.0, h)]
        b.sweep("front", [(m(fx0), m(fy1), m(z0)), (m(fx1), m(fy1), m(z0))],
                [(m(s), m(u)) for s, u in prof])
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    planar = {"front": ("-Y", (m(-W / 2), m(W / 2)), (0.0, m(H)))}
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
