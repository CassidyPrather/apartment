"""What's inside the bathroom vanity (photos 17 and 18 of
Reference/cupboards_drawers/, sorted index: PXL_20261023_032025775 / _032032811).

  vanity_contents                    under the sink, on the white cabinet floor (photo 17):
      big blue mouthwash bottle, two green denture-cleanser boxes, a plum pump bottle and
      a small dark-red bottle, three white rinse bottles with tall navy caps, a small blue
      bottle with a silver cap, hand sanitizer, a white bottle with a red cap, a white
      lotion bottle with a gold band, a big clear jug of pale yellow liquid, a clear
      trigger spray at the back, a blue glass-cleaner spray (red trigger), a blue toilet-
      bowl cleaner (red cap, teal label), a navy tissue box, a white plastic-wrapped pack,
      a tan pouch and a toothbrush leaning at the south wall, a small lavender pick.
  vanity_drawer_top_contents         the TOP drawer (photo 18: the drawer level with the
      door top, right under the full-width rail). Reparented under vanity_drawer_top in
      Unity: cotton-swab pack, toothpaste tube, orange toothbrush, coral cup, coral brush
      tube with makeup brushes, a zip bag with a green card and a lavender bit, a blue
      bandage box on its side, pink razor, teal and pink small boxes, teal blister cards,
      a rose-gold compact, white papers, a navy jar (medicine) with a black lid, and
      floss packs standing at the back.
  vanity_drawer_bottom_contents      the BOTTOM drawer (no photo; per Cassidy): three
      flat tissue boxes (navy, light blue, white with a lavender band), a teal cube box and
      a lavender plastic-wrapped hygiene pack. Reparented under vanity_drawer_bottom.

No brands: every package is a flat colour block in its real colour scheme (no text,
logos or barcodes), so no parody names are used.

Source of truth: scripted. Frame: PLAN coordinates (inches x east, y north, z up, metres
out), so the package goes on a marker at (0, 0, 0) with no rotation. Items are laid out in
the vanity's LOCAL frame (vanity/object.py: front -Y, +X north, origin on the floor at the
counter footprint centre) and moved into plan by the vanity's PLACES entry
(182.65, 227.55, rot 90). The drawer contents object's origin sits at the top drawer's own
origin (closed), so it lines up with vanity_drawer_top when reparented.

Positions: PHOTO, from the photos rectified onto the cabinet floor / drawer bottom with a
4-corner homography (Reference/vanity_contents_work/homog.py), +-1.5 in, then cleared of
each other, the P-trap and the walls. Sizes: EST from the photos against the opening
(24 in) and the drawer (20.5 in inside) or SPEC for standard items (1.5 L mouthwash
4.2 x 3 x 10.5; 32 oz trigger spray; 500-count swab pack ~10 x 4; tissue box 8.5 x 4.7).
"""

import importlib.util
import math
import os

import bmesh
from mathutils import Matrix, Vector

import common

NAME = "vanity_contents"
IN = 0.0254
HERE = os.path.dirname(os.path.abspath(__file__))

_T = {}
exec(open(os.path.join(HERE, "textures.py"), encoding="utf-8").read(), _T)   # ATLAS only
ATLAS = _T["ATLAS"]
REGIONS = list(ATLAS["regions"])
CLEAR = "bag_clear"
CLEAR_ALPHA = 0.35
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
             NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": CLEAR_ALPHA}}
COLLIDER = "none"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 0.8)]

PLACE = (182.65, 227.55, 90.0)  # the vanity's PLACES entry (shell_layout.py)
DRAWER = "vanity_drawer_top"


