"""Black portable air conditioner with its exhaust hose run to the living room's west
window (window 2) and a window slider panel in that window.

Source of truth: scripted, from the living-room survey (LiDAR + splat registered in
layout inches) and four photo crops. The real unit's front logo is left off (no brand
on it at all), so no parody name is needed.

Local frame: front faces -Y, Z up, origin on the floor at the placement point.
Placed at (12.5, 125, 0), rotation 90 (front faces east), so
    world x = 12.5 - local y,   world y = 125 + local x.
The scan puts the unit's body at world x 17.5..32.5, y 110..128 (centre (25, 119)),
i.e. off the placement point: the body is built there in the local frame rather than
at the origin, so the hose meets the window without moving the marker.
The west wall's interior face is at local y = +12.5; the window recess is behind it.
"""

import importlib
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plant_tall"))
import common  # noqa: E402
import plantkit as K  # noqa: E402

importlib.reload(K)


def m(inches):
    return inches * 0.0254


NAME = "portable_ac"

# --- dimensions (inches, local frame) ----------------------------------------------------
BODY_W = 18.5            # SCAN (y extent 110..128 in the plan)
BODY_D = 15.0            # SCAN (x extent 17.5..32.5)
BODY_H = 34.0            # SCAN
BODY_CX = -6.0           # SCAN body centre (world y 119)
BODY_FRONT = -20.0       # SCAN front face (world x 32.5)
BEVEL = 1.4              # EST rounded edges (photos)
GRILLE_R = 3.3           # EST rounded top-front louvre (photos)
GRILLE_Z = 29.0          # EST
GRILLE_L = 16.2          # EST nearly full width (photos)
CASTER_H = 1.0           # EST
HOSE_R = 3.6             # EST 7.2 in corrugated duct (photos: ~1/3 of the unit's width)
COLLAR_Z = 28.5          # EST hose outlet on the back, upper
WALL_Y = 12.5            # SCAN/layout: west wall interior face (world x 0)
PANEL = dict(x=(-21.5, -13.5), y=(13.9, 14.7), z=(28.0, 83.5))  # EST window slider panel,
#   standing in window 2's recess (sill 26.5, head 85) just inside the sash
HOSE_END = (-17.5, 13.9, 32.5)   # SCAN hose enters the window near its south end

ATLAS = {
    "name": "portable_ac",
    "size": 512,
    "regions": {
        "body": (0, 0, 256, 256),
        "grille": (256, 0, 256, 256),
        "hose": (0, 256, 256, 256),
        "controls": (256, 256, 128, 128),
        "panel": (384, 256, 128, 128),
        "chrome": (256, 384, 128, 128),
        "rubber": (384, 384, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"portable_ac": {"atlas": "portable_ac", "mode": "opaque"}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front", -25, 32, 0.8)]


def hose_path():
    back = BODY_FRONT + BODY_D
    pts = [(BODY_CX, back + 0.5, COLLAR_Z), (BODY_CX - 1.5, back + 4.5, COLLAR_Z + 1.5),
           (BODY_CX - 6.5, back + 10.5, 31.0), (-16.5, 11.0, 32.3), HOSE_END]
    return common.smooth_path([Vector(tuple(m(v) for v in p)) for p in pts], samples=7)


def build(coll):
    b = K.CardBuilder(REGIONS)
    x0, x1 = BODY_CX - BODY_W / 2, BODY_CX + BODY_W / 2
    y0, y1 = BODY_FRONT, BODY_FRONT + BODY_D
    # Body on four casters.
    b.box("body", (m(x0), m(y0 + GRILLE_R * 0.6), m(CASTER_H)), (m(x1), m(y1), m(BODY_H)), bevel=m(BEVEL), segments=2)
    b.box("body", (m(x0), m(y0), m(CASTER_H)), (m(x1), m(y0 + GRILLE_R * 0.6 + 1), m(GRILLE_Z - GRILLE_R + 0.5)),
          bevel=m(BEVEL), segments=2)
    for cx in (x0 + 2.5, x1 - 2.5):
        for cy in (y0 + 2.5, y1 - 2.5):
            b.cylinder("rubber", (m(cx), m(cy), m(CASTER_H / 2)), m(1.0), m(CASTER_H), segments=8)
    # Rounded louvre across the top front, with bright end trims.
    b.cylinder("grille", (m(BODY_CX), m(y0 + GRILLE_R * 0.6), m(GRILLE_Z)), m(GRILLE_R), m(GRILLE_L),
               axis="X", segments=16)
    for s in (-1, 1):
        b.cylinder("chrome", (m(BODY_CX + s * (GRILLE_L / 2 + 0.35)), m(y0 + GRILLE_R * 0.6), m(GRILLE_Z)),
                   m(GRILLE_R + 0.15), m(0.7), axis="X", segments=16)
    gy1 = y0 + GRILLE_R * 0.6 + 1
    for lo_x, hi_x in ((x0, BODY_CX - GRILLE_L / 2 - 0.7), (BODY_CX + GRILLE_L / 2 + 0.7, x1)):
        b.box("body", (m(lo_x), m(y0 + 0.2), m(GRILLE_Z - GRILLE_R)), (m(hi_x), m(gy1), m(BODY_H - 0.3)),
              bevel=m(0.3))
    # Control strip on the top, behind the louvre.
    b.box("controls", (m(BODY_CX - 7.5), m(y0 + GRILLE_R * 0.6 + 2.2), m(BODY_H - 0.1)),
          (m(BODY_CX + 7.5), m(y0 + GRILLE_R * 0.6 + 4.2), m(BODY_H + 0.08)))
    # Hose collar on the back, then the corrugated duct to the window.
    b.cylinder("rubber", (m(BODY_CX), m(y1 + 0.6), m(COLLAR_Z)), m(HOSE_R + 0.5), m(1.4), axis="Y", segments=16)
    b.sweep_uv("hose", hose_path(), common.circle_profile(m(HOSE_R), 12), v_per_seg=0.5)
    # Window slider panel with the hose adapter.
    px, py, pz = PANEL["x"], PANEL["y"], PANEL["z"]
    b.box("panel", (m(px[0]), m(py[0]), m(pz[0])), (m(px[1]), m(py[1]), m(pz[1])))
    hx, hy, hz = HOSE_END
    b.cylinder("rubber", (m(hx), m(hy - 0.5), m(hz)), m(HOSE_R + 0.45), m(1.2), axis="Y", segments=16)
    return [b.to_object("portable_ac", coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material("portable_ac", ATLAS)
    y0 = BODY_FRONT
    common.atlas_uvs(ob, ATLAS, planar={
        "grille": ("-Y", (m(BODY_CX - GRILLE_L / 2), m(BODY_CX + GRILLE_L / 2)),
                   (m(GRILLE_Z - GRILLE_R), m(GRILLE_Z + GRILLE_R))),
        "controls": ("+Z", (m(BODY_CX - 7.5), m(BODY_CX + 7.5)),
                     (m(y0 + GRILLE_R * 0.6 + 2.2), m(y0 + GRILLE_R * 0.6 + 4.2))),
    })
    K.apply_card_uvs(ob, ATLAS, regions=["hose"])
    common.collapse_materials(ob, {r: mat for r in REGIONS})
