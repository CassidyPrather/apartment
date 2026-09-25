"""Office chair: black five-star base on twin-wheel casters, gas lift and tilt mechanism,
navy fabric seat and reclined backrest on a black spine, black T-arms with pads, and a
tan cloth draped over the backrest (hangs short in front, long down the back). Plus the
clear plastic chair mat it rolls on, as a second mesh with its own transparent material.

Source of truth: scripted from the bedroom survey (LiDAR slices: seat x 172..198,
y 34..64, z 15-21; back/cloth top ~42 at y 58-64) and the survey crops. Origin on the
floor at the chair's footprint centre; the chair faces -Y. In the room it faces the desk
(south): plan (185.5, 49.5), rotation 0. The mat is built in the same frame (world
x 164..210, y 28..75 plus a lip reaching under the desk to y 18).

Objects: office_chair (root, the chair) and office_chair_mat (the mat, a separate mesh so
it can stay put if the chair becomes a pickup).
"""

import math

from mathutils import Matrix, Vector

import common

IN = 0.0254


def m(v):
    return v * IN


BASE_R = 12.5       # SCAN floor points x 162..207 incl. mat edge; 25 in star is standard
CASTER_R = 1.0      # EST
LEG_W = 1.6         # EST
SEAT = (-10.0, 10.0, -13.5, 6.5)   # SCAN seat x 172..198 (with arms), front y ~36
SEAT_Z = (16.5, 19.5)              # SCAN seat top 18.5-20
BACK_W, BACK_H, BACK_T = 19.0, 18.0, 3.0   # EST photo; SCAN top ~40 at y ~62
BACK_Z0, BACK_Y0 = 22.0, 9.5       # EST bottom edge of the backrest
RECLINE = 12.0                     # EST degrees
ARM_X = 11.0                       # EST arm post centre; W with pads ~25.4
ARM_Z = 27.0                       # EST pad top (photo: ~7 in above the seat)
MAT_T = 0.12                       # EST
MAT_ALPHA = 0.3