def _vanity():
    """The vanity package module (layout of the carcass and drawers)."""
    p = os.path.join(HERE, "..", "vanity", "object.py")
    spec = importlib.util.spec_from_file_location("objects.vanity_for_contents", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def m(inches):
    return inches * IN


# --- geometry helpers (vanity-local inches in, metres out) -----------------------------

def V(x, y, z):
    return Vector((m(x), m(y), m(z)))


def rotz(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Z")


def box(b, region, c, size, heading=0.0, bevel=0.0, seg=2, tilt=(0.0, 0.0), local=(0.0, 0.0, 0.0)):
    """Box standing on c = (x, y, z0), size (sx, sy, sz) in its own frame, turned by
    heading (deg) about Z, tilted by (about-x, about-y) degrees about its base centre."""
    sx, sy, sz = size
    mat = (Matrix.Translation(V(*c)) @ rotz(heading)
           @ Matrix.Rotation(math.radians(tilt[0]), 4, "X") @ Matrix.Rotation(math.radians(tilt[1]), 4, "Y")
           @ Matrix.Translation(V(*local)))
    return b.box(region, V(-sx / 2, -sy / 2, 0), V(sx / 2, sy / 2, sz), bevel=m(bevel),
                 segments=seg, matrix=mat)


def cone(b, region, p0, p1, r0, r1=None, seg=10):
    r1 = r0 if r1 is None else r1
    a, c = V(*p0), V(*p1)
    d = c - a
    res = bmesh.ops.create_cone(b.bm, cap_ends=True, cap_tris=False, segments=seg,
                                radius1=m(r0), radius2=m(r1), depth=d.length)
    verts = res["verts"]
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(b.bm, matrix=Matrix.Translation((a + c) / 2) @ rot, verts=verts)
    faces = list({f for v in verts for f in v.link_faces})
    b._tag(faces, region)
    return faces


def rrect(w, d, r, seg=2):
    r = min(r, w / 2 - 1e-3, d / 2 - 1e-3)
    return common.rounded_rect(0, 0, w, d, r, seg)


def oval(a, bb, n=10):
    return [(a * math.cos(2 * math.pi * i / n), bb * math.sin(2 * math.pi * i / n)) for i in range(n)]


def loft(b, regions, rings, c=(0.0, 0.0), heading=0.0, top=True):
    """rings: [(outline [(x, y)] local inches, z inches)] bottom to top, same length;
    regions: one per band (or one name)."""
    if isinstance(regions, str):
        regions = [regions] * (len(rings) - 1)
    mat = Matrix.Translation(V(c[0], c[1], 0)) @ rotz(heading)
    vr = [[b.bm.verts.new(mat @ V(x, y, z)) for x, y in ol] for ol, z in rings]
    n = len(vr[0])
    faces = []
    for k in range(len(vr) - 1):
        lo, hi = vr[k], vr[k + 1]
        band = [b.bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i])) for i in range(n)]
        b._tag(band, regions[k])
        faces += band
    f = b.bm.faces.new(list(reversed(vr[0])))
    b._tag([f], regions[0])
    faces.append(f)
    if top:
        f = b.bm.faces.new(vr[-1])
        b._tag([f], regions[-1])
        faces.append(f)
    return faces


def scaled(ol, k):
    return [(x * k, y * k) for x, y in ol]


def bottle(b, x, y, z0, w, d, h, body, cap, cap_h=1.2, cap_r=0.6, band=None, shoulder=0.9,
           heading=0.0, n=10, neck_r=None):
    """Lathe-ish bottle: oval w x d body to h, shoulder to a neck, cap on top; band =
    (region, z0, z1) a label sleeve in its own colour."""
    ol = oval(w / 2, d / 2, n)
    neck_r = neck_r or cap_r * 0.85
    nk = oval(neck_r, neck_r, n)
    rings = [(ol, z0), (ol, z0 + h - shoulder), (scaled(ol, 0.75), z0 + h - shoulder * 0.35),
             (nk, z0 + h), (nk, z0 + h + 0.3)]
    loft(b, body, rings, c=(x, y), heading=heading)
    cone(b, cap, (x, y, z0 + h + 0.3), (x, y, z0 + h + 0.3 + cap_h), cap_r, seg=n)
    if band:
        reg, a, c_ = band
        lb = scaled(ol, 1.025)
        loft(b, reg, [(lb, z0 + a), (lb, z0 + c_)], c=(x, y), heading=heading)


