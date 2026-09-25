"""Dresser-top clutter: a small desk globe on a stand, a three-drawer clear plastic
organiser at the back and a small blue box. The plush toys are their own package,
`plushies`, modelled as real meshes in Blender.

Built in the dresser's local frame (origin on the floor at the dresser's footprint
centre, front -Y), so it shares the dresser placement: plan (264.75, 18), rotation -90.
Local +X is south once placed. The dresser top is at z 58.5.

Dimensions (inches, all on top of the 34 x 19.5 dresser top):
  organiser 13 W x 11 D x 10 H, 3 drawers, centre x +4.5 y +3.5   EST from photos
  globe 9.2 dia on a 5 dia base, centre x +11.2 y -1.5, top ~71    EST from photos
  plush: green dragon ~13 tall at x -10.5 (front-left), octopus on it to ~75,
         the rest 6-9 tall                                          EST from photos
  overall z 58.5 .. ~76                                              SCAN (items z 59.6-~80)
"""

import math

from mathutils import Matrix, Vector

import bmesh

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "dresser_items"
TOP = 58.5
GX, GY, GR = 11.2, -1.5, 4.6

ATLAS = {
    "name": "dresser_items",
    "size": 512,
    "regions": {
        "green": (0, 0, 64, 64), "green_light": (64, 0, 64, 64),
        "dark": (128, 0, 64, 64), "white": (192, 0, 64, 64),
        "grey": (256, 0, 64, 64), "pink": (320, 0, 64, 64),
        "purple": (384, 0, 64, 64), "yellow": (448, 0, 64, 64),
        "cream": (0, 64, 64, 64), "red": (64, 64, 64, 64),
        "black": (128, 64, 64, 64), "blue": (192, 64, 64, 64),
        "brass": (256, 64, 64, 64), "orange": (320, 64, 64, 64),
        "plastic": (384, 64, 128, 64),
        "globe": (0, 128, 256, 128),
        "clear": (256, 128, 128, 128),
        "stuff": (384, 128, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {
    "dresser_items": {"atlas": "dresser_items", "mode": "opaque", "tiled": False},
    "dresser_items_clear": {"atlas": "dresser_items", "mode": "transparent", "alpha": 0.45},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front", 345, 18, 0.7), ("photo_left", 300, 25, 0.7)]


def ell(b, region, c, r, seg=10, rings=6, rot=None):
    """Ellipsoid centred at c (inches) with radii r (inches)."""
    res = bmesh.ops.create_uvsphere(b.bm, u_segments=seg, v_segments=rings, radius=1.0)
    verts = res["verts"]
    mat = Matrix.Diagonal((m(r[0]), m(r[1]), m(r[2]), 1.0))
    if rot:
        mat = Matrix.Rotation(math.radians(rot[1]), 4, rot[0]) @ mat
    bmesh.ops.transform(b.bm, matrix=Matrix.Translation(Vector(tuple(map(m, c)))) @ mat, verts=verts)
    b._tag(list({f for v in verts for f in v.link_faces}), region)


def bx(b, region, lo, hi, bev=0.0):
    b.box(region, tuple(map(m, lo)), tuple(map(m, hi)), bevel=m(bev))


def critter(b, x, y, z, s, body, head=None, ears=None, ear_r=None, snout=None, eyes="black",
            face=-90):
    """Generic sitting plush: body blob, head, ears, snout, eyes, stub arms and feet.
    s = scale (head radius ~ 2.2 s in), face = heading of the face in degrees."""
    head = head or body
    a = math.radians(face)
    fx, fy = math.cos(a), math.sin(a)          # facing direction
    sx, sy = -fy, fx                           # to its left
    br = 2.4 * s
    ell(b, body, (x, y, z + br * 0.9), (br, br, br * 0.95))
    for k in (-1, 1):
        ell(b, body, (x + fx * br * 0.6 + sx * k * br * 0.55, y + fy * br * 0.6 + sy * k * br * 0.55,
                      z + 0.6 * s), (1.0 * s, 1.0 * s, 0.7 * s), seg=8, rings=4)            # feet
        ell(b, body, (x + fx * br * 0.5 + sx * k * br * 0.85, y + fy * br * 0.5 + sy * k * br * 0.85,
                      z + br * 1.1), (0.7 * s, 0.7 * s, 1.1 * s), seg=8, rings=4)          # arms
    hr = 2.2 * s
    hz = z + br * 1.75 + hr * 0.7
    ell(b, head, (x, y, hz), (hr, hr * 0.95, hr * 0.9))
    if ears:
        er = ear_r or (0.8 * s, 0.35 * s, 0.9 * s)
        for k in (-1, 1):
            ell(b, ears, (x + sx * k * hr * 0.6, y + sy * k * hr * 0.6, hz + hr * 0.8), er, seg=8, rings=4,
                rot=("Z", face + 90))
    if snout:
        ell(b, snout, (x + fx * hr * 0.85, y + fy * hr * 0.85, hz - 0.3 * s), (0.8 * s, 0.8 * s, 0.6 * s),
            seg=8, rings=4)
    for k in (-1, 1):
        ell(b, eyes, (x + fx * hr * 0.88 + sx * k * hr * 0.35, y + fy * hr * 0.88 + sy * k * hr * 0.35,
                      hz + 0.35 * s), (0.28 * s, 0.28 * s, 0.28 * s), seg=6, rings=4)
    return hz + hr * 0.9


def organiser(b):
    """Three-drawer clear organiser: white frame, clear fronts, dark contents inside."""
    x0, x1, y0, y1 = -2.0, 11.0, -2.0, 9.0
    z0, h = TOP, 10.0
    bx(b, "plastic", (x0, y0 + 0.4, z0 + h - 0.5), (x1, y1, z0 + h), 0.1)     # white top
    bx(b, "clear", (x0, y1 - 0.3, z0), (x1, y1, z0 + h - 0.5))                  # clear back
    for xx in (x0, x1 - 0.35):
        bx(b, "clear", (xx, y0 + 0.4, z0), (xx + 0.35, y1, z0 + h - 0.5))      # clear sides
        bx(b, "plastic", (xx, y0 + 0.4, z0), (xx + 0.35, y0 + 0.9, z0 + h - 0.5))   # white front posts
    dh = (h - 0.5) / 3
    for i in range(3):
        zb = z0 + i * dh
        bx(b, "stuff", (x0 + 0.6, y0 + 1.5, zb + 0.2), (x1 - 0.6, y1 - 0.8, zb + dh * 0.7))
        bx(b, "clear", (x0 + 0.4, y0, zb + 0.1), (x1 - 0.4, y0 + 0.4, zb + dh - 0.15))
        bx(b, "plastic", (x0 + 0.4, y0 - 0.05, zb + dh - 0.35), (x1 - 0.4, y0 + 0.45, zb + dh - 0.1))  # lip
    return z0 + h


def globe(b):
    gx, gy = GX, GY
    common_c = lambda *a, **k: b.cylinder(*a, **k)
    common_c("black", (m(gx), m(gy), m(TOP + 0.3)), m(2.5), m(0.6), segments=16)
    common_c("brass", (m(gx), m(gy), m(TOP + 1.3)), m(0.3), m(1.6), segments=8)
    cz = TOP + 7.0
    ell(b, "globe", (gx, gy, cz), (GR, GR, GR), seg=16, rings=10, rot=("Y", 23))
    # meridian half-ring
    pts = []
    for i in range(13):
        t = math.radians(-90 + 180 * i / 12 + 23)
        pts.append((m(gx + (GR + 0.4) * math.sin(t)), m(gy), m(cz - (GR + 0.4) * math.cos(t))))
    b.sweep("brass", pts, common.rect_profile(m(0.25), m(0.4)), up=(0, 1, 0))
    b.cylinder("brass", (m(gx), m(gy), m(TOP + 1.9)), m(0.25), m(0.6), segments=6)


def build(coll):
    b = common.Builder(REGIONS)
    ztop = organiser(b)
    globe(b)
    # small blue box at the front edge
    bx(b, "blue", (8.8, -9.2, TOP), (12.0, -6.8, TOP + 1.6), 0.05)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material("dresser_items_clear", ATLAS)
    # preview only: show the clear plastic as see-through in the Blender renders
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = MATERIALS["dresser_items_clear"]["alpha"]
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    cz = TOP + 7.0
    planar = {"globe": ("-Y", (m(GX - GR), m(GX + GR)), (m(cz - GR), m(cz + GR)))}
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: (clear if r == "clear" else mat) for r in REGIONS})
