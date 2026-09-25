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
    return 0.034 * u * u

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

def rounded_rect(w, h, r, n=6, edge=10):
    """Rounded rectangle outline with extra points along the long edges, so the wrap can
    curve them (straight edges with only corner points stay straight)."""
    corners = []
    for cx, cz, a0 in [(w/2-r, h/2-r, 0), (-w/2+r, h/2-r, 90), (-w/2+r, -h/2+r, 180), (w/2-r, -h/2+r, 270)]:
        corners.append([(cx + r*math.cos(math.radians(a0 + 90 * i / n)), cz + r*math.sin(math.radians(a0 + 90 * i / n))) for i in range(n + 1)])
    pts = []
    for k, arc_pts in enumerate(corners):
        pts += arc_pts
        a, b = arc_pts[-1], corners[(k + 1) % 4][0]
        segs = edge if abs(a[1] - b[1]) < 1e-6 else 2        # the top and bottom edges run across the face
        pts += [(a[0] + (b[0] - a[0]) * j / segs, a[1] + (b[1] - a[1]) * j / segs) for j in range(1, segs)]
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
for v in gasket.data.vertices:              # the cushion curves round the face with the visor
    u = v.co.x / 0.07
    depth = (v.co.y - wrap(v.co.x) - 0.004) / 0.015          # 0 at the visor, 1 at the face
    v.co.y += 0.020 * u * u * depth                           # sides wrap back towards the temples
    if depth > 0.5:
        v.co.y -= 0.004 * (1 - u * u) * (1 if v.co.z > 0 else 0.4)   # forehead / nose dip

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

# Rear halo (Cassidy's headset photos). Hinged on two big side knobs:
#   - an upper arc over the back of the crown,
#   - just below it (a narrow lens-shaped gap between them) the wide main band with the
#     dial, arching up a little in the middle,
#   - under the band two padded lobes curving down and inward that almost meet (an
#     incomplete lower arc), leaving an oval hole. There is no top strap.
HX, HY, HZ = 0.105, 0.180, 0.046          # hoop half-width and knob axis (y, z)
# Seen from the side, the three pieces lie on one curve round the back of the head: the
# centre of each is a point on a circle about the head centre (upper arc high, band at the
# back, lobes low and curving forward).
HEAD_C, HEAD_R = Vector((0, 0.135, 0.050)), 0.108
def on_head(phi_deg):
    f = math.radians(phi_deg)
    return HEAD_C.y + HEAD_R * math.cos(f) - HY, HEAD_C.z + HEAD_R * math.sin(f) - HZ   # (b, lift) for arc()
UP_B, UP_LIFT = on_head(58)
BAND_B, BAND_LIFT = on_head(8)
LOBE_B, LOBE_LIFT = on_head(-36)
def arc(t_deg, b, lift, back_frac=1.0, inset=0.0):
    """Knob-to-knob arc: t 0..180 from the right knob round the back to the left knob."""
    t = math.radians(t_deg); s_ = math.sin(t)
    return Vector(((HX - inset) * math.cos(t), HY + (b - inset) * s_ * back_frac, HZ + lift * s_))
# The hoop is ONE curved plate cupping the back of the head (from the side it reads as a
# single curve): a surface swept from knob to knob through latitude PHI, with a
# lens-shaped gap under the upper arc, an oval hole under the band and a gap between the
# two lobes at the bottom (the incomplete lower arc).
def plate_pt(t_deg, phi_deg, inset=0.0):
    b, lift = on_head(phi_deg)
    t = math.radians(t_deg); s_ = math.sin(t)
    p = Vector((HX * math.cos(t), HY + b * s_, HZ + lift * s_))
    if inset:
        p += (HEAD_C + Vector((p.x * 0.3, 0, 0)) - p).normalized() * inset
    return p
T0, T1, PHI0, PHI1 = 3.0, 177.0, -38.0, 63.5
def lens_w(phi):                                  # half-width (in t degrees) of the gap under the upper arc
    k = (phi - 22) / 22
    return 56 * math.sin(math.pi * k) ** 0.6 if 0 < k < 1 else 0.0
def oval_w(phi):                                  # the hole under the band, wider at the top
    k = (phi + 28) / 26
    return 44 * math.sin(math.pi * (k * 0.9 + 0.1)) ** 0.7 * (0.75 + 0.25 * k) if 0 <= k <= 1 else 0.0
def gap_w(phi):                                   # between the lobes, spreading downward
    return 8 + (-28 - phi) * 2.2
def open_w(phi):
    """Half-width (t degrees) of the opening in the row at latitude phi; 0 = solid row.
    Below the band the oval hole runs into the gap between the lobe tips, so the lower
    arc is incomplete."""
    if phi <= -2:
        return max(oval_w(phi), gap_w(phi) if phi < -28 else 0.0)
    return lens_w(phi)
