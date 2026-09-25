# Modelling steps for blender/assets/vr_headset.blend, run in the live Blender through the Blender MCP.
# Headset, modelled in the live Blender (run through the Blender MCP). Worn pose, metres:
# visor front faces -Y, Z up, origin between the eyes. Everything is parented to hs_root.
import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

scn = bpy.data.scenes.get("headset") or bpy.data.scenes.new("headset")
bpy.context.window.scene = scn
scn.unit_settings.system = 'METRIC'; scn.unit_settings.length_unit = 'MILLIMETERS'
for o in list(scn.collection.all_objects):
    bpy.data.objects.remove(o, do_unlink=True)

def mat(name, rgba, rough=0.5, alpha=1.0, emit=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; m.use_fake_user = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = rgba; b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = emit; b.inputs["Emission Strength"].default_value = 8.0
    m.diffuse_color = rgba
    return m

M = {
    "shell": mat("visor_front", (0.32, 0.06, 0.42, 1), 0.25, alpha=0.75),
    "core": mat("visor_inner", (0.03, 0.03, 0.035, 1), 0.6),
    "foam": mat("foam", (0.02, 0.02, 0.022, 1), 0.95),
    "strap": mat("strap", (0.025, 0.025, 0.028, 1), 0.55),
    "lens": mat("dial", (0.05, 0.07, 0.09, 1), 0.1),
    "led": mat("badge", (0.1, 0.3, 1.0, 1), 0.3, emit=(0.15, 0.35, 1.0, 1)),
    "cable": mat("cable", (0.02, 0.02, 0.022, 1), 0.4),
}

root = bpy.data.objects.new("hs_root", None); scn.collection.objects.link(root)
root.empty_display_type = 'ARROWS'; root.empty_display_size = 0.05

def link(ob, material=None):
    if ob.name not in scn.collection.objects:
        for c in ob.users_collection: c.objects.unlink(ob)
        scn.collection.objects.link(ob)
    ob.parent = root; ob.matrix_parent_inverse = Matrix()
    if material is not None and ob.type in ('MESH', 'CURVE'):
        ob.data.materials.clear(); ob.data.materials.append(material)
    return ob

def wrap(x):                       # the visor sweeps back around the face
    u = x / 0.0715
    return 0.018 * u * u

# --- visor shell: W 143, H 52, shell depth 30 (the gasket makes up the rest of the 49) ---
W, H, D = 0.143, 0.052, 0.030
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.scale(bm, vec=(W, D, H), verts=bm.verts)
bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).x) > 1e-6], cuts=14, use_grid_fill=True)
bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).z) > 1e-6], cuts=4, use_grid_fill=True)
for v in bm.verts:
    x, y, z = v.co; u = x / (W / 2)
    top = 0.004 * (z / (H / 2) + 1) / 2 * (1 - 0.3 * u * u)
    v.co = (x * (1 - 0.05 * max(0, -z / (H / 2))), y + wrap(x) + (top if y < 0 else 0) - D / 2 - 0.004, z)
me = bpy.data.meshes.new("visor_shell"); bm.to_mesh(me); bm.free()
visor = link(bpy.data.objects.new("visor_shell", me), M["shell"])
# Dark internals filling the translucent shell (the real visor shows its electronics
# through the plastic; without this the shell reads pale against whatever is behind it).
inner = me.copy(); inner.name = "visor_internals"
c = sum((v.co for v in inner.vertices), Vector()) / len(inner.vertices)
for v in inner.vertices:
    v.co = c + (v.co - c) * Vector((0.95, 0.80, 0.86))
link(bpy.data.objects.new("visor_internals", inner), M["core"])

def rounded_rect(w, h, r, n=6):
    pts = []
    for cx, cz, a0 in [(w/2-r, h/2-r, 0), (-w/2+r, h/2-r, 90), (-w/2+r, -h/2+r, 180), (w/2-r, -h/2+r, 270)]:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + r*math.cos(a), cz + r*math.sin(a)))
    return pts

