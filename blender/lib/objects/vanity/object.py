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
  plan y = 227.55 + local x,  plan x = 182.65 - local y   (inches, model plan coords)
Origin on the floor at the counter's footprint centre; the wall face is at y +11.35 in.

Interior (photos 17/18, Reference/cupboards_drawers/ 032025775 and 032032811): the
carcass is hollow behind an oak face frame. Sides, back and floor are white melamine
inside (floor top 5.0 in, its front edge chipped), a white partition separates the sink
space from the drawer stack, and a white PVC tailpiece and P-trap run from the basin's
drain back into the wall. The basin has an underside shell so it reads from below.

Objects:
  vanity                       carcass, face frame, rail false front, top, basin, drain,
                               faucet, toilet-paper holder (static)
  vanity_mirror                frameless wall mirror with clips
  vanity_door_sink             the sink door with its bow pull, HINGED ON ITS SOUTH (outer,
                               local -X) EDGE (photo 17: the hinges are on the left stile);
                               origin on the hinge axis at the leaf's front outer corner
  vanity_door_sink_out         empty 1 in in front of the door's face centre
  vanity_drawer_top / _bottom  white open-top drawer boxes with the oak fronts and knobs;
                               origin at the box's bottom centre (photo 18 = top drawer)
  vanity_drawer_top_grab / vanity_drawer_bottom_grab   empties at the knobs
Render-only check: VANITY_OPEN=1 swings the door 100 deg and pulls the drawers.
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
STILE = 1.5                    # PHOTO 17 face-frame end stiles (vs the 0.75 in panels)
MID_STILE = 1.7                # PHOTO 17/18 stile between the door and the drawer stack
MID_RAIL = 1.2                 # EST rail between the two drawers
FLOOR_Z = 5.0                  # PHOTO 17 cabinet floor top (white melamine), on the bottom rail
OPEN_TOP = 24.3                # EST top of the openings (the fronts overlay them ~0.5 in)
DRAWER_D = 19.0                # EST drawer box depth (photo 18: deep, ends short of the back)
DRAWER_SIDE = 0.5              # PHOTO 18 white drawer-box sides/back
DRAWER_BOT = 0.25              # EST drawer bottom
DRAWER_H = 7.0                 # EST drawer box height (both drawers)
DRAWER_CLR = 0.5               # EST box-to-opening side clearance (slides)
MIRROR_W, MIRROR_Z = 23.4, (39.2, 76.1)   # SCAN
MIRROR_X = -0.45               # SCAN centre (plan y 231.0 - 3.9)
MIRROR_T = 0.25                # EST

REGIONS = ["oak_doors", "oak", "dark", "marble", "sink_bowl", "nickel", "paper", "porcelain"]


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


def panel(b, region, lo, hi, inner=None, inner_region="porcelain"):
    """A carcass panel (closed box); its faces whose normal points along `inner` (the
    side facing the cabinet's interior) get the white melamine."""
    faces = b.box(region, lo, hi)
    if inner is not None:
        b.bm.normal_update()
        for f in faces:
            if f.normal.dot(inner) > 0.9:
                f.material_index = b.idx(inner_region)
    return faces


def frame_box(b, lo, hi):
    """A face-frame member: oak, its front face on the door-grain projection."""
    faces = b.box("oak", lo, hi)
    b.bm.normal_update()
    for f in faces:
        if f.normal.y < -0.9:
            f.material_index = b.idx("oak_doors")
    return faces


def layout():
    """Shared x/y/z of the carcass, fronts and openings (metres)."""
    L = {}
    L["xs"], L["xn"] = -m(TOP_W / 2), m(TOP_W / 2)
    L["cx0"], L["cx1"] = L["xs"], L["xs"] + m(CAB_W)
    L["yb"] = m(WALL_Y)
    L["yf"] = L["yb"] - m(CAB_D)
    L["ztop"] = m(TOP_Z0)
    L["fx0"], L["fx1"] = L["cx0"] + m(0.6), L["cx1"] - m(0.6)
    L["mid"] = (L["fx0"] + L["fx1"]) / 2
    L["dz0"], L["dz1"] = m(DOOR_Z[0]), m(DOOR_Z[1])
    L["dzm"] = (L["dz0"] + L["dz1"]) / 2
    L["yface"] = L["yf"] - m(FRONT_T)
    L["kx"] = (L["mid"] + L["fx1"]) / 2
    # Face-frame openings: door (south) and the two drawers (north).
    L["ox0"] = L["cx0"] + m(STILE)                  # door opening south edge
    L["ox1"] = L["mid"] - m(MID_STILE / 2)          # door opening north edge
    L["ox2"] = L["mid"] + m(MID_STILE / 2)          # drawer openings south edge
    L["ox3"] = L["cx1"] - m(STILE)                  # drawer openings north edge
    L["oz0"], L["oz1"] = m(FLOOR_Z), m(OPEN_TOP)
    return L


