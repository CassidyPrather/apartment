"""Over-the-range microwave: white case with a plain top band carrying a small parody
wordmark ("zapwhistle"), a raised door panel with a large pale screened window and a tall
C-shaped pull handle along its right edge, and a control column on the right with a raised
keypad panel (black display, two rows of convenience pads, a 3x4 number pad with three
function keys, start/cancel and a bottom row). Dark vent strip and two light lenses on the
underside. No visible wear in the photos, so none is painted.

Source of truth: scripted. Size from the living-room/kitchen LiDAR survey, layout and
colour from the survey crops and the close capture frames (wide_..._004000/004001/004016
front, _004249 straight-on from across the room, 31.6 px/in: door panel x 1.1-21.6 in from
the left, z 2.85-14.4; window x 2.7-18.0, z 4.1-11.5; handle x 20.3-21.7, z 2.7-12.7;
control panel x 22.1-26.7, z 2.2-12.7). There is no front vent grille: the top band is
plain white. ORIGIN AT THE BOTTOM of the case, centre of the footprint; front faces -Y.
Place at plan (64, 276.5), rotation 0, origin height Z 58.5 in (top at 76, under the short
uppers): footprint x 50-78, y 268.5-284.5.
"""

import math

from mathutils import Vector

import common

IN = 0.0254


def m(v):
    return v * IN


W = 28.0            # SCAN
D = 16.0            # SCAN (incl. the door and handle)
H = 17.5            # SCAN
CASE_FRONT = 1.8    # EST case front behind the door panel and handle (from the -Y extreme)
DOOR = (1.1, 21.6, 2.85, 14.4)      # PHOTO door panel x0, x1 (from the left edge), z0, z1
DOOR_T = 0.35       # EST door panel proud of the case
PANEL = (22.1, 26.7, 2.2, 12.7)     # PHOTO raised keypad panel x0, x1 (from the left), z0, z1
WINDOW = (2.7, 18.0, 4.1, 11.5)     # PHOTO window x0, x1 (from the left), z0, z1
HANDLE = (21.0, 2.6, 12.9)          # PHOTO handle centre x (from the left), z0, z1
GAP = 0.15          # EST

NAME = "microwave"
ATLAS = {
    "name": "microwave",
    "size": 1024,
    "regions": {
        "front": (0, 0, 1024, 640),
        "white": (0, 640, 256, 128),
        "under": (256, 640, 256, 128),
        "vent": (512, 640, 256, 128),
        "lens": (768, 640, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"microwave": {"atlas": "microwave", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 330, 8, 0.9), ("photo_below", 20, -15, 0.8), ("straight", 0, 3, 0.75)]


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0, seg=2: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg)
    yf = y0 + CASE_FRONT                         # case front (behind door panel and handle)
    # case: its front carries the printed band, seams and keypad (planar decal "front")
    bx("front", (x0, yf, 0.3), (x1, y1, H), 0.3, 1)
    bx("under", (x0 + 1.0, yf + 0.5, 0.0), (x1 - 1.0, y1 - 1.0, 0.3))
    bx("vent", (x0 + 2.0, yf + 0.4, -0.02), (x1 - 2.0, yf + 2.4, 0.3))
    for lx in (-8.0, 8.0):
        bx("lens", (lx - 1.5, yf + 3.0, -0.05), (lx + 1.5, yf + 5.5, 0.05))
    # raised door panel and keypad panel (same decal, so the window and pads land on them)
    dx0, dx1, dz0, dz1 = DOOR
    bx("front", (x0 + dx0, yf - DOOR_T, dz0), (x0 + dx1, yf + 0.05, dz1), 0.2, 1)
    kx0, kx1, kz0, kz1 = PANEL
    bx("front", (x0 + kx0, yf - 0.12, kz0), (x0 + kx1, yf + 0.05, kz1), 0.06, 1)
    # tall C-shaped pull on the door's right edge
    hx, hz0, hz1 = HANDLE
    hx += x0
    yd = yf - DOOR_T
    pts = [(hx, yd + 0.1, hz0), (hx, yd - 1.35, hz0 + 1.2), (hx, yd - 1.69, (hz0 + hz1) / 2),
           (hx, yd - 1.35, hz1 - 1.2), (hx, yd + 0.1, hz1)]
    path = common.smooth_path([Vector(tuple(map(m, p))) for p in pts], samples=2)
    prof = [(m(0.4) * math.cos(a), m(0.7) * math.sin(a)) for a in [i * math.pi / 6 for i in range(12)]]
    b.sweep("white", path, prof, up=(1, 0, 0))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS, planar={"front": ("-Y", (m(-W / 2), m(W / 2)), (0.0, m(H)))})
    common.collapse_materials(ob, {r: mat for r in REGIONS})