def ring(name, outer, inner, y0, y1, material):
    bm = bmesh.new(); rows = []
    for y in (y0, y1):
        rows.append(([bm.verts.new((x, y + wrap(x), z)) for x, z in outer], [bm.verts.new((x, y + wrap(x), z)) for x, z in inner]))
    n = len(outer); (o0, i0), (o1, i1) = rows
    for k in range(n):
        k2 = (k + 1) % n
        bm.faces.new((o0[k], o0[k2], o1[k2], o1[k])); bm.faces.new((i0[k2], i0[k], i1[k], i1[k2]))
        bm.faces.new((o0[k2], o0[k], i0[k], i0[k2])); bm.faces.new((o1[k], o1[k2], i1[k2], i1[k]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    return link(bpy.data.objects.new(name, me), material)

core = ring("visor_core", rounded_rect(0.140, 0.050, 0.014), rounded_rect(0.118, 0.034, 0.012), -0.004, 0.004, M["core"])
gasket = ring("face_gasket", rounded_rect(0.138, 0.049, 0.015), rounded_rect(0.112, 0.030, 0.012), 0.004, 0.019, M["foam"])
for v in gasket.data.vertices:              # face contour on the back edge
    if v.co.y > 0.004 + wrap(v.co.x) + 0.001:
        u = v.co.x / 0.07
        v.co.y -= 0.004 * (1 - u * u) * (1 if v.co.z > 0 else 0.4)

# nose notch through the bottom centre
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.018, radius2=0.018, depth=0.12)
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
bmesh.ops.scale(bm, vec=(1.0, 1.0, 1.25), verts=bm.verts)
bmesh.ops.translate(bm, vec=(0, 0, -0.030), verts=bm.verts)
me = bpy.data.meshes.new("nose_cutter"); bm.to_mesh(me); bm.free()
cutter = link(bpy.data.objects.new("nose_cutter", me)); cutter.display_type = 'WIRE'; cutter.hide_render = True
for ob in (visor, core, gasket):
    b = ob.modifiers.new("nose", "BOOLEAN"); b.object = cutter; b.operation = 'DIFFERENCE'; b.solver = 'EXACT'
    bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = 0.004 if ob is visor else 0.0025; bv.segments = 3 if ob is visor else 2
    bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(40)
    ob.modifiers.new("wn", "WEIGHTED_NORMAL")
    for p in ob.data.polygons: p.use_smooth = True
cutter.hide_set(True)

# lenses seen from behind
for sx, tag in ((-1, "l"), (1, "r")):
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=20, radius=0.018)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
    bmesh.ops.translate(bm, vec=(sx * 0.032, 0.005, 0.002), verts=bm.verts)
    me = bpy.data.meshes.new("lens_" + tag); bm.to_mesh(me); bm.free()
    link(bpy.data.objects.new("lens_" + tag, me), M["lens"])
    bm = bmesh.new(); bmesh.ops.create_circle(bm, segments=20, radius=0.0205)
    me = bpy.data.meshes.new("lens_ring_" + tag); bm.to_mesh(me); bm.free()
    lr = link(bpy.data.objects.new("lens_ring_" + tag, me), M["core"])
    lr.matrix_basis = Matrix.Translation((sx * 0.032, 0.006, 0.002)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    s = lr.modifiers.new("skin", "SCREW"); s.angle = 0; s.steps = 1; s.screw_offset = 0.003
    lr.modifiers.new("solid", "SOLIDIFY").thickness = 0.002

# vent slots along the top and the blue status light
for i in range(-4, 5):
    x = i * 0.013
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.0075, 0.012, 0.0012), verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.atan(2 * 0.018 * x / 0.0715 ** 2), 3, 'Z'))
    bmesh.ops.translate(bm, vec=(x, -0.020 + wrap(x), 0.0262), verts=bm.verts)
    me = bpy.data.meshes.new(f"vent_{i+4}"); bm.to_mesh(me); bm.free()
    link(bpy.data.objects.new(f"vent_{i+4}", me), M["core"])
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.010, 0.002, 0.004), verts=bm.verts)
bmesh.ops.translate(bm, vec=(0.048, -0.030 + wrap(0.048), 0.018), verts=bm.verts)
me = bpy.data.meshes.new("led_status"); bm.to_mesh(me); bm.free()
link(bpy.data.objects.new("led_status", me), M["led"])

# --- straps (curves with rounded-rectangle profiles) ---
def profile(name, w, h, r):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'
    sp = cu.splines.new('POLY'); pts = []
    for cx, cy, a0 in [(w/2-r, h/2-r, 0), (-w/2+r, h/2-r, 90), (-w/2+r, -h/2+r, 180), (w/2-r, -h/2+r, 270)]:
        for i in range(4):
            a = math.radians(a0 + 90 * i / 3); pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts): p.co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu); scn.collection.objects.link(ob); ob.hide_set(True); ob.hide_render = True
    return ob

