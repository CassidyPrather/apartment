"""Kitchen closet doors: a pair of white molded bifold doors (four leaves, each with a tall
upper and a shorter lower raised panel), closed, hung from a head track, with a small
nickel knob on each lead leaf. The shell draws the casings. Objects: door_kitchen_closet
(jamb, track) and door_kitchen_closet_leaf_0..3 (left to right), each leaf's origin on
the pin it turns about (jamb side for 0 and 3, the fold for 1 and 2) so the pairs fold
in Unity (BifoldDoor).

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
  knob 36 up, 1.75 from the fold edge     EST; small satin nickel mushroom knob (IMG_1523)
  pivots: floor L brackets and track blocks at both jambs, pins top/bottom of the jamb
    leaves, guide pins at the top of the lead leaves   EST (standard bifold hardware)
Wear: faint smudges round the knobs, scuffs along the bottoms (the "leaf" region).
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
    """The frame (jamb, track) plus the four leaves as separate objects, each with its
    origin on the pin it turns about: the outer leaves (0, 3) on the jamb pivots, the inner
    ones (1, 2) on the fold with their outer leaf, so Unity can fold each pair."""
    W, T = WIDTH, WALL_T
    x0, x1 = -W / 2, W / 2
    shift = (0, K.m(T / 2), 0)                # origin on the wall's front face
    b = K.builder()
    K.jamb(b, W, HEIGHT, T, hand=1, x_start=x0, stops=False)
    top = HEIGHT - K.JAMB_T
    y0 = -T / 2 + FACE_BACK                  # leaf front face (doorkit centreline frame)
    K.box(b, "aluminum", (x0 + K.JAMB_T, y0 - 0.2, top - TRACK_H), (x1 - K.JAMB_T, y0 + LEAF_T + 0.2, top))
    # the track's slot reads as a dark line under the head (IMG_1523)
    K.box(b, "dark", (x0 + K.JAMB_T + 0.1, y0 + LEAF_T / 2 - 0.25, top - TRACK_H - 0.02),
          (x1 - K.JAMB_T - 0.1, y0 + LEAF_T / 2 + 0.25, top - TRACK_H))
    # pivot brackets at both jambs: an L bracket on the floor and a pivot block in the track
    yc_ = y0 + LEAF_T / 2
    for sx in (-1, 1):
        xj = sx * (W / 2 - K.JAMB_T)
        K.box(b, "nickel", (xj, yc_ - 0.6, 0.0), (xj - sx * 1.6, yc_ + 0.6, 0.12))
        K.box(b, "nickel", (xj, yc_ - 0.6, 0.0), (xj - sx * 0.1, yc_ + 0.6, 2.0))
        K.box(b, "nickel", (xj, yc_ - 0.45, top - TRACK_H - 0.35), (xj - sx * 1.2, yc_ + 0.45, top - TRACK_H))
    bmesh.ops.translate(b.bm, vec=shift, verts=b.bm.verts)
    out = [b.to_object(NAME, coll)]

    xa, xb = x0 + K.JAMB_T + LEAF_GAP, x1 - K.JAMB_T - LEAF_GAP
    lw = (xb - xa - 3 * LEAF_GAP) / 4
    lz0, lz1 = K.FLOOR_GAP, top - TRACK_H - 0.25
    lh = lz1 - lz0
    rails = [(0.0, 5.0), (33.5, 38.5), (lh - 3.5, lh)]   # knobs sit on the mid rail
    yc = y0 + LEAF_T / 2                     # the pins run through the leaf's middle
    for i in range(4):
        la = xa + i * (lw + LEAF_GAP)
        lb = la + lw
        lb_ = K.builder()
        K.panel_leaf(lb_, la, lb, lz0, lz1, y0, y0 + LEAF_T, rails, [1, 1], stile=STILE)
        if i == 1:                           # mushroom knobs on the lead leaves, near the fold
            K.knob(lb_, "nickel", la + 1.75, K.KNOB_Z, y0, -1, style="mushroom")
        if i == 2:
            K.knob(lb_, "nickel", lb - 1.75, K.KNOB_Z, y0, -1, style="mushroom")
        # hardware on the pins: pivot pins top and bottom of the jamb leaves, the guide
        # pin (roller) at the top of each lead leaf's free edge
        if i in (0, 3):                      # on the pivot axis, so they turn in place
            pp = la if i == 0 else lb
            K.cyl(lb_, "nickel", (pp, yc, lz0 - 0.3), 0.18, 0.6, axis="Z", seg=6)
            K.cyl(lb_, "nickel", (pp, yc, lz1 + 0.3), 0.18, 0.6, axis="Z", seg=6)
        else:                                # the free edges meet in the middle
            pp = lb - 0.9 if i == 1 else la + 0.9
            K.cyl(lb_, "nickel", (pp, yc, lz1 + 0.3), 0.18, 0.6, axis="Z", seg=6)
        bmesh.ops.translate(lb_.bm, vec=shift, verts=lb_.bm.verts)
        # pins: the jamb edge of the outer leaves, the fold edge of the inner ones
        px = {0: la, 1: la, 2: lb, 3: lb}[i]
        ob = lb_.to_object(f"{NAME}_leaf_{i}", coll, origin=(K.m(px), K.m(yc + T / 2), 0.0))
        # wear: u = 1 at the knob (fold) edge of the lead leaves; the jamb leaves (no knob)
        # map into u 0..0.6 so they stay clear of the smudges
        if i in (1, 2):
            K.register_leaf(ob.name, lb if i == 1 else la, la if i == 1 else lb, lz0, lz1)
        else:
            K.register_leaf(ob.name, la if i == 0 else lb, lb if i == 0 else la, lz0, lz1,
                            u_scale=0.6)
        out.append(ob)
    return out


def texture(objs):
    K.texture(objs)
