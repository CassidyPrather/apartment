"""Washer/dryer: 24-inch stacked electric laundry center in the laundry closet.

Source of truth: scripted (this file). Coarse block-in from one photo (the closet seen
from the hallway, front-left and above); no tape measurements yet.

Layout, bottom to top: top-load washer cabinet with a dark toe kick and a lid on its
flat top; behind the lid a plain vertical riser; a full-width control strip (washer
timer, two small selector knobs, a push knob, dryer timer) with a slight lip (the riser face leans back beneath it); then the
dryer cabinet with a flat rounded-corner door hinged on the left, a recessed pull slot
on its right edge and a generic caution sticker. The whole upper section (riser,
controls, dryer) is set back from the washer front by the depth of the exposed washer top.

Object origin: on the floor at the footprint centre. Local frame: width along X,
front faces -Y, Z up. Parody brand on the control strip: tumblewump.
"""

import math

import bmesh
from mathutils import Matrix

import common

NAME = "washer_dryer"


def m(inches):
    return inches * 0.0254


# --- dimensions (inches) with provenance ------------------------------------------
# SPEC = typical published size of a 24" stacked laundry center (exact model unknown)
# EST  = read off the photo in proportion to the width
W_IN = 23.9            # SPEC  overall width
D_IN = 27.0            # SPEC  overall depth (closet is 27.25 deep)
H_IN = 71.5            # SPEC  overall height
KICK_IN = 1.0          # EST   toe-kick height
KICK_INSET_IN = 0.6    # EST   toe-kick setback
WASHER_TOP_IN = 36.0   # EST   washer cabinet top (typical 36; photo is too foreshortened)
TOP_EXPOSED_IN = 11.0  # EST   washer top depth in front of the riser (from the lid's shape)
RISER_TOP_IN = 41.3    # EST   riser runs from the washer top up to the control strip
RISER_RECESS_IN = 0.3  # EST   riser top sits a little behind the dryer front
RISER_SLOPE_IN = 3.5   # EST   riser face slopes back to here at the washer top (photo's diagonal edge)
PANEL_TOP_IN = 46.2    # EST   control strip 4.9 tall (photo: ~1/5 of the dryer height)
PANEL_LIP_IN = 0.3     # EST   control strip stands proud of the dryer front
DOOR_X_IN = (5.4, 21.5)    # EST  door left/right edges measured from the unit's left side
DOOR_Z_IN = (49.2, 66.0)   # EST  door bottom/top
DOOR_T_IN = 0.45           # EST  door stands proud of the dryer front
LID_MARGIN_IN = 1.6        # EST  lid inset from the cabinet sides
LID_FRONT_IN = 1.9         # EST  lid inset from the washer front
LID_BACK_GAP_IN = 0.8      # EST  gap between lid and riser
LID_T_IN = 0.35            # EST  lid thickness above the washer top
# knobs: (x fraction of width, diameter in, kind) read off the photo's control strip
# and the grip fin's tilt in degrees (clockwise as seen from the front)
KNOBS = [(0.18, 3.3, "dial", 35), (0.39, 1.6, "small", -30), (0.47, 1.6, "small", 25),
         (0.70, 1.3, "button", 0), (0.87, 3.3, "dial", 70)]

W, D, H = m(W_IN), m(D_IN), m(H_IN)
Y_FRONT = -D / 2
Y_UPPER = Y_FRONT + m(TOP_EXPOSED_IN)          # dryer front plane
Z_WASHER = m(WASHER_TOP_IN)
Z_RISER = m(RISER_TOP_IN)
Z_PANEL = m(PANEL_TOP_IN)
DOOR_X = (-W / 2 + m(DOOR_X_IN[0]), -W / 2 + m(DOOR_X_IN[1]))
DOOR_Z = (m(DOOR_Z_IN[0]), m(DOOR_Z_IN[1]))
Y_DOOR = Y_UPPER - m(DOOR_T_IN)
Y_PANEL = Y_UPPER - m(PANEL_LIP_IN)

