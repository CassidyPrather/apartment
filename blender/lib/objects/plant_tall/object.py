"""Tall artificial ficus in a small terracotta pot, standing in the living room's
south-west corner.

Source of truth: scripted, from the living-room survey (LiDAR + splat registered to the
layout, and three photo crops of the corner). Coarse block-in: overall size from the
scan, crown shape and pot from the photos.

Local frame: front faces -Y, Z up, origin on the floor at the pot centre. Placed at
(16.5, 16.5, 0), rotation 0, so the two corner walls sit at x = -16.5 and y = -16.5.

Two meshes:
  plant_tall         pot, soil and the braided trunks (opaque)
  plant_tall_leaves  leaf-sprig cards, two back-to-back quads each, alpha-cutout
"""

import importlib
import math
import os
import random
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import plantkit as K  # noqa: E402

importlib.reload(K)


def m(inches):
    return inches * 0.0254


NAME = "plant_tall"

# --- dimensions (inches) ---------------------------------------------------------------
HEIGHT = 84.0            # SCAN top of the crown (survey box 30 x 30 x 84)
SPREAD = 30.0            # SCAN crown footprint (corner-limited)
POT_TOP_D = 11.5         # EST from photos (pot ~ 1/7 of the plant's visible height)
POT_BOT_D = 8.5          # EST
POT_H = 9.0              # EST
RIM_H = 1.6              # EST rolled rim band
SOIL_Z = 8.0             # EST
TRUNK_TOP = 66.0         # EST where the braided stems disappear into the crown
TRUNK_D = 0.8            # EST each of three stems
LOWER_TIER = (20.0, 42.0)  # EST sparse lower leaf tier (photos)
UPPER_TIER = (40.0, HEIGHT)  # EST main crown

ATLAS = {
    "name": "plant_tall",
    "size": 1024,
    "regions": {
        "sprig_a": (0, 0, 512, 512),
        "sprig_b": (512, 0, 512, 512),
        "sprig_c": (0, 512, 512, 512),
        "pot": (512, 512, 256, 256),
        "bark": (768, 512, 256, 256),
        "soil": (512, 768, 256, 256),
    },
}
SPRIGS = ["sprig_a", "sprig_b", "sprig_c"]
SOLID = ["pot", "bark", "soil"]

