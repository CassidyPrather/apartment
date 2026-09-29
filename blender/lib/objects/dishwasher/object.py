"""Built-in dishwasher: white door and kick plate under an almond (cream) control band. The
band is a cream frame around a white inset panel: a row of long vent slots along its top
rim with a small cream latch tab, a cream dial with a pointer ridge and a small rocker on
the right, and a small maker badge at the lower left (parody "grumbleworks", the same
maker badge as the range). The tub body is hidden in the cabinet run.

Source of truth: scripted. Size from the living-room/kitchen LiDAR survey, layout and
colour from the survey crops (dishwasher_1-3) and the close capture frames
(wide_..._004117/004119/003847). Wear, as seen: the band is yellowed almond and there is a
faint grey smudge low on the right of the door.
Origin on the floor at the centre of the footprint (door included); front faces -Y.
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
PANEL_H = 7.5       # PHOTO cream control band (photos look down on it; corrected for perspective)
DIAL = (5.4, 1.1, 29.6)   # PHOTO dial x offset from centre, radius, z
ROCKER_X = 8.1      # PHOTO small rocker right of the dial
LATCH_X = 0.4       # PHOTO latch tab in the top rim
GAP = 0.25          # EST

NAME = "dishwasher"
ATLAS = {
    "name": "dishwasher",
    "size": 512,
    "regions": {
        "panel": (0, 0, 512, 160),
        "door": (0, 160, 256, 256),
        "white": (256, 160, 128, 128),
        "slot": (384, 160, 64, 64),
        "tub": (448, 160, 64, 64),
        "dial": (256, 288, 128, 128),
        "cream": (384, 288, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dishwasher": {"atlas": "dishwasher", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 35, 25, 0.9), ("photo_high", 20, 40, 0.8)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0, seg=2: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg)
    yf = y0 + DOOR_T
    bx("tub", (x0 + 0.5, yf, 0.0), (x1 - 0.5, y1, H - 0.2))
    # kick plate, recessed a little
    bx("white", (x0 + 0.3, y0 + 0.8, 0.3), (x1 - 0.3, yf, KICK_H - GAP))
    # door panel and the control band on top (both planar decals)
    zb = H - PANEL_H
    bx("door", (x0 + 0.1, y0 + 0.3, KICK_H), (x1 - 0.1, yf, zb - 0.1), 0.25, 1)
    bx("panel", (x0, y0, zb), (x1, yf, H), 0.3, 1)
    # grip lip under the band, latch tab in the top rim
    bx("cream", (x0 + 1.5, y0 - 0.25, zb - 0.35), (x1 - 1.5, y0 + 0.3, zb + 0.05), 0.1, 1)
    bx("cream", (LATCH_X - 0.55, y0 - 0.35, H - 2.0), (LATCH_X + 0.55, y0 + 0.1, H - 1.15), 0.1, 1)
    # dial with a pointer ridge, rocker switch
    dx, dr, dz = DIAL
    b.cylinder("dial", (m(dx), m(y0 - 0.25), m(dz)), m(dr), m(0.5), axis="Y", segments=14)
    bx("dial", (dx - 0.17, y0 - 0.8, dz - dr * 0.85), (dx + 0.17, y0 - 0.3, dz + dr * 0.85))
    bx("white", (ROCKER_X - 0.25, y0 - 0.2, dz - 0.45), (ROCKER_X + 0.25, y0 + 0.1, dz + 0.45))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    x0, x1 = m(-W / 2), m(W / 2)
    common.atlas_uvs(ob, ATLAS, planar={
        "panel": ("-Y", (x0, x1), (m(H - PANEL_H), m(H))),
        "door": ("-Y", (x0, x1), (m(KICK_H), m(H - PANEL_H))),
    })
    common.collapse_materials(ob, {r: mat for r in REGIONS})
