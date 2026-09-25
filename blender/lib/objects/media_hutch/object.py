"""Media hutch: dark cherry bookcase in the living room's SE corner. Solid raised-panel
doors and two drawers below, then three OPEN shelf bays (no doors) holding stacks of
flat-lying board-game boxes and small plain objects, an arched valance over the top bay,
a slim crown; a few game boxes stacked on top.

Source of truth: scripted from the living-room LiDAR survey (registered.npz, layout
inches) and the survey crops. Origin on the floor at the footprint centre; front faces -Y.
Place at plan (124.75, 17.75), rotation -90 (front faces west): the carcass back sits on
the center wall face (x 134), its south side 2.5 in off the window wall. The north side
panel measures square to the wall within 0.3 deg in the LiDAR, so -90 exactly.
"""

import random

import common

IN = 0.0254


def m(v):
    return v * IN


W = 31.0            # SCAN side panels at y 2.5 and 33.0 in the LiDAR, centre stile at 17
D = 18.5            # SCAN face frame x 116.8 to wall 135.3 (north side panel extent)
H = 80.0            # SCAN side panel top ~76-80, crown; games on top reach ~86
BASE_H = 4.0        # EST plinth
LOWER_TOP = 25.0    # EST lower doors top (photo: drawer band at ~25-31)
RAIL_TOP = 31.0     # EST
SHELVES = (44.0, 57.0)   # SCAN horizontal lines in the front elevation
DOOR_TOP = 67.0     # EST where the valance arch springs (top bay)
VAL_TOP = 76.0      # EST valance top / crown bottom (photo: slim crown)
STILE = 2.0         # EST face-frame stile width
SIDE_T = 0.75       # EST panel thickness
DOOR_T = 0.75       # EST
CROWN = 1.5         # EST crown overhang
ARCH_RISE = 5.0     # EST arch rise in the valance (photo)

