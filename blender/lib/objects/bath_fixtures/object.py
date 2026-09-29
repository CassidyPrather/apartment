"""Bathroom wall and ceiling fixtures, built in PLAN COORDINATES: object X = plan x,
object Y = plan y (model coordinates, north wall at y 286.0), Z = height above the floor,
all converted from inches to metres. Place at (0, 0, 0) with no rotation.

Contents:
  linen niche     4 white shelves on cleats between the south wall and the tub stub wall
  towel bar       north wall, west of the tub
  grab bar        vertical, north wall at the tub entry (bent returns, satin nickel)
  towel ring      south wall, over the vanity end
  round mirror    small decor mirror on the south wall, hung on a chain
  light bar       4 up-facing opal cylinder shades on a nickel bar over the vanity mirror
  ceiling light   fan/light plate with two round lamps

Source of truth: scripted, from the bathroom LiDAR survey (Reference/bathroom_survey/,
fixtures.py boxes; survey y values are 3.9 in north of the model, see SY()). SCAN =
measured from the registered capture (about +-1 in); EST = from the photos.

Materials: bath_fixtures (opaque atlas) and bath_fixtures_glow (the shades and lamps;
the same atlas, whose emission map is lit only in the glow region).
"""

import math
import os
import sys

import bmesh
from mathutils import Matrix

import common

IN = 0.0254


def m(v):
    return v * IN


def SY(v):
    """Survey plan y -> model plan y (the survey put the north wall at 289.9, not 286)."""
    return v - 3.9


NAME = "bath_fixtures"
ATLAS = {
    "name": "bath_fixtures",
    "size": 512,
    "regions": {
        "trim": (0, 0, 128, 128),       # white shelf paint
        "plate": (128, 0, 128, 128),    # white plastic (ceiling plate)
        "nickel": (256, 0, 128, 128),   # brushed nickel
        "chrome": (384, 0, 128, 128),   # polished (grab bar)
        "mirror": (0, 128, 128, 128),
        "dark": (128, 128, 128, 128),   # black mirror frame / hook
        "glow": (256, 128, 128, 128),   # opal glass, emissive
    },
}
MATERIALS = {
    "bath_fixtures": {"atlas": "bath_fixtures", "mode": "opaque", "tiled": False},
    "bath_fixtures_glow": {"atlas": "bath_fixtures", "mode": "opaque", "tiled": False},
}
COLLIDER = "none"
STATIC = True
VIEWS = [("vanity_wall", 270, 10, 0.45), ("niche", 90, 15, 0.5), ("ceiling_up", 0, -60, 0.6)]

# --- dimensions (inches, model plan coordinates) --------------------------------------
WALL_W = 177.75                         # SCAN bath west wall face (placed 6.45 west, onto the shell's 171.3)
WALL_E = WALL_W + 103.3                 # the shell's bath width (east wall moved in to 274.6)
WALL_S, WALL_N = 202.5, 286.0          # model south / north wall faces
CEILING = 108.0
NICHE_X = (WALL_E - 13.65, WALL_E)     # SCAN shelves 13.65 deep off the east wall
NICHE_Y = (SY(206.4), SY(226.45))      # SCAN 20.05 between the south wall and the stub
SHELF_TOPS = (22.5, 40.1, 58.0, 75.9)  # SCAN
SHELF_T, CLEAT_T, CLEAT_H = 0.75, 0.75, 1.5   # EST
TOWEL_BAR = (217.0, 242.0, 60.75)      # SCAN x0, x1, z
GRAB_BAR = (251.5, 31.4, 51.8)         # SCAN x, z0, z1
TOWEL_RING = (197.1, 58.0)             # SCAN x, top z
ROUND_MIRROR = (210.4, 63.5, 12.0)     # SCAN x, centre z, diameter
LIGHT_BAR_Y = SY(231.0)                # SCAN centre
SHADE_X = 181.3                        # SCAN shade centre off the west wall
SHADE_Z = (79.0, 85.0)                 # SCAN top 85 / EST
SHADE_D = 5.0                          # EST (4 shades in ~30 in)
SHADE_PITCH = 7.5                      # EST
FAN = (230.2, SY(253.1), 15.6, 11.2)   # SCAN centre x, y, size along x, along y
LAMP_R, LAMP_DX = 2.5, 3.7             # EST

