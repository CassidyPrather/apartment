"""Laundry closet door: 2-panel molded interior door (tall upper and lower raised panel),
white semi-gloss, round brushed-nickel knob. Closed.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py.
Local frame: origin on the floor at the hinge-side edge of the clear opening, on the wall
centreline; front (-Y) = hallway side (the door swings out into the hall, IMG_1502); the
opening runs to -X (hinge on the right seen from the hallway).

Dimensions (inches):
  opening 30 wide          layout (A)
  height 80                layout (A)
  wall 4.75                layout (M)
  leaf 1.375 thick         EST
  2-panel: bottom rail 9.5, lock rail 39-43, top rail 4.75, stiles 4.5
                           EST; IMG_1502 shows the knob just below the lower panel's top
  knob centre 36 up        EST
Hardware (see doorkit): brushed nickel ball knob on a stepped rose (IMG_1502), three
nickel butt hinges, latch and strike. Wear: faint smudges around the knob.
"""

import importlib
import os
import sys

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_laundry"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = False

WIDTH, HEIGHT, WALL_T, LEAF_T = 30.0, 80.0, 4.75, 1.375
HAND = -1
OPEN_DEG = 0.0

VIEWS = [("photo_match", 20, 20, 0.8)]


def rails_2panel(lh):
    return [(0.0, 9.5), (39.0, 43.0), (lh - 4.75, lh)]


def build(coll):
    lh = HEIGHT - K.JAMB_T - K.GAP - K.FLOOR_GAP
    return K.hinged(coll, NAME, WIDTH, HEIGHT, WALL_T, LEAF_T, HAND, OPEN_DEG,
                    rails_2panel(lh), [1, 1], handle="knob")


def texture(objs):
    K.texture(objs)
