"""Entry door: white half-lite door (a glazed upper half behind a 2 in white blind hung on the
door, two raised panels below), polished brass scroll lever and brass deadbolt, nickel
butt hinges. Closed. The placement also stands in for the bedroom's patio door, which is
the same half-lite door with a brass knob instead of the lever.

Source of truth: the living-room LiDAR capture (LidarSeries_20260925_003335_763 frames 0,
36, 39, 48 and 51: the door next to the window with the AC hose) and the bedroom capture
(LidarSeries_20260925_011425_918 frames 84, 240 and 252: the patio door); shared parts in
../door_bedroom/doorkit.py. No viewer: the door has a lite, and none shows in frame 51.
Local frame: origin on the floor at the hinge-side edge of the clear opening, on the wall
centreline; front (-Y) = the apartment interior (the door swings in: its knuckles face the
room in frame 48); the opening runs to -X (hinge on the right seen from inside).

Dimensions (inches):
  opening 36 wide          layout (M position, A width)
  height 80                layout (A)
  wall 6                   layout (A: exterior wall not measured)
  leaf 1.75 thick          EST (standard exterior door)
  half-lite: bottom rail 9.5, lock rail 30.5-43.25, top rail 4.75, stiles 4.5; two raised
    panels below the lock rail, the lite (~24 x 30 glass) above; the blind's bottom rail
    sits on the lite's bottom molding, just above the deadbolt (frames 36, 240)
                           EST, proportions read from frames 36, 48 and 240
  lever 36 up, deadbolt 5.5 above it       EST (standard), frame 36 agrees
  blind: 2 in slats at 1.75 pitch, tilted about 35 deg open; headrail 1.6 x 2.0
    just above the lite; two ladder tapes, two lift cords with tassels
                                           EST, read from frames 51 and 240
Wear: smudges around the lever and scuffs on the bottom rail (the "leaf" region, frame 48).
"""

import importlib
import math
import os
import sys

from mathutils import Matrix, Vector

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_entry"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = False

WIDTH, HEIGHT, WALL_T, LEAF_T = 36.0, 80.0, 6.0, 1.75
HAND = -1
OPEN_DEG = 0.0
DEADBOLT_Z = K.KNOB_Z + K.DEADBOLT_UP
STILE = 4.5
LOCK_RAIL = (30.5, 43.25)
SLAT_W, SLAT_T, SLAT_PITCH, SLAT_TILT = 2.0, 0.1, 1.75, 35.0

VIEWS = [("inside", 0, 8, 0.8), ("hardware", 30, 5, 0.45)]


def blind(b, lx0, lx1, lz0, lz1, y0, y1):
    """The 2 in blind hung on the inside face (y0) over the lite."""
    rails = rails_half_lite(lz1 - lz0)
    bay_z0, bay_z1 = lz0 + rails[1][1], lz0 + rails[2][0]
    bx0, bx1 = lx0 + STILE - 0.6, lx1 - STILE + 0.6          # a little past the lite
    yc = y0 - 1.2                                            # slat centreline
    top = bay_z1 + 1.0
    K.box(b, "slat", (bx0, y0 - 2.2, top - 1.6), (bx1, y0 - 0.2, top))            # headrail
    for x in (bx0 + 0.3, bx1 - 1.1):                                             # brackets
        K.box(b, "slat", (x, y0 - 0.25, top - 1.45), (x + 0.8, y0, top + 0.1))
    bottom = bay_z0 + 0.5                                     # rail over the lite bottom
    K.box(b, "slat", (bx0, yc - 0.55, bottom - 0.45), (bx1, yc + 0.55, bottom + 0.3))  # bottom rail
    n = int((top - 1.6 - 0.9 - (bottom + 0.3)) / SLAT_PITCH) + 1
    for i in range(n):
        zc = top - 1.6 - 0.9 - i * SLAT_PITCH
        mat = Matrix.Translation(Vector(K.mv(((bx0 + bx1) / 2, yc, zc)))) @ \
            Matrix.Rotation(math.radians(SLAT_TILT), 4, "X")
        w = bx1 - bx0 - 0.1
        K.box(b, "slat", (-w / 2, -SLAT_W / 2, -SLAT_T / 2), (w / 2, SLAT_W / 2, SLAT_T / 2),
              matrix=mat)
    # ladder tapes either side of the slats, and the lift cords with their tassels
    dy = math.cos(math.radians(SLAT_TILT)) * SLAT_W / 2 + 0.03
    for xl in (bx0 + 5.0, bx1 - 5.0):
        for y in (yc - dy, yc + dy):
            K.box(b, "slat", (xl - 0.15, y - 0.02, bottom + 0.3), (xl + 0.15, y + 0.02, top - 1.6))
        xc = xl + 0.5
        K.box(b, "slat", (xc - 0.04, yc - dy - 0.12, bottom + 1.5), (xc + 0.04, yc - dy - 0.04, top - 1.6))
        K.lathe(b, "slat", (xc, yc - dy - 0.08, bottom + 1.5),
                [(0.1, 0.0), (0.24, -0.3), (0.2, -1.1), (0.0, -1.25)], axis="Z", sign=1, seg=6)


def rails_half_lite(lh):
    return [(0.0, 9.5), LOCK_RAIL, (lh - 4.75, lh)]


def build(coll):
    lh = HEIGHT - K.JAMB_T - K.GAP - K.FLOOR_GAP
    return K.hinged(coll, NAME, WIDTH, HEIGHT, WALL_T, LEAF_T, HAND, OPEN_DEG,
                    rails_half_lite(lh), [2, 1], handle="lever", finish="brass",
                    hinge_finish="nickel", extras=blind, lite_bays=(1,), deadbolt_z=DEADBOLT_Z)


def texture(objs):
    K.texture(objs)
