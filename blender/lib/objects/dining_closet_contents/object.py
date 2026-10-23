"""Dining closet contents: the small closet behind the 4-panel door off the dining room
(photo 16 of the 2026-10-23 cupboards set,
Reference/cupboards_drawers/PXL_20261023_032010506.jpg), plus its shelf, which the shell
doesn't build.

  shelf: a painted board on 1x4 cleats (back and both end walls), no rod
  on the shelf (north -> south): a green/white portable carpet spot-cleaner with its hose
    coiled round the base and a black pole standing behind it; two red plastic things; a
    grey paisley-ish throw with a pink corner hanging over the edge; an orange gym duffel
    (grey handles, blank black patch) on the throw
  draped over the shelf front: a big printed game map (red top band with gold edges,
    then a made-up continent on a dark sea; painted from scratch, not a copy)
  floor: a red steel toolbox along the north wall (chrome handle and latches), a white
    pedestal fan taken apart (pole on its cross base in front of the toolbox, the 16 in
    head leaning on the floor facing the door), a handheld vacuum in its charger and a
    grey spray-mop handle against the back wall, an upright vacuum (charcoal, purple
    accents) in the south-east corner with a black cloth at its foot
Brands -> colour blocks only (no parody names): vacuums, spot-cleaner, duffel, mop.

Source of truth: scripted. Frame: PLAN coordinates (inches converted to metres), origin
= plan (0, 0, 0); place at (0, 0, 0) with no rotation.

Dimensions (inches):
  closet interior x 138.75 (center wall) .. 166.55 (laundry divider), y 163.15 (bedroom
    back wall) .. 197.75 (bath south wall); door opening y 164..194     shell_layout (D/S/A)
  shelf top z 68, 16 deep (x 150.55..166.55)          EST (photo, same as the kitchen closet)
  map 32.6 wide, hangs to z ~44.5                      EST (photo: ~23.5 in drop)
  red toolbox 20 x 8.5 x 9.3 (+ handle)                SPEC-ish (standard 20 in steel box)
  upright vacuum 44 tall, base 13 x 12                 SPEC-ish / EST
  pedestal fan head 16 dia; pole 1.3 dia x 18          SPEC-ish / EST
  handheld vacuum ~15 tall in its charger              EST
  spot-cleaner ~12 x 11 x 14                           EST (photo)
  orange duffel 16 x 12.5 x 12.5                       EST (photo)
Depths (x) are guesses from the doorway view; the hidden south strip behind the jamb is
kept sparse.

Door swing: the door is hinged north and in fact swings OUT into the dining room (its
hinge knuckles show on the dining side in IMG_1523, and photo 16 shows the north wall and
the toolbox right behind the hinge edge). An inward 90 deg swing (r = 30 about the hinge
at plan (138.75, 194)) would sweep through the toolbox, fan, vacuums and the east wall
itself; see clearance() below.
"""

import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(os.path.dirname(HERE), "kitchen_closet_contents")
if KIT not in sys.path:
    sys.path.insert(0, KIT)
import closetkit as K  # noqa: E402

importlib.reload(K)

import common  # noqa: E402

NAME = "dining_closet_contents"
_T = {}
exec(open(os.path.join(HERE, "textures.py"), encoding="utf-8").read(), _T)   # ATLAS only
ATLAS = _T["ATLAS"]
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "mesh"
STATIC = True

VIEWS = [("photo_match", 270, 10, 0.75), ("north", 330, 20, 0.7)]

X0, X1, Y0, Y1 = 138.75, 166.55, 163.15, 197.75
S, SHELF_FRONT = 68.0, 150.55
HINGE = (138.75, 194.0)
MAP_Y = (164.2, 196.8)
MAP_Z = (44.5, 68.12)

box, lump, cyl, sweep = K.box, K.lump, K.cyl, K.sweep
SQ = [(-0.15, -0.15), (0.15, -0.15), (0.15, 0.15), (-0.15, 0.15)]
PLANAR = {}


