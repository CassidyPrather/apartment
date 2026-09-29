"""Headboard bookcase: a solid golden-oak cubby bookcase standing behind the bed as its
headboard. Two open bays split by a divider, a fixed shelf at mattress height with soft
clothes stored on it, a lower shelf behind the bed, a toe kick. On top: a white power
strip with plugs, an over-ear headset with a mic boom, a VR headset with its strap and
a spare strap, and a few cables looping between them and hanging down the front.
All items are plain dark shapes with no markings.

Refinement (scan3 close-ups 88386375752, 88399009696, 88401443145 and capture frame
wide_..012051): thick top overhanging the front with a rounded edge, a rail under it,
thick side stiles proud of rounded shelf edges, an apron board under the upper shelf,
oak (not dark) back panel. No hardware anywhere.

Source of truth: scripted from the bedroom LiDAR survey (registered.npz, plan inches)
and the survey crops. Front faces -Y; origin on the floor at the footprint centre.
Place at plan (267.9, 105.25), rotation -90 (front faces west, local +X = south): side
panels at plan y 82 and 128.5, front face x 261.4, back on the east wall (274.4).
"""

import math

import common

IN = 0.0254


def m(v):
    return v * IN


W = 46.5            # SCAN side panels at plan y 82 and ~128.5 (LiDAR + splat top edge)
D = 13.0            # SCAN front face x 261.4 to the wall at 274.4
H = 39.5            # SCAN flat top at z 39-39.5 (LiDAR and splat histograms); items to ~46
T = 0.75            # EST board (back, lower shelves)
TOP_T = 1.25        # EST photo: top edge ~ the shelf edge's height
OVER = 0.75         # EST photo: top overhangs the side stiles at the front
SIDE_T = 1.25       # EST photo: side stile ~ as wide as the top is thick
SIDE_IN = 0.4       # EST photo: top overhangs the sides slightly
SHELF_T = 1.0       # EST photo: rounded shelf edge
SHELF_SET = 0.4     # EST photo: shelf edge set back from the side stiles
RAIL_H = 1.25       # EST photo: rail under the top
APRON_H = 4.0       # EST photo (88399009696): board under the upper shelf
DIV_X = 2.75        # SCAN divider at plan y 102.5 (wood-coloured points, both depth bands)
SHELF_Z = 30.0      # SCAN shelf line in the front elevation; photo: just above the mattress
LOW_Z = 15.5        # EST lower shelf (hidden behind the bed)
KICK = 2.5          # EST toe kick

