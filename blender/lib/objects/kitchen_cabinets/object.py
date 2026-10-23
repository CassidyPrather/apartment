"""Kitchen built-ins: honey-oak base cabinets on the west and north walls with a white
laminate countertop and backsplash, a double-bowl stainless sink with a gooseneck faucet,
upper wall cabinets (short over the sink and the microwave, a diagonal corner door) and
the cabinet over the fridge. The dishwasher, range, microwave and fridge are their own
packages; this one leaves their gaps.

The cabinets are hollow: side/back/floor/top panels with white melamine insides, an oak
face frame (centre stiles on the paired doors), white melamine shelves, worn/stained base
floors (the under-sink floor water-damaged), and the sink's disposal and drain under it.
Interior boxes and shelf heights come from interior.py (shared with the contents packages).

Objects (all in plan coordinates, see FRAME):
    kitchen_cabinets                      body: carcasses, face frames, shelves, counter,
                                          sink, plumbing, toe kicks, the sink false front
    kitchen_cabinets_door_<id>            one per door leaf (pull and hinge cups included),
                                          origin on the hinge axis (front face, hinge edge,
                                          door bottom); <id> per interior.py, pairs _l/_r
                                          (left/right seen from the room)
    kitchen_cabinets_door_<id>_out        empty 1 in in front of the leaf's face centre
    kitchen_cabinets_drawer_<id>          hollow drawer box + oak front + knob, origin at
                                          the drawer's centre (d1-d4, ed)
    kitchen_cabinets_drawer_<id>_grab     empty at the knob tip

Source of truth: scripted from the living-room/kitchen LiDAR survey (registered splat +
LiDAR points in plan inches), the survey photo crops (door and drawer layout, pulls) and
the 2026-10-23 inside photos (Reference/cupboards_drawers, sorted index 0-14: shelves,
hinge sides, white interiors, euro hinges, drawer boxes).

FRAME: PLAN COORDINATES. The object origin is plan (0, 0, 0) (the living room's SW
interior corner at floor level): object X = plan x, object Y = plan y, in metres. Place it
at the plan origin with no rotation (like window_units). West run fronts face +X, north
run fronts face -Y. Leaves and drawers carry their own origins but stay in the same frame.

Provenance tags: SCAN = measured on the registered survey points, PHOTO = counted or
proportioned from the survey crops / inside photos, EST = standard size or guess.

Verification hook: KC_OPEN_TEST=1 in the environment swings every leaf 100 degrees and pulls
every drawer out after texturing (render-only checks; never export with it set).
"""

import math
import os

import mathutils
from mathutils import Vector

import common
import interior as I

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
FRAME_T = I.FRAME_T     # EST 3/4 in oak face frame behind the doors
PANEL = I.PANEL         # EST 1/2 in carcass sides/back
FLOOR_T = I.FLOOR_T     # EST 3/4 in cabinet floor
STILE = 1.5             # PHOTO face-frame stile/rail width (photos 0-8)
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
BANK_EDGES = [CARC_Z, 28.5, 20.5, 12.5, TOE_H]   # PHOTO four-drawer bank front edges (short top drawer)
DRAWER_BOX_Y1 = I.DRAWER_BACK_Y  # EST drawer box back (21.25 in deep boxes)

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
# (id, a0, a1, z0, [(leaf id, hinge end "lo"/"hi" along the run)])  PHOTO (inside photos 0-6,
# survey crops 004158/004251: both north-run doors left of the microwave pull on their east edge)
W_UP = [
    ("wu1", 189.0, 214.0, UP_Z[0], [("wu1_l", "lo"), ("wu1_r", "hi")]),   # photo 0: pair, centre stile
    ("wu2", 214.0, 246.0, SINK_UP_Z0, [("wu2_l", "lo"), ("wu2_r", "hi")]),  # photo 1
    ("wu3", 246.0, 264.0, UP_Z[0], [("wu3", "hi")]),                     # photo 2: hinged north
]
CORNER = ((13.0, 264.0), (22.0, 273.0))   # PHOTO/EST 45-degree corner door face (photo 3: hinged SW end)
N_UP = [
    ("nu1", 22.0, 49.5, UP_Z[0], [("nu1_l", "lo"), ("nu1_r", "lo")]),    # photo 4: two bays, both hinged west
    ("nu2", 49.5, 79.5, MW_UP_Z0, [("nu2_l", "lo"), ("nu2_r", "hi")]),   # photo 5: pair, centre stile
    ("nu3", 79.5, 98.0, UP_Z[0], [("nu3", "hi")]),                       # photo 6: hinged east
]
FRIDGE_UP = (99.0, 134.0, 268.0, 84.0, 97.5)   # SCAN x0, x1, front y (splat/photos 004358, 004011: ~267-270), z0, z1 (to the wall)
PULL_L, PULL_W, PULL_T, PULL_OFF = 6.3, 0.45, 0.28, 1.15   # PHOTO brushed-nickel bow pulls: a flat bar
                                                # arching off the door on two feet (EST 128 mm centres)
KNOB_R, KNOB_L = 0.62, 1.0                      # PHOTO mushroom drawer knobs (EST 1.25 in)
CUP_IN = 1.9            # EST euro hinge cup centre from the door's hinge edge (photos 0-8)

