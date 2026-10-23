"""Kitchen closet contents: everything in the long closet behind the kitchen's white
bifold doors (photo 15 of the 2026-10-23 cupboards set,
Reference/cupboards_drawers/PXL_20261023_031959353.jpg), plus the closet's shelf and rod,
which the shell doesn't build.

  shelf: a painted board on 1x4 cleats (back and both end walls) the full length of the
    closet, a wooden closet rod just under its front edge
  on the shelf (north -> south): two black backpacks with straps over the edge, an open
    shipping box with a white bag sticking out, a big blue spinner suitcase standing
    upright (front wheels over the edge), a navy carry-on against the south wall; past the
    opening (hidden from the doorway) a folded blanket and a box
  below, left (north) stack: a vanity bench (grey seat, black legs) carrying a clear bin
    of cardboard and a clear bin of clip hangers (with a white mailer box); on the bins a
    grey cooler bag, a black file box, a copy-paper case and a black cylindrical air
    purifier with its cord; behind them white plastic bags; on the cooler a brown carton
    under the brown "catering" box (its hand-lettering left off)
  below, right (south): a lockbox on the floor with a kraft boot box on it, a moving
    carton behind, a navy bag on that, a red/black duffel with a grey top panel, a tan
    bag, a navy bag under the shelf and a black bag against the south wall
  floor, front: a seat-massager box (printed person -> plain colour block) and a black
    cushion behind it, a red/white tissue-style box with a white mailing tube, an
    orange box, a teal folding crate on edge; past the opening, two plain cartons
Brands -> colour blocks only (no parody names needed): paper case, cooler bag, file box,
boot box, purifier, massager box.

Source of truth: scripted. Frame: PLAN coordinates (inches converted to metres), origin
= plan (0, 0, 0); place at (0, 0, 0) with no rotation, like kitchen_clutter.

Dimensions (inches):
  closet interior x 138.75 (center wall) .. 166.55 (bath west wall), y 202.5 (bath
    south wall) .. 286 (north wall); opening y 206..253            shell_layout (D/S)
  shelf top z 68, 16 deep (x 150.55..166.55), 0.75 board, 1x4 cleats   EST (photo)
  closet rod 1.3 dia, centre x 151.6, z 66.55                      EST (photo)
  vanity bench seat 28 x 14, top z 17.5                            EST (photo)
  clear bins 23 x 16.4 x 11.5 (32 qt class)                        SPEC-ish / EST
  file box 14.3 x 11.3 x 11.3                                      SPEC-ish / EST
  8-ream paper case 17.5 x 11.25 x 8.6                             SPEC (case of 8 reams)
  air purifier 6.7 dia x 11.3                                      EST (photo vs case)
  cooler bag 15 x 10.5 x 19.7                                      EST (photo)
  blue spinner 28 in class: 27.5 x 18 x 12.8; navy carry-on 20.5 x 14 x 9.4   EST
  lockbox 13 x 9.5 x 9.5, boot box 13.4 x 12 x 10.5, massager box 13 x 7 x 14  EST
  bags / fabric: lumps sized from the photo                        EST
The photo is straight in through the doorway, so depths (x) are guesses: the stack's
front is kept at the closet face (x ~139-141) and the hidden back is filled sparsely.
"""

import importlib
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import closetkit as K  # noqa: E402

importlib.reload(K)

import common  # noqa: E402

NAME = "kitchen_closet_contents"
_T = {}
exec(open(os.path.join(HERE, "textures.py"), encoding="utf-8").read(), _T)   # ATLAS only
ATLAS = _T["ATLAS"]
REGIONS = list(ATLAS["regions"])
CLEAR = "clear"
CLEAR_ALPHA = 0.3
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
             NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": CLEAR_ALPHA}}
COLLIDER = "mesh"
STATIC = True

# camera: azimuth 270 = from the west (the kitchen), looking east into the closet
VIEWS = [("photo_match", 270, 8, 0.75), ("north_peek", 300, 15, 0.7)]

X0, X1, Y0, Y1 = 138.75, 166.55, 202.5, 286.0
SHELF_Z, SHELF_FRONT = 68.0, 150.55
ROD = (151.6, 66.55, 1.3)

box, lump, cyl, sweep = K.box, K.lump, K.cyl, K.sweep

CORD = [(-0.15, -0.15), (0.15, -0.15), (0.15, 0.15), (-0.15, 0.15)]

# printed faces: region -> (y0, y1, z0, z1) of the face seen from the west
PRINTED = {}


