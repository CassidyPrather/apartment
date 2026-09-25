"""PC VR headset: compact purple-shelled visor (vent slots, blue status light) with a
black face gasket and nose notch, thin side straps back to a padded rear cradle, a wide
top strap over the crown, off-ear speakers on pivot arms and a dial at the back. Resting
upright on the cabinet top.

Source of truth: modelled in the live Blender through the Blender MCP and saved as
blender/assets/vr_headset.blend (the modelling steps are in
blender/assets/vr_headset_model.py). The shape was fitted against the cabinet capture's
own cameras (photo | render | overlay). Object origin: on the resting surface near the
headset's centre. Local frame: the visor faces +X, up is +Z. Parody brand: squintscreen.

The visor is two layers: a translucent purple shell (its own material, alpha-blended
in Unity) around opaque internals, so the frame, lenses and blue status LED show
through the plastic like the real one.
"""

import importlib
import math
import os

import bpy

from mathutils import Matrix, Vector

import common
import dimensions

importlib.reload(dimensions)

HS = dimensions.HEADSET
REGIONS = ["visor_front", "visor_top", "visor_inner", "strap", "foam", "badge", "cable", "dial"]
SHELL_REGIONS = ("visor_front", "visor_top")

# Layout (meters, headset-local).
VISOR_FRONT_X = 0.135
VISOR_Z = (0.004, 0.004 + HS["visor_h"])
SHELL_ALPHA = 0.72          # dense tint; the internals show only faintly, as in the photos
# The strap is a closed oval ring standing across the headset behind the visor (seen
# face-on from behind, edge-on from above), leaning back a little, with the slotted
# crown pad inside its top and the adjustment dial at its bottom rear.
RING_X = HS["arch_x"]
RING_HALF_W = HS["arch_half_span"]
RING_Z0 = 0.012                        # bottom of the ring, just off the resting surface
RING_Z1 = HS["arch_height"]
RING_LEAN = math.radians(HS["ring_lean"])
RING_BAND, RING_T = 0.032, 0.020      # band depth (along x), radial thickness (orbit video)


def ring_point(theta):
    """Point on the ring; theta 0 = +Y side, pi/2 = top, 3pi/2 = bottom."""
    hz = (RING_Z1 - RING_Z0) / 2
    y = RING_HALF_W * math.cos(theta)
    z = hz * math.sin(theta) + hz                     # height above the ring's bottom
    return Vector((RING_X - z * math.sin(RING_LEAN), y, RING_Z0 + z * math.cos(RING_LEAN)))


RING_NORMAL = Vector((math.cos(RING_LEAN), 0.0, math.sin(RING_LEAN)))


def visor_arc(x_front, width, depth_curve=0.9, n=12):
    """Points along a visor front edge seen from above, curving back at the sides."""
    pts = []
    for i in range(n + 1):
        y = -width / 2 + width * i / n
        pts.append((x_front - depth_curve * y * y, y))
    return pts


def curved_slab(b, region, x_front, depth, width, z0, z1, cap_region, bottom_region):
    front = visor_arc(x_front, width)
    back = [(x - depth, y) for x, y in reversed(front)]
    return b.prism(region, front + back, z0, z1, cap_region=cap_region, bottom_region=bottom_region)


def edge_drop():
    """Tether points hanging over the cabinet's left edge, in headset-local coords."""
    px, py, rot = dimensions.PLACEMENT["vr_headset"]
    left = -dimensions.CABINET["width"] / 2
    a = -math.radians(rot)
    ye = py - 0.06
    out = []
    for x, y, z in ((left + 0.03, ye, 0.0022), (left - 0.002, ye - 0.002, -0.004), (left - 0.006, ye - 0.005, -0.11)):
        dx, dy = x - px, y - py
        out.append((dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a), z))
    return out


BLEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "vr_headset.blend")


def build(coll):
    """Append the hand-modelled headset (blender/assets/vr_headset.blend, modelled in the live
    Blender through the MCP against matched capture views), bake its modifiers and curves
    into one mesh, and add the tether cable, which depends on the cabinet placement."""
    with bpy.data.libraries.load(os.path.abspath(BLEND), link=False) as (src, dst):
        dst.objects = list(src.objects)
    loaded = [o for o in dst.objects if o is not None]
    for o in loaded:
        coll.objects.link(o)
    root = next(o for o in loaded if o.name.startswith("hs_root"))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    base = root.parent.matrix_world.inverted() if root.parent else Matrix()
    parts = []
    for o in loaded:
        if o.type not in ("MESH", "CURVE") or o.hide_render or not _under(o, root):
            continue
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.transform(base @ o.matrix_world)
        parts.append(bpy.data.objects.new(o.name + "_baked", me))
    for o in loaded:
        bpy.data.objects.remove(o, do_unlink=True)
    # Tether: from the back of the visor, along the right arm, across the cabinet top and
    # down its left side; the end is placed in cabinet space (edge_drop).
    b = common.Builder(["cable"])
    gx = VISOR_FRONT_X - HS["visor_d"] - HS["gasket_d"] * 0.5
    cpts = [(gx - 0.005, -0.02, VISOR_Z[1] - 0.002), (gx - 0.03, -0.06, 0.055), (-0.02, -0.095, 0.05),
            (-0.09, -0.11, 0.03), (-0.14, -0.12, 0.004)] + edge_drop()
    b.sweep("cable", common.smooth_path(cpts, 6), common.circle_profile(0.0022, 8), up=(0, 0, 1))
    parts.append(b.to_object("vr_headset_cable", coll))
    for p in parts:
        if p.name not in coll.objects:
            coll.objects.link(p)
    with bpy.context.temp_override(active_object=parts[0], selected_editable_objects=parts, object=parts[0]):
        bpy.ops.object.join()
    ob = parts[0]
    ob.name = ob.data.name = "vr_headset"
    return [ob]


def _under(o, root):
    while o.parent is not None:
        if o.parent == root:
            return True
        o = o.parent
    return False


def texture(obs):
    ob = obs[0]
    vw = HS["visor_w"]
    z0, z1 = VISOR_Z
    iw = vw - 0.014
    mat = common.atlas_material("vr_headset", "vr_headset")
    shell = common.atlas_material("vr_headset_shell", "vr_headset")
    bsdf = next(n for n in shell.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = SHELL_ALPHA
    shell.surface_render_method = "BLENDED"
    common.atlas_uvs(ob, "vr_headset", planar={
        "visor_front": ("+X", (-vw / 2, vw / 2), (z0, z1)),
        "visor_top": ("+Z_rot", (-vw / 2, vw / 2), (-VISOR_FRONT_X, -(VISOR_FRONT_X - HS["visor_d"]))),
        "visor_inner": ("+X", (-iw / 2, iw / 2), (z0 + 0.004, z1 - 0.004)),
    })
    common.collapse_materials(ob, {r: (shell if r in SHELL_REGIONS else mat) for r in REGIONS})