NAME = "kitchen_cabinets"
ATLAS = {
    "name": "kitchen_cabinets",
    "size": 1024,
    "regions": {
        "oak": (0, 0, 1024, 640),
        "counter": (0, 640, 256, 384),
        "melamine": (256, 640, 128, 128),
        "drawer": (384, 640, 128, 128),
        "floor_stain": (256, 768, 128, 256),
        "floor_water": (384, 768, 128, 256),
        "steel": (512, 640, 256, 192),
        "nickel": (768, 640, 128, 128),
        "toe": (896, 640, 128, 128),
        "oak_dark": (768, 768, 128, 128),
        "panel_black": (896, 768, 128, 128),
        "drain": (512, 832, 128, 128),
        "pvc": (512, 960, 128, 64),
        "oak_edge": (640, 832, 128, 192),
        "oak_worn": (768, 896, 256, 128),
    },
}
REGIONS = list(ATLAS["regions"])
WORN = ("oak_edge", "oak_worn", "floor_stain", "floor_water")   # island-mapped: each piece gets the whole painted image
MATERIALS = {"kitchen_cabinets": {"atlas": "kitchen_cabinets", "mode": "opaque", "tiled": False}}
COLLIDER = "mesh"       # body; CabinetSetup strips colliders from the moving leaves/drawers
STATIC = True
# (name, azimuth, elevation, distance scale); az 0 = from the south. Match the survey crops.
VIEWS = [("from_dining_se", 30, 18, 0.75), ("from_dining_s", 8, 20, 0.7),
         ("from_dining_e", 65, 18, 0.7), ("uppers", 5, 2, 0.7),
         ("close_base", 45, 25, 0.35)]


# --- geometry helpers ---------------------------------------------------------------

def _p(x, y, z):
    return (m(x), m(y), m(z))


class Kit:
    """Builds in run coordinates: a along the run, d outward from `face` toward the room
    (W: x = face + d, a = y; N: y = face - d, a = x; C: the corner's local frame `cmx`)."""

    def __init__(self, b, cmx=None):
        self.b = b
        self.cmx = cmx

    def box(self, region, x0, x1, y0, y1, z0, z1, bevel=0.0):
        return self.b.box(region, _p(min(x0, x1), min(y0, y1), min(z0, z1)),
                          _p(max(x0, x1), max(y0, y1), max(z0, z1)), bevel=m(bevel))

    def rbox(self, region, run, face, a0, a1, d0, d1, z0, z1, bevel=0.0):
        """Box in run coordinates: a along the wall, d outward from `face` (toward the room)."""
        if run == "W":
            return self.box(region, face + d0, face + d1, a0, a1, z0, z1, bevel)
        if run == "N":
            return self.box(region, a0, a1, face - d0, face - d1, z0, z1, bevel)
        return self.b.box(region, _p(min(a0, a1), -max(d0, d1), min(z0, z1)),
                          _p(max(a0, a1), -min(d0, d1), max(z0, z1)), bevel=m(bevel), matrix=self.cmx)

    def _out(self, run):
        if run == "W":
            return Vector((1, 0, 0))
        if run == "N":
            return Vector((0, -1, 0))
        return (self.cmx.to_3x3() @ Vector((0, -1, 0))).normalized()

    def _pt(self, run, face, a, d, z):
        if run == "W":
            return Vector(_p(face + d, a, z))
        if run == "N":
            return Vector(_p(a, face - d, z))
        return self.cmx @ Vector(_p(a, -d, z))

    def pull(self, run, face, a, z):
        """Bow pull: a flat bar arching off the door face on two feet (vertical)."""
        h = PULL_L / 2
        pts = [(a, DOOR_T - 0.05, z - h), (a, DOOR_T + PULL_OFF - PULL_T / 2, z - h + 0.9),
               (a, DOOR_T + PULL_OFF - PULL_T / 2, z + h - 0.9), (a, DOOR_T - 0.05, z + h)]
        path = common.smooth_path([self._pt(run, face, *p) for p in pts], samples=2)
        self.b.sweep("nickel", path, common.rect_profile(m(PULL_W), m(PULL_T)), up=tuple(self._out(run)))

    def knob(self, run, face, a, z):
        """Mushroom knob: a short neck flaring to a domed cap (lathe, 10 sides)."""
        c = self._pt(run, face, a, DOOR_T, z)
        ax = self._out(run)
        up = Vector((0, 0, 1))
        side = up.cross(ax).normalized()
        rings = [(0.0, 0.3), (0.35, 0.22), (0.55, 0.5), (0.72, KNOB_R), (0.9, 0.56), (KNOB_L, 0.34)]
        n = 10
        bm = self.b.bm
        vs = []
        for d, r in rings:
            vs.append([bm.verts.new(c + ax * m(d) + (side * math.cos(2 * math.pi * i / n)
                                                     + up * math.sin(2 * math.pi * i / n)) * m(r)) for i in range(n)])
        faces = []
        for r0, r1 in zip(vs, vs[1:]):
            for i in range(n):
                faces.append(bm.faces.new((r0[i], r0[(i + 1) % n], r1[(i + 1) % n], r1[i])))
        faces.append(bm.faces.new(vs[-1]))
        faces.append(bm.faces.new(list(reversed(vs[0]))))     # closed, so normals orient outward
        self.b._tag(faces, "nickel")

    def door(self, run, face, a0, a1, z0, z1, frame=2.0, worn=None):
        """Shaker door: a recessed flat panel inside a raised frame. worn="lo"/"hi" paints
        the stile carrying the pull with the worn-finish image (base doors, as in the photos)."""
        a0, a1, z0, z1 = a0 + GAP, a1 - GAP, z0 + GAP, z1 - GAP
        self.rbox("oak", run, face, a0, a1, 0, DOOR_T - 0.25, z0, z1)
        for s0, s1, t0, t1 in ((a0, a0 + frame, z0, z1), (a1 - frame, a1, z0, z1),
                               (a0 + frame, a1 - frame, z0, z0 + frame),
                               (a0 + frame, a1 - frame, z1 - frame, z1)):
            region = "oak"
            if worn and t1 - t0 == z1 - z0 and ((worn == "lo") == (s0 == a0)):
                region = "oak_edge"
            self.rbox(region, run, face, s0, s1, DOOR_T - 0.25, DOOR_T, t0, t1)

    def drawer_front(self, run, face, a0, a1, z0, z1):
        self.rbox("oak_worn", run, face, a0 + GAP, a1 - GAP, 0, DOOR_T, z0 + GAP, z1 - GAP, bevel=0.12)

    def panel(self, region_in, run, face, a0, a1, d0, d1, z0, z1, inward, region_out="oak_dark"):
        """A closed carcass panel: `region_out` everywhere except the face(s) whose normal
        points along `inward` (a world-space direction into the cabinet): `region_in`."""
        faces = self.rbox(region_out, run, face, a0, a1, d0, d1, z0, z1)
        self.b.bm.normal_update()
        idx = self.b.idx(region_in)
        for f in faces:
            if f.is_valid and f.normal.dot(inward) > 0.9:
                f.material_index = idx
        return faces

    def frame(self, run, face, a0, a1, z0, z1, stiles, rails, region="oak"):
        """Oak face frame in the plane just behind the doors (d -FRAME_T..0): full-height
        stiles [(s0, s1)] and rails [(t0, t1)] between a0 and a1."""
        for s0, s1 in stiles:
            self.rbox(region, run, face, s0, s1, -FRAME_T, 0, z0, z1)
        # rails only between the stiles: overlapping coplanar faces flicker (z-fighting)
        segs = [(a0, a1)]
        for s0, s1 in stiles:
            segs = [(p, q) for u, v in segs for p, q in ((u, min(v, s0)), (max(u, s1), v)) if q - p > 1e-3]
        for t0, t1 in rails:
            for u, v in segs:
                self.rbox(region, run, face, u, v, -FRAME_T, 0, t0, t1)

    def hinge_plate(self, run, face, a_stile_in, toward, z):
        """Static euro-hinge mounting plate on the inner edge of the hinge-side stile."""
        s = 1 if toward > 0 else -1
        self.rbox("nickel", run, face, a_stile_in, a_stile_in + s * 0.14, -FRAME_T + 0.05, -0.08,
                  z - 1.25, z + 1.25)


