"""Dining chair: ladder-back in dark charcoal-stained wood with a light grey upholstered
seat pad on a wood seat frame. Rear legs run up into raked back posts; a deep top rail
and four flat slats between them. One package, placed four times.

Source of truth: scripted. Sizes from the living-room survey scan (LiDAR + splat) and the
survey photos. Origin on the floor at the footprint centre; front (where you sit from)
faces -Y.
"""

import math

from mathutils import Matrix

import common

IN = 0.0254


def m(v):
    return v * IN


W = 18.0            # SCAN chair boxes 17.5-19.5 across
D = 19.0            # SCAN
H = 37.5            # SCAN back tops ~34-38 (thin rail, sparse points); brief ~38
SEAT_H = 18.0       # SCAN seat surface peaks at 16-18 in on all four chairs (brief said 21.5)
PAD_T = 2.0         # EST photo: pad sits proud of the frame
RAIL_H = 2.5        # EST seat frame rail depth
LEG = 1.5           # EST front leg square
POST = (1.25, 1.5)  # EST rear leg / back post (x, y)
TOP_RAIL_H = 3.0    # EST photo: top rail is the deepest bar
SLAT_H = 1.1        # EST
SLAT_T = 0.6        # EST
N_SLATS = 4         # photo
REAR_FOOT_Y = 8.75  # EST rear foot kicks back a little
KNEE_Y = 7.5        # EST post line at seat height
TOP_Y = 9.75        # EST raked back (~8 deg), curving (photo)

NAME = "dining_chair"
ATLAS = {
    "name": "dining_chair",
    "size": 512,
    "regions": {
        "wood_v": (0, 0, 256, 512),
        "wood_h": (256, 0, 256, 256),
        "cushion": (256, 256, 256, 256),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dining_chair": {"atlas": "dining_chair", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_left", 300, 25, 0.9), ("high_back", 160, 55, 0.9)]


def _post_y(z):
    zk = SEAT_H - PAD_T
    if z <= zk:
        return REAR_FOOT_Y + (KNEE_Y - REAR_FOOT_Y) * z / zk
    t = (z - zk) / (H - zk)
    return KNEE_Y + (TOP_Y - KNEE_Y) * t ** 0.75     # bends back most just above the seat


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0, seg=1, mat=None: b.box(
        r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg, matrix=mat)
    x1, y0 = W / 2, -D / 2
    zf = SEAT_H - PAD_T              # top of seat frame
    zr = zf - RAIL_H
    # front legs
    for s in (-1, 1):
        cx = s * (x1 - LEG / 2)
        bx("wood_v", (cx - LEG / 2, y0, 0.0), (cx + LEG / 2, y0 + LEG, zf), 0.1)
    # rear legs + back posts: swept rectangle, straight below the seat, raked above
    pw, pd = POST
    prof = [(-m(pw) / 2, -m(pd) / 2), (m(pw) / 2, -m(pd) / 2), (m(pw) / 2, m(pd) / 2), (-m(pw) / 2, m(pd) / 2)]
    for s in (-1, 1):
        cx = s * (x1 - pw / 2 - 0.25)
        pts = [(m(cx), m(_post_y(0.0)), 0.0)] + [(m(cx), m(_post_y(z)), m(z)) for z in [0.75, zf] + [zf + (H - zf) * k / 5 for k in range(1, 6)]]
        pts[1] = (pts[1][0], pts[0][1], pts[1][2])   # vertical foot keeps the end cap flat on the floor
        b.sweep("wood_v", pts, prof, up=(0, 1, 0))
    # seat frame rails
    yb = _post_y(zf) - POST[1] / 2
    rail_t = 0.9
    bx("wood_h", (-x1 + LEG, y0, zr), (x1 - LEG, y0 + rail_t, zf), 0.1)
    bx("wood_h", (-x1 + pw, yb - rail_t, zr), (x1 - pw, yb, zf), 0.1)
    for s in (-1, 1):
        xo = s * (x1 - 0.2)
        bx("wood_h", (min(xo, xo - s * rail_t), y0 + LEG, zr), (max(xo, xo - s * rail_t), yb - rail_t, zf), 0.1)
    # upholstered pad
    bx("cushion", (-x1 + 0.3, y0 + 0.3, zf), (x1 - 0.3, yb + 0.2, SEAT_H), 0.6, 2)
    # back: top rail and slats, tilted with the posts
    inner = x1 - pw - 0.25
    bars = [(H - TOP_RAIL_H - 0.3, TOP_RAIL_H, 1.0)]
    lo, hi = zf + 5.0, H - TOP_RAIL_H - 0.3 - 2.2
    for i in range(N_SLATS):
        zc = hi - i * (hi - lo) / (N_SLATS - 1)
        bars.append((zc - SLAT_H / 2, SLAT_H, SLAT_T))
    for zb, hgt, t in bars:
        zc = zb + hgt / 2
        yc = _post_y(zc)
        rake = math.atan2(_post_y(zc + 0.5) - _post_y(zc - 0.5), 1.0)
        mat = (Matrix.Translation((0, m(yc), m(zc))) @ Matrix.Rotation(-rake, 4, "X"))
        bx("wood_h", (-inner - 0.2, -t / 2, -hgt / 2), (inner + 0.2, t / 2, hgt / 2), 0.15 if t > 0.8 else 0.0, 1, mat)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
