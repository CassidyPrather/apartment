"""Exterior view: a made-up, generic outside world seen through the windows and the
patio door. Nothing here is modelled on the real surroundings (Privacy): a lawn with
paths, foundation shrubs, card trees, a wooden fence, a row of plain two-storey
buildings beyond it, and a painted daytime sky on a curved backdrop.

Source of truth: scripted; every placement below is invented (EST by definition).
Frame: SHELL coordinates, not the usual object frame. Origin = the apartment's interior
south-west corner at floor level, +X east, +Y north, Z up; place on a marker at
(0, 0, 0) with no rotation. The building's exterior walls are 6 in thick, so the
outside starts at x < -6, y < -6, x > 288.75, y > 295.9. Views face west and south.

Three meshes / materials:
  exterior_view          opaque atlas (sky backdrop, fence, buildings, paths, patio);
                         its atlas carries an emission map on the sky only, so the sky
                         glows at full brightness; everything else needs light (bake)
  exterior_view_foliage  tree and shrub cards; atlas alpha is the cutout (wants
                         alpha-test/cutout; shipped as transparent alpha 1)
  exterior_view_ground   tiling lawn
Tree and shrub cards are crossed thin boxes (both faces point outward, so no
double-sided shader is needed).
"""

import importlib
import math
import os
import sys

import bmesh
from mathutils import Vector

import atlas_layout
import common

LIB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import shell_layout as L  # noqa: E402

importlib.reload(L)
m = L.m

NAME = "exterior_view"

# --- layout (inches, shell coordinates; all EST / invented) --------------------------
GROUND_Z = -4.0                    # lawn a little below the slab floor
GROUND = (-2600.0, 2900.0, -2600.0, 2900.0)
SKY_C = (141.0, 145.0)             # backdrop centre (the apartment's middle)
SKY_R = 2400.0                     # ~61 m
SKY_Z = (-300.0, 1800.0)
SKY_ARC = (100.0, 360.0)           # degrees (atan2 from +X toward +Y): NNW, W, S, E
SKY_SEGS = 26
GRASS_TILE = 2.0                   # metres per grass tile

PATHS = [                          # (x0, x1, y0, y1) concrete walks, 0.5 in above lawn
    (-130.0, -82.0, -140.0, 900.0),        # west walk, north-south
    (-600.0, 900.0, -140.0, -92.0),        # south walk, east-west
    (-82.0, -6.0, 145.0, 181.0),           # entry walk to the west door
    (225.0, 252.0, -92.0, -78.0),          # patio to the south walk
]
PATIO = (205.0, 275.0, -78.0, -6.0)        # patio slab outside the sliding door
FENCE_H = 72.0
FENCE_PANEL = 96.0
FENCE_WEST_X, FENCE_SOUTH_Y = -520.0, -560.0
FENCE_WEST_Y = (-560.0, 1000.0)
FENCE_SOUTH_X = (-520.0, 1100.0)

# Neighbouring two-storey blocks: (side, facing-edge coord, start, n units, unit width).
BLOCK_H, ROOF_H, BLOCK_D = 240.0, 70.0, 360.0
BLOCKS = [("south", -1250.0, -1100.0, 7, 380.0), ("west", -1250.0, -700.0, 5, 380.0)]

# Trees: (x, y, height, variant). Shrubs: (x, y, height, variant).
TREES = [
    (-300, -40, 380, "tree_a"), (-340, 120, 430, "tree_b"), (-270, 280, 340, "tree_c"),
    (-390, 450, 400, "tree_a"), (-320, -280, 360, "tree_c"), (-700, 60, 470, "tree_b"),
    (-760, 330, 520, "tree_a"), (-680, -300, 440, "tree_c"),
    (-60, -330, 400, "tree_c"), (140, -300, 380, "tree_a"), (360, -360, 430, "tree_b"),
    (560, -290, 350, "tree_c"), (-300, -440, 350, "tree_a"), (60, -760, 470, "tree_b"),
    (440, -800, 500, "tree_a"), (800, -420, 420, "tree_b"),
]
SHRUBS = [
    (-30, 20, 40, "shrub_a"), (-32, 60, 44, "shrub_b"), (-30, 100, 38, "shrub_a"),
    (-34, 128, 42, "shrub_b"), (-30, 205, 40, "shrub_a"), (-32, 250, 44, "shrub_b"),
    (20, -30, 42, "shrub_b"), (60, -32, 40, "shrub_a"), (100, -30, 44, "shrub_b"),
    (150, -32, 38, "shrub_a"), (185, -30, 42, "shrub_b"),
    (-490, -200, 54, "shrub_a"), (-490, 250, 58, "shrub_b"), (200, -530, 56, "shrub_a"),
    (-150, -530, 52, "shrub_b"), (500, -530, 60, "shrub_a"),
]
CARD_T = 0.5

