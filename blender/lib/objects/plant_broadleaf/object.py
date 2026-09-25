"""Broadleaf artificial plant (dieffenbachia-like: long pointed leaves, cream variegation
along the midrib) in a dark wicker basket pot, under the living room's south window.

Source of truth: scripted, from the living-room survey (LiDAR + splat in layout inches)
and one photo crop. Coarse block-in.

Local frame: front faces -Y, Z up, origin on the floor at the basket centre. Placed at
(68, 15, 0), rotation 0, so the south wall is at y = -15 (the plant is round; its
"front" means nothing).

Two meshes:
  plant_broadleaf         basket, soil and the green canes (opaque)
  plant_broadleaf_leaves  leaf cards (two back-to-back quad strips each), alpha-cutout
"""

import importlib
import math
import os
import random
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plant_tall"))
import common  # noqa: E402
import plantkit as K  # noqa: E402

importlib.reload(K)


def m(inches):
    return inches * 0.0254


NAME = "plant_broadleaf"

# --- dimensions (inches) ---------------------------------------------------------------
HEIGHT = 31.0            # SCAN survey box 24 x 25 x 31
SPREAD = (24.0, 25.0)    # SCAN footprint
POT_TOP_D = 10.5         # EST from the photo (basket ~ 1/3 of the plant's width)
POT_BOT_D = 8.0          # EST
POT_H = 7.5              # EST
SOIL_Z = 6.5             # EST
CANES = [(-1.0, 0.5, 19.0), (1.2, -0.4, 16.0), (0.2, 1.3, 13.0)]   # EST (x, y, top z)

ATLAS = {
    "name": "plant_broadleaf",
    "size": 1024,
    "regions": {
        "leaf_a": (0, 0, 256, 512),
        "leaf_b": (256, 0, 256, 512),
        "leaf_c": (512, 0, 256, 512),
        "basket": (768, 0, 256, 256),
        "soil": (768, 256, 256, 128),
        "cane": (768, 384, 256, 128),
    },
}
LEAVES = ["leaf_a", "leaf_b", "leaf_c"]
SOLID = ["basket", "soil", "cane"]

MATERIALS = {
    "plant_broadleaf": {"atlas": "plant_broadleaf", "mode": "opaque"},
    "plant_broadleaf_leaves": {"atlas": "plant_broadleaf", "mode": "cutout", "alpha": 0.5},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_n", 180, 20, 1.0)]     # from the room (north), like the crop


def build(coll):
    rnd = random.Random(31)
    b = K.CardBuilder(SOLID)
    bm = b.bm
    n = 18

    def ring(r, z):
        return [bm.verts.new((m(r) * math.cos(2 * math.pi * i / n), m(r) * math.sin(2 * math.pi * i / n), m(z)))
                for i in range(n)]
    rings = [ring(POT_BOT_D / 2, 0.0), ring(POT_TOP_D / 2 - 0.3, POT_H * 0.55),
             ring(POT_TOP_D / 2, POT_H - 0.6), ring(POT_TOP_D / 2 + 0.3, POT_H),
             ring(POT_TOP_D / 2 - 0.5, POT_H), ring(POT_TOP_D / 2 - 0.7, SOIL_Z)]
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    b._tag(faces, "basket")
    b._tag([bm.faces.new(rings[-1])], "soil")
    prof = common.circle_profile(m(0.32), 5)
    cane_pts = []
    for cx, cy, top in CANES:
        path = [Vector((m(cx), m(cy), m(SOIL_Z - 0.5))), Vector((m(cx * 1.2), m(cy * 1.2), m((SOIL_Z + top) / 2))),
                Vector((m(cx * 1.5), m(cy * 1.5), m(top)))]
        b.sweep_uv("cane", path, prof, v_per_seg=0.5)
        cane_pts.append(path)
    solid = b.to_object("plant_broadleaf", coll)

    f = K.CardBuilder(LEAVES, recalc=False)
    # Leaves spring from each cane at a few heights; lower leaves arch out and droop,
    # upper leaves stand up. Card: petiole + blade, v=0 at the petiole.
    k = 0
    for ci, (cx, cy, top) in enumerate(CANES):
        levels = 4 if ci == 0 else 3
        for li in range(levels):
            t = li / max(1, levels - 1)
            z = SOIL_Z + 2 + (top - SOIL_Z - 2) * t
            for s in range(4 if li < levels - 1 else 5):
                heading = rnd.uniform(0, 360) if li < levels - 1 else rnd.uniform(0, 360)
                length = rnd.uniform(12, 15) - 2.5 * t
                width = rnd.uniform(6.8, 8.0)
                tilt = (82 - 30 * t) + rnd.uniform(-10, 10)
                bend = (45 - 25 * t) + rnd.uniform(-8, 12)
                org = Vector((m(cx * (1 + 0.5 * t)), m(cy * (1 + 0.5 * t)), m(z)))
                f.card(LEAVES[k % 3], org, m(width), m(length), heading - 90, tilt,
                       roll=rnd.uniform(-25, 25), bend=bend, segs=3, flip_u=rnd.random() < 0.5)
                k += 1
    leaves = f.to_object("plant_broadleaf_leaves", coll)
    fit(leaves)
    return [solid, leaves]


def fit(ob):
    """Scale the leaf spread about the centre into the scanned footprint and height."""
    vs = ob.data.vertices
    hx = max(abs(v.co.x) for v in vs)
    hy = max(abs(v.co.y) for v in vs)
    top = max(v.co.z for v in vs)
    sx = min(1.0, m(SPREAD[0] / 2) / hx)
    sy = min(1.0, m(SPREAD[1] / 2) / hy)
    sz = m(HEIGHT) / top
    for v in vs:
        v.co.x *= sx
        v.co.y *= sy
        v.co.z = max(m(2), m(SOIL_Z) + (v.co.z - m(SOIL_Z)) * sz) if v.co.z > m(SOIL_Z) else max(m(1), v.co.z)
    print("leaf fit scale", round(sx, 3), round(sy, 3), round(sz, 3))


def texture(objs):
    solid, leaves = objs
    opaque = common.atlas_material("plant_broadleaf", ATLAS)
    cut = K.cutout_material("plant_broadleaf_leaves", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        K.apply_card_uvs(ob, ATLAS)
    common.collapse_materials(solid, {r: opaque for r in SOLID})
    common.collapse_materials(leaves, {r: cut for r in LEAVES})
