"""Cassidy's own artwork, hung as a small gallery group on the bedroom side of the center wall:
  cat      acrylic on canvas, a black cat with hand-lettered text (the lettering is part of it)
  abstract acrylic on canvas, teal/red/gold swirls, painted edges
  rabbit   two-colour linocut (teal rabbit, red geometric outline, carrot), black frame, white mat
  cape     gouache of Cape Disappointment, waves breaking on dark rocks under a pale sky;
           landscape, thin black frame, grey mat (it lay sideways in its photo)
  isopod   black-ink linocut of an isopod, small deep black frame
Textures are the pieces themselves, rectified from Cassidy's photos (see layout.py/textures.py);
the signatures stay as they are (Cassidy asked that artists' signatures not be blurred).

Source of truth: Cassidy's seven photos Reference/PXL_20260925_173348922 .. 173438122 (the five
laid on a bed; one with a hand beside them, one overhead). Placement from the shell layout and
the bedroom LiDAR survey (Reference/bedroom_survey/registered.npz): the wall is bare there.
Frame: PLAN coordinates. Origin = plan (0, 0, 0), +X east, +Y north, Z up, metres; the package
goes on a marker at (0, 0, 0) with no rotation. u = plan y along the wall, d = distance out from
the wall surface (x 138.75, the center wall's east face) into the bedroom. Everything faces +X.

How the sizes were measured (Reference/own_art_work/*.py):
  1. Corners of every frame, mat window and canvas face in the overhead photo (173356899),
     snapped to edges (refine.py), back-projected onto the bed plane with a pinhole camera
     (closeup.py/sizes.py). The overhead view is nearly square-on, so the relative sizes and
     aspect ratios barely move with the assumed focal length (2400-3300 px: < 1 %).
  2. Absolute scale: the hand in 173348922 (knuckle breadth = 0.345 x the rabbit mat window's
     long side, both on the same bed row) and standard sizes agree on one scale: cat canvas
     14 x 14 -> hand breadth 3.0 in (a typical adult hand is 3.1-3.5), abstract 10.8 x 14.5
     (-> the standard 11 x 14 canvas), cape frame opening 11.5 x 7.9 (an A4 frame shows
     ~8.0 x 11.4), isopod window 3.75 x 6.1 (a 4 x 6 frame shows 3.75 x 5.75). The other
     candidate scales (cat 12 in or 16 in) put the hand at 2.6 or 3.4 in and break two or
     three of those fits. The letter-paper case is on the floor behind the bed, off the bed
     plane, so it only confirms the order of magnitude.
  3. The rabbit close-up (173425104) measured square-on gives the same frame and mat
     proportions as the overhead shot to 1 % (outer h/w 1.19 vs 1.18, window 1.30 vs 1.31).

Dimensions (inches, W x H as hung):                                      provenance
  cat canvas 14.0 x 14.0 (measured 13.8 x 14.2), 0.5 deep, edges painted near-black
                                                        PHOTO scale anchor / EST depth
  abstract canvas 11.0 x 14.0 (measured 10.8 x 14.5), 0.75 deep, edges painted teal
                                                        PHOTO + standard size / EST depth
  canvas depths: side bands in 173348922 are 42 px (cat) and 50 px (abstract) against
    105 and 90 px/in along the edge -> about 0.5 and 0.75 in at that viewing angle   EST
  rabbit frame 11.0 x 13.0 outer, moulding 0.68, 0.9 deep (a 10 x 12 frame); inside 9.64 x
    11.64; mat window 6.58 x 8.66, borders 1.54 L / 1.51 R / 1.51 T / 1.47 B            PHOTO
  cape frame 12.6 x 9.0 outer (landscape), moulding 0.55, 0.7 deep; inside 11.5 x 7.9 (grey mat
    and the paper, which sits a little low, all in the texture)                         PHOTO/EST depth
  isopod frame 8.2 x 5.6 outer (landscape; the edition number reads upright that way),
    moulding 1.05 sides / 0.93 top-bottom, 0.9 deep; window 6.1 x 3.75                   PHOTO/EST depth
  picture planes sit 0.36 behind the frame face; the rabbit mat is 0.06 thick on top    EST

Placement (plan inches): bedroom side of the center wall, east face x 138.75, in the bare
stretch between the desk (its west end fills y 0..29, top 30, PC tower to z 50) and the filing
cabinet set (y 66..81.5, with the framed print above it at y 67.25..82.25, z 53.5..71). The
tracking base station's cable runs down the wall at y 26, the bedroom door is at y 119.5.
The bedroom survey (registered.npz splat + LiDAR, elevation of this wall) shows nothing on the
wall there between z 38 and the ceiling, and the floor in front is the walkway between desk and
cabinet. The group is y 33..60, z 41.7..74.3, centred at z 58 (eye height); 7 in from the
cable, 7.25 in from the existing print. Two columns, as seen from the bed (left = south):
  cape over cat over isopod | rabbit over abstract.
(The dining-side spot first used is the dining closet door, y 164..194.)
"""

import os
import sys

from mathutils import Vector

import common
from atlas_layout import uv_rect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout  # noqa: E402


def m(inches):
    return inches * 0.0254


NAME = "own_art"
ATLAS = layout.ATLAS
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("gallery", 90, 4, 1.0), ("gallery_left", 55, 12, 1.0), ("gallery_right", 125, 12, 1.0),
         ("edge_close", 70, 0, 0.45)]

WALL_X = 138.75         # center wall, east (bedroom) face (bedroom survey)
GAP = 2.0