def pbox(b, region, lo, hi, front, sides=None, top=None, bevel=0.0):
    """Box whose west face carries the painted `front` region (planar), optional
    side (+-Y) and top regions."""
    table = {"-X": front}
    if sides:
        table["+Y"] = table["-Y"] = sides
    if top:
        table["+Z"] = top
    PRINTED[front] = (lo[1], hi[1], lo[2], hi[2])
    if sides:
        PRINTED[sides] = None
    return box(b, region, lo, hi, bevel=bevel, faces=table)


def clear_bin(b, x0, y0, z0, x1, y1, z1, lid="lid_white"):
    """Open clear bin (walls + floor, clear material) with a white snap lid."""
    t = 0.14
    box(b, CLEAR, (x0 + 0.3, y0 + 0.3, z0), (x1 - 0.3, y1 - 0.3, z0 + t))
    for lo, hi in (((x0, y0, z0), (x0 + t, y1, z1 - 1.0)), ((x1 - t, y0, z0), (x1, y1, z1 - 1.0)),
                   ((x0 + t, y0, z0), (x1 - t, y0 + t, z1 - 1.0)),
                   ((x0 + t, y1 - t, z0), (x1 - t, y1, z1 - 1.0))):
        box(b, CLEAR, lo, hi)
    box(b, lid, (x0 - 0.3, y0 - 0.3, z1 - 1.0), (x1 + 0.3, y1 + 0.3, z1 - 0.55), bevel=0.15)
    box(b, lid, (x0 + 0.6, y0 + 0.6, z1 - 0.6), (x1 - 0.6, y1 - 0.6, z1), bevel=0.2)


def suitcase(b, body, x0, y0, z0, x1, y1, z1, wheels_hang=True, badge=False):
    """Upright spinner suitcase, narrow side to the west: body, black bottom bumper,
    side carry handle, a zip gusset line, telescoping handle, spinner wheels."""
    box(b, body, (x0, y0, z0), (x1, y1, z1), bevel=1.0)
    box(b, "trim_black", (x0 - 0.05, y0 - 0.05, z0), (x1 + 0.05, y1 + 0.05, z0 + 1.2), bevel=0.4)
    yz = y1 - 1.6
    box(b, "trim_black", (x0 - 0.12, yz, z0 + 1.0), (x0 + 0.2, yz + 0.45, z1 - 1.0))
    yc = (y0 + y1) / 2
    box(b, "trim_black", (x0 - 0.9, yc - 0.8, z0 + (z1 - z0) * 0.45), (x0 - 0.1, yc + 0.8, z0 + (z1 - z0) * 0.78),
        bevel=0.3)
    xm = (x0 + x1) / 2
    box(b, "trim_black", (xm - 4.5, yc - 0.6, z1 + 0.6), (xm + 4.5, yc + 0.6, z1 + 1.8), bevel=0.3)
    for xp in (xm - 4.0, xm + 4.0):
        box(b, "zipper", (xp - 0.4, yc - 0.4, z1 - 0.2), (xp + 0.4, yc + 0.4, z1 + 0.7))
    if badge:
        cyl(b, "trim_black", (x0 - 0.15, yc + 1.2, z0 + (z1 - z0) * 0.62), 0.9, 0.3, axis="X", seg=10)
    if wheels_hang:
        pairs = [(x0 + 1.0, z0 - 1.6)]          # front pair over the shelf edge; the back pair is hidden
    else:
        pairs = [(x0 + 1.4, z0 - 1.15), (x1 - 1.4, z0 - 1.15)]
    for xw, zc in pairs:
        for yw in (y0 + 1.4, y1 - 1.4):
            box(b, "trim_black", (xw - 0.9, yw - 0.9, z0 - 0.5), (xw + 0.9, yw + 0.9, z0 + 0.2), bevel=0.2)
            for dx in (-0.45, 0.45):
                cyl(b, "wheel", (xw + dx, yw, zc), 1.1, 0.75, axis="X", seg=10)


def hanger(b, x, yc, zc, ang, length=13.0):
    """White plastic clip hanger: a bar with a clip at each end, tilted in the y-z plane."""
    faces = box(b, "hanger", (x - 0.3, yc - length / 2, zc - 0.35), (x + 0.3, yc + length / 2, zc + 0.35))
    for e in (-1, 1):
        faces += box(b, "hanger", (x - 0.55, yc + e * (length / 2 - 0.8) - 0.6, zc - 1.6),
                     (x + 0.55, yc + e * (length / 2 - 0.8) + 0.6, zc + 0.4))
    K.rotate_about(b, faces, (x, yc, zc), rx=ang)