def circ(r, n=8):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def map_drape(b):
    """The game map: a thin sheet lying on the shelf, rolling over the front edge and
    hanging down, with a few soft vertical folds."""
    path = [(161.0, S + 0.06), (155.0, S + 0.06), (151.2, S + 0.06), (150.7, S - 0.05), (150.45, S - 0.5),
            (150.35, S - 1.4), (150.3, S - 6.0), (150.05, S - 12.0), (149.9, S - 18.0), (150.1, MAP_Z[0] + 1.5),
            (150.35, MAP_Z[0])]
    pts, ups = [], []
    yc = (MAP_Y[0] + MAP_Y[1]) / 2
    for i, (x, z) in enumerate(path):
        xa, za = path[max(i - 1, 0)]
        xb, zb = path[min(i + 1, len(path) - 1)]
        tx, tz = xb - xa, zb - za
        ln = math.hypot(tx, tz)
        tx, tz = tx / ln, tz / ln
        pts.append((x, yc, z))
        ups.append((tz, 0.0, -tx))
    half = (MAP_Y[1] - MAP_Y[0]) / 2
    n = 12
    front = [(-half + 2 * half * i / n, 0.12 + 0.18 * math.sin(i * 1.9)) for i in range(n + 1)]
    back = [(s, v - 0.12) for s, v in reversed(front)]
    profile = front + back
    # sweep wants plan inches for points; ups are directions
    return b.sweep("map", [K.V(*p) for p in pts], [(K.m(s), K.m(v)) for s, v in profile], ups=ups)


