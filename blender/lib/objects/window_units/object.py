"""Window units: white vinyl horizontal sliders set in the four window recesses of the
shell, plus a raised mini-blind in the bedroom window.

Source of truth: scripted, from shell_layout.OPENINGS (read-only import) for the
openings; the frame/sash profile below is EST (standard residential vinyl slider).
Frame: SHELL coordinates, not the usual object frame. Origin = the apartment's interior
south-west corner at floor level, +X east, +Y north, Z up, so the package goes on a
marker at (0, 0, 0) with no rotation. Each unit is built in a local (u, d, z) frame:
u runs along the opening, d is depth measured inward from the wall's exterior face
(0 = exterior face, 6 = interior face), z is height above the floor.

Two meshes: window_units (frames, sashes, latches, blind) and window_units_glass (the
panes, their own translucent material). The shell's placeholder shell_glass panes sit
at d = 1.5 and should be dropped (or hidden) once these are in.
"""

import importlib
import os
import sys

import common

LIB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import shell_layout as L  # noqa: E402

importlib.reload(L)
m = L.m

NAME = "window_units"

# --- dimensions (inches) -------------------------------------------------------------
EXT_WALL = L.EXTERIOR_WALL          # A (shell) 6 in
FRAME_FACE = 1.5                    # EST visible width of the outer frame members
FRAME_D = (0.75, 3.75)              # EST frame depth span (from the exterior face)
SASH_W = 1.75                       # EST sash rail/stile width
MEET_W = 1.25                       # EST meeting stile width (each sash)
OVERLAP = 1.0                       # EST sash overlap at the meeting rail
FIXED_D = (1.0, 2.0)                # EST fixed sash track (exterior)
SLIDE_D = (2.35, 3.35)              # EST sliding sash track (interior)
GLASS_T = 0.2                       # EST
LATCH = (0.8, 0.6, 2.75)            # EST latch w, proud, h
BLIND_D = (4.25, 5.35)              # EST blind head rail depth span (inside mount)
BLIND_HEAD_H = 1.25                 # EST
BLIND_STACK_H = 5.5                 # EST raised stack of ~1 in slats
BLIND_BOTTOM_H = 0.75               # EST
WAND_L = 22.0                       # EST tilt wand length

# Units: (wall, a0, a1, sliding sash side "lo"/"hi" along the wall axis). The wide south
# opening is two sliders side by side (plan illustration). Which half slides is EST.
UNITS = [
    ("ext_west", 42.5, 77.25, "lo"),
    ("ext_west", 101.75, 136.5, "hi"),
    ("ext_south", 38.5, 73.5, "lo"),
    ("ext_south", 73.5, 108.5, "hi"),
    ("ext_south", 171.25, 205.45, "lo"),
]
BLIND_UNIT = 4                      # the bedroom window
Z0, Z1 = L.WINDOW_SILL, L.WINDOW_HEAD

REGIONS = ["vinyl", "vinyl_track", "latch", "blind_slats", "blind_rail", "glass"]

ATLAS = {
    "name": "window_units",
    "size": 512,
    "regions": {
        "vinyl": (0, 0, 256, 256),
        "vinyl_track": (256, 0, 256, 256),
        "latch": (0, 256, 128, 128),
        "blind_slats": (128, 256, 128, 256),
        "blind_rail": (256, 256, 128, 128),
        "glass": (384, 256, 128, 128),
    },
}
GLASS_ALPHA = 0.15
MATERIALS = {
    "window_units_vinyl": {"atlas": "window_units", "mode": "opaque"},
    "window_units_glass": {"atlas": "window_units", "mode": "transparent", "alpha": GLASS_ALPHA},
}
COLLIDER = "mesh"
STATIC = True
VIEWS = []


def local_box(b, region, wall, u, d, z):
    """Box given as (u0, u1), (d0, d1), (z0, z1) inches in the unit frame of `wall`."""
    (u0, u1), (d0, d1), (z0, z1) = u, d, z
    if wall == "ext_west":           # exterior face at x = -6, inward +X, u along Y
        lo, hi = (-EXT_WALL + d0, u0, z0), (-EXT_WALL + d1, u1, z1)
    elif wall == "ext_south":        # exterior face at y = -6, inward +Y, u along X
        lo, hi = (u0, -EXT_WALL + d0, z0), (u1, -EXT_WALL + d1, z1)
    else:
        raise ValueError(wall)
    b.box(region, tuple(m(v) for v in lo), tuple(m(v) for v in hi))