# (u0, u1, z0, z1) as hung
# left column (south, centre y 40): cape 12.6 x 9 over cat 14 x 14 over isopod 8.2 x 5.6
CAPE = (33.7, 46.3, 65.3, 74.3)
CAT = (33.0, 47.0, 49.3, 63.3)
ISOPOD = (35.9, 44.1, 41.7, 47.3)
# right column (north, centre y 54.5): rabbit 11 x 13 over abstract 11 x 14, same top line
RABBIT = (49.0, 60.0, 61.3, 74.3)
ABSTRACT = (49.0, 60.0, 45.3, 59.3)

PLANAR = {}
PERFACE = {}     # region -> True: each face gets the whole region, long side along u


def plan_box(u, d, z):
    """(u0,u1),(d0,d1),(z0,z1) on the wall -> plan lo/hi in metres (d grows toward +X)."""
    x0, x1 = sorted((WALL_X + d[0], WALL_X + d[1]))
    return (m(x0), m(u[0]), m(z[0])), (m(x1), m(u[1]), m(z[1]))


def panel(b, region, u, d, z, side_region=None, back_region=None):
    """Wall box; with side_region only the room-facing face keeps `region`."""
    lo, hi = plan_box(u, d, z)
    faces = b.box(region, lo, hi)
    for f in faces:
        f.normal_update()
        n = f.normal
        if n.x > 0.9:
            continue
        if n.x < -0.9 and back_region:
            f.material_index = b.idx(back_region)
        elif side_region:
            f.material_index = b.idx(side_region)
    return faces


def picture_bounds(region, u0, u1, z0, z1):
    """Planar map of the room-facing faces: image left = south (-y) for a viewer facing west."""
    PLANAR[region] = ("+X", (m(u0), m(u1)), (m(z0), m(z1)))


def framed(b, region, box, fw_u, fw_z, depth, mat_window=None):
    u0, u1, z0, z1 = box
    # moulding: four bars, full depth
    panel(b, "frame_black", (u0, u0 + fw_u), (0.0, depth), (z0, z1))
    panel(b, "frame_black", (u1 - fw_u, u1), (0.0, depth), (z0, z1))
    panel(b, "frame_black", (u0 + fw_u, u1 - fw_u), (0.0, depth), (z1 - fw_z, z1))
    panel(b, "frame_black", (u0 + fw_u, u1 - fw_u), (0.0, depth), (z0, z0 + fw_z))
    iu0, iu1, iz0, iz1 = u0 + fw_u, u1 - fw_u, z0 + fw_z, z1 - fw_z
    back = depth - 0.36
    # glass-less picture plane: the photo of everything inside the frame
    panel(b, region, (iu0, iu1), (back - 0.05, back), (iz0, iz1), "frame_black")
    picture_bounds(region, iu0, iu1, iz0, iz1)
    if mat_window:
        # mat plate with a window, textured by the same projection (its bevel is plain white)
        wl, wr, wt, wb = mat_window          # borders: left(south), right(north), top, bottom
        d = (back, back + 0.06)
        panel(b, region, (iu0, iu0 + wl), d, (iz0, iz1), "mat_white")
        panel(b, region, (iu1 - wr, iu1), d, (iz0, iz1), "mat_white")
        panel(b, region, (iu0 + wl, iu1 - wr), d, (iz1 - wt, iz1), "mat_white")
        panel(b, region, (iu0 + wl, iu1 - wr), d, (iz0, iz0 + wb), "mat_white")


def canvas(b, region, box, depth, side_region):
    u0, u1, z0, z1 = box
    panel(b, region, (u0, u1), (0.0, depth), (z0, z1), side_region, "canvas_back")
    picture_bounds(region, u0, u1, z0, z1)
    if side_region == "abstract_side":
        PERFACE[side_region] = True


def build(coll):
    PLANAR.clear()
    PERFACE.clear()
    b = common.Builder(REGIONS)
    canvas(b, "cat", CAT, 0.5, "cat_side")
    canvas(b, "abstract", ABSTRACT, 0.75, "abstract_side")
    # rabbit mat window, measured in the rectified close-up: left 0.160, right 0.843 (of the
    # 9.64 width, image left = south), top 0.130, bottom 0.874 (of the 11.64 height)
    framed(b, "rabbit", RABBIT, 0.68, 0.68, 0.9,
           mat_window=(0.160 * 9.64, (1 - 0.843) * 9.64, 0.130 * 11.64, (1 - 0.874) * 11.64))
    framed(b, "cape", CAPE, 0.55, 0.55, 0.7)
    framed(b, "isopod", ISOPOD, 1.05, 0.93, 0.9)
    return [b.to_object(NAME, coll)]


def _perface_uvs(ob):
    """Painted canvas edges: each side face shows the whole photographed edge strip, the
    strip's top (the edge next to the picture face) toward the room."""
    me = ob.data
    uvl = me.uv_layers["UVMap"]
    for region in PERFACE:
        idx = REGIONS.index(region)
        u0, v0, u1, v1 = uv_rect(ATLAS, region)
        for p in me.polygons:
            if p.material_index != idx:
                continue
            cos = [me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices]
            n = p.normal
            # top/bottom edges (normal +-Z) run along y, north/south edges (+-Y) along z;
            # the other in-face axis is always the depth, x
            along = 1 if abs(n.z) > 0.5 else 2
            lo_a, hi_a = min(c[along] for c in cos), max(c[along] for c in cos)
            lo_x, hi_x = min(c.x for c in cos), max(c.x for c in cos)
            for li, c in zip(p.loop_indices, cos):
                fa = (c[along] - lo_a) / max(hi_a - lo_a, 1e-6)
                fd = (c.x - lo_x) / max(hi_x - lo_x, 1e-6)    # 1 at the room side (large x)
                uvl.data[li].uv = (u0 + fa * (u1 - u0), v0 + fd * (v1 - v0))


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=dict(PLANAR))
        _perface_uvs(ob)
        common.collapse_materials(ob, {r: mat for r in REGIONS})