def build(coll):
    b = common.Builder(REGIONS)
    PLANAR.clear()

    # --- shelf ----------------------------------------------------------------------
    K.closet_shelf(b, SHELF_FRONT, X1, Y0, Y1, S)

    # --- on the shelf ---------------------------------------------------------------
    map_drape(b)
    T = S + 0.14                                           # on top of the map
    # spot cleaner (north end): base, translucent-white tank, hose coils, handle column
    box(b, "cleaner_green", (152.0, 185.8, T), (165.0, 196.9, T + 3.2), bevel=1.0)
    lump(b, "cleaner_white", (152.8, 186.8, T + 2.8), (164.0, 196.0, T + 16.0), seed=21, round_=0.45,
         amp=0.02, cuts=2)
    for i, (r_in, z) in enumerate(((0.0, T + 1.2), (0.6, T + 2.6))):
        loop = [(158.3 + (7.0 - r_in) * math.cos(a), 191.0 + (5.7 - r_in) * math.sin(a), z)
                for a in [2 * math.pi * k / 14 for k in range(14)]]
        sweep(b, "cleaner_hose", loop, circ(0.9, 6), closed=True)
    box(b, "cleaner_green", (157.5, 184.9, T + 2.0), (160.0, 186.6, T + 17.5), bevel=0.4)
    cyl(b, "cleaner_hose", (156.8, 185.6, T + 2.0), 0.55, 14.0, seg=8)
    box(b, "cleaner_lime", (151.4, 191.0, T + 0.5), (153.4, 195.6, T + 4.2), bevel=0.4)
    box(b, "cleaner_lime", (152.0, 186.6, T + 5.0), (153.6, 189.0, T + 8.0), bevel=0.3)
    # black pole standing behind the cleaner, leaning on the back wall
    cyl(b, "pole_black", (163.0, 185.2, T), 0.5, 34.0, seg=8, ry=4, pivot=(163.0, 185.2, T))
    # red plastic things
    lump(b, "red_plastic", (154.5, 179.5, T + 2.5), (160.5, 184.5, T + 10.0), seed=22, round_=0.6, amp=0.12)
    lump(b, "red_plastic", (152.0, 180.0, T + 1.0), (157.0, 184.2, T + 6.0), seed=23, round_=0.6, amp=0.1)
    # throw (grey paisley) with a pink corner over the edge
    lump(b, "throw", (150.9, 164.5, T - 0.1), (165.3, 187.0, T + 4.2), seed=24, round_=0.25, amp=0.3,
         freq=3.0, cuts=4, sag=0.15)
    PLANAR["throw"] = K.planar_x(164.0, 187.0, T - 2.0, T + 6.0)
    sweep(b, "pink_cloth", [(154.0, 174.5, T + 1.5), (151.0, 174.0, T + 0.8), (150.2, 174.2, T - 0.8),
                            (150.0, 174.8, T - 5.5)],
          [(-1.6, -0.1), (1.6, -0.1), (1.6, 0.1), (-1.6, 0.1)], up=(1, 0, 0))
    lump(b, "pink_cloth", (151.5, 181.0, T), (156.0, 186.0, T + 2.2), seed=25, round_=0.3, amp=0.25)
    # orange duffel lying front-to-back on the throw
    lump(b, "duffel_orange", (150.4, 164.4, T + 3.2), (166.3, 178.2, T + 16.0), seed=26, round_=0.5,
         amp=0.04, faces={"-X": "duffel_end"})
    PLANAR["duffel_end"] = K.planar_x(164.4, 178.2, T + 3.2, T + 16.0)
    for yh in (167.0, 175.6):
        sweep(b, "strap_grey", [(152.0, yh, T + 14.5), (155.0, yh + 0.2, T + 18.0), (159.0, yh + 0.3, T + 18.5),
                                (163.0, yh + 0.2, T + 18.0), (165.0, yh, T + 15.0)],
              [(-0.6, -0.1), (0.6, -0.1), (0.6, 0.1), (-0.6, 0.1)], up=(0, 0, 1))

    # a small black tool hanging on the north wall by the door, a blank card above it
    box(b, "pole_black", (139.6, 196.75, 46.0), (141.8, 197.7, 51.5), bevel=0.15)
    box(b, "duffel_orange", (139.5, 196.65, 48.3), (141.9, 196.8, 49.6))
    box(b, "handvac_white", (139.8, 197.2, 52.0), (141.6, 197.7, 54.6))

    # --- floor ----------------------------------------------------------------------
    # red toolbox along the north wall
    ty0, ty1, tx0, tx1 = 188.9, 197.35, 142.5, 162.5
    box(b, "toolbox_red", (tx0, ty0, 0.0), (tx1, ty1, 7.0), bevel=0.15)
    box(b, "toolbox_red", (tx0 - 0.1, ty0 - 0.1, 7.0), (tx1 + 0.1, ty1 + 0.1, 9.3), bevel=0.35)
    box(b, "vac_black", (tx0 + 0.2, ty0 - 0.02, 6.95), (tx1 - 0.2, ty1 + 0.02, 7.05))
    yh = (ty0 + ty1) / 2
    sweep(b, "chrome", common.smooth_path([(147.5, yh, 9.3), (148.2, yh, 10.6), (152.5, yh, 11.1),
                                           (156.8, yh, 10.6), (157.5, yh, 9.3)], 3), circ(0.3, 6))
    for hx in (147.0, 157.0):
        box(b, "chrome", (hx - 0.6, yh - 0.6, 9.25), (hx + 0.6, yh + 0.6, 9.55))
    for lx in (144.6, 159.4):
        box(b, "chrome", (lx - 0.5, ty0 - 0.25, 6.0), (lx + 0.5, ty0, 8.2))
    # pedestal fan: pole on its cross base, head leaning on the floor facing the door
    fx, fy = 146.5, 186.2
    for ang in (35.0, 125.0):
        box(b, "fan_white", (fx - 7.5, fy - 0.8, 0.0), (fx + 7.5, fy + 0.8, 0.9), bevel=0.2, rz=ang)
    cyl(b, "fan_white", (fx, fy, 0.0), 1.4, 2.2, seg=10)
    cyl(b, "fan_white", (fx, fy, 0.9), 0.65, 17.5, seg=10)
    cyl(b, "vac_black", (fx, fy, 18.3), 0.5, 0.3, seg=10)
    hx, hy, hz = 149.5, 173.0, 8.4
    cyl(b, "fan_white", (hx, hy, hz), 8.0, 2.2, axis="X", seg=20, cap="fan_grille", ry=25, rz=12,
        pivot=(hx, hy, hz))
    cyl(b, "fan_white", (hx + 2.6, hy, hz), 2.6, 3.4, axis="X", seg=12, ry=25, rz=12, pivot=(hx, hy, hz))
    PLANAR["fan_grille"] = K.planar_x(hy - 8.2, hy + 8.2, hz - 7.6, hz + 7.6)
    # handheld vacuum in its charger, against the back wall
    box(b, "charger_grey", (160.6, 177.6, 0.0), (165.9, 183.2, 2.2), bevel=0.4)
    cyl(b, "handvac_teal", (162.4, 180.4, 1.6), 2.1, 7.0, seg=10, ry=6, pivot=(162.4, 180.4, 1.6))
    box(b, "handvac_white", (161.4, 179.2, 7.6), (164.0, 181.6, 16.0), bevel=0.6, ry=6, pivot=(162.4, 180.4, 1.6))
    box(b, "handvac_black", (161.1, 179.6, 6.0), (161.7, 181.2, 11.0), ry=6, pivot=(162.4, 180.4, 1.6))
    # grey spray-mop handle leaning on the back wall
    cyl(b, "mop_grey", (157.6, 175.6, 0.5), 1.1, 15.0, seg=10, ry=22, pivot=(157.6, 175.6, 0.5))
    cyl(b, "mop_black", (157.6, 175.6, 15.5), 0.9, 1.6, seg=10, ry=22, pivot=(157.6, 175.6, 0.5))
    box(b, "mop_black", (152.0, 169.5, 0.0), (165.4, 177.0, 1.2), bevel=0.3)
    # upright vacuum in the south-east corner
    box(b, "vac_dark", (152.6, 163.7, 0.0), (166.2, 175.0, 4.6), bevel=1.0)
    box(b, "vac_purple", (152.4, 165.5, 3.0), (152.9, 173.2, 3.8))
    cyl(b, "vac_cup", (161.6, 168.4, 5.5), 3.3, 15.5, seg=14)
    box(b, "vac_purple", (159.6, 166.8, 20.5), (164.4, 170.0, 23.0), bevel=0.3)
    box(b, "vac_dark", (158.6, 165.3, 21.0), (164.8, 171.6, 32.5), bevel=0.8)
    box(b, "vac_purple", (158.3, 167.6, 26.0), (158.8, 169.2, 31.5))
    cyl(b, "vac_black", (161.8, 168.4, 32.5), 0.75, 10.0, seg=8)
    box(b, "vac_black", (160.9, 166.6, 41.5), (162.7, 170.2, 44.0), bevel=0.5)
    sweep(b, "vac_black", common.smooth_path([(164.8, 166.2, 30.0), (165.8, 164.6, 18.0), (165.6, 164.4, 6.0)], 3),
          circ(0.6, 6))
    lump(b, "cloth_black", (153.0, 169.5, 0.4), (160.5, 178.5, 8.5), seed=27, round_=0.3, amp=0.25)

    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    planar = dict(PLANAR)
    planar["map"] = K.planar_x(MAP_Y[0], MAP_Y[1], MAP_Z[0], MAP_Z[1])
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
    clearance(ob)


def clearance(ob, r=30.6):
    """Report the mesh inside the dining door's INWARD swing (quarter disc r about the
    hinge, x > 138.75, y < 194, below the head z 80)."""
    hx, hy = HINGE
    inside = 0
    names = set()
    for v in ob.data.vertices:
        x, y, z = (c / K.IN for c in v.co)
        if x > hx and y < hy and z < 80 and math.hypot(x - hx, y - hy) < r:
            inside += 1
    print("dining door inward-swing clearance: %d of %d verts inside r=%.1f" % (
        inside, len(ob.data.vertices), r), names or "")
