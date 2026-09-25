"""Bedroom cables: the wiring in the corner between the desk's pedestal and the filing
cabinet, on the bedroom face of the center wall (x 138.75), from Cassidy's photo
Reference/IMG_1516.jpg (looking down into that corner).

  - two wall plates: a white single-gang cable (coax) plate with an F-connector and a
    duplex power outlet with one black plug in its lower receptacle
  - a black six-outlet power strip on the carpet (blue power LED, red switch) with two
    wall-wart adapters and three plugs in it; its own cord goes to the wall outlet
  - an in-line black adapter on the carpet (the light stand's supply) and a loose square
    black charger brick
  - cables, swept with slack loops on the carpet:
      router power, modem power       stub ends on the cabinet side -> strip (adapters)
      coax                            stub end -> the cable plate
      white ethernet                  router LAN port -> PC tower back (over the desk's
                                      west edge; replaces cable_stubs' black LAN stub)
      VR headset tether               the headset's tether end on the cabinet side ->
                                      loops on the carpet -> PC tower back (DisplayPort),
                                      the headset is wired straight to the PC
      PC power cord                   tower PSU -> strip
      light stand (center)            base station on top of the stand -> down the pole
                                      -> along the baseboard behind the cabinet -> in-line
                                      adapter -> strip
      wall base station (SW)          continues bedroom_fixtures' wall run (ends z 30
                                      behind the desk) -> strip
No brands: plain plates, plain black plastic.

Source of truth: scripted. Frame: PLAN coordinates (+X east, +Y north, Z up, metres,
origin plan (0, 0, 0)); the package goes on a marker at (0, 0, 0) with no rotation.
The stub ends are computed from cable_stubs.py and vr_headset.py's formulas and
dimensions.PLACEMENT, so moving an item on the cabinet re-routes the start of its cable.

Dimensions (inches, plan):
  center wall bedroom face x 138.75, baseboard 3.5 h x 0.5                 shell_layout / shell.py
  filing cabinet (152.6, 73.75) rot 90: south side y 66.25, back x 139.35   shell_layout + dimensions
  desk top x 139.4..210.8, y 0.4..27.3, z 29.5; pedestal x 140..159        desk package (SCAN)
  PC tower x 146.5..155.5, y 8..26, z 29.5..48.5, back faces south (y 8)   desk_computer (SCAN)
  light stand pole (143.5, 104.5), base station centre z 80, back x 142     light_stand package
  SW wall base-station cable: x 138.875, y 26.0, bottom z 30               bedroom_fixtures
  cable plate centre y 45.0, z 12.75                                       PHOTO (IMG_1516) +-2
  duplex outlet centre y 62.5, z 12.75                                     PHOTO (IMG_1516) +-2
  wall plates 2.75 w x 4.5 h x 0.25                                        SPEC (standard 1-gang)
  power strip 10.5 x 1.9 x 1.2, from (147.5, 36) to (141.3, 44.5)          PHOTO/EST
  wall-wart adapters 1.3 x 1.9 x 2.3 on the strip                          EST
  in-line adapter 2.0 x 2.8 x 1.1 at (150.4, 40)                           PHOTO/EST
  square charger brick 2.5 x 2.5 x 1.0 at (146.5, 52.5)                    PHOTO/EST
  cable diameters: power 0.17, coax 0.25, ethernet 0.22, tether 0.17       stub radii / EST
The lidar survey is too sparse on the white wall to see the plates (checked with
Reference/bedroom_cables_work/elev.py); positions come from the photo, scaled between
the pedestal's front (y 27.3) and the cabinet's side (y 66.25).
"""

import math

import bmesh
from mathutils import Matrix, Vector

import common
import dimensions

NAME = "bedroom_cables"
IN = 0.0254


def m(inches):
    return inches * IN


