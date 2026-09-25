"""Hanging bags: two white adhesive wall hooks on the closet's south wall over the head
of the bed, with everything hung on them.
  hook 1 (west): a black structured tote on its long black webbing shoulder strap (slider
    and buckle), a woven brown belt and a plain brown belt
  hook 2 (east): a glossy cognac-brown leather shoulder bag on two dark brown straps, a
    tan hobo bag with an all-over print on a dark brown strap, and a patchwork lanyard
All generic; the tan bag's print is a from-scratch moon-and-dot parody pattern
("Moonpouch"), not the real monogram.

Source of truth: scripted, positions from the bedroom LiDAR survey (Reference/bedroom_survey,
registered.npz lidar + splat) and the capture frames (wide_20260925_012131_927 is the
straight-on view), measured with Reference/hanging_bags_work/*.py.
Frame: PLAN coordinates. Origin = plan (0, 0, 0), +X east, +Y north, Z up, metres; the
package goes on a marker at (0, 0, 0) with no rotation. The wall face is at y 130.35 and
everything hangs toward -Y (into the bedroom).

Dimensions (inches, plan):
  closet south wall bedroom face y 130.35, its west end (closet front wall) x 247.7   S
  hook centres x 249.3 and 260.8, load point z 61.5 (straps top out at z 61-62)      SCAN +-1
  hook plate 1.3 w x 1.7 h x 0.25, arm 0.9 out                                     EST
  black tote: centre (245.8, 127.3, 32.0), 14.5 w x 10 h x 5 d, west end up 18 deg    SCAN +-1
  black strap 1.5 wide; slider at z ~49                                            EST/photo
  woven belt 1.25 wide, x 250.5..252, z 61 -> 27                                   SCAN/photo
  cognac bag: centre (264.6, 127.6, 44.5), 9.5 w x 7 h x 4.5 d                     SCAN +-1.5
  tan hobo: centre (260.2, 125.9, 34.5), 8.5 w x 13 h x 5 d, bottom z ~27.5         SCAN +-1
  lanyard 0.8 wide, loop to z ~50                                                  photo/EST
Hidden backs (against the wall) are guessed.
"""

import math

import bmesh
from mathutils import Matrix, Vector

import common

NAME = "hanging_bags"


def m(inches):
    return inches * 0.0254


WALL_Y = 130.35
HOOKS = [(249.3, 61.5), (260.8, 61.5)]

