"""Bathroom toilet: two-piece, elongated bowl, closed seat and lid, tank with lid and a
chrome flush lever.

Source of truth: scripted. Coarse block-in from standard fixture sizes (no photos of the
real toilet yet): every size is EST.

Local frame: front faces -Y, tank back toward the wall at +Y (1 in off it). Origin on
the floor at the footprint centre; the footprint runs y -14..+14 in, so the marker sits
14 in out from the wall face.
"""

import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bathtub"))

import common  # noqa: E402
import bathroom_shared as S  # noqa: E402

importlib.reload(S)
m = S.m

NAME = "toilet"
ATLAS = S.ATLAS
MATERIALS = S.MATERIALS
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 1.0)]

DEPTH = 28.0          # EST wall to bowl front, incl. 1 in gap behind the tank
RIM_Z = 14.5          # EST bowl rim; seat + lid bring it to ~16
BOWL_W, BOWL_L = 14.4, 19.5   # EST elongated bowl outside
BOWL_CY = -4.25       # EST bowl centre (front at -14)
TANK_W, TANK_D = 20.0, 8.0    # EST
TANK_Z0, TANK_Z1 = 15.0, 29.5  # EST tank body; lid to ~30.8
WALL_GAP = 1.0        # EST

REGIONS = ["porcelain", "seat", "chrome"]


def build(coll):
    b = common.Builder(REGIONS)
    n = 32
    cy = m(BOWL_CY)
    # Pedestal and bowl as one loft: foot, waist, belly, rim.
    secs = [
        (S.ellipse(0, m(-1.5), m(4.8), m(7.5), n), 0.0),
        (S.ellipse(0, m(-1.5), m(4.3), m(6.6), n), m(1.0)),
        (S.ellipse(0, m(-2.0), m(4.2), m(6.2), n), m(5.0)),
        (S.ellipse(0, cy, m(6.0), m(8.8), n), m(9.5)),
        (S.ellipse(0, cy, m(BOWL_W / 2), m(BOWL_L / 2), n), m(12.8)),
        (S.ellipse(0, cy, m(BOWL_W / 2), m(BOWL_L / 2), n), m(RIM_Z)),
    ]
    S.loft(b, "porcelain", secs)
    # Rear deck under the tank.
    b.box("porcelain", (-m(5.5), m(1.0), m(4.0)), (m(5.5), m(12.0), m(TANK_Z0)), bevel=m(0.8))
    # Seat and closed lid.
    S.loft(b, "seat", [(S.ellipse(0, cy - m(0.3), m(7.1), m(9.9), n), m(RIM_Z)),
                       (S.ellipse(0, cy - m(0.3), m(7.1), m(9.9), n), m(RIM_Z + 0.9))])
    S.loft(b, "seat", [(S.ellipse(0, cy - m(0.1), m(6.9), m(9.6), n), m(RIM_Z + 0.9)),
                       (S.ellipse(0, cy - m(0.1), m(6.7), m(9.3), n), m(RIM_Z + 1.6))])
    b.box("seat", (-m(4.5), m(4.8), m(RIM_Z)), (m(4.5), m(6.2), m(RIM_Z + 1.8)), bevel=m(0.4))
    # Tank and lid.
    ty1 = m(DEPTH / 2 - WALL_GAP)
    ty0 = ty1 - m(TANK_D)
    b.box("porcelain", (-m(TANK_W / 2), ty0, m(TANK_Z0)), (m(TANK_W / 2), ty1, m(TANK_Z1)),
          bevel=m(0.6))
    b.box("porcelain", (-m(TANK_W / 2 + 0.4), ty0 - m(0.4), m(TANK_Z1)),
          (m(TANK_W / 2 + 0.4), ty1 + m(0.3), m(TANK_Z1 + 1.3)), bevel=m(0.5))
    # Flush lever, front left.
    b.cylinder("chrome", (-m(7.0), ty0 - m(0.2), m(26.5)), m(0.8), m(0.5), axis="Y",
               segments=12)
    b.box("chrome", (-m(6.8), ty0 - m(0.7), m(26.2)), (-m(3.8), ty0 - m(0.3), m(26.8)),
          bevel=m(0.15))
    # Supply valve and line at the wall, left.
    b.cylinder("chrome", (-m(6.0), m(DEPTH / 2 - 0.8), m(7.0)), m(0.6), m(1.6), axis="Y",
               segments=10)
    b.cylinder("chrome", (-m(6.0), m(DEPTH / 2 - 1.6), m(11.0)), m(0.2), m(8.0), axis="Z",
               segments=8)
    return [b.to_object("toilet", coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
