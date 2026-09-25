"""Patio door: sliding glass door, white vinyl frame (EST) with one fixed and one sliding
glass panel. Closed. No photo yet: frame colour and which panel slides are estimates.

Source of truth: scripted, shared parts in ../door_bedroom/doorkit.py.
Local frame: origin on the floor at the centre of the opening, on the wall centreline;
front (-Y) = the apartment interior. The fixed panel is on the outer track at +X, the
sliding panel on the inner track at -X. Objects: door_patio (frame, sill, fixed panel),
door_patio_slider (origin on the floor at its centre; slides along +X to open) and
door_patio_slider_grab (handle marker). Glass uses doors_glass (transparent, alpha 0.25).

Dimensions (inches):
  opening 36 wide          layout (M), as given; very narrow for a two-panel slider, check
  height 80                layout (A)
  wall 6                   layout (A)
  frame 1.25 face, 4.5 deep; sill 1.5    EST
  panels 1.25 thick, stiles/rails 2 (bottom rail 3), glass 0.25   EST
  handle 32-41 up          EST
"""

import importlib
import os
import sys

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "door_bedroom")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import doorkit as K  # noqa: E402

importlib.reload(K)

NAME = "door_patio"
ATLAS = K.ATLAS
MATERIALS = dict(K.MATERIALS)
MATERIALS.update(K.MATERIALS_GLASS)
COLLIDER = "box"
STATIC = False

WIDTH, HEIGHT, WALL_T = 36.0, 80.0, 6.0
FACE, DEPTH, SILL = 1.25, 4.5, 1.5
PANEL_T, STILE, GLASS_T = 1.25, 2.0, 0.25
OVERLAP = 1.5

VIEWS = [("inside", 180, 10, 0.8)]


def glass_panel(b, xa, xb, za, zb, ya, yb, bottom=3.0):
    K.box(b, "vinyl", (xa, ya, za), (xa + STILE, yb, zb))
    K.box(b, "vinyl", (xb - STILE, ya, za), (xb, yb, zb))
    K.box(b, "vinyl", (xa + STILE, ya, za), (xb - STILE, yb, za + bottom))
    K.box(b, "vinyl", (xa + STILE, ya, zb - STILE), (xb - STILE, yb, zb))
    yc = (ya + yb) / 2
    K.box(b, "glass", (xa + STILE, yc - GLASS_T / 2, za + bottom),
          (xb - STILE, yc + GLASS_T / 2, zb - STILE))


def build(coll):
    W = WIDTH
    x0, x1 = -W / 2, W / 2
    ya, yb = -DEPTH / 2, DEPTH / 2
    f = K.builder()
    K.box(f, "vinyl", (x0, ya, 0), (x0 + FACE, yb, HEIGHT))
    K.box(f, "vinyl", (x1 - FACE, ya, 0), (x1, yb, HEIGHT))
    K.box(f, "vinyl", (x0 + FACE, ya, HEIGHT - FACE), (x1 - FACE, yb, HEIGHT))
    K.box(f, "vinyl", (x0 + FACE, ya, 0), (x1 - FACE, yb, SILL))
    K.box(f, "dark", (x0 + FACE, -1.8, SILL), (x1 - FACE, 1.8, SILL + 0.3))    # track
    iw = W - 2 * FACE
    pw = (iw + OVERLAP) / 2
    za, zb = SILL + 0.3, HEIGHT - FACE - 0.1
    glass_panel(f, x1 - FACE - pw, x1 - FACE, za, zb, 0.2, 0.2 + PANEL_T)        # fixed, outer
    frame = f.to_object(NAME, coll)
    b = K.builder()
    sa, sb = x0 + FACE, x0 + FACE + pw
    y0, y1 = -0.2 - PANEL_T, -0.2
    glass_panel(b, sa, sb, za, zb, y0, y1)
    hx = sa + 1.0                                                   # pull on the lock stile
    K.box(b, "dark", (hx - 0.4, y0 - 1.0, 32.0), (hx + 0.4, y0, 41.0), bevel=0.2)
    slider = b.to_object(NAME + "_slider", coll, origin=K.mv(((sa + sb) / 2, (y0 + y1) / 2, 0)))
    mk = K.marker(coll, NAME + "_slider_grab", (hx, y0 - 1.5, 36.5))
    return [frame, slider, mk]


def texture(objs):
    K.texture(objs)
