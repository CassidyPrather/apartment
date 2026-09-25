"""Kitchen built-ins: the L-shaped run of oak base cabinets, laminate countertop, upper
wall cabinets, double-bowl sink with faucet, the dishwasher front and the range hood.

Source of truth: scripted (measurement-driven, repeated structure). Coarse block-in.
Layout is written in the shell's plan inches (blender/lib/shell_layout.py: +X east,
+Y north, origin at the living room's SW interior corner) and shifted so the object's
origin sits on the floor at the centre of the kitchen footprint (x 0-134, y 189.9-289.9).
Place it at plan (67.0, 239.95), rotation 0. The run hugs the west wall (fronts face +X)
and the north wall (fronts face -Y).

Layout provenance: the plan illustration (not to scale) gives the order along each wall;
a photo through the bedroom door gives the west-wall uppers (single door, a short pair
over the sink, a single wide door into the corner) and the oak shaker doors with bar
pulls. Every position below is EST until the kitchen is tape-measured.
"""

import math

import common

IN = 0.0254


def m(v):
    return v * IN


# --- dimensions (inches) ----------------------------------------------------------
X0, X1, Y0, Y1 = 0.0, 134.0, 189.9, 289.9     # kitchen interior (shell_layout, M)
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2          # object origin in plan inches

BASE_H = 34.5          # EST standard carcass height
TOP_T = 1.5            # EST counter thickness (top at 36)
BASE_D = 23.25         # EST carcass depth; doors bring the face to ~24
DOOR_T = 0.75          # EST
OVERHANG_D = 25.0      # EST counter depth from the wall (1 in past the doors)
TOE_H, TOE_D = 4.0, 3.0    # EST toe kick height and recess
SPLASH_H, SPLASH_T = 4.0, 0.75   # EST laminate backsplash (guess; photo shows a light wall)
UP_D = 12.0            # EST upper cabinet depth
UP_Z0, UP_Z1 = 54.0, 84.0   # EST uppers: bottoms at 54, 30 tall
SHORT_Z0 = 66.0        # EST short uppers over the sink and range (18 tall; photo ratio ~0.6)
FRIDGE_UP_Z0 = 70.0    # EST cabinet over the fridge
GAP = 0.125            # EST reveal between doors
RANGE_X = (56.0, 86.0)     # EST 30 in range gap on the north wall (plan order)
FRIDGE_X = (100.0, 134.0)  # EST fridge alcove against the center wall (plan)
NORTH_FACE = Y1 - BASE_D   # north run carcass face (y)
WEST_FACE = X0 + BASE_D    # west run carcass face (x)

# Base sections: (run, a0, a1, kind, columns). run "W" = west wall (a = y), "N" = north (a = x).
BASE = [
    ("W", Y0, 192.0, "filler", 0),
    ("W", 192.0, 216.0, "dishwasher", 0),          # EST: plan shows an appliance here
    ("W", 216.0, 252.0, "sink", 2),                # EST: sink centred on y 234 (plan)
    ("W", 252.0, NORTH_FACE, "drawer_door", 1),
    ("N", WEST_FACE + DOOR_T, RANGE_X[0], "drawer_door", 2),
    ("N", RANGE_X[1], FRIDGE_X[0], "drawer_door", 1),
]
# Upper sections: (run, a0, a1, z0, z1, doors, hinge). hinge: "pair", "lo" or "hi" = which
# end of the run axis the hinge sits on (the pull goes on the other side).
UPPER = [
    ("W", Y0, 216.0, UP_Z0, UP_Z1, 1, "lo"),        # photo: opened, hinged on the south
    ("W", 216.0, 252.0, SHORT_Z0, UP_Z1, 2, "pair"),   # photo: short pair over the sink
    ("W", 252.0, Y1 - UP_D, UP_Z0, UP_Z1, 1, "hi"),    # photo: wide door, pull bottom-left
    ("N", X0 + UP_D, RANGE_X[0], UP_Z0, UP_Z1, 3, "pair"),
    ("N", RANGE_X[0], RANGE_X[1], SHORT_Z0, UP_Z1, 2, "pair"),
    ("N", RANGE_X[1], FRIDGE_X[0], UP_Z0, UP_Z1, 1, "lo"),
    ("N", FRIDGE_X[0], FRIDGE_X[1], FRIDGE_UP_Z0, UP_Z1, 2, "pair"),
]
HOOD = (RANGE_X[0], RANGE_X[1], 60.0, SHORT_Z0, 17.0)     # EST x0, x1, z0, z1, depth
SINK = {"x": (5.5, 21.5), "bowls": [(218.5, 233.0), (235.0, 249.5)], "depth": 8.0,
        "rim": (2.5, 23.0, 217.0, 251.0)}                  # EST 33 x 20.5 double bowl
