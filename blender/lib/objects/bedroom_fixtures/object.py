"""Bedroom fixtures: the small wall/ceiling things of the bedroom, all in one package.
  - vertical vane blinds in the bedroom's south window
  - two tracking base stations on swivel wall brackets (cable run down the wall)
  - ceiling smoke detector, thermostat on the center wall
  - all the wall art, textured from rectified capture photos (the photo strip stays abstract)

Source of truth: scripted, positions from the bedroom LiDAR survey (Reference/bedroom_survey).
Frame: PLAN coordinates. Origin = plan (0, 0, 0), +X east, +Y north, Z up, metres; the package
goes on a marker at (0, 0, 0) with no rotation. Wall pieces are built in a wall frame:
u = the plan coordinate along the wall, d = distance out from the wall surface into the room.

Dimensions (inches, plan):
  wall surfaces: center wall east face x 138.75, south y 0, east x 274.6, back y 158.4,
    closet south wall south face y 130.35, closet front wall west face x 247.7   S (survey)
  window x 171.25..205.45, sill 26.5, head 85                    M / layout
  blinds: carrier y -1.5 (inside the recess), headrail z 83.5..85, vanes 3.5 wide,
    to 0.75 above the sill, near-closed (8 deg)                  SCAN depth / EST
  base station SW centre (139.5, 25, 97), closet (260, 129.8, 96)  S +-2
  base station 3.4 x 3.4 x 3.0, bracket arm 2.0                  EST
  smoke detector (166, 142), 6 dia x 2, ceiling z 108            S
  thermostat y 110..114, z 45.5..50.5, 1.1 deep                  A (survey z 45..51)
  wall art: every piece's bounds are in ART below, measured on capture frames rectified onto
    the known wall plane (Reference/bedroom_fixtures_work/rect.py, final.py), +-0.5   SCAN
  frame widths: center 1.4 black, tree 0.4 black, south 1.1 white                   SCAN
  back wall photo strip x 174.5..191.5, z 60.5..67: stays an abstract painted strip (privacy)
Artwork textures are the real pictures, rectified from the capture photos; signatures, a
game logo and a place name are blurred or blanked (see final.py).
"""

import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

import common


def m(inches):
    return inches * 0.0254


NAME = "bedroom_fixtures"

# wall: (axis index of the normal, surface coordinate, outward sign, planar axis name)
WALLS = {
    "center_e": (0, 138.75, +1, "+X"),
    "south": (1, 0.0, +1, "+Y"),
    "east": (0, 274.6, -1, "-X"),
    "back": (1, 158.4, -1, "-Y"),
    "closet_s": (1, 130.35, -1, "-Y"),
    "closet_fw": (0, 247.7, -1, "-X"),
}

import layout  # noqa: E402  (package dir is on sys.path during builds)

ATLAS = layout.ATLAS
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("east_wall", 270, 8, 0.45), ("south_wall", 0, 8, 0.45), ("north_side", 180, 10, 0.45)]

PLANAR = {}

# (region, wall, u0, u1, z0, z1, style)   style: paper | frame_black | frame_thin | frame_white
# Bounds re-measured on the rectified capture frames (Reference/bedroom_fixtures_work/final).
ART = [
    ("art_center", "center_e", 67.7, 82.1, 53.7, 71.0, "frame_black"),
    ("art_south", "south", 162.0, 169.8, 58.2, 69.7, "frame_white"),
    ("card_s", "south", 156.75, 160.0, 65.4, 70.25, "paper"),
    ("art_strip", "back", 174.5, 191.5, 60.5, 67.0, "paper"),
    ("art_moon", "east", 91.75, 117.0, 52.0, 67.1, "paper"),
    ("art_tree", "east", 70.8, 87.4, 51.3, 71.5, "frame_thin"),
    ("mid_poster", "east", 37.15, 45.75, 59.85, 71.0, "paper"),
    ("card_a", "east", 45.9, 50.1, 52.25, 58.6, "paper"),
    ("card_b", "east", 45.6, 50.25, 45.0, 51.15, "paper"),
    ("card_c", "east", 42.7, 45.2, 55.6, 59.25, "paper"),
    ("card_d", "east", 39.5, 43.6, 48.5, 54.65, "paper"),
    ("drawing_bw", "east", 27.0, 35.25, 56.25, 65.5, "paper"),
    ("corner_poster", "east", 6.0, 12.75, 67.5, 77.75, "paper"),
    ("art_space", "closet_s", 248.4, 266.5, 65.5, 89.75, "paper"),   # above the bag hooks (z 61.5)
    ("art_purple", "closet_fw", 137.3, 153.8, 85.8, 98.1, "paper"),
]
# keychain charms, east wall corner: (u centre, z centre, w, h), measured on the rectified frame;
# the photo of the whole cluster (y 13.25..23.25, z 64.75..77.75) is projected across them.
CHARMS = [(21.75, 75.1, 3.0, 5.25), (16.6, 75.25, 1.75, 4.0), (18.75, 72.5, 4.5, 4.5),
          (14.85, 71.15, 2.7, 6.5), (22.0, 68.25, 2.0, 5.0), (16.6, 67.5, 2.75, 5.5)]
