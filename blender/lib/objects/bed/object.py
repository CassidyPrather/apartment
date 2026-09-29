"""Twin bed: an espresso metal-and-wood frame on black casters, a box spring in a dark
grey skirt, a mattress in a white sheet, a light aqua fleece blanket (a cloth simulation,
see sim_blanket) that drapes over the sides and the foot almost to the floor with soft
folds on top, and a grey pillow
propped against the headboard with a crumple of sheet beside it.

Source of truth: scripted from the bedroom LiDAR survey (registered.npz, plan inches)
and the survey photo crops. Local frame: head end +Y (against the headboard bookcase),
foot -Y, origin on the floor at the centre of the blanket's outer footprint.
Place at plan (224.5, 107.5), rotation -90 (foot faces west, local +X = south).
Measured: blanket hem x 187.5 (foot) to the headboard face at 261.5; drape sides at
y 88 and 127 (LiDAR and splat agree within 0.5 in).
"""

import math
import os
import random

import atlas_layout
import bmesh
import bpy
import common

IN = 0.0254


def m(v):
    return v * IN


L_OUT = 74.0        # SCAN blanket hem at the foot (x 187.5) to the headboard face (261.5)
W_OUT = 39.5        # SCAN drape outer faces at plan y 88 and 127 (+0.5 for the hem flare)
MAT_W = 36.5        # EST mattress under the drape (outer width minus drape bend and flare)
MAT_L = 72.5        # EST (twin nominal 75; the scan leaves 72.5 inside the foot drape)
TOP = 27.0          # SCAN mattress+sheet top: blanket top reads 27.5-28 flat in the section
BOX_Z = (7.0, 16.0)         # EST box spring (hidden by the drape, the skirt shows below)
MAT_Z = (16.0, TOP - 1.0)   # EST mattress (1 in under the blanket so folds never dip into it)
FRAME_Z = (4.5, 7.0)        # EST angle-iron rails
CASTER_R = 1.2              # EST caster wheel
HEM_SIDE = 6.0      # EST drape hem above the floor on the sides (photos: ~shoe height)
HEM_FOOT = 3.5      # EST at the foot (photo bed_3: almost to the floor)
BLANKET_HEAD = 36.5  # EST blanket runs up to the headboard (photos); pillow lies on it
ROLL_Y = 20.5       # EST bunched roll of blanket in front of the pillow
PILLOW = (29.0, 16.0, 7.0)  # EST pillow W x D x thickness; top SCAN ~33.5 (LiDAR 31.5-34)
R_BEND = 1.0        # EST blanket bend radius over the mattress edge

