"""Blankets heaped on the living-room couch, as a separate piece that drops onto it:
a chocolate fleece over the seat that hangs down the front, a dark leaf-print throw on
top of it toward the north arm, a white bunny-print blanket heaped over the north back
cushion and arm, and a blue-violet tie-dye blanket over the south back cushion.

Source of truth: scripted. Placement of each blanket from the colours of the survey
splat's top surface over the couch, colours from the photo crops; the fold shapes are
EST (soft bumps on a sheet laid over the couch's surface).

Same local frame and origin as `couch` (front -Y, local +X = north at plan rotation 90,
origin on the floor at the couch footprint centre), so it takes the couch's placement.
"""

import math

import atlas_layout
import common

IN = 0.0254


def m(v):
    return v * IN


# couch surface (inches, copied from objects/couch/object.py)
L, D = 87.0, 39.0
ARM_W, ARM_H = 9.5, 24.0
SEAT_H, BACK_H = 17.5, 33.0
BACK_FOOT_Y = 2.5
BACK_TOP_Y = 11.0
FRAME_Y, FRAME_H = 17.0, 30.0
FRONT = -D / 2
T = 0.45            # EST blanket thickness

NAME = "couch_blankets"
ATLAS = {
    "name": "couch_blankets",
    "size": 1024,
    "regions": {
        "brown_fleece": (0, 0, 512, 512),
        "leaf_print": (512, 0, 512, 512),
        "white_bunny": (0, 512, 512, 512),
        "blue_tiedye": (512, 512, 512, 512),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "none"
STATIC = True
VIEWS = [("from_north", 90, 18, 1.0), ("plan_top", 0, 89.9, 1.0)]

# (region, x range, y range (y below FRONT hangs down the front), grid, lift,
#  bumps [(x, y, height, radius)], wrinkle amplitude)
BLANKETS = [
    ("brown_fleece", (-34.0, 32.0), (-28.0, 6.0), (16, 11), 0.3,
     [(-18, -8, 1.2, 7), (4, -12, 1.0, 6), (20, -5, 1.6, 7), (-30, 0, 0.8, 5)], 0.5),
    ("leaf_print", (8.0, 40.0), (-15.0, 4.0), (10, 7), 1.1,
     [(18, -4, 2.4, 6), (30, -8, 1.8, 5), (36, 0, 1.5, 5)], 0.7),
    ("blue_tiedye", (-34.0, 5.0), (-2.0, 18.0), (12, 7), 0.9,
     [(-24, 6, 2.5, 6), (-10, 9, 3.0, 7), (0, 5, 2.0, 5)], 0.6),
    ("white_bunny", (3.0, 42.0), (-9.0, 18.0), (13, 9), 1.4,
     [(30, 2, 6.5, 8), (18, 8, 3.5, 7), (38, -4, 3.0, 5), (8, 10, 1.5, 5)], 0.6),
]


def surface(x, y):
    """Top of the bare couch at (x, y), inches."""
    if y > FRAME_Y:
        return FRAME_H
    if abs(x) > L / 2 - ARM_W:
        return ARM_H if y < 13.0 else FRAME_H
    if y >= BACK_TOP_Y:
        return BACK_H
    if y >= BACK_FOOT_Y:
        return SEAT_H + (y - BACK_FOOT_Y) * (BACK_H - SEAT_H) / (BACK_TOP_Y - BACK_FOOT_Y)
    return SEAT_H


def draped(x, y, r=3.0):
    """Cone-dilated surface: a blanket bridges steps instead of hugging them."""
    best = -1e9
    for i in range(-2, 3):
        for j in range(-2, 3):
            dx, dy = r * i / 2, r * j / 2
            best = max(best, surface(x + dx, max(y + dy, FRONT)) - 0.9 * math.hypot(dx, dy))
    return best


def sheet(b, uv, region, xr, yr, grid, lift, bumps, wr):
    bm = b.bm
    nx, ny = grid
    u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, region)

    def pos(x, yp):
        h = lift
        for bx, by, bh, br in bumps:
            h += bh * math.exp(-((x - bx) ** 2 + (yp - by) ** 2) / (2 * br * br))
        h += wr * math.sin(x * 0.45 + yp * 0.2) * math.sin(yp * 0.35 - x * 0.1)
        if yp >= FRONT:
            return (x, yp, draped(x, yp) + h)
        # hangs down the seat front: the overhang becomes drop
        top = draped(x, FRONT) + h
        drop = FRONT - yp
        return (x, FRONT - 0.4 - 0.35 * h - 0.15 * drop * abs(math.sin(x * 0.3)), top - drop)

    top, bot = [], []
    for j in range(ny + 1):
        yp = yr[0] + (yr[1] - yr[0]) * j / ny
        rt, rb = [], []
        for i in range(nx + 1):
            x = xr[0] + (xr[1] - xr[0]) * i / nx
            px, py, pz = pos(x, yp)
            if (i in (0, nx) or j in (0, ny)) and yp >= FRONT:
                pz -= 0.9            # edges tuck down onto the couch
            if i in (0, nx) and yp >= FRONT:
                px += 0.8 * math.sin(yp * 0.9) * (1 if i else -1)   # wavy hem
            rt.append((bm.verts.new((m(px), m(py), m(pz))), i / nx, j / ny))
            if yp >= FRONT:
                q = (px, py, pz - T)
            else:
                q = (px, py + T, pz)
            rb.append((bm.verts.new(tuple(map(m, q))), i / nx, j / ny))
        top.append(rt)
        bot.append(rb)

    faces = []

    def face(corners):
        f = bm.faces.new([c[0] for c in corners])
        for loop, c in zip(f.loops, corners):
            loop[uv].uv = (u0 + c[1] * (u1 - u0), v0 + c[2] * (v1 - v0))
        faces.append(f)

    for j in range(ny):
        for i in range(nx):
            face([top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i]])
            face([bot[j][i], bot[j + 1][i], bot[j + 1][i + 1], bot[j][i + 1]])
    # edges all round
    ring = ([(j, 0) for j in range(ny)] + [(ny, i) for i in range(nx)]
            + [(j, nx) for j in range(ny, 0, -1)] + [(0, i) for i in range(nx, 0, -1)])
    for k in range(len(ring)):
        a, c = ring[k], ring[(k + 1) % len(ring)]
        face([top[a[0]][a[1]], top[c[0]][c[1]], bot[c[0]][c[1]], bot[a[0]][a[1]]])
    b._tag(faces, region)


def build(coll):
    b = common.Builder(REGIONS)
    uv = b.bm.loops.layers.uv.new("UVMap")
    for spec in BLANKETS:
        sheet(b, uv, *spec)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