MATERIALS = {
    "plant_tall": {"atlas": "plant_tall", "mode": "opaque"},
    "plant_tall_leaves": {"atlas": "plant_tall", "mode": "cutout", "alpha": 0.5},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_ne", 135, 8, 1.0)]   # from the room (north-east), like the crops


def crown_radius(z):
    """Crown half-width (inches) at height z: lower tier, a waist, then the main crown."""
    if z < LOWER_TIER[0]:
        return 0.0
    if z < LOWER_TIER[1]:
        t = (z - LOWER_TIER[0]) / (LOWER_TIER[1] - LOWER_TIER[0])
        return 5 + 9 * math.sin(math.pi * min(1.0, t * 1.2))
    t = (z - UPPER_TIER[0]) / (UPPER_TIER[1] - UPPER_TIER[0])
    return 6 + 9.5 * math.sin(math.pi * (0.15 + 0.8 * t))


def trunk_path(k):
    """Three stems braided loosely around the centre, rising from the soil."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        z = SOIL_Z - 1 + (TRUNK_TOP - SOIL_Z + 1) * t
        a = 2 * math.pi * (k / 3 + 1.1 * t)
        r = 0.55 + 1.2 * t
        lean = Vector((1.2, 0.9, 0)) * t      # a slight lean out of the corner
        pts.append(Vector((m(r * math.cos(a) + lean.x), m(r * math.sin(a) + lean.y), m(z))))
    return pts


def build(coll):
    rnd = random.Random(84)
    b = K.CardBuilder(SOLID)
    # Pot: tapered body + rolled rim + soil disc.
    n = 20
    import bmesh
    bm = b.bm
    ring = lambda r, z: [bm.verts.new((m(r) * math.cos(2 * math.pi * i / n), m(r) * math.sin(2 * math.pi * i / n), m(z))) for i in range(n)]  # noqa: E731
    rings = [ring(POT_BOT_D / 2, 0.0), ring(POT_TOP_D / 2 - 0.3, POT_H - RIM_H),
             ring(POT_TOP_D / 2 + 0.35, POT_H - RIM_H + 0.2), ring(POT_TOP_D / 2 + 0.35, POT_H),
             ring(POT_TOP_D / 2 - 0.4, POT_H), ring(POT_TOP_D / 2 - 0.6, SOIL_Z)]
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    b._tag(faces, "pot")
    soil = bm.faces.new(rings[-1])
    b._tag([soil], "soil")
    # Braided trunks.
    prof = common.circle_profile(m(TRUNK_D / 2), 5)
    tips = []
    for k in range(3):
        path = trunk_path(k)
        b.sweep_uv("bark", path, prof, v_per_seg=0.25)
        tips.append(path[-1])
    # A few thin side branches into the crown tiers.
    branch_prof = common.circle_profile(m(0.28), 4)
    anchors = []
    for i in range(9):
        z = rnd.uniform(24, 62)
        a = rnd.uniform(0, 2 * math.pi)
        base = Vector((m(0.8 * math.cos(a)), m(0.8 * math.sin(a)), m(z)))
        L = rnd.uniform(6, 10)
        mid = base + Vector((m(L * 0.5 * math.cos(a)), m(L * 0.5 * math.sin(a)), m(L * 0.45)))
        end = base + Vector((m(L * math.cos(a)), m(L * math.sin(a)), m(L * 0.7)))
        b.sweep_uv("bark", [base, mid, end], branch_prof, v_per_seg=0.25)
        anchors.append((end, a))
    solid = b.to_object("plant_tall", coll)

    # Leaf cards.
    f = K.CardBuilder(SPRIGS, recalc=False)
    cards = 0
    # Upper crown: rings of cards leaning outward, denser in the middle.
    for z in range(int(UPPER_TIER[0]), int(HEIGHT) - 8, 3):
        R = crown_radius(z + 6)
        count = max(3, round(R * 0.62))
        for i in range(count):
            a = 2 * math.pi * (i + rnd.random() * 0.8) / count
            r = rnd.uniform(0.35, 0.8) * R
            h = rnd.uniform(12, 16)
            w = h * rnd.uniform(0.85, 1.0)
            tilt = rnd.uniform(25, 55)
            reach = r + math.sin(math.radians(tilt)) * h
            if reach > R + 2:
                r = max(0.5, R + 2 - math.sin(math.radians(tilt)) * h)
            org = Vector((m(r * math.cos(a) + 1.2 * (z - SOIL_Z) / (TRUNK_TOP - SOIL_Z)),
                          m(r * math.sin(a) + 0.9 * (z - SOIL_Z) / (TRUNK_TOP - SOIL_Z)), m(z)))
            f.card(rnd.choice(SPRIGS), org, m(w), m(h), math.degrees(a) - 90 + rnd.uniform(-25, 25),
                   tilt, roll=rnd.uniform(-20, 20), bend=rnd.uniform(0, 25), segs=1,
                   flip_u=rnd.random() < 0.5)
            cards += 1
    # Crown top: a few near-upright sprigs.
    for i in range(6):
        a = 2 * math.pi * i / 6 + rnd.uniform(-0.3, 0.3)
        org = Vector((m(1.2 + 2.5 * math.cos(a)), m(0.9 + 2.5 * math.sin(a)), m(HEIGHT - 16)))
        f.card(rnd.choice(SPRIGS), org, m(12), m(15.5), math.degrees(a) - 90, rnd.uniform(5, 22),
               roll=rnd.uniform(-30, 30), flip_u=rnd.random() < 0.5)
    # Lower tier: a wide, sparse skirt of sprigs (the photos show it wider than the waist).
    for z in range(22, 46, 4):
        for i in range(6):
            a = 2 * math.pi * (i + rnd.random() * 0.7) / 6
            org = Vector((m(4 * math.cos(a) + 0.5), m(4 * math.sin(a) + 0.4), m(z)))
            f.card(rnd.choice(SPRIGS), org, m(rnd.uniform(12, 15)), m(rnd.uniform(12, 15)),
                   math.degrees(a) - 90, rnd.uniform(50, 72), roll=rnd.uniform(-25, 25),
                   bend=rnd.uniform(5, 25), flip_u=rnd.random() < 0.5)
    # Lower tier: sprigs off the side branches, drooping.
    for end, a in anchors:
        zin = end.z / 0.0254
        for s in range(3 if zin < LOWER_TIER[1] + 4 else 2):
            aa = a + rnd.uniform(-0.6, 0.6)
            f.card(rnd.choice(SPRIGS), end, m(rnd.uniform(11, 14)), m(rnd.uniform(11, 14)),
                   math.degrees(aa) - 90, rnd.uniform(35, 65), roll=rnd.uniform(-25, 25),
                   bend=rnd.uniform(10, 30), flip_u=rnd.random() < 0.5)
    leaves = f.to_object("plant_tall_leaves", coll)
    clamp_to_footprint(leaves)
    return [solid, leaves]


def clamp_to_footprint(ob):
    """Keep every leaf vertex inside the 30 x 30 corner footprint and under HEIGHT."""
    half = m(SPREAD / 2 - 0.3)
    for v in ob.data.vertices:
        v.co.x = max(-half, min(half, v.co.x))
        v.co.y = max(-half, min(half, v.co.y))
        v.co.z = max(m(4), min(m(HEIGHT), v.co.z))


def texture(objs):
    solid, leaves = objs
    opaque = common.atlas_material("plant_tall", ATLAS)
    cut = K.cutout_material("plant_tall_leaves", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        K.apply_card_uvs(ob, ATLAS)
    common.collapse_materials(solid, {r: opaque for r in SOLID})
    common.collapse_materials(leaves, {r: cut for r in SPRIGS})
