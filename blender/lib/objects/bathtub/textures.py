"""The shared `bathroom` atlas (bathtub, toilet, vanity). Runs inside GIMP with the
gimp_textures helpers in scope:

    python blender/lib/textures/gimp_headless.py --object bathtub

Flat fills for porcelain, acrylic, chrome, nickel, marble, curtain, mirror and wall
paint, in the albedo colours sampled by the bathroom survey (Reference/bathroom_survey/).
The oak grain is photo-derived: a plain stretch of the kitchen's oak cabinet door
(same honey-oak species as the vanity), rectified, lighting-flattened and tinted to the
vanity's surveyed colour. Door and drawer shapes are geometry, not drawn.
"""

import importlib
import os
import sys

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "bathtub")
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)
import bathroom_shared as S  # noqa: E402

importlib.reload(S)
ATLAS = S.ATLAS

OAK = (178, 104, 32)           # tint; lands at the survey albedo #9a5a1c after flattening
OAK_QUAD = [(2198, 300), (2288, 300), (2288, 460), (2198, 460)]   # plain door panel


def oak_grain(w, h):
    img = rectify(os.path.join(REF, "IMG_1498.jpg"), OAK_QUAD, w, h)
    flatten_lighting(img, 60, OAK, detail=70.0)
    return img


def paste(a, src, region):
    x, y, w, h = a.rect(region)
    add_layer_from(a.img, src, region, x, y)
    a.lay = flatten(a.img)


def build():
    a = Atlas(ATLAS)
    # Oak: photo grain for both oak regions.
    for region in ("oak", "oak_doors"):
        _, _, w, h = a.rect(region)
        g = oak_grain(w, h)
        paste(a, g, region)
        g.delete()
        a.material(region, 0.0, 0.45)       # satin lacquer

    a.fill("marble", (226, 226, 221), 0.0, 0.8, noise=0.02, blur=4.0)   # survey #e2e2dd
    grain(a.img, a.lay, a.rect("marble"), 0.04, 0.6)                     # fine speckle
    a.fill("chrome", (214, 216, 220), 1.0, 0.92, noise=0.01)
    a.fill("nickel", (168, 166, 160), 1.0, 0.55, noise=0.03)            # survey #a8a6a0
    a.fill("porcelain", (242, 237, 230), 0.0, 0.9, noise=0.006)         # survey #f2ede6
    a.fill("acrylic", (233, 230, 225), 0.0, 0.8, noise=0.006)           # survey #e9e6e1
    a.fill("curtain", (228, 224, 214), 0.0, 0.12, noise=0.05, blur=0.6)  # plain neutral
    a.fill("mirror", (188, 196, 200), 1.0, 0.97)
    a.fill("wall_paint", (207, 197, 180), 0.0, 0.18, noise=0.04, blur=1.6)  # survey #cfc5b4
    a.fill("dark", (34, 32, 30), 0.0, 0.2, noise=0.02)
    a.fill("seat", (240, 236, 229), 0.0, 0.7, noise=0.006)
    a.fill("paper", (244, 243, 238), 0.0, 0.05, noise=0.03)
    a.save()