ATLAS = {
    "name": NAME,
    "size": 1024,
    "regions": {
        "door": (0, 0, 512, 536),
        "panel": (0, 560, 1024, 180),
        "enamel": (512, 0, 256, 256),
        "knob": (768, 0, 128, 128),
        "knob_ring": (896, 0, 128, 128),
        "kick": (512, 256, 128, 128),
        "hinge": (640, 256, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", -26, 14, 1.0), ("photo_upper", -26, 10, 0.6)]


def frustum(b, region, center, r_base, r_tip, depth, segments):
    """Front-facing cone frustum: radius r_base against the panel (+Y), r_tip toward -Y."""
    r = bmesh.ops.create_cone(b.bm, cap_ends=True, cap_tris=False, segments=segments,
                              radius1=r_tip, radius2=r_base, depth=depth)
    bmesh.ops.transform(b.bm, matrix=Matrix.Translation(center) @ Matrix.Rotation(-math.pi / 2, 4, "X"),
                        verts=r["verts"])
    b._tag(list({f for v in r["verts"] for f in v.link_faces}), region)


def fin(b, region, center, width, depth, height, tilt_deg):
    """Grip fin standing off a knob face, tilted about the knob's axis."""
    rot = Matrix.Translation(center) @ Matrix.Rotation(math.radians(tilt_deg), 4, "Y")
    b.box(region, (-width / 2, -depth / 2, -height / 2), (width / 2, depth / 2, height / 2),
          bevel=min(width, depth) * 0.3, segments=1, matrix=rot)


def build(coll):
    b = common.Builder(REGIONS)
    # washer cabinet and toe kick
    b.box("kick", (-W / 2 + m(0.4), Y_FRONT + m(KICK_INSET_IN), 0), (W / 2 - m(0.4), D / 2 - m(0.5), m(KICK_IN) + 0.002))
    b.box("enamel", (-W / 2, Y_FRONT, m(KICK_IN)), (W / 2, D / 2, Z_WASHER), bevel=m(0.35), segments=2)
    # lid
    b.box("enamel", (-W / 2 + m(LID_MARGIN_IN), Y_FRONT + m(LID_FRONT_IN), Z_WASHER - 0.002),
          (W / 2 - m(LID_MARGIN_IN), Y_UPPER + m(RISER_SLOPE_IN) - m(LID_BACK_GAP_IN), Z_WASHER + m(LID_T_IN)),
          bevel=m(0.3), segments=2)
    # upper section: riser, control strip, dryer
    # riser: a wedge whose face leans back from under the control strip to the washer top
    yb, yt = Y_UPPER + m(RISER_SLOPE_IN), Y_UPPER + m(RISER_RECESS_IN)
    faces = b.prism("enamel", [(yb, Z_WASHER - 0.002), (D / 2, Z_WASHER - 0.002), (D / 2, Z_RISER), (yt, Z_RISER)],
                    -W / 2 + m(0.15), W / 2 - m(0.15))
    verts = list({v for f in faces for v in f.verts})
    bmesh.ops.transform(b.bm, matrix=Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))), verts=verts)
    b.box("enamel", (-W / 2, Y_UPPER, Z_RISER), (W / 2, D / 2, Z_PANEL))
    b.box("panel", (-W / 2, Y_PANEL, Z_RISER), (W / 2, Y_UPPER + 0.001, Z_PANEL))
    b.box("enamel", (-W / 2, Y_UPPER, Z_PANEL), (W / 2, D / 2, H), bevel=m(0.3), segments=2)
    # dryer door (flat plate, rounded corners), hinge knuckles on its left
    x0, x1 = DOOR_X
    z0, z1 = DOOR_Z
    b.box("door", (x0, Y_DOOR, z0), (x1, Y_UPPER + 0.001, z1), bevel=m(0.35), segments=2)
    for zc in (z0 + m(2.5), z1 - m(2.5)):
        b.box("hinge", (x0 - m(0.35), Y_DOOR + m(0.1), zc - m(0.9)), (x0 + m(0.1), Y_UPPER + 0.001, zc + m(0.9)))
    # knobs
    # Photo detail: the timers are a white knob with a grip fin standing in a sloped grey
    # skirt; the two selectors are grey with a white fin; the push knob sits in a bezel.
    zc = (Z_RISER + Z_PANEL) / 2
    for fx, dia, kind, ang in KNOBS:
        x = -W / 2 + fx * W
        r = m(dia) / 2
        if kind == "dial":
            frustum(b, "knob_ring", (x, Y_PANEL - m(0.18), zc), r, r * 0.84, m(0.36), 24)
            frustum(b, "knob", (x, Y_PANEL - m(0.6), zc), r * 0.72, r * 0.66, m(0.5), 20)
            fin(b, "knob", (x, Y_PANEL - m(1.0), zc), r * 0.34, m(0.5), r * 1.3, ang)
        elif kind == "small":
            frustum(b, "knob_ring", (x, Y_PANEL - m(0.3), zc), r, r * 0.9, m(0.6), 16)
            fin(b, "knob", (x, Y_PANEL - m(0.75), zc), r * 0.4, m(0.4), r * 1.75, ang)
        else:
            frustum(b, "knob_ring", (x, Y_PANEL - m(0.07), zc), r * 1.3, r * 1.18, m(0.14), 16)
            frustum(b, "knob", (x, Y_PANEL - m(0.3), zc), r, r * 0.93, m(0.45), 16)
    # The control strip's raised right-hand end cap.
    b.box("enamel", (W / 2 - m(0.45), Y_PANEL - m(0.2), Z_RISER - m(0.05)),
          (W / 2, Y_UPPER + 0.001, Z_PANEL + m(0.1)), bevel=m(0.08), segments=1)
    ob = b.to_object(NAME, coll)
    return [ob]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS, planar={
        "door": ("-Y", DOOR_X, DOOR_Z),
        "panel": ("-Y", (-W / 2, W / 2), (Z_RISER, Z_PANEL)),
    })
    common.collapse_materials(ob, {r: mat for r in REGIONS})