FAUCET_X, FAUCET_Y = 3.6, 234.0                           # EST
PULL_L, PULL_T, PULL_OFF = 5.0, 0.375, 1.1               # EST bar pull length, bar, standoff

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
        "white": (768, 768, 128, 128),
        "panel_black": (896, 768, 128, 128),
        "drain": (512, 832, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"kitchen_cabinets": {"atlas": "kitchen_cabinets", "mode": "opaque", "tiled": False}}
COLLIDER = "mesh"
STATIC = True
VIEWS = [("photo", 62, 6, 0.75), ("plan_top", 0, 89, 1.0)]


# --- geometry helpers ---------------------------------------------------------------

def _p(x, y, z):
    return (m(x - CX), m(y - CY), m(z))


class Kit:
    def __init__(self, b):
        self.b = b

    def box(self, region, x0, x1, y0, y1, z0, z1, bevel=0.0):
        lo = _p(min(x0, x1), min(y0, y1), min(z0, z1))
        hi = _p(max(x0, x1), max(y0, y1), max(z0, z1))
        self.b.box(region, lo, hi, bevel=m(bevel))

    def run_box(self, region, run, face, a0, a1, d0, d1, z0, z1, bevel=0.0):
        """Box in run coordinates: a along the wall, d outward from `face`."""
        if run == "W":
            self.box(region, face + d0, face + d1, a0, a1, z0, z1, bevel)
        else:
            self.box(region, a0, a1, face - d0, face - d1, z0, z1, bevel)

    def pull(self, run, face, a, z, vertical):
        h = PULL_L / 2
        t = PULL_T / 2
        if vertical:
            self.run_box("nickel", run, face, a - t, a + t, PULL_OFF - PULL_T, PULL_OFF, z - h, z + h)
            for zz in (z - h + 0.5, z + h - 0.5):
                self.run_box("nickel", run, face, a - 0.15, a + 0.15, 0, PULL_OFF - PULL_T, zz - 0.15, zz + 0.15)
        else:
            self.run_box("nickel", run, face, a - h, a + h, PULL_OFF - PULL_T, PULL_OFF, z - t, z + t)
            for aa in (a - h + 0.5, a + h - 0.5):
                self.run_box("nickel", run, face, aa - 0.15, aa + 0.15, 0, PULL_OFF - PULL_T, z - 0.15, z + 0.15)

    def door(self, run, face, a0, a1, z0, z1, frame=2.25):
        """Shaker door: a recessed flat panel inside a raised frame."""
        a0, a1, z0, z1 = a0 + GAP, a1 - GAP, z0 + GAP, z1 - GAP
        self.run_box("oak", run, face, a0, a1, 0, DOOR_T - 0.25, z0, z1)
        for s0, s1, t0, t1 in ((a0, a0 + frame, z0, z1), (a1 - frame, a1, z0, z1),
                               (a0 + frame, a1 - frame, z0, z0 + frame),
                               (a0 + frame, a1 - frame, z1 - frame, z1)):
            self.run_box("oak", run, face, s0, s1, DOOR_T - 0.25, DOOR_T, t0, t1)

    def drawer(self, run, face, a0, a1, z0, z1):
        a0, a1, z0, z1 = a0 + GAP, a1 - GAP, z0 + GAP, z1 - GAP
        self.run_box("oak", run, face, a0, a1, 0, DOOR_T, z0, z1, bevel=0.12)


# --- build ----------------------------------------------------------------------------

