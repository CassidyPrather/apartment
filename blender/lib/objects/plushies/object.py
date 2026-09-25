"""Plush toys on the dresser: a big green dragon with a dark octopus riding on its head,
a panda, a grey mouse, a purple bunny, a pink pig and a yellow chick on the dresser top,
and a plague-doctor plush and a cream bear on the clear organiser. All generic.

Source of truth: modelled by hand in the live Blender (Blender MCP) as soft fused shapes
(ellipsoids joined with a voxel remesh and smoothed), saved in
blender/assets/plushies.blend, one object per colour part, each at its own origin
(floor at the plush's footprint centre, front -Y). Material names are the atlas regions.
This package appends them, places them and decimates them to the budget.

Built in the dresser's local frame (origin on the floor at the dresser's footprint
centre, front -Y), so it shares the dresser placement: plan (264.75, 18), rotation -90.
Positions are the dresser survey's (inches, dresser-local); sizes are EST from the
bedroom photos.
"""

import math
import os

import bpy
from mathutils import Matrix

import common

NAME = "plushies"
IN = 0.0254
TOP = 58.5                  # dresser top (SCAN)
ORGANISER_TOP = TOP + 10.0  # the clear three-drawer organiser (EST)
BLEND = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "plushies.blend")
TRI_BUDGET = 9000

# plush: (x, y, z inches in dresser-local, yaw degrees)
PLACES = {
    "dragon": (-10.5, -3.5, TOP, 8),
    "octo": (-10.5, -3.2, TOP + 10.2, -6),       # rides on the dragon's head
    "panda": (-4.5, -5.5, TOP, 15),
    "mouse": (-6.0, 3.5, TOP, -10),
    "bunny": (-0.5, -2.0, TOP, 5),
    "pig": (3.0, -6.5, TOP, -12),
    "chick": (6.8, -6.0, TOP, 20),
    "doctor": (1.8, 3.5, ORGANISER_TOP, 10),
    "bear": (8.3, 4.0, ORGANISER_TOP, -15),
}

ATLAS = {
    "name": "plushies",
    "size": 512,
    "regions": {name: ((i % 4) * 128, (i // 4) * 128, 128, 128) for i, name in enumerate([
        "green", "green_light", "red", "black", "dark", "white", "cream", "grey",
        "pink", "purple", "yellow", "orange"])},
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"plushies": {"atlas": "plushies", "mode": "opaque"}}
COLLIDER = "none"
STATIC = True


def build(coll):
    with bpy.data.libraries.load(os.path.abspath(BLEND), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    parts = []
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in dst.objects if o)
    ratio = min(1.0, TRI_BUDGET / max(tris, 1))
    for ob in dst.objects:
        if ob is None:
            continue
        key = ob.name.split("_")[0]
        if key not in PLACES:
            bpy.data.objects.remove(ob, do_unlink=True)
            continue
        x, y, z, yaw = PLACES[key]
        coll.objects.link(ob)
        ob.matrix_world = Matrix.Translation((x * IN, y * IN, z * IN)) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        if ratio < 1.0:
            d = ob.modifiers.new("decimate", "DECIMATE")
            d.ratio = ratio
        parts.append(ob)
    # Apply the transforms and modifiers, then join into one mesh (material slots = regions).
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in parts:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        me.transform(ob.matrix_world)
        ob.modifiers.clear()
        ob.data = me
        ob.matrix_world = Matrix()
    out = parts[0]
    with bpy.context.temp_override(active_object=out, selected_editable_objects=parts, object=out):
        bpy.ops.object.join()
    out.name = NAME
    out.data.name = NAME
    return [out]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
    for p in ob.data.polygons:
        p.use_smooth = True
