"""Light stand: black steel tripod light stand, telescoping pole, with a small black
tracking base station on a tilt head at the top. One package, placed twice in the bedroom
(between the filing cabinet and the wall heater, and just inside the patio door).

Frame: origin on the floor at the footprint centre (the pole), front (the base station's
face) toward -Y, Z up.

Dimensions (inches):
  footprint 24 x 24 (feet on a 13.5 in radius) SCAN (bedroom survey, +-2)
  overall height 82, base station centre ~80    SCAN (head ~z 80)
  leg collar z 22, brace collar z 9            EST from photos (knee-high collar)
  leg tube 0.7 dia, braces 0.4 dia              EST
  pole sections 1.1 / 0.85 / 0.65 dia, joints at z 36 and 60   EST (photos: 3 sections)
  lock knobs 0.9 wide at each joint             EST
  base station 3.4 w x 3.4 h x 3.0 d            EST (typical tracking base station)
  tilt head: 1.0 dia, box pitched 12 deg down   EST from photos
"""

import math

from mathutils import Matrix, Vector

import common


def m(inches):
    return inches * 0.0254


NAME = "light_stand"

FOOT_R = 13.5
LEG_COLLAR_Z, BRACE_COLLAR_Z = 22.0, 9.0
LEG_D, BRACE_D = 0.7, 0.4
POLE = [(0.0, 36.0, 1.1), (35.0, 60.0, 0.85), (59.0, 77.2, 0.65)]   # (z0, z1, dia)
BOX_W, BOX_H, BOX_D = 3.4, 3.4, 3.0
BOX_CZ = 80.0
PITCH = 12.0

REGIONS = ["metal", "plastic", "rubber", "box", "face"]
ATLAS = {
    "name": NAME,
    "size": 256,
    "regions": {
        "metal": (0, 0, 128, 128),
        "plastic": (128, 0, 128, 128),
        "rubber": (0, 128, 128, 128),
        "box": (128, 128, 64, 128),
        "face": (192, 128, 64, 128),
    },
}
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"}}
COLLIDER = "none"
STATIC = True
VIEWS = [("photo_low", 20, 5, 0.9)]


def rod(b, region, p0, p1, dia, seg=8):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    faces = b.cylinder(region, (0, 0, 0), m(dia) / 2, d.length, segments=seg)
    verts = list({v for f in faces for v in f.verts})
    import bmesh
    bmesh.ops.transform(b.bm, matrix=Matrix.Translation((p0 + p1) / 2) @ rot, verts=verts)


def build(coll):
    b = common.Builder(REGIONS)
    # telescoping pole with lock knobs at the joints
    for z0, z1, dia in POLE:
        b.cylinder("metal", (0, 0, m((z0 + z1) / 2)), m(dia) / 2, m(z1 - z0), segments=10)
    for z, dia in ((LEG_COLLAR_Z, 1.6), (BRACE_COLLAR_Z, 1.4), (36.0, 1.3), (60.0, 1.05)):
        b.cylinder("plastic", (0, 0, m(z)), m(dia) / 2, m(1.4), segments=10)
    for z in (35.5, 59.5):
        b.box("plastic", (m(0.5), m(-0.3), m(z - 0.3)), (m(1.5), m(0.3), m(z + 0.3)))
    b.box("plastic", (m(0.8), m(-0.3), m(LEG_COLLAR_Z - 0.3)), (m(1.8), m(0.3), m(LEG_COLLAR_Z + 0.3)))
    # tripod: legs from the upper collar to the feet, braces from the lower collar to mid-leg
    for k in range(3):
        a = math.radians(90 + 120 * k)
        c, s = math.cos(a), math.sin(a)
        top = (m(0.8) * c, m(0.8) * s, m(LEG_COLLAR_Z))
        foot = (m(FOOT_R) * c, m(FOOT_R) * s, m(0.6))
        rod(b, "metal", top, foot, LEG_D)
        t = 0.55
        mid = tuple(top[i] + (foot[i] - top[i]) * t for i in range(3))
        rod(b, "metal", (m(0.7) * c, m(0.7) * s, m(BRACE_COLLAR_Z)), mid, BRACE_D, seg=6)
        b.cylinder("rubber", (m(FOOT_R) * c, m(FOOT_R) * s, m(0.35)), m(0.55), m(0.7), segments=8)
    # tilt head and base station, face toward -Y, pitched down
    b.cylinder("plastic", (0, 0, m(77.8)), m(0.55), m(1.2), segments=10)
    b.cylinder("plastic", (0, 0, m(78.4)), m(0.5), m(0.9), axis="X", segments=10)
    mat = Matrix.Translation((0, 0, m(BOX_CZ))) @ Matrix.Rotation(math.radians(PITCH), 4, "X")
    w, h, d = m(BOX_W) / 2, m(BOX_H) / 2, m(BOX_D) / 2
    b.box("box", (-w, -d + m(0.2), -h), (w, d, h), bevel=m(0.25), segments=1, matrix=mat)
    b.box("face", (-w + m(0.2), -d, -h + m(0.2)), (w - m(0.2), -d + m(0.25), h - m(0.2)), matrix=mat)
    return [b.to_object(NAME, coll)]


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        common.collapse_materials(ob, {r: mat for r in REGIONS})