ATLAS = {
    "name": NAME,
    "size": 512,
    "regions": {
        "black_body": (0, 0, 128, 128),
        "black_trim": (128, 0, 128, 128),
        "webbing": (256, 0, 128, 128),
        "silver": (384, 0, 128, 128),
        "hook_white": (0, 128, 128, 128),
        "cognac": (128, 128, 128, 128),
        "dark_strap": (256, 128, 128, 128),
        "belt_brown": (384, 128, 128, 128),
        "tan_print": (0, 256, 256, 256),
        "braid": (256, 256, 64, 256),
        "lanyard": (320, 256, 64, 256),
        "tan_trim": (384, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("photo_match", 8, 18, 0.55), ("from_bed", 340, 30, 0.6)]


# --- helpers -------------------------------------------------------------------------

def P(x, y, z):
    """Plan inches -> metres vector."""
    return Vector((m(x), m(y), m(z)))


def frame(center, rot_deg=(0, 0, 0)):
    rx, ry, rz = (math.radians(a) for a in rot_deg)
    return (Matrix.Translation(P(*center)) @ Matrix.Rotation(rz, 4, "Z")
            @ Matrix.Rotation(ry, 4, "Y") @ Matrix.Rotation(rx, 4, "X"))


def blob(b, region, center, size, rot=(0, 0, 0), box=0.45, taper=0.0, belly=0.25,
         sag=0.0, flat_back=True, useg=14, vseg=9, trim=None):
    """A soft bag body: a UV sphere pushed toward a rounded box (box < 1), narrower at
    the top by `taper`, fuller at the bottom by `belly`, the bottom corners dropped by
    `sag`, and the back flattened against the wall. size = (w, d, h) inches.
    trim: region for the top band (the zip/opening), or None."""
    r = bmesh.ops.create_uvsphere(b.bm, u_segments=useg, v_segments=vseg, radius=1.0)
    verts = r["verts"]
    w, d, h = size
    for v in verts:
        x, y, z = v.co
        sx = math.copysign(abs(x) ** box, x)
        sz = math.copysign(abs(z) ** box, z)
        sy = math.copysign(abs(y) ** 0.8, y)
        t = (1 - sz) / 2                       # 0 top .. 1 bottom
        sx *= 1 - taper * (1 - t)
        sy *= 1 - belly + belly * min(1.0, 1.6 * t)
        if flat_back and sy > 0:
            sy *= 0.35
        v.co = Vector((m(sx * w / 2), m(sy * d / 2), m(sz * h / 2 - sag * t * (1 - abs(sx)) ** 2 * h / 4)))
    M = frame(center, rot)
    bmesh.ops.transform(b.bm, matrix=M, verts=verts)
    faces = list({f for v in verts for f in v.link_faces})
    b._tag(faces, region)
    if trim:
        up = (M.to_3x3() @ Vector((0, 0, 1))).normalized()
        c = P(*center)
        for f in faces:
            if (f.calc_center_median() - c).dot(up) > m(h / 2) * 0.86:
                f.material_index = b.idx(trim)
    return faces


def strap(b, region, pts, width, thick=0.12, samples=4, up=(0, 1, 0)):
    path = common.smooth_path([P(*p) for p in pts], samples=samples)
    return b.sweep(region, path, common.rect_profile(m(width), m(thick)), up=up)


def cord(b, region, pts, radius, samples=4, n=6):
    path = common.smooth_path([P(*p) for p in pts], samples=samples)
    return b.sweep(region, path, common.circle_profile(m(radius), n))


def local_box(b, region, M, lo, hi, bevel=0.0):
    return b.box(region, [m(v) for v in lo], [m(v) for v in hi], bevel=m(bevel), matrix=M)


def hook(b, x, z):
    """White adhesive plate with a short upturned arm."""
    y = WALL_Y
    b.box("hook_white", P(x - 0.65, y - 0.25, z - 0.2), P(x + 0.65, y, z + 1.5), bevel=m(0.1))
    cord(b, "hook_white", [(x, y - 0.2, z + 0.5), (x, y - 0.8, z + 0.1), (x, y - 1.05, z + 0.5)],
         0.14, samples=3, n=6)


# --- parts -------------------------------------------------------------------------

def black_tote(b):
    c, rot = (245.8, 127.3, 32.0), (0, 18, 0)       # west end up
    blob(b, "black_body", c, (14.5, 5.0, 10.0), rot=rot, box=0.35, taper=0.06, belly=0.2,
         trim="black_trim")
    M = frame(c, rot)
    # leather trim tabs where the handles and strap meet the body
    for sx in (-4.3, 4.3):
        local_box(b, "black_trim", M, (sx - 0.6, -2.55, 1.2), (sx + 0.6, -2.2, 4.4), bevel=0.1)
        local_box(b, "silver", M, (sx - 0.45, -2.7, 3.9), (sx + 0.45, -2.45, 4.7))
    # two short handles, front and back
    for dy in (-1.2, 0.9):
        pts = [M @ P(sx, dy, hz) for sx, hz in ((-4.3, 4.6), (-3.8, 6.3), (0, 7.0), (3.8, 6.3), (4.3, 4.6))]
        pts = [(v.x / 0.0254, v.y / 0.0254, v.z / 0.0254) for v in pts]
        cord(b, "black_trim", pts, 0.3, samples=3, n=6)
    # zip pull
    local_box(b, "silver", M, (5.2, -1.0, 4.5), (5.6, -0.6, 5.7))
    # the long webbing shoulder strap: west strand straight down, east strand angled
    hx, hz = HOOKS[0]
    west = M @ P(-6.8, 0, 4.4)
    east = M @ P(6.8, 0, 4.0)
    wx, wy, wz = (west / 0.0254)
    ex, ey, ez = (east / 0.0254)
    strap(b, "webbing", [(wx, wy + 0.3, wz), (hx - 1.4, 129.6, 47), (hx - 0.3, 129.75, 58),
                         (hx, 129.3, hz + 0.3)], 1.5)
    strap(b, "webbing", [(hx + 0.2, 129.3, hz + 0.3), (hx + 1.2, 129.7, 57), (253.0, 129.5, 49),
                         (ex - 1.0, 128.8, ez + 3), (ex, ey + 0.3, ez)], 1.5)
    # slider on the east strand
    b.box("silver", P(252.2, 129.1, 48.3), P(254.0, 129.8, 49.0))


def belts(b):
    hx, hz = HOOKS[0]
    # woven belt, buckle at the top over the hook
    strap(b, "braid", [(hx + 0.6, 129.2, hz), (251.0, 129.6, 50), (251.4, 129.7, 38), (251.9, 129.6, 27)],
          1.25, thick=0.22)
    b.box("silver", P(hx + 0.0, 128.95, hz - 2.6), P(hx + 1.3, 129.15, hz - 0.4))
    # plain brown belt behind it, loose end lower
    strap(b, "belt_brown", [(hx + 1.0, 129.6, hz + 0.2), (252.2, 129.95, 50), (252.9, 129.95, 36),
                            (253.3, 129.8, 26.5)], 1.3, thick=0.15)


def cognac_bag(b):
    c, rot = (264.6, 127.6, 44.5), (4, -6, 0)
    blob(b, "cognac", c, (9.5, 4.5, 7.0), rot=rot, box=0.45, taper=0.12, belly=0.2,
         trim="dark_strap")
    M = frame(c, rot)
    # front flap pocket seam and buckle straps with studs
    local_box(b, "dark_strap", M, (-3.8, -2.3, -0.6), (3.8, -2.05, -0.3))
    for sx in (-2.4, 2.4):
        local_box(b, "dark_strap", M, (sx - 0.4, -2.35, -0.5), (sx + 0.4, -2.1, 3.0))
        local_box(b, "silver", M, (sx - 0.5, -2.5, 0.4), (sx + 0.5, -2.25, 1.0))
    hx, hz = HOOKS[1]
    for sx in (-4.2, 4.2):
        a = M @ P(sx, 0, 3.0)
        ax, ay, az = a / 0.0254
        strap(b, "dark_strap", [(hx + 0.3 * (sx > 0), 129.3, hz + 0.2), (hx + (0.5 if sx < 0 else 2.2), 129.0, 55),
                                (ax, ay + 0.4, az)], 0.9, thick=0.14)
        local_box(b, "silver", M, (sx - 0.35, -0.3, 2.8), (sx + 0.35, 0.3, 3.5))


def tan_hobo(b):
    c, rot = (260.2, 125.9, 34.5), (-12, 4, 0)       # bottom swings out off the wall
    blob(b, "tan_print", c, (8.5, 5.0, 13.0), rot=rot, box=0.6, taper=0.45, belly=0.35,
         sag=0.25, trim="tan_trim")
    M = frame(c, rot)
    top = M @ P(0, 0, 6.3)
    tx, ty, tz = top / 0.0254
    hx, hz = HOOKS[1]
    strap(b, "dark_strap", [(tx - 1.2, ty + 0.2, tz - 0.5), (hx - 1.2, 128.6, 50), (hx - 0.3, 129.3, hz + 0.2),
                            (hx + 0.6, 129.2, 55), (tx + 1.0, ty + 0.2, tz - 0.5)], 1.0, thick=0.14)
    # snap tab
    local_box(b, "tan_trim", M, (-0.8, -2.65, 3.5), (0.8, -2.35, 6.1), bevel=0.1)
    local_box(b, "silver", M, (-0.3, -2.8, 4.1), (0.3, -2.6, 4.7))


def lanyard(b):
    hx, hz = HOOKS[1]
    strap(b, "lanyard", [(hx + 0.2, 129.1, hz + 0.3), (hx + 1.6, 129.0, 56), (263.2, 128.7, 50.5),
                         (262.4, 128.8, 49.8), (hx + 0.9, 129.0, 56), (hx + 0.6, 129.2, hz + 0.3)],
          0.8, thick=0.08, samples=3)
    b.box("silver", P(262.3, 128.2, 49.0), P(263.4, 128.8, 50.2))


def build(coll):
    b = common.Builder(REGIONS)
    for x, z in HOOKS:
        hook(b, x, z)
    belts(b)
    black_tote(b)
    tan_hobo(b)
    cognac_bag(b)
    lanyard(b)
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS, planar={
        # square mapping so the print stays round; covers the whole bag
        "tan_print": ("-Y", (m(260.2 - 7.5), m(260.2 + 7.5)), (m(34.5 - 7.5), m(34.5 + 7.5))),
        "braid": ("-Y", (m(249.2), m(253.2)), (m(26), m(62))),
        "lanyard": ("-Y", (m(260.5), m(264.5)), (m(49), m(63))),
    })
    common.collapse_materials(ob, {r: mat for r in REGIONS})