NAME = "office_chair"
ATLAS = {
    "name": "office_chair",
    "size": 512,
    "regions": {
        "fabric": (0, 0, 256, 256),
        "cloth": (256, 0, 256, 256),
        "plastic": (0, 256, 128, 128),
        "metal": (128, 256, 128, 128),
        "pad": (0, 384, 128, 128),
        "mat": (256, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {
    "office_chair": {"atlas": "office_chair", "mode": "opaque", "tiled": False},
    "office_chair_mat": {"atlas": "office_chair", "mode": "transparent", "alpha": MAT_ALPHA},
}
COLLIDER = "box"
STATIC = False
VIEWS = [("photo_back_left", 215, 40, 0.8), ("photo_north", 180, 10, 0.8)]


def _back_frame():
    """Matrix for the backrest: local x across, y thickness, z up its height."""
    return (Matrix.Translation((0, m(BACK_Y0), m(BACK_Z0)))
            @ Matrix.Rotation(-math.radians(RECLINE), 4, "X"))


def _cloth(b, region):
    """Closed thin sheet draped over the backrest: path in (y, z) from the front hem, over
    the top, down the back; x across with folds that deepen away from the top."""
    path = [(6.2, 21.5), (6.9, 26.0), (7.9, 30.0), (8.9, 34.5), (9.9, 38.6), (11.4, 41.0), (13.6, 41.6),
            (15.7, 40.3), (15.9, 36.5), (16.3, 31.0), (16.6, 24.0), (16.9, 17.0), (17.2, 11.0)]
    pts = [Vector((0, y, z)) for y, z in path]
    # resample evenly
    L = [0.0]
    for a, c in zip(pts, pts[1:]):
        L.append(L[-1] + (c - a).length)
    n_s, n_x = 26, 15
    samp = []
    for i in range(n_s):
        s = L[-1] * i / (n_s - 1)
        k = max(j for j in range(len(L) - 1) if L[j] <= s + 1e-9) if s < L[-1] else len(L) - 2
        t = (s - L[k]) / (L[k + 1] - L[k])
        samp.append((pts[k].lerp(pts[k + 1], t), s))
    top_s = L[5]
    thick = 0.18
    outer, inner = [], []
    for i, (p, s) in enumerate(samp):
        a, c = samp[max(i - 1, 0)][0], samp[min(i + 1, n_s - 1)][0]
        tan = (c - a).normalized()
        nrm = Vector((0, -tan.z, tan.y))            # outward, away from the backrest
        drop = abs(s - top_s)
        half = 10.6 + 0.09 * drop                    # flares as it hangs
        amp = 0.15 + 0.035 * drop
        ro, ri = [], []
        for j in range(n_x):
            u = -1 + 2 * j / (n_x - 1)
            x = u * half
            fold = amp * math.sin(u * 7.3 + 0.8) + 0.5 * amp * math.sin(u * 13.1 + 2.0)
            curl = -1.2 * (abs(u) ** 3) * min(drop / 8.0, 1.0)   # edges wrap toward the chair
            q = p + nrm * (fold + curl) + Vector((x, 0, 0))
            ro.append(b.bm.verts.new(m_v(q + nrm * thick / 2)))
            ri.append(b.bm.verts.new(m_v(q - nrm * thick / 2)))
        outer.append(ro)
        inner.append(ri)
    faces = []
    nf = b.bm.faces.new
    for i in range(n_s - 1):
        for j in range(n_x - 1):
            faces.append(nf((outer[i][j], outer[i][j + 1], outer[i + 1][j + 1], outer[i + 1][j])))
            faces.append(nf((inner[i][j], inner[i + 1][j], inner[i + 1][j + 1], inner[i][j + 1])))
    for i in range(n_s - 1):              # side rims
        faces.append(nf((outer[i][0], outer[i + 1][0], inner[i + 1][0], inner[i][0])))
        faces.append(nf((outer[i][-1], inner[i][-1], inner[i + 1][-1], outer[i + 1][-1])))
    for j in range(n_x - 1):              # hems
        faces.append(nf((outer[0][j], inner[0][j], inner[0][j + 1], outer[0][j + 1])))
        faces.append(nf((outer[-1][j], outer[-1][j + 1], inner[-1][j + 1], inner[-1][j])))
    b._tag(faces, region)


def m_v(v):
    return Vector((m(v.x), m(v.y), m(v.z)))


def build(coll):
    b = common.Builder(REGIONS[:-1])

    def bx(r, a, c, bev=0.0, mat=None, seg=1):
        return b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg, matrix=mat)

    # five-star base + casters
    for k in range(5):
        ang = math.radians(90 + 72 * k)
        R = Matrix.Rotation(ang, 4, "Z")
        bx("plastic", (1.2, -LEG_W / 2, 3.0), (BASE_R - 0.6, LEG_W / 2, 4.3), 0.3, R)
        c = R @ Vector((m(BASE_R - 0.9), 0, 0))
        Rc = Matrix.Translation((c.x, c.y, 0)) @ Matrix.Rotation(ang, 4, "Z")
        bx("plastic", (-1.1, -0.9, 0.05), (1.1, 0.9, 2.1), 0.8, Rc, 2)       # twin-wheel body
        bx("metal", (-0.25, -0.25, 2.1), (0.25, 0.25, 3.0), 0.0, Rc)         # stem
    b.cylinder("plastic", (0, 0, m(3.7)), m(1.9), m(1.6), segments=12)       # hub
    b.cylinder("metal", (0, 0, m(9.5)), m(0.9), m(11.0), segments=12)        # gas lift
    b.cylinder("plastic", (0, 0, m(7.5)), m(1.3), m(6.0), segments=12)       # lower shroud
    bx("plastic", (-4.5, -5.0, 14.8), (4.5, 4.0, 16.6), 0.3)                # mechanism
    bx("plastic", (-0.5, -5.5, 15.2), (0.5, -4.0, 15.9), 0.1)                # tension knob stub
    # seat
    x0, x1, y0, y1 = SEAT
    bx("plastic", (x0 + 0.5, y0 + 0.5, SEAT_Z[0] - 0.3), (x1 - 0.5, y1 - 0.5, SEAT_Z[0] + 0.6), 0.3)
    bx("fabric", (x0, y0, SEAT_Z[0] + 0.6), (x1, y1, SEAT_Z[1]), 1.3, None, 2)
    # spine up to the backrest
    prof = [(-0.45, -1.3), (0.45, -1.3), (0.45, 1.3), (-0.45, 1.3)]
    pts = [(0, m(2.5), m(15.4)), (0, m(8.5), m(15.9)), (0, m(10.9), m(19.0)),
           (0, m(11.6), m(23.0)), (0, m(12.6), m(30.0))]
    b.sweep("plastic", pts, [(m(s), m(u)) for s, u in prof], up=(1, 0, 0))
    # backrest (shell + cushion)
    F = _back_frame()
    bx("plastic", (-BACK_W / 2 + 0.4, 0.8, 0.3), (BACK_W / 2 - 0.4, BACK_T / 2 + 0.2, BACK_H - 0.3), 1.0, F)
    bx("fabric", (-BACK_W / 2, -BACK_T / 2, 0.0), (BACK_W / 2, 0.9, BACK_H), 1.1, F, 2)
    # T-arms
    for s in (-1, 1):
        ax = s * ARM_X
        bx("plastic", (min(s * 4.0, ax), -3.0, 15.0), (max(s * 4.0, ax), -0.8, 16.0))     # bracket
        bx("plastic", (ax - 0.6, -3.0, 15.0), (ax + 0.6, -0.8, ARM_Z - 1.1), 0.2)          # post
        bx("pad", (ax - 1.6, -9.0, ARM_Z - 1.2), (ax + 1.6, 2.0, ARM_Z), 0.5, None, 2)     # pad
    # the draped cloth
    _cloth(b, "cloth")
    chair = b.to_object(NAME, coll)

    # chair mat: rectangle plus a lip reaching under the desk (toward -Y)
    g = common.Builder(["mat"])
    outline = [(-21.5, -21.5), (-9.5, -21.5), (-9.5, -31.5), (12.5, -31.5), (12.5, -21.5),
               (24.5, -21.5), (24.5, 25.5), (-21.5, 25.5)]
    g.prism("mat", [(m(x), m(y)) for x, y in outline], 0.0, m(MAT_T))
    mat = g.to_object(NAME + "_mat", coll)
    return [chair, mat]


def texture(objs):
    chair, matob = objs
    opaque = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_mat", ATLAS)
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = MAT_ALPHA
    try:
        clear.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        clear.blend_method = "BLEND"
    clear.use_backface_culling = False
    common.atlas_uvs(chair, ATLAS)
    common.collapse_materials(chair, {r: opaque for r in REGIONS[:-1]})
    common.atlas_uvs(matob, ATLAS)
    common.collapse_materials(matob, {"mat": clear})