def _vec_a(run):
    return Vector((0, 1, 0)) if run == "W" else Vector((1, 0, 0))


def marker(coll, name, loc):
    import bpy
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.03
    ob.location = loc
    coll.objects.link(ob)
    return ob


# --- moving parts -------------------------------------------------------------------

def _leaf(coll, objs, body_kit, lid, run, face, a0, a1, z0, z1, hinge, pull_z, worn=False,
          stile_in=None, cmx=None):
    """One door leaf as its own object. a0..a1 / z0..z1 is the door's section (GAP is taken
    off inside); hinge "lo"/"hi" is the hinged end. stile_in: the a of the hinge-side stile's
    inner edge (where the static hinge plate sits)."""
    b = common.Builder(REGIONS)
    k = Kit(b, cmx)
    worn_side = ("hi" if hinge == "lo" else "lo") if worn else None
    k.door(run, face, a0, a1, z0, z1, worn=worn_side)
    s = 1 if hinge == "lo" else -1                      # from the hinge edge toward the pull
    ha = a0 + GAP if hinge == "lo" else a1 - GAP
    pa = a1 - 1.6 if hinge == "lo" else a0 + 1.6
    k.pull(run, face, pa, pull_z)
    # concealed hinges: a cup let into the back of the door and the arm reaching back to the
    # plate on the face-frame stile (small nickel boxes)
    zs = (z0 + GAP + 3.0, z1 - GAP - 3.0)
    if z1 - z0 > 40:                                    # the tall uppers have three (photos 0, 2, 3)
        zs = zs + ((z0 + z1) / 2,)
    ca = ha + s * CUP_IN
    for hz in zs:
        k.rbox("nickel", run, face, ca - 0.75, ca + 0.75, -0.12, 0.02, hz - 0.95, hz + 0.95)
        k.rbox("nickel", run, face, ca - 0.3 - s * 0.2, ca + 0.3 - s * 0.2, -FRAME_T + 0.08, -0.1,
               hz - 0.5, hz + 0.5)
        if stile_in is not None:
            body_kit.hinge_plate(run, face, stile_in, s, hz)
    origin = k._pt(run, face, ha, DOOR_T, z0 + GAP)
    ob = b.to_object(f"{NAME}_door_{lid}", coll, origin=tuple(origin))
    objs.append(ob)
    out = k._pt(run, face, (a0 + a1) / 2, DOOR_T + 1.0, (z0 + z1) / 2)
    objs.append(marker(coll, f"{NAME}_door_{lid}_out", tuple(out)))
    return ob


def _drawer(coll, objs, did, a0, a1, fz0, fz1, knob_z):
    """North-run drawer: oak front, knob and an open-top melamine box (inside per interior.py)."""
    b = common.Builder(REGIONS)
    k = Kit(b)
    nc = N_FACE
    k.drawer_front("N", nc, a0, a1, fz0, fz1)
    ka = (a0 + a1) / 2
    k.knob("N", nc, ka, knob_z)
    d = I.DRAWERS[did]
    (ix0, ix1), (iy0, iy1), (iz0, iz1) = d["x"], d["y"], d["z"]
    sd, bt = I.DRAWER_SIDE, I.DRAWER_BOTTOM
    x0, x1, y0, y1, z0 = ix0 - sd, ix1 + sd, iy0 - sd, iy1 + sd, iz0 - bt
    k.box("drawer", x0, x1, y0, iy0, z0, iz1)              # sub-front (behind the oak front)
    k.box("drawer", x0, ix0, iy0, iy1, z0, iz1)            # sides
    k.box("drawer", ix1, x1, iy0, iy1, z0, iz1)
    k.box("drawer", x0, x1, iy1, y1, z0, iz1)              # back
    k.box("drawer", ix0, ix1, iy0, iy1, z0, iz0)           # bottom
    # metal runners low on the sides
    for xa, xb in ((x0 - 0.45, x0), (x1, x1 + 0.45)):
        k.box("nickel", xa, xb, y0 + 0.5, y1 - 0.3, z0 + 0.3, z0 + 1.2)
    origin = _p((a0 + a1) / 2, (nc - DOOR_T + y1) / 2, (fz0 + fz1) / 2)
    ob = b.to_object(f"{NAME}_drawer_{did}", coll, origin=origin)
    objs.append(ob)
    objs.append(marker(coll, f"{NAME}_drawer_{did}_grab", tuple(k._pt("N", nc, ka, DOOR_T + KNOB_L, knob_z))))
    return ob


# --- base run -----------------------------------------------------------------------

