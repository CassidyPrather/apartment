"""Shared helpers for the two hall-side closet contents packages (kitchen_closet_contents,
dining_closet_contents): boxes in plan inches with per-face retagging, lumpy fabric
masses, the painted closet shelf on its cleats. Everything takes PLAN inches and builds
straight into a common.Builder (metres)."""

import math

import bmesh
from mathutils import Matrix, Vector, noise

IN = 0.0254


def m(v):
    return v * IN


def V(x, y, z):
    return Vector((m(x), m(y), m(z)))


def _new_faces(b, before):
    return [f for f in b.bm.faces if f not in before]


def _verts(faces):
    return list({v for f in faces for v in f.verts})


def retag(b, faces, table):
    """Retag faces by their outward axis: table maps '+X','-X','+Y','-Y','+Z','-Z' -> region."""
    for f in faces:
        f.normal_update()
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        key = ("+" if n[ax] > 0 else "-") + "XYZ"[ax]
        if key in table:
            f.material_index = b.idx(table[key])


def rotate_about(b, faces, centre, rz=0.0, ry=0.0, rx=0.0):
    """Rotate the faces' verts about a plan-inch centre (degrees)."""
    c = V(*centre)
    mat = (Matrix.Translation(c) @ Matrix.Rotation(math.radians(rz), 4, "Z")
           @ Matrix.Rotation(math.radians(ry), 4, "Y") @ Matrix.Rotation(math.radians(rx), 4, "X")
           @ Matrix.Translation(-c))
    bmesh.ops.transform(b.bm, matrix=mat, verts=_verts(faces))


def box(b, region, lo, hi, bevel=0.0, faces=None, rz=0.0, ry=0.0, rx=0.0, pivot=None):
    """Box from plan-inch corner lo to hi; `faces` retags by outward axis (before any
    rotation); rz/ry/rx rotate about `pivot` (default the box centre)."""
    before = set(b.bm.faces)
    b.box(region, V(*lo), V(*hi), bevel=m(bevel))
    new = _new_faces(b, before)
    if faces:
        retag(b, new, faces)
    if rz or ry or rx:
        c = pivot or tuple((a + c) / 2 for a, c in zip(lo, hi))
        rotate_about(b, new, c, rz, ry, rx)
    return new


def cyl(b, region, centre, r, h, axis="Z", seg=10, cap=None, rz=0.0, ry=0.0, rx=0.0, pivot=None):
    """Cylinder; centre is the BASE centre for axis Z (z0), the middle otherwise."""
    x, y, z = centre
    before = set(b.bm.faces)
    if axis == "Z":
        b.cylinder(region, V(x, y, z + h / 2), m(r), m(h), axis="Z", segments=seg, cap_region=cap)
    else:
        b.cylinder(region, V(x, y, z), m(r), m(h), axis=axis, segments=seg, cap_region=cap)
    new = _new_faces(b, before)
    if rz or ry or rx:
        rotate_about(b, new, pivot or (x, y, z), rz, ry, rx)
    return new


def lump(b, region, lo, hi, seed=0, round_=0.55, amp=0.10, freq=2.2, cuts=3, rz=0.0, ry=0.0,
         rx=0.0, sag=0.0, faces=None):
    """A soft mass (bag, fabric pile) filling roughly the box lo..hi: a subdivided cube
    pulled toward a sphere by round_, displaced by smooth noise (amp, relative to the
    half-size), its top sagging by `sag` (fraction) toward the middle."""
    bm = b.bm
    before = set(bm.faces)
    r = bmesh.ops.create_cube(bm, size=1.0)
    edges = list({e for v in r["verts"] for e in v.link_edges})
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts, use_grid_fill=True)
    new = _new_faces(b, before)
    lo, hi = Vector(lo), Vector(hi)
    half = (hi - lo) / 2
    c = (hi + lo) / 2
    off = Vector((seed * 1.7, seed * 3.1, seed * 0.9))
    for v in _verts(new):
        p = v.co * 2.0                                    # cube [-1, 1]^3
        x, y, z = p
        s = Vector((x * math.sqrt(max(0.0, 1 - y * y / 2 - z * z / 2 + y * y * z * z / 3)),
                    y * math.sqrt(max(0.0, 1 - z * z / 2 - x * x / 2 + z * z * x * x / 3)),
                    z * math.sqrt(max(0.0, 1 - x * x / 2 - y * y / 2 + x * x * y * y / 3))))
        q = p.lerp(s, round_)
        n = q.normalized() if q.length > 1e-6 else Vector((0, 0, 1))
        q = q + n * amp * noise.noise(q * freq + off)
        if sag and q.z > 0:
            q.z -= sag * q.z * (1 - min(1.0, (q.x * q.x + q.y * q.y) * 0.5))
        v.co = Vector((m(c.x + q.x * half.x), m(c.y + q.y * half.y), m(c.z + q.z * half.z)))
    for f in new:
        f.material_index = b.idx(region)
    if faces:
        retag(b, new, faces)
    if rz or ry or rx:
        rotate_about(b, new, tuple(c), rz, ry, rx)
    return new


def sweep(b, region, pts, profile, ups=None, up=(0, 0, 1), closed=False):
    """common.Builder.sweep with plan-inch points and an inch profile."""
    return b.sweep(region, [V(*p) for p in pts], [(m(s), m(u)) for s, u in profile],
                   up=up, closed=closed, ups=ups)


def closet_shelf(b, x_front, x_back, y0, y1, z_top, board="shelf_paint", cleat="shelf_paint",
                 t=0.75, cleat_h=3.5, cleat_t=0.75, rod=None):
    """A painted closet shelf board on 1x4 cleats along the back and both side walls.
    rod = (x, z, dia, region) adds a closet rod spanning y0..y1."""
    box(b, board, (x_front, y0 + 0.05, z_top - t), (x_back - 0.05, y1 - 0.05, z_top), bevel=0.06)
    zc0, zc1 = z_top - t - cleat_h, z_top - t
    box(b, cleat, (x_back - cleat_t, y0 + cleat_t, zc0), (x_back - 0.02, y1 - cleat_t, zc1), bevel=0.05)
    for ya, yb in ((y0 + 0.02, y0 + cleat_t), (y1 - cleat_t, y1 - 0.02)):
        box(b, cleat, (x_front + 1.0, ya, zc0), (x_back - 0.02, yb, zc1), bevel=0.05)
    if rod:
        x, z, dia, region = rod
        cyl(b, region, (x, (y0 + y1) / 2, z), dia / 2, (y1 - y0) - 0.1, axis="Y", seg=10)


def planar_x(y_lo, y_hi, z0, z1):
    """atlas_uvs planar entry for a face seen from the west (-X), plan inches: u runs
    north (left of the painted rect) -> south, v bottom -> top."""
    return ("-X", (m(-y_hi), m(-y_lo)), (m(z0), m(z1)))
