"""Living-room couch: sage grey-green fabric, square track arms with rounded tops, two
seat cushions, two sloped back cushions on a low back frame, short dark block feet.

Source of truth: scripted. Sizes from the living-room survey (registered splat + LiDAR in
layout inches, sliced through the couch) and colour from two photo crops.

Local frame: front faces -Y, length along X, origin on the floor at the footprint
centre. With plan rotation 90 (front faces east) local +X points north.
Measured footprint in plan: x 3..42 (wall side to front), y 25.5..112.5, so the origin
sits at plan (22.5, 69.0). The survey box (100 long, centred y 74.5) includes the
blanket heap and the portable AC that stands off the north arm.
"""

import math

from mathutils import Matrix, Vector

import atlas_layout
import common

IN = 0.0254


def m(v):
    return v * IN


L = 87.0            # SCAN outer arm to outer arm (plan y 25.5..112.5)
D = 39.0            # SCAN back frame to seat front (plan x 3..42); survey box said 38
ARM_W = 9.5         # SCAN south arm 26..35, north arm ~102..112 (under blankets)
ARM_H = 24.0        # SCAN arm top 23-25
SEAT_H = 17.5       # SCAN seat top 17-18 (blanket on it)
DECK_H = 10.5       # EST seat cushion ~7 thick
BACK_FRAME = (13.0, 30.0)   # EST frame from local y 13 to the back, top 30 (SCAN 28-31 at arms)
BACK_H = 33.0       # SCAN back cushion top 32-33
CUSH_T = 7.0        # EST back cushion thickness
BACK_FOOT_Y = 2.5   # SCAN back cushion meets the seat 20 in from the wall (plan x 20)
LEG_H = 1.5         # EST (feet barely visible in the photos)
LEG = 2.0           # EST square feet

NAME = "couch"
ATLAS = {
    "name": "couch",
    "size": 1024,
    "regions": {
        "fabric": (0, 0, 1024, 832),
        "fabric_shade": (0, 832, 512, 192),
        "leg": (512, 832, 128, 192),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"couch": {"atlas": "couch", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("from_north", 90, 18, 1.0), ("plan_top", 0, 89.9, 1.0)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -L / 2, L / 2
    y0, y1 = -D / 2, D / 2
    ix0, ix1 = x0 + ARM_W, x1 - ARM_W

    def bx(r, lo, hi, bev=0.0, seg=2, mat=None):
        b.box(r, tuple(map(m, lo)), tuple(map(m, hi)), bevel=m(bev), segments=seg, matrix=mat)

    # base / deck between the arms, and the back frame
    bx("fabric_shade", (ix0 - 0.5, y0 + 0.5, LEG_H), (ix1 + 0.5, BACK_FRAME[0] + 1, DECK_H), 1.0)
    bx("fabric", (x0 + 0.5, BACK_FRAME[0], LEG_H), (x1 - 0.5, y1, BACK_FRAME[1]), 1.5, 3)
    # track arms, rounded along the top
    for ax0, ax1 in ((x0, ix0), (ix1, x1)):
        bx("fabric", (ax0, y0, LEG_H), (ax1, y1, ARM_H), 2.5, 3)
    # seat cushions
    cw = (ix1 - ix0) / 2
    for i in range(2):
        cx0 = ix0 + i * cw
        bx("fabric", (cx0 + 0.15, y0, DECK_H), (cx0 + cw - 0.15, BACK_FOOT_Y + 3.0, SEAT_H),
           2.2, 3)
    # back cushions: slabs leaning back from the seat to the frame top
    rise = BACK_H - SEAT_H
    theta = math.atan2(8.5, rise)                  # SCAN top 8.5 in behind the foot
    hgt = rise / math.cos(theta) + 0.3
    s, c = math.sin(theta), math.cos(theta)
    for i in range(2):
        cx0 = ix0 + i * cw
        mat = (Matrix.Translation(Vector((0, m(BACK_FOOT_Y + CUSH_T / 2 * c),
                                          m(SEAT_H - CUSH_T / 2 * s))))
               @ Matrix.Rotation(-theta, 4, "X"))
        b.box("fabric", (m(cx0 + 0.2), m(-CUSH_T / 2), 0.0),
              (m(cx0 + cw - 0.2), m(CUSH_T / 2), m(hgt)), bevel=m(2.2), segments=3, matrix=mat)
    # feet
    for fx in (x0 + 1.5, x1 - 1.5 - LEG):
        for fy in (y0 + 1.5, y1 - 1.5 - LEG):
            bx("leg", (fx, fy, 0.0), (fx + LEG, fy + LEG, LEG_H + 0.3))
    return [b.to_object(NAME, coll)]


def uniform_uvs(ob, atlas):
    """Per-face box projection at one uniform scale (fabric weave stays square): the
    largest object extent spans the region's width."""
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    me.uv_layers.active = uvl
    lo = Vector([min(v.co[i] for v in me.vertices) for i in range(3)])
    hi = Vector([max(v.co[i] for v in me.vertices) for i in range(3)])
    span = max(hi - lo)
    regions = [s.name.split(".")[0] for s in me.materials]
    for p in me.polygons:
        region = regions[p.material_index]
        u0, v0, u1, v1 = atlas_layout.uv_rect(atlas, region)
        _, _, rw, rh = atlas["regions"][region]
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        ua, va = [(1, 2), (0, 2), (0, 1)][ax]
        su = span
        sv = span * rh / rw
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            fu = min((co[ua] - lo[ua]) / su, 1.0)
            fv = min((co[va] - lo[va]) / sv, 1.0)
            uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    uniform_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
