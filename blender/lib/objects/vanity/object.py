"""Bathroom vanity: 30 in oak sink base (two shaker doors, brushed-nickel pulls, toe
kick), cultured-marble top with an integral oval basin and backsplash, a chrome
single-lever faucet, and a frameless wall mirror above.

Source of truth: scripted. Coarse block-in from standard sizes (no photos of the real
bathroom yet): every size is EST. The oak is assumed to match the kitchen cabinets
(golden oak shaker), whose grain the atlas borrows.

Local frame: front faces -Y, back against the wall at +Y. Origin on the floor at the
footprint centre; the footprint runs y -10.75..+10.75 in, so the marker sits 10.75 in
out from the wall face.

Objects:
  vanity         cabinet, top, basin, faucet (static; the doors are part of it in this
                 block-in pass, split them out when they get hinges)
  vanity_mirror  wall mirror, 30 x 36 in, bottom 40 in above the floor
"""

import importlib
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bathtub"))

import common  # noqa: E402
import bathroom_shared as S  # noqa: E402

importlib.reload(S)
m = S.m
F = S.VANITY_FRONT

NAME = "vanity"
ATLAS = S.ATLAS
MATERIALS = S.MATERIALS
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 1.0), ("basin", 0, 55, 0.6)]

HALF_D = 10.75        # EST top depth 21.5 (cabinet 20.75 + overhang)
TOP_W = 31.0          # EST top 0.5 in over each side
TOP_T = 0.75          # EST
TOP_Z = 32.0          # EST finished counter height
TOE_H, TOE_D = 3.5, 3.0   # EST toe kick
SPLASH_H, SPLASH_T = 4.0, 0.75   # EST
BASIN_W, BASIN_D, BASIN_DEPTH = 16.0, 12.5, 6.0   # EST integral oval bowl
BASIN_CY = -1.0       # EST
MIRROR_W, MIRROR_H, MIRROR_Z = 30.0, 36.0, 40.0   # EST
MIRROR_T = 0.25       # EST

REGIONS = ["oak_doors", "oak", "dark", "marble", "chrome", "nickel"]


