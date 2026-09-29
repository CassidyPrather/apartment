"""Bathroom one-piece acrylic tub/shower unit on the east wall: tub with a plain apron,
moulded unit walls on three sides up to 77 in, a flat ledge along the back wall at rim
height, polished-chrome spout/valve/overflow/drain/shower head on the north (faucet) end,
a curved satin-nickel shower rod with red rings and the pink-and-white floral curtain
gathered at the faucet end, the frosted clear liner hanging inside it into the tub, plus
the 33 in stub wall at the tub's foot.

Source of truth: scripted, from the bathroom LiDAR survey (Reference/bathroom_survey/,
fixtures.py and the chk_tub_* check images) and the capture's frames (curtain 010059,
valve 010259, spout 010303, overflow 010307, rod and rings 010247). SCAN = measured from
the registered capture (about +-1 in); EST = guessed from the photos or standard sizes.

Local frame: tub long axis along X, apron (front) faces -Y, back against the east wall
at +Y. Origin on the floor at the centre of the tub's 57.9 x 30 footprint. The faucet end
is -X (FAUCET_END = -1): placed at rotation 270 the front faces west, local -X points
north (the faucet wall) and local +X south (the stub wall).
  plan x = 267.75 + local y,  plan y = 257.05 - local x   (inches, model plan coords)

Wear (texture only): the basin is mapped from above onto its own atlas region (yellowed
floor edge and corners, rust flecks round the drain) and the unit walls are unrolled
onto another (grime along the rim joint, mildew in the corners, rust under the trim).

Objects:
  bathtub          tub, unit walls, trim, shower head, rod, rings, curtain (static)
  bath_stub_wall   the stub wall at the tub's foot, full height, wall paint
"""

import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from mathutils import Vector  # noqa: E402

import common  # noqa: E402
import bathroom_shared as S  # noqa: E402

importlib.reload(S)
m = S.m

NAME = "bathtub"
ATLAS = S.ATLAS
MATERIALS = dict(S.MATERIALS)
MATERIALS["bathroom_clear"] = {"atlas": "bathroom", "mode": "transparent", "alpha": 0.3}   # the liner
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 1.0), ("in_tub", 0, 35, 0.7), ("from_west_low", 20, 8, 0.8),
         ("faucet_end", 300, 25, 0.45), ("curtain", 0, 5, 0.75)]

FAUCET_END = S.TUB_FAUCET_END

# --- dimensions (inches) ---------------------------------------------------------
TUB_L = S.TUB_L       # SCAN finished faces: stub face (plan y 228.1) to north wall (286.0)
TUB_W = S.TUB_W       # SCAN east wall (282.75) to apron face (252.75)
TUB_H = S.TUB_H       # SCAN rim height
RIM_FRONT = S.TUB_RIM_FRONT      # EST apron rim width
BASIN_DEPTH = S.TUB_BASIN_DEPTH  # EST water-side depth
UNIT_TOP = 77.0       # SCAN top of the unit walls
UNIT_T = S.TUB_UNIT_T  # EST moulded wall thickness (incl. the flange off the studs)
UNIT_FILLET = 2.0     # EST inside-corner radius of the moulded walls
STUB_T = 5.55         # SCAN (plan y 222.55..228.1)
STUB_WEST = 3.2       # SCAN the stub runs 3.2 in past the apron (to plan x 249.55)
CEILING = 108.0       # TAPE (shell_layout)
ROD_Z = 79.5          # SCAN
ROD_BOW = 4.55        # SCAN rod ends at the apron line (plan x 252.75), bows to 248.2
ROD_R = 0.5           # EST (1 in rod)
CURTAIN_BOTTOM = 4.0  # EST hem a few inches off the floor (frames 010059, 010117)
CURTAIN_U = (0.0, 0.5)   # EST gathered at the north (faucet) end, foot end open
                         # (frames 010025-010120, chk_tub_0), fraction along rod
