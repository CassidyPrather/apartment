"""Plastic drawers: a six-drawer white-framed tower with clear drawer fronts (clothes
showing through) on casters, a dark board laid across its top carrying a black
multi-zip shoulder bag, a white lidded plastic box and a small tissue box, and a blue
plastic wastebasket tucked in beside it (under the headboard shelf).

Source of truth: scripted from the LiDAR survey (tower plan y 60-76, x 257.4-272.7,
top 34; board and bag to z 44 at y ~67-73; basket y 78-88) and the survey crops.
Origin on the floor; front faces -Y. Place at plan (265, 75), rotation -90 (front faces
west, local +X is south: plan y = 75 - x, plan x = 265 + y).

Dimensions (inches):
  tower 16 W x 15.3 D x 34 H, centre x +7     SCAN
  6 drawers, casters 1.5 tall                  photo count / EST
  board 20 W x 16 D x 0.5 at z 34              SCAN / photo
  bag 11 W x 7 D x 9.5 H on the board          SCAN top z 44
  white box 6 x 7 x 4, tissue box 3.5 x 4 x 5  EST
  wastebasket 10 W x 13 D x 12 H, centre x -8  SCAN (y 78-88) / EST height
"""

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "plastic_drawers"
TX0, TX1 = -1.0, 15.0
TY0, TY1 = -7.6, 7.7
TOP = 34.0
N = 6
CASTER = 1.5

ATLAS = {
    "name": "plastic_drawers",
    "size": 512,
    "regions": {
        "white": (0, 0, 128, 128),
        "clear": (128, 0, 128, 128),
        "clothes": (256, 0, 256, 128),
        "board": (0, 128, 128, 128),
        "bag": (128, 128, 128, 128),
        "zip": (256, 128, 64, 64),
        "caster": (320, 128, 64, 64),
        "tissue": (384, 128, 128, 128),
        "basket": (0, 256, 128, 128),
        "box_lid": (128, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {
    "plastic_drawers": {"atlas": "plastic_drawers", "mode": "opaque", "tiled": False},
    "plastic_drawers_clear": {"atlas": "plastic_drawers", "mode": "transparent", "alpha": 0.4},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 335, 22, 0.8)]


def bx(b, r, lo, hi, bev=0.0):
    b.box(r, tuple(map(m, lo)), tuple(map(m, hi)), bevel=m(bev))


def build(coll):
    b = common.Builder(REGIONS)
    # casters
    for x in (TX0 + 1.2, TX1 - 1.2):
        for y in (TY0 + 1.2, TY1 - 1.2):
            b.cylinder("caster", (m(x), m(y), m(CASTER / 2)), m(0.7), m(CASTER), axis="X", segments=8)
    z0 = CASTER
    # frame: base, sides, back, top
    bx(b, "white", (TX0, TY0, z0), (TX1, TY1, z0 + 0.6))
    for x0, x1 in ((TX0, TX0 + 0.5), (TX1 - 0.5, TX1)):
        bx(b, "white", (x0, TY0, z0), (x1, TY1, TOP))
    bx(b, "white", (TX0, TY1 - 0.3, z0), (TX1, TY1, TOP))
    bx(b, "white", (TX0, TY0, TOP - 0.6), (TX1, TY1, TOP), 0.15)
    # drawers: clear front, white lip handle, clothes inside
    dh = (TOP - 0.6 - z0 - 0.6) / N
    for i in range(N):
        zb = z0 + 0.6 + i * dh
        bx(b, "clothes", (TX0 + 1.0, TY0 + 1.5, zb + 0.4), (TX1 - 1.0, TY1 - 1.0, zb + dh * 0.7))
        bx(b, "clear", (TX0 + 0.5, TY0 + 1.0, zb + 0.2), (TX1 - 0.5, TY1 - 0.4, zb + 0.4))    # tray floor
        bx(b, "clear", (TX0 + 0.55, TY0 - 0.1, zb + 0.15), (TX1 - 0.55, TY0 + 0.3, zb + dh - 0.6))
        bx(b, "white", (TX0 + 0.55, TY0 - 0.5, zb + dh - 0.7), (TX1 - 0.55, TY0 + 0.3, zb + dh - 0.1), 0.1)
    # board across the top
    bx(b, "board", (-3.0, -8.2, TOP), (17.0, 8.0, TOP + 0.5))
    bt = TOP + 0.5
    # black shoulder bag, strap down the front left
    bx(b, "bag", (0.0, -3.5, bt), (11.0, 3.5, bt + 8.5), 1.8)
    bx(b, "bag", (1.0, -3.9, bt + 1.0), (10.0, -2.8, bt + 7.0), 0.6)     # front pocket
    b.sweep("bag", [(m(1.2), m(-4.0), m(bt + 7.5)), (m(0.2), m(-5.0), m(bt + 1.0)),
                    (m(0.2), m(-8.6), m(bt - 1.0)), (m(0.0), m(-8.8), m(bt - 10.0)),
                    (m(1.0), m(-8.4), m(bt - 13.5))],
            common.rect_profile(m(1.3), m(0.15)), up=(0, 1, 0))
    for zz in (bt + 6.5, bt + 4.0):
        bx(b, "zip", (2.0, -4.1, zz), (2.8, -3.8, zz + 1.2))
        bx(b, "zip", (7.5, -4.1, zz - 0.5), (8.3, -3.8, zz + 0.7))
    # white lidded box and a small tissue box behind it
    bx(b, "white", (10.8, -6.0, bt), (16.6, 1.0, bt + 3.4), 0.2)
    bx(b, "box_lid", (10.6, -6.2, bt + 3.4), (16.8, 1.2, bt + 4.2), 0.2)
    bx(b, "tissue", (11.5, 2.5, bt), (15.0, 6.5, bt + 5.0), 0.05)
    # blue wastebasket
    bx0, bx1, by0, by1, bh = -13.0, -3.0, -6.5, 6.5, 12.0
    w = 0.3
    bx(b, "basket", (bx0, by0, 0), (bx1, by1, 0.3))
    bx(b, "basket", (bx0, by0, 0), (bx0 + w, by1, bh), 0.1)
    bx(b, "basket", (bx1 - w, by0, 0), (bx1, by1, bh), 0.1)
    bx(b, "basket", (bx0, by0, 0), (bx1, by0 + w, bh), 0.1)
    bx(b, "basket", (bx0, by1 - w, 0), (bx1, by1, bh), 0.1)
    bx(b, "clothes", (bx0 + 0.5, by0 + 0.5, 0.3), (bx1 - 0.5, by1 - 0.5, 6.0))     # paper inside
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material("plastic_drawers_clear", ATLAS)
    # preview only: show the clear plastic as see-through in the Blender renders
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = MATERIALS["plastic_drawers_clear"]["alpha"]
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: (clear if r == "clear" else mat) for r in REGIONS})
