"""Fixed verification cameras for the filing cabinet set, and contact sheets.

Views roughly match the reference photos so renders can be compared side by side:
  front_3q_left  ~ IMG_1492 (front-left, looking down)
  front_3q_right ~ IMG_1495 (front-right, looking down)
  right_side     ~ IMG_1493 (right side panel, router/modem fronts)
  back_left_high ~ IMG_1496
  top_down       ~ IMG_1497
  front / hardware_close / drawer_open for geometry checks.
Each set renders lit and with the UV checker; sheets land in blender/out/filing_cabinet/.
"""

import math
import os

import bpy
import numpy as np

import common
import dimensions

C = dimensions.CABINET
OUT = os.path.join(common.OUT, "filing_cabinet")

VIEWS = [
    ("front_3q_left", -28, 38, 1.0),
    ("front_3q_right", 30, 40, 1.0),
    ("right_side", 80, 30, 1.0),
    ("back_left_high", -140, 50, 1.0),
    ("top_down", 0, 80, 0.8),
    ("front", 0, 8, 1.0),
]
CLOSE = [("hardware_close", 12, 12, 1.0)]
TOP_CLOSE = [("top_items", 40, 35, 1.0), ("top_items_left", -60, 30, 1.0)]


def _sheet(paths, out_path, cols=3):
    """Tile rendered PNGs into one contact sheet using Blender's image API."""
    imgs = [bpy.data.images.load(p, check_existing=False) for p in paths]
    w, h = imgs[0].size
    rows = math.ceil(len(imgs) / cols)
    sheet = np.zeros((rows * h, cols * w, 4), np.float32)
    for i, im in enumerate(imgs):
        px = np.empty(w * h * 4, np.float32)
        im.pixels.foreach_get(px)
        r, c = divmod(i, cols)
        # Blender pixels start bottom-left; place row 0 at the top of the sheet.
        y0 = (rows - 1 - r) * h
        sheet[y0:y0 + h, c * w:(c + 1) * w] = px.reshape(h, w, 4)
        bpy.data.images.remove(im)
    out = bpy.data.images.new("contact_sheet", cols * w, rows * h, alpha=True)
    out.pixels.foreach_set(sheet.ravel())
    out.filepath_raw = out_path
    out.file_format = "PNG"
    out.save()
    bpy.data.images.remove(out)
    print("sheet", os.path.relpath(out_path, common.ROOT))


def render_all(objects, modes=("lit", "checker")):
    common.render_setup(res=(800, 800))
    common.stage(wall_y=C["depth"] / 2 + 0.03)
    wall = bpy.data.objects.get("stage_wall")
    target = (0, 0, C["height"] * 0.55)
    cams = common.camera_views(target, 2.0, VIEWS, lens=45)
    close = common.camera_views((0, -C["depth"] / 2, C["height"] - 0.12), 0.55, CLOSE, lens=50)
    topc = common.camera_views((0, 0.02, C["height"] + 0.06), 0.9, TOP_CLOSE, lens=50)
    checker = common.checker_material()
    meshes = [o for o in objects if o.type == "MESH"]
    sets = {}
    for mode in modes:
        def go(cam_list=cams + close + topc, mode=mode):
            # the back wall blocks the rear views; hide it for them
            paths = []
            for cam in cam_list:
                if wall:
                    wall.hide_render = cam.name.startswith("back")
                paths += common.render_views([cam], OUT, mode)
            return paths
        if mode == "checker":
            paths = common.with_material_override(meshes, checker, go)
        else:
            paths = go()
        sets[mode] = paths
        _sheet(paths, os.path.join(OUT, f"sheet_{mode}.png"), cols=3)
    # Drawer-open pass: top drawer pulled out to full travel.
    d1 = bpy.data.objects.get("filing_cabinet_drawer_1")
    if d1:
        y = d1.location.y
        d1.location.y = y - C["drawer_travel"]
        dcams = common.camera_views((0, -C["depth"] / 2 - 0.2, C["height"] * 0.7), 1.6,
                                    [("drawer_open", -35, 40, 1.0)], lens=45)
        if wall:
            wall.hide_render = False
        common.render_views(dcams, OUT, "lit")
        d1.location.y = y
    return sets