def build_vanity(coll):
    b = common.Builder(REGIONS)
    L = layout()
    xs, xn = L["xs"], L["xn"]
    cx0, cx1, yb, yf, ytf = L["cx0"], L["cx1"], L["yb"], L["yf"], L["yb"] - m(TOP_D)
    ztop = L["ztop"]
    t = m(0.75)
    zf = m(FLOOR_Z)
    # Toe kick; hollow carcass: sides, back and floor are oak outside and white melamine
    # inside (photo 17: white walls and floor under the sink).
    b.box("dark", (cx0 + t, yf + m(TOE_D), 0), (cx1 - t, yb, m(TOE_H)))
    panel(b, "oak", (cx0, yf, 0), (cx0 + t, yb, ztop), inner=(1, 0, 0))
    panel(b, "oak", (cx1 - t, yf, 0), (cx1, yb, ztop), inner=(-1, 0, 0))
    panel(b, "oak", (cx0 + t, yb - t, m(TOE_H)), (cx1 - t, yb, ztop), inner=(0, -1, 0))
    panel(b, "oak", (cx0 + t, yf + t, zf - t), (cx1 - t, yb - t, zf), inner=(0, 0, 1))
    # Chipped front edge of the floor (photo 17): particleboard showing through the white
    # in a few nicks along the front.
    for a, w in ((0.06, 2.2), (0.21, 0.8), (0.33, 3.1), (0.55, 1.4), (0.74, 2.6), (0.9, 0.9)):
        x0 = L["ox0"] + (L["ox1"] - L["ox0"]) * a
        b.box("oak", (x0, yf + t - m(0.02), zf - m(0.04)), (x0 + m(w), yf + t + m(0.22), zf + m(0.012)))
    # Partition between the sink space and the drawer stack, white both sides.
    p0 = L["ox2"] - t
    panel(b, "porcelain", (p0, yf + t, zf), (L["ox2"], yb - t, ztop))
    # Face frame (stiles, rails), flush with the old solid face: the openings it leaves.
    yfr = yf + t
    frame_box(b, (cx0, yf, m(TOE_H)), (L["ox0"], yfr, ztop))
    frame_box(b, (L["ox3"], yf, m(TOE_H)), (cx1, yfr, ztop))
    frame_box(b, (L["ox1"], yf, m(TOE_H)), (L["ox2"], yfr, ztop))
    frame_box(b, (L["ox0"], yf, m(TOE_H)), (L["ox1"], yfr, zf))
    frame_box(b, (L["ox2"], yf, m(TOE_H)), (L["ox3"], yfr, zf))
    frame_box(b, (L["ox0"], yf, L["oz1"]), (L["ox3"], yfr, ztop))
    frame_box(b, (L["ox2"], yf, L["dzm"] - m(MID_RAIL / 2)), (L["ox3"], yfr, L["dzm"] + m(MID_RAIL / 2)))
    # Semi-concealed hinges on the south stile's opening edge (photo 17: chrome, two).
    for hz in (L["dz0"] + m(3.2), L["dz1"] - m(3.2)):
        b.box("nickel", (L["ox0"] - m(0.02), yf + m(0.04), hz - m(1.1)),
              (L["ox0"] + m(0.1), yf + m(0.62), hz + m(1.1)))
    # Rail false front (static).
    front_slab(b, L["fx0"], L["fx1"], m(RAIL_Z[0]), m(RAIL_Z[1]), yf)

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
    # Underside of the basin, seen from inside the cabinet: a shell 0.3 in under the bowl
    # (the bowl faces alone are one-sided and would show the room through them).
    def push(ring_, d):
        out = []
        for x, y in ring_:
            dx, dy = x - sx, y - sy
            k = math.hypot(dx, dy) or 1.0
            out.append((x + dx / k * m(d), y + dy / k * m(d)))
        return out
    zb = zt - m(SINK_DEPTH)
    u0 = S.ring(b, push(und, 0.3), ztop)
    u1 = S.ring(b, push(mid_r, 0.3), zmid - m(0.25))
    u2 = S.ring(b, push(bot, 0.3), zb - m(0.3))
    shell = S.bridge(b, "porcelain", u0, u1) + S.bridge(b, "porcelain", u1, u2) +         S.cap(b, "porcelain", u2)
    # Drain under the basin (photo 17): white PVC tailpiece, slip nuts, a P-trap whose
    # arm runs back into the wall.
    pr = common.circle_profile(m(0.75), 10)
    trap = [(sx, sy, zb - m(0.3)), (sx, sy, m(21.2)), (sx, sy + m(0.4), m(19.9)),
            (sx, sy + m(1.6), m(19.3)), (sx, sy + m(2.8), m(19.9)), (sx, sy + m(3.2), m(21.0)),
            (sx, sy + m(3.6), m(22.0)), (sx, sy + m(4.8), m(22.3)), (sx, yb - m(0.5), m(22.3))]
    b.sweep("porcelain", common.smooth_path(trap, samples=3), pr, up=(1, 0, 0))
    for c, ax in (((sx, sy, m(23.2)), "Z"), ((sx, sy + m(3.4), m(21.7)), "Z"),
                  ((sx, sy + m(5.6), m(22.3)), "Y")):
        b.cylinder("porcelain", c, m(0.98), m(0.7), axis=ax, segments=10)
    b.cylinder("nickel", (sx, yb - t - m(0.08), m(22.3)), m(1.5), m(0.12), axis="Y", segments=12)
    # Pop-up drain: flange and the stopper cap (the grime ring round it is texture).
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
    b.bm.faces.index_update()
    shell_idx = [f.index for f in shell]
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
    # The basin's underside shell faces away from that point (down and out).
    bm.faces.ensure_lookup_table()
    flip += [bm.faces[i] for i in shell_idx
             if bm.faces[i].normal.dot(eye - bm.faces[i].calc_center_median()) > 0]
    _bm.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def marker(coll, name, loc):
    import bpy
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.03
    ob.location = loc
    coll.objects.link(ob)
    return ob


