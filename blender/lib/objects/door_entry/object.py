"""Entry door: exterior 6-panel door, white, brushed-nickel knob, deadbolt and peephole.
Closed. No photo yet: style, hardware and hinge side are estimates.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py.
Local frame: origin on the floor at the hinge-side edge of the clear opening, on the wall
centreline; front (-Y) = the apartment interior (the door swings in); the opening runs to
-X (hinge on the right seen from inside).

Dimensions (inches):
  opening 36 wide          layout (M position, A width)
  height 80                layout (A)
  wall 6                   layout (A: exterior wall not measured)
  leaf 1.75 thick          EST (standard exterior door)
  6-panel: bottom rail 9.5, lock rail 32-38, intermediate rail 60-64, top rail 4.75
                           EST (common 6-panel layout)
  knob 36, deadbolt 42, peephole 60 up   EST
"""

import importlib
import os
import sys

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
DEADBOLT_Z, PEEP_Z = 42.0, 60.0


def extras(b, lx0, lx1, lz0, lz1, y0, y1):
    latch_x = HAND * (WIDTH - K.JAMB_T - K.GAP - K.BACKSET)
    for sign, yf in ((-1, y0), (1, y1)):
        K.cyl(b, "nickel", (latch_x, yf + sign * 0.2, DEADBOLT_Z), 1.1, 0.4, seg=14, bevel=0.1)
        if sign < 0:   # thumb turn inside
            K.box(b, "nickel", (latch_x - 0.2, yf - 1.1, DEADBOLT_Z - 0.7),
                  (latch_x + 0.2, yf - 0.4, DEADBOLT_Z + 0.7))
        else:          # key cylinder outside
            K.cyl(b, "nickel", (latch_x, yf + 0.6, DEADBOLT_Z), 0.55, 0.5, seg=10)
    xc = (lx0 + lx1) / 2
    K.cyl(b, "nickel", (xc, y0 - 0.1, PEEP_Z), 0.4, 0.3, seg=10)
    K.cyl(b, "nickel", (xc, y1 + 0.1, PEEP_Z), 0.4, 0.3, seg=10)


def build(coll):
    lh = HEIGHT - K.JAMB_T - K.GAP - K.FLOOR_GAP
    rails = [(0.0, 9.5), (32.0, 38.0), (60.0, 64.0), (lh - 4.75, lh)]
    return K.hinged(coll, NAME, WIDTH, HEIGHT, WALL_T, LEAF_T, HAND, OPEN_DEG,
                    rails, [2, 2, 2], handle="knob", extras=extras)


def texture(objs):
    K.texture(objs)