NAME = "bed"
ATLAS = {
    "name": "bed",
    "size": 1024,
    "regions": {
        "blanket": (0, 0, 768, 768),
        "pillow": (768, 0, 256, 256),
        "sheet": (768, 256, 256, 256),
        "skirt": (768, 512, 256, 256),
        "frame": (0, 768, 256, 256),
        "caster": (256, 768, 256, 256),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
# photo-matching views: bed_3 from the foot (west, high), bed_2 from the NW-ish foot corner
VIEWS = [("photo_foot", 0, 30, 0.75), ("photo_foot_corner", 330, 32, 0.75),
         ("low_side", 90, 4, 0.8)]

HW = MAT_W / 2
Y_FOOT = -L_OUT / 2 + (W_OUT - MAT_W) / 2       # mattress foot, inside the foot drape
Y_HEAD = L_OUT / 2
RNG = random.Random(11)

# soft folds on the blanket top: (x0, y0, x1, y1, height, half-width) ridges, EST from
# the photos (long diagonal wrinkles, a bunched roll near the pillow)
FOLDS = [(-10, 30, 12, 26, 1.0, 2.0), (-16, -34, -4, -20, 0.8, 1.6), (4, -34, 12, -26, 0.9, 1.5),
         (-4, -14, 8, -20, 0.9, 1.4), (-16, 12, -6, 2, 0.9, 1.5), (10, 2, 16, 20, 0.8, 1.5),
         (-16, 16, 14, 20, 1.2, 2.2), (-12, 6, 10, 12, 0.8, 1.8), (-17, -4, 6, 4, 0.9, 2.0),
         (2, -8, 17, -2, 0.8, 1.8), (-14, -18, 4, -12, 0.7, 2.0), (6, -24, 17, -16, 0.6, 1.8),
         (-17, -30, -2, -26, 0.6, 1.6), (-6, 20, 12, 22, 1.4, 2.5), (-18, 22, -6, 17, 1.0, 2.0),
         (8, 8, 18, 16, 0.7, 1.8)]


# plus many small wrinkles, seeded (photos: the fleece is rumpled all over)
_R = random.Random(5)
for _ in range(26):
    _x, _y = _R.uniform(-17, 17), _R.uniform(-34, 30)
    _a = _R.uniform(-0.9, 0.9) + (0.5 if _R.random() < 0.5 else -0.5)
    _l = _R.uniform(5, 11)
    FOLDS.append((_x - _l * math.cos(_a) / 2, _y - _l * math.sin(_a) / 2,
                  _x + _l * math.cos(_a) / 2, _y + _l * math.sin(_a) / 2,
                  _R.uniform(0.5, 1.0), _R.uniform(1.1, 1.5)))


def fold_height(x, y):
    h = 0.35
    for x0, y0, x1, y1, a, w in FOLDS:
        dx, dy = x1 - x0, y1 - y0
        ll = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / ll))
        px, py = x0 + t * dx, y0 + t * dy
        d2 = (x - px) ** 2 + (y - py) ** 2
        taper = math.sin(math.pi * (0.1 + 0.8 * t))
        h += a * taper * math.exp(-d2 / (2 * w * w))
    h += 0.45 * math.sin(x * 0.55 + y * 0.21) * math.sin(y * 0.33 - x * 0.12)
    h += 0.3 * math.sin(x * 1.1 - y * 0.7) * math.sin(y * 0.45 + x * 0.3)
    # the blanket bunches up toward its top edge by the pillow
    h += 1.6 * math.exp(-((y - ROLL_Y) ** 2) / 10.0) * (0.6 + 0.4 * math.sin(x * 0.5))
    return h


def blanket_point(s, t):
    """Unfolded blanket coords (s across, t along) -> (x, y, z) in inches."""
    cx = max(-HW, min(HW, s))
    cy = max(t, Y_FOOT)
    dx, dy = s - cx, t - cy
    d = math.hypot(dx, dy)
    # folds fade out over the edge so the drape hangs clean
    fx = max(-HW + 2.5, min(HW - 2.5, cx))
    fy = max(Y_FOOT + 2.5, cy)
    edge = min(HW - abs(cx), cy - Y_FOOT, 6.0) / 6.0
    h = max(fold_height(fx, fy), 0.1) * (0.35 + 0.65 * edge)
    ztop = TOP + h
    if d < 1e-6:
        return (s, t, ztop)
    ux, uy = dx / d, dy / d
    arc = math.pi * R_BEND / 2
    if d <= arc:
        th = d / R_BEND
        out, up = R_BEND * math.sin(th), R_BEND * math.cos(th) - R_BEND
        return (cx + ux * out, cy + uy * out, ztop + up)
    e = d - arc
    perim = cx + cy                     # runs along each edge: folds in the hanging part
    k = min(e / 12.0, 1.0)
    wave = 0.55 * k * math.sin(perim * 0.42 + 1.3) + 0.3 * k * math.sin(perim * 0.9)
    flare = R_BEND + 0.015 * e + max(wave, -0.4)
    z = max(ztop - R_BEND - e, HEM_FOOT - 1.5)    # corner cones fold onto the hem line
    return (cx + ux * flare, cy + uy * flare, z)