def sash(b, g, wall, u0, u1, dspan, meet_side):
    """One sash: rails, stiles and its pane. meet_side is the stile at the meeting rail."""
    zb, zt = Z0 + FRAME_FACE, Z1 - FRAME_FACE
    local_box(b, "vinyl", wall, (u0, u1), dspan, (zb, zb + SASH_W))
    local_box(b, "vinyl", wall, (u0, u1), dspan, (zt - SASH_W, zt))
    wl = MEET_W if meet_side == "lo" else SASH_W
    wh = MEET_W if meet_side == "hi" else SASH_W
    local_box(b, "vinyl", wall, (u0, u0 + wl), dspan, (zb + SASH_W, zt - SASH_W))
    local_box(b, "vinyl", wall, (u1 - wh, u1), dspan, (zb + SASH_W, zt - SASH_W))
    dm = (dspan[0] + dspan[1]) / 2
    local_box(g, "glass", wall, (u0 + wl - 0.25, u1 - wh + 0.25), (dm - GLASS_T / 2, dm + GLASS_T / 2),
              (zb + SASH_W - 0.25, zt - SASH_W + 0.25))


def unit(b, g, wall, a0, a1, slide):
    f = FRAME_FACE
    # Outer frame: sill, head, two jambs, plus a darker track strip on the sill.
    local_box(b, "vinyl", wall, (a0, a1), FRAME_D, (Z0, Z0 + f))
    local_box(b, "vinyl", wall, (a0, a1), FRAME_D, (Z1 - f, Z1))
    local_box(b, "vinyl", wall, (a0, a0 + f), FRAME_D, (Z0 + f, Z1 - f))
    local_box(b, "vinyl", wall, (a1 - f, a1), FRAME_D, (Z0 + f, Z1 - f))
    local_box(b, "vinyl_track", wall, (a0 + f, a1 - f), (FRAME_D[0] + 0.2, SLIDE_D[1] + 0.2),
              (Z0 + f, Z0 + f + 0.35))
    mid = (a0 + a1) / 2
    lo_span = (a0 + f, mid + OVERLAP / 2)
    hi_span = (mid - OVERLAP / 2, a1 - f)
    fixed, sliding = (hi_span, lo_span) if slide == "lo" else (lo_span, hi_span)
    sash(b, g, wall, *fixed, FIXED_D, "lo" if slide == "lo" else "hi")
    sash(b, g, wall, *sliding, SLIDE_D, "hi" if slide == "lo" else "lo")
    # Latch on the sliding sash's meeting stile, interior face, mid height.
    lw, lp, lh = LATCH
    su = sliding[1] - MEET_W / 2 if slide == "lo" else sliding[0] + MEET_W / 2
    zc = (Z0 + Z1) / 2
    local_box(b, "latch", wall, (su - lw / 2, su + lw / 2), (SLIDE_D[1], SLIDE_D[1] + lp),
              (zc - lh / 2, zc + lh / 2))


def blind(b, wall, a0, a1):
    u = (a0 + 0.25, a1 - 0.25)
    zt = Z1
    local_box(b, "blind_rail", wall, u, BLIND_D, (zt - BLIND_HEAD_H, zt))
    zs = zt - BLIND_HEAD_H
    local_box(b, "blind_slats", wall, u, (BLIND_D[0] + 0.05, BLIND_D[1] - 0.05), (zs - BLIND_STACK_H, zs))
    zb = zs - BLIND_STACK_H
    local_box(b, "blind_rail", wall, u, (BLIND_D[0], BLIND_D[1]), (zb - BLIND_BOTTOM_H, zb))
    # Tilt wand at the low end, lift cord at the high end (interior side).
    dw = BLIND_D[1] + 0.1
    local_box(b, "blind_rail", wall, (u[0] + 1.5, u[0] + 1.8), (dw, dw + 0.3), (zs - WAND_L, zs))
    local_box(b, "blind_rail", wall, (u[1] - 1.8, u[1] - 1.7), (dw, dw + 0.1), (zb - 14.0, zs))
    local_box(b, "blind_rail", wall, (u[1] - 2.1, u[1] - 1.4), (dw - 0.2, dw + 0.4), (zb - 16.0, zb - 14.0))


def build(coll):
    b = common.Builder(REGIONS[:-1])
    g = common.Builder(["glass"])
    for i, (wall, a0, a1, slide) in enumerate(UNITS):
        unit(b, g, wall, a0, a1, slide)
        if i == BLIND_UNIT:
            blind(b, wall, a0, a1)
    return [b.to_object("window_units", coll), g.to_object("window_units_glass", coll)]


def texture(objs):
    vinyl = common.atlas_material("window_units_vinyl", ATLAS)
    glass = common.atlas_material("window_units_glass", ATLAS)
    # Blender preview of the translucency (Unity reads the manifest alpha instead).
    bsdf = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = GLASS_ALPHA
    try:
        glass.surface_render_method = "BLENDED"
    except (AttributeError, TypeError):
        glass.blend_method = "BLEND"
    glass.use_backface_culling = False
    bu, bl = UNITS[BLIND_UNIT][1], UNITS[BLIND_UNIT][2]
    zs = Z1 - BLIND_HEAD_H
    planar = {"blind_slats": ("+Y", (-m(bl), -m(bu)), (m(zs - BLIND_STACK_H), m(zs)))}
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=planar)
        common.collapse_materials(ob, {r: (glass if r == "glass" else vinyl) for r in REGIONS})
