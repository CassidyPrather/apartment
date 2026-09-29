"""Shared by the bathroom packages (bathtub, toilet, vanity): the one `bathroom` atlas
and a few loft helpers for oval and rounded shapes.

Pure Python (no bpy at import time) so the GIMP texture script can read ATLAS too.
The atlas is built by objects/bathtub/textures.py; toilet/ and vanity/ textures.py
just run that same builder.
"""

import math

IN = 0.0254


def m(v):
    """Inches to meters (the one conversion)."""
    return v * IN


# 1024 px atlas, rects (x, y, w, h) in pixels, origin top-left.
ATLAS = {
    "name": "bathroom",
    "size": 1024,
    "regions": {
        "oak_doors": (0, 0, 512, 512),      # honey-oak grain, vertical (vanity fronts)
        "oak": (512, 0, 256, 512),          # honey-oak grain (carcass sides)
        "marble": (768, 0, 256, 256),       # white cultured-marble countertop, fine speckle
        "chrome": (768, 256, 128, 128),
        "nickel": (896, 256, 128, 128),     # brushed nickel (pulls, faucet, holder)
        "porcelain": (768, 384, 128, 128),  # vitreous china, bright white
        "acrylic": (896, 384, 128, 128),    # one-piece tub/shower unit
        "curtain": (0, 512, 512, 384),      # floral print, one seamless tile (photo)
        "mirror": (512, 512, 256, 256),
        "wall_paint": (768, 512, 256, 256),  # matches shell_wall's sampled colour
        "dark": (512, 768, 128, 128),       # drains, toe kick shadow
        "seat": (640, 768, 128, 128),       # toilet seat plastic
        "paper": (768, 768, 128, 128),      # toilet-paper roll
        "ring_red": (896, 768, 128, 128),   # shower-curtain rings (red plastic)
        "basin": (0, 896, 256, 128),        # tub basin seen from above (planar +Z), grime
        "unit_wall": (256, 896, 256, 128),  # tub unit walls unrolled (perimeter x height)
        "sink_bowl": (512, 896, 128, 128),  # vanity basin from above, drain grime
        "toilet_deck": (640, 896, 128, 128),  # toilet rim/rear deck from above, stains
    },
}

MATERIALS = {"bathroom": {"atlas": "bathroom", "mode": "opaque", "tiled": False}}


# --- loft helpers (work on a common.Builder) -----------------------------------------

def rrect(cx, cy, w, h, r, seg=7):
    """CCW rounded rectangle, 4*(seg+1) points, starting on the east side."""
    pts = []
    corners = [(cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90),
               (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)]
    for x, y, a0 in corners:
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return pts


def ellipse(cx, cy, a, b, n=32, phase=0.0):
    return [(cx + a * math.cos(2 * math.pi * i / n + phase),
             cy + b * math.sin(2 * math.pi * i / n + phase)) for i in range(n)]


def match_polar(outline, cx, cy, shape):
    """For each point of `outline`, the point of `shape(theta) -> (x, y)` at the same
    polar angle about (cx, cy): gives rings with matching vertex order for bridging."""
    out = []
    for x, y in outline:
        t = math.atan2(y - cy, x - cx)
        out.append(shape(t))
    return out


def ellipse_at(cx, cy, a, b):
    """shape(theta) for an ellipse: the point where the ray at polar angle theta hits it."""
    def f(t):
        c, s = math.cos(t), math.sin(t)
        r = 1.0 / math.sqrt((c / a) ** 2 + (s / b) ** 2)
        return (cx + r * c, cy + r * s)
    return f


def rrect_at(cx, cy, w, h, r):
    """shape(theta) for a rounded rectangle (ray/boundary intersection by bisection)."""
    def inside(x, y):
        dx, dy = abs(x - cx) - (w / 2 - r), abs(y - cy) - (h / 2 - r)
        if dx <= 0 or dy <= 0:
            return abs(x - cx) <= w / 2 and abs(y - cy) <= h / 2
        return dx * dx + dy * dy <= r * r

    def f(t):
        c, s = math.cos(t), math.sin(t)
        lo, hi = 0.0, max(w, h)
        for _ in range(40):
            mid = (lo + hi) / 2
            if inside(cx + mid * c, cy + mid * s):
                lo = mid
            else:
                hi = mid
        return (cx + lo * c, cy + lo * s)
    return f


def ring(b, outline, z):
    return [b.bm.verts.new((x, y, z)) for x, y in outline]


def bridge(b, region, r0, r1):
    n = len(r0)
    faces = [b.bm.faces.new((r0[i], r0[(i + 1) % n], r1[(i + 1) % n], r1[i])) for i in range(n)]
    b._tag(faces, region)
    return faces


def cap(b, region, r):
    f = b.bm.faces.new(r)
    b._tag([f], region)
    return [f]


def loft(b, region, sections, top_region=None, bottom_region=None):
    """sections: [(outline, z), ...] bottom to top, all the same point count.
    Closed solid: bridged sides plus bottom and top caps."""
    rings = [ring(b, o, z) for o, z in sections]
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        faces += bridge(b, region, r0, r1)
    faces += cap(b, bottom_region or region, rings[0])
    faces += cap(b, top_region or region, rings[-1])
    return faces


# --- tub basin geometry, shared by the model (bathtub/object.py) and the grime texture --
# All in inches, tub-local (x along the tub, + = foot end when FAUCET_END = -1; y + = back).
TUB_L, TUB_W, TUB_H = 57.9, 30.0, 17.4
TUB_UNIT_T, TUB_RIM_FRONT, TUB_BASIN_DEPTH = 1.25, 3.0, 14.0
TUB_FAUCET_END = -1
TUB_BACK_LEDGE = 3.75   # SPLAT flat deck at rim height along the back wall (x 271-275)


def tub_basin():
    """(top opening x0, x1, y0, y1), (floor centre x, y, width, depth, corner radius)."""
    x0, x1 = -TUB_L / 2 + TUB_UNIT_T, TUB_L / 2 - TUB_UNIT_T
    y0, y1 = -TUB_W / 2 + TUB_RIM_FRONT, TUB_W / 2 - TUB_UNIT_T - TUB_BACK_LEDGE
    cx, cy = (x0 + x1) / 2 + 1.5 * TUB_FAUCET_END, (y0 + y1) / 2
    return (x0, x1, y0, y1), (cx, cy, (x1 - x0) - 9.0, (y1 - y0) - 6.0, 5.0)


# --- mesh helpers needing bpy (imported lazily so the GIMP side can load this file) ----

def frustum(b, region, center, r_base, r_tip, depth, axis="X", segments=16, sign=1):
    """Cone frustum along an axis: radius r_base at the end toward -axis*sign (the wall
    or surface it stands on), r_tip at the other end."""
    import bmesh
    from mathutils import Matrix
    r1, r2 = (r_base, r_tip) if sign > 0 else (r_tip, r_base)
    r = bmesh.ops.create_cone(b.bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=r1, radius2=r2, depth=depth)
    rot = {"X": Matrix.Rotation(math.pi / 2, 4, "Y"), "Y": Matrix.Rotation(-math.pi / 2, 4, "X"),
           "Z": Matrix.Identity(4)}[axis]
    bmesh.ops.transform(b.bm, matrix=Matrix.Translation(center) @ rot, verts=r["verts"])
    faces = list({f for v in r["verts"] for f in v.link_faces})
    b._tag(faces, region)
    return faces
