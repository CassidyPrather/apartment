"""Shoes on the bedroom floor: two pairs of sneakers side by side in the nook north of the
bed head, west of the closet front wall, toes toward the bed (south).
  black pair (west): black knit runners with orange-red flecks low on the sides, thick
    light grey foam soles, black laces
  beige pair (east): tan suede low-tops with white leather heel tabs and toe bumpers,
    white laces, white cupsoles
All generic, no logos (the real ones carry no readable marks at this resolution; any
side stripe is left out).

Source of truth: scripted, positions and lengths from the bedroom LiDAR survey
(Reference/bedroom_survey registered.npz, lidar + splat height maps in
Reference/shoes_work/), colours and shapes from the capture frames
wide_20260925_012252_927 / 012314_928 / 012716_930.

Frame: origin on the floor at the group's footprint centre, plan (238.8, 135.2);
front (toes) faces -Y. Placement: plan (238.8, 135.2), rotation 0 (toes south / -Y).

Dimensions (inches, local x east / y north; plan = local + (238.8, 135.2)):
  black W: heel (-5.4, 3.0) -> toe (-5.2, -7.6), 10.6 long               SCAN +-0.7
  black E: heel (-2.2, 7.4) -> toe (-2.4, -3.6), 11.0 long               SCAN +-0.7
  beige W: heel (2.0, 1.8) -> toe (1.8, -7.0), 8.8 -> use 10.0 (toe under the bed skirt) SCAN/EST
  beige E: heel (5.2, 3.8) -> toe (5.0, -6.6), 10.4 long                 SCAN +-0.7
  black: 4.1 wide, collar 4.4 high, sole 1.2                             SCAN (heel blobs z 3-4.5) / EST
  beige: 3.5 wide, collar 3.4 high, sole 0.9                             SCAN / EST
"""

import math

import bmesh
from mathutils import Matrix, Vector

import common

NAME = "shoes"


def m(inches):
    return inches * 0.0254


