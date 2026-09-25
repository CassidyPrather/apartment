"""Shared helpers for the scripted Blender builds.

Mesh building (bmesh boxes, cylinders, sweeps), per-region atlas UVs, materials that
mirror the Unity setup, verification renders, and FBX export. Runs inside Blender,
either through the Blender MCP (exec the build script) or headless with `blender -b -P`.
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

LIB = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(LIB, "..", ".."))
if LIB not in sys.path:
    sys.path.insert(0, LIB)

from atlas_layout import uv_rect  # noqa: E402

TEXTURES = os.path.join(ROOT, "Assets", "Apartment", "Textures")
MODELS = os.path.join(ROOT, "Assets", "Apartment", "Models")
OUT = os.path.join(ROOT, "blender", "out")


# --- scene -------------------------------------------------------------------------

def reset_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras,
                 bpy.data.lights, bpy.data.images):
        for block in list(coll):
            if block.users == 0:
                coll.remove(block)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    scn = bpy.context.scene
    scn.unit_settings.system = "METRIC"
    scn.unit_settings.scale_length = 1.0


def collection(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


# --- mesh building -----------------------------------------------------------------

class Builder:
    """Accumulates geometry into one bmesh; each part tags its faces with a region."""

    def __init__(self, regions):
        self.bm = bmesh.new()
        self.regions = list(regions)

    def idx(self, region):
        return self.regions.index(region)

    def _tag(self, faces, region):
        i = self.idx(region)
        for f in faces:
            f.material_index = i

    def box(self, region, lo, hi, bevel=0.0, segments=2, matrix=None):
        """Box from corner lo to corner hi, optionally with rounded edges, then
        optionally moved by `matrix` (for rotated parts)."""
        lo, hi = Vector(lo), Vector(hi)
        size = hi - lo
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        verts = r["verts"]
        bmesh.ops.scale(self.bm, vec=size, verts=verts)
        bmesh.ops.translate(self.bm, vec=(lo + hi) / 2, verts=verts)
        if matrix is not None:
            bmesh.ops.transform(self.bm, matrix=matrix, verts=verts)
        faces = list({f for v in verts for f in v.link_faces})
        self._tag(faces, region)          # tag first: bevel faces inherit it
        if bevel > 0:
            edges = list({e for v in verts for e in v.link_edges})
            bmesh.ops.bevel(self.bm, geom=edges + verts, offset=min(bevel, min(size) * 0.49),
                            segments=segments, affect="EDGES", profile=0.5,
                            material=self.idx(region))
        return faces

    def cylinder(self, region, center, radius, depth, axis="Z", segments=24, cap_region=None,
                 bevel=0.0):
        r = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=segments,
                                  radius1=radius, radius2=radius, depth=depth)
        verts = r["verts"]
        rot = {"X": Matrix.Rotation(math.pi / 2, 4, "Y"),
               "Y": Matrix.Rotation(math.pi / 2, 4, "X"),
               "Z": Matrix.Identity(4)}[axis]
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(center) @ rot, verts=verts)
        faces = list({f for v in verts for f in v.link_faces})
        self._tag(faces, region)
        if cap_region:
            self.bm.normal_update()
            ax = Vector({"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}[axis])
            self._tag([f for f in faces if abs(f.normal.dot(ax)) > 0.99], cap_region)
        if bevel > 0:
            edges = [e for e in {e for v in verts for e in v.link_edges}
                     if len(e.link_faces) == 2 and e.calc_face_angle(0) > 0.6]
            bmesh.ops.bevel(self.bm, geom=edges, offset=bevel, segments=2, affect="EDGES",
                            material=self.idx(region))
        return faces

    def prism(self, region, outline, z0, z1, cap_region=None, bottom_region=None):
        """Extrude a closed 2D outline (list of (x, y)) from z0 to z1."""
        area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(outline, outline[1:] + outline[:1]))
        if area < 0:
            outline = list(reversed(outline))     # CCW so side normals point outward
        bot = [self.bm.verts.new((x, y, z0)) for x, y in outline]
        top = [self.bm.verts.new((x, y, z1)) for x, y in outline]
        n = len(outline)
        sides = [self.bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
                 for i in range(n)]
        cap = self.bm.faces.new(top)
        base = self.bm.faces.new(list(reversed(bot)))
        self._tag(sides, region)
        self._tag([cap], cap_region or region)
        self._tag([base], bottom_region or region)
        return sides + [cap, base]

    def sweep(self, region, points, profile, up=(0, 0, 1), closed=False, caps=True, ups=None):
        """Sweep a 2D profile [(side, up), ...] (CCW) along a 3D polyline."""
        pts = [Vector(p) for p in points]
        n = len(pts)
        rings = []
        for i, p in enumerate(pts):
            if closed:
                t = pts[(i + 1) % n] - pts[i - 1]
            else:
                t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
            t.normalize()
            u = Vector(ups[i] if ups else up)
            side = t.cross(u)
            if side.length < 1e-6:
                side = t.orthogonal()
            side.normalize()
            u2 = side.cross(t).normalized()
            rings.append([self.bm.verts.new(p + side * s + u2 * v) for s, v in profile])
        faces = []
        m = len(profile)
        segs = range(n) if closed else range(n - 1)
        for i in segs:
            a, b = rings[i], rings[(i + 1) % n]
            for j in range(m):
                faces.append(self.bm.faces.new((a[j], a[(j + 1) % m], b[(j + 1) % m], b[j])))
        if caps and not closed:
            faces.append(self.bm.faces.new(list(reversed(rings[0]))))
            faces.append(self.bm.faces.new(rings[-1]))
        self._tag(faces, region)
        return faces

    def to_object(self, name, coll=None, origin=(0, 0, 0)):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        bmesh.ops.translate(self.bm, vec=-Vector(origin), verts=self.bm.verts)
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name, me)
        ob.location = origin
        (coll or bpy.context.scene.collection).objects.link(ob)
        for region in self.regions:
            me.materials.append(placeholder_material(region))
        return ob


def rounded_rect(cx, cy, w, h, r, seg=6):
    """CCW outline of a rounded rectangle."""
    pts = []
    corners = [(cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90),
               (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)]
    for x, y, a0 in corners:
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return pts


def circle_profile(radius, n=8):
    return [(radius * math.cos(2 * math.pi * i / n), radius * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def rect_profile(w, h):
    return [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]


def smooth_path(points, samples=6):
    """Catmull-Rom through points, for cables and straps."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for s in range(samples):
            t = s / samples
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(pts[-1])
    return out