def _base(k):
    # carcasses: north run owns the corner
    # west run carcass; under the sink its top drops below the bowls
    s0, s1 = BASE[2][1], BASE[2][2]
    k.box("oak", X0, WEST_FACE, Y0, s0, TOE_H, BASE_H)
    k.box("oak", X0, WEST_FACE, s0, s1, TOE_H, BASE_H + TOP_T - SINK["depth"] - 0.6)
    k.box("oak", WEST_FACE - 0.75, WEST_FACE, s0, s1, TOE_H, BASE_H)   # face frame
    k.box("oak", X0, WEST_FACE, s1, NORTH_FACE, TOE_H, BASE_H)
    k.box("oak", X0, RANGE_X[0], NORTH_FACE, Y1, TOE_H, BASE_H)          # north run, corner-56
    k.box("oak", RANGE_X[1], FRIDGE_X[0], NORTH_FACE, Y1, TOE_H, BASE_H)
    # toe kicks
    k.box("toe", X0, WEST_FACE - TOE_D, Y0, NORTH_FACE - TOE_D, 0, TOE_H)
    k.box("toe", X0, RANGE_X[0], NORTH_FACE + TOE_D, Y1, 0, TOE_H)
    k.box("toe", RANGE_X[1], FRIDGE_X[0], NORTH_FACE + TOE_D, Y1, 0, TOE_H)
    dz0, dz1 = TOE_H, BASE_H
    drawer_z = BASE_H - 6.5
    for run, a0, a1, kind, cols in BASE:
        face = WEST_FACE if run == "W" else NORTH_FACE
        if kind == "filler":
            continue
        if kind == "dishwasher":
            k.run_box("white", run, face, a0 + GAP, a1 - GAP, 0, DOOR_T, dz0 + GAP, drawer_z - GAP, bevel=0.2)
            k.run_box("panel_black", run, face, a0 + GAP, a1 - GAP, 0, DOOR_T, drawer_z + GAP, dz1 - GAP)
            k.run_box("white", run, face, a0 + 3, a1 - 3, DOOR_T, DOOR_T + 1.0, drawer_z - 2.6, drawer_z - 1.6)
            continue
        w = (a1 - a0) / cols
        for c in range(cols):
            c0, c1 = a0 + c * w, a0 + (c + 1) * w
            k.drawer(run, face, c0, c1, drawer_z, dz1)       # sink: tilt-out false fronts
            k.door(run, face, c0, c1, dz0, drawer_z)
            mid = (c0 + c1) / 2
            if kind != "sink":
                k.pull(run, face, mid, (drawer_z + dz1) / 2, vertical=False)
            if cols == 1:
                pa = c1 - 1.6
            else:
                pa = c1 - 1.6 if c == 0 else c0 + 1.6
            k.pull(run, face, pa, drawer_z - 3.5, vertical=True)


def _counter(k):
    z0, z1 = BASE_H, BASE_H + TOP_T
    sx0, sx1 = SINK["x"]
    by0, by1 = SINK["bowls"][0][0], SINK["bowls"][-1][1]
    ox = X0 + OVERHANG_D
    # west run, split around the sink hole
    k.box("counter", X0, ox, Y0, by0, z0, z1)
    k.box("counter", X0, ox, by1, Y1 - OVERHANG_D, z0, z1)
    k.box("counter", X0, sx0, by0, by1, z0, z1)
    k.box("counter", sx1, ox, by0, by1, z0, z1)
    # north run: corner to the range, range to the fridge
    k.box("counter", X0, RANGE_X[0], Y1 - OVERHANG_D, Y1, z0, z1)
    k.box("counter", RANGE_X[1], FRIDGE_X[0], Y1 - OVERHANG_D, Y1, z0, z1)
    # backsplash
    k.box("counter", X0, X0 + SPLASH_T, Y0, Y1 - SPLASH_T, z1, z1 + SPLASH_H)
    k.box("counter", X0, RANGE_X[0], Y1 - SPLASH_T, Y1, z1, z1 + SPLASH_H)
    k.box("counter", RANGE_X[1], FRIDGE_X[0], Y1 - SPLASH_T, Y1, z1, z1 + SPLASH_H)
    # sink base: carcass top sits below the bowls
    return z1


