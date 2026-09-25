"""Shared helpers for the alpha-cutout plant packages (plant_tall, plant_broadleaf) and
any package that wants per-face UVs it sets itself (the portable AC hose).

Cards are two back-to-back quads (one per side, opposite winding), so a single-sided
cutout shader shows both sides. CardBuilder skips the normal recalculation that
common.Builder.to_object does, because it would flip one quad of each pair.

Per-face UVs: faces made here carry normalised (0..1) UVs in a "card01" loop layer;
`apply_card_uvs` maps those into each region's atlas rect after common.atlas_uvs and
then removes the layer, so the FBX keeps just UVMap (+ the lightmap UVs).
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import atlas_layout
import common

LAYER = "card01"


class CardBuilder(common.Builder):
    def __init__(self, regions, recalc=True):
        super().__init__(regions)
        self.recalc = recalc
        self.uv = self.bm.loops.layers.uv.new(LAYER)
        self.card_faces = set()

    def set_uvs(self, face, uvs):
        for loop, uv in zip(face.loops, uvs):
            loop[self.uv].uv = uv

    def card(self, region, origin, width, height, yaw, tilt, roll=0.0, bend=0.0, segs=1,
             flip_u=False):
        """A vertical card, bottom edge centred at `origin`, width across and `height`
        up, then tilted `tilt` degrees about its bottom edge (positive leans it along
        its facing direction), rolled about its own up axis, and yawed about Z.
        `bend` (degrees) curls it progressively over `segs` segments (drooping leaves).
        Before the yaw the card faces -Y and leans (tilt) and curls (bend) toward +Y, so
        yaw = heading - 90 sends the lean toward `heading`; v=0 at the bottom edge."""
        w = width / 2
        rows = []
        p = Vector((0, 0, 0))
        ang = 0.0
        pts = [p.copy()]
        for i in range(segs):
            ang += bend / segs if i else bend / segs / 2
            d = Vector((0, math.sin(math.radians(ang)), math.cos(math.radians(ang))))
            p = p + d * (height / segs)
            pts.append(p.copy())
        rot = (Matrix.Translation(origin) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
               @ Matrix.Rotation(math.radians(-tilt), 4, "X") @ Matrix.Rotation(math.radians(roll), 4, "Z"))
        backs = []
        for q in pts:
            pa, pb = rot @ Vector((-w, q.y, q.z)), rot @ Vector((w, q.y, q.z))
            rows.append([self.bm.verts.new(pa), self.bm.verts.new(pb)])
            backs.append([self.bm.verts.new(pa), self.bm.verts.new(pb)])
        faces = []
        u0, u1 = (1.0, 0.0) if flip_u else (0.0, 1.0)
        for i in range(segs):
            a, b = rows[i], rows[i + 1]
            v0, v1 = i / segs, (i + 1) / segs
            front = self.bm.faces.new((a[0], a[1], b[1], b[0]))
            self.set_uvs(front, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
            a, b = backs[i], backs[i + 1]
            back = self.bm.faces.new((b[0], b[1], a[1], a[0]))
            self.set_uvs(back, [(u0, v1), (u1, v1), (u1, v0), (u0, v0)])
            faces += [front, back]
        self._tag(faces, region)
        self.card_faces.update(faces)
        return faces

    def sweep_uv(self, region, points, profile, v_per_seg=1.0, **kw):
        """common.Builder.sweep with per-face UVs: u around the profile, v along the
        path (v_per_seg of the region per segment, wrapping)."""
        faces = self.sweep(region, points, profile, caps=False, **kw)
        m = len(profile)
        for k, f in enumerate(faces):
            i, j = divmod(k, m)
            va = (i * v_per_seg) % 1.0
            vb = va + v_per_seg
            if vb > 1.0 + 1e-6:
                va, vb = 0.0, v_per_seg
            ua, ub = j / m, (j + 1) / m
            self.set_uvs(f, [(ua, va), (ub, va), (ub, vb), (ua, vb)])
        return faces      # left to the normal recalculation (a tube is closed around)

    def to_object(self, name, coll=None, origin=(0, 0, 0)):
        if not self.recalc:
            bm = self.bm
            me = bpy.data.meshes.new(name)
            bm.to_mesh(me)
            bm.free()
            ob = bpy.data.objects.new(name, me)
            (coll or bpy.context.scene.collection).objects.link(ob)
            for region in self.regions:
                me.materials.append(common.placeholder_material(region))
            return ob
        # keep card faces' windings: recalc only the rest
        bm = self.bm
        rest = [f for f in bm.faces if f not in self.card_faces]
        if rest:
            bmesh.ops.recalc_face_normals(bm, faces=rest)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        (coll or bpy.context.scene.collection).objects.link(ob)
        for region in self.regions:
            me.materials.append(common.placeholder_material(region))
        return ob


def apply_card_uvs(ob, atlas, regions=None):
    """Map card01 UVs into the atlas rect of each face's region, then drop card01.
    Faces whose card01 UVs were never set (all zero) keep the UVMap they have."""
    me = ob.data
    if LAYER not in me.uv_layers:
        return
    src = me.uv_layers[LAYER]
    dst = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    names = [mt.name.split(".")[0] for mt in me.materials]
    for p in me.polygons:
        region = names[p.material_index]
        if regions is not None and region not in regions:
            continue
        uvs = [src.data[li].uv.copy() for li in p.loop_indices]
        if all(uv.length < 1e-9 for uv in uvs):
            continue
        u0, v0, u1, v1 = atlas_layout.uv_rect(atlas, region)
        for li, uv in zip(p.loop_indices, uvs):
            dst.data[li].uv = (u0 + uv.x * (u1 - u0), v0 + uv.y * (v1 - v0))
    me.uv_layers.remove(me.uv_layers[LAYER])
    me.uv_layers.active = me.uv_layers["UVMap"]


def cutout_material(name, atlas):
    """atlas_material with albedo alpha wired for a dithered Blender preview of the
    Unity cutout (same wiring as exterior_view's foliage)."""
    mat = common.atlas_material(name, atlas)
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    alb = next(n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image and n.image.name.endswith("_albedo.png"))
    nt.links.new(alb.outputs["Alpha"], bsdf.inputs["Alpha"])
    try:
        mat.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        mat.blend_method = "HASHED"
    return mat


def order_uvmap_first(ob):
    """Make sure UVMap is channel 0 (card01 was created first in the bmesh)."""
    me = ob.data
    if me.uv_layers and me.uv_layers[0].name != "UVMap" and "UVMap" not in me.uv_layers:
        me.uv_layers[0].name = "UVMap"
