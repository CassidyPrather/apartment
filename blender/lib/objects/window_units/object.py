"""Window units: white vinyl horizontal sliders set in the four window recesses of the
shell. (The bedroom window has vertical blinds like the living room's, in window_blinds:
bedroom LiDAR frames 96-132 and 276-708; the 2 in blind in the bedroom captures hangs on
the patio door, door_entry.)

Source of truth: scripted, from shell_layout.OPENINGS (read-only import) for the
openings; the frame/sash profile below is EST (standard residential vinyl slider).
Frame: SHELL coordinates, not the usual object frame. Origin = the apartment's interior
south-west corner at floor level, +X east, +Y north, Z up, so the package goes on a
marker at (0, 0, 0) with no rotation. Each unit is built in a local (u, d, z) frame:
u runs along the opening, d is depth measured inward from the wall's exterior face
(0 = exterior face, 6 = interior face), z is height above the floor.

Hardware per unit (EST, standard vinyl slider; the photos only show the blinds): a cam
latch on the sliding sash's meeting stile (body + lever) and its keeper on the fixed
sash's meeting stile, a finger-pull strip on the sliding sash's meeting stile, and two
weep-slot covers on the exterior sill.

Two meshes: window_units (frames, sashes, hardware) and window_units_glass (the
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
LATCH = (0.8, 0.6, 2.75)            # EST latch body w, proud, h
LATCH_LEVER = (0.35, 0.3, 1.9)      # EST cam lever w, proud, h (points up when locked)
PULL_H = 8.0                        # EST finger-pull strip length

# Units: (wall, a0, a1, sliding sash side "lo"/"hi" along the wall axis). The wide south
# opening is two sliders side by side (plan illustration). Which half slides is EST.
UNITS = [
    ("ext_west", 42.5, 77.25, "lo"),
    ("ext_west", 101.75, 136.5, "hi"),
    ("ext_south", 38.5, 73.5, "lo"),
    ("ext_south", 73.5, 108.5, "hi"),
    ("ext_south", 171.25, 205.45, "lo"),
]
Z0, Z1 = L.WINDOW_SILL, L.WINDOW_HEAD

REGIONS = ["vinyl", "vinyl_track", "latch", "blind_slats", "blind_rail", "glass"]
# blind_slats / blind_rail are no longer used (the bedroom mini-blind moved to the patio
# door); the atlas keeps them so the texture layout is unchanged.

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
    # Cam latch on the sliding sash's meeting stile, interior face, mid height, with its
    # lever; the keeper on the fixed sash's meeting stile beside it.
    lw, lp, lh = LATCH
    su = sliding[1] - MEET_W / 2 if slide == "lo" else sliding[0] + MEET_W / 2
    zc = (Z0 + Z1) / 2
    local_box(b, "latch", wall, (su - lw / 2, su + lw / 2), (SLIDE_D[1], SLIDE_D[1] + lp),
              (zc - lh / 2, zc + lh / 2))
    vw, vp, vh = LATCH_LEVER
    local_box(b, "latch", wall, (su - vw / 2, su + vw / 2), (SLIDE_D[1] + lp, SLIDE_D[1] + lp + vp),
              (zc - 0.2, zc + vh))
    ku = sliding[1] + 0.2 if slide == "lo" else sliding[0] - 0.2   # just past the sash edge
    local_box(b, "latch", wall, (ku - 0.18, ku + 0.18), (FIXED_D[1], SLIDE_D[1] + 0.25),
              (zc - 0.9, zc + 0.9))
    # finger-pull strip on the same stile, below the latch
    local_box(b, "vinyl_track", wall, (su - 0.25, su + 0.25), (SLIDE_D[1], SLIDE_D[1] + 0.3),
              (zc - lh / 2 - 2.0 - PULL_H, zc - lh / 2 - 2.0))
    # weep-slot covers on the exterior face of the sill
    for fu in (0.25, 0.75):
        u = a0 + (a1 - a0) * fu
        local_box(b, "vinyl_track", wall, (u - 0.75, u + 0.75), (FRAME_D[0] - 0.12, FRAME_D[0]),
                  (Z0 + 0.3, Z0 + 0.8))


def build(coll):
    b = common.Builder(REGIONS[:-1])
    g = common.Builder(["glass"])
    for i, (wall, a0, a1, slide) in enumerate(UNITS):
        unit(b, g, wall, a0, a1, slide)
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
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        common.collapse_materials(ob, {r: (glass if r == "glass" else vinyl) for r in REGIONS})