NAME = "media_hutch"
ATLAS = {
    "name": "media_hutch",
    "size": 1024,
    "regions": {
        "wood": (0, 0, 512, 512),
        "wood_end": (512, 0, 256, 256),
        "interior": (768, 0, 256, 256),
        "ceramic": (512, 256, 128, 64),
        "dark_obj": (512, 320, 128, 64),
        "brass": (640, 256, 128, 128),
        "games_top": (768, 256, 256, 256),
        "panel": (0, 512, 512, 512),
        "game_0": (512, 512, 128, 128),
        "game_1": (640, 512, 128, 128),
        "game_2": (768, 512, 128, 128),
        "game_3": (896, 512, 128, 128),
        "game_4": (512, 640, 128, 128),
        "game_5": (640, 640, 128, 128),
        "game_6": (768, 640, 128, 128),
        "game_7": (896, 640, 128, 128),
        "tin": (512, 768, 256, 256),
    },
}
REGIONS = list(ATLAS["regions"])
GAME_REGIONS = [f"game_{i}" for i in range(8)]
OBJ_REGIONS = ["ceramic", "dark_obj", "tin"]
MATERIALS = {"media_hutch": {"atlas": "media_hutch", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_nw", 300, 8, 0.9), ("front_low", 0, 0, 0.8), ("photo_front_nw", 330, 10, 0.9)]

X0, X1 = -W / 2, W / 2
Y0, Y1 = -D / 2, D / 2
# inner opening between the face-frame stiles
IX0, IX1 = X0 + STILE, X1 - STILE


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    fy = Y0 + 0.75                                   # carcass front (face frame depth)
    # carcass: sides, back, top, bottom
    bx("wood", (X0, fy, BASE_H), (X0 + SIDE_T, Y1, VAL_TOP))
    bx("wood", (X1 - SIDE_T, fy, BASE_H), (X1, Y1, VAL_TOP))
    bx("interior", (X0 + SIDE_T, Y1 - 0.5, BASE_H), (X1 - SIDE_T, Y1, VAL_TOP))
    bx("interior", (X0 + SIDE_T, fy, RAIL_TOP - 0.75), (X1 - SIDE_T, Y1 - 0.5, RAIL_TOP))
    for z in SHELVES:
        bx("wood_end", (X0 + SIDE_T, fy + 1.0, z - 0.75), (X1 - SIDE_T, Y1 - 0.5, z))
    bx("interior", (X0 + SIDE_T, fy, VAL_TOP - 0.75), (X1 - SIDE_T, Y1 - 0.5, VAL_TOP))
    # plinth with a small base moulding
    bx("wood", (X0 - 0.25, Y0 - 0.25, 0.0), (X1 + 0.25, Y1, BASE_H), 0.15)
    bx("wood_end", (X0 - 0.5, Y0 - 0.5, BASE_H - 0.6), (X1 + 0.5, Y1, BASE_H), 0.2)
    # face frame: stiles full height, rail band
    bx("wood", (X0, Y0, BASE_H), (IX0, fy, VAL_TOP))
    bx("wood", (IX1, Y0, BASE_H), (X1, fy, VAL_TOP))
    bx("wood", (IX0, Y0, LOWER_TOP), (IX1, fy, RAIL_TOP), 0.1)
    bx("wood_end", (IX0, Y0 - 0.25, RAIL_TOP - 0.6), (IX1, fy, RAIL_TOP), 0.1)
    dwr = (IX1 - IX0) / 2
    for i in range(2):
        a0, a1 = IX0 + i * dwr + 0.15, IX0 + (i + 1) * dwr - 0.15
        bx("panel", (a0, Y0 - 0.5, LOWER_TOP + 0.3), (a1, Y0 + 0.1, RAIL_TOP - 0.9), 0.2)
        b.cylinder("brass", (m((a0 + a1) / 2), m(Y0 - 0.8), m((LOWER_TOP + RAIL_TOP - 0.6) / 2)),
                   m(0.4), m(0.7), axis="Y", segments=10)
    # lower doors: frame + recessed raised panel + brass knob
    dw = (IX1 - IX0) / 2
    for i in range(2):
        a0, a1 = IX0 + i * dw + 0.1, IX0 + (i + 1) * dw - 0.1
        z0, z1 = BASE_H + 0.3, LOWER_TOP - 0.2
        dy0 = Y0 - DOOR_T + 0.5
        f = 2.25
        bx("wood", (a0, dy0, z0), (a1, dy0 + DOOR_T, z0 + f))
        bx("wood", (a0, dy0, z1 - f), (a1, dy0 + DOOR_T, z1))
        bx("wood", (a0, dy0, z0 + f), (a0 + f, dy0 + DOOR_T, z1 - f))
        bx("wood", (a1 - f, dy0, z0 + f), (a1, dy0 + DOOR_T, z1 - f))
        bx("panel", (a0 + f, dy0 + 0.3, z0 + f), (a1 - f, dy0 + DOOR_T, z1 - f), 0.25)
        kx = a1 - 1.3 if i == 0 else a0 + 1.3
        b.cylinder("brass", (m(kx), m(dy0 - 0.35), m(z1 - 4.0)), m(0.45), m(0.7), axis="Y",
                   segments=10)
    # arched valance: stepped strips whose lower edge follows the arch (low at the sides)
    n = 12
    sw = (IX1 - IX0) / n
    for k in range(n):
        xa, xb = IX0 + k * sw, IX0 + (k + 1) * sw
        t = ((xa + xb) / 2) / ((IX1 - IX0) / 2)
        zb = DOOR_TOP + 1.0 + ARCH_RISE * (1 - t * t) ** 0.5
        bx("wood", (xa, Y0, zb), (xb, fy, VAL_TOP))
    # stepped crown
    bx("wood_end", (X0 - 0.6, Y0 - 0.6, VAL_TOP), (X1 + 0.6, Y1, VAL_TOP + 1.5), 0.25)
    bx("wood", (X0 - CROWN, Y0 - CROWN, VAL_TOP + 1.5), (X1 + CROWN, Y1, H), 0.3)
    # shelf contents: stacks of flat-lying game boxes and small plain objects
    rng = random.Random(5)
    ix0, ix1 = X0 + SIDE_T + 0.3, X1 - SIDE_T - 0.3
    iy0, iy1 = fy + 1.2, Y1 - 0.8
    bays = [(RAIL_TOP, SHELVES[0] - 0.75), (SHELVES[0], SHELVES[1] - 0.75), (SHELVES[1], DOOR_TOP + 2.0)]
    for bi, (z0, z1) in enumerate(bays):
        x = ix0 + rng.uniform(0.0, 0.8)
        while x < ix1 - 2.5:
            if rng.random() < 0.72 and ix1 - x > 7.5:       # a stack of games
                w = min(rng.uniform(7.5, 11.5), ix1 - x)
                d = rng.uniform(8.0, 12.0)
                yb = iy1 - rng.uniform(0.0, 1.5)
                z = z0
                top = z1 - rng.uniform(1.0, 4.0)
                while True:
                    h = rng.uniform(1.6, 3.4)
                    if z + h > top:
                        break
                    jx = rng.uniform(-0.4, 0.4)
                    ww = w * rng.uniform(0.85, 1.0)
                    bx(rng.choice(GAME_REGIONS), (x + jx, yb - d, z), (x + jx + ww, yb, z + h))
                    z += h
                x += w + rng.uniform(0.3, 1.0)
            else:                                             # a small object
                kind = rng.random()
                cx = x + 1.8
                cy = iy0 + rng.uniform(1.5, 4.0)
                if kind < 0.4:
                    r, h = rng.uniform(1.0, 1.8), rng.uniform(3.0, 6.0)
                    b.cylinder(rng.choice(OBJ_REGIONS), (m(cx), m(cy), m(z0 + h / 2)), m(r), m(h),
                               segments=8)
                    x += 2 * r + 0.8
                else:
                    w, h = rng.uniform(2.5, 5.0), rng.uniform(2.0, 5.0)
                    bx(rng.choice(OBJ_REGIONS + GAME_REGIONS[:3]), (x, cy - 1.8, z0), (x + w, cy + 1.8, z0 + h))
                    x += w + 0.8
    # games stacked on top (loose boxes)
    tops = [(-13.5, -2.0, -6.0, 6.5, 2.2), (-13.0, -2.5, -6.5, 6.0, 2.6), (-1.0, 11.0, -7.0, 5.0, 2.4),
            (-0.5, 10.5, -6.0, 5.5, 2.0), (4.0, 14.0, -3.0, 7.0, 3.0)]
    zt = H
    stacks = {}
    for x0, x1, y0, y1, h in tops:
        key = round(x0 / 5)
        z0 = stacks.get(key, zt)
        bx("games_top", (x0, y0, z0), (x1, y1, z0 + h))
        stacks[key] = z0 + h
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
