"""Bathroom vanity: 50 in honey-oak sink base on the west wall (full-width top rail
false front, one door with an arched bow pull on the south half, two stacked drawers
with mushroom knobs on the north half, fronts with eased edges, toe kick), white
cultured-marble top with an integral oval basin set off-centre to the south (pop-up
drain), back and south side splashes, a brushed-nickel 4 in centerset faucet with two
lever handles, a two-post toilet-paper holder on the north side panel, and the frameless
clip-hung mirror above. Hinges are concealed (none show in the photos).

Wear (texture, bathroom atlas): finger grime round the pull and knobs, paler scuffed
bottom edges, water-marked side panel near the floor, and the basin (own atlas region,
mapped from above) with a brassy grime ring round the drain and water spots.

Source of truth: scripted, from the bathroom LiDAR survey (Reference/bathroom_survey/,
fixtures.py boxes vanity_counter, vanity_cabinet, backsplash, sink_bowl, mirror, and the
chk_vanity_* check images). SCAN = measured from the registered capture (about +-1 in);
EST = from the photos or standard sizes.

Local frame: front faces -Y, back against the wall at +Y. Placed at rotation 90 the
front faces east, local +X points north and local +Y west (the wall):
  plan y = 227.55 + local x,  plan x = 189.1 - local y   (inches, model plan coords)
Origin on the floor at the counter's footprint centre; the wall face is at y +11.35 in.

Objects:
  vanity         cabinet, top, basin, faucet, toilet-paper holder (static)
  vanity_mirror  frameless wall mirror with clips
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

NAME = "vanity"
ATLAS = S.ATLAS
MATERIALS = S.MATERIALS
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 1.0), ("basin", 0, 55, 0.6), ("survey_view", 330, 30, 0.8),
         ("front_close", 350, 15, 0.5), ("faucet", 15, 35, 0.28), ("tp_holder", 60, 15, 0.45)]

# --- dimensions (inches) ---------------------------------------------------------
TOP_W, TOP_D = 50.1, 22.65     # SCAN counter
TOP_Z0, TOP_Z = 30.4, 31.9     # SCAN counter underside / finished height
CAB_W, CAB_D = 49.6, 21.95     # SCAN cabinet (flush with the south wall, 0.5 short at N)
WALL_Y = 11.35                 # SCAN wall face (plan x 177.75) from the placement centre
TOE_H, TOE_D = 3.5, 3.0        # EST (survey: 3-4 in)
SPLASH_H, SPLASH_T = 3.9, 0.75  # SCAN height / EST thickness
SINK_W, SINK_D = 17.0, 13.0    # SCAN integral oval, along the counter x across it
SINK_X, SINK_Y = -13.95, 1.6   # SCAN centre (plan 217.5 - 3.9, 187.5)
SINK_DEPTH = 6.5               # SCAN (box z 25..31.9)
RAIL_Z = (25.3, 29.8)          # EST top rail false front (~5 in, survey)
DOOR_Z = (4.2, 24.8)           # EST
GAP = 0.4                      # EST between fronts
FRONT_T = 0.75                 # EST door/drawer slab
EDGE_EASE = 0.2                # EST chamfer on the fronts' edges
MIRROR_W, MIRROR_Z = 23.4, (39.2, 76.1)   # SCAN
MIRROR_X = -0.45               # SCAN centre (plan y 231.0 - 3.9)
MIRROR_T = 0.25                # EST

REGIONS = ["oak_doors", "oak", "dark", "marble", "sink_bowl", "nickel", "paper"]


def counter_outline(cx, cy, x0, x1, y0, y1, n=44):
    """Rectangle outline sampled at polar angles about (cx, cy), plus its corners, so it
    bridges to the basin rings."""
    corners = [math.atan2(y - cy, x - cx) for x, y in ((x1, y1), (x0, y1), (x0, y0), (x1, y0))]
    angs = sorted({round(2 * math.pi * i / n - math.pi, 6) for i in range(n)}
                  | {round(a, 6) for a in corners})
    out = []
    for a in angs:
        c, s = math.cos(a), math.sin(a)
        kx = ((x1 - cx) / c if c > 0 else (x0 - cx) / c) if abs(c) > 1e-9 else 1e9
        ky = ((y1 - cy) / s if s > 0 else (y0 - cy) / s) if abs(s) > 1e-9 else 1e9
        k = min(kx, ky)
        out.append((cx + k * c, cy + k * s))
    return out


def front_slab(b, x0, x1, z0, z1, yf, frame=0.0):
    """A door/drawer slab proud of the face at yf, its front edges eased with a small
    chamfer (the routed edge the photos show); frame > 0 adds a raised frame."""
    t = m(FRONT_T)
    before = set(b.bm.faces)
    b.box("oak", (x0, yf - t, z0), (x1, yf, z1), bevel=m(EDGE_EASE), segments=1)
    faces = [f for f in b.bm.faces if f not in before]
    b.bm.normal_update()
    for f in faces:
        if f.normal.y < -0.9:
            f.material_index = b.idx("oak_doors")
    if frame:
        fr, p = m(frame), m(0.22)
        for lo, hi in (((x0, z1 - fr), (x1, z1)), ((x0, z0), (x1, z0 + fr)),
                       ((x0, z0 + fr), (x0 + fr, z1 - fr)), ((x1 - fr, z0 + fr), (x1, z1 - fr))):
            fs = b.box("oak", (lo[0], yf - t - p, lo[1]), (hi[0], yf - t, hi[1]))
            b.bm.normal_update()
            for f in fs:
                if f.normal.y < -0.9:
                    f.material_index = b.idx("oak_doors")


def build_vanity(coll):
    b = common.Builder(REGIONS)
    xs, xn = -m(TOP_W / 2), m(TOP_W / 2)           # south, north counter ends
    cx0, cx1 = xs, xs + m(CAB_W)
    yb = m(WALL_Y)
    yf = yb - m(CAB_D)
    ytf = yb - m(TOP_D)
    ztop = m(TOP_Z0)
    t = m(0.75)
    # Toe kick, carcass (sides, back, deck, face).
    b.box("dark", (cx0 + t, yf + m(TOE_D), 0), (cx1 - t, yb, m(TOE_H)))
    b.box("oak", (cx0, yf, 0), (cx0 + t, yb, ztop))
    b.box("oak", (cx1 - t, yf, 0), (cx1, yb, ztop))
    b.box("oak", (cx0 + t, yb - t, m(TOE_H)), (cx1 - t, yb, ztop))
    b.box("oak", (cx0 + t, yf, m(TOE_H)), (cx1 - t, yb - t, m(TOE_H) + t))
    faces = b.box("oak", (cx0 + t, yf, m(TOE_H)), (cx1 - t, yf + t, ztop))
    b.bm.normal_update()
    for f in faces:
        if f.normal.y < -0.9:
            f.material_index = b.idx("oak_doors")
    # Fronts: rail false front, south door, north drawers.
    g = m(GAP)
    fx0, fx1 = cx0 + m(0.6), cx1 - m(0.6)
    mid = (fx0 + fx1) / 2
    front_slab(b, fx0, fx1, m(RAIL_Z[0]), m(RAIL_Z[1]), yf)
    dz0, dz1 = m(DOOR_Z[0]), m(DOOR_Z[1])
    front_slab(b, fx0, mid - g / 2, dz0, dz1, yf, frame=2.3)
    dzm = (dz0 + dz1) / 2
    front_slab(b, mid + g / 2, fx1, dz0, dzm - g / 2, yf)
    front_slab(b, mid + g / 2, fx1, dzm + g / 2, dz1, yf)
    yface = yf - m(FRONT_T)
    # Door pull: a vertical arched bow pull near the centre gap, upper half (005839):
    # round rod bowing out from two feet, on small round bases.
    px = mid - g / 2 - m(2.4)
    pz0, pz1 = dz1 - m(9.5), dz1 - m(3.0)
    bow = [(px, yface - m(1.15) * math.sin(math.pi * (0.08 + 0.84 * i / 8)) + m(0.05),
            pz0 + (pz1 - pz0) * i / 8) for i in range(9)]
    b.sweep("nickel", [(x, y, z) for x, y, z in bow], common.circle_profile(m(0.2), 6),
            up=(0, -1, 0))
    for pz in (pz0, pz1):
        S.frustum(b, "nickel", (px, yface - m(0.12), pz), m(0.32), m(0.24), m(0.24), "Y", 8,
                  sign=-1)
    # Drawer knobs: small mushroom knobs on a stem.
    kx = (mid + fx1) / 2
    for kz in ((dz0 + dzm) / 2, (dzm + dz1) / 2 + m(0.8)):
        S.frustum(b, "nickel", (kx, yface - m(0.45), kz), m(0.3), m(0.2), m(0.9), "Y", 8,
                  sign=-1)
        b.cylinder("nickel", (kx, yface - m(1.15), kz), m(0.6), m(0.45), axis="Y", segments=14,
                   bevel=m(0.12))

    # Counter with the integral basin: outer rectangle -> rim -> bowl -> floor.
    sx, sy = m(SINK_X), m(SINK_Y)
    outer = counter_outline(sx, sy, xs, xn, ytf, yb)
    rim = S.match_polar(outer, sx, sy, S.ellipse_at(sx, sy, m(SINK_W / 2), m(SINK_D / 2)))
    mid_r = S.match_polar(outer, sx, sy, S.ellipse_at(sx, sy, m(SINK_W / 2 - 1.3),
                                                      m(SINK_D / 2 - 1.2)))
    bot = S.match_polar(outer, sx, sy, S.ellipse_at(sx, sy, m(SINK_W / 2 - 4.5),
                                                    m(SINK_D / 2 - 3.8)))
    zt = m(TOP_Z)
    r_ob = S.ring(b, outer, ztop)
    r_ot = S.ring(b, outer, zt)
    r_rim = S.ring(b, rim, zt)
    zmid = zt - m(SINK_DEPTH * 0.55)
    # Where the bowl wall passes the counter's underside: the underside is an annulus
    # round this ring (a full cap there used to close the bowl off at 30.4 in).
    f = (zt - ztop) / (zt - zmid)
    und = [(a[0] + f * (c[0] - a[0]), a[1] + f * (c[1] - a[1])) for a, c in zip(rim, mid_r)]
    r_und = S.ring(b, und, ztop)
    r_mid = S.ring(b, mid_r, zmid)
    r_bot = S.ring(b, bot, zt - m(SINK_DEPTH))
    S.bridge(b, "marble", r_ob, r_ot)
    S.bridge(b, "marble", r_ot, r_rim)
    S.bridge(b, "sink_bowl", r_rim, r_und)
    S.bridge(b, "sink_bowl", r_und, r_mid)
    S.bridge(b, "sink_bowl", r_mid, r_bot)
    S.cap(b, "sink_bowl", r_bot)
    S.bridge(b, "marble", r_und, r_ob)
    # Pop-up drain: flange and the stopper cap (the grime ring round it is texture).
    zb = zt - m(SINK_DEPTH)
    S.frustum(b, "nickel", (sx, sy, zb + m(0.05)), m(0.9), m(0.8), m(0.12), "Z", 12)
    b.cylinder("nickel", (sx, sy, zb + m(0.2)), m(0.62), m(0.25), segments=12, bevel=m(0.08))
    # Back splash and the south side splash.
    b.box("marble", (xs, yb - m(SPLASH_T), zt), (xn, yb, zt + m(SPLASH_H)), bevel=m(0.1))
    b.box("marble", (xs, ytf + m(0.6), zt), (xs + m(SPLASH_T), yb - m(SPLASH_T), zt + m(SPLASH_H)),
          bevel=m(0.1))
    # Faucet: two-handle centerset, brushed nickel, behind the basin.
    fy = sy + m(SINK_D / 2) + m(1.4)
    b.box("nickel", (sx - m(3.2), fy - m(0.9), zt), (sx + m(3.2), fy + m(0.9), zt + m(0.7)),
          bevel=m(0.3))
    b.cylinder("nickel", (sx, fy, zt + m(1.6)), m(0.65), m(2.0), segments=14)
    arc =[(sx, fy, zt + m(2.4))] + [(sx, fy - m(1.2) - m(3.0) * i / 3,
                                      zt + m(3.0) - m(0.6) * (i / 3) ** 2) for i in range(4)]
    b.sweep("nickel", arc, common.circle_profile(m(0.4), 10), up=(0, 0, 1))
    # Two lever handles on the 4 in centres (photo 005857): a tapered hub each, and a
    # flat blade reaching forward and out, tipped slightly up.
    for hx in (-2.0, 2.0):
        sgn = 1 if hx > 0 else -1
        hxm = sx + m(hx)
        S.frustum(b, "nickel", (hxm, fy, zt + m(0.9)), m(0.75), m(0.5), m(1.1), "Z", 12)
        blade = [(hxm, fy - m(0.1), zt + m(1.35)),
                 (hxm + sgn * m(0.9), fy - m(1.2), zt + m(1.65)),
                 (hxm + sgn * m(1.7), fy - m(2.4), zt + m(1.95)),
                 (hxm + sgn * m(2.1), fy - m(3.2), zt + m(2.05))]
        b.sweep("nickel", blade, [(-m(0.32), -m(0.12)), (m(0.32), -m(0.12)), (m(0.26), m(0.12)),
                                  (-m(0.26), m(0.12))], up=(0, 0, 1))

    # Toilet-paper holder on the north side panel: two bell posts either side of the
    # roll with the spindle between them (photos 005931, 005934).
    hy, hz = -m(4.5), m(24.0)
    ry = hy - m(1.6)
    for py in (ry - m(2.3), ry + m(2.3)):
        S.frustum(b, "nickel", (cx1 + m(1.3), py, hz), m(0.9), m(0.3), m(2.6), "X", 10)
    b.cylinder("nickel", (cx1 + m(2.6), ry, hz), m(0.3), m(4.6), axis="Y", segments=8)
    b.cylinder("paper", (cx1 + m(2.6), ry, hz), m(2.2), m(3.9), axis="Y", segments=18,
               cap_region="paper")
    ob = b.to_object("vanity", coll)
    # The open bowl makes the counter a non-closed shell, and the normal recalc can turn the
    # bowl faces outward (down): Unity culls them and you see into the cabinet. Face every
    # bowl face toward a point above the bowl's centre.
    import bmesh as _bm
    from mathutils import Vector as _V
    bm = _bm.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    bowl = [i for i, s_ in enumerate(ob.data.materials) if s_ and s_.name.split(".")[0] == "sink_bowl"]
    eye = _V((sx, sy, zt + m(4.0)))
    flip = [f for f in bm.faces if f.material_index in bowl and f.normal.dot(eye - f.calc_center_median()) < 0]
    _bm.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def build_mirror(coll):
    b = common.Builder(["mirror", "nickel"])
    yb = m(WALL_Y)
    x0, x1 = m(MIRROR_X - MIRROR_W / 2), m(MIRROR_X + MIRROR_W / 2)
    z0, z1 = m(MIRROR_Z[0]), m(MIRROR_Z[1])
    b.box("mirror", (x0, yb - m(MIRROR_T), z0), (x1, yb, z1), bevel=m(0.06), segments=1)
    # Clips: two along the bottom, two at the top, one on each side.
    clips = [(x0 + m(4), z0), (x1 - m(4), z0), (x0 + m(4), z1), (x1 - m(4), z1)]
    for cx, cz in clips:
        b.box("nickel", (cx - m(0.5), yb - m(MIRROR_T + 0.15), cz - m(0.35)),
              (cx + m(0.5), yb, cz + m(0.35)), bevel=m(0.1), segments=1)
    for cx in (x0, x1):
        cz = (z0 + z1) / 2
        b.box("nickel", (cx - m(0.35), yb - m(MIRROR_T + 0.15), cz - m(0.5)),
              (cx + m(0.35), yb, cz + m(0.5)), bevel=m(0.1), segments=1)
    return b.to_object("vanity_mirror", coll)


def build(coll):
    return [build_vanity(coll), build_mirror(coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    planar = {
        "oak_doors": ("-Y", (-m(TOP_W / 2), m(TOP_W / 2)), (0, m(TOP_Z0))),
        "oak": ("+X", (-m(WALL_Y), m(WALL_Y)), (0, m(TOP_Z0))),
        "sink_bowl": ("+Z", (m(SINK_X - SINK_W / 2), m(SINK_X + SINK_W / 2)),
                      (m(SINK_Y - SINK_D / 2), m(SINK_Y + SINK_D / 2))),
    }
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=planar)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
