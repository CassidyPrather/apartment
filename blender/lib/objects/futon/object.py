"""Futon: a king-size Japanese floor futon, the one Cassidy, Nora and Isha slept on during
the September visit. Two states, swapped by a switch in Unity: laid out flat on the
living room floor in front of the TV, or rolled up in its cylindrical sack against a wall.

Source of truth: modelled by hand in the live Blender (Blender MCP), saved in
blender/assets/futon.blend as two objects:
  futon_flat    76 x 80 x 4 in quilted mattress, rounded bulging edges, tufts on a
                5 x 6 grid (12.65 x 13.3 in), puffed panels between them
  futon_rolled  rolled lengthwise (not folded) and standing on end in its drawstring
                sack: 76 in tall (the futon's width) and ~20 in across (80 x 4 in of
                mattress rolled up), a soft ridge where the mattress edge ends, the
                sack gathered above it (84 in overall), a drawstring with a toggle
Each has its origin on the floor at its footprint centre (the flat one's length along +Y). One material
slot, "coffee" (the atlas region).

Product (Cassidy): MAXYOYO Japanese floor mattress, 4 in thick, king, in coffee. The
listing gives the size and thickness; the tuft layout and the roll's diameter are EST (Cassidy: rolled into a cylinder, "far longer") from typical
floor futons of this kind.

Built in PLAN coordinates (like bedroom_cables): the package goes on a marker at the plan
origin with no rotation, and each state is placed below.
"""

import math
import os

import bpy
from mathutils import Matrix

import common

NAME = "futon"
IN = 0.0254
BLEND = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "futon.blend")
TRI_BUDGET = {"futon_flat": 9000, "futon_rolled": 3000}   # the flat one keeps its tufts

# state: (plan x, plan y, heading deg: the futon's length runs along this direction)
PLACES = {
    # 76 in across between the couch front (x 44, blankets) and the toolboxes under the TV
    # (x 122), 80 in along the room clear of the bean bag (y 30) and the AC (y 109)
    "futon_flat": (83.0, 72.5, 90.0),
    # stored standing on end (Cassidy: "in a corner"); every living-room corner near the TV is
    # taken, so it stands against the south wall in the gap between the two plants (x 31..56)
    # until Cassidy says which corner
    "futon_rolled": (43.5, 11.3, 0.0),
}

ATLAS = {
    "name": "futon",
    "size": 256,
    "regions": {"coffee": (0, 0, 256, 256)},
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"futon": {"atlas": "futon", "mode": "opaque"}}
COLLIDER = "none"
STATIC = False              # toggled at runtime: lit by the Light Volumes, not the lightmap


def build(coll):
    with bpy.data.libraries.load(os.path.abspath(BLEND), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in PLACES]
    out = []
    dg = None
    for ob in dst.objects:
        if ob is None:
            continue
        coll.objects.link(ob)
        x, y, heading = PLACES[ob.name]
        # heading 0 = length along plan +X, so turn the model's +Y onto it
        ob.matrix_world = Matrix.Translation((x * IN, y * IN, 0.0)) @ Matrix.Rotation(math.radians(heading - 90.0), 4, "Z")
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        ratio = min(1.0, TRI_BUDGET[ob.name] / max(tris, 1))
        if ratio < 1.0:
            d = ob.modifiers.new("decimate", "DECIMATE")
            d.ratio = ratio
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        me.transform(ob.matrix_world)
        ob.modifiers.clear()
        ob.data = me
        ob.matrix_world = Matrix()
        me.name = ob.name
        out.append(ob)
    return out


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        common.collapse_materials(ob, {r: mat for r in REGIONS})
        for p in ob.data.polygons:
            p.use_smooth = True