def trigger_spray(b, x, y, z0, heading, body, neck, head, lbl=None, h=8.0, w=2.6, d=4.0):
    """32 oz trigger spray: the wide face toward `heading` (deg, 0 = +X)."""
    ol = rrect(w, d, 0.6)
    sh = rrect(w * 0.8, d * 0.65, 0.8)
    nk = [(0.65 * math.cos(a), 0.65 * math.sin(a)) for a in
          (math.atan2(py, px) for px, py in ol)]
    loft(b, [body, body, neck], [(ol, z0), (ol, z0 + h - 1.6), (sh, z0 + h - 0.8), (nk, z0 + h)],
         c=(x, y), heading=heading)
    cone(b, neck, (x, y, z0 + h), (x, y, z0 + h + 0.6), 0.65, seg=10)
    box(b, head, (x, y, z0 + h + 0.6), (3.0, 1.3, 1.5), heading=heading, bevel=0.3, local=(0.4, 0, 0))
    box(b, head, (x, y, z0 + h + 0.9), (0.6, 0.9, 0.8), heading=heading, bevel=0.12, local=(2.1, 0, 0))
    box(b, head, (x, y, z0 + h - 0.6), (0.4, 0.7, 1.2), heading=heading, bevel=0.1, local=(1.1, 0, 0))
    if lbl:
        box(b, lbl, (x, y, z0 + 0.8), (0.06, d * 0.8, h * 0.55), heading=heading, local=(w / 2 + 0.01, 0, 0))


# --- under the sink (photo 17) --------------------------------------------------------
FLOOR = 5.0          # vanity FLOOR_Z (cabinet floor top), PHOTO
# Interior x -24.3 .. -0.15 (south side .. partition), y -9.85 .. 10.6 (face frame .. back);
# the P-trap hangs at x -13.95, y 1.6..10.6, z 18.5 and up.


