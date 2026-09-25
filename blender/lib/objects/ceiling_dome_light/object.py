"""Ceiling dome light: a generic flush-mount fixture, a brushed-metal ring at the ceiling
holding a frosted white glass dome, with a small metal finial at the centre.

Source of truth: scripted. Frame: origin at the top centre (on the ceiling), everything
hangs to -Z. Placed in several rooms.

Dimensions (inches):
  diameter 13, drop 5                  coordinator brief (EST, typical flush mount)
  metal ring 13 dia at the ceiling, 12.4 at its lower lip, 1.4 tall   EST from photo
  glass dome 12 dia, from 1.4 down to 4.7                              EST
  finial 0.9 dia, to 5.0                                               EST
"""

import math

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "ceiling_dome_light"
SEGS = 32
R_OUT, R_LIP, RING_H = 6.5, 6.2, 1.4
R_GLASS, DOME_Z = 6.0, 4.7
FINIAL_R, DROP = 0.45, 5.0

REGIONS = ["metal", "diffuser"]
ATLAS = {
    "name": "ceiling_dome_light",
    "size": 512,
    "regions": {
        "metal": (0, 0, 256, 256),
        "diffuser": (256, 0, 256, 256),
    },
}
MATERIALS = {
    "ceiling_dome_light": {"atlas": "ceiling_dome_light", "mode": "opaque"},
    "ceiling_dome_light_diffuser": {"atlas": "ceiling_dome_light", "mode": "opaque"},
}
COLLIDER = "none"
STATIC = True
VIEWS = [("below", 30, -40, 1.0)]


def lathe(b, profile, segs=SEGS):
    """Revolve [(r, z, region of the segment to the next point)] (inches) about Z.
    r = 0 points become poles."""
    bm = b.bm
    rings = []
    for r, z, _ in profile:
        if r == 0:
            rings.append([bm.verts.new((0, 0, m(z)))])
        else:
            rings.append([bm.verts.new((m(r) * math.cos(2 * math.pi * i / segs),
                                        m(r) * math.sin(2 * math.pi * i / segs), m(z)))
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
    prof = [(0, 0, "metal"), (R_OUT, 0, "metal"), (R_LIP, -RING_H, "metal"),
            (R_GLASS, -RING_H, "diffuser")]
    # dome: quarter-ellipse from the lip down to the finial
    n = 8
    depth = DOME_Z - RING_H
    for i in range(1, n):
        t = (math.pi / 2) * i / n
        r = max(R_GLASS * math.cos(t), FINIAL_R + 0.3)
        prof.append((r, -RING_H - depth * math.sin(t), "diffuser"))
    prof += [(FINIAL_R, -DOME_Z, "metal"), (FINIAL_R, -DROP + 0.1, "metal"), (0, -DROP, "metal")]
    lathe(b, prof)
    return [b.to_object(NAME, coll)]


def texture(objs):
    metal = common.atlas_material("ceiling_dome_light", ATLAS)
    diff = common.atlas_material("ceiling_dome_light_diffuser", ATLAS)
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        common.collapse_materials(ob, {"metal": metal, "diffuser": diff})