def build_vanity(coll):
    b = common.Builder(REGIONS)
    x0, x1 = m(F["x"][0]), m(F["x"][1])
    yb = m(HALF_D)
    yf = yb - m(20.75)                     # cabinet front
    ztop = m(TOP_Z - TOP_T)
    # Toe kick and carcass (front face mapped with the door drawing).
    b.box("dark", (x0 + m(0.75), yf + m(TOE_D), 0), (x1 - m(0.75), yb, m(TOE_H)))
    # Open-topped carcass (sides, back, deck, face frame) so the basin can hang inside.
    t = m(0.75)
    b.box("oak", (x0, yf, m(TOE_H)), (x0 + t, yb, ztop))
    b.box("oak", (x1 - t, yf, m(TOE_H)), (x1, yb, ztop))
    b.box("oak", (x0 + t, yb - t, m(TOE_H)), (x1 - t, yb, ztop))
    b.box("oak", (x0 + t, yf, m(TOE_H)), (x1 - t, yb - t, m(TOE_H) + t))
    faces = b.box("oak", (x0 + t, yf, m(TOE_H)), (x1 - t, yf + t, ztop))
    b.bm.normal_update()
    for f in faces:
        if f.normal.y < -0.9:
            f.material_index = b.idx("oak_doors")
    b.box("dark", (x0 + t, yf + t, m(TOE_H) + t), (x1 - t, yb - t, m(TOE_H) + t + m(0.05)))
    # Doors: slabs proud of the face frame.
    dz0, dz1 = m(F["door_z"][0]), m(F["door_z"][1])
    for d0, d1 in F["doors"]:
        fs = b.box("oak", (m(d0), yf - m(0.75), dz0), (m(d1), yf, dz1))
        b.bm.normal_update()
        for f in fs:
            if f.normal.y < -0.9:
                f.material_index = b.idx("oak_doors")
        # Bar pull near the centre gap, vertical, top of the door.
        px = m(d1 - 2.0) if d1 < 0 else m(d0 + 2.0)
        b.box("nickel", (px - m(0.25), yf - m(1.9), dz1 - m(6.0)),
              (px + m(0.25), yf - m(1.4), dz1 - m(2.0)), bevel=m(0.15))
        for pz in (dz1 - m(5.6), dz1 - m(2.4)):
            b.box("nickel", (px - m(0.2), yf - m(1.5), pz - m(0.2)),
                  (px + m(0.2), yf - m(0.75), pz + m(0.2)))

    # Counter with the integral basin: outer rounded rect -> rim -> bowl -> floor.
    cy = m(BASIN_CY)
    # Uniform polar angles about the basin centre plus the four exact corner angles.
    W2, D2 = m(TOP_W / 2), m(HALF_D)
    corners = [math.atan2(sy * D2 - cy, sx * W2) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    angs = sorted({round(2 * math.pi * i / 44 - math.pi, 6) for i in range(44)}
                  | {round(a, 6) for a in corners})
    outer = []
    for a in angs:
        c, sn = math.cos(a), math.sin(a)
        k = min(W2 / abs(c) if abs(c) > 1e-9 else 1e9,
                ((D2 - cy) if sn > 0 else (D2 + cy)) / abs(sn) if abs(sn) > 1e-9 else 1e9)
        outer.append((k * c, cy + k * sn))
    rim = S.match_polar(outer, 0, cy, S.ellipse_at(0, cy, m(BASIN_W / 2), m(BASIN_D / 2)))
    mid = S.match_polar(outer, 0, cy, S.ellipse_at(0, cy, m(BASIN_W / 2 - 1.2),
                                                    m(BASIN_D / 2 - 1.2)))
    bot = S.match_polar(outer, 0, cy, S.ellipse_at(0, cy, m(BASIN_W / 2 - 4.0),
                                                    m(BASIN_D / 2 - 3.5)))
    zt = m(TOP_Z)
    r_ob = S.ring(b, outer, ztop)
    r_ot = S.ring(b, outer, zt)
    r_rim = S.ring(b, rim, zt)
    r_mid = S.ring(b, mid, zt - m(BASIN_DEPTH * 0.55))
    r_bot = S.ring(b, bot, zt - m(BASIN_DEPTH))
    S.bridge(b, "marble", r_ob, r_ot)
    S.bridge(b, "marble", r_ot, r_rim)
    S.bridge(b, "marble", r_rim, r_mid)
    S.bridge(b, "marble", r_mid, r_bot)
    S.cap(b, "marble", r_bot)
    S.cap(b, "marble", r_ob)
    b.cylinder("chrome", (0, cy, zt - m(BASIN_DEPTH) + m(0.06)), m(0.9), m(0.12),
               segments=12)
    # Backsplash.
    b.box("marble", (-m(TOP_W / 2), yb - m(SPLASH_T), zt), (m(TOP_W / 2), yb, zt + m(SPLASH_H)),
          bevel=m(0.1))
    # Faucet: deck plate, body, spout, lever.
    fy = yb - m(SPLASH_T) - m(2.2)
    b.box("chrome", (-m(3.0), fy - m(1.0), zt), (m(3.0), fy + m(1.0), zt + m(0.5)), bevel=m(0.2))
    b.cylinder("chrome", (0, fy, zt + m(2.0)), m(0.8), m(3.0), segments=16)
    b.box("chrome", (-m(0.45), fy - m(4.2), zt + m(2.8)), (m(0.45), fy, zt + m(3.5)),
          bevel=m(0.2))
    b.box("chrome", (-m(0.35), fy - m(4.2), zt + m(2.3)), (m(0.35), fy - m(3.4), zt + m(2.9)),
          bevel=m(0.1))
    b.box("chrome", (-m(0.3), fy - m(0.2), zt + m(3.5)), (m(0.3), fy + m(3.0), zt + m(4.1)),
          bevel=m(0.15))
    return b.to_object("vanity", coll)


def build_mirror(coll):
    b = common.Builder(["mirror"])
    yb = m(HALF_D)
    b.box("mirror", (-m(MIRROR_W / 2), yb - m(MIRROR_T), m(MIRROR_Z)),
          (m(MIRROR_W / 2), yb, m(MIRROR_Z + MIRROR_H)), bevel=m(0.08))
    return b.to_object("vanity_mirror", coll)


def build(coll):
    return [build_vanity(coll), build_mirror(coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    planar = {
        "oak_doors": ("-Y", (m(F["x"][0]), m(F["x"][1])), (m(F["z"][0]), m(F["z"][1]))),
        "oak": ("+X", (-m(HALF_D), m(HALF_D)), (0, m(TOP_Z))),
    }
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=planar)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