REGIONS = ["trim", "plate", "nickel", "chrome", "mirror", "dark", "glow"]


def P(x, y, z):
    return (m(x), m(y), m(z))


def box(b, region, lo, hi, bevel=0.0):
    b.box(region, P(*lo), P(*hi), bevel=m(bevel) if bevel else 0.0)


def cyl(b, region, c, r, d, axis="Z", seg=16, cap=None):
    b.cylinder(region, P(*c), m(r), m(d), axis=axis, segments=seg, cap_region=cap)


def niche(b):
    x0, x1 = NICHE_X
    y0, y1 = NICHE_Y
    for top in SHELF_TOPS:
        box(b, "trim", (x0, y0, top - SHELF_T), (x1, y1, top), bevel=0.08)
        cz0, cz1 = top - SHELF_T - CLEAT_H, top - SHELF_T
        box(b, "trim", (x1 - CLEAT_T, y0 + CLEAT_T, cz0), (x1, y1 - CLEAT_T, cz1))
        for ya, yb in ((y0, y0 + CLEAT_T), (y1 - CLEAT_T, y1)):
            box(b, "trim", (x0 + 1.0, ya, cz0), (x1, yb, cz1))


def frustum(b, region, c, r_base, r_tip, d, axis="Y", seg=16, sign=1):
    """Cone frustum (inches, plan coords): r_base toward -axis*sign, r_tip the other end."""
    r1, r2 = (r_base, r_tip) if sign > 0 else (r_tip, r_base)
    r = bmesh.ops.create_cone(b.bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=m(r1), radius2=m(r2), depth=m(d))
    rot = {"X": Matrix.Rotation(math.pi / 2, 4, "Y"), "Y": Matrix.Rotation(-math.pi / 2, 4, "X"),
           "Z": Matrix.Identity(4)}[axis]
    bmesh.ops.transform(b.bm, matrix=Matrix.Translation(P(*c)) @ rot, verts=r["verts"])
    b._tag(list({f for v in r["verts"] for f in v.link_faces}), region)


def towel_bar(b):
    x0, x1, z = TOWEL_BAR
    y = WALL_N - 2.4
    cyl(b, "nickel", ((x0 + x1) / 2, y, z), 0.375, x1 - x0 - 1.0, axis="X", seg=12)
    for x in (x0 + 0.6, x1 - 0.6):
        # bell post tapering from its wall flange out to the bar
        frustum(b, "nickel", (x, WALL_N - 1.5, z), 1.0, 0.55, 2.2, sign=-1)
        cyl(b, "nickel", (x, WALL_N - 0.2, z), 1.2, 0.4, axis="Y", seg=16)


def grab_bar(b):
    """Satin-nickel grab bar (photos 010106, 010111): one tube that bends back to the wall
    at both ends on round flanges."""
    x, z0, z1 = GRAB_BAR
    y = WALL_N - 2.1                     # bar centreline off the wall
    rb = 1.1                             # bend radius
    za, zb = z0 + 1.5, z1 - 1.5          # return centrelines
    pts = [(WALL_N - 0.3, za)]
    for i in range(5):                   # bottom bend: from horizontal (toward -y) to up
        a = math.radians(90 * i / 4)
        pts.append((y + rb - rb * math.sin(a), za + rb - rb * math.cos(a)))
    for i in range(5):                   # top bend: from up back to the wall
        a = math.radians(90 * i / 4)
        pts.append((y + rb - rb * math.cos(a), zb - rb + rb * math.sin(a)))
    pts.append((WALL_N - 0.3, zb))
    b.sweep("nickel", [P(x, py, pz) for py, pz in pts], common.circle_profile(m(0.625), 12),
            up=(1, 0, 0))
    for zc in (za, zb):
        frustum(b, "nickel", (x, WALL_N - 0.25, zc), 1.5, 1.3, 0.5, sign=-1)


