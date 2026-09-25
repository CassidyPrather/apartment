"""Living room wall art: the small framed picture between the west windows, the canvas above
the bedroom door, the city-map poster beside the bedroom door and a framed diploma further
north, all on the living-room walls.

Source of truth: scripted, positions from the living-room LiDAR survey (Reference/living_survey).
Frame: PLAN coordinates. Origin = plan (0, 0, 0), +X east, +Y north, Z up, metres; the package
goes on a marker at (0, 0, 0) with no rotation. u = plan coordinate along the wall, d = distance
out from the wall surface into the room.

Dimensions (inches, plan), measured on capture frames rectified onto the wall plane
(Reference/bedroom_fixtures_work/rect.py + final.py), +-0.5                           SCAN
  west wall x 0: framed picture y 80.3..90.1, z 58.1..64.7, black frame 0.6, 0.8 deep
  center wall west face x 134:
    poster: unframed 17 x 11 tabloid paper                                             SPEC
      the capture gives 16.7..16.8 x 10.8, centre y 109.07, z 60.08 (re-measured on a
      30 px/in rectification of the best frame, Reference/living_wall_art_work/rect2);
      the close-up photo's aspect is 1.54 = 17/11. Placed at y 98.8..115.8, z 54.58..65.58:
      1.77 south of the capture centre so it clears the modelled bedroom door casing (3 wide,
      starts at y 116.5); the real casing edge measures y 118.8 on the capture
    canvas y 127.47..146.13, z 87..96.67, 1.5 deep (gallery wrap)
    diploma frame y 155.3..175.8, z 86.3..104.5, cherry, 1.0 deep                   SCAN
      inside it, as fractions of the frame measured on two capture frames:
      moulding 1.75 wide                                                              EST
      sheet window y 161.2..172.9, z 90.1..100.0 (11.7 x 9.9)                        SCAN +-0.4
      medallion centre y 166.9, z 101.3, 2.3 dia                                     SCAN
      gold lettering y 163.0..171.6, z 88.6..89.8                                    SCAN
      tassel tube y 158.8..160.5, z 89.5..101.6, 0.4 deep                            SCAN / EST depth

Textures: the picture, the canvas and the map poster are the real images (the poster is a
fictional city from a 1985 text game, rectified from Cassidy's close-up photo IMG_1505). The
diploma is painted from scratch for a made-up school; the graduate line reads "Cassidy Company"
(Cassidy's request).
"""

from mathutils import Vector

import common
import layout  # noqa: E402  (package dir is on sys.path during builds)


def m(inches):
    return inches * 0.0254


NAME = "living_wall_art"
ATLAS = layout.ATLAS
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("west_wall", 270, 8, 0.5), ("center_wall", 90, 8, 0.5)]

# wall: (axis index of the normal, surface coordinate, outward sign, planar axis name)
WALLS = {"west": (0, 0.0, +1, "+X"), "center_w": (0, 134.0, -1, "-X")}
PLANAR = {}


def plan_box(wall, u, d, z):
    ax, s0, sign, _ = WALLS[wall]
    dd = sorted((s0 + sign * d[0], s0 + sign * d[1]))
    if ax == 0:
        lo, hi = (dd[0], u[0], z[0]), (dd[1], u[1], z[1])
    else:
        lo, hi = (u[0], dd[0], z[0]), (u[1], dd[1], z[1])
    return tuple(map(m, lo)), tuple(map(m, hi))


def panel(b, region, wall, u, d, z, side_region=None, planar=False):
    lo, hi = plan_box(wall, u, d, z)
    faces = b.box(region, lo, hi)
    ax, _, sign, axis = WALLS[wall]
    if side_region:
        n = Vector((0, 0, 0))
        n[ax] = sign
        for f in faces:
            f.normal_update()
            if f.normal.dot(n) < 0.9:
                f.material_index = b.idx(side_region)
    if planar:
        ub = (m(u[0]), m(u[1])) if axis in ("+X", "-Y") else (-m(u[1]), -m(u[0]))
        PLANAR[region] = (axis, ub, (m(z[0]), m(z[1])))
    return faces


def build(coll):
    PLANAR.clear()
    b = common.Builder(REGIONS)
    # framed picture between the west windows
    u0, u1, z0, z1, fw = 80.3, 90.1, 58.1, 64.7, 0.6
    panel(b, "frame_black", "west", (u0, u1), (0.0, 0.8), (z0, z1))
    panel(b, "pic_west", "west", (u0 + fw, u1 - fw), (0.6, 0.83), (z0 + fw, z1 - fw), "frame_black", True)
    # city-map poster beside the bedroom door (unframed 17 x 11 paper)
    panel(b, "map", "center_w", (98.8, 115.8), (0.0, 0.06), (54.58, 65.58), "paper", True)
    # gallery-wrap canvas above the bedroom door
    panel(b, "canvas", "center_w", (127.47, 146.13), (0.0, 1.5), (87.0, 96.67), "canvas_side", True)
    # framed diploma: cherry moulding, black mat, sheet, medallion, gold lettering, tassel tube
    u0, u1, z0, z1, fw = 155.3, 175.8, 86.3, 104.5, 1.75
    panel(b, "frame_cherry", "center_w", (u0, u1), (0.0, 1.0), (z0, z1))
    panel(b, "mat_black", "center_w", (u0 + fw, u1 - fw), (0.6, 1.02), (z0 + fw, z1 - fw))
    panel(b, "diploma_sheet", "center_w", (161.2, 172.9), (1.02, 1.05), (90.1, 100.0), "paper", True)
    panel(b, "dip_seal", "center_w", (165.75, 168.05), (1.02, 1.05), (100.15, 102.45), "mat_black", True)
    panel(b, "dip_plate", "center_w", (163.0, 171.6), (1.02, 1.04), (88.6, 89.8), "mat_black", True)
    panel(b, "tassel", "center_w", (158.8, 160.5), (1.02, 1.42), (89.5, 101.6), "tassel_side", True)
    return [b.to_object(NAME, coll)]


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=dict(PLANAR))
        common.collapse_materials(ob, {r: mat for r in REGIONS})