# --- materials ---------------------------------------------------------------------

def placeholder_material(region):
    mat = bpy.data.materials.get(region) or bpy.data.materials.new(region)
    return mat


def _image(path, non_color=False):
    name = os.path.basename(path)
    img = bpy.data.images.get(name)
    if img is None:
        img = bpy.data.images.load(path)
    else:
        img.reload()
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def atlas_material(name, atlas, tiled=False):
    """Principled material wired like VRChat Standard Lite: albedo, mask (R metallic,
    A smoothness) and optional emission."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    alb = nt.nodes.new("ShaderNodeTexImage")
    alb.image = _image(os.path.join(TEXTURES, f"{atlas}_albedo.png"))
    msk = nt.nodes.new("ShaderNodeTexImage")
    msk.image = _image(os.path.join(TEXTURES, f"{atlas}_mask.png"), non_color=True)
    for t in (alb, msk):
        t.interpolation = "Linear"
        t.extension = "REPEAT" if tiled else "EXTEND"
        nt.links.new(uv.outputs[0], t.inputs[0])
    nt.links.new(alb.outputs["Color"], bsdf.inputs["Base Color"])
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(msk.outputs["Color"], sep.inputs[0])
    nt.links.new(sep.outputs[0], bsdf.inputs["Metallic"])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(msk.outputs["Alpha"], inv.inputs[1])
    nt.links.new(inv.outputs[0], bsdf.inputs["Roughness"])
    emis_path = os.path.join(TEXTURES, f"{atlas}_emission.png")
    if os.path.exists(emis_path):
        em = nt.nodes.new("ShaderNodeTexImage")
        em.image = _image(emis_path)
        nt.links.new(uv.outputs[0], em.inputs[0])
        nt.links.new(em.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.0
    return mat


def checker_material():
    mat = bpy.data.materials.get("uv_checker") or bpy.data.materials.new("uv_checker")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    img = bpy.data.images.get("uv_checker_grid") or bpy.data.images.new(
        "uv_checker_grid", 1024, 1024)
    img.generated_type = "COLOR_GRID"
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "UVMap"
    nt.links.new(uv.outputs[0], tex.inputs[0])
    nt.links.new(tex.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return mat


def collapse_materials(ob, slot_to_material):
    """Replace the per-region placeholder slots with the final materials.

    slot_to_material maps region name -> bpy material. Regions sharing a material merge
    into one slot, so each object ends with one slot per real material."""
    me = ob.data
    regions = [m.name.split(".")[0] for m in me.materials]
    finals = []
    for r in regions:
        m = slot_to_material[r]
        if m not in finals:
            finals.append(m)
    remap = [finals.index(slot_to_material[r]) for r in regions]
    new_idx = [remap[p.material_index] for p in me.polygons]
    me.materials.clear()          # also drops the material_index attribute in Blender 4+
    for m in finals:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", new_idx)
    me.update()


# --- UVs ---------------------------------------------------------------------------

def _loops_by_region(ob):
    me = ob.data
    regions = [m.name.split(".")[0] for m in me.materials]
    by = {}
    for p in me.polygons:
        by.setdefault(regions[p.material_index], []).append(p)
    return by


def _axes(axis):
    # (u axis, v axis) for a planar projection seen from `axis` (e.g. "-Y" = from the front)
    return {
        "+Z": ((1, 0, 0), (0, 1, 0)), "-Z": ((1, 0, 0), (0, -1, 0)),
        "+Z_rot": ((0, 1, 0), (-1, 0, 0)),     # from above, u along Y (rows run along X)
        "-Y": ((1, 0, 0), (0, 0, 1)), "+Y": ((-1, 0, 0), (0, 0, 1)),
        "+X": ((0, 1, 0), (0, 0, 1)), "-X": ((0, -1, 0), (0, 0, 1)),
    }[axis]


def atlas_uvs(ob, atlas, planar=None, tiled=None):
    """Write UVMap: each region's faces land in that region's atlas rect.

    planar: {region: (axis, (umin, umax), (vmin, vmax))} projects those faces straight
            along an axis (object space), mapping the given bounds onto the rect exactly.
    tiled:  {region: meters_per_tile} box-projects in object space for a repeating
            material (outside the atlas).
    Everything else is box-projected per face and normalized into its rect."""
    planar = planar or {}
    tiled = tiled or {}
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    me.uv_layers.active = uvl
    bb_lo = Vector([min(v.co[i] for v in me.vertices) for i in range(3)])
    bb_hi = Vector([max(v.co[i] for v in me.vertices) for i in range(3)])
    ext = bb_hi - bb_lo
    for region, polys in _loops_by_region(ob).items():
        if region in tiled:
            s = tiled[region]
            for p in polys:
                n = p.normal
                ax = max(range(3), key=lambda i: abs(n[i]))
                ua, va = [(1, 2), (0, 2), (0, 1)][ax]
                for li in p.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    uvl.data[li].uv = (co[ua] / s, co[va] / s)
            continue
        u0, v0, u1, v1 = uv_rect(atlas, region)
        if region in planar:
            axis, (umin, umax), (vmin, vmax) = planar[region]
            ua, va = map(Vector, _axes(axis))
            for p in polys:
                for li in p.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    fu = (co.dot(ua) - umin) / (umax - umin)
                    fv = (co.dot(va) - vmin) / (vmax - vmin)
                    uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))
            continue
        for p in polys:
            n = p.normal
            ax = max(range(3), key=lambda i: abs(n[i]))
            ua, va = [(1, 2), (0, 2), (0, 1)][ax]
            for li in p.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                fu = (co[ua] - bb_lo[ua]) / max(ext[ua], 1e-6)
                fv = (co[va] - bb_lo[va]) / max(ext[va], 1e-6)
                uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def lightmap_uvs(ob):
    """Second UV channel for Unity's baked lightmaps (non-overlapping)."""
    me = ob.data
    if "UVLightmap" not in me.uv_layers:
        me.uv_layers.new(name="UVLightmap")
    me.uv_layers.active = me.uv_layers["UVLightmap"]
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.02,
                             scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    me.uv_layers.active = me.uv_layers["UVMap"]
    me.uv_layers["UVMap"].active_render = True


