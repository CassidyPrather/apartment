"""Wall TV: ~55 in flat panel on a flat wall mount, black bezel and back, plus a
separate screen quad for a video player.

Source of truth: scripted from the living-room LiDAR survey (panel y 47.5-96.5,
z 40-68, front face ~3 in off the wall) and the survey crops (thin black bezel, slightly
thicker bottom bezel with a small standby light, no visible logo).

Origin: the bottom-centre of the BACK face (the wall side). Local frame: X along the
width, the wall plane is y = 0 and the front faces -Y (so the whole TV is at y -3..0),
bottom edge at z = 0, top at z = 27.5. Place at plan (134, 72.5), Z 39.5, rotation -90:
the back sits on the center wall face and the panel faces west.

Objects:
  wall_tv          bezel, back and mount (material wall_tv, atlas)
  wall_tv_screen   one quad over the visible panel, front facing -Y, UVs 0..1
                   (u left to right, v bottom to top as seen from the front), its own
                   material slot wall_tv_screen (opaque, near-black texture)
"""

import bmesh
import bpy

import common

IN = 0.0254


def m(v):
    return v * IN


W = 49.0            # SCAN y 47.5-96.5
H = 27.5            # SCAN z 40-68 (LiDAR), coordinator bottom Z 39.5
D = 3.0             # SCAN front face at x ~131.8, wall ~134.5-135
PANEL_T = 0.45      # EST panel edge thickness
BEZEL = 0.35        # EST side/top bezel (photo)
BEZEL_BOT = 0.6     # EST bottom bezel (photo: slightly thicker, standby light)
HUMP = (38.0, 1.3, 20.0)   # EST back electronics hump w, d, h
MOUNT = (16.0, 20.0)       # EST flat mount plate w, h
SCREEN_OFF = 0.02   # screen quad in front of the panel face

NAME = "wall_tv"
ATLAS = {
    "name": "wall_tv",
    "size": 256,
    "regions": {
        "bezel": (0, 0, 128, 128),
        "back": (128, 0, 128, 128),
        "mount": (0, 128, 128, 128),
        "led": (128, 128, 64, 64),
        "panel_edge": (192, 128, 64, 64),
    },
}
SCREEN_ATLAS = {"name": "wall_tv_screen", "size": 256, "regions": {"screen": (0, 0, 256, 256)}}
REGIONS = list(ATLAS["regions"])
MATERIALS = {
    "wall_tv": {"atlas": "wall_tv", "mode": "opaque", "tiled": False},
    "wall_tv_screen": {"atlas": "wall_tv_screen", "mode": "opaque", "tiled": False},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_left", 330, 10, 0.9)]

# screen (visible panel) rectangle in local inches
SX0, SX1 = -W / 2 + BEZEL, W / 2 - BEZEL
SZ0, SZ1 = BEZEL_BOT, H - BEZEL


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev))
    yf = -D                                              # front face of the panel
    # panel slab (bezel frame is its front face around the screen)
    bx("bezel", (-W / 2, yf, 0.0), (W / 2, yf + PANEL_T, H), 0.08)
    # back hump, mount plate and wall plate
    hw, hd, hh = HUMP
    zc = H / 2 + 1.0
    bx("back", (-hw / 2, yf + PANEL_T, zc - hh / 2), (hw / 2, yf + PANEL_T + hd, zc + hh / 2), 0.3)
    mw, mh = MOUNT
    bx("mount", (-mw / 2, yf + PANEL_T + hd, zc - mh / 2), (mw / 2, -0.3, zc + mh / 2))
    bx("mount", (-mw / 2 - 1.0, -0.3, zc - mh / 2 + 2), (mw / 2 + 1.0, 0.0, zc + mh / 2 - 2))
    # standby light under the bottom bezel, centre
    bx("led", (-0.25, yf - 0.05, 0.1), (0.25, yf + 0.1, 0.3))
    ob = b.to_object(NAME, coll)

    # the screen quad: its own mesh and material slot, 0..1 UVs
    me = bpy.data.meshes.new(NAME + "_screen")
    bm = bmesh.new()
    y = m(yf - SCREEN_OFF)
    vs = [bm.verts.new((m(SX0), y, m(SZ0))), bm.verts.new((m(SX1), y, m(SZ0))),
          bm.verts.new((m(SX1), y, m(SZ1))), bm.verts.new((m(SX0), y, m(SZ1)))]
    f = bm.faces.new(vs)          # CCW seen from -Y: normal points -Y
    bm.normal_update()
    assert f.normal.y < -0.99, f.normal
    uv = bm.loops.layers.uv.new("UVMap")
    for loop, (u, v) in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop[uv].uv = (u, v)
    bm.to_mesh(me)
    bm.free()
    scr = bpy.data.objects.new(NAME + "_screen", me)
    (coll or bpy.context.scene.collection).objects.link(scr)
    return [ob, scr]


def texture(objs):
    ob, scr = objs
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
    smat = common.atlas_material("wall_tv_screen", SCREEN_ATLAS)
    scr.data.materials.clear()
    scr.data.materials.append(smat)
