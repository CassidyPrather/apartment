"""Tall rectangular stainless step-on kitchen trash can.

Source of truth: scripted, from the living-room survey (LiDAR + splat box
12.5 x 21 x 29) and three photo crops: rounded vertical corners, a flat lid on a thin
rim band, black plastic base trim and a steel foot pedal at the narrow front.

Local frame: front (pedal) faces -Y, Z up, origin on the floor at the footprint centre.
Placed at (30.5, 183), rotation 90 (pedal toward the east). No brand is visible.
"""

import common

NAME = "trash_can"


def m(inches):
    return inches * 0.0254


# --- dimensions (inches) -------------------------------------------------------------
W, D, H = 12.5, 21.0, 29.0      # SCAN overall
PEDAL = 2.2                     # EST pedal reach in front of the body
BODY_D = D - PEDAL
CORNER_R = 1.3                  # EST rounded vertical corners (photos)
BASE_H = 0.6                    # EST black base trim
RIM_Z = 26.8                    # EST lid rim band bottom
RIM_H = 0.6                     # EST
LID_INSET = 0.35                # EST

ATLAS = {
    "name": "trash_can",
    "size": 512,
    "regions": {
        "steel": (0, 0, 256, 512),
        "lid": (256, 0, 256, 256),
        "plastic": (256, 256, 256, 128),
        "pedal": (256, 384, 256, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"trash_can": {"atlas": "trash_can", "mode": "opaque"}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_high", 300, 40, 0.9)]


def rr(w, d, r, cy=0.0):
    return [(m(x), m(y)) for x, y in common.rounded_rect(0.0, cy, w, d, r, seg=4)]


def build(coll):
    b = common.Builder(REGIONS)
    cy = PEDAL / 2                                  # body sits behind the pedal
    b.prism("plastic", rr(W - 0.2, BODY_D - 0.2, CORNER_R, cy), 0.0, m(BASE_H))
    b.prism("steel", rr(W, BODY_D, CORNER_R, cy), m(BASE_H), m(RIM_Z), cap_region="steel")
    b.prism("lid", rr(W + 0.12, BODY_D + 0.12, CORNER_R + 0.06, cy), m(RIM_Z), m(RIM_Z + RIM_H))
    b.prism("lid", rr(W - LID_INSET, BODY_D - LID_INSET, CORNER_R - 0.2, cy), m(RIM_Z + RIM_H), m(H - 0.3))
    b.prism("lid", rr(W - LID_INSET - 0.8, BODY_D - LID_INSET - 0.8, CORNER_R - 0.5, cy), m(H - 0.3), m(H))
    # Pedal: a flat steel paddle at the front, just off the floor.
    y0 = -D / 2
    b.box("pedal", (m(-4.2), m(y0), m(0.5)), (m(4.2), m(y0 + PEDAL + 0.5), m(1.4)), bevel=m(0.25))
    b.box("plastic", (m(-3.5), m(y0 + 0.6), m(0.1)), (m(3.5), m(y0 + PEDAL + 0.5), m(0.6)))
    return [b.to_object("trash_can", coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material("trash_can", ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