DOOR = "vanity_door_sink"
DRAWERS = ("vanity_drawer_top", "vanity_drawer_bottom")


def build_door(coll):
    """The sink door, hinged on its south (outer) edge: origin on the hinge axis at the
    front outer corner of the leaf, so the leaf swings out clear of the face frame and
    the south wall. Arched bow pull near the free (north) edge, upper half."""
    L = layout()
    b = common.Builder(REGIONS)
    g = m(GAP)
    x0, x1 = L["fx0"], L["mid"] - g / 2
    dz0, dz1, yf, yface = L["dz0"], L["dz1"], L["yf"], L["yface"]
    front_slab(b, x0, x1, dz0, dz1, yf, frame=2.3)
    # Bow pull (005839): round rod bowing out from two feet, on small round bases.
    px = x1 - m(2.4)
    pz0, pz1 = dz1 - m(9.5), dz1 - m(3.0)
    bow = [(px, yface - m(1.15) * math.sin(math.pi * (0.08 + 0.84 * i / 8)) + m(0.05),
            pz0 + (pz1 - pz0) * i / 8) for i in range(9)]
    b.sweep("nickel", bow, common.circle_profile(m(0.2), 6), up=(0, -1, 0))
    for pz in (pz0, pz1):
        S.frustum(b, "nickel", (px, yface - m(0.12), pz), m(0.32), m(0.24), m(0.24), "Y", 8,
                  sign=-1)
    # Hinge leaves on the back of the door (photo 17), clear of the stile.
    for hz in (dz0 + m(3.2), dz1 - m(3.2)):
        b.box("nickel", (L["ox0"] + m(0.15), yf, hz - m(1.1)), (L["ox0"] + m(1.2), yf + m(0.06), hz + m(1.1)))
    pin = (x0, yface, dz0)
    ob = b.to_object(DOOR, coll, origin=pin)
    out = marker(coll, DOOR + "_out", ((x0 + x1) / 2, yface - m(1.0), (dz0 + dz1) / 2))
    return [ob, out]