def sweep(name, pts, prof, material, res=5):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.twist_mode = 'MINIMUM'
    cu.bevel_mode = 'OBJECT'; cu.bevel_object = prof; cu.use_fill_caps = True; cu.resolution_u = res
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    return link(bpy.data.objects.new(name, cu), material)

P_HALO = profile("prof_halo", 0.006, 0.032, 0.0025)
P_PAD = profile("prof_pad", 0.009, 0.026, 0.004)
P_ARM = profile("prof_arm", 0.004, 0.014, 0.0018)
P_TOP = profile("prof_top", 0.042, 0.004, 0.0019)     # wide band (matched top-down views)

# Rear cradle: only the back third of a long, narrow loop is the thick padded band; the
# sides are thin straps running nearly parallel from the temples (matched capture views).
RX, RY, CY = 0.078, 0.108, 0.088
def loop_pt(t_deg, inset=0.0, z0=0.012, rise=0.030):
    t = math.radians(t_deg)
    return Vector(((RX - inset) * math.cos(t), CY + (RY - inset) * math.sin(t), z0 + rise * max(0.0, math.sin(t)) ** 2))
sweep("halo", [loop_pt(t) for t in range(25, 160, 15)], P_HALO, M["strap"])
for k, (t0, t1) in enumerate([(32, 66), (72, 108), (114, 148)]):
    sweep(f"halo_pad_{k}", [loop_pt(t, inset=0.0075) for t in (t0, (t0 + t1) / 2, t1)], P_PAD, M["foam"])
for sx, tag in ((1, "r"), (-1, "l")):
    end = loop_pt(25 if sx > 0 else 155)
    sweep("arm_" + tag, [Vector((sx*0.068, 0.006, 0.004)), Vector((sx*0.077, 0.050, 0.010)), Vector((sx*0.079, 0.100, 0.012)), end + Vector((0, 0.01, 0))], P_ARM, M["strap"])
back = loop_pt(90)
sweep("top_strap", [Vector((0, 0.000, 0.026)), Vector((0, 0.050, 0.100)), Vector((0, 0.130, 0.125)), Vector((0, 0.195, 0.090)), back + Vector((0, -0.004, 0.012))], P_TOP, M["strap"])

# adjustment dial on the outside of the rear cradle, low down (matched capture views)
back = loop_pt(90)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.016, radius2=0.015, depth=0.016)
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
bmesh.ops.translate(bm, vec=(0, back.y + 0.011, back.z - 0.008), verts=bm.verts)
me = bpy.data.meshes.new("dial"); bm.to_mesh(me); bm.free()
d = link(bpy.data.objects.new("dial", me), M["lens"])
bv = d.modifiers.new("bevel", "BEVEL"); bv.width = 0.002; bv.segments = 3
for p in me.polygons: p.use_smooth = True

# --- speakers on pivot arms at the ears ---
for sx, tag in ((1, "r"), (-1, "l")):
    c = Vector((sx * 0.094, 0.082, -0.030))
    for part, r, depth, off, mm in (("speaker_" + tag, 0.022, 0.012, 0.0, M["strap"]), ("speaker_pad_" + tag, 0.020, 0.008, -0.009, M["foam"])):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=r, radius2=r, depth=depth)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
        bmesh.ops.translate(bm, vec=c + Vector((sx * off, 0, 0)), verts=bm.verts)
        me = bpy.data.meshes.new(part); bm.to_mesh(me); bm.free()
        o = link(bpy.data.objects.new(part, me), mm)
        bv = o.modifiers.new("bevel", "BEVEL"); bv.width = 0.004 if "pad" in part else 0.002; bv.segments = 2
        for p in me.polygons: p.use_smooth = True
    sweep("speaker_arm_" + tag, [Vector((sx*0.083, 0.070, 0.011)), Vector((sx*0.092, 0.078, -0.004)), Vector((sx*0.098, 0.082, -0.012))], P_ARM, M["strap"])

# Resting pose on the cabinet (package frame: visor faces +X, origin on the surface).
root.rotation_euler = (0, 0, math.radians(90))
root.location = (0.101, 0, 0.030)
print("headset objects:", len([o for o in scn.objects if o.parent == root]))