ATLAS = {
    "name": "exterior_view",
    "size": 1024,
    "regions": {
        "sky": (0, 0, 1024, 512),
        "tree_a": (0, 512, 256, 384),
        "tree_b": (256, 512, 256, 384),
        "tree_c": (512, 512, 256, 384),
        "shrub_a": (768, 512, 256, 192),
        "shrub_b": (768, 704, 256, 192),
        "fence": (0, 896, 256, 128),
        "facade": (256, 896, 256, 128),
        "roof": (512, 896, 128, 128),
        "path": (640, 896, 128, 128),
        "patio": (768, 896, 128, 128),
        "wall_plain": (896, 896, 128, 128),
    },
}
GROUND_ATLAS = {"name": "exterior_ground", "size": 1024, "regions": {"grass": (0, 0, 1024, 1024)}}
FOLIAGE = ["tree_a", "tree_b", "tree_c", "shrub_a", "shrub_b"]
OPAQUE = ["sky", "fence", "facade", "roof", "path", "patio", "wall_plain"]

MATERIALS = {
    "exterior_view": {"atlas": "exterior_view", "mode": "opaque"},
    "exterior_view_foliage": {"atlas": "exterior_view", "mode": "cutout", "alpha": 0.5},   # alpha = cutoff
    "exterior_ground": {"atlas": "exterior_ground", "mode": "opaque", "tiled": True},
}
COLLIDER = "none"
STATIC = True
VIEWS = []


def box(b, region, lo, hi):
    b.box(region, tuple(m(v) for v in lo), tuple(m(v) for v in hi))


def gable(b, region, x0, x1, y0, y1, z0, z1, along):
    """Closed triangular roof prism, ridge running along `along` ("x" or "y")."""
    bm = b.bm
    if along == "x":
        yc = (y0 + y1) / 2
        ends = [[(x, y0, z0), (x, y1, z0), (x, yc, z1)] for x in (x0, x1)]
    else:
        xc = (x0 + x1) / 2
        ends = [[(x0, y, z0), (x1, y, z0), (xc, y, z1)] for y in (y0, y1)]
    a = [bm.verts.new(tuple(m(v) for v in p)) for p in ends[0]]
    c = [bm.verts.new(tuple(m(v) for v in p)) for p in ends[1]]
    faces = [bm.faces.new(a), bm.faces.new(list(reversed(c)))]
    for i in range(3):
        j = (i + 1) % 3
        faces.append(bm.faces.new((a[i], c[i], c[j], a[j])))
    b._tag(faces, region)


def card(b, region, x, y, h, w):
    """Two crossed thin boxes, h tall, w wide, standing on the lawn."""
    z0 = GROUND_Z
    box(b, region, (x - w / 2, y - CARD_T / 2, z0), (x + w / 2, y + CARD_T / 2, z0 + h))
    box(b, region, (x - CARD_T / 2, y - w / 2, z0), (x + CARD_T / 2, y + w / 2, z0 + h))


def sky(b):
    bm = b.bm
    cx, cy = SKY_C
    a0, a1 = SKY_ARC
    cols = []
    for i in range(SKY_SEGS + 1):
        t = math.radians(a0 + (a1 - a0) * i / SKY_SEGS)
        x, y = cx + SKY_R * math.cos(t), cy + SKY_R * math.sin(t)
        cols.append([bm.verts.new((m(x), m(y), m(z))) for z in SKY_Z])
    faces = []
    for i in range(SKY_SEGS):
        (p, q), (r, s) = cols[i], cols[i + 1]
        faces.append(bm.faces.new((p, r, s, q)))
    b._tag(faces, "sky")


def fence_run(b, axis, fixed, a0, a1):
    n = max(1, round((a1 - a0) / FENCE_PANEL))
    step = (a1 - a0) / n
    for i in range(n):
        s0, s1 = a0 + i * step, a0 + (i + 1) * step
        if axis == "x":
            box(b, "fence", (s0, fixed - 1, GROUND_Z), (s1, fixed + 1, GROUND_Z + FENCE_H))
        else:
            box(b, "fence", (fixed - 1, s0, GROUND_Z), (fixed + 1, s1, GROUND_Z + FENCE_H))


def blocks(b):
    for side, fixed, start, n, w in BLOCKS:
        depth = BLOCK_D
        for i in range(n):
            s0, s1 = start + i * w, start + (i + 1) * w - 2
            if side == "south":
                x0, x1, y0, y1 = s0, s1, fixed - depth, fixed
                box(b, "facade", (x0, y0, GROUND_Z), (x1, y1, BLOCK_H))
                gable(b, "roof", x0 - 12, x1 + 12, y0 - 12, y1 + 12, BLOCK_H, BLOCK_H + ROOF_H, "x")
            else:
                x0, x1, y0, y1 = fixed - depth, fixed, s0, s1
                box(b, "facade", (x0, y0, GROUND_Z), (x1, y1, BLOCK_H))
                gable(b, "roof", x0 - 12, x1 + 12, y0 - 12, y1 + 12, BLOCK_H, BLOCK_H + ROOF_H, "y")


