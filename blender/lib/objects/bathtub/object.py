"""Bathroom alcove tub/shower combo: tub, three-wall surround, spout/valve/shower head,
straight curtain rod with a bunched curtain, plus the stub wall at the tub's foot.

Source of truth: scripted. Coarse block-in from standard fixture sizes: there are no
photos or measurements of the real bathroom yet, so every size below is EST except the
stub wall's 33 in length (TAPE, from Cassidy's layout notes; its position is an open item).

Local frame: tub long axis along X, apron (front) faces -Y, back against the wall at
+Y. Origin on the floor at the centre of the tub's 60 x 30 footprint. The faucet end is
+X when FAUCET_END = +1 (the stub wall then stands past the -X end); set it to -1 to
mirror the plumbing and the stub for the other tub orientation (see the report).

Objects:
  bathtub          tub, surround, spout, valve, shower head, drain, rod, curtain (static)
  bath_stub_wall   the 33 in stub wall at the tub's foot, full height, wall paint
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
VIEWS = [("plan_top", 0, 89.9, 1.0), ("in_tub", 0, 35, 0.7)]

FAUCET_END = -1

# --- dimensions (inches) ---------------------------------------------------------
TUB_L = 60.0          # EST standard alcove tub length (wall to wall)
TUB_W = 30.0          # EST standard width
TUB_H = 15.0          # EST rim height (typ. 14-15.5)
RIM_FRONT = 3.5       # EST apron rim width
RIM_BACK = 3.0        # EST
RIM_ENDS = 3.0        # EST
BASIN_DEPTH = 12.5    # EST water-side depth (floor at 2.5 above the tub bottom)
SURROUND_H = 72.0     # EST top of the surround panels above the floor
SURROUND_T = 0.375    # EST acrylic panel + adhesive
STUB_LEN = 33.0       # TAPE (layout notes: "33 in long"); position is an open item
STUB_T = 4.75         # TAPE-derived: interior wall thickness (shell_layout)
CEILING = 108.0       # TAPE (shell_layout)
ROD_Z = 76.0          # EST rod height
ROD_Y = -12.5         # EST rod set just inside the apron
ROD_R = 0.5           # EST (1 in rod)
CURTAIN_BOTTOM = 16.0  # EST hem just above the rim
CURTAIN_X = (6.0, 29.4)  # EST the curtain is drawn back toward the faucet end
SPOUT_Z = 20.0        # EST
VALVE_Z = 30.0        # EST
HEAD_Z = 78.0         # EST shower arm height

REGIONS = ["acrylic", "chrome", "dark", "curtain"]


def _x(v):
    """Local X for a faucet-end-relative coordinate (+ = toward the faucet end)."""
    return v * FAUCET_END


def build_tub(coll):
    b = common.Builder(REGIONS)
    L, W, H = m(TUB_L), m(TUB_W), m(TUB_H)
    outer = S.rrect(0, 0, L, W, m(0.6), seg=7)
    # Inner basin: rim widths per side, drain (faucet) end slightly deeper and flatter.
    x0, x1 = -L / 2 + m(RIM_ENDS + 0.5), L / 2 - m(RIM_ENDS)
    if FAUCET_END < 0:
        x0, x1 = -x1, -x0
    y0, y1 = -W / 2 + m(RIM_FRONT), W / 2 - m(RIM_BACK)
    top_c = ((x0 + x1) / 2, (y0 + y1) / 2)
    top = S.match_polar(outer, 0, 0, S.rrect_at(top_c[0], top_c[1], x1 - x0, y1 - y0, m(4)))
    bw, bh = (x1 - x0) - m(6.5), (y1 - y0) - m(5.5)
    bc = (top_c[0] + _x(m(1.0)), top_c[1])
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

    # Surround: back panel and two end panels on the wall faces, rim to SURROUND_H.
    t = m(SURROUND_T)
    zs0, zs1 = H - m(0.2), m(SURROUND_H)
    b.box("acrylic", (-L / 2, W / 2 - t, zs0), (L / 2, W / 2, zs1), bevel=m(0.12))
    b.box("acrylic", (-L / 2, -W / 2, zs0), (-L / 2 + t, W / 2 - t, zs1), bevel=m(0.12))
    b.box("acrylic", (L / 2 - t, -W / 2, zs0), (L / 2, W / 2 - t, zs1), bevel=m(0.12))
    # Moulded soap ledge across the back panel.
    b.box("acrylic", (-L / 2 + t, W / 2 - t - m(3), m(44)), (L / 2 - t, W / 2 - t, m(45)),
          bevel=m(0.3))

    # Faucet-end trim (on the end panel's face).
    wall = _x(L / 2 - t)
    inward = -FAUCET_END
    # Tub spout: a short wedge out of the wall plus its nose.
    sx0, sx1 = sorted((wall, wall + inward * m(5.5)))
    b.box("chrome", (sx0, -m(1.1), m(SPOUT_Z) - m(0.9)), (sx1, m(1.1), m(SPOUT_Z) + m(0.9)),
          bevel=m(0.35))
    b.cylinder("chrome", (wall + inward * m(5.0), 0, m(SPOUT_Z) - m(1.2)), m(0.7), m(0.8),
               axis="Z", segments=12)
    # Valve: escutcheon plate and lever.
    b.cylinder("chrome", (wall + inward * m(0.25), 0, m(VALVE_Z)), m(3.5), m(0.5), axis="X",
               segments=20)
    b.cylinder("chrome", (wall + inward * m(1.2), 0, m(VALVE_Z)), m(1.0), m(1.6), axis="X",
               segments=12)
    lx = wall + inward * m(1.9)
    b.box("chrome", (min(lx, lx + inward * m(0.6)), -m(0.35), m(VALVE_Z) - m(0.4)),
          (max(lx, lx + inward * m(0.6)), m(0.35) + m(0.1), m(VALVE_Z) + m(4.0)), bevel=m(0.2))
    # Shower arm and head.
    ax0, ax1 = sorted((wall, wall + inward * m(6.5)))
    b.box("chrome", (ax0, -m(0.4), m(HEAD_Z) - m(0.4)), (ax1, m(0.4), m(HEAD_Z) + m(0.4)),
          bevel=m(0.15))
    b.cylinder("chrome", (wall + inward * m(0.2), 0, m(HEAD_Z)), m(1.3), m(0.4), axis="X",
               segments=12)
    b.cylinder("chrome", (wall + inward * m(7.2), 0, m(HEAD_Z) - m(0.6)), m(2.3), m(1.4),
               axis="X", segments=20, cap_region="chrome")
    # Overflow plate on the basin end wall and the drain on the floor.
    b.cylinder("chrome", (_x(x1 if FAUCET_END > 0 else -x0) + inward * m(0.9), 0, m(10.5)),
               m(1.5), m(0.5), axis="X", segments=16)
    b.cylinder("dark", (bc[0] + _x(bw / 2 - m(3.5)), bc[1], zf + m(0.05)), m(1.5), m(0.12),
               axis="Z", segments=16, cap_region="chrome")

    # Curtain rod with flanges, spanning wall to wall.
    b.cylinder("chrome", (0, m(ROD_Y), m(ROD_Z)), m(ROD_R), L - 2 * t, axis="X", segments=12)
    for sx in (-1, 1):
        b.cylinder("chrome", (sx * (L / 2 - t - m(0.3)), m(ROD_Y), m(ROD_Z)), m(1.3), m(0.6),
                   axis="X", segments=16)
    # Curtain: a thin wavy sheet hanging from the rod, bunched toward the faucet end.
    ca, cb = CURTAIN_X
    n = 40
    pts = []
    for i in range(n + 1):
        u = i / n
        x = ca + (cb - ca) * u
        amp = 1.2 + 1.0 * u                      # deeper folds where it's bunched
        y = ROD_Y + amp * math.sin(2 * math.pi * (x - ca) / 4.2)
        pts.append((_x(m(x)), m(y), 0.0))
    top_z, bot_z = ROD_Z - 0.8, CURTAIN_BOTTOM
    h = m(top_z - bot_z)
    zc = m((top_z + bot_z) / 2)
    prof = [(-m(0.08), -h / 2), (m(0.08), -h / 2), (m(0.08), h / 2), (-m(0.08), h / 2)]
    b.sweep("curtain", [(p[0], p[1], zc) for p in pts], prof, up=(0, 0, 1))
    # Hook rings where the curtain meets the rod.
    for i in range(0, n + 1, 5):
        x, y, _ = pts[i]
        b.cylinder("chrome", (x, m(ROD_Y), m(ROD_Z) - m(0.2)), m(0.8), m(0.25), axis="X",
                   segments=8)
    return b.to_object("bathtub", coll)


def build_stub(coll):
    b = common.Builder(["wall_paint"])
    L, W = m(TUB_L), m(TUB_W)
    xs = sorted((_x(-L / 2), _x(-L / 2 - m(STUB_T))))
    b.box("wall_paint", (xs[0], W / 2 - m(STUB_LEN), 0), (xs[1], W / 2, m(CEILING)))
    return b.to_object("bath_stub_wall", coll)


def build(coll):
    return [build_tub(coll), build_stub(coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    ca, cb = sorted((_x(m(CURTAIN_X[0])), _x(m(CURTAIN_X[1]))))
    planar = {"curtain": ("-Y", (ca, cb), (m(CURTAIN_BOTTOM), m(ROD_Z - 0.8)))}
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=planar)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
