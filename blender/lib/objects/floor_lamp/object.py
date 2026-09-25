"""Floor lamp: a black torchiere with a white frosted-glass bowl on a slotted black socket,
a thin black pole on a round weighted base, and a short side reading arm carrying a small
black cone shade that hangs downward.

Source of truth: scripted from the LiDAR survey and the survey crops. Origin on the
floor at the centre of the base; the reading arm points to local -Y. Place at plan
(265, 42), rotation -90 (the arm then points west into the room).

Dimensions (inches):
  base 11 dia, 1.2 tall (domed)            SCAN (floor disk ~ x 259-271, y 36-48) / photo
  pole 0.9 dia                             EST
  socket 2.2 dia, z 57.5-62.5              EST from photo
  bowl 13 dia at the rim, rim z 71, bottom z 62.5   SCAN (bowl top ~70 +-4) / photo
  reading arm at z 42, reaches 5.5 in; shade 2.6 dia x 4 long, hangs to z ~36.5   EST
Materials: floor_lamp (opaque atlas) and floor_lamp_glow (the frosted bowl, inside and
out; its emission is warm white, brighter inside).
"""

import math

from mathutils import Matrix, Vector

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "floor_lamp"
SEGS = 24
BASE_R = 5.5
POLE_R = 0.45
ARM_Z, ARM_L = 42.0, 5.5

ATLAS = {
    "name": "floor_lamp",
    "size": 256,
    "regions": {
        "black": (0, 0, 128, 128),
        "socket": (128, 0, 128, 128),
        "glass_out": (0, 128, 128, 128),
        "glass_in": (128, 128, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {
    "floor_lamp": {"atlas": "floor_lamp", "mode": "opaque", "tiled": False},
    "floor_lamp_glow": {"atlas": "floor_lamp", "mode": "opaque", "tiled": False},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 300, 5, 0.9), ("below", 330, -20, 0.6)]


def lathe(b, profile, segs=SEGS, centre=(0, 0)):
    """Revolve [(r, z, region of the segment to the next point)] (inches) about Z."""
    bm = b.bm
    cx, cy = centre
    rings = []
    for r, z, _ in profile:
        if r == 0:
            rings.append([bm.verts.new((m(cx), m(cy), m(z)))])
        else:
            rings.append([bm.verts.new((m(cx + r * math.cos(2 * math.pi * i / segs)),
                                        m(cy + r * math.sin(2 * math.pi * i / segs)), m(z)))
                          for i in range(segs)])
    for k in range(len(profile) - 1):
        a, c, region = rings[k], rings[k + 1], profile[k][2]
        faces = []
        for i in range(segs):
            j = (i + 1) % segs
            if len(a) == 1:
                faces.append(bm.faces.new((a[0], c[i], c[j])))
            elif len(c) == 1:
                faces.append(bm.faces.new((a[i], c[0], a[j])))
            else:
                faces.append(bm.faces.new((a[i], c[i], c[j], a[j])))
        b._tag(faces, region)


def build(coll):
    b = common.Builder(REGIONS)
    # base, pole, socket
    lathe(b, [(0, 0, "black"), (BASE_R, 0, "black"), (BASE_R, 0.5, "black"), (BASE_R - 0.8, 1.0, "black"),
              (1.2, 1.3, "black"), (POLE_R, 1.4, "black"), (POLE_R, 57.5, "socket"), (1.1, 57.6, "socket"),
              (1.1, 62.6, "socket"), (0, 62.6, "black")])
    # bowl: frosted outside from the socket up to the rim, then the inside back down
    out = [(1.3, 62.4), (3.4, 62.9), (5.0, 64.2), (6.0, 66.2), (6.45, 68.6), (6.5, 71.0)]
    inn = [(6.3, 71.0), (6.25, 68.7), (5.8, 66.4), (4.8, 64.5), (3.2, 63.3), (0, 63.0)]
    prof = [(r, z, "glass_out") for r, z in out[:-1]] + [(out[-1][0], out[-1][1], "glass_out")]
    prof += [(r, z, "glass_in") for r, z in inn]
    lathe(b, prof)
    # reading arm: a short tube out along -Y, a knuckle, and a hanging cone shade
    ax, ay = 0.0, -ARM_L
    b.sweep("black", [(0, 0, m(ARM_Z - 1.5)), (0, m(-2.5), m(ARM_Z)), (0, m(ay), m(ARM_Z + 0.6))],
            common.circle_profile(m(0.28), 8))
    b.cylinder("black", (m(ax), m(ay), m(ARM_Z + 0.4)), m(0.5), m(1.0), segments=10)
    lathe(b, [(0.6, ARM_Z - 0.2, "black"), (1.0, ARM_Z - 1.2, "black"), (1.3, ARM_Z - 4.8, "black"),
              (1.1, ARM_Z - 4.9, "black"), (0, ARM_Z - 4.3, "socket")], segs=14, centre=(ax, ay))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    glow = common.atlas_material("floor_lamp_glow", ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: (glow if r.startswith("glass") else mat) for r in REGIONS})