def plate(name, inset, material, keep_row, thick, n=13):
    """A regular grid whose columns sit exactly on the solid parts of each row, so the
    openings get smooth tapered edges and the shading stays even."""
    phis = [PHI0 + (PHI1 - PHI0) * i / 24 for i in range(25)]
    bm = bmesh.new(); rows = []
    for phi in phis:
        w = open_w(phi)
        left = [T0 + (90 - w - T0) * j / n for j in range(n + 1)]
        right = [90 + w + (T1 - 90 - w) * j / n for j in range(n + 1)]
        rows.append([bm.verts.new(plate_pt(t, phi, inset)) for t in left + right])
    for i in range(len(phis) - 1):
        if not (keep_row(phis[i]) and keep_row(phis[i + 1])):
            continue
        for j in range(2 * n + 1):
            if j == n and (open_w(phis[i]) > 0 or open_w(phis[i + 1]) > 0):
                continue                             # the opening between the two halves
            bm.faces.new((rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me), material)
    so = o.modifiers.new("solid", "SOLIDIFY"); so.thickness = thick; so.offset = 0
    bv = o.modifiers.new("bevel", "BEVEL"); bv.width = 0.0012; bv.segments = 1; bv.limit_method = 'ANGLE'
    for p in me.polygons: p.use_smooth = True
    o.modifiers.new("wn", "WEIGHTED_NORMAL")
    return o
plate("halo", 0.0, M["strap"], lambda phi: True, 0.005)
# foam lining on the inside of the band and the lobes (and a strip under the upper arc)
plate("halo_pad", 0.006, M["foam"], lambda phi: phi < 16 or phi > 46, 0.006)
# side knobs where the arms and the hoop pivot
for sx, tag in ((1, "r"), (-1, "l")):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.015, radius2=0.014, depth=0.024)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'))
    bmesh.ops.translate(bm, vec=(sx * (HX + 0.010), HY, HZ), verts=bm.verts)
    me = bpy.data.meshes.new("knob_" + tag); bm.to_mesh(me); bm.free()
    kb = link(bpy.data.objects.new("knob_" + tag, me), M["strap"])
    bv = kb.modifiers.new("bevel", "BEVEL"); bv.width = 0.002; bv.segments = 2
    for p in me.polygons: p.use_smooth = True
# side arms: flat rigid bands from the hinge at the visor's lower rear to the knobs
for sx, tag in ((1, "r"), (-1, "l")):
    sweep("arm_" + tag, [Vector((sx*0.071, 0.012, -0.012)), Vector((sx*0.084, 0.070, 0.014)), Vector((sx*(HX - 0.004), HY - 0.012, HZ))], P_ARM, M["strap"])
# rear adjustment dial on the outside of the main band, at the back centre
top = plate_pt(90, 8)
normal = Vector((0, math.cos(math.radians(8)), math.sin(math.radians(8))))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.016, radius2=0.015, depth=0.010)
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(normal).to_matrix())
bmesh.ops.translate(bm, vec=top + normal * 0.008, verts=bm.verts)
me = bpy.data.meshes.new("dial"); bm.to_mesh(me); bm.free()
d = link(bpy.data.objects.new("dial", me), M["strap"])
bv = d.modifiers.new("bevel", "BEVEL"); bv.width = 0.002; bv.segments = 2
for p in me.polygons: p.use_smooth = True

# --- speakers: each hangs from its own thin audio bar that runs forward from the knob,
# below the main side arm; the bar's front end is a slotted aluminium slider and the
# speaker's hub goes through the slot, the foam facing the ear. ---
M["metal"] = mat("cable", (0.55, 0.56, 0.58, 1), 0.35)   # region "cable" doubles as brushed metal
P_BAR = profile("prof_bar", 0.003, 0.010, 0.0014)
for sx, tag in ((1, "r"), (-1, "l")):
    # straight from the knob, forward and a little down
    k0, k1 = Vector((sx * (HX + 0.004), HY - 0.006, HZ - 0.012)), Vector((sx * 0.090, 0.066, -0.013))
    sweep("audio_bar_" + tag, [k0, k1], P_BAR, M["strap"])
    a0, a1 = k1.lerp(k0, 0.02), k1.lerp(k0, 0.48)          # the slotted slider is the bar's front half
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.002, 0.060, 0.010), verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Vector((0, 1, 0)).rotation_difference(a1 - a0).to_matrix())
    bmesh.ops.translate(bm, vec=(a0 + a1) / 2 + Vector((sx * 0.0025, 0, 0)), verts=bm.verts)
    me = bpy.data.meshes.new("slider_" + tag); bm.to_mesh(me); bm.free()
    link(bpy.data.objects.new("slider_" + tag, me), M["metal"])
    hub = k1.lerp(k0, 0.25)
    for part, r, depth, off, mm in (("speaker_hub_" + tag, 0.007, 0.012, 0.004, M["strap"]),
                                    ("speaker_" + tag, 0.021, 0.010, -0.006, M["strap"]),
                                    ("speaker_pad_" + tag, 0.027, 0.014, -0.016, M["foam"])):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r, radius2=r * 0.92, depth=depth)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90 * sx), 3, 'Y'))
        bmesh.ops.translate(bm, vec=hub + Vector((sx * off, 0, 0)), verts=bm.verts)
        me = bpy.data.meshes.new(part); bm.to_mesh(me); bm.free()
        o = link(bpy.data.objects.new(part, me), mm)
        bv = o.modifiers.new("bevel", "BEVEL"); bv.width = 0.007 if "pad" in part else 0.002; bv.segments = 2
        for p in me.polygons: p.use_smooth = True

# Resting pose on the cabinet (package frame: visor faces +X, origin on the surface).
root.rotation_euler = (0, 0, math.radians(90))
root.location = (0.101, 0, 0.030)
print("headset objects:", len([o for o in scn.objects if o.parent == root]))