def towel_ring(b):
    x, ztop = TOWEL_RING
    cyl(b, "nickel", (x, WALL_S + 0.2, ztop), 1.1, 0.4, axis="Y", seg=16)
    cyl(b, "nickel", (x, WALL_S + 0.9, ztop - 0.3), 0.35, 1.2, axis="Y", seg=10)
    r, cz = 2.6, ztop - 0.6 - 2.6
    pts = [P(x + r * math.sin(2 * math.pi * i / 20), WALL_S + 1.4,
             cz + r * math.cos(2 * math.pi * i / 20)) for i in range(20)]
    b.sweep("nickel", pts, common.circle_profile(m(0.22), 8), up=(0, 1, 0), closed=True)


def round_mirror(b):
    x, z, d = ROUND_MIRROR
    cyl(b, "dark", (x, WALL_S + 0.3, z), d / 2, 0.6, axis="Y", seg=32)
    cyl(b, "mirror", (x, WALL_S + 0.62, z), d / 2 - 0.4, 0.06, axis="Y", seg=32)
    hz = z + d / 2 + 3.0
    cyl(b, "dark", (x, WALL_S + 0.5, hz), 0.35, 1.0, axis="Y", seg=10)   # hook
    # The hanging chain: two runs from the hook down to the frame (photo 005827).
    for sx in (-1, 1):
        a = math.radians(50)
        end = P(x + sx * (d / 2) * math.sin(a), WALL_S + 0.35, z + (d / 2) * math.cos(a))
        b.sweep("dark", [P(x, WALL_S + 0.5, hz - 0.2), end], common.circle_profile(m(0.09), 4),
                up=(0, 1, 0))


def light_bar(b):
    y = LIGHT_BAR_Y
    zb = 77.3
    box(b, "nickel", (WALL_W, y - 13.5, zb - 0.9), (WALL_W + 0.9, y + 13.5, zb + 0.9), bevel=0.2)
    z0, z1 = SHADE_Z
    for i in range(4):
        yi = y + (i - 1.5) * SHADE_PITCH
        arm = [P(WALL_W + 0.8, yi, zb), P(SHADE_X - 1.2, yi, zb), P(SHADE_X - 0.2, yi, zb + 0.6),
               P(SHADE_X, yi, z0 - 1.0)]
        b.sweep("nickel", arm, common.circle_profile(m(0.28), 8), up=(0, 1, 0))
        cyl(b, "nickel", (SHADE_X, yi, z0 - 0.5), 1.4, 1.0, seg=16)
        cyl(b, "glow", (SHADE_X, yi, (z0 + z1) / 2), SHADE_D / 2, z1 - z0, seg=20)


def ceiling_light(b):
    cx, cy, w, d = FAN
    box(b, "plate", (cx - w / 2, cy - d / 2, CEILING - 0.6), (cx + w / 2, cy + d / 2, CEILING),
        bevel=0.15)
    for sx in (-1, 1):
        lx = cx + sx * LAMP_DX
        cyl(b, "nickel", (lx, cy, CEILING - 0.75), LAMP_R + 0.45, 0.3, seg=24)
        cyl(b, "glow", (lx, cy, CEILING - 1.0), LAMP_R, 0.5, seg=24)


def build(coll):
    b = common.Builder(REGIONS)
    niche(b)
    towel_bar(b)
    grab_bar(b)
    towel_ring(b)
    round_mirror(b)
    light_bar(b)
    ceiling_light(b)
    return [b.to_object("bath_fixtures", coll)]


def texture(objs):
    mat = common.atlas_material("bath_fixtures", ATLAS)
    glow = common.atlas_material("bath_fixtures_glow", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: (glow if r == "glow" else mat) for r in regions})
