"""Build the apartment shell, render its verification views, and export
Assets/Apartment/Models/apartment_shell.fbx.

Through the Blender MCP:
    exec(open(r"<repo>/blender/lib/build_shell.py").read())   # with __file__ set
Set STEPS = {"render": bool, "export": bool} to limit what runs.
"""

import importlib
import os
import sys

import bpy

LIB = os.path.dirname(os.path.abspath(__file__))
if LIB not in sys.path:
    sys.path.insert(0, LIB)

import atlas_layout  # noqa: E402
import common  # noqa: E402
import shell_layout  # noqa: E402

for mod in (atlas_layout, common, shell_layout):
    importlib.reload(mod)
import shell  # noqa: E402

importlib.reload(shell)

STEPS = globals().get("STEPS") or {"render": True, "export": True}


def main():
    common.reset_scene()
    coll = common.collection("apartment_shell")
    obs = shell.build(coll)
    shell.texture(obs)
    meshes = [o for o in obs if o.type == "MESH"]
    for ob in meshes:
        common.shade_flat_with_sharp(ob)
        common.lightmap_uvs(ob)
    tris = {o.name: common.tri_count(o) for o in meshes}
    print("shell triangles:", sum(tris.values()), "objects:", len(obs))
    if STEPS["export"]:
        common.export_fbx(obs, os.path.join(common.MODELS, "apartment_shell.fbx"))
    return obs


RESULT = main()
