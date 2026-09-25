"""Kitchen closet doors: a pair of white molded bifold doors (four leaves, each with a tall
upper and a shorter lower raised panel), closed, hung from a head track, with a small
nickel knob on each lead leaf. The shell draws the casings.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py (imported, not edited).
Local frame: origin on the floor at the opening's centre, ON THE WALL'S FRONT FACE (not
the centreline as in doorkit); front (-Y) = kitchen side, the wall runs to +Y. Placement:
plan (134, 229.5), rotation -90 (front faces west, local +X = south).

Dimensions (inches):
  opening 47 wide (y 206..253), 80 tall   layout (S / A)
  wall 4.75                               layout (M)
  leaves 4 x ~11.4 wide, 1.125 thick      EST (standard bifold), 4 leaves from the photo
  leaf front face 1.0 behind the wall face  SCAN (LiDAR depth histogram, x 135..136.5)
  panels: bottom rail 5, mid rail 33.5-38.5 (knobs on it), top rail 3.5, stiles 2.25
                                          EST, proportions read from the photo
  head track 1.0 tall                     EST
  knob 36 up, 1.75 from the fold edge     EST
"""

import importlib
import os
import sys

import bmesh

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_kitchen_closet"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
COLLIDER = "box"
STATIC = True

WIDTH, HEIGHT, WALL_T, LEAF_T = 47.0, 80.0, 4.75, 1.125
FACE_BACK = 1.0          # leaf front face behind the wall's front face
TRACK_H = 1.0
LEAF_GAP = 0.125
STILE = 2.25

VIEWS = [("photo_match", 340, 5, 0.75), ("close", 20, 10, 0.5)]


def build(coll):
    W, T = WIDTH, WALL_T
    x0, x1 = -W / 2, W / 2
    b = K.builder()
    K.jamb(b, W, HEIGHT, T, hand=1, x_start=x0, stops=False)
    top = HEIGHT - K.JAMB_T
    y0 = -T / 2 + FACE_BACK                  # leaf front face (doorkit centreline frame)
    K.box(b, "aluminum", (x0 + K.JAMB_T, y0 - 0.2, top - TRACK_H), (x1 - K.JAMB_T, y0 + LEAF_T + 0.2, top))
    xa, xb = x0 + K.JAMB_T + LEAF_GAP, x1 - K.JAMB_T - LEAF_GAP
    lw = (xb - xa - 3 * LEAF_GAP) / 4
    lz0, lz1 = K.FLOOR_GAP, top - TRACK_H - 0.25
    lh = lz1 - lz0
    rails = [(0.0, 5.0), (33.5, 38.5), (lh - 3.5, lh)]   # knobs sit on the mid rail
    for i in range(4):
        la = xa + i * (lw + LEAF_GAP)
        K.panel_leaf(b, la, la + lw, lz0, lz1, y0, y0 + LEAF_T, rails, [1, 1], stile=STILE)
    # knobs on the two lead leaves (the inner pair), near the fold with the outer leaf
    for kx in (xa + lw + LEAF_GAP + 1.75, xb - lw - LEAF_GAP - 1.75):
        K.knob(b, "nickel", kx, K.KNOB_Z, y0, -1)
    # move the frame so the origin sits on the wall's front face
    bmesh.ops.translate(b.bm, vec=(0, K.m(T / 2), 0), verts=b.bm.verts)
    return [b.to_object(NAME, coll)]


def texture(objs):
    K.texture(objs)