CHARM_BOX = (13.25, 23.25, 64.75, 77.75)


def plan_box(wall, u, d, z):
    """(u0,u1),(d0,d1),(z0,z1) in a wall frame -> plan lo/hi in metres."""
    ax, s0, sign, _ = WALLS[wall]
    dd = sorted((s0 + sign * d[0], s0 + sign * d[1]))
    if ax == 0:
        lo, hi = (dd[0], u[0], z[0]), (dd[1], u[1], z[1])
    else:
        lo, hi = (u[0], dd[0], z[0]), (u[1], dd[1], z[1])
    return tuple(map(m, lo)), tuple(map(m, hi))


def panel(b, region, wall, u, d, z, side_region=None, planar=False):
    """Wall-frame box; with side_region, only the face toward the room keeps `region`."""
    lo, hi = plan_box(wall, u, d, z)
    faces = b.box(region, lo, hi)
    if side_region:
        ax, _, sign, axis = WALLS[wall]
        n = Vector((0, 0, 0))
        n[ax] = sign
        for f in faces:
            f.normal_update()
            if f.normal.dot(n) < 0.9:
                f.material_index = b.idx(side_region)
    if planar:
        ax, _, sign, axis = WALLS[wall]
        # u bounds in the direction the planar projection reads left-to-right
        ub = (m(u[0]), m(u[1])) if axis in ("+X", "-Y") else (-m(u[1]), -m(u[0]))
        PLANAR[region] = (axis, ub, (m(z[0]), m(z[1])))
    return faces


def art(b, region, wall, u0, u1, z0, z1, style):
    if style == "paper":
        panel(b, region, wall, (u0, u1), (0.0, 0.06), (z0, z1), "paper", True)
        return
    fw, dep, fr = {"frame_black": (1.4, 0.8, "frame_black"), "frame_thin": (0.4, 0.6, "frame_black"),
                   "frame_white": (1.1, 0.8, "frame_white")}[style]
    panel(b, fr, wall, (u0, u1), (0.0, dep), (z0, z1))
    # the photo covers everything inside the frame (mat and print), just proud of the frame
    panel(b, region, wall, (u0 + fw, u1 - fw), (dep - 0.2, dep + 0.03), (z0 + fw, z1 - fw), fr, True)


def charms(b):
    for uc, zc, w, h in CHARMS:
        panel(b, "charms", "east", (uc - w / 2, uc + w / 2), (0.05, 0.2), (zc - h / 2, zc + h / 2), "charms")
    u0, u1, z0, z1 = CHARM_BOX
    PLANAR["charms"] = ("-X", (-m(u1), -m(u0)), (m(z0), m(z1)))


# --- blinds (south window, as window_blinds does it) --------------------------------

WIN_X = (171.25, 205.45)
SILL, HEAD = 26.5, 85.0
VANE_W, VANE_PITCH, VANE_T = 3.5, 3.0, 0.06
TILT = 8.0


def south_box(b, region, x, y, z, tilt=0.0):
    (x0, x1), (y0, y1), (z0, z1) = x, y, z
    c = Vector((m((x0 + x1) / 2), m((y0 + y1) / 2), m((z0 + z1) / 2)))
    hx, hy, hz = m(x1 - x0) / 2, m(y1 - y0) / 2, m(z1 - z0) / 2
    mat = Matrix.Translation(c) @ Matrix.Rotation(math.radians(tilt), 4, "Z")
    b.box(region, (-hx, -hy, -hz), (hx, hy, hz), matrix=mat)


