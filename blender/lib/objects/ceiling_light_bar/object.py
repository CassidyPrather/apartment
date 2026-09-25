"""Kitchen ceiling light bar: a gently S-curved brushed-metal bar under a round canopy,
with six swivel spot heads, each a short stem and socket cup holding a frosted white
tulip glass shade.

Source of truth: scripted. Frame: origin at the ceiling mount centre (top of the canopy,
flush with the ceiling), bar along X (east-west), everything hangs to -Z. Placement: plan
(68, 235) at Z = 108 in (the ceiling), rotation 0.

Dimensions (inches):
  bar length 48, heads spread over ~52   SCAN (LiDAR x 41.5..94.4) / inventory
  lowest point ~Z 98 (drop ~10)          SCAN (lowest LiDAR returns at Z 98-100)
  six heads                              photos (ceiling_light_bar_1/_2 both show six)
  canopy 5 dia x 1.1                     EST from photos
  bar 0.55 wide x 0.3, 2.4 below ceiling EST
  plan wave amplitude 1.5                EST (the bar is an S curve seen from below)
  head stem 0.3 dia x 2.0, socket 1.3 dia x 1.0, shade 1.6 -> 2.9 dia x 3.6
                                         EST from photos
  head tilt alternating 15 deg           EST (photos show heads aimed various ways)
"""

import math

import bmesh
from mathutils import Matrix, Vector

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "ceiling_light_bar"

BAR_L, BAR_W, BAR_T, BAR_Z = 48.0, 0.55, 0.3, -2.4
WAVE = 1.5
CANOPY_R, CANOPY_T = 2.5, 1.1
N_HEADS = 6
HEAD_SPAN = 42.0
STEM_R, STEM_L = 0.15, 2.0
SOCKET_R, SOCKET_L = 0.65, 1.0
SHADE_R0, SHADE_R1, SHADE_L = 0.8, 1.45, 3.6
TILT = 15.0

REGIONS = ["metal", "lens"]
ATLAS = {
    "name": "ceiling_light_bar",
    "size": 512,
    "regions": {
        "metal": (0, 0, 256, 256),
        "lens": (256, 0, 256, 256),
    },
}
MATERIALS = {
    "ceiling_light_bar": {"atlas": "ceiling_light_bar", "mode": "opaque"},
    "ceiling_light_bar_lens": {"atlas": "ceiling_light_bar", "mode": "opaque"},
}
COLLIDER = "none"
STATIC = True
VIEWS = [("below", 20, -35, 0.8), ("photo_side", 10, -12, 0.8)]


def wave_y(x):
    return WAVE * math.sin(2 * math.pi * x / BAR_L)


def cone(b, region, mat, r_top, r_bot, length, segs=12):
    """Truncated cone from z=0 (radius r_top) down to z=-length (r_bot), inches, placed by mat."""
    r = bmesh.ops.create_cone(b.bm, cap_ends=True, cap_tris=False, segments=segs,
                              radius1=m(r_bot), radius2=m(r_top), depth=m(length))
    verts = r["verts"]
    bmesh.ops.translate(b.bm, vec=(0, 0, -m(length) / 2), verts=verts)
    bmesh.ops.transform(b.bm, matrix=mat, verts=verts)
    b._tag(list({f for v in verts for f in v.link_faces}), region)


def build(coll):
    b = common.Builder(REGIONS)
    # canopy: slightly tapered disc, and a short post down to the bar
    cone(b, "metal", Matrix.Identity(4), CANOPY_R, CANOPY_R - 0.35, CANOPY_T, segs=20)
    cone(b, "metal", Matrix.Translation((0, 0, -m(CANOPY_T))), 0.3, 0.3, abs(BAR_Z) - CANOPY_T, segs=8)
    # bar: flat strip swept along an S curve
    pts = [Vector((m(x), m(wave_y(x)), m(BAR_Z)))
           for x in [-BAR_L / 2 + BAR_L * i / 24 for i in range(25)]]
    b.sweep("metal", pts, common.rect_profile(m(BAR_W), m(BAR_T)), up=(0, 0, 1))
    for i in range(N_HEADS):
        x = -HEAD_SPAN / 2 + HEAD_SPAN * i / (N_HEADS - 1)
        y = wave_y(x)
        tilt = TILT if i % 2 else -TILT
        base = Matrix.Translation((m(x), m(y), m(BAR_Z - BAR_T / 2)))
        cone(b, "metal", base, STEM_R, STEM_R, STEM_L * 0.4, segs=6)
        # swivel: the rest of the head leans toward +/-Y
        piv = (base @ Matrix.Translation((0, 0, -m(STEM_L * 0.4)))
               @ Matrix.Rotation(math.radians(tilt), 4, "X"))
        cone(b, "metal", piv, STEM_R, STEM_R, STEM_L * 0.6, segs=6)
        sock = piv @ Matrix.Translation((0, 0, -m(STEM_L * 0.6)))
        cone(b, "metal", sock, 0.35, SOCKET_R, SOCKET_L, segs=12)
        shade = sock @ Matrix.Translation((0, 0, -m(SOCKET_L)))
        cone(b, "lens", shade, SHADE_R0, SHADE_R1, SHADE_L, segs=14)
    return [b.to_object(NAME, coll)]


def texture(objs):
    metal = common.atlas_material("ceiling_light_bar", ATLAS)
    lens = common.atlas_material("ceiling_light_bar_lens", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        common.collapse_materials(ob, {"metal": metal, "lens": lens})
