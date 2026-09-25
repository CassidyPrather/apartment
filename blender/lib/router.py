"""Router: AC1750-class dual-band router with a three-slat lid and three antennas.

Source of truth: scripted. Dimensions: dimensions.ROUTER (body SPEC, antennas EST).
Object origin: bottom center. Local frame: long axis +X, front (status LEDs) -Y,
antennas along the back (+Y) edge. Parody brand: tadpole link.
"""

import importlib
import math

from mathutils import Matrix

import common
import dimensions

importlib.reload(dimensions)

R = dimensions.ROUTER
REGIONS = ["top", "front", "back", "body", "antenna"]


def build(coll):
    L, W, H = R["length"], R["width"], R["height"]
    g = R["slat_groove"]
    lid = 0.004                                  # slats stand this far above the body
    b = common.Builder(REGIONS)
    # Body tapers in slightly toward the bottom, like the real shell.
    b.box("body", (-L / 2 + 0.003, -W / 2 + 0.003, 0.0), (L / 2 - 0.003, W / 2 - 0.003, 0.006), bevel=0.002)
    b.box("body", (-L / 2, -W / 2, 0.005), (L / 2, W / 2, H - lid), bevel=0.002)
    # Front and back strips carry the LEDs and ports; drawn as thin plates on the body.
    b.box("front", (-L / 2 + 0.004, -W / 2 - 0.0006, 0.008), (L / 2 - 0.004, -W / 2, H - lid - 0.002))
    b.box("back", (-L / 2 + 0.004, W / 2, 0.008), (L / 2 - 0.004, W / 2 + 0.0006, H - lid - 0.002))
    # Three lid slats running the full length, separated by grooves.
    sw = (W - 2 * g) / 3
    for i in range(3):
        y0 = -W / 2 + i * (sw + g)
        b.box("top", (-L / 2, y0, H - lid - 0.001), (L / 2, y0 + sw, H), bevel=0.0015)
    # Antennas: hinge knuckle on the back edge, then a flat paddle standing up.
    al, aw, at = R["antenna_len"], R["antenna_w"], R["antenna_t"]
    lean = [4, -2, 3]                            # degrees back, a little uneven like the photos
    for i, fx in enumerate((-0.36, 0.0, 0.36)):
        x = fx * L
        y = W / 2 + 0.008
        z = H * 0.5
        b.cylinder("antenna", (x, y, z), 0.007, 0.016, axis="X", segments=12)
        m = Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(-lean[i]), 4, "X")
        b.box("antenna", (-aw / 2, -at / 2, 0), (aw / 2, at / 2, al), bevel=at * 0.45, segments=3,
              matrix=m)
    ob = b.to_object("router", coll)
    return [ob]


def texture(obs):
    ob = obs[0]
    L, W, H = R["length"], R["width"], R["height"]
    mat = common.atlas_material("router", "router")
    common.atlas_uvs(ob, "router", planar={
        "top": ("+Z", (-L / 2, L / 2), (-W / 2, W / 2)),
        "front": ("-Y", (-L / 2, L / 2), (0.008, H - 0.006)),
        "back": ("+Y", (-L / 2, L / 2), (0.008, H - 0.006)),
    })
    common.collapse_materials(ob, {r: mat for r in REGIONS})
