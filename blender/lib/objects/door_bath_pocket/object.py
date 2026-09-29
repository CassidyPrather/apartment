"""Bathroom pocket door: 2-panel molded leaf (EST, matched to the laundry door) that slides
into the wall, shown mostly open with 4 in of its leading edge showing. No photo yet.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py.
Local frame: origin on the floor at the centre of the clear opening, on the wall
centreline; front (-Y) = hallway side; the pocket is on the -X side (EST). Objects:
door_bath_pocket (jamb liners, split jamb at the pocket), door_bath_pocket_leaf (origin
on the floor at the leaf's leading edge; it slides along X, closed = +(WIDTH - SHOW) in X)
and door_bath_pocket_leaf_grab (edge pull). The part of the leaf inside the pocket is
hidden by the shell's solid wall.

Dimensions (inches):
  opening 31.75 wide       layout (M)
  height 80                layout (A)
  wall 4.75                layout (M; a real pocket wall is usually thicker, check)
  leaf 1.375 thick, 32 wide (0.75 into the latch jamb)   EST
  leading edge showing 4   choice (coordinator: mostly open)
"""

import importlib
import os
import sys

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_bath_pocket"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = False

WIDTH, HEIGHT, WALL_T, LEAF_T = 31.75, 80.0, 4.75, 1.375
SHOW = 4.0

VIEWS = [("close", 20, 10, 0.6)]


def build(coll):
    W, T = WIDTH, WALL_T
    x0, x1 = -W / 2, W / 2
    f = K.builder()
    # head and latch-side leg liners; the pocket side is a split jamb either side of the slot
    K.box(f, "paint", (x0, -T / 2, HEIGHT - K.JAMB_T), (x1, T / 2, HEIGHT))
    K.box(f, "paint", (x1 - K.JAMB_T, -T / 2, 0), (x1, T / 2, HEIGHT - K.JAMB_T))
    slot = LEAF_T / 2 + 0.25
    for ya, yb in ((-T / 2, -slot), (slot, T / 2)):
        K.box(f, "paint", (x0, ya, 0), (x0 + K.JAMB_T, yb, HEIGHT - K.JAMB_T))
    # guide strip at the head of the slot
    K.box(f, "dark", (x0, -slot, HEIGHT - K.JAMB_T - 0.4), (x1 - K.JAMB_T, slot, HEIGHT - K.JAMB_T))
    frame = f.to_object(NAME, coll)

    lead = x0 + SHOW                              # leading edge, mostly open
    lw = W + 0.75 - K.JAMB_T
    lh = HEIGHT - K.JAMB_T - 0.4 - K.FLOOR_GAP
    b = K.builder()
    K.panel_leaf(b, lead - lw, lead, K.FLOOR_GAP, K.FLOOR_GAP + lh, -LEAF_T / 2, LEAF_T / 2,
                 [(0.0, 9.5), (39.0, 43.0), (lh - 4.75, lh)], [1, 1])
    # edge pull on the leading edge (nickel plate, dark finger slot), and a rectangular
    # flush pull near it on both faces (nickel flange, dark recess)
    K.box(b, "nickel", (lead - 0.02, -0.5, K.KNOB_Z - 1.6), (lead + 0.05, 0.5, K.KNOB_Z + 1.6))
    K.box(b, "dark", (lead + 0.05, -0.3, K.KNOB_Z - 1.1), (lead + 0.07, 0.3, K.KNOB_Z + 1.1))
    for sign in (-1, 1):
        yf = sign * LEAF_T / 2
        K.box(b, "nickel", (lead - 3.2, yf - sign * 0.02, K.KNOB_Z - 1.6),
              (lead - 1.2, yf + sign * 0.06, K.KNOB_Z + 1.6))
        K.box(b, "dark", (lead - 2.95, yf + sign * 0.06, K.KNOB_Z - 1.3),
              (lead - 1.45, yf + sign * 0.075, K.KNOB_Z + 1.3))
    leaf = b.to_object(NAME + "_leaf", coll, origin=K.mv((lead, 0, 0)))
    K.register_leaf(leaf.name, lead - lw, lead, K.FLOOR_GAP, K.FLOOR_GAP + lh)
    mk = K.marker(coll, NAME + "_leaf_grab", (lead - 2.2, -LEAF_T / 2 - 1.0, K.KNOB_Z))
    return [frame, leaf, mk]


def texture(objs):
    K.texture(objs)