def blanket(b, uvl):
    bm = b.bm
    drop_s = (TOP - HEM_SIDE) - R_BEND + math.pi * R_BEND / 2
    drop_f = (TOP - HEM_FOOT) - R_BEND + math.pi * R_BEND / 2
    s0, s1 = -HW - drop_s, HW + drop_s
    t0, t1 = Y_FOOT - drop_f, BLANKET_HEAD
    # denser over the top, coarser down the drape
    def ticks(a, b_, inner0, inner1, n_in, n_out):
        out = [a + (inner0 - a) * i / n_out for i in range(n_out)]
        out += [inner0 + (inner1 - inner0) * i / n_in for i in range(n_in)]
        return out
    arc = math.pi * R_BEND / 2
    def outer(a, n):             # distances past the edge: through the bend, then the drop
        return [arc * 0.5, arc] + [arc + (a - arc) * i / n for i in range(1, n + 1)]
    so = outer(drop_s, 5)
    ss = [-HW - d for d in reversed(so)] + [-HW + MAT_W * i / 28 for i in range(29)] + [HW + d for d in so]
    to = outer(drop_f, 5)
    tt = [Y_FOOT - d for d in reversed(to)] + [Y_FOOT + (t1 - Y_FOOT) * i / 40 for i in range(41)]
    u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, "blanket")
    span = max(s1 - s0, t1 - t0)
    grid = []
    for t in tt:
        row = []
        for s in ss:
            x, y, z = blanket_point(s, t)
            if t == t1 and abs(s) < HW:          # top edge: a rolled lip
                z += 0.3
            row.append((bm.verts.new((m(x), m(y), m(z))), (s - s0) / span, (t - t0) / span))
        grid.append(row)
    faces = []
    for j in range(len(tt) - 1):
        for i in range(len(ss) - 1):
            cs = [grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]]
            f = bm.faces.new([c[0] for c in cs])
            for loop, c in zip(f.loops, cs):
                loop[uvl].uv = (u0 + c[1] * (u1 - u0), v0 + c[2] * (v1 - v0))
            faces.append(f)
    # a thin hem band along the top edge so it reads as cloth, not paper
    top_row = grid[-1]
    lip = []
    for (v, us, vs) in top_row:
        co = v.co.copy()
        co.z -= m(0.45)
        co.y -= m(0.2)
        lip.append((bm.verts.new(co), us, vs + 0.004))
    for i in range(len(top_row) - 1):
        cs = [top_row[i], lip[i], lip[i + 1], top_row[i + 1]]
        f = bm.faces.new([c[0] for c in cs])
        for loop, c in zip(f.loops, cs):
            loop[uvl].uv = (u0 + c[1] * (u1 - u0), v0 + min(c[2], 1.0) * (v1 - v0))
        faces.append(f)
    b._tag(faces, "blanket")
    return faces


def pillow(b, uvl, cx, cy, cz, w, d, th, tilt, yaw=0.0, lump=0.0, region="pillow"):
    """A pillow: two pinched grid surfaces meeting at a seam, tilted up by `tilt` deg."""
    from mathutils import Matrix, Vector
    bm = b.bm
    nu, nv = 10, 7
    u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, region)
    rot = (Matrix.Rotation(math.radians(yaw), 3, "Z") @ Matrix.Rotation(math.radians(tilt), 3, "X"))

    def P(i, j, side):
        a = -1 + 2 * i / nu
        c = -1 + 2 * j / nv
        puff = (1 - abs(a) ** 2.6) ** 0.55 * (1 - abs(c) ** 2.6) ** 0.55
        z = side * th / 2 * puff * (1 + lump * math.sin(a * 3.1 + 0.7) * 0.25)
        x = a * w / 2 * (1 - 0.06 * (1 - c * c))    # corners pinch in a little
        y = c * d / 2 * (1 - 0.1 * (1 - a * a) * 0.5)
        return rot @ Vector((x, y, z)) + Vector((cx, cy, cz))

    faces = []
    for side in (1, -1):
        g = [[bm.verts.new(tuple(map(m, P(i, j, side)))) for i in range(nu + 1)] for j in range(nv + 1)]
        for j in range(nv):
            for i in range(nu):
                cs = [(g[j][i], i, j), (g[j][i + 1], i + 1, j), (g[j + 1][i + 1], i + 1, j + 1),
                      (g[j + 1][i], i, j + 1)]
                if side < 0:
                    cs.reverse()
                f = bm.faces.new([c[0] for c in cs])
                for loop, c in zip(f.loops, cs):
                    loop[uvl].uv = (u0 + c[1] / nu * (u1 - u0), v0 + c[2] / nv * (v1 - v0))
                faces.append(f)
        if side > 0:
            top = g
        else:
            bot = g
    b._tag(faces, region)
    return faces, top, bot


