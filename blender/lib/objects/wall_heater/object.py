"""Wall heater: small white recessed-can wall heater under the north end of the TV:
a white frame and faceplate, horizontal louvres behind the grille opening,
split into upper and lower halves by a bar.

Source of truth: scripted. Size and height come from rays cast through two source
frames onto the wall plane (heater y 92.8-102.3) and the heater scaled against the TV in a second frame
(top ~6 in under the TV); the LiDAR
shows nothing proud of the wall there, so it sits under 1 in proud.

Origin: on the FLOOR at the wall plane, below the heater's centre (the mounting height is
baked in: the heater spans z 15..33). The wall is y = 0 and the front faces -Y.
Place at plan (134, 97.5), Z 0, rotation -90.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 9.5             # SCAN (frame rays and TV scale agree)
H = 18.0            # SCAN rays 18; the photo aspect agrees (~1:1.9)
Z0 = 15.0           # SCAN rays 14, TV-relative scaling ~20: split, top at 33
D = 0.75            # EST (LiDAR: < 1 in proud)
FRAME = 0.8         # EST frame border
BAR = 0.6           # EST centre divider

NAME = "wall_heater"
ATLAS = {
    "name": "wall_heater",
    "size": 256,
    "regions": {
        "frame": (0, 0, 128, 128),
        "louvres": (128, 0, 128, 256),
        "dark": (0, 128, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"wall_heater": {"atlas": "wall_heater", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_left", 330, 5, 0.8)]


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    x0, x1, z0, z1 = -W / 2, W / 2, Z0, Z0 + H
    f = FRAME
    bx("frame", (x0, -D, z0), (x1, -D + 0.35, z0 + f), 0.12)
    bx("frame", (x0, -D, z1 - f), (x1, -D + 0.35, z1), 0.12)
    bx("frame", (x0, -D, z0 + f), (x0 + f, -D + 0.35, z1 - f), 0.12)
    bx("frame", (x1 - f, -D, z0 + f), (x1, -D + 0.35, z1 - f), 0.12)
    zm = (z0 + z1) / 2
    bx("frame", (x0 + f, -D + 0.1, zm - BAR / 2), (x1 - f, -D + 0.35, zm + BAR / 2))
    bx("frame", (x0 + 0.2, -D + 0.35, z0 + 0.2), (x1 - 0.2, 0.0, z1 - 0.2))    # body to wall
    # louvres: a single recessed plate, planar-mapped with the slat texture
    bx("louvres", (x0 + f, -D + 0.3, z0 + f), (x1 - f, -D + 0.34, z1 - f))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    planar = {"louvres": ("-Y", (m(-W / 2 + FRAME), m(W / 2 - FRAME)), (m(Z0 + FRAME), m(Z0 + H - FRAME)))}
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