NAME = "headboard_bookcase"
ATLAS = {
    "name": "headboard_bookcase",
    "size": 1024,
    "regions": {
        "oak": (0, 0, 512, 512),
        "oak_edge": (512, 0, 256, 256),
        "interior": (768, 0, 256, 256),
        "strip": (512, 256, 128, 128),
        "plastic": (640, 256, 128, 128),
        "cable": (768, 256, 128, 128),
        "cable_white": (896, 256, 128, 128),
        "accent": (512, 384, 128, 128),
        "cloth_mauve": (640, 384, 128, 128),
        "cloth_maroon": (768, 384, 128, 128),
        "cloth_dark": (896, 384, 128, 128),
        "strap": (512, 512, 256, 128),
        "cushion": (768, 512, 256, 128),
        "oak_v": (0, 512, 512, 512),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front", 0, 14, 1.0), ("photo_front_left", 340, 20, 1.0),
         ("top_items", 0, 55, 0.55), ("photo_s3_150", 30, 38, 0.8)]

X0, X1 = -W / 2, W / 2
Y0, Y1 = -D / 2, D / 2


def lump(b, region, cx, cy, z0, w, d, h, seg=6):
    """A soft heap of folded cloth: a squashed, rounded blob."""
    b.box(region, (m(cx - w / 2), m(cy - d / 2), m(z0)), (m(cx + w / 2), m(cy + d / 2), m(z0 + h)),
          bevel=m(min(w, d, h) * 0.45), segments=2)


def cable(b, region, pts, r=0.12):
    prof = common.circle_profile(m(r), 5)
    path = common.smooth_path([tuple(map(m, p)) for p in pts], samples=4)
    b.sweep(region, path, prof)


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    # carcass: rounded solid-oak top overhanging thick side stiles
    b.box("oak", tuple(map(m, (X0, Y0, H - TOP_T))), tuple(map(m, (X1, Y1, H))),
          bevel=m(0.4), segments=2)
    cf = Y0 + OVER                                   # carcass front plane (stile faces)
    sx0, sx1 = X0 + SIDE_IN + SIDE_T, X1 - SIDE_IN - SIDE_T   # inner faces of the sides
    for a0, a1 in ((X0 + SIDE_IN, sx0), (sx1, X1 - SIDE_IN)):
        b.box("oak_v", tuple(map(m, (a0, cf, 0))), tuple(map(m, (a1, Y1, H - TOP_T))),
              bevel=m(0.3), segments=2)
    bx("interior", (sx0, Y1 - 0.25, KICK), (sx1, Y1, H - TOP_T))
    bx("oak", (sx0, cf + 0.25, H - TOP_T - RAIL_H), (sx1, cf + 1.0, H - TOP_T), 0.15)   # top rail
    bx("oak", (sx0, cf + 0.5, 0), (sx1, cf + 1.25, KICK))                              # toe kick
    sf = cf + SHELF_SET
    for z in (KICK + T, LOW_Z):
        bx("oak_edge", (sx0, sf, z - T), (sx1, Y1 - 0.25, z), 0.12)
    b.box("oak_edge", tuple(map(m, (sx0, sf, SHELF_Z - SHELF_T))),
          tuple(map(m, (sx1, Y1 - 0.25, SHELF_Z))), bevel=m(0.3), segments=2)
    bx("oak_v", (sx0, sf + 0.5, SHELF_Z - SHELF_T - APRON_H), (sx1, sf + 1.25, SHELF_Z - SHELF_T),
       0.08)                                                                            # apron
    for za, zb in ((KICK + T, LOW_Z - T), (LOW_Z, SHELF_Z - SHELF_T - APRON_H),
                   (SHELF_Z, H - TOP_T - RAIL_H)):
        b.box("oak_v", tuple(map(m, (DIV_X - 0.5, sf, za))), tuple(map(m, (DIV_X + 0.5, Y1 - 0.25, zb))),
              bevel=m(0.2), segments=1)

    # clothes kept in the bays (photo: maroon behind the pillow, mauve and black on the right)
    lump(b, "cloth_maroon", -12.0, 0.5, SHELF_Z, 16.0, 10.0, 5.5)
    lump(b, "cloth_dark", -19.0, 1.5, SHELF_Z, 5.0, 8.0, 4.0)
    lump(b, "cloth_mauve", 9.0, 0.5, SHELF_Z, 9.5, 10.0, 5.0)
    lump(b, "cloth_dark", 17.5, 1.0, SHELF_Z, 8.0, 9.5, 5.5)
    lump(b, "cloth_dark", -10.0, 0.5, LOW_Z, 18.0, 10.0, 6.0)
    lump(b, "cloth_mauve", 12.0, 0.5, LOW_Z, 14.0, 10.0, 4.5)

    # power strip with a few plugs (north end, local -X)
    zt = H
    bx("strip", (-20.0, 0.5, zt), (-6.5, 2.8, zt + 1.3), 0.3)
    for x in (-17.5, -14.5, -9.5):
        bx("plastic", (x - 0.6, 1.0, zt + 1.3), (x + 0.6, 2.3, zt + 2.6), 0.15)
    bx("plastic", (-12.2, 0.9, zt + 1.3), (-11.0, 2.4, zt + 2.2), 0.15)

    # over-ear headset lying on its side, mic boom up
    for x in (-0.5, 5.0):
        b.cylinder("plastic", (m(x), m(-0.5), m(zt + 1.9)), m(1.9), m(1.4), axis="X",
                   segments=14, cap_region="cushion")
    band = [(-0.5 + 5.5 * t, -0.5 + 1.2 * math.sin(math.pi * t),
             zt + 3.5 + 1.8 * math.sin(math.pi * t)) for t in [i / 8 for i in range(9)]]
    b.sweep("plastic", [tuple(map(m, p)) for p in band], common.rect_profile(m(1.2), m(0.5)))
    cable(b, "plastic", [(-1.2, -1.5, zt + 1.2), (-2.4, -2.5, zt + 3.0), (-2.6, -2.2, zt + 5.8)], 0.14)
    b.cylinder("plastic", (m(-2.6), m(-2.2), m(zt + 6.1)), m(0.35), m(0.8), segments=8)

    # VR headset: visor block with a face cushion, strap loop, and a spare strap
    hx, hy = 14.5, 0.5
    bx("plastic", (hx - 3.6, hy - 3.2, zt), (hx + 3.6, hy + 0.8, zt + 3.4), 0.9)
    bx("cushion", (hx - 3.0, hy + 0.8, zt + 0.3), (hx + 3.0, hy + 1.8, zt + 3.0), 0.5)
    ring = [(hx + 4.2 * math.cos(a), hy + 3.0 + 2.4 * math.sin(a), zt + 1.4 + 0.9 * math.cos(a))
            for a in [2 * math.pi * i / 14 for i in range(14)]]
    b.sweep("strap", [tuple(map(m, p)) for p in ring], common.rect_profile(m(1.3), m(0.3)),
            closed=True)
    ring2 = [(19.6 + 2.4 * math.cos(a), -1.5 + 2.2 * math.sin(a), zt + 1.0 + 0.6 * math.sin(2 * a))
             for a in [2 * math.pi * i / 12 for i in range(12)]]
    b.sweep("accent", [tuple(map(m, p)) for p in ring2], common.rect_profile(m(1.2), m(0.9)),
            closed=True)
    bx("plastic", (6.5, -2.5, zt), (10.0, 1.0, zt + 1.6), 0.5)    # a small dark pouch

    # cables: strip -> headset, strip -> VR headset, one down the back, two down the front
    cable(b, "cable", [(-9.5, 1.6, zt + 2.5), (-7.0, -1.0, zt + 0.2), (-3.5, -2.0, zt + 0.2),
                       (-1.2, -1.5, zt + 1.2)])
    cable(b, "cable", [(-14.5, 1.6, zt + 2.5), (-12.0, -2.0, zt + 0.2), (-4.0, -4.5, zt + 0.2),
                       (-0.5, Y0 - 0.3, zt - 0.2), (0.5, Y0 - 0.5, zt - 3.5),
                       (1.2, Y0 - 0.4, SHELF_Z + 3.0)])
    cable(b, "cable_white", [(-17.5, 1.6, zt + 2.5), (-15.0, -3.0, zt + 0.2), (4.0, -4.0, zt + 0.2),
                             (6.8, Y0 - 0.3, zt - 0.3), (7.4, Y0 - 0.5, zt - 4.5),
                             (8.0, Y0 + 1.0, SHELF_Z + 5.5)], 0.1)
    cable(b, "cable", [(-18.0, 2.0, zt + 1.0), (-19.0, Y1 - 0.4, zt + 0.3),
                       (-19.3, Y1 + 0.2, zt - 1.0), (-19.3, Y1 + 0.2, zt - 10.0)])
    cable(b, "cable", [(-9.5, 1.8, zt + 2.2), (-2.0, 3.5, zt + 0.2), (8.0, 3.8, zt + 0.2),
                       (12.0, 1.5, zt + 0.5)])
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
