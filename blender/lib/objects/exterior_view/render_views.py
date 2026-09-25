"""Verification renders for window_units + exterior_view: builds a throwaway copy of the
shell (shell.build, unchanged), both packages, a sun, and cameras at standing eye height
looking out of each window and the patio door, plus an aerial overview. Output goes to
Reference/exterior_work/ (local-only scratch).

    blender -b --factory-startup -P blender/lib/objects/exterior_view/render_views.py
"""

import importlib.util
import math
import os
import sys

import bpy
from mathutils import Vector

LIB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, LIB)
import common  # noqa: E402
import shell  # noqa: E402
import shell_layout as L  # noqa: E402
import verify  # noqa: E402

OUT = os.path.join(common.ROOT, "Reference", "exterior_work")
m = L.m
EYE = 63.0


def load(name):
    pkg = os.path.join(LIB, "objects", name)
    spec = importlib.util.spec_from_file_location(f"objects.{name}", os.path.join(pkg, "object.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def camera(name, pos, target, lens=22):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.05
    cd.clip_end = 300
    ob = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(ob)
    p = Vector(tuple(m(v) for v in pos))
    t = Vector(tuple(m(v) for v in target))
    ob.location = p
    ob.rotation_euler = (t - p).to_track_quat("-Z", "Y").to_euler()
    return ob


def main():
    common.reset_scene()
    sc = common.collection("shell_preview")
    sobs = shell.build(sc)
    shell.texture(sobs)
    for ob in sobs:
        if ob.name == "shell_glass":
            ob.hide_render = True
    for name in ("window_units", "exterior_view"):
        mod = load(name)
        objs = mod.build(common.collection(name))
        mod.texture(objs)
    scn = bpy.context.scene
    common.render_setup(res=(960, 640))
    next(n for n in scn.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (0.55, 0.68, 0.85, 1)
    next(n for n in scn.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Strength"].default_value = 0.9
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.5
    sun.angle = math.radians(3)
    so = bpy.data.objects.new("sun", sun)
    so.rotation_euler = (math.radians(50), 0, math.radians(-130))   # from the south-west
    scn.collection.objects.link(so)
    # A soft room fill so the interior side of the frames reads.
    for x, y in ((70, 90), (205, 80)):
        ld = bpy.data.lights.new("fill", "AREA")
        ld.energy = 120
        ld.size = 1.5
        lo = bpy.data.objects.new("fill", ld)
        lo.location = (m(x), m(y), m(L.CEILING - 4))
        scn.collection.objects.link(lo)
    cams = [
        camera("west_window_south", (80, 60, EYE), (-6, 59.9, 52)),
        camera("west_window_north", (80, 119, EYE), (-6, 119.1, 52)),
        camera("south_window_living", (73.5, 90, EYE), (73.5, -6, 52)),
        camera("south_window_bedroom", (188, 85, EYE), (188.3, -6, 52)),
        camera("patio_door", (238.75, 100, EYE), (238.75, -6, 42)),
        camera("living_overview", (125, 150, EYE), (10, 60, 50), lens=18),
        camera("aerial", (900, 900, 1400), (-150, -150, 0), lens=24),
    ]
    paths = common.render_views(cams, OUT, "view")
    verify._sheet(paths, os.path.join(OUT, "sheet_views.png"), cols=2)
    # Frame close-up from inside (details of the slider and blind).
    close = [camera("close_west_window", (30, 70, 58), (-4, 59, 52), lens=28),
             camera("close_bedroom_blind", (175, 30, 70), (190, -4, 72), lens=28)]
    cp = common.render_views(close, OUT, "view")
    verify._sheet(cp, os.path.join(OUT, "sheet_close.png"), cols=2)
    print("renders in", OUT)


main()
