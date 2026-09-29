"""Bathroom toilet: two-piece, elongated bowl, closed seat and lid on two hinge posts
with a hinge barrel, squared tank with a round chrome push button in the lid (no flush
lever: it is top-flush, photos 005946, 010010), white bolt caps at the floor, and an angle
stop with a braided supply line on the wall, on the west wall facing east.

Source of truth: scripted, from the bathroom LiDAR survey (Reference/bathroom_survey/,
fixtures.py box "toilet" and the chk_toilet_* check images) and the capture's frames
(005928-010010). SCAN = measured from the registered capture (about +-1 in); EST = from
the photos or standard sizes.

Wear (texture, bathroom atlas region toilet_deck, mapped from above): brown drips and
grime round the seat hinges on the rear rim and deck (frames 005949, 005952).

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
VIEWS = [("plan_top", 0, 89.9, 1.0), ("survey_view", 35, 40, 0.8), ("hinges", 20, 55, 0.45),
         ("side_low", 280, 10, 0.7)]

DEPTH = 29.75         # SCAN tank back to bowl front
LID_TOP = 18.5        # SCAN top of the closed seat lid
RIM_Z = 16.3          # EST bowl rim (comfort height; seat + lid bring it to 18.5)
BOWL_W, BOWL_L = 14.6, 19.5   # EST elongated bowl outside
TANK_W, TANK_D = 19.5, 8.0    # EST (the survey box is 15.8 wide, but the check photo shows
                              # the tank overhanging it on both sides)
TANK_TOP = 30.9       # SCAN top of the tank lid
TANK_Z0 = 16.0        # EST tank bottom on the rear deck
LID_T = 1.3           # EST tank lid
HINGE_X = 2.8         # EST hinge posts either side of centre (photo 005949)
WALL_GAP = 1.25       # SCAN tank back to the wall face
SUPPLY_X, SUPPLY_Z = -6.0, 7.0   # EST angle stop on the wall, left (photo 005958)
# texture mapping of the toilet_deck region (inches, local): x span and y span
DECK_U = (-7.3, 7.3)
DECK_V = (-14.875, 9.4)

REGIONS = ["porcelain", "toilet_deck", "seat", "chrome"]


def build(coll):
    b = common.Builder(REGIONS)
    n = 32
    front = -m(DEPTH / 2)
    cy = front + m(BOWL_L / 2)
    # Pedestal and bowl as one loft: foot, waist, belly, rim (rim top = stained deck).
    secs = [
        (S.ellipse(0, cy + m(2.8), m(4.9), m(7.8), n), 0.0),
        (S.ellipse(0, cy + m(2.8), m(4.4), m(6.9), n), m(1.0)),
        (S.ellipse(0, cy + m(2.3), m(4.3), m(6.5), n), m(5.5)),
        (S.ellipse(0, cy, m(6.2), m(9.0), n), m(10.5)),
        (S.ellipse(0, cy, m(BOWL_W / 2), m(BOWL_L / 2), n), m(RIM_Z - 1.6)),
        (S.ellipse(0, cy, m(BOWL_W / 2), m(BOWL_L / 2), n), m(RIM_Z)),
    ]
    S.loft(b, "porcelain", secs, top_region="toilet_deck")
    ty1 = m(DEPTH / 2)
    ty0 = ty1 - m(TANK_D)
    # Rear deck under the tank.
    faces = b.box("porcelain", (-m(4.3), cy + m(5.0), m(1.0)), (m(4.3), ty0 + m(2.5), m(TANK_Z0)),
                  bevel=m(1.5))
    b.bm.normal_update()
    for f in b.bm.faces:
        if f.material_index == b.idx("porcelain") and f.normal.z > 0.6 and \
                f.calc_center_median().z > m(RIM_Z - 0.5):
            f.material_index = b.idx("toilet_deck")
    # Bolt caps on the foot, one each side.
    for sx in (-1, 1):
        x = sx * m(4.75)
        b.cylinder("porcelain", (x, cy + m(2.8), m(0.55)), m(0.55), m(1.1), segments=8)
        S.frustum(b, "porcelain", (x, cy + m(2.8), m(1.25)), m(0.55), m(0.25), m(0.3), "Z", 8)
    # Seat and closed lid.
    zs = m(RIM_Z)
    S.loft(b, "seat", [(S.ellipse(0, cy - m(0.3), m(7.2), m(10.0), n), zs),
                       (S.ellipse(0, cy - m(0.3), m(7.2), m(10.0), n), zs + m(1.0))])
    S.loft(b, "seat", [(S.ellipse(0, cy - m(0.1), m(7.0), m(9.7), n), zs + m(1.0)),
                       (S.ellipse(0, cy - m(0.1), m(6.8), m(9.4), n), m(LID_TOP))])
    # Hinges: two plastic posts bolted through the deck and the barrel the seat and lid
    # turn on.
    hy = cy + m(10.1)
    for sx in (-1, 1):
        b.box("seat", (sx * m(HINGE_X) - m(0.65), hy - m(0.9), zs - m(0.05)),
              (sx * m(HINGE_X) + m(0.65), hy + m(0.8), zs + m(1.2)), bevel=m(0.25), segments=1)
    b.cylinder("seat", (0, hy - m(0.3), zs + m(1.35)), m(0.55), m(2 * HINGE_X + 1.6), axis="X",
               segments=10)
    # Tank and lid (squared, softly rounded).
    b.box("porcelain", (-m(TANK_W / 2), ty0, m(TANK_Z0)),
          (m(TANK_W / 2), ty1, m(TANK_TOP - LID_T)), bevel=m(0.9))
    b.box("porcelain", (-m(TANK_W / 2 + 0.3), ty0 - m(0.35), m(TANK_TOP - LID_T)),
          (m(TANK_W / 2 + 0.3), ty1 + m(0.1), m(TANK_TOP)), bevel=m(0.55))
    # Round push button in the lid, left of centre, in a thin bezel.
    bx, by = -m(3.0), (ty0 + ty1) / 2
    S.frustum(b, "chrome", (bx, by, m(TANK_TOP) + m(0.05)), m(1.3), m(1.15), m(0.14), "Z", 16)
    b.cylinder("chrome", (bx, by, m(TANK_TOP) + m(0.15)), m(0.95), m(0.22), segments=16)
    # Angle stop on the wall (escutcheon, valve body, oval handle) and the braided line
    # curving up to the fill valve's coupling nut under the tank.
    wy = ty1 + m(WALL_GAP)
    vx, vz = m(SUPPLY_X), m(SUPPLY_Z)
    S.frustum(b, "chrome", (vx, wy - m(0.15), vz), m(1.1), m(0.8), m(0.3), "Y", 10, sign=-1)
    b.cylinder("chrome", (vx, wy - m(0.9), vz), m(0.45), m(1.3), axis="Y", segments=8)
    b.box("chrome", (vx - m(0.2), wy - m(2.0), vz - m(0.7)), (vx + m(0.2), wy - m(1.55), vz + m(0.7)),
          bevel=m(0.12), segments=1)
    line = [(vx, wy - m(1.0), vz + m(0.4)), (vx, wy - m(1.1), vz + m(3.0)),
            (vx, wy - m(1.7), vz + m(6.0)), (vx, wy - m(2.6), vz + m(8.0)),
            (vx, wy - m(2.8), m(TANK_Z0) - m(0.6))]
    b.sweep("chrome", line, common.circle_profile(m(0.2), 6), up=(1, 0, 0))
    b.cylinder("chrome", (vx, wy - m(2.8), m(TANK_Z0) - m(0.35)), m(0.5), m(0.7), segments=8)
    return [b.to_object("toilet", coll)]


def texture(objs):
    mat = common.atlas_material("bathroom", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar={
            "toilet_deck": ("+Z", (m(DECK_U[0]), m(DECK_U[1])), (m(DECK_V[0]), m(DECK_V[1])))})
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: mat for r in regions})