def blinds(b):
    dc = -1.5
    u0, u1 = WIN_X[0] + 0.25, WIN_X[1] - 0.25
    south_box(b, "rail", (u0, u1), (-2.6, 0.2), (83.5, HEAD))
    south_box(b, "carrier", (u0 + 0.5, u1 - 0.5), (dc - 0.3, dc + 0.3), (83.2, 83.5))
    n = int(round((u1 - u0 - VANE_W) / VANE_PITCH)) + 1
    pitch = (u1 - u0 - VANE_W) / (n - 1)
    zb, zv = SILL + 0.75, 83.2
    for i in range(n):
        cu = u0 + VANE_W / 2 + i * pitch
        dd = dc + (0.04 if i % 2 else -0.04)
        south_box(b, "vane", (cu - VANE_W / 2, cu + VANE_W / 2), (dd - VANE_T / 2, dd + VANE_T / 2),
                  (zb, zv), tilt=TILT)
    # tilt wand and pull chain at the west end, room side
    south_box(b, "wand", (u0 + 0.6, u0 + 0.95), (-0.2, 0.15), (zv - 30.0, zv))


# --- base stations, smoke detector, thermostat -------------------------------------

# (wall, surface point (x, y), centre z, aim target in plan, cable bottom z)
BASE_STATIONS = [
    ("center_e", (139.5, 25.0), 97.0, (205.0, 80.0, 40.0), 30.0),
    ("closet_s", (260.0, 129.8), 96.0, (205.0, 70.0, 40.0), 40.0),
]


def base_station(b, wall, p, zc, target, cable_z):
    ax, s0, sign, _ = WALLS[wall]
    n = Vector((0, 0, 0))
    n[ax] = sign
    wp = Vector((p[0], p[1], zc))
    wp[ax] = s0
    # wall plate and arm
    along = 0 if ax == 1 else 1
    u = wp[along]
    panel(b, "bracket", wall, (u - 0.8, u + 0.8), (0.0, 0.3), (zc - 1.9, zc + 0.7))
    arm0 = wp + n * 0.3 + Vector((0, 0, -0.6))
    arm1 = wp + n * 2.2 + Vector((0, 0, -0.6))
    lo = Vector([min(arm0[i], arm1[i]) for i in range(3)]) - Vector((0.3, 0.3, 0.3))
    hi = Vector([max(arm0[i], arm1[i]) for i in range(3)]) + Vector((0.3, 0.3, 0.3))
    for i in range(3):
        if i != ax:
            lo[i], hi[i] = (arm0[i] - 0.3, arm0[i] + 0.3)
    b.box("bracket", tuple(map(m, lo)), tuple(map(m, hi)))
    # box centre out from the wall, aimed at the room (local -Y = face)
    c = wp + n * 4.0
    f = Vector(target) - c
    yaw = math.atan2(f.x, -f.y)
    pitch = math.atan2(-f.z, Vector((f.x, f.y)).length)
    mat = (Matrix.Translation(c * 0.0254) @ Matrix.Rotation(yaw, 4, "Z")
           @ Matrix.Rotation(pitch, 4, "X"))
    w, h, d = m(3.4) / 2, m(3.4) / 2, m(3.0) / 2
    b.box("bs_body", (-w, -d + m(0.2), -h), (w, d, h), bevel=m(0.25), segments=1, matrix=mat)
    b.box("bs_face", (-w + m(0.2), -d, -h + m(0.2)), (w - m(0.2), -d + m(0.25), h - m(0.2)), matrix=mat)
    # cable from under the box down the wall
    panel(b, "cable", wall, (u + 0.9, u + 1.15), (0.0, 0.25), (cable_z, zc - 1.0))


def smoke_detector(b):
    b.cylinder("smoke", (m(166.0), m(142.0), m(107.4)), m(3.0), m(1.2), segments=20)
    b.cylinder("smoke", (m(166.0), m(142.0), m(106.5)), m(2.4), m(0.7), segments=20)


def thermostat(b):
    panel(b, "thermo", "center_e", (110.0, 114.0), (0.0, 1.0), (45.5, 50.5))
    panel(b, "thermo_face", "center_e", (110.2, 113.8), (1.0, 1.1), (45.7, 50.3), "thermo", True)


def build(coll):
    PLANAR.clear()
    b = common.Builder(REGIONS)
    for a in ART:
        art(b, *a)
    charms(b)
    blinds(b)
    for bs in BASE_STATIONS:
        base_station(b, *bs)
    smoke_detector(b)
    thermostat(b)
    return [b.to_object(NAME, coll)]


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=dict(PLANAR))
        common.collapse_materials(ob, {r: mat for r in REGIONS})
