"""Kitchen built-ins: honey-oak base cabinets on the west and north walls with a white
laminate countertop and backsplash, a double-bowl stainless sink with a gooseneck faucet,
upper wall cabinets (short over the sink and the microwave, a diagonal corner door) and
the cabinet over the fridge. The dishwasher, range, microwave and fridge are their own
packages; this one leaves their gaps.

Source of truth: scripted from the living-room/kitchen LiDAR survey (registered splat +
LiDAR points in plan inches) and the survey photo crops (door and drawer layout, pulls).

FRAME: PLAN COORDINATES. The object origin is plan (0, 0, 0) (the living room's SW
interior corner at floor level): object X = plan x, object Y = plan y, in metres. Place it
at the plan origin with no rotation (like window_units). West run fronts face +X, north
run fronts face -Y.

Provenance tags: SCAN = measured on the registered survey points, PHOTO = counted or
proportioned from the survey crops, EST = standard size or guess.
"""

import math

import common

IN = 0.0254


def m(v):
    return v * IN


# --- dimensions (plan inches) -------------------------------------------------------
NW = 286.0              # SCAN north wall face
WW = 0.0                # SCAN west wall face
STUB_Y = 186.0          # SCAN north face of the stub wall (shell builds the wall)
TOP_Z0, TOP_Z1 = 34.5, 36.0   # SCAN top at 36; EST 1.5 in laminate slab with bullnose
CARC_Z = TOP_Z0         # carcass top
TOE_H, TOE_D = 4.0, 3.0 # EST toe kick (light vinyl base in the photos)
DOOR_T = 0.75           # EST
GAP = 0.2               # EST reveal between fronts (shows the oak frame behind)
SPLASH_H, SPLASH_T = 4.0, 0.75   # PHOTO/EST short laminate backsplash

# west base run (fronts face +X)
W_COUNTER_X = 25.5      # SCAN counter edge
W_FACE = 24.75          # SCAN/EST door face (counter overhangs ~0.75)
DW_Y = (188.5, 212.5)   # SCAN dishwasher gap (dishwasher package)
SINK_BASE_Y = (212.5, 248.5)   # PHOTO false front + two doors, centred on the sink
W_DOOR_Y = (248.5, 259.5)      # PHOTO single full-height door up to the north run front

# north base run (fronts face -Y)
N_FACE = 259.5          # SCAN door face
N_COUNTER_Y = 256.8     # SCAN counter edge
N_X0, N_X1 = 25.5, 100.0       # SCAN run (x 0-25.5 is the blind corner under the west top)
RANGE_X = (49.5, 79.5)  # SCAN range gap
N_CORNER_DOOR = (25.5, 36.5)   # PHOTO corner door
N_DRAWERS = (36.5, 49.5)       # PHOTO four-drawer bank
N_EAST = (79.5, 100.0)         # PHOTO drawer over door
DRAWER_Z = (27.0, CARC_Z)      # PHOTO top drawer band on door sections

# sink (SCAN centre (12, 230.5), bowls y 214-246)
SINK_RIM = (1.0, 23.0, 213.5, 246.5)          # EST x0, x1, y0, y1 of the rim
SINK_BOWLS = [(214.5, 229.75), (231.25, 245.5)]   # SCAN/EST two near-equal bowls
SINK_BX = (3.5, 21.0)                         # EST bowl x span
SINK_DEPTH = 8.0                              # EST
FAUCET = (2.2, 230.5)                         # PHOTO behind the divider