def under_sink(b):
    z = FLOOR
    # Back row, south to north.
    bottle(b, -21.0, 8.2, z, 2.4, 1.8, 6.8, "plum", "white", cap_h=0.7, cap_r=0.55)   # pump bottle
    cone(b, "white", (-21.0, 8.2, z + 7.8), (-21.0, 8.2, z + 9.4), 0.18, seg=6)
    box(b, "white", (-21.0, 8.2, z + 9.3), (1.8, 0.6, 0.6), heading=-30, bevel=0.15, local=(0.5, 0, 0))
    bottle(b, -22.7, 6.0, z, 1.6, 1.6, 5.0, "dark_red", "black", cap_h=0.9, cap_r=0.5)
    # Denture-cleanser boxes: green lower half, white upper, the flaps open with the
    # tablets' tissue liner poking up; a darker second box behind on the right.
    box(b, "dent_green", (-17.6, 8.0, z), (4.2, 2.6, 3.4), heading=-8)
    box(b, "dent_white", (-17.6, 8.0, z + 3.4), (4.2, 2.6, 2.7), heading=-8)
    box(b, "dent_green", (-17.6, 8.0, z + 3.9), (4.22, 2.62, 0.5), heading=-8)
    box(b, "dent_white", (-17.6, 8.0, z + 6.05), (4.0, 0.05, 1.6), heading=-8, tilt=(-25, 0), local=(0, -1.25, 0))
    box(b, "pack_white", (-17.9, 8.3, z + 6.0), (2.6, 1.6, 1.4), heading=10, bevel=0.4)
    box(b, "dent_dark", (-14.4, 9.0, z), (1.8, 2.4, 6.2), heading=-8)
    # Clear trigger spray at the back, blue liquid in its lower half.
    trigger_spray(b, -10.6, 8.9, z, -90, "gc_blue", "sanit_clear", "white", h=8.0, w=2.4, d=3.6)
    # Plastic-wrapped white pack and the navy tissue box in the north-back corner.
    box(b, "pack_white", (-7.0, 6.4, z), (3.6, 3.2, 6.6), heading=5, bevel=0.3)
    box(b, "tissue_navy", (-3.0, 6.2, z), (4.6, 8.4, 4.2), heading=2, bevel=0.15)
    box(b, "tissue_blue", (-3.0, 6.2, z + 4.2), (3.4, 6.0, 0.03), heading=2)
    # Middle: three white rinse bottles with tall navy dosing caps, a small blue bottle
    # with a silver cap, the white lotion bottle with a gold band.
    for (x, y, h) in ((-16.0, 2.4, 7.4), (-14.2, 4.6, 7.0), (-12.2, 6.2, 6.6)):
        bottle(b, x, y, z, 2.4, 1.8, h, "white", "navy", cap_h=1.7, cap_r=0.75,
               band=("rinse_blue", h * 0.25, h * 0.6), shoulder=1.2)
    bottle(b, -18.0, 0.6, z, 1.8, 1.8, 4.0, "jo_blue", "silver", cap_h=1.6, cap_r=0.85, neck_r=0.7)
    bottle(b, -10.4, 3.0, z, 2.8, 1.9, 7.8, "white", "white", cap_h=1.4, cap_r=0.9, neck_r=0.8,
           band=("gold", 6.2, 6.6), shoulder=1.0)
    # Front: big blue mouthwash (south), the toothbrush and a tan pouch at the wall,
    # sanitizer, red-cap bottle, the clear jug, the blue glass spray, toilet cleaner.
    ol = rrect(4.2, 3.0, 0.9, 2)
    sh = rrect(2.4, 2.0, 0.8, 2)
    nk = [(0.7 * math.cos(a), 0.7 * math.sin(a)) for a in (math.atan2(py, px) for px, py in ol)]
    loft(b, ["mw_blue", "mw_blue", "mw_blue", "mw_blue"],
         [(ol, z), (ol, z + 7.6), (sh, z + 8.8), (nk, z + 9.4), (nk, z + 9.6)], c=(-19.8, -5.0))
    cone(b, "black", (-19.8, -5.0, z + 9.6), (-19.8, -5.0, z + 11.0), 0.8, seg=12)
    lb = scaled(ol, 1.02)
    loft(b, "mw_label", [(lb, z + 2.0), (lb, z + 5.8)], c=(-19.8, -5.0))
    box(b, "mw_band", (-19.8, -6.55, z + 3.4), (3.6, 0.06, 1.0))
    box(b, "tan_pouch", (-22.6, -6.2, z), (1.4, 2.8, 3.4), heading=10, tilt=(0, -18), bevel=0.4)
    cone(b, "tb_clear", (-22.4, -3.0, z + 0.2), (-24.0, -2.0, z + 7.2), 0.25, seg=6)
    box(b, "white", (-24.0, -2.0, z + 6.6), (0.5, 0.35, 1.2), heading=30, tilt=(0, -13))
    box(b, "lavender", (-20.6, -8.6, z), (1.3, 0.35, 0.2), heading=25)
    bottle(b, -15.2, -7.0, z, 2.3, 1.6, 5.2, "sanit_clear", "white", cap_h=1.0, cap_r=0.6,
           band=("sanit_blue", 0.6, 4.0))
    bottle(b, -12.1, -6.4, z, 2.3, 2.0, 7.0, "white", "red", cap_h=2.0, cap_r=0.85,
           band=("red", 1.0, 2.0), shoulder=1.1)
    # Clear jug of pale yellow liquid: square-shouldered, white cap and a front label.
    ol = rrect(4.4, 4.0, 0.8, 2)
    sh = rrect(2.6, 2.4, 0.9, 2)
    nk = [(0.75 * math.cos(a), 0.75 * math.sin(a)) for a in (math.atan2(py, px) for px, py in ol)]
    loft(b, ["jug_liquid", "bag_clear", "bag_clear", "bag_clear", "bag_clear"],
         [(ol, z), (ol, z + 5.6), (ol, z + 7.0), (sh, z + 8.4), (nk, z + 9.0), (nk, z + 9.4)], c=(-8.4, -5.9))
    cone(b, "white", (-8.4, -5.9, z + 9.4), (-8.4, -5.9, z + 10.4), 0.95, seg=12)
    box(b, "label_white", (-8.4, -7.92, z + 1.2), (3.0, 0.05, 3.6))
    box(b, "label_blue", (-8.4, -7.96, z + 4.0), (2.4, 0.05, 0.7))
    trigger_spray(b, -4.2, -5.0, z, -90, "gc_blue", "white", "red", lbl=None, h=8.4, w=2.4, d=3.8)
    # Toilet-bowl cleaner: blue bottle, teal label sleeve, angled neck, red cap.
    ol = rrect(2.9, 2.2, 0.9, 2)
    loft(b, ["bc_blue", "bc_blue"], [(ol, z), (ol, z + 6.4), (scaled(ol, 0.6), z + 7.6)], c=(-1.75, -7.7))
    loft(b, "bc_teal", [(scaled(ol, 1.03), z + 0.3), (scaled(ol, 1.03), z + 4.0)], c=(-1.75, -7.7))
    cone(b, "bc_blue", (-1.75, -7.7, z + 7.5), (-2.1, -8.4, z + 9.0), 0.6, seg=10)
    cone(b, "red", (-2.1, -8.4, z + 9.0), (-2.3, -8.8, z + 10.0), 0.62, 0.45, seg=10)