# --- dimensions (inches, plan) -----------------------------------------------------
WALL_X = 138.75                        # shell_layout center wall bedroom face
BASE_H, BASE_T = 3.5, 0.5              # shell.py baseboard
CAB_X, CAB_Y = 152.6, 73.75            # shell_layout filing_cabinet_set (rot 90)
PLATE_W, PLATE_H, PLATE_T = 2.75, 4.5, 0.25   # SPEC standard single-gang plate
COAX_PLATE = (45.0, 12.75)             # PHOTO (y, z centre)
OUTLET = (62.5, 12.75)                 # PHOTO (y, z centre)
STRIP_A, STRIP_B = (147.5, 36.0), (141.3, 44.5)   # PHOTO: room end, wall end (cord + switch)
STRIP_W, STRIP_H = 1.9, 1.2            # EST
INLINE = (150.4, 40.0, 25.0)           # PHOTO (x, y, heading deg); 2.0 x 2.8 x 1.1 EST
BRICK = (146.5, 52.5, 20.0)            # PHOTO (x, y, heading deg); 2.5 x 2.5 x 1.0 EST
TOWER_BACK_Y = 8.0                     # desk_computer: tower y 8..26
DESK_TOP = 29.5                        # desk package
STAND = (143.5, 104.5)                 # shell_layout light_stand__center
SW_BS_CABLE = (138.875, 26.025, 30.0)  # bedroom_fixtures base station cable bottom
# cable radii (inches)
R_PWR = 0.0022 / IN                    # matches cable_stubs' power stubs
R_COAX = 0.0032 / IN                   # matches the coax stub
R_ETH = 0.0028 / IN                    # the white modem-router patch in cable_stubs
R_TETHER = 0.0022 / IN                 # matches vr_headset's tether
R_DC = 0.07                            # EST thin DC leads