CURTAIN_TILE_IN = 20.0   # EST fabric width one texture tile shows (the photo crop's span)
SPOUT_Z = 24.0        # SCAN
OVERFLOW_Z = 15.0     # SCAN
VALVE_Z = 34.0        # EST
HEAD_Z = 78.5         # EST head just below the unit top, arm through the wall above it
                      # (photo 010155; the survey box read 80, which sat too high)
HEAD_R = 1.8          # EST 3.6 in polished chrome face (photo 010155)
HW_Y = 0.25           # SCAN hardware centreline (plan x 268)
ESCUTCHEON_R = 3.5    # EST 7 in round trim plate (photo 010259)
SPOUT_LEN = 5.8       # EST (photo 010303)

REGIONS = ["acrylic", "basin", "unit_wall", "chrome", "nickel", "dark", "curtain", "ring_red", "liner"]

_CURTAIN = {}         # filled by build_tub(): path points and tiling, read by texture()


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


frustum = S.frustum


def tube_x(b, region, rings, n=10):
    """Closed loft along X: rings = [(x, y, z, half_width_y, half_height_z), ...]."""
    loops = []
    for x, y, z, hw, hh in rings:
        loops.append([b.bm.verts.new((x, y + hw * math.cos(2 * math.pi * i / n),
                                      z + hh * math.sin(2 * math.pi * i / n))) for i in range(n)])
    faces = []
    for r0, r1 in zip(loops, loops[1:]):
        faces += S.bridge(b, region, r0, r1)
    faces += S.cap(b, region, loops[0]) + S.cap(b, region, loops[-1])
    return faces