# --- top drawer (photo 18) ------------------------------------------------------------

def drawer_items(b, x0, x1, y0, y1, zf):
    """Laid out from the photo rectification; (x0..x1, y0..y1) is the drawer's inside,
    zf its bottom (vanity-local inches)."""
    z = zf
    # Cotton-swab pack: blue card with the white swab bundle under a clear window.
    box(b, "swab_blue", (7.1, -1.4, z), (10.4, 3.8, 0.12), heading=-2)
    box(b, "swab_white", (8.1, -1.4, z + 0.12), (6.4, 2.4, 0.55), heading=-2, bevel=0.15)
    box(b, "bag_clear", (8.1, -1.4, z + 0.12), (6.8, 2.8, 0.7), heading=-2)
    # Toothpaste tube (white, red/blue block at the crimp end, white cap at the right),
    # a hair tie round it, the orange toothbrush in front.
    loft(b, "paste_white", [(oval(0.15, 0.95, 8), 0.0), (oval(0.55, 0.85, 8), 2.0), (oval(0.6, 0.8, 8), 6.0)],
         c=(0, 0), heading=0, top=True)
    _move_last(b, 24, Matrix.Translation(V(1.9, -5.9, z + 0.6)) @ rotz(4) @ Matrix.Rotation(math.pi / 2, 4, "Y"))
    box(b, "paste_red", (3.0, -5.84, z + 0.05), (1.6, 1.75, 1.0), heading=4)
    box(b, "paste_blue", (4.2, -5.76, z + 0.05), (0.9, 1.65, 1.08), heading=4)
    cone(b, "paste_white", (7.9, -5.5, z + 0.6), (8.9, -5.43, z + 0.6), 0.55, seg=8)
    cone(b, "black", (4.6, -5.73, z + 0.6), (4.75, -5.72, z + 0.6), 0.66, seg=8)
    box(b, "orange", (5.3, -8.45, z), (6.0, 0.45, 0.35), heading=4, bevel=0.1)
    box(b, "white", (4.6, -8.5, z + 0.32), (2.6, 0.3, 0.05), heading=4)
    box(b, "orange", (9.0, -8.2, z), (1.2, 0.35, 0.25), heading=4)
    box(b, "bristle_teal", (9.0, -8.2, z + 0.25), (1.1, 0.35, 0.4), heading=4)
    # Coral oval cup, open top.
    cup = oval(1.9, 1.5, 14)
    loft(b, ["coral", "coral", "coral_dark"],
         [(cup, z), (scaled(cup, 1.06), z + 3.4), (scaled(cup, 0.96), z + 3.4), (scaled(cup, 0.9), z + 0.25)],
         c=(11.7, -7.2))
    # Coral brush tube lying across, makeup brushes out of its open (south) end.
    cone(b, "coral", (14.4, -4.0, z + 1.4), (21.0, -4.7, z + 1.45), 1.4, seg=12)
    for dy, dz in ((-0.5, 0.3), (0.3, 0.6), (0.4, -0.2)):
        cone(b, "brush_dark", (14.0, -4.0 + dy, z + 1.3 + dz), (16.0, -4.0 + dy, z + 1.3 + dz), 0.22, seg=6)
        cone(b, "copper", (12.8, -3.95 + dy, z + 1.3 + dz), (14.0, -4.0 + dy, z + 1.3 + dz), 0.3, 0.25, seg=6)
        cone(b, "brush_dark", (11.8, -3.9 + dy, z + 1.3 + dz), (12.8, -3.95 + dy, z + 1.3 + dz), 0.45, 0.32, seg=6)
    # Zip bag (clear) with a green card and a lavender floss holder inside.
    box(b, "lime", (16.0, 1.6, z + 0.2), (3.0, 2.2, 0.08), heading=8)
    box(b, "lavender", (18.4, -0.2, z + 0.2), (2.4, 0.5, 0.3), heading=-25)
    box(b, "white", (14.3, 2.6, z + 0.2), (2.6, 1.4, 0.1), heading=-12)
    box(b, "bag_clear", (16.0, 1.0, z), (8.0, 6.0, 0.7), heading=6)
    # Bandage box on its side against the north wall.
    box(b, "band_blue", (x1 - 0.85, 2.4, z), (1.5, 4.6, 2.9), heading=2)
    box(b, "white", (x1 - 0.85, 2.4, z + 2.9), (1.5, 4.6, 0.04), heading=2)
    # Pink razor along the back, teal and pink small boxes, the teal blister cards with
    # a rose-gold compact on them, white papers at the south wall.
    cone(b, "razor_pink", (11.6, 5.4, z + 0.45), (17.0, 5.0, z + 0.45), 0.45, 0.4, seg=8)
    box(b, "pale_blue", (17.6, 4.95, z + 0.1), (1.4, 1.6, 0.5), heading=-4)
    box(b, "teal_box", (9.0, 3.4, z), (3.6, 2.6, 1.0), heading=6, bevel=0.05)
    box(b, "teal_card", (4.6, 5.0, z), (3.6, 4.4, 0.35), heading=-20)
    box(b, "white", (4.4, 5.2, z + 0.35), (2.4, 2.8, 0.25), heading=-20, bevel=0.1)
    cone(b, "rose_gold", (3.4, 6.4, z + 0.6), (3.4, 6.4, z + 1.1), 1.0, seg=12)
    box(b, "white", (3.4, 2.0, z), (2.6, 4.2, 0.12), heading=8)
    box(b, "magenta", (9.4, 6.4, z), (1.5, 2.2, 1.1), heading=-5)
    # Navy medicine jar with a black lid and a yellow lid label.
    cone(b, "jar_navy", (12.8, 6.0, z), (12.8, 6.0, z + 3.8), 1.3, seg=12)
    cone(b, "black", (12.8, 6.0, z + 3.8), (12.8, 6.0, z + 4.5), 1.25, seg=12)
    box(b, "yellow", (12.8, 6.0, z + 4.5), (1.6, 1.0, 0.04), heading=10)
    # Floss packs standing against the back, leaning back a little.
    for x, h in ((16.0, 3.6), (18.9, 3.4), (20.4, 3.2)):
        box(b, "floss_grey", (x, y1 - 1.15, z), (2.4, 0.5, h), heading=0, tilt=(-10, 0))
    cone(b, "white", (14.6, 6.8, z), (14.6, 6.8, z + 1.0), 0.9, seg=10)
    # More of the clutter under the bag and at the back: floss cards, papers, a blister.
    box(b, "floss_grey", (19.0, 3.4, z), (2.4, 3.4, 0.25), heading=-15)
    box(b, "white", (13.0, 2.4, z), (3.0, 2.0, 0.15), heading=20)
    box(b, "label_blue", (17.2, -2.4, z + 0.15), (2.2, 1.4, 0.2), heading=30)
    box(b, "teal_card", (6.0, 6.6, z + 0.35), (3.0, 1.8, 0.3), heading=10, tilt=(0, 8))
    box(b, "silver", (5.8, 4.4, z + 0.6), (1.6, 1.0, 0.3), heading=-25)
    box(b, "teal_card", (3.4, 3.6, z + 0.12), (3.2, 4.0, 0.3), heading=15, tilt=(6, 0))
    box(b, "white", (6.8, 2.6, z), (3.0, 2.2, 0.3), heading=-10)
    box(b, "magenta", (10.6, 5.0, z), (1.6, 0.9, 0.8), heading=20)
    cone(b, "white", (17.6, 6.3, z), (17.6, 6.3, z + 0.9), 0.75, seg=10)
    box(b, "floss_grey", (14.0, 4.4, z), (2.4, 3.0, 0.3), heading=35, tilt=(0, -6))