def shade_flat_with_sharp(ob, angle=35):
    """Smooth shading up to `angle`, crisp beyond (Blender 4.1+ API)."""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


# --- verification renders ----------------------------------------------------------

def render_setup(engine_pref=("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"), res=(900, 900)):
    scn = bpy.context.scene
    for eng in engine_pref:
        try:
            scn.render.engine = eng
            break
        except TypeError:
            continue
    scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.resolution_percentage = 100
    scn.render.film_transparent = False
    scn.view_settings.view_transform = "AgX"
    scn.view_settings.look = "None"
    world = bpy.data.worlds.get("verify_world") or bpy.data.worlds.new("verify_world")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.55, 0.55, 0.57, 1)
    bg.inputs["Strength"].default_value = 0.35
    scn.world = world


def stage(coll_name="verify_stage", floor=True, wall_y=None):
    """Neutral floor (and optional back wall) plus a key and fill light."""
    coll = collection(coll_name)
    if floor and "stage_floor" not in bpy.data.objects:
        me = bpy.data.meshes.new("stage_floor")
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("stage_floor", me)
        coll.objects.link(ob)
        mat = bpy.data.materials.new("stage_floor")
        mat.use_nodes = True
        b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0.33, 0.3, 0.28, 1)
        b.inputs["Roughness"].default_value = 0.9
        me.materials.append(mat)
    if wall_y is not None and "stage_wall" not in bpy.data.objects:
        me = bpy.data.meshes.new("stage_wall")
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3)
        bmesh.ops.rotate(bm, verts=bm.verts, matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, wall_y, 3))
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new("stage_wall", me)
        coll.objects.link(ob)
        mat = bpy.data.materials.new("stage_wall")
        mat.use_nodes = True
        b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (0.8, 0.78, 0.75, 1)
        me.materials.append(mat)
    if "key_light" not in bpy.data.objects:
        for name, loc, energy, size in (("key_light", (1.6, -2.2, 2.6), 160, 1.5),
                                         ("fill_light", (-2.4, -1.0, 1.8), 60, 2.5)):
            ld = bpy.data.lights.new(name, "AREA")
            ld.energy = energy
            ld.size = size
            lo = bpy.data.objects.new(name, ld)
            lo.location = loc
            lo.rotation_euler = (Vector((0, 0, 0.5)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
            coll.objects.link(lo)
    return coll


def camera_views(target, radius, views, lens=50):
    """views: [(name, azimuth_deg, elevation_deg, distance_scale)] around target.

    Azimuth 0 looks from the front (-Y) toward +Y; positive azimuth orbits toward +X."""
    coll = collection("verify_cameras")
    cams = []
    for name, az, el, ds in views:
        cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
        cd.lens = lens
        cd.clip_start = 0.01
        ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, cd)
        if ob.name not in coll.objects:
            coll.objects.link(ob)
        a, e = math.radians(az), math.radians(el)
        d = radius * ds
        off = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * d
        ob.location = Vector(target) + off
        ob.rotation_euler = (-off).to_track_quat("-Z", "Y").to_euler()
        cams.append(ob)
    return cams


def render_views(cams, folder, prefix):
    os.makedirs(folder, exist_ok=True)
    scn = bpy.context.scene
    paths = []
    for cam in cams:
        scn.camera = cam
        path = os.path.join(folder, f"{prefix}_{cam.name}.png")
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def with_material_override(objects, mat, fn):
    """Temporarily swap every slot on objects to mat, run fn, restore."""
    saved = {ob.name: [s.material for s in ob.material_slots] for ob in objects}
    for ob in objects:
        for s in ob.material_slots:
            s.material = mat
    try:
        return fn()
    finally:
        for ob in objects:
            for s, m in zip(ob.material_slots, saved[ob.name]):
                s.material = m


# --- export ------------------------------------------------------------------------

def export_fbx(objects, path):
    """FBX for Unity: Y-up, transforms baked, so objects import at scale 1, rotation 0."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, object_types={"MESH", "EMPTY"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z", axis_up="Y", bake_space_transform=True,
        use_mesh_modifiers=True, mesh_smooth_type="FACE", use_tspace=False,
        add_leaf_bones=False, bake_anim=False, path_mode="STRIP")
    print("exported", os.path.relpath(path, ROOT))