def _carcass(k, run, face, a0, a1, depth, z0, z1, floor_region="melamine", top=True,
             sides=(True, True), back=True):
    """Hollow carcass between a0..a1, from the back wall (d = -depth) to the face frame
    (d = -FRAME_T): back, sides, floor (z0..z0+FLOOR_T) and optional top (z1-PANEL..z1)."""
    out = k._out(run)
    av = _vec_a(run)
    up = Vector((0, 0, 1))
    df = -FRAME_T
    if back:
        k.panel("melamine", run, face, a0, a1, -depth, -depth + PANEL, z0, z1, out)
    if sides[0]:
        k.panel("melamine", run, face, a0, a0 + PANEL, -depth, df, z0, z1, av)
    if sides[1]:
        k.panel("melamine", run, face, a1 - PANEL, a1, -depth, df, z0, z1, -av)
    k.panel(floor_region, run, face, a0, a1, -depth, df, z0, z0 + FLOOR_T, up)
    if top:
        k.panel("melamine", run, face, a0, a1, -depth, df, z1 - PANEL, z1, -up)


def _shelf(k, run, face, a0, a1, depth, s, shelf_depth=None):
    d1 = -FRAME_T - I.FRONT_SETBACK
    d0 = -depth + PANEL
    if shelf_depth:
        d1 = d0 + shelf_depth
    k.rbox("melamine", run, face, a0, a1, d0, d1, s - I.SHELF_T, s)


def _base(k, coll, objs):
    wc = W_FACE     # west face-frame front (doors sit on it)
    nc = N_FACE     # north face-frame front
    wd = wc - WW    # west base depth to the wall
    nd = NW - nc
    s0, s1 = SINK_BASE_Y
    z0, dz0, dz1 = TOE_H, DRAWER_Z[0], DRAWER_Z[1]
    up = Vector((0, 0, 1))
    # fillers that stay solid: at the stub wall, the dishwasher's side panel
    k.box("oak_dark", WW, wc, STUB_Y, DW_Y[0], TOE_H, CARC_Z)
    k.box("oak", wc, wc + DOOR_T, STUB_Y, DW_Y[0] - GAP, TOE_H, CARC_Z)
    k.box("oak_dark", WW, wc, DW_Y[1] - 0.5, s0, TOE_H, CARC_Z)
    # toe kicks
    k.box("toe", WW, wc - TOE_D, STUB_Y, DW_Y[0], 0, TOE_H)
    k.box("toe", WW, wc - TOE_D, DW_Y[1], nc + TOE_D, 0, TOE_H)
    k.box("toe", WW, RANGE_X[0], nc + TOE_D, NW, 0, TOE_H)
    k.box("toe", RANGE_X[1], N_X1, nc + TOE_D, NW, 0, TOE_H)
    k.box("oak", N_X1 - 0.5, N_X1, nc - DOOR_T, NW, TOE_H, CARC_Z)   # finished end panel

    # --- sink base (photo 7): hollow, water-damaged floor, centre stile, no top
    mid = (s0 + s1) / 2
    _carcass(k, "W", wc, s0, s1, wd, z0, CARC_Z, floor_region="floor_water", top=False)
    k.frame("W", wc, s0, s1, z0, CARC_Z, [(s0, s0 + STILE), (mid - 0.75, mid + 0.75), (s1 - 1.5, s1 + 0.5)],
            [(z0, z0 + STILE), (dz0 - 1.25, CARC_Z)])
    k.drawer_front("W", wc, s0, s1, dz0, dz1)                 # fixed false front
    for lid, a0, a1, hinge, st in (("sink_l", s0, mid, "lo", s0 + STILE), ("sink_r", mid, s1, "hi", s1 - 1.5)):
        _leaf(coll, objs, k, lid, "W", wc, a0, a1, z0, dz0, hinge, dz0 - 4.0, worn=True, stile_in=st)

    # --- west single door next to the corner (no inside photo): one shelf
    a0, a1 = W_DOOR_Y
    _carcass(k, "W", wc, a0, a1, wd, z0, CARC_Z, floor_region="floor_stain", top=False, sides=(True, False))
    k.rbox("melamine", "W", wc, a1 - PANEL, a1 + FRAME_T, -wd + PANEL, -FRAME_T, z0, CARC_Z)   # also closes the blind corner
    k.frame("W", wc, s1 + 0.5, a1, z0, CARC_Z, [(a1 - STILE, a1)],
            [(z0, z0 + STILE), (CARC_Z - 2.0, CARC_Z)])
    for s in I.CABINETS["wb"]["shelves"]:
        _shelf(k, "W", wc, a0 + PANEL, a1 - PANEL, wd, s)
    # hinged on the south (sink) side: survey frames 003812 / kitchen_base_west_3 show no pull on
    # its south stile and the pull up by the inside corner (the old model had it the other way)
    _leaf(coll, objs, k, "wb", "W", wc, a0, a1, z0, dz1, "lo", dz1 - 4.5, worn=True, stile_in=s1 + 0.5)

    # --- north blind corner (photo 8): door x 25.5-36.5, L-shaped shelf
    cx0, cx1 = WW, 36.25
    av = _vec_a("N")
    k.panel("melamine", "N", nc, cx0, cx1, -nd, -nd + PANEL, z0, CARC_Z, Vector((0, -1, 0)))       # back
    k.panel("melamine", "N", nc, cx0, cx0 + PANEL, -nd, -FRAME_T, z0, CARC_Z, av)                  # west wall side
    k.panel("melamine", "N", nc, cx1 - PANEL, cx1, -nd, -FRAME_T, z0, CARC_Z, -av)                 # to the drawers
    k.panel("floor_stain", "N", nc, cx0, cx1, -nd, -FRAME_T, z0, z0 + FLOOR_T, up)
    # the blind part's front (behind the west run's door) is closed by the west cabinet's side
    k.frame("N", nc, wc - FRAME_T, cx1, z0, CARC_Z, [(wc - FRAME_T, 26.5), (35.5, 37.25)],
            [(z0, z0 + STILE), (CARC_Z - 2.0, CARC_Z)])
    sp = I.CABINETS["corner"]["shelf_poly"]
    for s in I.CABINETS["corner"]["shelves"]:
        k.b.prism("melamine", [_p(x, y, 0)[:2] for x, y in sp], m(s - I.SHELF_T), m(s))
    a0, a1 = N_CORNER_DOOR
    _leaf(coll, objs, k, "corner", "N", nc, a0, a1, z0, dz1, "lo", dz1 - 4.5, worn=True, stile_in=26.5)

    # --- four-drawer bank (photos 9-12)
    a0, a1 = N_DRAWERS
    _carcass(k, "N", nc, cx1, RANGE_X[0], nd, z0, CARC_Z, top=False, sides=(False, True))
    rails = [(z0, z0 + 0.9), (11.75, 12.75), (19.75, 20.75), (27.6, 28.9), (CARC_Z - 0.75, CARC_Z)]
    k.frame("N", nc, 37.25, RANGE_X[0], z0, CARC_Z, [(48.75, RANGE_X[0])], rails)
    for (zt, zb), did in zip(zip(BANK_EDGES, BANK_EDGES[1:]), ("d1", "d2", "d3", "d4")):
        _drawer(coll, objs, did, a0, a1, zb, zt, (zb + zt) / 2 + (1.0 if zt < dz1 else 0.0))

    # --- east of the range (photos 13, 14): drawer over a door with one shelf
    a0, a1 = N_EAST
    _carcass(k, "N", nc, a0, a1 - 0.5, nd, z0, CARC_Z, floor_region="floor_stain", top=False,
             sides=(True, False))
    eb = I.CABINETS["eb"]
    k.rbox("melamine", "N", nc, a0 + PANEL, a1 - 0.5, -nd + PANEL, -FRAME_T, eb["z"][1], eb["z"][1] + 0.75)   # drawer deck
    k.rbox("melamine", "N", nc, a1 - 0.56, a1 - 0.5, -nd + PANEL, -FRAME_T, z0, CARC_Z)   # white inside the end panel
    k.frame("N", nc, a0, a1 - 0.5, z0, CARC_Z, [(a0, 80.75), (98.75, a1 - 0.5)],
            [(z0, z0 + STILE), (26.25, 27.5), (CARC_Z - 0.75, CARC_Z)])
    for s in eb["shelves"]:
        _shelf(k, "N", nc, a0 + PANEL, a1 - 0.5, nd, s)
    _drawer(coll, objs, "ed", a0, a1, dz0, dz1, (dz0 + dz1) / 2)
    _leaf(coll, objs, k, "eb", "N", nc, a0, a1, z0, dz0, "hi", dz0 - 4.0, worn=True, stile_in=98.75)


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