ATLAS = {
    "name": NAME,
    "size": 256,
    "regions": {
        "cable_black": (0, 0, 64, 64),
        "cable_white": (64, 0, 64, 64),
        "plastic_black": (128, 0, 64, 64),
        "plate_white": (192, 0, 64, 64),
        "outlet_face": (0, 64, 64, 96),
        "coax_face": (64, 64, 64, 96),
        "metal": (128, 64, 64, 64),
        "led_blue": (192, 64, 32, 32),
        "switch_red": (224, 64, 32, 32),
        "strip_top": (0, 160, 256, 48),
        "strip_side": (0, 208, 256, 48),
        "rubber": (192, 96, 64, 64),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "none"
STATIC = True
VIEWS = [("photo_dir", 250, 45, 0.55), ("corner_top", 270, 70, 0.4)]

STRIP_UV = []          # (faces-centre test) filled by build: strip local frame for UVs


# --- helpers -----------------------------------------------------------------------

def P(x, y, z):
    return Vector((m(x), m(y), m(z)))


def cab_to_plan(v):
    """Cabinet space (metres; +X right, -Y front) -> plan inches. Rotation 90 about Z."""
    return Vector((CAB_X - v.y / IN, CAB_Y + v.x / IN, v.z / IN))


def simplify(pts, max_turn=22.0, max_len=9.0):
    """Drop polyline points where the path runs straight (keeps the tris for the loops)."""
    out = [pts[0]]
    acc = 0.0
    for i in range(1, len(pts) - 1):
        a = (pts[i] - out[-1])
        b = (pts[i + 1] - pts[i])
        if a.length < 1e-6 or b.length < 1e-6:
            continue
        turn = math.degrees(a.angle(b))
        acc += turn
        if acc > max_turn or (pts[i] - out[-1]).length > m(max_len):
            out.append(pts[i])
            acc = 0.0
    out.append(pts[-1])
    return out


def retag(b, src, dst, test):
    """Re-tag faces of region src that pass test (bevel replaces a box's faces)."""
    b.bm.normal_update()
    i = b.idx(src)
    for f in b.bm.faces:
        if f.material_index == i and test(f):
            f.material_index = b.idx(dst)


def cable(b, region, pts, r, n=5, layer=0, samples=8):
    """Sweep a cable through plan-inch points. z <= 0 means 'lying on the carpet'
    (sunk a little into the pile; `layer` lifts crossing cables apart)."""
    q = []
    for x, y, z in pts:
        if z <= 0.0:
            z = r * 0.75 + 0.05 * layer
        q.append(P(x, y, z))
    dense = common.smooth_path(q, samples)
    for v in dense:                     # the spline overshoots where a drop meets the carpet
        v.z = max(v.z, m(r * 0.75))
    path = simplify(dense)
    b.sweep(region, path, common.circle_profile(m(r), n), up=(0, 0, 1))
    return path


def obox(b, region, c, size, heading=0.0, z0=0.0, bevel=0.0):
    """Box standing on z0, centred at plan (x, y), rotated `heading` deg about Z."""
    w, d, h = size
    mat = Matrix.Translation(P(c[0], c[1], z0)) @ Matrix.Rotation(math.radians(heading), 4, "Z")
    return b.box(region, (m(-w / 2), m(-d / 2), 0.0), (m(w / 2), m(d / 2), m(h)), bevel=m(bevel),
                 segments=1, matrix=mat)


# --- power strip -------------------------------------------------------------------

SA, SB = Vector(STRIP_A), Vector(STRIP_B)
S_LEN = (SB - SA).length
S_DIR = (SB - SA).normalized()
S_OUT = Vector((S_DIR.y, -S_DIR.x))            # right of the axis = toward the room (+x, +y)
S_HEAD = math.degrees(math.atan2(S_DIR.y, S_DIR.x))


def spt(s, side=0.0, z=0.0):
    """Point on the strip: s inches from the room end along it, `side` toward the room."""
    p = SA + S_DIR * s + S_OUT * side
    return (p.x, p.y, z)


SLOTS = [1.3, 2.7, 4.1, 5.5, 6.9, 8.3]        # EST receptacle centres from the room end


def power_strip(b):
    mid = (SA + SB) / 2
    mat = Matrix.Translation(P(mid.x, mid.y, 0.0)) @ Matrix.Rotation(math.radians(S_HEAD), 4, "Z")
    L, W, H = S_LEN, STRIP_W, STRIP_H
    b.box("strip_side", (m(-L / 2), m(-W / 2), 0.0), (m(L / 2), m(W / 2), m(H)), bevel=m(0.3),
          segments=1, matrix=mat)
    retag(b, "strip_side", "strip_top", lambda f: f.normal.z > 0.9)
    STRIP_UV.append((mat, L, W))
    # switch and LED near the wall end
    s_sw, s_led = 9.55, 8.95
    for s, reg, sz in ((s_sw, "switch_red", (0.6, 0.8, 0.25)), (s_led, "led_blue", (0.22, 0.22, 0.08))):
        x, y, _ = spt(s, 0.0)
        obox(b, reg, (x, y), sz, S_HEAD, z0=H - 0.05)


def plug_on_strip(b, s, heading_off=90.0, size=(0.75, 1.0, 1.05)):
    """A plug head standing in a receptacle; returns the cable exit point (plan in)."""
    x, y, _ = spt(s, 0.0)
    obox(b, "plastic_black", (x, y), size, S_HEAD, z0=STRIP_H - 0.05, bevel=0.12)
    return spt(s, size[1] / 2 + 0.05, STRIP_H + 0.55)


def wart_on_strip(b, s, side=1.0):
    """A wall-wart adapter plugged into the strip, body overhanging toward `side`;
    returns its DC lead exit (plan in)."""
    x, y, _ = spt(s, 0.35 * side)
    obox(b, "plastic_black", (x, y), (1.3, 1.9, 2.3), S_HEAD, z0=STRIP_H - 0.05, bevel=0.18)
    return spt(s, 1.05 * side, STRIP_H + 1.5)


# --- wall plates -------------------------------------------------------------------

PLANAR = {}


def wall_plate(b, face_region, yc, zc):
    y0, y1 = yc - PLATE_W / 2, yc + PLATE_W / 2
    z0, z1 = zc - PLATE_H / 2, zc + PLATE_H / 2
    b.box("plate_white", P(WALL_X, y0, z0), P(WALL_X + PLATE_T, y1, z1), bevel=m(0.08), segments=1)
    retag(b, "plate_white", face_region,
          lambda f: f.normal.x > 0.9 and m(y0) < f.calc_center_median().y < m(y1))
    PLANAR[face_region] = ("+X", (m(y0), m(y1)), (m(z0), m(z1)))


def coax_plate(b):
    y, z = COAX_PLATE
    wall_plate(b, "coax_face", y, z)
    fx = WALL_X + PLATE_T
    # F-connector: brass barrel, black boot on the cable's plug, cable goes straight down
    b.cylinder("metal", P(fx + 0.3, y, z), m(0.22), m(0.6), axis="X", segments=8)
    b.cylinder("plastic_black", P(fx + 0.95, y, z), m(0.3), m(0.8), axis="X", segments=8)
    return (fx + 1.35, y, z)


def duplex_outlet(b):
    y, z = OUTLET
    wall_plate(b, "outlet_face", y, z)
    fx = WALL_X + PLATE_T
    zp = z - 0.72                      # lower receptacle
    # plug head: flat black body out of the receptacle, cord out of its bottom
    b.box("plastic_black", P(fx, y - 0.72, zp - 0.6), P(fx + 1.1, y + 0.72, zp + 0.6), bevel=m(0.2), segments=1)
    b.cylinder("plastic_black", P(fx + 0.6, y, zp - 0.8), m(0.22), m(0.5), segments=8)
    return (fx + 0.6, y, zp - 1.05)


# --- stub ends from the filing cabinet set -----------------------------------------

def stub_ends():
    """Plan-inch end points of the cable_stubs / vr_headset tether runs over the cabinet's
    left (south) side, plus the router's LAN port for the white ethernet."""
    import cable_stubs
    C = dimensions.CABINET
    H = C["height"]
    lan, lan_out = cable_stubs.router_port(-0.002)
    _, pwr_out = cable_stubs.router_port(0.095)
    _, m_pwr_out = cable_stubs.modem_port(0.079)
    _, m_coax_out = cable_stubs.modem_port(0.36)
    ends = {
        "router_pwr": cable_stubs.over_left_edge(pwr_out)[-1],
        "modem_pwr": cable_stubs.over_left_edge(m_pwr_out, 0.01)[-1],
        "coax": cable_stubs.over_left_edge(m_coax_out, 0.03)[-1],
    }
    # vr_headset.edge_drop(): last point, in cabinet space
    px, py, _ = dimensions.PLACEMENT["vr_headset"]
    ends["tether"] = Vector((-C["width"] / 2 - 0.006, py - 0.06 - 0.005, H - 0.11))
    out = {k: cab_to_plan(v) for k, v in ends.items()}
    out["lan"] = cab_to_plan(lan)
    out["lan_out"] = cab_to_plan(lan_out)
    out["top"] = H / IN
    return out


def down_from(e, pts):
    """Start at a stub end (hanging straight down) and continue through pts."""
    e = tuple(e)
    return [e, (e[0], e[1] - 0.05, e[2] - 1.2)] + pts


# --- build -------------------------------------------------------------------------

def build(coll):
    PLANAR.clear()
    STRIP_UV.clear()
    b = common.Builder(REGIONS)
    E = stub_ends()
    top = E["top"]
    fl = 0.0                                           # "on the carpet"
    bx = WALL_X + BASE_T                               # baseboard face

    power_strip(b)
    coax_in = coax_plate(b)
    outlet_cord = duplex_outlet(b)

    # strip cord: wall end -> along the baseboard -> up into the outlet's lower plug
    se = spt(S_LEN + 0.35, 0.0, 0.55)
    b.cylinder("plastic_black", P(*spt(S_LEN + 0.2, 0.0, 0.55)), m(0.2), m(0.5), axis="X", segments=6)
    cable(b, "cable_black", [se, spt(S_LEN + 1.6, -0.2, fl), (bx + 0.35, 47.5, fl), (bx + 0.3, 53.0, fl),
                             (bx + 0.5, 57.5, fl), (bx + 1.4, 60.5, fl), (bx + 1.3, 62.2, 4.0),
                             (outlet_cord[0] + 0.2, OUTLET[0] - 0.3, 8.5), outlet_cord], 0.13, layer=0)

    # adapters and plugs on the strip
    w_router = wart_on_strip(b, SLOTS[4], 1.0)
    w_modem = wart_on_strip(b, SLOTS[3], -1.0)
    p_pc = plug_on_strip(b, SLOTS[0])
    p_stand = plug_on_strip(b, SLOTS[1])
    p_swbs = plug_on_strip(b, SLOTS[2])

    # in-line adapter (light stand supply) and the loose square charger
    ix, iy, ih = INLINE
    obox(b, "plastic_black", (ix, iy), (2.0, 2.8, 1.1), ih, bevel=0.2)
    hx, hy, hh = BRICK
    obox(b, "plastic_black", (hx, hy), (2.5, 2.5, 1.0), hh, bevel=0.2)
    rot = Matrix.Rotation(math.radians(hh), 4, "Z")
    for sx in (-0.25, 0.25):                          # folding prongs, lying flat on top
        c = Vector((hx, hy, 0)) + rot @ Vector((sx, 0.2, 0))
        obox(b, "metal", (c.x, c.y), (0.06, 0.62, 0.25), hh, z0=1.0)

    # --- router + modem power: stub ends -> down the cabinet side -> carpet -> adapters
    e = E["router_pwr"]
    cable(b, "cable_black", down_from(e, [(e[0] - 2.5, 62.2, 13.0), (141.8, 60.8, 2.0), (143.2, 60.5, fl),
                                          (146.8, 57.0, fl), (150.8, 52.5, fl), (151.0, 47.0, fl),
                                          (w_router[0] + 1.2, w_router[1] + 0.8, fl),
                                          (w_router[0] + 0.3, w_router[1] + 0.15, 0.8), w_router]),
          R_PWR, layer=2)
    e = E["modem_pwr"]
    cable(b, "cable_black", down_from(e, [(e[0] - 1.2, 63.0, 14.0), (140.4, 61.0, 2.0), (140.9, 59.0, fl),
                                          (143.6, 55.5, fl), (145.6, 51.0, fl), (143.2, 47.8, fl),
                                          (w_modem[0] - 0.9, w_modem[1] - 0.4, fl),
                                          (w_modem[0] - 0.3, w_modem[1] - 0.1, 0.8), w_modem]),
          R_PWR, layer=1)

    # --- coax: stub end -> carpet by the wall -> loop -> up to the cable plate
    e = E["coax"]
    cable(b, "cable_black", down_from(e, [(e[0] - 0.4, 65.3, 12.0), (bx + 0.4, 63.0, 2.5), (bx + 0.6, 59.5, fl),
                                          (144.0, 56.0, fl), (147.5, 52.0, fl), (145.0, 47.5, fl),
                                          (bx + 1.2, 46.4, fl), (bx + 0.25, 45.6, 3.9),
                                          (WALL_X + 0.6, 45.2, 8.5), (coax_in[0] - 0.1, 45.0, 11.4),
                                          (coax_in[0] - 0.4, 45.0, COAX_PLATE[1])]),
          R_COAX, layer=3)

    # --- white ethernet: router LAN port -> over the cabinet's south edge by the wall ->
    # down the wall corner -> along the baseboard -> up the desk's west gap -> tower back
    lan, lo = E["lan"], E["lan_out"]
    eth_port = (148.0, TOWER_BACK_Y, 44.0)
    gap = WALL_X + 0.3
    eth = [tuple(lan), tuple(lo), (lo[0] - 0.4, 66.45, top + R_ETH), (lo[0] - 0.8, 66.12, top - 0.2),
           (lo[0] - 2.2, 65.95, top - 3.0), (140.2, 65.85, 16.0), (bx + 0.2, 65.4, 3.8),
           (bx + 0.15, 62.0, fl), (bx + 0.15, 45.0, fl), (bx + 0.2, 30.0, fl), (bx + 0.2, 24.0, fl),
           (gap + 0.25, 21.8, 3.9), (gap, 21.6, 15.0), (gap, 21.4, DESK_TOP - 0.6),
           (139.8, 20.8, DESK_TOP + R_ETH), (141.5, 13.0, DESK_TOP + R_ETH), (145.0, 6.8, DESK_TOP + R_ETH),
           (eth_port[0], 6.2, 36.0), (eth_port[0], 7.2, 43.2), eth_port]
    cable(b, "cable_white", eth, R_ETH, layer=0)
    b.box("cable_white", P(eth_port[0] - 0.3, TOWER_BACK_Y - 0.6, eth_port[2] - 0.25),
          P(eth_port[0] + 0.3, TOWER_BACK_Y, eth_port[2] + 0.25))

    # --- VR headset tether: the tether end on the cabinet's south side -> down the front
    # corner -> slack loops across the carpet -> the desk's west gap -> tower (DisplayPort)
    e = E["tether"]
    dp = (150.2, TOWER_BACK_Y, 38.0)
    teth = down_from(e, [(e[0] + 0.5, 65.5, 12.0), (e[0] + 0.3, 64.6, 1.5), (163.0, 61.5, fl),
                         (159.5, 58.5, fl), (155.5, 54.0, fl), (153.5, 47.0, fl), (157.5, 41.0, fl),
                         (161.0, 44.5, fl), (158.0, 50.5, fl), (151.0, 58.5, fl), (147.5, 60.0, fl),
                         (150.5, 49.0, fl), (155.0, 37.5, fl), (152.5, 32.0, fl), (146.0, 30.8, fl),
                         (141.4, 29.6, fl), (bx + 0.4, 26.0, fl), (bx + 0.35, 21.0, fl),
                         (gap + 0.4, 19.6, 3.9), (gap - 0.05, 19.3, 15.0), (gap - 0.05, 19.1, DESK_TOP - 0.6),
                         (139.7, 18.6, DESK_TOP + R_TETHER), (142.0, 11.0, DESK_TOP + R_TETHER),
                         (147.0, 5.2, DESK_TOP + R_TETHER), (dp[0], 5.8, 33.0), (dp[0], 7.1, 37.4), dp])
    cable(b, "cable_black", teth, R_TETHER, layer=4)
    b.box("plastic_black", P(dp[0] - 0.4, TOWER_BACK_Y - 0.7, dp[2] - 0.2), P(dp[0] + 0.4, TOWER_BACK_Y, dp[2] + 0.2))

    # --- PC power cord: PSU (bottom of the tower back) -> desk gap -> carpet -> strip
    psu = (153.2, TOWER_BACK_Y, DESK_TOP + 2.0)
    b.box("plastic_black", P(psu[0] - 0.5, TOWER_BACK_Y - 0.9, psu[2] - 0.35), P(psu[0] + 0.5, TOWER_BACK_Y, psu[2] + 0.35))
    cable(b, "cable_black", [(psu[0], TOWER_BACK_Y - 0.9, psu[2]), (psu[0], 6.5, psu[2] - 0.8),
                             (151.0, 4.2, DESK_TOP + 0.15), (144.0, 6.5, DESK_TOP + 0.15), (140.2, 14.5, DESK_TOP + 0.15),
                             (gap - 0.1, 16.6, DESK_TOP - 0.7), (gap - 0.1, 16.9, 15.0), (gap + 0.3, 17.4, 3.9),
                             (bx + 0.35, 19.0, fl), (bx + 0.4, 25.5, fl), (140.8, 29.0, fl), (143.0, 31.5, fl),
                             (p_pc[0] - 1.6, p_pc[1] - 1.8, fl), (p_pc[0] - 0.4, p_pc[1] - 0.5, 0.8), p_pc],
          0.13, layer=1)

    # --- center light stand: base station back -> down the pole -> carpet -> baseboard ->
    # behind the cabinet -> in-line adapter -> strip
    sx, sy = STAND
    zl = 0.0
    stand = [(sx - 1.55, sy, 79.2), (sx - 1.9, sy, 78.2), (sx - 0.62, sy, 76.0), (sx - 0.42, sy, 70.0),
             (sx - 0.5, sy, 60.5), (sx - 0.52, sy, 48.0), (sx - 0.66, sy, 36.8), (sx - 0.7, sy + 0.1, 30.0),
             (sx - 0.95, sy + 0.1, 23.0), (sx - 1.1, sy - 0.6, 12.0), (sx - 1.8, sy - 1.6, zl),
             (bx + 0.6, sy - 3.5, zl), (bx + 0.35, 96.0, zl), (bx + 0.3, 82.0, zl), (bx + 0.3, 69.0, zl),
             (bx + 1.2, 64.5, zl), (142.0, 60.0, zl), (148.5, 57.5, zl), (153.5, 52.5, zl), (154.0, 45.5, zl),
             (ix + 1.9, iy + 1.8, zl), (ix + 0.45, iy + 1.2, 0.5)]
    cable(b, "cable_black", stand, R_PWR, layer=5)
    cable(b, "cable_black", [(ix - 0.45, iy - 1.2, 0.5), (ix - 1.4, iy - 2.4, zl), (ix - 4.0, iy - 3.8, zl),
                             (p_stand[0] + 1.1, p_stand[1] - 1.9, zl), (p_stand[0] + 0.5, p_stand[1] - 0.5, 0.8),
                             p_stand], R_PWR, layer=2)

    # --- SW wall base station: bedroom_fixtures' run ends at z 30 behind the desk
    wx, wy, wz = SW_BS_CABLE
    cable(b, "cable_black", [(wx, wy, wz + 1.0), (wx, wy, wz - 0.5), (wx + 0.05, wy + 0.2, 12.0),
                             (bx - 0.1, wy + 0.5, 3.9), (bx + 0.45, wy + 1.4, fl), (140.8, 28.6, fl),
                             (140.2, 31.0, fl), (141.4, 33.4, fl),
                             (p_swbs[0] - 1.4, p_swbs[1] - 0.2, fl), (p_swbs[0] - 0.4, p_swbs[1], 0.8), p_swbs],
          R_PWR, layer=3)

    # a short slack loop on the loose charger, as in the photo
    cable(b, "cable_black", [(hx + 1.0, hy + 0.9, 0.4), (hx + 2.4, hy + 2.3, fl), (hx + 5.0, hy + 1.0, fl),
                             (hx + 4.6, hy - 3.0, fl), (hx + 1.0, hy - 3.8, fl), (hx - 2.2, hy - 1.8, fl),
                             (hx - 2.6, hy + 1.8, fl), (hx - 0.6, hy + 3.4, fl)], R_DC, n=5, layer=6)

    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS, planar=dict(PLANAR))
    _strip_top_uvs(ob)
    common.collapse_materials(ob, {r: mat for r in REGIONS})


def _strip_top_uvs(ob):
    """Map the strip's top face along its own axis so the receptacle row lines up."""
    import atlas_layout
    mat, L, W = STRIP_UV[0]
    inv = mat.inverted()
    u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, "strip_top")
    me = ob.data
    ri = [m_.name.split(".")[0] for m_ in me.materials].index("strip_top")
    uvl = me.uv_layers["UVMap"]
    for p in me.polygons:
        if p.material_index != ri:
            continue
        for li in p.loop_indices:
            lc = inv @ me.vertices[me.loops[li].vertex_index].co
            fu = (lc.x + m(L / 2)) / m(L)
            fv = (lc.y + m(W / 2)) / m(W)
            uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))
