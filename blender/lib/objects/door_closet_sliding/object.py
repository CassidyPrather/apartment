"""Bedroom closet bypass doors: two sliding leaves on a double head track, 2-panel molded
(EST, matched to the laundry door) with round finger cups. Closed. No photo yet.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py.
Local frame: origin on the floor at the centre of the opening, on the wall centreline;
front (-Y) = hallway side. Objects: door_closet_sliding (jamb liners, track, floor guide),
door_closet_sliding_left (front track, -X half) and door_closet_sliding_right (back track,
+X half), each with its origin on the floor at its own centre so it slides along X, plus
a _grab marker at each finger cup.

Dimensions (inches):
  opening 61 wide (Y 138-199 in the layout)   layout (A: door widths not measured)
  height 81.5              layout (A: measured closet height)
  wall 4.75                layout (A)
  leaves 30.5 wide each (1 in overlap), 1.375 thick, ~79 tall   EST
  track 1.25 tall, 3.8 deep; leaf centres 1.6 apart            EST
"""

import importlib
import os
import sys

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_closet_sliding"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = False

WIDTH, HEIGHT, WALL_T, LEAF_T = 61.0, 81.5, 4.75, 1.375
TRACK_H, OVERLAP = 1.25, 1.0

VIEWS = [("close", 25, 10, 0.7)]


def build(coll):
    W, T = WIDTH, WALL_T
    x0, x1 = -W / 2, W / 2
    f = K.builder()
    K.jamb(f, W, HEIGHT, T, hand=1, x_start=x0, stops=False)
    top = HEIGHT - K.JAMB_T
    K.box(f, "aluminum", (x0 + K.JAMB_T, -1.9, top - TRACK_H), (x1 - K.JAMB_T, 1.9, top))
    K.box(f, "dark", (-1.0, -1.9, 0), (1.0, 1.9, 1.0))            # floor guide
    frame = f.to_object(NAME, coll)
    out = [frame]
    lw = (W - 2 * K.JAMB_T + OVERLAP) / 2
    lz0, lz1 = 0.5, top - TRACK_H - 0.25
    lh = lz1 - lz0
    rails = [(0.0, 9.5), (39.0, 43.0), (lh - 4.75, lh)]
    for side, name, yc in ((-1, "left", -0.8), (1, "right", 0.8)):
        xa = x0 + K.JAMB_T if side < 0 else x1 - K.JAMB_T - lw
        xb = xa + lw
        ya, yb = yc - LEAF_T / 2, yc + LEAF_T / 2
        b = K.builder()
        K.panel_leaf(b, xa, xb, lz0, lz1, ya, yb, rails, [1, 1])
        cx = xa + 2.25 if side < 0 else xb - 2.25                # cups near the outer edges
        for sign, yf in ((-1, ya), (1, yb)):
            K.cyl(b, "dark", (cx, yf + sign * 0.03, K.KNOB_Z), 0.9, 0.08, seg=12)
        ob = b.to_object(f"{NAME}_{name}", coll, origin=K.mv(((xa + xb) / 2, yc, 0)))
        out.append(ob)
        out.append(K.marker(coll, f"{NAME}_{name}_grab", (cx, ya - 1.0, K.KNOB_Z)))
    return out


def texture(objs):
    K.texture(objs)
