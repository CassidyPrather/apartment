"""Build the filing cabinet set (cabinet + router + modem + VR headset + cable stubs),
render the verification views, and export one FBX per item to Assets/Apartment/Models/.

Through the Blender MCP:
    exec(open(r"<repo>/blender/lib/build_filing_cabinet_set.py").read())
Headless:
    blender -b -P blender/lib/build_filing_cabinet_set.py -- [--no-render] [--no-export]

Set STEPS (a global, or the CLI flags) to limit what runs while iterating.
"""

import importlib
import math
import os
import sys

import bpy

LIB = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else \
    os.path.join(os.path.dirname(bpy.data.filepath or ""), "")
if not os.path.exists(os.path.join(LIB, "common.py")):
    LIB = r"C:\Source\apartment\blender\lib"
if LIB not in sys.path:
    sys.path.insert(0, LIB)

import atlas_layout  # noqa: E402
import common  # noqa: E402
import dimensions  # noqa: E402

for mod in (atlas_layout, common, dimensions):   # layout first: common imports from it
    importlib.reload(mod)

import filing_cabinet  # noqa: E402

importlib.reload(filing_cabinet)

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
STEPS = globals().get("STEPS") or {
    "render": "--no-render" not in ARGS,
    "export": "--no-export" not in ARGS,
    "items": ["cabinet", "router", "modem", "vr_headset", "cables"],
}

H = dimensions.CABINET["height"]


def place(ob, key):
    x, y, rot = dimensions.PLACEMENT[key]
    ob.location = (x, y, H)
    ob.rotation_euler = (0, 0, math.radians(rot))


def main():
    common.reset_scene()
    coll = common.collection("filing_cabinet_set")
    items = {}
    if "cabinet" in STEPS["items"]:
        body, drawers, guards = filing_cabinet.build(coll)
        filing_cabinet.texture(body, drawers, guards)
        markers = [o for o in coll.objects if o.type == "EMPTY"]
        items["filing_cabinet"] = [body] + drawers + guards + markers
    for key, modname in (("router", "router"), ("modem", "modem"),
                         ("vr_headset", "vr_headset"), ("cables", "cable_stubs")):
        if key not in STEPS["items"]:
            continue
        mod = importlib.import_module(modname)
        importlib.reload(mod)
        obs = mod.build(coll)
        mod.texture(obs)
        if key in dimensions.PLACEMENT:
            place(obs[0], key)
        items[modname] = obs
    all_obs = [o for obs in items.values() for o in obs]
    for ob in all_obs:
        if ob.type == "MESH":
            common.shade_flat_with_sharp(ob)
            common.lightmap_uvs(ob)
    report = {o.name: common.tri_count(o) for o in all_obs if o.type == "MESH"}
    print("triangles:", report, "total", sum(report.values()))
    if STEPS["render"]:
        import verify
        importlib.reload(verify)
        verify.render_all(all_obs)
    if STEPS["export"]:
        for name, obs in items.items():
            export_item(name, obs)
    return items


def export_item(name, obs):
    """Export at the item's own origin: temporarily clear the placement transform."""
    root = obs[0]
    saved = (root.location.copy(), root.rotation_euler.copy())
    if name != "filing_cabinet":
        root.location = (0, 0, 0)
        root.rotation_euler = (0, 0, 0)
    common.export_fbx(obs, os.path.join(common.MODELS, name + ".fbx"))
    root.location, root.rotation_euler = saved


if __name__ == "__main__" or "STEPS" in globals():
    RESULT = main()