def _rrect_polar(cx, cy, hx, hy, r, n=40):
    """Rounded rectangle sampled on n evenly spaced rays from its centre (counter-clockwise
    seen from above), so rings of different sizes share spokes and a circle can join them."""
    def inside(x, y):
        qx, qy = abs(x) - (hx - r), abs(y) - (hy - r)
        return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r <= 0.0
    pts = []
    for i in range(n):
        t = 2 * math.pi * (i + 0.5) / n
        dx, dy = math.cos(t), math.sin(t)
        lo, hi = 0.0, hx + hy
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inside(mid * dx, mid * dy) else (lo, mid)
        pts.append((cx + lo * dx, cy + lo * dy))
    return pts


def _face(b, region, verts, want):
    """New face, flipped if its normal disagrees with the direction `want`."""
    f = b.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(want) < 0:
        f.normal_flip()
    f.material_index = b.idx(region)
    return f


def _sink(k):
    """Double-bowl drop-in stainless sink (capture frames 003858/003853): rounded bowl
    corners, floors sloping to round strainer drains with a chrome flange."""
    b = k.b
    top = TOP_Z1
    rx0, rx1, ry0, ry1 = SINK_RIM
    bx0, bx1 = SINK_BX
    rim = 0.12
    R = 2.5                                   # PHOTO bowl corner radius at the rim
    zt = top + rim
    # rim deck: the rim rectangle with the two rounded bowl openings cut out, built as one
    # ring per opening joined to the outer edge by the deck strips between/around them
    k.box("steel", rx0, bx0, ry0, ry1, top, zt)
    k.box("steel", bx1, rx1, ry0, ry1, top, zt)
    k.box("steel", bx0, bx1, ry0, SINK_BOWLS[0][0], top, zt)
    k.box("steel", bx0, bx1, SINK_BOWLS[1][1], ry1, top, zt)
    k.box("steel", bx0, bx1, SINK_BOWLS[0][1], SINK_BOWLS[1][0], top, zt)
    up = Vector((0, 0, 1))
    zb = top - SINK_DEPTH
    for y0, y1 in SINK_BOWLS:
        cx, cy = (bx0 + bx1) / 2, (y0 + y1) / 2
        hx, hy = (bx1 - bx0) / 2, (y1 - y0) / 2
        axis = Vector(_p(cx, cy, 0))
        # deck around the opening: the square hole's edge to the rounded rim ring (one fan
        # per spoke to the nearest point on the square)
        ring = _rrect_polar(cx, cy, hx, hy, R)
        for (x0_, y0_), (x1_, y1_) in zip(ring, ring[1:] + ring[:1]):
            def onsq(x, y):
                dx, dy = x - cx, y - cy
                k_ = min(hx / abs(dx) if dx else 1e9, hy / abs(dy) if dy else 1e9)
                return cx + dx * k_, cy + dy * k_
            sa, sb = onsq(x0_, y0_), onsq(x1_, y1_)
            q = [b.bm.verts.new(_p(x0_, y0_, zt)), b.bm.verts.new(_p(x1_, y1_, zt)),
                 b.bm.verts.new(_p(sb[0], sb[1], zt)), b.bm.verts.new(_p(sa[0], sa[1], zt))]
            _face(b, "steel", q, up)
        # bowl walls: rim, just under the rim, near the floor (slightly drawn in), floor edge
        prof = [(zt, 0.0, R), (top - 0.6, 0.0, R), (zb + 1.2, 0.5, R + 0.3), (zb + 0.35, 0.9, R + 0.5)]
        rings = []
        for z, ins, rr in prof:
            rings.append([b.bm.verts.new(_p(x, y, z)) for x, y in _rrect_polar(cx, cy, hx - ins, hy - ins, rr)])
        m_ = len(rings[0])
        for r0, r1 in zip(rings, rings[1:]):
            for j in range(m_):
                q = [r0[j], r0[(j + 1) % m_], r1[(j + 1) % m_], r1[j]]
                mid = sum((v.co for v in q), Vector()) / 4
                _face(b, "steel", q, Vector((axis.x - mid.x, axis.y - mid.y, 0)).normalized())
        # floor sloping down to the drain; the drain: chrome flange ring, dark strainer basket
        dr, fl = 1.75, 0.45                    # EST 3.5 in strainer, chrome flange (photo)
        edge = rings[-1]
        angs = [math.atan2(v.co.y - axis.y, v.co.x - axis.x) for v in edge]   # same spokes as the bowl

        def circ(rad, z):
            return [b.bm.verts.new(_p(cx + rad * math.cos(t), cy + rad * math.sin(t), z)) for t in angs]
        flange_out = circ(dr + fl, zb + 0.04)
        flange_in = circ(dr, zb + 0.1)
        basket = circ(1.1, zb - 0.3)
        hole = circ(0.9, zb - 0.32)
        centre = b.bm.verts.new(_p(cx, cy, zb - 0.45))
        for j in range(m_):
            j2 = (j + 1) % m_
            _face(b, "steel", [edge[j], edge[j2], flange_out[j2], flange_out[j]], up)
            _face(b, "nickel", [flange_out[j], flange_out[j2], flange_in[j2], flange_in[j]], up)
            _face(b, "nickel", [flange_in[j], flange_in[j2], basket[j2], basket[j]], up)
            _face(b, "drain", [basket[j], basket[j2], hole[j2], hole[j]], up)
            _face(b, "drain", [hole[j], hole[j2], centre], up)


    # faucet: base, gooseneck arching out over the bowls, side lever
    fx, fy = FAUCET
    k.b.cylinder("nickel", _p(fx, fy, top + rim + 0.5), m(1.1), m(1.0), segments=10)
    path = common.smooth_path([_p(fx, fy, top + rim + 0.8), _p(fx, fy, top + 11.0),
                               _p(fx + 2.5, fy, top + 14.0), _p(fx + 6.5, fy, top + 13.0),
                               _p(fx + 8.0, fy, top + 9.5)], samples=3)
    k.b.sweep("nickel", path, common.circle_profile(m(0.5), 8), up=(0, 1, 0))
    k.box("nickel", fx - 0.3, fx + 0.3, fy + 1.0, fy + 4.0, top + 5.0, top + 5.6)