ATLAS = {
    "name": NAME,
    "size": 512,
    "regions": {
        "knit_black": (0, 0, 128, 128),
        "knit_side": (128, 0, 128, 128),
        "sole_grey": (256, 0, 128, 128),
        "insole_dark": (384, 0, 128, 128),
        "laces_black": (0, 128, 128, 128),
        "suede_tan": (128, 128, 128, 128),
        "leather_white": (256, 128, 128, 128),
        "sole_white": (384, 128, 128, 128),
        "laces_white": (0, 256, 128, 128),
        "insole_tan": (128, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("photo_match", 200, 40, 0.8), ("top_down", 180, 70, 0.8)]

STYLES = {
    "black": dict(W=4.1, H=4.4, Ts=1.2, upper="knit_black", side="knit_side", sole="sole_grey",
                  laces="laces_black", insole="insole_dark", tab="knit_black", toe="knit_black"),
    "beige": dict(W=3.5, H=3.4, Ts=0.9, upper="suede_tan", side="suede_tan", sole="sole_white",
                  laces="laces_white", insole="insole_tan", tab="leather_white", toe="leather_white"),
}
# (style, heel (x, y), toe (x, y), length override or None, mirror for left/right)
SHOES = [
    ("black", (-5.4, 3.0), (-5.2, -7.6), None, -1),
    ("black", (-2.2, 7.4), (-2.4, -3.6), None, 1),
    ("beige", (2.0, 1.8), (1.8, -7.0), 10.0, -1),
    ("beige", (5.2, 3.8), (5.0, -6.6), None, 1),
]

# footprint half-width (fraction of W/2) and top height (fraction of H) along heel->toe
WIDTH = [(0.0, 0.45), (0.04, 0.78), (0.12, 0.86), (0.3, 0.84), (0.5, 0.94), (0.66, 1.0),
         (0.8, 0.95), (0.9, 0.8), (0.96, 0.58), (1.0, 0.2)]
TOP = [(0.0, 0.92), (0.04, 1.0), (0.12, 0.93), (0.22, 0.62), (0.34, 0.62), (0.42, 0.92),
       (0.52, 0.8), (0.66, 0.62), (0.8, 0.46), (0.92, 0.36), (1.0, 0.26)]
STATIONS = [0.0, 0.02, 0.06, 0.12, 0.2, 0.28, 0.36, 0.44, 0.54, 0.64, 0.74, 0.84, 0.92, 0.97, 1.0]
ARC = [10, 35, 62, 80, 100, 118, 145, 170]          # degrees, right side (0) over to left (180)


def interp(table, s):
    for (s0, v0), (s1, v1) in zip(table, table[1:]):
        if s <= s1:
            t = (s - s0) / (s1 - s0) if s1 > s0 else 0
            return v0 + (v1 - v0) * t
    return table[-1][1]


def shoe(b, style, heel, toe, length, mirror):
    st = STYLES[style]
    hx, hy = heel
    tx, ty = toe
    d = Vector((tx - hx, ty - hy))
    L = length or d.length
    d.normalize()
    side = Vector((-d.y, d.x)) * -1                  # points to the shoe's right when toe is -Y... either way
    W, H, Ts = st["W"], st["H"], st["Ts"]
    rings = []
    for s in STATIONS:
        w = W / 2 * interp(WIDTH, s)
        h = H * interp(TOP, s)
        spring = 0.35 * max(0.0, (s - 0.85) / 0.15) ** 2      # toe spring
        heelr = 0.15 * max(0.0, (0.06 - s) / 0.06)            # heel rocker
        ring = []
        ws = w * 1.04
        pts = [(ws, 0.0), (ws, Ts)]
        for a in ARC:
            r = math.radians(a)
            # the knit instep bulges a little inboard (mirror picks the arch side)
            pts.append((w * math.cos(r), Ts + (h - Ts) * math.sin(r)))
        pts += [(-ws, Ts), (-ws, 0.0)]
        c = Vector((hx, hy)) + d * (s * L)
        for u, z in pts:
            p = c + side * (u * mirror)
            ring.append(b.bm.verts.new((m(p.x), m(p.y), m(z + spring + heelr))))
        rings.append((s, ring))
    n = len(rings[0][1])
    for i in range(len(rings) - 1):
        s0, r0 = rings[i]
        s1, r1 = rings[i + 1]
        sm = (s0 + s1) / 2
        for j in range(n):
            k = (j + 1) % n
            f = b.bm.faces.new((r0[j], r1[j], r1[k], r0[k]))
            # classify the segment j -> k of the cross-section
            if j == 0 or j == n - 2 or j == n - 1:
                reg = st["sole"]
            else:
                a0 = ARC[j - 2] if j >= 2 else 0
                a1 = ARC[k - 2] if 2 <= k < 2 + len(ARC) else 180
                amid = (a0 + a1) / 2
                top = 60 < amid < 120
                low = amid < 30 or amid > 150
                if top and 0.12 < sm < 0.38:
                    reg = st["insole"]
                elif top and 0.38 <= sm < 0.72:
                    reg = st["laces"]
                elif sm < 0.1 and not top:
                    reg = st["tab"]
                elif sm > 0.84 and low:
                    reg = st["toe"]
                elif low:
                    reg = st["side"]
                else:
                    reg = st["upper"]
            f.material_index = b.idx(reg)
    for (s, ring), rev in ((rings[0], False), (rings[-1], True)):
        f = b.bm.faces.new(list(reversed(ring)) if not rev else ring)
        f.material_index = b.idx(st["tab"] if s == 0 else st["toe"])


def build(coll):
    b = common.Builder(REGIONS)
    for style, heel, toe, length, mirror in SHOES:
        shoe(b, style, heel, toe, length, mirror)
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    lace = ("+Z", (m(-7.0), m(7.0)), (m(-8.5), m(8.5)))
    common.atlas_uvs(ob, ATLAS, planar={"laces_black": lace, "laces_white": lace,
                                        "knit_side": ("-X", (m(-9), m(9)), (0, m(3)))})
    common.collapse_materials(ob, {r: mat for r in REGIONS})
