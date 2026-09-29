"""Dining-room closet door: 4-panel molded interior door (tall upper panels, short lower
ones), white semi-gloss, brushed-nickel scroll lever and three nickel butt hinges. Closed.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py.
Local frame: origin on the floor at the hinge-side edge of the clear opening, on the wall
centreline; front (-Y) = dining-room side (the door swings into the closet); the opening
runs to -X (hinge on the left seen from the dining room, IMG_1523).

Dimensions (inches):
  opening 30 wide          layout (M)
  height 80                layout (A)
  wall 4.75                layout (M)
  leaf 1.375 thick         EST
  4-panel: bottom rail 9.5, lock rail 32-40, top rail 4.75, stiles/mullion 4.5
                           EST, proportions from IMG_1523 (upper panels ~1.7x lower)
  lever centre 36 up       EST
Hardware (see doorkit): brushed nickel scroll lever on a stepped rose, three nickel butt
hinges (IMG_1523), latch and strike. Wear: faint hand smudges around the lever.
"""

import importlib
import os
import sys

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_dining_closet"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = False

WIDTH, HEIGHT, WALL_T, LEAF_T = 30.0, 80.0, 4.75, 1.375
HAND = -1
OPEN_DEG = 0.0

VIEWS = [("photo_match", 200, 10, 0.8)]


def rails_4panel(lh):
    return [(0.0, 9.5), (32.0, 40.0), (lh - 4.75, lh)]


def build(coll):
    lh = HEIGHT - K.JAMB_T - K.GAP - K.FLOOR_GAP
    return K.hinged(coll, NAME, WIDTH, HEIGHT, WALL_T, LEAF_T, HAND, OPEN_DEG,
                    rails_4panel(lh), [2, 2], handle="lever", finish="nickel")


def texture(objs):
    K.texture(objs)