def tissue_box(b, c, size, body, top, heading=0.0, band=None):
    """Plain tissue box lying flat: body colour, a top panel with the dispenser slot as a
    darker/white oval-ish inset, an optional colour band round the middle."""
    sx, sy, sz = size
    box(b, body, c, size, heading=heading, bevel=0.08, seg=1)
    box(b, top, (c[0], c[1], c[2] + sz), (sx * 0.45, sy * 0.6 if sy > sx else sy * 0.45, 0.03),
        heading=heading)
    if band:
        box(b, band, (c[0], c[1], c[2] + sz * 0.3), (sx + 0.04, sy + 0.04, sz * 0.35), heading=heading)


def bottom_drawer_items(b, x0, x1, y0, y1, zf):
    """Bottom drawer (no photo; Cassidy: spare tissue boxes and a hygiene pack). Inside
    x0..x1, y0..y1, bottom zf; the box's top edge is 6.75 in above zf."""
    z = zf
    # Three flat boxes side by side, long axis front to back (8.6 x 4.6 x 3.6 SPEC-ish).
    tissue_box(b, (x0 + 2.6, y0 + 5.0, z), (4.6, 8.6, 3.6), "tissue_navy", "tissue_blue", heading=2)
    tissue_box(b, (x0 + 7.6, y0 + 5.2, z), (4.6, 8.6, 3.6), "pale_blue", "white", heading=-3)
    tissue_box(b, (x0 + 12.6, y0 + 5.0, z), (4.6, 8.6, 3.6), "white", "lavender", heading=1,
               band="lavender")
    # A cube box standing at the back (4.6 cube), teal with a white top.
    tissue_box(b, (x1 - 3.0, y1 - 3.2, z), (4.6, 4.6, 4.6), "bc_teal", "white", heading=6)
    # Hygiene pack: soft plastic-wrapped lavender pack lying at the back.
    box(b, "lavender", (x0 + 6.5, y1 - 2.6, z), (6.0, 4.2, 2.8), heading=-4, bevel=0.6)
    box(b, "white", (x0 + 6.5, y1 - 2.6, z + 2.8), (3.0, 2.0, 0.03), heading=-4)