# uppers
UP_D = 13.0             # SCAN depth (north front y ~273, west front x ~13)
UP_Z = (53.0, 97.5)     # SCAN
SINK_UP_Z0 = 70.0       # SCAN short cabinets over the sink
MW_UP_Z0 = 76.0         # SCAN short cabinets over the microwave (microwave top)
W_UP = [                 # (y0, y1, z0, doors, pull side "lo"/"hi"/"pair")  PHOTO
    (189.0, 214.0, UP_Z[0], 1, "hi"),
    (214.0, 246.0, SINK_UP_Z0, 2, "pair"),
    (246.0, 264.0, UP_Z[0], 1, "lo"),
]
CORNER = ((13.0, 264.0), (22.0, 273.0))   # PHOTO/EST 45-degree corner door face
N_UP = [                 # (x0, x1, z0, doors, pull side)  PHOTO
    (22.0, 49.5, UP_Z[0], 2, "pair"),
    (49.5, 79.5, MW_UP_Z0, 2, "pair"),
    (79.5, 98.0, UP_Z[0], 1, "lo"),
]
FRIDGE_UP = (99.0, 134.0, 255.0, 84.0, 97.5)   # SCAN x0, x1, front y, z0, z1 (to the wall)
PULL_L, PULL_T, PULL_OFF = 5.0, 0.4, 1.1       # PHOTO arched bar pulls (EST size)
KNOB_R, KNOB_L = 0.6, 1.0                       # PHOTO round drawer knobs (EST size)