def build(coll):
    b = common.Builder(REGIONS)
    PRINTED.clear()

    # --- shelf and rod --------------------------------------------------------------
    K.closet_shelf(b, SHELF_FRONT, X1, Y0, Y1, SHELF_Z, rod=(ROD[0], ROD[1], ROD[2], "rod_wood"))
    S = SHELF_Z

    # --- on the shelf ---------------------------------------------------------------
    # two black backpacks, straps over the front edge
    lump(b, "pack_black", (151.2, 240.0, S), (165.5, 258.0, S + 7.5), seed=1, round_=0.45, amp=0.12, sag=0.2,
         faces={"+Z": "pack_grey"})
    lump(b, "pack_black", (152.0, 239.0, S + 6.5), (164.5, 255.5, S + 13.0), seed=2, round_=0.5, amp=0.1, rz=8)
    for yb in (244.0, 250.5):
        sweep(b, "pack_black", [(153.0, yb, S + 0.6), (150.6, yb, S + 0.2), (150.2, yb + 0.3, S - 3.0),
                                (150.4, yb + 1.2, S - 6.5), (150.6, yb + 2.4, S - 3.0), (150.7, yb + 2.8, S + 0.2),
                                (153.0, yb + 3.0, S + 0.6)], K_strap(), up=(1, 0, 0))
    for zp, yp in ((S + 5.8, 252.5), (S + 10.5, 251.0)):
        box(b, "zipper", (150.9, yp, zp), (151.5, yp + 0.5, zp + 1.4))
    # open shipping box, flaps up, a white bag inside
    bx0, by0, bx1, by1, bz1 = 153.0, 226.5, 165.5, 239.5, S + 9.5
    t = 0.18
    pbox(b, "kraft", (bx0, by0, S), (bx0 + t, by1, bz1), "kraft_front")
    for lo, hi in (((bx1 - t, by0, S), (bx1, by1, bz1)), ((bx0, by0, S), (bx1, by0 + t, bz1)),
                   ((bx0, by1 - t, S), (bx1, by1, bz1)), ((bx0, by0, S), (bx1, by1, S + t))):
        box(b, "kraft", lo, hi)
    box(b, "kraft", (bx0 - 0.05, by0, bz1 - 0.1), (bx0 + 0.13, by1, bz1 + 5.5), ry=-28, pivot=(bx0, by0, bz1))
    box(b, "kraft", (bx1 - 0.13, by0, bz1 - 0.1), (bx1 + 0.05, by1, bz1 + 5.5), ry=5, pivot=(bx1, by0, bz1))
    box(b, "kraft_dark", (bx0, by1 - 0.13, bz1 - 0.1), (bx1, by1 + 0.05, bz1 + 5.0), rx=-20, pivot=(bx0, by1, bz1))
    lump(b, "bag_white", (155.0, 228.5, S + 6.0), (163.0, 236.5, S + 14.5), seed=3, round_=0.3, amp=0.25,
         rz=20, ry=-20)
    # blue spinner (front wheels over the edge) and the navy carry-on (on the shelf)
    suitcase(b, "blue_case", 148.2, 213.0, S, 166.3, 225.8, S + 27.5, wheels_hang=True)
    suitcase(b, "navy_case", 151.6, 203.0, S + 2.3, 165.6, 212.4, S + 22.5, wheels_hang=False, badge=True)
    # past the opening: folded blanket and a box
    lump(b, "blanket", (152.0, 262.0, S), (165.5, 282.0, S + 6.0), seed=4, round_=0.25, amp=0.05, sag=0.1)
    box(b, "kraft", (153.0, 265.0, S + 5.6), (165.0, 279.0, S + 15.0), bevel=0.15)

    # --- left (north) stack ---------------------------------------------------------
    # vanity bench
    box(b, "bench_grey", (141.0, 223.5, 14.5), (155.0, 251.5, 17.5), bevel=0.8)
    for lx in (141.7, 152.9):
        for ly in (224.2, 249.4):
            box(b, "bench_leg", (lx, ly, 0.0), (lx + 1.4, ly + 1.4, 14.5))
    for ly in (224.6, 249.8):
        box(b, "bench_leg", (142.5, ly, 4.0), (153.5, ly + 0.6, 5.0))
    # hidden supports at the back (plain cartons)
    box(b, "kraft", (155.5, 240.0, 0.0), (165.8, 259.5, 17.4), bevel=0.15)
    box(b, "kraft_dark", (152.5, 222.0, 29.1), (165.8, 242.0, 46.0), bevel=0.15)
    box(b, "kraft", (152.0, 250.6, 29.4), (165.8, 259.5, 49.1), bevel=0.15)
    # left clear bin (cardboard inside, a black umbrella handle)
    clear_bin(b, 141.0, 242.8, 17.5, 164.0, 259.0, 29.0)
    box(b, "kraft", (143.0, 245.0, 17.7), (160.0, 257.0, 27.0))
    box(b, "kraft_dark", (142.0, 246.0, 17.7), (142.6, 256.0, 25.5))
    cyl(b, "cord", (146.0, 251.5, 24.0), 0.45, 9.0, axis="X", seg=8, rz=-25, ry=12)
    # big clear bin of clip hangers, a white mailer box at the back
    clear_bin(b, 140.5, 219.5, 17.5, 156.9, 242.5, 29.0)
    box(b, "mail_white", (148.5, 224.0, 17.7), (156.4, 240.0, 26.0))
    box(b, "mail_red", (148.4, 224.0, 24.0), (148.5, 240.0, 24.6))
    rng = random.Random(15)
    for i in range(9):
        hanger(b, 141.6 + i * 0.75, 231.0 + rng.uniform(-3.5, 3.5), 20.0 + rng.uniform(0, 5.0),
               rng.uniform(-35, 35))
    # grey cooler bag across both lids
    pbox(b, "cooler_grey", (141.0, 235.4, 29.3), (151.5, 250.4, 46.6), "cooler_front", bevel=0.8)
    box(b, "cooler_black", (140.8, 235.2, 46.5), (151.7, 250.6, 49.0), bevel=0.5)
    sweep(b, "cooler_black", [(146.0, 238.5, 48.9), (146.0, 239.5, 50.6), (146.0, 243.0, 51.2),
                              (146.0, 246.5, 50.6), (146.0, 247.5, 48.9)], [(-0.7, -0.12), (0.7, -0.12),
                                                                           (0.7, 0.12), (-0.7, 0.12)],
          up=(1, 0, 0))
    box(b, "trim_black", (140.9, 236.5, 29.3), (141.4, 249.3, 30.8))
    box(b, "teal", (141.1, 237.0, 28.2), (141.5, 246.0, 29.4), rx=8)                 # blue strap end
    # black file box (grey lid, blank label)
    box(b, "file_black", (140.5, 222.0, 29.0), (151.8, 236.3, 39.0), bevel=0.4)
    box(b, "lid_grey", (140.3, 221.8, 38.8), (152.0, 236.5, 40.3), bevel=0.3)
    pbox(b, "label_white", (140.32, 226.6, 31.6), (140.5, 232.0, 36.4), "file_label")
    # copy-paper case, purifier and its cord
    pbox(b, "ream_white", (139.6, 223.5, 40.3), (157.1, 234.75, 48.9), "ream_end", sides="ream_side",
         top="ream_white", bevel=0.1)
    cyl(b, "purifier_grille", (145.6, 229.6, 48.9), 3.35, 6.6, seg=16, cap="purifier")
    cyl(b, "purifier", (145.6, 229.6, 55.5), 3.35, 4.7, seg=16)
    cyl(b, "pack_grey", (145.6, 229.6, 60.2), 2.6, 0.12, seg=16)
    sweep(b, "cord", common.smooth_path([(148.6, 230.5, 49.2), (150.5, 234.0, 50.6), (149.0, 238.5, 49.4),
                                         (146.5, 241.5, 49.3), (145.0, 244.0, 49.3)], 4),
          CORD)
    # plastic grocery bags piled behind the purifier: crumpled, roundish, set back
    for i, (lo, hi) in enumerate((((149.5, 230.0, 46.5), (160.0, 240.5, 57.5)),
                                  ((150.0, 236.0, 49.3), (161.5, 245.5, 59.0)),
                                  ((152.0, 226.5, 55.0), (163.0, 236.0, 64.5)),
                                  ((153.5, 238.0, 57.5), (163.5, 247.0, 65.0)))):
        lump(b, "bag_white", lo, hi, seed=5 + i * 7, round_=0.75, amp=0.35, freq=3.5, cuts=4)
    # brown carton under the "catering" box (lettering left off)
    box(b, "box_brown", (141.5, 243.0, 49.1), (159.5, 259.0, 52.1), bevel=0.15)
    box(b, "catering", (141.5, 241.5, 52.1), (159.5, 259.5, 62.6), bevel=0.15)
    box(b, "catering", (141.3, 241.5, 62.4), (141.5, 259.5, 64.4), ry=-30, pivot=(141.5, 250.0, 62.5))

    # --- right (south) stack --------------------------------------------------------
    box(b, "lock_black", (140.0, 214.5, 0.0), (153.0, 224.0, 9.5), bevel=0.2)
    for lo, hi in (((139.9, 214.4, 9.0), (153.1, 224.1, 9.7)), ((139.9, 214.4, 0.0), (140.3, 224.1, 0.6)),
                   ((139.9, 214.4, 0.0), (140.3, 214.9, 9.7)), ((139.9, 223.6, 0.0), (140.3, 224.1, 9.7)),
                   ((139.85, 214.4, 6.8), (140.3, 224.1, 7.3))):
        box(b, "alu", lo, hi)
    box(b, "alu", (139.6, 218.0, 7.6), (140.0, 220.5, 9.0))
    pbox(b, "kraft", (139.6, 212.0, 9.7), (151.6, 225.4, 20.2), "rugged_front", top="rugged_top", bevel=0.12)
    pbox(b, "kraft", (152.0, 211.0, 0.0), (165.5, 226.0, 24.5), "moving_front", bevel=0.15)
    box(b, "teal", (143.0, 225.6, 0.0), (157.0, 226.8, 16.5))
    lump(b, "navy_bag", (141.5, 210.5, 24.4), (157.0, 222.0, 42.5), seed=7, round_=0.3, amp=0.06,
         faces={"+Z": "trim_black"})
    box(b, "label_white", (141.25, 211.6, 32.0), (141.6, 212.4, 35.0), rx=4)
    # red/black duffel standing diagonally: grey drawstring end up to the north, black end
    # panels, a black band round the middle
    lump(b, "duffel_red", (141.5, 213.5, 39.5), (154.5, 226.5, 63.5), seed=8, round_=0.75, amp=0.06,
         rx=-38, faces={"+Z": "duffel_grey", "-Z": "duffel_black"})
    lump(b, "duffel_black", (141.3, 213.3, 49.5), (154.7, 226.7, 52.5), seed=13, round_=0.8, amp=0.02,
         cuts=2, rx=-38)
    sweep(b, "cord", [(142.0, 222.0, 60.5), (143.5, 219.0, 57.5), (142.5, 214.0, 55.0)],
          CORD)
    lump(b, "tan_bag", (145.5, 211.0, 51.0), (157.0, 220.0, 60.5), seed=9, round_=0.45, amp=0.15, rx=-18)
    lump(b, "navy_bag", (147.0, 214.5, 57.0), (164.5, 229.0, 65.4), seed=10, round_=0.6, amp=0.18, sag=0.2)
    lump(b, "black_bag", (144.0, 202.6, 22.0), (163.0, 210.4, 52.0), seed=11, round_=0.3, amp=0.07)

    # --- floor, front ---------------------------------------------------------------
    pbox(b, "label_white", (139.0, 235.5, 0.0), (146.0, 248.5, 14.0), "massager_front", bevel=0.1)
    box(b, "label_white", (139.2, 235.5, 14.0), (145.8, 235.68, 19.0), rx=-18, pivot=(142.5, 235.6, 14.0))
    lump(b, "massager_black", (145.8, 236.0, 0.3), (154.0, 252.0, 14.2), seed=12, round_=0.3, amp=0.06)
    pbox(b, "red_box", (140.5, 228.0, 0.0), (148.5, 235.2, 10.0), "redbox_front", top="red_box", bevel=0.1)
    box(b, "mail_white", (141.0, 229.0, 10.0), (149.5, 232.0, 12.4), rz=32, ry=-12)
    box(b, "mail_red", (148.8, 230.0, 10.6), (149.3, 231.6, 12.0), rz=32, ry=-12, pivot=(145.25, 230.5, 11.2))
    box(b, "orange_box", (148.6, 226.9, 0.0), (157.0, 236.0, 8.5), bevel=0.1)
    # past the opening: two plain cartons on the floor
    box(b, "kraft", (145.0, 262.0, 0.0), (165.5, 282.0, 16.0), bevel=0.15)
    box(b, "kraft_dark", (147.0, 264.0, 16.0), (163.0, 280.0, 27.0), bevel=0.15)

    return [b.to_object(NAME, coll)]


def K_strap():
    return [(-0.6, -0.08), (0.6, -0.08), (0.6, 0.08), (-0.6, 0.08)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA          # preview only
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    planar = {r: K.planar_x(*v) for r, v in PRINTED.items() if v}
    # the paper case's long sides and the purifier grille
    planar["ream_side"] = ("+Y", (K.m(-157.1), K.m(-139.6)), (K.m(40.3), K.m(48.9)))
    planar["purifier_grille"] = K.planar_x(226.25, 232.95, 48.9, 55.5)
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: (clear if r == CLEAR else mat) for r in REGIONS})
