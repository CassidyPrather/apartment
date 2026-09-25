"""Bedroom door: 4-panel molded (raised-panel look) interior door, white semi-gloss, dark
lever set, shown open about 90 degrees into the bedroom against the bedroom back wall.

Source of truth: scripted (shared parts in doorkit.py, used by every door_* package).
Local frame (see doorkit): origin on the floor at the hinge-side edge of the clear opening,
on the wall centreline; front (-Y) = bedroom side; the opening runs to -X (hinge on the
right seen from the bedroom). Objects: door_bedroom (jamb, stops, hinge knuckles),
door_bedroom_leaf (origin on the hinge pin) and door_bedroom_leaf_grab (lever marker).

Dimensions (inches):
  opening 34 wide          layout (M position / width M)
  height 80                layout (A: assumed)
  wall 4.75                layout (M)
  leaf 1.375 thick         EST (standard hollow-core interior)
  4-panel layout: bottom rail 9.5, lock rail 32-40, top rail 4.75, stiles/mullion 4.5
                           EST, proportions read from IMG_1498 (upper panels ~1.5x lower)
  lever centre 36 up       EST
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import importlib  # noqa: E402

import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_bedroom"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = False           # the leaf swings (a later pass adds the hinge interaction)

WIDTH, HEIGHT, WALL_T, LEAF_T = 34.0, 80.0, 4.75, 1.375
HAND = -1
OPEN_DEG = 90.0

VIEWS = [("photo_match", 290, 4, 0.75)]


def rails_4panel(lh):
    return [(0.0, 9.5), (32.0, 40.0), (lh - 4.75, lh)]


def build(coll):
    lh = HEIGHT - K.JAMB_T - K.GAP - K.FLOOR_GAP
    return K.hinged(coll, NAME, WIDTH, HEIGHT, WALL_T, LEAF_T, HAND, OPEN_DEG,
                    rails_4panel(lh), [2, 2], handle="lever")


def texture(objs):
    K.texture(objs)
