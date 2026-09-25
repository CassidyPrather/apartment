"""Bathroom one-piece acrylic tub/shower unit on the east wall: tub with a plain apron,
moulded unit walls on three sides up to 77 in, spout/valve/overflow/shower head on the
north (faucet) end, a curved shower rod with a plain neutral curtain, plus the 33 in stub
wall at the tub's foot.

Source of truth: scripted, from the bathroom LiDAR survey (Reference/bathroom_survey/,
fixtures.py and the chk_tub_* check images). SCAN = measured from the registered capture
(about +-1 in); EST = guessed from the photos or standard fixture sizes.

Local frame: tub long axis along X, apron (front) faces -Y, back against the east wall
at +Y. Origin on the floor at the centre of the tub's 57.9 x 30 footprint. The faucet end
is -X (FAUCET_END = -1): placed at rotation 270 the front faces west, local -X points
north (the faucet wall) and local +X south (the stub wall).
  plan x = 267.75 + local y,  plan y = 257.05 - local x   (inches, model plan coords)

Objects:
  bathtub          tub, unit walls, spout, valve, shower head, drain, rod, curtain (static)
  bath_stub_wall   the stub wall at the tub's foot, full height, wall paint
"""

import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import common  # noqa: E402
import bathroom_shared as S  # noqa: E402

importlib.reload(S)
m = S.m

NAME = "bathtub"
ATLAS = S.ATLAS
MATERIALS = S.MATERIALS
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 1.0), ("in_tub", 0, 35, 0.7), ("from_west_low", 20, 8, 0.8)]

FAUCET_END = -1

# --- dimensions (inches) ---------------------------------------------------------
TUB_L = 57.9          # SCAN finished faces: stub face (plan y 228.1) to north wall (286.0)
TUB_W = 30.0          # SCAN east wall (282.75) to apron face (252.75)
TUB_H = 17.4          # SCAN rim height
RIM_FRONT = 3.0       # EST apron rim width
BASIN_DEPTH = 14.0    # EST water-side depth
UNIT_TOP = 77.0       # SCAN top of the unit walls
UNIT_T = 1.25         # EST moulded wall thickness (incl. the flange off the studs)
UNIT_FILLET = 2.0     # EST inside-corner radius of the moulded walls
STUB_T = 5.55         # SCAN (plan y 222.55..228.1)
STUB_WEST = 3.2       # SCAN the stub runs 3.2 in past the apron (to plan x 249.55)
CEILING = 108.0       # TAPE (shell_layout)
ROD_Z = 79.5          # SCAN
ROD_BOW = 4.55        # SCAN rod ends at the apron line (plan x 252.75), bows to 248.2
ROD_R = 0.5           # EST (1 in rod)
CURTAIN_BOTTOM = 10.0  # EST hem well below the rim (it hangs outside the tub)
CURTAIN_U = (0.45, 1.0)  # EST drawn back toward the stub (foot) end, fraction along rod
SPOUT_Z = 24.0        # SCAN
OVERFLOW_Z = 15.0     # SCAN
VALVE_Z = 34.0        # EST
HEAD_Z = 80.0         # SCAN (arm comes through the wall above the unit)
HW_Y = 0.25           # SCAN hardware centreline (plan x 268)

REGIONS = ["acrylic", "chrome", "dark", "curtain"]


def _x(v):
    """Local X for a faucet-end-relative coordinate (+ = toward the faucet end)."""
    return v * FAUCET_END


def rod_point(u):
    """Point on the curved rod for u in 0..1 (0 = faucet end, 1 = foot end)."""
    L = m(TUB_L)
    c, s = L / 2, m(ROD_BOW)
    R = (c * c + s * s) / (2 * s)
    a = math.asin(c / R)
    t = -a + 2 * a * u
    x = R * math.sin(t)
    y = -m(TUB_W / 2) - (R * math.cos(t) - (R - s))
    return (_x(-x) if FAUCET_END > 0 else x, y, m(ROD_Z))