# The blanket is a cloth simulation made in the live Blender (Blender MCP): a fleece grid
# dropped onto the mattress/box spring with its head edge pinned by the headboard, rumpled
# afterwards with fleece wrinkles on top, sides smoothed. Saved in blender/assets/
# bed_blanket.blend as `bed_blanket_final`, already in this package's frame. The scripted
# blanket() below is kept as the fallback when the blend is missing.
BLANKET_BLEND = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "bed_blanket.blend")
BLANKET_TRIS = 10000
BLANKET_T = 0.3     # EST fleece thickness


def sim_blanket(b, uvl):
    """Add the simulated blanket to the builder: thickened, trimmed to budget, its own UVs
    mapped into the blanket region (written to the sheet_uv layer like the scripted one)."""
    with bpy.data.libraries.load(os.path.abspath(BLANKET_BLEND), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n == "bed_blanket_final"]
    ob = dst.objects[0]
    bpy.context.scene.collection.objects.link(ob)
    ob.modifiers.clear()
    sol = ob.modifiers.new("thick", "SOLIDIFY")
    sol.thickness = m(BLANKET_T)
    sol.offset = -1.0
    tris = 4 * len(ob.data.polygons)                  # quads, doubled by the solidify
    dec = ob.modifiers.new("trim", "DECIMATE")
    dec.ratio = min(1.0, BLANKET_TRIS / max(tris, 1))
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    tmp = bmesh.new()
    tmp.from_mesh(me)
    src_uv = tmp.loops.layers.uv.get("UVMap")
    u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, "blanket")
    bi = b.idx("blanket")
    vmap = {v: b.bm.verts.new(v.co.copy()) for v in tmp.verts}
    for f in tmp.faces:
        try:
            nf = b.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:
            continue
        nf.material_index = bi
        nf.smooth = True
        for l_src, l_dst in zip(f.loops, nf.loops):
            u, v = l_src[src_uv].uv if src_uv else (0.5, 0.5)
            l_dst[uvl].uv = (u0 + min(max(u, 0.0), 1.0) * (u1 - u0), v0 + min(max(v, 0.0), 1.0) * (v1 - v0))
    tmp.free()
    bpy.data.meshes.remove(me)
    old = ob.data
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(old)


