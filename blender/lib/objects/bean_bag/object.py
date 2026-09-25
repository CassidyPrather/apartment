"""Small brown bean-bag pouf on the living-room floor under the south window.

Source of truth: scripted, from the living-room survey (LiDAR + splat box 25 x 26 x 24)
and the south-window photo crop: a slouched round bag of brown suede with a lighter,
patterned beige base band, the top dented in like a seat.

Local frame: front faces -Y (toward the south wall at y = -16.5 once placed), Z up,
origin on the floor at the footprint centre. Placed at (91, 16.5, 0), rotation 0.
"""

import math

import bmesh
import bpy

import common

NAME = "bean_bag"


def m(inches):
    return inches * 0.0254


# --- dimensions (inches) -------------------------------------------------------------
SIZE = (25.0, 26.0, 18.0)   # SCAN footprint x, y; height EST 18 from the photo's
#   proportions (~1.5:1 wide); the scan box's 24 likely catches the wall/sill behind it
BASE_BAND = 4.0             # EST beige base band (photo shows it mostly on the room side)

ATLAS = {
    "name": "bean_bag",
    "size": 512,
    "regions": {
        "suede": (0, 0, 512, 320),
        "panel": (0, 320, 512, 192),
    },
}
REGIONS = ["suede", "panel"]
MATERIALS = {"bean_bag": {"atlas": "bean_bag", "mode": "opaque"}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_n", 180, 22, 1.0)]


def build(coll):
    b = common.Builder(REGIONS)
    bm = b.bm
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        # slump: a soft mound, widest low down, flat base, domed shoulders, and a seat
        # hollow pushed into the top on the room side (+Y); the wall side rolls up higher
        z = max(z, -0.6)
        spread = 1.0 + 0.22 * max(0.0, -z) - 0.22 * max(0.0, z) ** 1.5
        x, y = x * spread, y * spread
        if z > 0:
            dent = 0.55 * math.exp(-((x / 0.6) ** 2 + ((y - 0.25) / 0.55) ** 2))
            z -= dent * z
            z += 0.18 * max(0.0, -y) * z + 0.06 * x * z
        v.co = (x, y, z)
    lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
    hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
    for v in bm.verts:
        v.co = tuple(m(SIZE[i]) * ((v.co[i] - lo[i]) / (hi[i] - lo[i]) - (0.5 if i < 2 else 0.0))
                     for i in range(3))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    for f in bm.faces:
        f.material_index = b.idx("panel" if f.calc_center_median().z < m(BASE_BAND) else "suede")
    return [b.to_object("bean_bag", coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material("bean_bag", ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
    for p in ob.data.polygons:
        p.use_smooth = True