NAME = "kitchen_cabinets"
ATLAS = {
    "name": "kitchen_cabinets",
    "size": 1024,
    "regions": {
        "oak": (0, 0, 1024, 640),
        "counter": (0, 640, 512, 384),
        "steel": (512, 640, 256, 192),
        "nickel": (768, 640, 128, 128),
        "toe": (896, 640, 128, 128),
        "oak_dark": (768, 768, 128, 128),
        "panel_black": (896, 768, 128, 128),
        "drain": (512, 832, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"kitchen_cabinets": {"atlas": "kitchen_cabinets", "mode": "opaque", "tiled": False}}
COLLIDER = "mesh"
STATIC = True
# (name, azimuth, elevation, distance scale); az 0 = from the south. Match the survey crops.
VIEWS = [("from_dining_se", 30, 18, 0.75), ("from_dining_s", 8, 20, 0.7),
         ("from_dining_e", 65, 18, 0.7), ("uppers", 5, 2, 0.7)]


# --- geometry helpers ---------------------------------------------------------------

def _p(x, y, z):
    return (m(x), m(y), m(z))


class Kit:
    def __init__(self, b):
        self.b = b

    def box(self, region, x0, x1, y0, y1, z0, z1, bevel=0.0):
        self.b.box(region, _p(min(x0, x1), min(y0, y1), min(z0, z1)),
                   _p(max(x0, x1), max(y0, y1), max(z0, z1)), bevel=m(bevel))

    def rbox(self, region, run, face, a0, a1, d0, d1, z0, z1, bevel=0.0):
        """Box in run coordinates: a along the wall, d outward from `face` (toward the room)."""
        if run == "W":
            self.box(region, face + d0, face + d1, a0, a1, z0, z1, bevel)
        else:
            self.box(region, a0, a1, face - d0, face - d1, z0, z1, bevel)

    def pull(self, run, face, a, z, vertical):
        h, t = PULL_L / 2, PULL_T / 2
        if vertical:
            self.rbox("nickel", run, face, a - t, a + t, PULL_OFF - PULL_T, PULL_OFF, z - h, z + h)
            for zz in (z - h + 0.4, z + h - 0.4):
                self.rbox("nickel", run, face, a - 0.15, a + 0.15, 0, PULL_OFF - PULL_T, zz - 0.15, zz + 0.15)
        else:
            self.rbox("nickel", run, face, a - h, a + h, PULL_OFF - PULL_T, PULL_OFF, z - t, z + t)
            for aa in (a - h + 0.4, a + h - 0.4):
                self.rbox("nickel", run, face, aa - 0.15, aa + 0.15, 0, PULL_OFF - PULL_T, z - 0.15, z + 0.15)

    def knob(self, run, face, a, z):
        if run == "W":
            c, ax = _p(face + DOOR_T + KNOB_L / 2, a, z), "X"
        else:
            c, ax = _p(a, face - DOOR_T - KNOB_L / 2, z), "Y"
        self.b.cylinder("nickel", c, m(KNOB_R), m(KNOB_L), axis=ax, segments=8)

    def door(self, run, face, a0, a1, z0, z1, frame=2.0):
        """Shaker door: a recessed flat panel inside a raised frame."""
        a0, a1, z0, z1 = a0 + GAP, a1 - GAP, z0 + GAP, z1 - GAP
        self.rbox("oak", run, face, a0, a1, 0, DOOR_T - 0.25, z0, z1)
        for s0, s1, t0, t1 in ((a0, a0 + frame, z0, z1), (a1 - frame, a1, z0, z1),
                               (a0 + frame, a1 - frame, z0, z0 + frame),
                               (a0 + frame, a1 - frame, z1 - frame, z1)):
            self.rbox("oak", run, face, s0, s1, DOOR_T - 0.25, DOOR_T, t0, t1)

    def drawer(self, run, face, a0, a1, z0, z1):
        self.rbox("oak", run, face, a0 + GAP, a1 - GAP, 0, DOOR_T, z0 + GAP, z1 - GAP, bevel=0.12)


# --- base run -----------------------------------------------------------------------

def _base(k):
    wc = W_FACE     # west carcass face (fronts sit on it)
    nc = N_FACE     # north carcass face
    s0, s1 = SINK_BASE_Y
    # west carcass (dishwasher gap left open); under the sink the top drops below the bowls
    k.box("oak_dark", WW, wc, s0, s1, TOE_H, TOP_Z1 - SINK_DEPTH - 1.0)
    k.box("oak_dark", wc - 0.75, wc, s0, s1, TOE_H, CARC_Z)          # face frame
    k.box("oak_dark", WW, wc, s1, NW, TOE_H, CARC_Z)                  # to the north wall (corner)
    k.box("oak_dark", WW, wc, STUB_Y, DW_Y[0], TOE_H, CARC_Z)         # filler at the stub wall
    k.box("oak", wc, wc + DOOR_T, STUB_Y, DW_Y[0] - GAP, TOE_H, CARC_Z)
    k.box("oak_dark", WW, wc, DW_Y[1] - 0.5, s0, TOE_H, CARC_Z)       # dishwasher side panel
    # north carcass, corner door to the range and range to the end
    k.box("oak_dark", wc, RANGE_X[0], nc, NW, TOE_H, CARC_Z)
    k.box("oak_dark", RANGE_X[1], N_X1, nc, NW, TOE_H, CARC_Z)
    k.box("oak", N_X1 - 0.5, N_X1, nc - DOOR_T, NW, TOE_H, CARC_Z)   # finished end panel
    # toe kicks
    k.box("toe", WW, wc - TOE_D, STUB_Y, DW_Y[0], 0, TOE_H)
    k.box("toe", WW, wc - TOE_D, DW_Y[1], nc + TOE_D, 0, TOE_H)
    k.box("toe", WW, RANGE_X[0], nc + TOE_D, NW, 0, TOE_H)
    k.box("toe", RANGE_X[1], N_X1, nc + TOE_D, NW, 0, TOE_H)

    z0, dz0, dz1 = TOE_H, DRAWER_Z[0], DRAWER_Z[1]
    # sink base: false front over two doors, pulls by the meeting stiles
    mid = (s0 + s1) / 2
    k.drawer("W", wc, s0, s1, dz0, dz1)
    for a0, a1, pa in ((s0, mid, mid - 1.6), (mid, s1, mid + 1.6)):
        k.door("W", wc, a0, a1, z0, dz0)
        k.pull("W", wc, pa, dz0 - 4.0, vertical=True)
    # single full-height door next to the corner
    a0, a1 = W_DOOR_Y
    k.door("W", wc, a0, a1, z0, dz1)
    k.pull("W", wc, a0 + 1.6, dz1 - 4.5, vertical=True)
    # north: corner door
    a0, a1 = N_CORNER_DOOR
    k.door("N", nc, a0, a1, z0, dz1)
    k.pull("N", nc, a1 - 1.6, dz1 - 4.5, vertical=True)
    # four-drawer bank (short top drawer)
    a0, a1 = N_DRAWERS
    edges = [dz1, 28.5, 20.5, 12.5, z0]
    for zt, zb in zip(edges, edges[1:]):
        k.drawer("N", nc, a0, a1, zb, zt)
        k.knob("N", nc, (a0 + a1) / 2, (zb + zt) / 2 + (1.0 if zt < dz1 else 0.0))
    # east of the range: drawer over a door
    a0, a1 = N_EAST
    k.drawer("N", nc, a0, a1, dz0, dz1)
    k.knob("N", nc, (a0 + a1) / 2, (dz0 + dz1) / 2)
    k.door("N", nc, a0, a1, z0, dz0)
    k.pull("N", nc, a0 + 1.6, dz0 - 4.0, vertical=True)


def _counter(k):
    z0, z1 = TOP_Z0, TOP_Z1
    rx0, rx1, ry0, ry1 = SINK_RIM
    ex = W_COUNTER_X
    # west top, split around the sink cut-out
    k.box("counter", WW, ex, STUB_Y, ry0, z0, z1, bevel=0.4)
    k.box("counter", WW, ex, ry1, NW, z0, z1, bevel=0.4)
    k.box("counter", WW, rx0, ry0, ry1, z0, z1)
    k.box("counter", rx1, ex, ry0, ry1, z0, z1, bevel=0.4)
    # north top, both sides of the range
    k.box("counter", ex, RANGE_X[0], N_COUNTER_Y, NW, z0, z1, bevel=0.4)
    k.box("counter", RANGE_X[1], N_X1, N_COUNTER_Y, NW, z0, z1, bevel=0.4)
    # backsplash
    k.box("counter", WW, WW + SPLASH_T, STUB_Y, NW - SPLASH_T, z1, z1 + SPLASH_H)
    k.box("counter", WW, RANGE_X[0], NW - SPLASH_T, NW, z1, z1 + SPLASH_H)
    k.box("counter", RANGE_X[1], N_X1, NW - SPLASH_T, NW, z1, z1 + SPLASH_H)


def _sink(k):
    top = TOP_Z1
    rx0, rx1, ry0, ry1 = SINK_RIM
    bx0, bx1 = SINK_BX
    (b0y0, b0y1), (b1y0, b1y1) = SINK_BOWLS
    rim = 0.12
    # rim deck around and between the bowls
    k.box("steel", rx0, bx0, ry0, ry1, top, top + rim)
    k.box("steel", bx1, rx1, ry0, ry1, top, top + rim)
    k.box("steel", bx0, bx1, ry0, b0y0, top, top + rim)
    k.box("steel", bx0, bx1, b1y1, ry1, top, top + rim)
    k.box("steel", bx0, bx1, b0y1, b1y0, top, top + rim)
    t = 0.08
    zb = top - SINK_DEPTH
    for y0, y1 in SINK_BOWLS:
        k.box("steel", bx0, bx0 + t, y0, y1, zb, top)
        k.box("steel", bx1 - t, bx1, y0, y1, zb, top)
        k.box("steel", bx0, bx1, y0, y0 + t, zb, top)
        k.box("steel", bx0, bx1, y1 - t, y1, zb, top)
        k.box("steel", bx0, bx1, y0, y1, zb - t, zb)
        cy, cx = (y0 + y1) / 2, (bx0 + bx1) / 2
        k.box("drain", cx - 1.6, cx + 1.6, cy - 1.6, cy + 1.6, zb, zb + 0.05)
    # faucet: base, gooseneck arching out over the bowls, side lever
    fx, fy = FAUCET
    k.b.cylinder("nickel", _p(fx, fy, top + rim + 0.5), m(1.1), m(1.0), segments=10)
    path = common.smooth_path([_p(fx, fy, top + rim + 0.8), _p(fx, fy, top + 11.0),
                               _p(fx + 2.5, fy, top + 14.0), _p(fx + 6.5, fy, top + 13.0),
                               _p(fx + 8.0, fy, top + 9.5)], samples=3)
    k.b.sweep("nickel", path, common.circle_profile(m(0.5), 8), up=(0, 1, 0))
    k.box("nickel", fx - 0.3, fx + 0.3, fy + 1.0, fy + 4.0, top + 5.0, top + 5.6)


# --- uppers -------------------------------------------------------------------------

def _pull_a(hinge, i, doors, d0, d1):
    if hinge == "pair":
        return d1 - 1.6 if i % 2 == 0 else d0 + 1.6
    return d0 + 1.6 if hinge == "lo" else d1 - 1.6


def _uppers(k):
    z1 = UP_Z[1]
    face_w = WW + UP_D
    for y0, y1, z0, doors, hinge in W_UP:
        k.box("oak_dark", WW, face_w - DOOR_T, y0, y1, z0, z1)
        w = (y1 - y0) / doors
        for i in range(doors):
            d0, d1 = y0 + i * w, y0 + (i + 1) * w
            k.door("W", face_w - DOOR_T, d0, d1, z0, z1)
            k.pull("W", face_w - DOOR_T, _pull_a(hinge, i, doors, d0, d1), z0 + 3.5, vertical=True)
    face_n = NW - UP_D
    for x0, x1, z0, doors, hinge in N_UP:
        k.box("oak_dark", x0, x1, face_n + DOOR_T, NW, z0, z1)
        w = (x1 - x0) / doors
        for i in range(doors):
            d0, d1 = x0 + i * w, x0 + (i + 1) * w
            k.door("N", face_n + DOOR_T, d0, d1, z0, z1)
            k.pull("N", face_n + DOOR_T, _pull_a(hinge, i, doors, d0, d1), z0 + 3.5, vertical=True)
    # diagonal corner cabinet: carcass prism plus a door on the 45-degree face
    (cx0, cy0), (cx1, cy1) = CORNER
    outline = [_p(WW, cy0, 0)[:2], _p(cx0, cy0, 0)[:2], _p(cx1, cy1, 0)[:2],
               _p(cx1, NW, 0)[:2], _p(WW, NW, 0)[:2]]
    k.b.prism("oak_dark", outline, m(UP_Z[0]), m(z1))
    L = math.hypot(cx1 - cx0, cy1 - cy0)
    ang = math.atan2(cy1 - cy0, cx1 - cx0)
    import mathutils
    mx = mathutils.Matrix.Translation(_p(cx0, cy0, 0)) @ mathutils.Matrix.Rotation(ang, 4, "Z")
    # door in a local frame: u along the face (0..L), v outward (-Y local points to the room)
    g, fr, z0 = GAP, 2.0, UP_Z[0]

    def lbox(u0, u1, v0, v1, zz0, zz1, region="oak"):
        k.b.box(region, (m(u0), m(-v1), m(zz0)), (m(u1), m(-v0), m(zz1)), matrix=mx)

    lbox(g, L - g, 0, DOOR_T - 0.25, z0 + g, z1 - g)
    for u0, u1, t0, t1 in ((g, g + fr, z0 + g, z1 - g), (L - g - fr, L - g, z0 + g, z1 - g),
                           (g + fr, L - g - fr, z0 + g, z0 + g + fr), (g + fr, L - g - fr, z1 - g - fr, z1 - g)):
        lbox(u0, u1, DOOR_T - 0.25, DOOR_T, t0, t1)
    pu, pz = L - g - 1.6, z0 + 3.5
    lbox(pu - PULL_T / 2, pu + PULL_T / 2, PULL_OFF - PULL_T, PULL_OFF, pz - PULL_L / 2, pz + PULL_L / 2, "nickel")
    for zz in (pz - PULL_L / 2 + 0.4, pz + PULL_L / 2 - 0.4):
        lbox(pu - 0.15, pu + 0.15, 0, PULL_OFF - PULL_T, zz - 0.15, zz + 0.15, "nickel")
    # cabinet over the fridge: deep box to the wall, a pair of short doors
    x0, x1, fy, z0, z1f = FRIDGE_UP
    k.box("oak_dark", x0, x1, fy + DOOR_T, NW, z0, z1f)
    mid = (x0 + x1) / 2
    for d0, d1, pa in ((x0, mid, mid - 1.6), (mid, x1, mid + 1.6)):
        k.door("N", fy + DOOR_T, d0, d1, z0, z1f)
        k.pull("N", fy + DOOR_T, pa, z0 + 3.5, vertical=True)


def build(coll):
    b = common.Builder(REGIONS)
    k = Kit(b)
    _base(k)
    _counter(k)
    _sink(k)
    _uppers(k)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