def _plumbing(k):
    """Under the sink (photo 7): a black disposal under the south bowl, its white waste arm
    across to the north bowl's black tailpiece and P-trap into the back wall, and two
    chrome supply stops with braided lines up to the faucet."""
    b = k.b
    dx = (SINK_BX[0] + SINK_BX[1]) / 2
    dy = sum(SINK_BOWLS[0]) / 2
    ny = sum(SINK_BOWLS[1]) / 2
    zb = TOP_Z1 - SINK_DEPTH                      # bowl floor (drain flange)
    b.cylinder("panel_black", _p(dx, dy, 21.0), m(3.3), m(11.0), segments=12)   # EST disposal body z 15.5-26.5
    b.cylinder("nickel", _p(dx, dy, zb - 0.95), m(1.9), m(1.1), segments=12)    # mounting ring
    b.cylinder("panel_black", _p(dx, dy, 15.3), m(2.4), m(0.5), segments=12)    # base cap
    pipe = common.circle_profile(m(0.75), 8)
    b.sweep("pvc", [_p(dx, dy + 3.1, 23.0), _p(dx, ny, 23.0)], pipe, up=(0, 0, 1))   # waste arm (white, photo 7)
    b.sweep("panel_black", [_p(dx, ny, zb - 0.4), _p(dx, ny, 19.5)], pipe, up=(0, 1, 0))  # tailpiece + tee
    b.cylinder("panel_black", _p(dx, ny, 23.0), m(1.0), m(2.2), segments=8)    # tee
    trap = common.smooth_path([_p(dx, ny, 19.5), _p(dx, ny, 16.6), _p(dx - 1.3, ny, 15.0),
                               _p(dx - 2.8, ny, 15.6), _p(dx - 3.4, ny, 17.6), _p(dx - 4.2, ny, 18.6),
                               _p(WW + 0.6, ny, 18.6)], samples=2)
    b.sweep("panel_black", trap, pipe, up=(0, 1, 0))
    b.cylinder("pvc", _p(WW + 0.6, ny, 18.6), m(1.4), m(0.25), axis="X", segments=10)   # wall escutcheon
    for sy in (226.0, 235.0):                                       # EST supply stops
        b.cylinder("nickel", _p(WW + 1.2, sy, 13.0), m(0.45), m(1.6), axis="X", segments=8)
        b.cylinder("nickel", _p(WW + 2.2, sy, 13.0), m(0.35), m(0.9), axis="Z", segments=8)
        line = common.smooth_path([_p(WW + 2.2, sy, 13.4), _p(WW + 2.6, sy, 20.0),
                                   _p(FAUCET[0] + 0.3, (sy + FAUCET[1]) / 2, 30.0),
                                   _p(FAUCET[0], FAUCET[1] + (sy - FAUCET[1]) * 0.1, TOP_Z0 - 0.05)], samples=2)
        b.sweep("nickel", line, common.circle_profile(m(0.2), 6), up=(1, 0, 0))


# --- uppers -------------------------------------------------------------------------