def build_drawer(coll, name, z0, z1):
    """A drawer: oak front with its mushroom knob, and a white open-top box behind it
    (photo 18). Origin on the box's bottom at its centre; `_grab` at the knob."""
    L = layout()
    b = common.Builder(REGIONS)
    g = m(GAP)
    yf, yface, kx = L["yf"], L["yface"], L["kx"]
    front_slab(b, L["mid"] + g / 2, L["fx1"], z0, z1, yf)
    # The front's back face is white like the box (photo 18).
    b.bm.normal_update()
    for f in b.bm.faces:
        if f.normal.y > 0.9 and f.material_index == b.idx("oak"):
            f.material_index = b.idx("porcelain")
    kz = (z0 + z1) / 2 if z0 < L["dzm"] else (z0 + z1) / 2 + m(0.8)
    S.frustum(b, "nickel", (kx, yface - m(0.45), kz), m(0.3), m(0.2), m(0.9), "Y", 8, sign=-1)
    b.cylinder("nickel", (kx, yface - m(1.15), kz), m(0.6), m(0.45), axis="Y", segments=14,
               bevel=m(0.12))
    # Box: inside the opening with slide clearance.
    oz0 = L["oz0"] if z0 < L["dzm"] else L["dzm"] + m(MID_RAIL / 2)
    oz1 = L["dzm"] - m(MID_RAIL / 2) if z0 < L["dzm"] else L["oz1"]
    bx0, bx1 = L["ox2"] + m(DRAWER_CLR), L["ox3"] - m(DRAWER_CLR)
    bz0 = oz0 + m(0.4)
    bz1 = min(bz0 + m(DRAWER_H), oz1 - m(0.5))
    by0, by1 = yf, yf + m(DRAWER_D)
    s_, bt = m(DRAWER_SIDE), m(DRAWER_BOT)
    w = "porcelain"
    b.box(w, (bx0, by0, bz0), (bx1, by0 + s_, bz1))                 # front wall
    b.box(w, (bx0, by1 - s_, bz0), (bx1, by1, bz1))                 # back
    b.box(w, (bx0, by0 + s_, bz0), (bx0 + s_, by1 - s_, bz1))       # sides
    b.box(w, (bx1 - s_, by0 + s_, bz0), (bx1, by1 - s_, bz1))
    b.box(w, (bx0 + s_, by0 + s_, bz0), (bx1 - s_, by1 - s_, bz0 + bt))   # bottom
    org = ((bx0 + bx1) / 2, (by0 + by1) / 2, bz0)
    ob = b.to_object(name, coll, origin=org)
    grab = marker(coll, name + "_grab", (kx, yface - m(1.15), kz))
    return [ob, grab]


def drawer_interior(which):
    """(x0, x1, y0, y1, floor z) of a drawer's inside, metres, vanity-local, closed."""
    L = layout()
    top = which == "top"
    oz0 = L["dzm"] + m(MID_RAIL / 2) if top else L["oz0"]
    s_ = m(DRAWER_SIDE)
    bx0, bx1 = L["ox2"] + m(DRAWER_CLR), L["ox3"] - m(DRAWER_CLR)
    return (bx0 + s_, bx1 - s_, L["yf"] + s_, L["yf"] + m(DRAWER_D) - s_,
            oz0 + m(0.4) + m(DRAWER_BOT))


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
    L = layout()
    g = m(GAP)
    objs = [build_vanity(coll), build_mirror(coll)]
    objs += build_door(coll)
    objs += build_drawer(coll, DRAWERS[0], L["dzm"] + g / 2, L["dz1"])
    objs += build_drawer(coll, DRAWERS[1], L["dz0"], L["dzm"] - g / 2)
    for ob in objs:
        ob["origin0"] = tuple(ob.location)
    if os.environ.get("VANITY_OPEN"):            # render-only check: door open, top drawer out
        for ob in objs:
            if ob.name == DOOR:
                ob.rotation_euler.z = -math.radians(100)
            elif ob.name == DRAWERS[0]:
                ob.location.y -= m(DRAWER_D) * 0.75
            elif ob.name == DRAWERS[1]:
                ob.location.y -= m(DRAWER_D) * 0.35
    return objs


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    planar = {
        "oak_doors": ("-Y", (-m(TOP_W / 2), m(TOP_W / 2)), (0, m(TOP_Z0))),
        "oak": ("+X", (-m(WALL_Y), m(WALL_Y)), (0, m(TOP_Z0))),
        "sink_bowl": ("+Z", (m(SINK_X - SINK_W / 2), m(SINK_X + SINK_W / 2)),
                      (m(SINK_Y - SINK_D / 2), m(SINK_Y + SINK_D / 2))),
    }
    for ob in objs:
        if ob.type != "MESH":
            continue
        o = ob.get("origin0", (0.0, 0.0, 0.0))       # planar bounds are in object space
        pl = {}
        for r, (ax, (u0, u1), (v0, v1)) in planar.items():
            ua, va = common._axes(ax)
            du = sum(a * c for a, c in zip(ua, o))
            dv = sum(a * c for a, c in zip(va, o))
            pl[r] = (ax, (u0 - du, u1 - du), (v0 - dv, v1 - dv))
        common.atlas_uvs(ob, ATLAS, planar=pl)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