def fix_sky_normals(ob):
    """The backdrop is an open strip; make every face point in toward the centre."""
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    c = Vector((m(SKY_C[0]), m(SKY_C[1]), 0))
    sky_idx = [i for i, mt in enumerate(me.materials) if mt.name.split(".")[0] == "sky"]
    flip = []
    for f in bm.faces:
        if f.material_index in sky_idx:
            fc = f.calc_center_median()
            to_c = Vector((c.x - fc.x, c.y - fc.y, 0))
            if f.normal.dot(to_c) < 0:
                flip.append(f)
    bmesh.ops.reverse_faces(bm, faces=flip)
    bm.to_mesh(me)
    bm.free()


def build(coll):
    b = common.Builder(OPAQUE)
    sky(b)
    for x0, x1, y0, y1 in PATHS:
        box(b, "path", (x0, y0, GROUND_Z - 1), (x1, y1, GROUND_Z + 0.5))
    x0, x1, y0, y1 = PATIO
    box(b, "patio", (x0, y0, GROUND_Z - 1), (x1, y1, -1.0))
    fence_run(b, "y", FENCE_WEST_X, *FENCE_WEST_Y)
    fence_run(b, "x", FENCE_SOUTH_Y, *FENCE_SOUTH_X)
    blocks(b)
    main = b.to_object("exterior_view", coll)
    fix_sky_normals(main)

    f = common.Builder(FOLIAGE)
    for x, y, h, v in TREES:
        card(f, v, x, y, h, h * 0.75)
    for x, y, h, v in SHRUBS:
        card(f, v, x, y, h, h * 1.4)
    foliage = f.to_object("exterior_view_foliage", coll)

    g = common.Builder(["grass"])
    gx0, gx1, gy0, gy1 = GROUND
    box(g, "grass", (gx0, gy0, GROUND_Z - 2), (gx1, gy1, GROUND_Z))
    ground = g.to_object("exterior_view_ground", coll)
    return [main, foliage, ground]


def face_uvs(ob):
    """Per-face UVs: sky by angle around the backdrop, grass tiled in world metres, and
    everything else stretched so each face shows its whole region (a fence panel, a
    tree card, a building front). Sliver faces (card edges) collapse onto a corner."""
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    me.uv_layers.active = uvl
    regions = [mt.name.split(".")[0] for mt in me.materials]
    for p in me.polygons:
        region = regions[p.material_index]
        cos = [me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
        if region == "grass":
            for li, co in zip(p.loop_indices, cos):
                uvl.data[li].uv = (co.x / GRASS_TILE, co.y / GRASS_TILE)
            continue
        u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, region)
        if region == "sky":
            a0, a1 = SKY_ARC
            for li, co in zip(p.loop_indices, cos):
                t = math.degrees(math.atan2(co.y - m(SKY_C[1]), co.x - m(SKY_C[0]))) % 360.0
                if t < a0 - 1:
                    t += 360.0
                fu = (t - a0) / (a1 - a0)
                fv = (co.z - m(SKY_Z[0])) / (m(SKY_Z[1]) - m(SKY_Z[0]))
                uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))
            continue
        n = p.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        ua, va = [(1, 2), (0, 2), (0, 1)][ax]
        us = [c[ua] for c in cos]
        vs = [c[va] for c in cos]
        du, dv = max(us) - min(us), max(vs) - min(vs)
        if region in FOLIAGE and (du < m(2.0) or ax == 2):
            for li in p.loop_indices:
                uvl.data[li].uv = (u0, v1)          # a transparent corner
            continue
        for li, co in zip(p.loop_indices, cos):
            fu = (co[ua] - min(us)) / max(du, 1e-6)
            fv = (co[va] - min(vs)) / max(dv, 1e-6)
            uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def texture(objs):
    main, foliage, ground = objs
    opaque = common.atlas_material("exterior_view", ATLAS)
    leaves = common.atlas_material("exterior_view_foliage", ATLAS)
    grass = common.atlas_material("exterior_ground", GROUND_ATLAS, tiled=True)
    # Blender preview of the cutout: albedo alpha -> BSDF alpha, dithered.
    nt = leaves.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    alb = next(n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image and n.image.name.endswith("_albedo.png"))
    nt.links.new(alb.outputs["Alpha"], bsdf.inputs["Alpha"])
    for n in nt.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name.endswith("_emission.png"):
            for lk in list(n.outputs["Color"].links):
                nt.links.remove(lk)          # Unity's transparent mode drops emission too
    bsdf.inputs["Emission Strength"].default_value = 0.0
    try:
        leaves.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        leaves.blend_method = "HASHED"
    for ob in objs:
        face_uvs(ob)
    common.collapse_materials(main, {r: opaque for r in OPAQUE})
    common.collapse_materials(foliage, {r: leaves for r in FOLIAGE})
    common.collapse_materials(ground, {"grass": grass})