def build_tub(coll):
    b = common.Builder(REGIONS)
    L, W, H = m(TUB_L), m(TUB_W), m(TUB_H)
    t = m(UNIT_T)
    outer = S.rrect(0, 0, L, W, m(0.6), seg=7)
    # Basin opening inside the unit walls, rim on the apron side (shared with the texture).
    (x0, x1, y0, y1), (bcx, bcy, bw, bh, br) = S.tub_basin()
    x0, x1, y0, y1 = m(x0), m(x1), m(y0), m(y1)
    top_c = ((x0 + x1) / 2, (y0 + y1) / 2)
    top = S.match_polar(outer, 0, 0, S.rrect_at(top_c[0], top_c[1], x1 - x0, y1 - y0, m(3)))
    bw, bh = m(bw), m(bh)
    bc = (m(bcx), m(bcy))
    bot = S.match_polar(outer, 0, 0, S.rrect_at(bc[0], bc[1], bw, bh, m(br)))
    zf = H - m(BASIN_DEPTH)
    r_ob = S.ring(b, outer, 0.0)
    r_ot = S.ring(b, outer, H)
    r_it = S.ring(b, top, H)
    r_ib = S.ring(b, bot, zf)
    S.bridge(b, "acrylic", r_ob, r_ot)
    S.bridge(b, "acrylic", r_ot, r_it)
    S.bridge(b, "basin", r_it, r_ib)
    S.cap(b, "basin", r_ib)
    S.cap(b, "acrylic", r_ob)

    # One-piece unit walls: back and both ends from the rim to UNIT_TOP, the ends
    # running out to the apron face, a rolled lip along the top.
    zs0, zs1 = H - m(0.2), m(UNIT_TOP)
    b.box("unit_wall", (-L / 2, W / 2 - t, zs0), (L / 2, W / 2, zs1), bevel=m(0.2))
    b.box("unit_wall", (-L / 2, -W / 2, zs0), (-L / 2 + t, W / 2 - t, zs1), bevel=m(0.2))
    b.box("unit_wall", (L / 2 - t, -W / 2, zs0), (L / 2, W / 2 - t, zs1), bevel=m(0.2))
    # Rounded inside corners (concave quarter-round fillets) where the ends meet the back.
    for sx in (-1, 1):
        b.prism("unit_wall", fillet_outline(sx, L / 2 - t, W / 2 - t, m(UNIT_FILLET)), zs0, zs1)
    # Moulded soap shelf on the back wall toward the faucet end.
    b.box("acrylic", (_x(m(8)) if FAUCET_END > 0 else -L / 2 + t, W / 2 - t - m(3.5), m(44)),
          (L / 2 - t if FAUCET_END > 0 else _x(m(8)), W / 2 - t, m(45)), bevel=m(0.3))

    # Faucet-end trim, polished chrome (photos 010259, 010303, 010307, 010155); the rod
    # is the satin one.
    wall = _x(L / 2 - t)
    inward = -FAUCET_END
    hy = m(HW_Y)
    # Slip-on spout: an oval tube tapering from the wall, nose turned down, dark outlet.
    zs = m(SPOUT_Z)
    tube_x(b, "chrome", [(wall + inward * m(d * SPOUT_LEN), hy, zs + m(dz), m(hw), m(hh))
                         for d, dz, hw, hh in ((-0.01, 0.0, 1.15, 1.05), (0.1, 0.0, 1.1, 1.0),
                                               (0.43, -0.1, 0.95, 0.8), (0.74, -0.3, 0.85, 0.65),
                                               (0.93, -0.55, 0.8, 0.55), (1.0, -0.75, 0.6, 0.4))])
    b.cylinder("dark", (wall + inward * m(0.88 * SPOUT_LEN), hy, zs - m(1.05)), m(0.45), m(0.2),
               axis="Z", segments=8)
    # Valve: domed round escutcheon, hub and a lever hanging down and out.
    zv = m(VALVE_Z)
    frustum(b, "chrome", (wall + inward * m(0.22), hy, zv), m(ESCUTCHEON_R), m(2.9), m(0.44),
            "X", 24, sign=inward)
    frustum(b, "chrome", (wall + inward * m(0.95), hy, zv), m(1.25), m(0.95), m(1.1), "X", 12,
            sign=inward)
    lever = [(wall + inward * m(1.3), hy, zv), (wall + inward * m(1.9), hy, zv - m(1.0)),
             (wall + inward * m(2.3), hy, zv - m(2.6)), (wall + inward * m(2.5), hy, zv - m(4.0))]
    b.sweep("chrome", lever, [(-m(0.45), -m(0.17)), (m(0.45), -m(0.17)), (m(0.4), m(0.17)),
                              (-m(0.4), m(0.17))], up=(1, 0, 0))
    # Shower arm from the room wall above the unit, and the head (polished chrome).
    rw = _x(L / 2)
    za = m(HEAD_Z) + m(2.2)
    ax0, ax1 = sorted((rw, rw + inward * m(4.2)))
    b.box("chrome", (ax0, hy - m(0.35), za - m(0.35)), (ax1, hy + m(0.35), za + m(0.35)),
          bevel=m(0.12))
    frustum(b, "chrome", (rw + inward * m(0.3), hy, za), m(1.2), m(0.6), m(0.6), "X", 12,
            sign=inward)
    b.cylinder("chrome", (rw + inward * m(4.4), hy, za - m(0.5)), m(0.6), m(1.4), axis="Z",
               segments=10)
    frustum(b, "chrome", (rw + inward * m(4.6), hy, m(HEAD_Z)), m(0.6), m(HEAD_R), m(2.0), "X",
            20, sign=inward)
    # Overflow plate flat on the sloped basin end wall (centre screw), and the toe-touch
    # drain stopper on the floor.
    zo = m(OVERFLOW_Z)
    slope = ((bc[0] - bw / 2) - x0) if FAUCET_END < 0 else (x1 - (bc[0] + bw / 2))
    xo = wall + inward * (slope * (H - zo) / (H - zf) + m(0.1))
    frustum(b, "chrome", (xo, bc[1], zo), m(1.65), m(1.45), m(0.3), "X", 16, sign=inward)
    b.cylinder("dark", (xo + inward * m(0.16), bc[1], zo), m(0.22), m(0.06), axis="X",
               segments=6)
    dx = bc[0] + _x(bw / 2 - m(3.5))
    frustum(b, "chrome", (dx, bc[1], zf + m(0.07)), m(1.5), m(1.3), m(0.14), "Z", 16)
    b.cylinder("chrome", (dx, bc[1], zf + m(0.35)), m(0.75), m(0.5), axis="Z", segments=12,
               bevel=m(0.12))

    # Curved shower rod between the north wall and the stub wall, bowed out west, on
    # bell flanges.
    n = 24
    pts = [rod_point(i / n) for i in range(n + 1)]
    b.sweep("nickel", pts, common.circle_profile(m(ROD_R), 10), up=(0, 0, 1))
    for u in (0.0, 1.0):
        x, y, z = rod_point(u)
        sx = 1 if x > 0 else -1
        frustum(b, "nickel", (sx * (L / 2 - m(0.45)), y, z), m(1.4), m(0.7), m(0.9), "X", 16,
                sign=-sx)
    # The curtain, gathered at the faucet end: split in two bands so the print's
    # tile repeats up and down as well as along (see texture()).
    ua, ub = CURTAIN_U
    k = 48
    cpts = []
    for i in range(k + 1):
        u = ua + (ub - ua) * i / k
        x, y, _ = rod_point(u)
        amp = m(1.0 + 1.2 * (1 - i / k))      # deepest folds in the gathered end
        y += amp * math.sin(2 * math.pi * i / 5.0)
        cpts.append((x, y))
    top_z, bot_z = ROD_Z - 1.0, CURTAIN_BOTTOM
    h = m(top_z - bot_z)
    zc = m((top_z + bot_z) / 2)
    th = m(0.08)
    prof = [(-th, -h / 2), (th, -h / 2), (th, 0.0), (th, h / 2), (-th, h / 2), (-th, 0.0)]
    b.sweep("curtain", [(x, y, zc) for x, y in cpts], prof, up=(0, 0, 1))
    cum = [0.0]
    for (xa, ya), (xb, yb) in zip(cpts, cpts[1:]):
        cum.append(cum[-1] + math.hypot(xb - xa, yb - ya))
    spt = min((4, 6, 8, 12, 16, 24, 48), key=lambda d: abs(cum[-1] * d / k - m(CURTAIN_TILE_IN)))
    _CURTAIN.clear()
    _CURTAIN.update(pts=cpts, cum=cum, spt=spt, z0=m(bot_z), z1=m(top_z))
    # The clear liner on the same rings, just inside the curtain, dropping over the apron
    # rim into the basin (frames 010059, 010117). Two-sided: Unity culls back faces.
    y_in = -m(TUB_W / 2) + m(RIM_FRONT) + m(0.6)
    rows = [(top_z - 0.5, 0.0), (TUB_H + 4.0, 0.0), (TUB_H - 7.0, 0.4)]   # (z, extra inward)
    grid = []
    for x, y in cpts:
        yl = y + m(0.5)
        col = []
        for k_, (z, extra) in enumerate(rows):
            yy = yl if k_ == 0 else max(yl, y_in) + m(extra)
            col.append((x, yy, m(z)))
        grid.append(col)
    for side in (1, -1):
        vs = [[b.bm.verts.new(c) for c in col] for col in grid]
        for i in range(len(vs) - 1):
            for k_ in range(len(rows) - 1):
                q = [vs[i][k_], vs[i + 1][k_], vs[i + 1][k_ + 1], vs[i][k_ + 1]]
                f = b.bm.faces.new(q if side > 0 else list(reversed(q)))
                f.material_index = b.idx("liner")
    # Red plastic rings looped over the rod, one every 4 path points.
    for i in range(0, k + 1, 4):
        u = ua + (ub - ua) * i / k
        x, y, z = rod_point(u)
        xa, ya, _ = rod_point(max(0.0, u - 0.01))
        xb, yb, _ = rod_point(min(1.0, u + 0.01))
        tang = Vector((xb - xa, yb - ya, 0)).normalized()
        side = tang.cross(Vector((0, 0, 1)))
        rr = m(0.8)
        c = Vector((x, y, z + m(ROD_R) - rr + m(0.1)))
        loop = [c + side * rr * math.sin(2 * math.pi * j / 8)
                + Vector((0, 0, rr)) * math.cos(2 * math.pi * j / 8) for j in range(8)]
        b.sweep("ring_red", loop, common.circle_profile(m(0.13), 3), up=tuple(tang), closed=True)
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


