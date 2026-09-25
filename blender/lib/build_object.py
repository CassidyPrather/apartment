"""Build one object package: blender/lib/objects/<name>/object.py.

Headless (the normal way; several can run at once):
    blender -b --factory-startup -P blender/lib/build_object.py -- <name> [--no-render] [--no-export]
Through the Blender MCP (to look at it live): exec this file with
    {"__file__": <path>, "__name__": "build", "ARGS": ["<name>", "--no-export"]}

Steps: build + texture the object at its own origin, smooth-by-angle shading, lightmap
UVs, a turntable contact sheet in blender/out/<name>/, the FBX in
Assets/Apartment/Models/<name>.fbx, and objects/<name>/manifest.json for Unity's
Apartment > Import Objects.

Object package contract (object.py):
    NAME       str, lowercase snake_case, no brands
    ATLAS      {"name": NAME, "size": 512|1024, "regions": {region: (x, y, w, h)}}
    MATERIALS  {blender_material_name: {"atlas": atlas name, "mode": "opaque"|"transparent",
                "alpha": 0-1 (transparent only), "tiled": bool}}
    COLLIDER   "box" | "mesh" | "none"
    STATIC     bool (False for anything that moves)
    build(coll) -> [objects]   (first object is the root; origin on the resting surface)
    texture(objs)
and optionally VIEWS = [(name, azimuth, elevation, distance_scale)] for extra renders.
"""

import importlib.util
import json
import math
import os
import sys

import bpy

LIB = os.path.dirname(os.path.abspath(__file__))
if LIB not in sys.path:
    sys.path.insert(0, LIB)

import atlas_layout  # noqa: E402
import common  # noqa: E402

for mod in (atlas_layout, common):
    importlib.reload(mod)

ARGS = globals().get("ARGS") or (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
NAME = ARGS[0]
RENDER = "--no-render" not in ARGS
EXPORT = "--no-export" not in ARGS
PKG = os.path.join(LIB, "objects", NAME)


def load_package():
    spec = importlib.util.spec_from_file_location(f"objects.{NAME}", os.path.join(PKG, "object.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, PKG)
    spec.loader.exec_module(mod)
    return mod


def bounds(objs):
    pts = [ob.matrix_world @ v.co for ob in objs if ob.type == "MESH" for v in ob.data.vertices]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return lo, hi


def render_sheet(obj, objs):
    out = os.path.join(common.OUT, NAME)
    lo, hi = bounds(objs)
    centre = [(a + b) / 2 for a, b in zip(lo, hi)]
    radius = max(hi[i] - lo[i] for i in range(3)) * 1.6 + 0.2
    common.render_setup(res=(600, 600))
    common.stage()
    views = [("front", 0, 12, 1.0), ("front_right", 45, 25, 1.0), ("right", 90, 12, 1.0),
             ("back_right", 135, 25, 1.0), ("back", 180, 12, 1.0), ("back_left", 225, 25, 1.0),
             ("left", 270, 12, 1.0), ("front_left", 315, 25, 1.0), ("top", 0, 85, 1.0)]
    views += list(getattr(obj, "VIEWS", []))
    cams = common.camera_views(centre, radius, views, lens=50)
    import verify
    lit = common.render_views(cams, out, "lit")
    verify._sheet(lit, os.path.join(out, "sheet_lit.png"), cols=3)
    checker = common.checker_material()
    meshes = [o for o in objs if o.type == "MESH"]
    chk = common.with_material_override(meshes, checker, lambda: common.render_views(cams, out, "checker"))
    verify._sheet(chk, os.path.join(out, "sheet_checker.png"), cols=3)
    print("sheets in", os.path.relpath(out, common.ROOT))


def write_manifest(obj, objs):
    lo, hi = bounds(objs)
    man = {
        "name": NAME,
        "fbx": f"Assets/Apartment/Models/{NAME}.fbx",
        "materials": obj.MATERIALS,
        "collider": getattr(obj, "COLLIDER", "box"),
        "static": getattr(obj, "STATIC", True),
        "triangles": sum(common.tri_count(o) for o in objs if o.type == "MESH"),
        "bounds_m": {"min": [round(v, 4) for v in lo], "max": [round(v, 4) for v in hi]},
    }
    with open(os.path.join(PKG, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2)
    print("manifest", json.dumps(man))


def main():
    obj = load_package()
    common.reset_scene()
    coll = common.collection(NAME)
    objs = obj.build(coll)
    obj.texture(objs)
    for ob in objs:
        if ob.type == "MESH":
            common.shade_flat_with_sharp(ob)
            common.lightmap_uvs(ob)
    print("triangles:", {o.name: common.tri_count(o) for o in objs if o.type == "MESH"})
    if RENDER:
        render_sheet(obj, objs)
    if EXPORT:
        common.export_fbx(objs, os.path.join(common.MODELS, NAME + ".fbx"))
        write_manifest(obj, objs)
    return objs


RESULT = main()
