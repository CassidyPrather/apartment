"""Built-in dishwasher: white door with a cream control band across the top (vent slots
on the left, a round dial and a push button on the right), white kick plate, and the
tub body hidden in the cabinet run. No badge (plain appliance front).

Source of truth: scripted. Size from the living-room/kitchen LiDAR survey, layout and
colour from the survey photo crops. Origin on the floor at the centre of the footprint
(door included); front faces -Y.
Place at plan (12.75, 200.5), rotation 90 (front faces east): x 0-25.5, y 188.5-212.5.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 24.0            # SCAN
D = 25.5            # SCAN (tub to wall + door)
H = 34.0            # SCAN (under the 34.5 counter underside)
DOOR_T = 2.0        # EST
KICK_H = 4.0        # PHOTO/EST white kick plate
PANEL_H = 6.0       # PHOTO cream control band at the top of the door
DIAL = (8.5, 1.4)   # PHOTO/EST dial x offset from centre, radius
GAP = 0.25          # EST

NAME = "dishwasher"
ATLAS = {
    "name": "dishwasher",
    "size": 512,
    "regions": {
        "white": (0, 0, 256, 256),
        "cream": (256, 0, 256, 256),
        "slot": (0, 256, 128, 128),
        "tub": (128, 256, 128, 128),
        "dial": (256, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dishwasher": {"atlas": "dishwasher", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 35, 25, 0.9)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    yf = y0 + DOOR_T
    bx("tub", (x0 + 0.5, yf, 0.0), (x1 - 0.5, y1, H - 0.2))
    # kick plate, recessed a little
    bx("white", (x0 + 0.3, y0 + 0.8, 0.3), (x1 - 0.3, yf, KICK_H - GAP))
    # door: main panel and the control band on top
    zb = H - PANEL_H
    bx("white", (x0 + 0.1, y0 + 0.3, KICK_H), (x1 - 0.1, yf, zb - 0.1), 0.25)
    bx("cream", (x0, y0, zb), (x1, yf, H), 0.3)
    # vent slots on the left of the band, the dial and a button on the right
    for i in range(6):
        sx = x0 + 2.0 + i * 1.3
        bx("slot", (sx, y0 - 0.02, zb + 3.0), (sx + 0.7, y0 + 0.2, zb + 4.6))
    dx, dr = DIAL
    b.cylinder("dial", (m(dx), m(y0 - 0.4), m(zb + PANEL_H / 2)), m(dr), m(0.8), axis="Y", segments=16)
    bx("dial", (dx + 2.6, y0 - 0.3, zb + 2.2), (dx + 3.4, y0 + 0.1, zb + 3.0))
    # finger lip under the band
    bx("cream", (x0 + 2.0, y0 - 0.6, zb - 0.6), (x1 - 2.0, y0 + 0.3, zb))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
