"""Living-room floor details by the portable AC: the white plastic tub that catches the
AC's condensate, with the thin drain tube running into it, and the pair of white-and-navy
running shoes left in front of the couch's north arm.

Source of truth: scripted. Positions and sizes from the living-room splat
(Reference/lidarseries-splat, registered with Reference/living_survey/transform.json):
bright near-white clusters on the floor; looks from the photo in
Reference/couch_work/side_by_side.jpg (left). The AC itself moved 6 in north of its
surveyed spot in the layout (to clear the couch arm), so the tub, which sits at its side,
moves with it; the shoes stay where the survey has them.
Frame: PLAN coordinates (X east, Y north, Z up, inches via m()); the package sits on a
marker at the plan origin with no rotation.

Dimensions (inches, plan):
  tub       x 1.6..11.7, y 118.8..130.5 surveyed -> +6 in y with the AC; 6.7 tall   SCAN
            walls 0.12, rounded corners 1.2, slight taper, rolled rim                  EST
  drain tube 0.45 dia, from low on the AC's north end (x 25, y 134) into the tub      EST (photo)
  shoes     heels/toes from the splat cluster x 37.5..45.8, y 114.8..131.3 (toes north,
            the east shoe a little ahead); 4.0 wide, 11 long, collar 3.8 high         SCAN / EST
No brands: the shoes' side logo is left off.
"""

import importlib.util
import math
import os

from mathutils import Vector

import common

HERE = os.path.dirname(os.path.abspath(__file__))
# the shoes package's shoe() builder, loaded under its own name (every package's module is
# called object.py)
_spec = importlib.util.spec_from_file_location("shoes_kit", os.path.join(HERE, "..", "shoes", "object.py"))
shoes_kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shoes_kit)

NAME = "living_floor"
IN = 0.0254


def m(v):
    return v * IN


ATLAS = {
    "name": NAME,
    "size": 256,
    "regions": {
        "tub_white": (0, 0, 64, 64),
        "tube_clear": (64, 0, 64, 64),
        "mesh_white": (128, 0, 64, 64),
        "navy": (192, 0, 64, 64),
        "sole_white": (0, 64, 64, 64),
        "laces_white": (64, 64, 64, 64),
        "insole_grey": (128, 64, 64, 64),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("from_ne", 225, 35, 0.9), ("top", 0, 89.9, 1.0)]

TUB = (1.6, 11.7, 124.8, 136.5, 6.7)      # x0, x1, y0, y1, height (plan inches)
TUB_WALL, TUB_R = 0.12, 1.2
TUBE_R = 0.225
TUBE = [(25.0, 134.3, 1.6), (22.0, 136.5, 1.2), (17.0, 137.5, 0.9), (12.5, 135.5, 5.2),
        (10.0, 132.5, 6.9), (8.0, 131.5, 4.0), (7.0, 131.0, 1.0)]   # AC -> over the rim -> in the tub

# the runners, in the shoes package's style table (region names from this atlas)
shoes_kit.STYLES["runner"] = dict(W=4.0, H=3.8, Ts=1.1, upper="mesh_white", side="navy", sole="sole_white",
                                  laces="laces_white", insole="insole_grey", tab="navy", toe="mesh_white")
SHOES = [
    ("runner", (39.6, 116.2), (39.4, 127.2), None, -1),
    ("runner", (43.9, 120.0), (43.6, 131.0), None, 1),
]


def tub(b):
    x0, x1, y0, y1, h = TUB
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, d = (x1 - x0), (y1 - y0)
    taper = 0.9                                   # the bottom is a little smaller than the rim
    rings = []
    for k, (z, s, inset) in enumerate([(0.0, taper, 0.0), (h - 0.5, 1.0, 0.0), (h, 1.02, 0.0),
                                       (h, 1.0, TUB_WALL * 2), (0.35, taper, TUB_WALL * 2)]):
        ring = []
        for a in range(0, 360, 15):
            r = math.radians(a)
            # rounded rectangle by superellipse
            ex, ey = (w / 2 * s - inset), (d / 2 * s - inset)
            px = math.copysign(abs(math.cos(r)) ** 0.35, math.cos(r)) * ex
            py = math.copysign(abs(math.sin(r)) ** 0.35, math.sin(r)) * ey
            ring.append(b.bm.verts.new((m(cx + px), m(cy + py), m(z))))
        rings.append(ring)
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for j in range(n):
            f = b.bm.faces.new((rings[i][j], rings[i][(j + 1) % n], rings[i + 1][(j + 1) % n], rings[i + 1][j]))
            f.material_index = b.idx("tub_white")
    for ring, flip in ((rings[0], True), (rings[-1], False)):
        f = b.bm.faces.new(list(reversed(ring)) if flip else ring)
        f.material_index = b.idx("tub_white")


def build(coll):
    b = common.Builder(REGIONS)
    tub(b)
    path = common.smooth_path([Vector(p) * IN for p in TUBE], 8)
    b.sweep("tube_clear", path, common.circle_profile(m(TUBE_R), 6), up=(0, 0, 1))
    for style, heel, toe, length, mirror in SHOES:
        shoes_kit.shoe(b, style, heel, toe, length, mirror)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