def _sink(k, top):
    rx0, rx1, ry0, ry1 = SINK["rim"]
    sx0, sx1 = SINK["x"]
    rim = 0.12
    b0, b1 = SINK["bowls"]
    # rim frame and divider
    k.box("steel", rx0, sx0, ry0, ry1, top, top + rim)
    k.box("steel", sx1, rx1, ry0, ry1, top, top + rim)
    k.box("steel", sx0, sx1, ry0, b0[0], top, top + rim)
    k.box("steel", sx0, sx1, b1[1], ry1, top, top + rim)
    k.box("steel", sx0, sx1, b0[1], b1[0], top, top + rim)
    t = 0.08
    zb = top - SINK["depth"]
    for y0, y1 in (b0, b1):
        k.box("steel", sx0, sx0 + t, y0, y1, zb, top)
        k.box("steel", sx1 - t, sx1, y0, y1, zb, top)
        k.box("steel", sx0, sx1, y0, y0 + t, zb, top)
        k.box("steel", sx0, sx1, y1 - t, y1, zb, top)
        k.box("steel", sx0, sx1, y0, y1, zb - t, zb)
        cy, cx = (y0 + y1) / 2, (sx0 + sx1) / 2
        k.box("drain", cx - 1.6, cx + 1.6, cy - 1.6, cy + 1.6, zb, zb + 0.05)
    # faucet: base, gooseneck, lever
    k.b.cylinder("nickel", _p(FAUCET_X, FAUCET_Y, top + rim + 0.5), m(1.1), m(1.0), segments=10)
    path = common.smooth_path([_p(FAUCET_X, FAUCET_Y, top + rim + 0.8), _p(FAUCET_X, FAUCET_Y, top + 9.5),
                               _p(FAUCET_X + 2.5, FAUCET_Y, top + 12.0), _p(FAUCET_X + 6.5, FAUCET_Y, top + 11.0),
                               _p(FAUCET_X + 8.0, FAUCET_Y, top + 8.0)], samples=3)
    k.b.sweep("nickel", path, common.circle_profile(m(0.45), 8), up=(0, 1, 0))
    k.box("nickel", FAUCET_X - 0.3, FAUCET_X + 0.3, FAUCET_Y + 1.0, FAUCET_Y + 4.0, top + 4.0, top + 4.6)


def _uppers(k):
    for run, a0, a1, z0, z1, doors, hinge in UPPER:
        wall = X0 if run == "W" else Y1
        face = wall + UP_D if run == "W" else wall - UP_D
        if run == "W":
            k.box("oak", X0, X0 + UP_D, a0, a1, z0, z1)
        else:
            k.box("oak", a0 if a0 > X0 + UP_D else X0, a1, Y1 - UP_D, Y1, z0, z1)
        w = (a1 - a0) / doors
        for i in range(doors):
            d0, d1 = a0 + i * w, a0 + (i + 1) * w
            k.door(run, face, d0, d1, z0, z1)
            if hinge == "pair":
                if doors == 3 and i == 2:
                    pa = d0 + 1.6
                elif doors == 3 and i == 1:
                    pa = d0 + 1.6
                else:
                    pa = d1 - 1.6 if i % 2 == 0 else d0 + 1.6
            elif hinge == "lo":
                pa = d1 - 1.6
            else:
                pa = d0 + 1.6
            pz = z0 + 3.5 if z1 - z0 > 20 else z0 + (z1 - z0) / 2
            k.pull(run, face, pa, pz, vertical=True)
    # range hood under the short uppers
    hx0, hx1, hz0, hz1, hd = HOOD
    k.box("white", hx0 + 0.25, hx1 - 0.25, Y1 - hd, Y1, hz0, hz1)
    k.box("panel_black", hx0 + 1.0, hx1 - 1.0, Y1 - hd - 0.05, Y1 - hd + 3.0, hz0 - 0.05, hz0 + 0.02)


def build(coll):
    b = common.Builder(REGIONS)
    k = Kit(b)
    _base(k)
    top = _counter(k)
    _sink(k, top)
    _uppers(k)
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