# --- UVs for the wear regions and the curtain print ----------------------------------

def unit_wall_s(co, normal):
    """Unrolled position (inches) along the unit walls: 0 at the faucet end's front edge,
    round the back wall, 2W+L at the foot end's front edge."""
    L, W, t = m(TUB_L), m(TUB_W), m(UNIT_T)
    x, y = co.x * FAUCET_END * -1, co.y      # x now + toward the foot end
    on_end = abs(normal.x) >= abs(normal.y) if abs(normal.z) < 0.7 else abs(x) > L / 2 - t - m(0.5)
    if on_end and x < 0:
        s = y + W / 2
    elif on_end:
        s = W + L + (W / 2 - y)
    else:
        s = W + (x + L / 2)
    return s / (2 * W + L)


def _set_region_uvs(ob, region, fn):
    """fn(co, poly) -> (fu, fv) in 0..1 for each loop of the region's faces."""
    me = ob.data
    uvl = me.uv_layers["UVMap"]
    slot = [s.name.split(".")[0] for s in me.materials].index(region)
    u0, v0, u1, v1 = common.uv_rect(ATLAS, region)
    for p in me.polygons:
        if p.material_index != slot:
            continue
        for li, fu_fv in zip(p.loop_indices, fn(p)):
            fu, fv = fu_fv
            uvl.data[li].uv = (u0 + max(0.0, min(1.0, fu)) * (u1 - u0),
                               v0 + max(0.0, min(1.0, fv)) * (v1 - v0))


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    clear = common.atlas_material("bathroom_clear", ATLAS)
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")   # preview only
    bsdf.inputs["Alpha"].default_value = MATERIALS["bathroom_clear"]["alpha"]
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    (x0, x1, y0, y1), _ = S.tub_basin()
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar={
            "basin": ("+Z", (m(x0), m(x1)), (m(y0), m(y1)))})
        if ob.name.startswith("bathtub"):
            me = ob.data
            H, top = m(TUB_H), m(UNIT_TOP)

            def wall_uv(p):
                c, nrm = p.center, p.normal
                # Faces toward the room walls (outside the unit) take a clean spot.
                if (nrm.y > 0.5 and c.y > m(TUB_W / 2) - m(0.3)) or \
                        (abs(nrm.x) > 0.5 and nrm.x * c.x > 0 and abs(c.x) > m(TUB_L / 2) - m(0.3)):
                    return [(0.5, 0.9)] * len(p.loop_indices)
                return [(unit_wall_s(me.vertices[me.loops[li].vertex_index].co, p.normal),
                         (me.vertices[me.loops[li].vertex_index].co.z - H) / (top - H))
                        for li in p.loop_indices]

            _set_region_uvs(ob, "unit_wall", wall_uv)
            pts, cum, spt = _CURTAIN["pts"], _CURTAIN["cum"], _CURTAIN["spt"]
            z0, z1 = _CURTAIN["z0"], _CURTAIN["z1"]
            zm = (z0 + z1) / 2

            def near(co):
                return min(range(len(pts)), key=lambda i: (pts[i][0] - co.x) ** 2
                           + (pts[i][1] - co.y) ** 2)

            def curtain_uv(p):
                cos = [me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
                idx = [near(c) for c in cos]
                seg = min(min(idx), len(pts) - 2)
                t0 = (seg // spt) * spt
                t1 = min(t0 + spt, len(pts) - 1)
                band_lo = p.center.z < zm - 1e-4
                za, zb = (z0, zm) if band_lo else (zm, z1)
                return [((cum[i] - cum[t0]) / (cum[t1] - cum[t0]), (c.z - za) / (zb - za))
                        for i, c in zip(idx, cos)]

            _set_region_uvs(ob, "curtain", curtain_uv)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: (clear if r == "liner" else mat) for r in regions})