def _upper(k, coll, objs, cid, run, face, a0, a1, z0, z1, depth, leaves):
    """Hollow upper: carcass, face frame (centre stile on pairs), partitions, shelves, leaves."""
    _carcass(k, run, face, a0, a1, depth, z0, z1)
    mid = (a0 + a1) / 2
    stiles = [(a0, a0 + STILE), (a1 - STILE, a1)]
    if len(leaves) == 2:
        stiles.append((mid - 0.75, mid + 0.75))
    k.frame(run, face, a0, a1, z0, z1, stiles, [(z0, z0 + STILE), (z1 - 2.0, z1)])
    cab = I.CABINETS[cid]
    bays = [(a0 + PANEL, a1 - PANEL)]
    for p0, p1 in cab.get("partitions", []):
        k.rbox("melamine", run, face, p0, p1, -depth + PANEL, -FRAME_T, z0 + FLOOR_T, z1 - PANEL)
        bays = [bb for b0, b1 in bays for bb in ((b0, p0), (p1, b1)) if b0 < p0 < b1] or bays
    for s in cab["shelves"]:
        for b0, b1 in bays:
            _shelf(k, run, face, b0, b1, depth, s, cab.get("shelf_depth"))
    sections = [(a0, a1)] if len(leaves) == 1 else [(a0, mid), (mid, a1)]
    for (lid, hinge), (d0, d1) in zip(leaves, sections):
        if hinge == "lo":
            st = a0 + STILE if d0 == a0 else mid + 0.75
        else:
            st = a1 - STILE if d1 == a1 else mid - 0.75
        _leaf(coll, objs, k, lid, run, face, d0, d1, z0, z1, hinge, z0 + 3.5 + (PULL_L - 5.0) / 2,
              stile_in=st)


def _uppers(k, coll, objs):
    z1 = UP_Z[1]
    face_w = WW + UP_D - DOOR_T          # face-frame front (door back) plane
    for cid, y0, y1, z0, leaves in W_UP:
        _upper(k, coll, objs, cid, "W", face_w, y0, y1, z0, z1, face_w - WW, leaves)
    face_n = NW - UP_D + DOOR_T
    for cid, x0, x1, z0, leaves in N_UP:
        _upper(k, coll, objs, cid, "N", face_n, x0, x1, z0, z1, NW - face_n, leaves)
    # cabinet over the fridge: a box to the wall, a pair of short doors (no photo)
    x0, x1, fy, z0, z1f = FRIDGE_UP
    _upper(k, coll, objs, "fu", "N", fy + DOOR_T, x0, x1, z0, z1f, NW - fy - DOOR_T,
           [("fu_l", "lo"), ("fu_r", "hi")])
    _corner_upper(k, coll, objs)


def _corner_upper(k, coll, objs):
    """Diagonal corner cabinet (photo 3): pentagon carcass, 45-degree face frame and door
    (hinged at its SW end), three pentagon shelves."""
    (cx0, cy0), (cx1, cy1) = CORNER
    z0, z1 = UP_Z
    L = math.hypot(cx1 - cx0, cy1 - cy0)
    ang = math.atan2(cy1 - cy0, cx1 - cx0)
    mx = mathutils.Matrix.Translation(_p(cx0, cy0, 0)) @ mathutils.Matrix.Rotation(ang, 4, "Z")
    kc = Kit(k.b, mx)        # local frame: a along the face (0..L), d outward (local -Y)
    fo = FRAME_T * math.sqrt(2)          # floor/top stop at the back of the diagonal face frame
    outline = [_p(x, y, 0)[:2] for x, y in ((WW, cy0), (cx0 - fo, cy0), (cx1, cy1 + fo), (cx1, NW), (WW, NW))]
    k.b.prism("oak_dark", outline, m(z0), m(z0 + FLOOR_T), cap_region="melamine")
    k.b.prism("oak_dark", outline, m(z1 - PANEL), m(z1), bottom_region="melamine")
    zi0, zi1 = z0 + FLOOR_T, z1 - PANEL
    k.panel("melamine", "W", WW, cy0, NW, 0, PANEL, zi0, zi1, Vector((1, 0, 0)))            # west wall back
    k.panel("melamine", "N", NW, WW, cx1, 0, PANEL, zi0, zi1, Vector((0, -1, 0)))           # north wall back
    k.panel("melamine", "W", WW, cy0, cy0 + PANEL, PANEL, cx0 - 0.4, zi0, zi1, Vector((0, 1, 0)))   # south side
    k.panel("melamine", "W", WW, cy1 + 0.4, NW - PANEL, cx1 - PANEL, cx1, zi0, zi1, Vector((-1, 0, 0)))  # east side
    kc.frame("C", None, 0, L, z0, z1, [(0, 1.25), (L - 1.25, L)], [(z0, z0 + STILE), (z1 - 2.0, z1)])
    cab = I.CABINETS["cu"]
    for s in cab["shelves"]:
        k.b.prism("melamine", [_p(x, y, 0)[:2] for x, y in cab["poly"]], m(s - I.SHELF_T), m(s))
    _leaf(coll, objs, kc, "cu", "C", None, 0, L, z0, z1, "lo", z0 + 3.5 + (PULL_L - 5.0) / 2,
          stile_in=1.25, cmx=mx)


def build(coll):
    b = common.Builder(REGIONS)
    k = Kit(b)
    objs = []
    _base(k, coll, objs)
    _counter(k)
    _sink(k)
    _plumbing(k)
    _uppers(k, coll, objs)
    ob = b.to_object(NAME, coll)
    _face_bowls_up(ob)
    leaves = [o for o in objs if o.type == "MESH"]
    print("moving parts:", len(leaves), [o.name for o in leaves])
    return [ob] + objs