def build(coll):
    b = common.Builder(REGIONS)
    uvl = b.bm.loops.layers.uv.new("sheet_uv")
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))

    # frame: angle-iron rails, cross rails, legs on casters
    fx0, fx1 = -HW + 1.0, HW - 1.0
    fy0, fy1 = Y_FOOT + 1.0, Y_HEAD - 1.5
    z0, z1 = FRAME_Z
    bx("frame", (fx0, fy0, z0), (fx0 + 1.5, fy1, z1))
    bx("frame", (fx1 - 1.5, fy0, z0), (fx1, fy1, z1))
    for y in (fy0, (fy0 + fy1) / 2 - 0.75, fy1 - 1.5):
        bx("frame", (fx0, y, z1 - 1.2), (fx1, y + 1.5, z1))
    for x in (fx0 + 0.75, fx1 - 0.75):
        for y in (fy0 + 0.75, (fy0 + fy1) / 2, fy1 - 0.75):
            b.cylinder("frame", (m(x), m(y), m((2 * CASTER_R + z0) / 2)), m(0.45),
                       m(z0 - 2 * CASTER_R + 0.2), segments=6)
            b.cylinder("caster", (m(x), m(y), m(CASTER_R)), m(CASTER_R), m(0.9), axis="X",
                       segments=10)
    # box spring in its skirt (the skirt hangs to ~1.5 in above the floor)
    bx("skirt", (-HW + 0.2, Y_FOOT + 0.2, BOX_Z[0]), (HW - 0.2, Y_HEAD - 0.2, BOX_Z[1]), 0.4)
    bx("skirt", (-HW + 0.4, Y_FOOT + 0.4, 1.6), (HW - 0.4, Y_HEAD - 0.4, BOX_Z[0] + 0.1))
    # mattress in a white fitted sheet
    bx("sheet", (-HW, Y_FOOT, MAT_Z[0]), (HW, Y_HEAD - 0.3, MAT_Z[1]), 1.5)
    use_sim = os.path.exists(BLANKET_BLEND)
    if use_sim:
        sim_blanket(b, uvl)
    else:
        blanket(b, uvl)
    # pillow propped against the headboard, a smaller squashed one beside it, and a
    # crumple of sheet at the north end (local -X)
    pw, pd, pt = PILLOW
    pillow(b, uvl, 1.5, Y_HEAD - pd / 2 - 0.6, 30.2, pw, pd, pt, tilt=12, yaw=-2, lump=1.0)
    ob_pl = pillow(b, uvl, 0.0, 0.0, 0.0, 12.0, 6.5, 3.0, tilt=0, yaw=0, lump=0.5, region="sheet")
    # place the sheet crumple: move its verts
    faces, top, bot = ob_pl
    from mathutils import Vector
    moved = {v for f in faces for v in f.verts}
    for v in moved:
        x, y, z = v.co
        v.co = Vector((y * 0.9 + m(-HW + 2.5), -x * 0.9 + m(Y_HEAD - 9.5), z + m(TOP + 2.2)))
    ob = b.to_object(NAME, coll)

    if use_sim:                 # the simulated blanket is a closed solid shell: normals are right
        return [ob]
    # an open sheet's normals can come out of recalc pointing inward: face them outward
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.normal_update()
    bi = REGIONS.index("blanket")
    flip = []
    for f in bm.faces:
        if f.material_index != bi:
            continue
        c = f.calc_center_median()
        core = (max(m(-HW + 2), min(m(HW - 2), c.x)), max(m(Y_FOOT + 2), min(m(Y_HEAD), c.y)),
                min(c.z, m(TOP - 2)))
        out = c - __import__("mathutils").Vector(core)
        if f.normal.dot(out) < 0:
            flip.append(f)
    bmesh.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(ob.data)
    bm.free()
    return [ob]


def texture(objs):
    ob = objs[0]
    common.atlas_uvs(ob, ATLAS)
    me = ob.data
    src = me.uv_layers["sheet_uv"]
    dst = me.uv_layers["UVMap"]
    keep = {REGIONS.index(r) for r in ("blanket", "pillow")}
    sheet_i = REGIONS.index("sheet")
    for p in me.polygons:
        if p.material_index in keep or (p.material_index == sheet_i and
                                       any(src.data[li].uv.length > 0 for li in p.loop_indices)):
            for li in p.loop_indices:
                dst.data[li].uv = src.data[li].uv
    me.uv_layers.remove(me.uv_layers["sheet_uv"])
    me.uv_layers.active = me.uv_layers["UVMap"]
    mat = common.atlas_material(NAME, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