def build_tub(coll):
    b = common.Builder(REGIONS)
    L, W, H = m(TUB_L), m(TUB_W), m(TUB_H)
    t = m(UNIT_T)
    outer = S.rrect(0, 0, L, W, m(0.6), seg=7)
    # Basin opening inside the unit walls, rim on the apron side.
    x0, x1 = -L / 2 + t, L / 2 - t
    y0, y1 = -W / 2 + m(RIM_FRONT), W / 2 - t
    top_c = ((x0 + x1) / 2, (y0 + y1) / 2)
    top = S.match_polar(outer, 0, 0, S.rrect_at(top_c[0], top_c[1], x1 - x0, y1 - y0, m(3)))
    bw, bh = (x1 - x0) - m(9.0), (y1 - y0) - m(6.0)
    bc = (top_c[0] + _x(m(1.5)), top_c[1])
    bot = S.match_polar(outer, 0, 0, S.rrect_at(bc[0], bc[1], bw, bh, m(5)))
    zf = H - m(BASIN_DEPTH)
    r_ob = S.ring(b, outer, 0.0)
    r_ot = S.ring(b, outer, H)
    r_it = S.ring(b, top, H)
    r_ib = S.ring(b, bot, zf)
    S.bridge(b, "acrylic", r_ob, r_ot)
    S.bridge(b, "acrylic", r_ot, r_it)
    S.bridge(b, "acrylic", r_it, r_ib)
    S.cap(b, "acrylic", r_ib)
    S.cap(b, "acrylic", r_ob)

    # One-piece unit walls: back and both ends from the rim to UNIT_TOP, the ends
    # running out to the apron face, a rolled lip along the top.
    zs0, zs1 = H - m(0.2), m(UNIT_TOP)
    b.box("acrylic", (-L / 2, W / 2 - t, zs0), (L / 2, W / 2, zs1), bevel=m(0.2))
    b.box("acrylic", (-L / 2, -W / 2, zs0), (-L / 2 + t, W / 2 - t, zs1), bevel=m(0.2))
    b.box("acrylic", (L / 2 - t, -W / 2, zs0), (L / 2, W / 2 - t, zs1), bevel=m(0.2))
    # Rounded inside corners (concave quarter-round fillets) where the ends meet the back.
    for sx in (-1, 1):
        b.prism("acrylic", fillet_outline(sx, L / 2 - t, W / 2 - t, m(UNIT_FILLET)), zs0, zs1)
    # Moulded soap shelf on the back wall toward the faucet end.
    b.box("acrylic", (_x(m(8)) if FAUCET_END > 0 else -L / 2 + t, W / 2 - t - m(3.5), m(44)),
          (L / 2 - t if FAUCET_END > 0 else _x(m(8)), W / 2 - t, m(45)), bevel=m(0.3))

    # Faucet-end trim (on the end wall's inner face).
    wall = _x(L / 2 - t)
    inward = -FAUCET_END
    hy = m(HW_Y)
    sx0, sx1 = sorted((wall, wall + inward * m(5.5)))
    b.box("chrome", (sx0, hy - m(1.1), m(SPOUT_Z) - m(0.9)), (sx1, hy + m(1.1), m(SPOUT_Z) + m(0.9)),
          bevel=m(0.35))
    b.cylinder("chrome", (wall + inward * m(5.0), hy, m(SPOUT_Z) - m(1.2)), m(0.7), m(0.8),
               axis="Z", segments=12)
    b.cylinder("chrome", (wall + inward * m(0.25), hy, m(VALVE_Z)), m(3.5), m(0.5), axis="X",
               segments=20)
    b.cylinder("chrome", (wall + inward * m(1.2), hy, m(VALVE_Z)), m(1.0), m(1.6), axis="X",
               segments=12)
    lx = wall + inward * m(1.9)
    b.box("chrome", (min(lx, lx + inward * m(0.6)), hy - m(0.35), m(VALVE_Z) - m(0.4)),
          (max(lx, lx + inward * m(0.6)), hy + m(0.45), m(VALVE_Z) + m(4.0)), bevel=m(0.2))
    # Shower arm from the room wall above the unit, and the head.
    rw = _x(L / 2)
    ax0, ax1 = sorted((rw, rw + inward * m(6.5)))
    b.box("chrome", (ax0, hy - m(0.4), m(HEAD_Z) + m(1.2)), (ax1, hy + m(0.4), m(HEAD_Z) + m(2.0)),
          bevel=m(0.15))
    b.cylinder("chrome", (rw + inward * m(0.2), hy, m(HEAD_Z) + m(1.6)), m(1.3), m(0.4), axis="X",
               segments=12)
    b.cylinder("chrome", (rw + inward * m(7.0), hy, m(HEAD_Z)), m(2.2), m(1.6),
               axis="X", segments=20)
    # Overflow plate on the basin end wall and the drain on the floor.
    b.cylinder("chrome", (_x(L / 2 - t - m(3.0)), bc[1], m(OVERFLOW_Z)), m(1.5), m(0.5),
               axis="X", segments=16)
    b.cylinder("dark", (bc[0] + _x(bw / 2 - m(3.5)), bc[1], zf + m(0.05)), m(1.5), m(0.12),
               axis="Z", segments=16, cap_region="chrome")

    # Curved shower rod between the north wall and the stub wall, bowed out west.
    n = 24
    pts = [rod_point(i / n) for i in range(n + 1)]
    b.sweep("chrome", pts, common.circle_profile(m(ROD_R), 10), up=(0, 0, 1))
    for u in (0.0, 1.0):
        x, y, z = rod_point(u)
        sx = 1 if x > 0 else -1
        b.cylinder("chrome", (sx * (L / 2 - m(0.3)), y, z), m(1.4), m(0.6), axis="X",
                   segments=16)
    # Plain neutral curtain on the rod, drawn back toward the foot end.
    ua, ub = CURTAIN_U
    k = 48
    cpts = []
    for i in range(k + 1):
        u = ua + (ub - ua) * i / k
        x, y, _ = rod_point(u)
        amp = m(1.0 + 1.2 * (i / k))
        y += amp * math.sin(2 * math.pi * i / 5.0)
        cpts.append((x, y))
    top_z, bot_z = ROD_Z - 1.0, CURTAIN_BOTTOM
    h = m(top_z - bot_z)
    zc = m((top_z + bot_z) / 2)
    prof = [(-m(0.08), -h / 2), (m(0.08), -h / 2), (m(0.08), h / 2), (-m(0.08), h / 2)]
    b.sweep("curtain", [(x, y, zc) for x, y in cpts], prof, up=(0, 0, 1))
    for i in range(0, k + 1, 4):
        x, _, _ = rod_point(ua + (ub - ua) * i / k)
        _, y, z = rod_point(ua + (ub - ua) * i / k)
        b.cylinder("chrome", (x, y, z - m(0.3)), m(0.8), m(0.25), axis="X", segments=8)
    return b.to_object("bathtub", coll)


def fillet_outline(sx, xw, yw, f, seg=6):
    """Concave quarter-round filling the inside corner (sx*xw, yw): the corner point and
    the arc about (sx*(xw-f), yw-f) from the end wall round to the back wall."""
    cx, cy = sx * (xw - f), yw - f
    return [(sx * xw, yw)] + [(cx + sx * f * math.cos(math.radians(90 * i / seg)),
                               cy + f * math.sin(math.radians(90 * i / seg)))
                              for i in range(seg + 1)]


def build_stub(coll):
    b = common.Builder(["wall_paint"])
    L, W = m(TUB_L), m(TUB_W)
    xs = sorted((_x(-L / 2), _x(-L / 2 - m(STUB_T))))
    b.box("wall_paint", (xs[0], -W / 2 - m(STUB_WEST), 0), (xs[1], W / 2, m(CEILING)))
    return b.to_object("bath_stub_wall", coll)


def build(coll):
    return [build_tub(coll), build_stub(coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
