"""Living room wall art: the small framed picture between the west windows, the canvas above
the bedroom door, a poster beside the bedroom door and a framed certificate above the next
door north, all on the living-room walls.

Source of truth: scripted, positions from the living-room LiDAR survey (Reference/living_survey).
Frame: PLAN coordinates. Origin = plan (0, 0, 0), +X east, +Y north, Z up, metres; the package
goes on a marker at (0, 0, 0) with no rotation. u = plan coordinate along the wall, d = distance
out from the wall surface into the room.

Dimensions (inches, plan), all measured on capture frames rectified onto the wall plane
(Reference/bedroom_fixtures_work/rect.py + final.py), +-0.5                           SCAN
  west wall x 0: framed picture y 80.3..90.1, z 58.1..64.7, black frame 0.6, 0.8 deep
      (the survey inventory had y ~83..95 x 9 tall; the rectified frames agree on these)
  center wall west face x 134:
    poster y 100.73..117.4, z 54.67..65.5 (paper)
    canvas y 127.47..146.13, z 87..96.67, 1.5 deep (gallery wrap)
    certificate frame y 155.3..175.8, z 86.3..104.5, cherry frame 2.0, 1.0 deep     frame widths EST

Textures: the picture and the canvas are the real images, rectified from the capture
photos. The poster is a street-level map of a real town and the certificate carries a name,
so both are neutral stand-ins (privacy).
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
    # poster beside the bedroom door (stand-in)
    panel(b, "map_standin", "center_w", (100.73, 117.4), (0.0, 0.06), (54.67, 65.5), "paper", True)
    # gallery-wrap canvas above the bedroom door
    panel(b, "canvas", "center_w", (127.47, 146.13), (0.0, 1.5), (87.0, 96.67), "canvas_side", True)
    # framed certificate (blank stand-in)
    u0, u1, z0, z1, fw = 155.3, 175.8, 86.3, 104.5, 2.0
    panel(b, "frame_cherry", "center_w", (u0, u1), (0.0, 1.0), (z0, z1))
    panel(b, "mat_black", "center_w", (u0 + fw, u1 - fw), (0.6, 1.02), (z0 + fw, z1 - fw))
    panel(b, "diploma_sheet", "center_w", (u0 + 7.0, u1 - 3.0), (1.02, 1.05), (z0 + 3.5, z1 - 3.5),
          "diploma_sheet", True)
    panel(b, "tassel", "center_w", (u0 + 3.2, u0 + 4.8), (1.02, 1.4), (z0 + 3.5, z1 - 3.5))
    return [b.to_object(NAME, coll)]


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=dict(PLANAR))
        common.collapse_materials(ob, {r: mat for r in REGIONS})
