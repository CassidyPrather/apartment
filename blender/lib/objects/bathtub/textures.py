"""The shared `bathroom` atlas (bathtub, toilet, vanity). Runs inside GIMP with the
gimp_textures helpers in scope:

    python blender/lib/textures/gimp_headless.py --object bathtub

Flat fills for porcelain, acrylic, chrome, nickel, marble, curtain, mirror and wall
paint (no bathroom photos exist yet). The oak grain is photo-derived: a plain stretch
of the kitchen's tall oak cabinet door (the vanity is assumed to match the kitchen),
rectified, lighting-flattened and tinted; the vanity's shaker door frames are drawn on
top at the positions vanity/object.py builds them.
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

OAK = (192, 130, 70)           # golden oak, sampled mid-tone from the kitchen cabinets
OAK_QUAD = [(2198, 300), (2288, 300), (2288, 460), (2198, 460)]   # plain door panel


def oak_grain(w, h):
    img = rectify(os.path.join(REF, "IMG_1498.jpg"), OAK_QUAD, w, h)
    flatten_lighting(img, 60, OAK, detail=70.0)
    return img


def paste(a, src, region):
    x, y, w, h = a.rect(region)
    add_layer_from(a.img, src, region, x, y)
    a.lay = flatten(a.img)


def vanity_doors(a):
    """Face frame + two shaker doors, mapped planar over the vanity front."""
    x, y, w, h = a.rect("oak_doors")
    F = S.VANITY_FRONT
    fx0, fx1 = F["x"]
    fz0, fz1 = F["z"]

    def px(v):
        return x + (v - fx0) / (fx1 - fx0) * w

    def pz(v):
        return y + (fz1 - v) / (fz1 - fz0) * h

    shadow = (92, 56, 26, 0.55)
    light = (238, 196, 140, 0.35)
    dz0, dz1 = F["door_z"]
    s = F["stile"]
    for d0, d1 in F["doors"]:
        # gap shadow around each door
        fill_rect(a.img, a.lay, (round(px(d0)) - 3, round(pz(dz1)) - 3,
                                 round(px(d1) - px(d0)) + 6, 3), shadow)
        fill_rect(a.img, a.lay, (round(px(d0)) - 3, round(pz(dz0)),
                                 round(px(d1) - px(d0)) + 6, 3), shadow)
        # recessed centre panel: slightly darker, with a shadowed top/left bevel and a
        # lit bottom/right bevel.
        p0, p1, q0, q1 = px(d0 + s), px(d1 - s), pz(dz1 - s), pz(dz0 + s)
        fill_rect(a.img, a.lay, (round(p0), round(q0), round(p1 - p0), round(q1 - q0)),
                  (150, 95, 45, 0.18))
        fill_rect(a.img, a.lay, (round(p0), round(q0), round(p1 - p0), 5), shadow)
        fill_rect(a.img, a.lay, (round(p0), round(q0), 5, round(q1 - q0)), shadow)
        fill_rect(a.img, a.lay, (round(p0), round(q1) - 4, round(p1 - p0), 4), light)
        fill_rect(a.img, a.lay, (round(p1) - 4, round(q0), 4, round(q1 - q0)), light)
        # rail/stile joints on the door frame
        for zz in (dz1 - s, dz0 + s):
            fill_rect(a.img, a.lay, (round(px(d0)), round(pz(zz)), round(p0 - px(d0)), 1),
                      (110, 70, 35, 0.5))
            fill_rect(a.img, a.lay, (round(p1), round(pz(zz)), round(px(d1) - p1), 1),
                      (110, 70, 35, 0.5))
    # centre gap between the doors
    fill_rect(a.img, a.lay, (round(px(-0.25)), round(pz(dz1)), round(px(0.25) - px(-0.25)),
                             round(pz(dz0) - pz(dz1))), (70, 42, 20))
    # top rail of the face frame: faint horizontal joint under it
    fill_rect(a.img, a.lay, (x, round(pz(fz1 - 0.3)), w, 2), (110, 70, 35, 0.4))


def build():
    a = Atlas(ATLAS)
    # Oak: photo grain for both oak regions.
    for region in ("oak", "oak_doors"):
        _, _, w, h = a.rect(region)
        g = oak_grain(w, h)
        paste(a, g, region)
        g.delete()
        a.material(region, 0.0, 0.45)       # satin lacquer
    vanity_doors(a)

    a.fill("marble", (232, 222, 204), 0.0, 0.8, noise=0.03, blur=6.0)   # cultured marble, cream
    # soft two-scale mottling instead of hard veins
    grain(a.img, a.lay, a.rect("marble"), 0.05, 14.0)
    grain(a.img, a.lay, a.rect("marble"), 0.015, 1.0)
    a.fill("chrome", (214, 216, 220), 1.0, 0.92, noise=0.01)
    a.fill("nickel", (178, 176, 170), 1.0, 0.55, noise=0.03)
    a.fill("porcelain", (240, 240, 238), 0.0, 0.9, noise=0.008)
    a.fill("acrylic", (238, 236, 231), 0.0, 0.78, noise=0.01)
    a.fill("curtain", (226, 226, 220), 0.0, 0.12, noise=0.05, blur=0.6)  # light woven fabric
    a.fill("mirror", (188, 196, 200), 1.0, 0.97)
    a.fill("wall_paint", (206, 200, 191), 0.0, 0.18, noise=0.04, blur=1.6)  # = shell_wall
    a.fill("dark", (34, 32, 30), 0.0, 0.2, noise=0.02)
    a.fill("seat", (236, 235, 230), 0.0, 0.7, noise=0.008)
    a.save()