def _face_bowls_up(ob):
    """to_object() orients normals as if every piece were closed, which turns the open sink
    bowls inside out (Unity then culls them): face everything inside a bowl toward an eye
    above that bowl, then add a reversed copy just below so the bowls are solid seen from
    under the sink too."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    (bx0, bx1), zt = SINK_BX, TOP_Z1 + 0.12
    flip, bowl = [], []
    for f in bm.faces:
        c = f.calc_center_median()
        for y0, y1 in SINK_BOWLS:
            if m(bx0) - 1e-4 <= c.x <= m(bx1) + 1e-4 and m(y0) - 1e-4 <= c.y <= m(y1) + 1e-4 and m(TOP_Z1 - SINK_DEPTH - 0.6) <= c.z <= m(zt) + 1e-4:
                eye = Vector(_p((bx0 + bx1) / 2, (y0 + y1) / 2, TOP_Z1 + 10.0))
                if f.normal.dot(eye - c) < 0:
                    flip.append(f)
                bowl.append(f)
                break
    bmesh.ops.reverse_faces(bm, faces=flip)
    ret = bmesh.ops.duplicate(bm, geom=bowl)
    dup_f = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
    dup_v = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.reverse_faces(bm, faces=dup_f)
    for v in dup_v:                      # push the copy out of the bowl (not coplanar: no bake/z-fight)
        y0, y1 = min(SINK_BOWLS, key=lambda b: abs(m((b[0] + b[1]) / 2) - v.co.y))
        c = Vector(_p((bx0 + bx1) / 2, (y0 + y1) / 2, 0))
        r = Vector((v.co.x - c.x, v.co.y - c.y, 0))
        if r.length > 1e-6:
            r.normalize()
        v.co += r * m(0.08) + Vector((0, 0, -m(0.08)))
    bm.to_mesh(ob.data)
    bm.free()
    print("sink faces turned up:", len(flip), "underside copies:", len(dup_f))


def _island_uvs(ob, atlas, regions):
    """Per connected piece of each region, box-project every face onto the whole region
    rect using that piece's own bounds (so each drip pan, coil or handle gets the full
    painted image). Axes as common._axes (seen from outside, image up = +Z or +Y)."""
    me = ob.data
    names = [mm.name.split(".")[0] for mm in me.materials]
    uvl = me.uv_layers["UVMap"]
    for region in regions:
        ri = names.index(region)
        polys = [p for p in me.polygons if p.material_index == ri]
        parent = {}

        def find(a):
            parent.setdefault(a, a)
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for p in polys:
            r0 = find(p.vertices[0])
            for v in p.vertices[1:]:
                rv = find(v)
                if rv != r0:
                    parent[rv] = r0
        groups = {}
        for p in polys:
            groups.setdefault(find(p.vertices[0]), []).append(p)
        u0, v0, u1, v1 = common.uv_rect(atlas, region)
        for ps in groups.values():
            vids = {v for p in ps for v in p.vertices}
            rng = {}
            for p in ps:
                n = p.normal
                ax = max(range(3), key=lambda i: abs(n[i]))
                key = ("+" if n[ax] > 0 else "-") + "XYZ"[ax]
                ua, va = map(Vector, common._axes(key))
                if key not in rng:
                    us = [me.vertices[v].co.dot(ua) for v in vids]
                    vs = [me.vertices[v].co.dot(va) for v in vids]
                    rng[key] = (min(us), max(us) - min(us) or 1e-6, min(vs), max(vs) - min(vs) or 1e-6)
                umin, ur, vmin, vr = rng[key]
                for li in p.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    fu, fv = (co.dot(ua) - umin) / ur, (co.dot(va) - vmin) / vr
                    uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def _box_uvs(ob, lo, ext):
    """common.atlas_uvs' default box projection, but over the whole package's bounds in plan
    space, so the leaves and drawers get the same oak scale and grain as the body."""
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    me.uv_layers.active = uvl
    names = [mm.name.split(".")[0] for mm in me.materials]
    off = Vector(ob.location)
    for p in me.polygons:
        u0, v0, u1, v1 = common.uv_rect(ATLAS, names[p.material_index])
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        ua, va = [(1, 2), (0, 2), (0, 1)][ax]
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co + off
            fu = (co[ua] - lo[ua]) / max(ext[ua], 1e-6)
            fv = (co[va] - lo[va]) / max(ext[va], 1e-6)
            uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def texture(objs):
    meshes = [o for o in objs if o.type == "MESH"]
    pts = [v.co + Vector(o.location) for o in meshes for v in o.data.vertices]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    mat = common.atlas_material(NAME, ATLAS)
    for ob in meshes:
        _box_uvs(ob, lo, hi - lo)
        _island_uvs(ob, ATLAS, WORN)
        common.collapse_materials(ob, {r: mat for r in REGIONS})
    if os.environ.get("KC_OPEN_TEST"):
        _open_all(objs, os.environ["KC_OPEN_TEST"])


def _open_all(objs, which="1"):
    """Render-only check: swing each leaf 100 degrees toward its _out marker (as Unity's
    CabinetSetup does) and pull each drawer out 75% of its depth toward its _grab marker.
    which: "1" = everything, else comma-separated ids (e.g. "wb,corner,d1")."""
    import bpy
    names = {o.name: o for o in objs}
    ids = None if which == "1" else set(which.split(","))
    for ob in objs:
        if ob.type != "MESH" or ob is objs[0]:
            continue
        if ids is not None and ob.name.split("_door_")[-1].split("_drawer_")[-1] not in ids:
            continue
        verts = [v.co for v in ob.data.vertices]
        if "_door_" in ob.name:
            out = Vector(names[ob.name + "_out"].location)
            best = None
            for turn in (100.0, -100.0):
                rot = mathutils.Matrix.Rotation(math.radians(turn), 3, "Z")
                c = sum((rot @ v for v in verts), Vector()) / len(verts) + Vector(ob.location)
                c0 = sum(verts, Vector()) / len(verts) + Vector(ob.location)
                d = (c - c0).dot(out - c0)
                if best is None or d > best[0]:
                    best = (d, turn)
            ob.rotation_euler.z += math.radians(best[1])
        elif "_drawer_" in ob.name:
            g = Vector(names[ob.name + "_grab"].location) - Vector(ob.location)
            g.z = 0
            axis = Vector((0, math.copysign(1, g.y), 0)) if abs(g.y) > abs(g.x) else Vector((math.copysign(1, g.x), 0, 0))
            ys = [v.dot(axis) for v in verts]
            ob.location += axis * 0.75 * (max(ys) - min(ys))
    bpy.context.view_layer.update()
    print("KC_OPEN_TEST: leaves swung, drawers pulled")
