"""Bathroom toilet: two-piece, elongated bowl, closed seat and lid, squared tank with a
push-button flush in the lid, on the west wall facing east.

Source of truth: scripted, from the bathroom LiDAR survey (Reference/bathroom_survey/,
fixtures.py box "toilet" and the chk_toilet_* check images). SCAN = measured from the
registered capture (about +-1 in); EST = from the photos or standard sizes.

Local frame: front faces -Y, tank back toward the wall at +Y. Origin on the floor at the
footprint centre; the footprint runs y -14.875..+14.875 in (29.75 deep), the wall face
is 1.25 in behind the tank (plan: wall x 177.75, toilet x 179.0..208.75).
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
VIEWS = [("plan_top", 0, 89.9, 1.0), ("survey_view", 35, 40, 0.8)]

DEPTH = 29.75         # SCAN tank back to bowl front
LID_TOP = 18.5        # SCAN top of the closed seat lid
RIM_Z = 16.3          # EST bowl rim (comfort height; seat + lid bring it to 18.5)
BOWL_W, BOWL_L = 14.6, 19.5   # EST elongated bowl outside
TANK_W, TANK_D = 19.5, 8.0    # EST (the survey box is 15.8 wide, but the check photo shows
                              # the tank overhanging it on both sides)
TANK_TOP = 30.9       # SCAN top of the tank lid
TANK_Z0 = 16.0        # EST tank bottom on the rear deck
LID_T = 1.3           # EST tank lid

REGIONS = ["porcelain", "seat", "chrome"]


def build(coll):
    b = common.Builder(REGIONS)
    n = 32
    front = -m(DEPTH / 2)
    cy = front + m(BOWL_L / 2)
    # Pedestal and bowl as one loft: foot, waist, belly, rim.
    secs = [
        (S.ellipse(0, cy + m(2.8), m(4.9), m(7.8), n), 0.0),
        (S.ellipse(0, cy + m(2.8), m(4.4), m(6.9), n), m(1.0)),
        (S.ellipse(0, cy + m(2.3), m(4.3), m(6.5), n), m(5.5)),
        (S.ellipse(0, cy, m(6.2), m(9.0), n), m(10.5)),
        (S.ellipse(0, cy, m(BOWL_W / 2), m(BOWL_L / 2), n), m(RIM_Z - 1.6)),
        (S.ellipse(0, cy, m(BOWL_W / 2), m(BOWL_L / 2), n), m(RIM_Z)),
    ]
    S.loft(b, "porcelain", secs)
    ty1 = m(DEPTH / 2)
    ty0 = ty1 - m(TANK_D)
    # Rear deck under the tank.
    b.box("porcelain", (-m(4.3), cy + m(5.0), m(1.0)), (m(4.3), ty0 + m(2.5), m(TANK_Z0)),
          bevel=m(1.5))
    # Seat and closed lid.
    zs = m(RIM_Z)
    S.loft(b, "seat", [(S.ellipse(0, cy - m(0.3), m(7.2), m(10.0), n), zs),
                       (S.ellipse(0, cy - m(0.3), m(7.2), m(10.0), n), zs + m(1.0))])
    S.loft(b, "seat", [(S.ellipse(0, cy - m(0.1), m(7.0), m(9.7), n), zs + m(1.0)),
                       (S.ellipse(0, cy - m(0.1), m(6.8), m(9.4), n), m(LID_TOP))])
    b.box("seat", (-m(4.5), cy + m(9.3), zs), (m(4.5), cy + m(10.8), m(LID_TOP) + m(0.2)),
          bevel=m(0.4))
    # Tank and lid (squared, softly rounded).
    b.box("porcelain", (-m(TANK_W / 2), ty0, m(TANK_Z0)),
          (m(TANK_W / 2), ty1, m(TANK_TOP - LID_T)), bevel=m(0.9))
    b.box("porcelain", (-m(TANK_W / 2 + 0.3), ty0 - m(0.35), m(TANK_TOP - LID_T)),
          (m(TANK_W / 2 + 0.3), ty1 + m(0.1), m(TANK_TOP)), bevel=m(0.55))
    # Dual push button in the lid, left of centre.
    b.cylinder("chrome", (-m(3.0), (ty0 + ty1) / 2, m(TANK_TOP) + m(0.1)), m(1.1), m(0.25),
               segments=16)
    # Supply valve and line at the wall, left.
    b.cylinder("chrome", (-m(6.0), ty1 + m(0.6), m(7.0)), m(0.6), m(1.4), axis="Y",
               segments=10)
    b.cylinder("chrome", (-m(6.0), ty1 - m(0.2), m(11.5)), m(0.2), m(9.0), axis="Z",
               segments=8)
    return [b.to_object("toilet", coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
