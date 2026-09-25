"""Window blinds: inside-mount vertical blinds in the three living-room windows (two on
the west wall, one wide one on the south wall), vanes hanging from a headrail at the top
of each recess to just above the sill, tilted as photographed.

Source of truth: scripted, openings from shell_layout.OPENINGS (read-only import).
Frame: PLAN coordinates, like window_units. Origin = plan (0, 0, 0) (the apartment's
interior south-west corner at floor level), +X east, +Y north, Z up, so the package goes on
a marker at (0, 0, 0) with no rotation. Each blind is built in a local (u, d, z) frame:
u along the opening, d depth measured inward from the wall's interior face (negative =
into the recess), z height above the floor.

Dimensions (inches):
  openings, sill 26.5, head 85        layout (M)
  vane width 3.5, pitch 3.0           EST (standard 3.5 in PVC vanes), count read from photos
  vane thickness 0.06                 EST
  headrail 1.25 tall x 2.0 deep       EST
  carrier line (vane centreline) d=-1.25 on the west wall, -1.75 on the south wall
                                      SCAN (LiDAR depth histogram through each recess)
  vane bottom 0.75 above the sill     EST (photos: vanes stop just above the stool)
  wand 0.35 thick, 30 long            EST
  tilt: west-south 15, west-north 45, south 12 degrees from closed  EST, read from photos
"""

import importlib
import math
import os
import sys

from mathutils import Matrix, Vector

import common

LIB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import shell_layout as L  # noqa: E402

importlib.reload(L)
m = L.m

NAME = "window_blinds"

Z0, Z1 = L.WINDOW_SILL, L.WINDOW_HEAD
VANE_W, VANE_PITCH, VANE_T = 3.5, 3.0, 0.06
RAIL_H, RAIL_D = 1.25, 2.0
BOTTOM_GAP = 0.75
WAND_T, WAND_L = 0.35, 30.0
END_GAP = 0.25

# (wall, a0, a1, carrier depth, tilt degrees)
BLINDS = [
    ("ext_west", 42.5, 77.25, -1.25, 15.0),
    ("ext_west", 101.75, 136.5, -1.25, 45.0),
    ("ext_south", 38.5, 108.5, -1.75, 12.0),
]
# The portable AC's hose goes out through window 2: its vanes part around it, the ones in
# the way pushed aside and bunched up either side (hose centre along the wall, half-gap).
HOSE_PARTS = {("ext_west", 101.75): (113.5, 4.5)}

REGIONS = ["vane", "rail", "carrier", "wand"]
ATLAS = {
    "name": "window_blinds",
    "size": 512,
    "regions": {
        "vane": (0, 0, 256, 512),
        "rail": (256, 0, 256, 256),
        "carrier": (256, 256, 128, 128),
        "wand": (384, 256, 128, 128),
    },
}
MATERIALS = {"window_blinds": {"atlas": "window_blinds", "mode": "opaque"}}
COLLIDER = "box"
STATIC = True
VIEWS = [("room_side", 60, 10, 0.55)]


def to_plan(wall, u, d, z):
    """Local (u, d, z) inches -> plan metres."""
    if wall == "ext_west":        # interior face x = 0, inward +X, u along +Y
        return Vector((m(d), m(u), m(z)))
    if wall == "ext_south":       # interior face y = 0, inward +Y, u along +X
        return Vector((m(u), m(d), m(z)))
    raise ValueError(wall)


def wall_box(b, region, wall, u, d, z, tilt=0.0):
    """Box (u0,u1),(d0,d1),(z0,z1) in the wall frame, rotated `tilt` deg about its own
    vertical centreline."""
    (u0, u1), (d0, d1), (z0, z1) = u, d, z
    cu, cd, cz = (u0 + u1) / 2, (d0 + d1) / 2, (z0 + z1) / 2
    lo = (-(u1 - u0) / 2, -(d1 - d0) / 2, -(z1 - z0) / 2)
    hi = tuple(-v for v in lo)
    # Build centred in (u, d, z), tilt about z, then map (u, d) onto the wall axes.
    c = to_plan(wall, cu, cd, cz)
    if wall == "ext_west":
        swap = Matrix(((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))   # u->Y, d->X
    else:
        swap = Matrix.Identity(4)
    mat = Matrix.Translation(c) @ swap @ Matrix.Rotation(math.radians(tilt), 4, "Z")
    b.box(region, tuple(m(v) for v in lo), tuple(m(v) for v in hi), matrix=mat)


def blind(b, wall, a0, a1, dc, tilt):
    u0, u1 = a0 + END_GAP, a1 - END_GAP
    zt = Z1
    wall_box(b, "rail", wall, (u0, u1), (dc - RAIL_D / 2, dc + RAIL_D / 2), (zt - RAIL_H, zt))
    # dark carrier slot along the rail's underside
    wall_box(b, "carrier", wall, (u0 + 0.5, u1 - 0.5), (dc - 0.3, dc + 0.3), (zt - RAIL_H - 0.3, zt - RAIL_H))
    n = int(round((u1 - u0 - VANE_W) / VANE_PITCH)) + 1
    pitch = (u1 - u0 - VANE_W) / (n - 1)
    zb, zv = Z0 + BOTTOM_GAP, zt - RAIL_H - 0.3
    part = HOSE_PARTS.get((wall, a0))
    for i in range(n):
        cu = u0 + VANE_W / 2 + i * pitch
        if part:
            g, half = part
            if abs(cu - g) < half + VANE_W / 2:
                # push aside to the nearer edge of the gap, stacked tight
                side = -1 if cu < g else 1
                k = abs(cu - g) // 1.0
                cu = g + side * (half + VANE_W / 2 + 0.5 + (half - k) * 0.4)
        # alternate a hair in depth so closed, overlapping vanes never z-fight
        dd = dc + (0.04 if i % 2 else -0.04)
        wall_box(b, "vane", wall, (cu - VANE_W / 2, cu + VANE_W / 2), (dd - VANE_T / 2, dd + VANE_T / 2),
                 (zb, zv), tilt=tilt)
    # tilt wand at the low-u end, room side of the vanes
    dw = dc + VANE_W / 2 * math.sin(math.radians(tilt)) + 0.6
    wall_box(b, "wand", wall, (u0 + 0.6, u0 + 0.6 + WAND_T), (dw, dw + WAND_T), (zv - WAND_L, zv))


def build(coll):
    b = common.Builder(REGIONS)
    for wall, a0, a1, dc, tilt in BLINDS:
        blind(b, wall, a0, a1, dc, tilt)
    return [b.to_object(NAME, coll)]


def texture(objs):
    mat = common.atlas_material("window_blinds", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        common.collapse_materials(ob, {r: mat for r in REGIONS})