def _move_last(b, n, mat):
    """Transform the last n vertices created (the loft just made) by mat."""
    b.bm.verts.ensure_lookup_table()
    verts = b.bm.verts[-n:]
    bmesh.ops.transform(b.bm, matrix=mat, verts=list(verts))


# --- build ----------------------------------------------------------------------------

def plan_matrix():
    x, y, deg = PLACE
    return Matrix.Translation(V(x, y, 0)) @ rotz(deg)


def build(coll):
    vz = _vanity()
    P = plan_matrix()
    b = common.Builder(REGIONS)
    under_sink(b)
    bmesh.ops.transform(b.bm, matrix=P, verts=list(b.bm.verts))
    root = b.to_object(NAME, coll)
    # Drawer contents: origin at each drawer's own origin (closed), in plan.
    L = vz.layout()
    s_ = m(vz.DRAWER_CLR)
    out = [root]
    for which, fill, oz0 in (("top", drawer_items, L["dzm"] + m(vz.MID_RAIL / 2)),
                             ("bottom", bottom_drawer_items, L["oz0"])):
        x0, x1, y0, y1, zf = (v / IN for v in vz.drawer_interior(which))
        d = common.Builder(REGIONS)
        fill(d, x0, x1, y0, y1, zf)
        bmesh.ops.transform(d.bm, matrix=P, verts=list(d.bm.verts))
        org_local = Vector(((L["ox2"] + s_ + L["ox3"] - s_) / 2, L["yf"] + m(vz.DRAWER_D) / 2,
                            oz0 + m(0.4)))
        out.append(d.to_object(f"vanity_drawer_{which}_contents", coll, origin=P @ org_local))
    return out


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA       # preview only
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        regions = [s.name.split(".")[0] for s in ob.data.materials]
        common.collapse_materials(ob, {r: (clear if r == CLEAR else mat) for r in regions})
