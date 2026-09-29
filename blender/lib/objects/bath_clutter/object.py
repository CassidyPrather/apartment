"""Bathroom clutter: the everyday items outside the tub and the linen niche, as seen in
the bathroom LiDAR capture (Reference/bathroom-splat/LidarSeries_20260925_005649_127,
frame indices below are positions in the sorted COLMAP images list).

  vanity counter   electric toothbrush on its charger, teal round container, mouthwash
                   bottle, soap dispenser, clear acrylic organizer tray (hair straightener,
                   paddle brush, lotion pump bottle, lotion tube, deodorant, toothpaste,
                   lipsticks), acrylic brush cup with makeup brushes, tilted hand mirror,
                   small purple jar, purple hair spray, black setting spray, big blue jar,
                   7-day pill box, black toiletry bag with a tan band, nail clippers,
                   foundation bottle, steel makeup palette, makeup brush, two eyeliners,
                   hair clip, makeup-wipes pack          (frames 109-139)
  wall             hair dryer hanging from a small hook north of the mirror, its black cord
                   looping over the counter into a plug-in shock-protection plug in the
                   duplex outlet, and the toothbrush charger's white cord along the back
                   splash into the same outlet            (frames 111, 125, 145-149)
  towel           tan hand towel through the towel ring (84, 99). The two yellow bath
                   towels on the north towel bar belong to tub_niche_clutter.
  toilet           three trigger-spray cleaners and a bamboo paper-towel stand on the tank
                   lid (151-155, 200-207); a chrome wire rack with three toilet rolls hooked
                   on the tank's south side (153-166)
  floor            blue-grey shag bath mat in front of the vanity (70-79, 109-119), toilet
                   plunger and toilet brush in their holders in the NW corner (168-199), small
                   white wastebasket under the towel bar (213-231), stainless pedal bin in
                   the corner by the tub (216-225, 263-266)
No brands: parody labels (see textures.py), plain everything else.

Source of truth: scripted. Frame: PLAN coordinates (+X east, +Y north, Z up from the
finished floor, metres; origin plan (0, 0, 0)). The package goes on a marker at (0, 0, 0)
with no rotation, like bedroom_cables and bath_fixtures.

Placement (inches, model plan). Positions come from the capture photos rectified onto
the counter / floor / wall planes (Reference/bath_clutter_work/rect.py, survey frame
shifted by the survey->model offset (-6.45, -3.9) from bath_fixtures), then snapped
onto the MODELLED surfaces and cleared from the modelled fixtures:
  vanity top z 31.9, x 172.05 (back splash face) .. 193.95, y 203.25 .. 252.6,
  basin ellipse centre (181.05, 213.6) 13 x 17, faucet base x 172.25..174.05     vanity
  toilet tank lid x 172.475..180.925, y 258.45..278.55, top z 30.9; button (176.6, 265.5)
  towel ring centre (190.65, 203.9, 54.8) r 2.6; towel bar x 210.55..235.55 (the bin
  sits under it); mirror north edge y 238.8                                           bath_fixtures
  tub apron x 245.45, north wall y 286, west wall x 171.3                      bathtub/shell
The rectified photos agree with each other to about +-2 in, so each position is PHOTO
(+-2 in); sizes are EST from the photos against the known counter / tank sizes, or SPEC
where the item is a standard size (toilet roll 4.4 dia x 4.0, duplex plate 2.75 x 4.5).
"""

import math
import os

import bmesh
from mathutils import Matrix, Vector

import atlas_layout
import common

NAME = "bath_clutter"
IN = 0.0254
HERE = os.path.dirname(os.path.abspath(__file__))

_T = {}
exec(open(os.path.join(HERE, "textures.py"), encoding="utf-8").read(), _T)   # ATLAS only
ATLAS = _T["ATLAS"]
REGIONS = list(ATLAS["regions"])
CLEAR = "clear"
CLEAR_ALPHA = 0.3
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
             NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": CLEAR_ALPHA}}
COLLIDER = "none"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 0.8)]


def m(inches):
    return inches * IN


# --- anchors (inches, model plan) -------------------------------------------------------
TOP = 31.9                      # vanity top (vanity TOP_Z, SCAN)
WALL_W = 171.3                  # bath west wall face (shell)
SPLASH_X, SPLASH_TOP = 172.05, 35.8     # vanity back splash face / top
TANK_TOP = 30.9                 # toilet tank lid top (toilet TANK_TOP, SCAN)
OUTLET = (244.0, 43.5)          # PHOTO (y, z centre) duplex outlet north of the mirror
RING = (190.65, 203.9, 54.8, 2.6)       # bath_fixtures towel ring (x, y, z centre, r)

PROJ = {}   # region -> UV projection spec (inches), filled while building


# --- geometry helpers (inches in, metres out) ---------------------------------------------

def V(x, y, z):
    return Vector((m(x), m(y), m(z)))


def rotz(deg):
    return Matrix.Rotation(math.radians(deg), 4, "Z")


def box(b, region, c, size, heading=0.0, bevel=0.0, seg=2, local=(0.0, 0.0)):
    """Box standing on c = (x, y, z0), size (sx, sy, sz) in its own frame, turned by
    heading (deg); local = (lx, ly) offset in the turned frame."""
    sx, sy, sz = size
    lx, ly = local
    mat = Matrix.Translation(V(c[0], c[1], c[2])) @ rotz(heading) @ Matrix.Translation(V(lx, ly, 0))
    return b.box(region, V(-sx / 2, -sy / 2, 0), V(sx / 2, sy / 2, sz), bevel=m(bevel),
                 segments=seg, matrix=mat)


def cone(b, region, p0, p1, r0, r1=None, seg=10, cap=None):
    """Truncated cone between two points (inches)."""
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
    if cap:
        b.bm.normal_update()
        ax = d.normalized()
        b._tag([f for f in faces if abs(f.normal.dot(ax)) > 0.99], cap)
    return faces


def sphere(b, region, c, r, seg=8, rings=6, scale=(1, 1, 1)):
    res = bmesh.ops.create_uvsphere(b.bm, u_segments=seg, v_segments=rings, radius=m(r))
    verts = res["verts"]
    bmesh.ops.scale(b.bm, vec=scale, verts=verts)
    bmesh.ops.translate(b.bm, vec=V(*c), verts=verts)
    faces = list({f for v in verts for f in v.link_faces})
    b._tag(faces, region)
    return faces


def rrect(w, d, r, seg=3):
    """CCW rounded-rect outline centred on 0 (inches): w along local x, d along local y."""
    r = min(r, w / 2 - 1e-3, d / 2 - 1e-3)
    return common.rounded_rect(0, 0, w, d, r, seg)


def circle(r, n=12):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def loft(b, regions, rings, c=(0.0, 0.0), heading=0.0, bottom=True, top=True, top_region=None,
         bottom_region=None):
    """rings: [(outline [(x, y)] local inches, z inches)], all the same length; regions: one
    per band between consecutive rings (or a single name)."""
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
    if bottom:
        f = b.bm.faces.new(list(reversed(vr[0])))
        b._tag([f], bottom_region or regions[0])
        faces.append(f)
    if top:
        f = b.bm.faces.new(vr[-1])
        b._tag([f], top_region or regions[-1])
        faces.append(f)
    return faces


def cord(b, region, pts, r=0.12, n=6, samples=3):
    path = common.smooth_path([V(*p) for p in pts], samples=samples)
    return b.sweep(region, path, common.circle_profile(m(r), n), up=(0, 0, 1))


def wire_loop(b, region, pts, r=0.09):
    return b.sweep(region, [V(*p) for p in pts], common.circle_profile(m(r), 6), up=(0, 0, 1),
                   closed=True)


def label(b, region, c, d_deg, w, h, off, t=0.03):
    """Thin label plate standing on c = (x, y, z0) centre-line, pushed `off` in along its
    outward direction d_deg; registers a planar projection seen from outside."""
    d = Vector((math.cos(math.radians(d_deg)), math.sin(math.radians(d_deg)), 0))
    right = Vector((-d.y, d.x, 0))
    cx, cy = c[0] + d.x * off, c[1] + d.y * off
    box(b, region, (cx, cy, c[2]), (t, w, h), heading=d_deg)
    o = Vector((cx, cy, c[2])) - right * (w / 2)
    PROJ[region] = ("plane", o, right, Vector((0, 0, 1)), w, h)


def sheet(b, region, grid, normal, t):
    """A cloth slab: grid rows of (x, y, z) inches (top row first); thickness t along
    `normal` (plan unit vector toward the viewer)."""
    nv = Vector(normal).normalized() * (t / 2)
    rows, cols = len(grid), len(grid[0])
    front = [[b.bm.verts.new(V(*(Vector(p) + nv))) for p in row] for row in grid]
    back = [[b.bm.verts.new(V(*(Vector(p) - nv))) for p in row] for row in grid]
    faces = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            faces.append(b.bm.faces.new((front[i][j], front[i + 1][j], front[i + 1][j + 1], front[i][j + 1])))
            faces.append(b.bm.faces.new((back[i][j], back[i][j + 1], back[i + 1][j + 1], back[i + 1][j])))
    ring = [(0, j) for j in range(cols)] + [(i, cols - 1) for i in range(1, rows)] + \
           [(rows - 1, j) for j in range(cols - 2, -1, -1)] + [(i, 0) for i in range(rows - 2, 0, -1)]
    for k in range(len(ring)):
        (i0, j0), (i1, j1) = ring[k], ring[(k + 1) % len(ring)]
        faces.append(b.bm.faces.new((front[i0][j0], back[i0][j0], back[i1][j1], front[i1][j1])))
    b._tag(faces, region)
    return faces


def drape(x0, x1, y_top, z_top, y_bot, z_bot, rows, cols, amp, period, phase=0.0, normal=(0, -1),
          x0b=None, x1b=None, hem_wave=0.4):
    """Grid for a hanging cloth in a vertical plane parallel to x: vertical pleats that grow
    toward the hem; the width can flare from (x0, x1) at the top to (x0b, x1b) at the hem."""
    x0b = x0 if x0b is None else x0b
    x1b = x1 if x1b is None else x1b
    grid = []
    for i in range(rows):
        s = i / (rows - 1)
        z = z_top + (z_bot - z_top) * s
        y = y_top + (y_bot - y_top) * s
        a0, a1 = x0 + (x0b - x0) * s, x1 + (x1b - x1) * s
        row = []
        for j in range(cols):
            u = j / (cols - 1)
            x = a0 + (a1 - a0) * u
            fold = amp * (0.35 + 0.65 * s) * math.sin(2 * math.pi * (x - x0) / period + phase)
            zz = z + (hem_wave * math.sin(2 * math.pi * (x - x0) / period + phase + 1.0) if i == rows - 1 else 0)
            row.append((x, y + normal[1] * fold, zz))
        grid.append(row)
    return grid


# --- counter items ------------------------------------------------------------------------

def toothbrush(b):
    x, y = 173.6, 205.0                                   # PHOTO frames 84, 109, 141
    box(b, "tb_white", (x, y, TOP), (2.0, 2.0, 0.7), bevel=0.3)
    cone(b, "tb_white", (x, y, TOP + 0.7), (x, y, TOP + 6.2), 0.55, 0.5, seg=10)
    cone(b, "tb_blue", (x, y, TOP + 2.0), (x, y, TOP + 5.0), 0.57, 0.555, seg=10)
    cone(b, "tb_white", (x, y, TOP + 6.2), (x, y, TOP + 8.0), 0.28, 0.2, seg=8)
    box(b, "tb_white", (x, y, TOP + 7.9), (0.45, 0.5, 1.0), bevel=0.12, seg=1)
    box(b, "tb_blue", (x + 0.35, y, TOP + 8.0), (0.3, 0.42, 0.8), bevel=0.08, seg=1)


def teal_jar(b):
    x, y = 174.3, 207.6                                   # PHOTO frames 139, 141
    cone(b, "teal_dark", (x, y, TOP), (x, y, TOP + 1.1), 1.7, seg=16)
    cone(b, "teal", (x, y, TOP + 1.1), (x, y, TOP + 1.6), 1.75, 1.7, seg=16)


def mouthwash(b):
    x, y = 189.3, 206.9                                   # PHOTO frames 84, 109, 128
    ol = rrect(2.3, 3.3, 0.6)
    neck = [(0.8 * math.cos(math.atan2(py, px)), 0.8 * math.sin(math.atan2(py, px))) for px, py in ol]
    loft(b, ["mw_liquid", CLEAR, CLEAR], [(ol, TOP), (ol, TOP + 3.0), (ol, TOP + 7.4), (neck, TOP + 8.4)],
         c=(x, y), bottom=True, top=False)
    cone(b, "black", (x, y, TOP + 8.3), (x, y, TOP + 9.5), 0.82, 0.8, seg=12)
    label(b, "lbl_mouthwash", (x, y, TOP + 1.0), 0.0, 2.2, 4.2, 1.16)


def soap_dispenser(b):
    x, y = 174.6, 221.0                                   # PHOTO frames 125, 131, 138
    cone(b, "soap_body", (x, y, TOP), (x, y, TOP + 5.0), 1.5, 1.45, seg=14)
    cone(b, "soap_body", (x, y, TOP + 5.0), (x, y, TOP + 5.5), 1.45, 0.8, seg=14)
    cone(b, "dark_grey", (x, y, TOP + 5.5), (x, y, TOP + 6.1), 0.75, seg=12)
    box(b, "dark_grey", (x + 0.4, y, TOP + 6.1), (2.8, 1.4, 0.7), bevel=0.3)


TRAY = (172.6, 181.2, 223.2, 236.2, 2.2, 0.12)            # x0, x1, y0, y1, h, wall (PHOTO)
TRAY_DIV_X, TRAY_DIV_Y = 176.2, 229.9


def organizer(b):
    """Clear acrylic tray with a long back compartment and two front ones."""
    x0, x1, y0, y1, h, t = TRAY
    fl = TOP + t
    b.box(CLEAR, V(x0, y0, TOP), V(x1, y1, fl))
    for lo, hi in (((x0, y0), (x0 + t, y1)), ((x1 - t, y0), (x1, y1)),
                   ((x0, y0), (x1, y0 + t)), ((x0, y1 - t), (x1, y1)),
                   ((TRAY_DIV_X - t / 2, y0), (TRAY_DIV_X + t / 2, y1)),
                   ((TRAY_DIV_X, TRAY_DIV_Y - t / 2), (x1, TRAY_DIV_Y + t / 2))):
        top = TOP + (h if lo[0] in (x0, x1 - t) or lo[1] in (y0, y1 - t) else h - 0.2)
        b.box(CLEAR, V(lo[0], lo[1], fl), V(hi[0], hi[1], top))
    # back compartment: hair straightener (blue grips, black plates and hinge) + paddle brush
    sx = 174.0
    box(b, "black", (sx, 225.05, fl), (1.3, 2.7, 1.0), bevel=0.35)
    box(b, "strt_blue", (sx, 228.85, fl), (1.35, 4.9, 1.0), bevel=0.4)
    box(b, "black", (sx, 231.9, fl), (1.25, 1.3, 0.9), bevel=0.3)
    brush = rrect(2.2, 3.2, 1.05, seg=3)
    loft(b, "black", [(brush, fl), (brush, fl + 0.55)], c=(174.3, 234.4))
    cone(b, "black", (174.9, 232.9, fl + 0.3), (175.7, 228.3, fl + 0.3), 0.4, 0.3, seg=8)
    # east compartments: lotion pump bottle, lotion tube, lipsticks, deodorant, toothpaste
    lotion(b, 178.3, 234.4, fl)
    cone(b, "paste_white", (179.9, 231.2, fl + 0.45), (179.9, 234.8, fl + 0.6), 0.45, 0.6, seg=10)
    cone(b, "orange", (179.9, 234.8, fl + 0.6), (179.9, 235.8, fl + 0.6), 0.45, seg=10)
    for (lx, hh, reg) in ((177.1, 2.4, "lip_gold"), (177.9, 2.8, "lip_black"), (178.7, 2.2, "lip_rose")):
        cone(b, reg, (lx, 231.1, fl), (lx, 231.1, fl + hh), 0.35, seg=8)
    box(b, "deo_blue", (178.6, 226.6, fl), (2.4, 1.8, 1.1), bevel=0.4)
    box(b, "deo_light", (180.2, 226.6, fl), (0.8, 1.8, 1.1), bevel=0.35)
    cone(b, "paste_white", (177.0, 228.6, fl + 0.45), (180.1, 228.6, fl + 0.55), 0.3, 0.55, seg=10)
    cone(b, "tb_blue", (180.1, 228.6, fl + 0.55), (180.7, 228.6, fl + 0.55), 0.38, seg=10)
    # straightener cord: out of the hinge end, over the tray wall, onto the counter
    cord(b, "black", [(sx, 223.9, fl + 0.45), (174.2, 223.1, TOP + h + 0.15), (175.2, 222.4, TOP + 0.6),
                      (176.6, 222.2, TOP + 0.1), (178.3, 222.7, TOP + 0.1), (179.4, 222.4, TOP + 0.1)],
         r=0.1)
    box(b, "black", (179.9, 222.4, TOP), (1.0, 0.6, 0.5), bevel=0.15)


def lotion(b, x, y, z0):
    """Slatherby pump bottle, label facing east (the room)."""
    body = rrect(1.9, 3.0, 0.5)
    sh = rrect(1.6, 2.4, 0.75)
    neck = circle(0.6, len(body))
    loft(b, "lotion_yellow", [(body, z0), (body, z0 + 5.5), (sh, z0 + 6.8), (neck, z0 + 7.3)], c=(x, y))
    label(b, "lbl_lotion", (x, y, z0 + 1.0), 0.0, 2.1, 4.2, 0.96)
    cone(b, "pump_blue", (x, y, z0 + 7.3), (x, y, z0 + 7.9), 0.65, seg=10)
    cone(b, "white", (x, y, z0 + 7.9), (x, y, z0 + 8.5), 0.2, seg=6)
    box(b, "pump_blue", (x, y + 0.3, z0 + 8.5), (1.2, 2.6, 0.6), bevel=0.25)


def brush_cup(b):
    """Clear two-compartment acrylic cup with makeup brushes and pencils."""
    x, y = 183.4, 225.6                                   # PHOTO frames 125, 131, 139
    w, d, h, t = 3.8, 2.4, 4.0, 0.12
    x0, x1, y0, y1 = x - w / 2, x + w / 2, y - d / 2, y + d / 2
    b.box(CLEAR, V(x0, y0, TOP), V(x1, y1, TOP + t))
    for lo, hi in (((x0, y0), (x0 + t, y1)), ((x1 - t, y0), (x1, y1)), ((x0, y0), (x1, y0 + t)),
                   ((x0, y1 - t), (x1, y1)), ((x - t / 2, y0), (x + t / 2, y1))):
        b.box(CLEAR, V(lo[0], lo[1], TOP + t), V(hi[0], hi[1], TOP + h))
    for bx, by, tx, ty in ((181.9, 225.2, -0.6, -0.3), (182.4, 225.9, -0.2, 0.5),
                           (182.9, 225.1, 0.3, -0.5), (182.3, 225.4, -0.4, 0.1)):
        p0 = (bx, by, TOP + t)
        p1 = (bx + tx, by + ty, TOP + 5.6)
        p2 = (bx + tx * 1.23, by + ty * 1.23, TOP + 6.9)
        cone(b, "rose_gold", p0, p1, 0.2, 0.14, seg=6)
        cone(b, "tan", p1, p2, 0.2, 0.04, seg=6)
    for bx, by, tx in ((184.1, 225.3, 0.4), (184.7, 225.9, 0.7)):
        cone(b, "black", (bx, by, TOP + t), (bx + tx, by, TOP + 6.2), 0.16, 0.12, seg=6)


def hand_mirror(b):
    x, y = 183.6, 231.0                                   # PHOTO frames 125, 131, 139
    n = Vector((0.77, 0.0, 0.64))                         # face tilted up toward the room
    cz = TOP + 1.7 * 0.77 + 0.05
    c = Vector((x, y, cz))
    cone(b, "black", tuple(c - n * 0.15), tuple(c + n * 0.15), 1.7, seg=20)
    cone(b, "mirror_face", tuple(c + n * 0.15), tuple(c + n * 0.18), 1.45, seg=20)
    box(b, "black", (x - 1.3, y, TOP), (0.3, 0.8, 1.9), heading=0.0)     # fold-out stand


def counter_jars(b):
    x, y = 182.6, 235.6                                   # small purple jar (PHOTO 131, 132)
    cone(b, "jar_purple_dark", (x, y, TOP), (x, y, TOP + 0.9), 1.25, seg=14)
    cone(b, "jar_purple", (x, y, TOP + 0.9), (x, y, TOP + 1.6), 1.3, 1.28, seg=14)
    x, y = 174.4, 238.7                                   # big blue jar (PHOTO 125, 131, 132)
    cone(b, "jar_blue_dark", (x, y, TOP), (x, y, TOP + 1.7), 2.1, seg=18)
    cone(b, "jar_blue", (x, y, TOP + 1.7), (x, y, TOP + 2.9), 2.15, 2.12, seg=18)


def spray_bottle(b, x, y, h, body, lbl, cap, lbl_z=(0.6, 4.8)):
    """Round spray bottle with a wrapped label facing east."""
    cone(b, body, (x, y, TOP), (x, y, TOP + h), 1.0, seg=14)
    cone(b, lbl, (x, y, TOP + lbl_z[0]), (x, y, TOP + lbl_z[1]), 1.03, seg=14)
    PROJ[lbl] = ("wrap", (x, y), TOP + lbl_z[0], TOP + lbl_z[1], 0.0)
    cone(b, body, (x, y, TOP + h), (x, y, TOP + h + 0.4), 1.0, 0.45, seg=14)
    cone(b, "white" if cap != "black" else "black", (x, y, TOP + h + 0.4), (x, y, TOP + h + 0.9), 0.45, seg=10)
    cone(b, cap, (x, y, TOP + h + 0.9), (x, y, TOP + h + 1.5), 0.36, seg=10)


def north_counter(b):
    spray_bottle(b, 184.8, 234.2, 5.6, "purple_body", "lbl_purple", "purple_cap")   # PHOTO 125, 131
    spray_bottle(b, 184.0, 240.8, 4.6, "black_matte", "lbl_black", "black", (0.5, 3.8))  # PHOTO 131, 132
    # 7-day AM/PM pill box
    box(b, "pill_white", (176.8, 246.9, TOP), (4.3, 8.8, 0.9), bevel=0.15)
    box(b, "pill_top", (176.8, 246.9, TOP + 0.9), (4.2, 8.7, 0.1))
    PROJ["pill_top"] = ("plane", Vector((174.7, 242.55, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)), 4.2, 8.7)
    # black toiletry bag, tan band on the east end, zipper along the top
    bx, by, bh = 184.3, 249.1, 5.0
    box(b, "bag_black", (bx, by, TOP), (10.0, 5.6, 5.8), heading=bh, bevel=2.1, seg=3)
    box(b, "bag_tan", (bx, by, TOP + 2.2), (0.12, 2.6, 0.9), heading=bh, local=(5.0, 0.0))
    box(b, "zipper", (bx, by, TOP + 5.78), (5.6, 0.3, 0.08), heading=bh)
    box(b, "metal", (bx, by, TOP + 5.8), (0.9, 0.4, 0.15), heading=bh, local=(2.4, 0.3))
    # nail clippers, foundation, palette, makeup brush
    box(b, "metal", (184.8, 243.2, TOP), (2.3, 0.55, 0.3), heading=70, bevel=0.1, seg=1)
    box(b, "metal", (185.5, 244.3, TOP), (2.2, 0.5, 0.3), heading=58, bevel=0.1, seg=1)
    box(b, "beige", (188.4, 243.8, TOP), (1.1, 1.1, 2.4), bevel=0.3)
    cone(b, "white", (188.4, 243.8, TOP + 2.4), (188.4, 243.8, TOP + 3.2), 0.4, seg=8)
    px, py, ph = 190.3, 240.2, 10.0
    box(b, "palette_top", (px, py, TOP), (4.4, 5.8, 0.08), heading=ph)
    r = rotz(ph).to_3x3()
    ux, uy = r @ Vector((1, 0, 0)), r @ Vector((0, 1, 0))
    PROJ["palette_top"] = ("plane", Vector((px, py, 0)) - ux * 2.2 - uy * 2.9, ux, uy, 4.4, 5.8)
    cone(b, "black", (186.0, 245.6, TOP + 0.25), (190.2, 245.6, TOP + 0.42), 0.22, 0.3, seg=8)
    cone(b, "metal", (190.2, 245.6, TOP + 0.42), (191.2, 245.6, TOP + 0.45), 0.3, 0.36, seg=8)
    cone(b, "tan", (191.2, 245.6, TOP + 0.45), (192.2, 245.6, TOP + 0.45), 0.44, 0.32, seg=8)


def front_counter(b):
    # eyeliners, hair clip (PHOTO 125, 131)
    cone(b, "navy", (186.2, 229.9, TOP + 0.2), (190.3, 229.2, TOP + 0.2), 0.2, 0.17, seg=6)
    cone(b, "metal", (187.4, 229.7, TOP + 0.2), (187.7, 229.65, TOP + 0.2), 0.21, seg=6)
    cone(b, "black", (184.9, 232.8, TOP + 0.18), (186.6, 228.4, TOP + 0.18), 0.18, 0.15, seg=6)
    box(b, "black", (187.4, 235.5, TOP), (2.0, 0.45, 0.08), heading=60)
    # Smudgebuster makeup-wipes pack
    wx, wy, wh = 188.3, 224.0, -8.0
    box(b, "wipes_blue", (wx, wy, TOP), (5.2, 7.4, 1.2), heading=wh, bevel=0.5)
    box(b, "wipes_top", (wx, wy, TOP + 1.18), (4.0, 6.2, 0.04), heading=wh)
    r = rotz(wh).to_3x3()
    ux, uy = r @ Vector((1, 0, 0)), r @ Vector((0, 1, 0))
    o = Vector((wx, wy, 0)) + ux * 2.0 - uy * 3.1          # east-south corner of the label
    PROJ["wipes_top"] = ("plane", o, uy, -ux, 6.2, 4.0)    # reads left-to-right from the room


def hair_dryer(b):
    """Silver dryer hanging from a hook by its handle loop, barrel along the wall pointing
    north; PHOTO frames 145-149 rectified on the wall (Reference/bath_clutter_work/w147.png)."""
    hx, hy, hz = WALL_W, 242.6, 71.0
    box(b, "metal", (hx + 0.08, hy, hz - 0.45), (0.16, 0.5, 0.9))
    cone(b, "metal", (hx + 0.1, hy, hz), (hx + 1.0, hy, hz), 0.1, seg=6)
    cone(b, "metal", (hx + 1.0, hy, hz), (hx + 1.0, hy, hz + 0.5), 0.1, seg=6)
    bx, bz = 173.55, 61.6                                   # barrel axis
    cone(b, "dark_grey", (bx, 239.0, bz), (bx, 239.6, bz), 1.7, 1.95, seg=16)
    cone(b, "silver", (bx, 239.6, bz), (bx, 245.1, bz), 1.95, 1.75, seg=16)
    cone(b, "dark_grey", (bx, 245.1, bz), (bx, 246.1, bz), 1.7, 1.55, seg=16)
    cone(b, "metal", (bx + 1.5, 242.6, bz), (bx + 1.95, 242.6, bz), 0.5, 0.5, seg=10)  # side badge disc
    top, bot = (173.3, 242.4, 69.6), (173.55, 243.0, 63.3)
    cone(b, "silver", top, bot, 0.62, 0.72, seg=12)
    # hanging loop over the hook
    wire_loop(b, "black", [(173.2, 242.5, 70.0), (172.6, 242.6, 71.3), (171.9, 242.6, 71.8),
                           (171.7, 242.6, 71.0), (172.4, 242.5, 70.1)], r=0.12)
    # the cord: out of the handle top, down the wall past the mirror, a loop on the counter,
    # back up the splash into the plug-in shock-protection plug in the outlet
    oy, oz = OUTLET
    pts = [(173.1, 242.2, 70.0), (172.4, 241.4, 69.0), (171.6, 241.0, 66.0), (171.5, 241.1, 55.0),
           (171.5, 241.2, 45.0), (171.5, 241.2, 37.5), (171.6, 241.25, 36.0), (172.0, 241.3, 35.98),
           (172.3, 241.35, 35.2), (172.35, 241.4, 32.3), (172.9, 241.4, 32.08), (175.5, 241.3, 32.04),
           (178.5, 241.4, 32.04), (181.0, 241.9, 32.04), (182.6, 242.9, 32.04), (182.4, 244.4, 32.04),
           (180.6, 244.6, 32.04), (179.3, 243.5, 32.04), (177.0, 242.2, 32.04), (174.3, 242.3, 32.04),
           (172.9, 243.3, 32.1), (172.35, 243.6, 32.4), (172.3, 243.7, 35.2), (171.95, 243.8, 35.98),
           (171.5, 243.9, 37.0), (171.48, oy, 40.2), (171.9, oy, 41.1)]
    cord(b, "black", pts, r=0.14, samples=3)
    # warning tag on the cord near the splash (no text)
    box(b, "tag", (171.62, 243.85, 37.6), (0.04, 0.9, 1.4))
    # duplex outlet plate, the black shock-protection plug (red test button) and the
    # toothbrush charger's white plug
    b.box("outlet_white", V(WALL_W, oy - 1.375, oz - 2.25), V(WALL_W + 0.25, oy + 1.375, oz + 2.25),
          bevel=m(0.06), segments=1)
    b.box("black", V(WALL_W + 0.25, oy - 0.8, oz - 2.3), V(WALL_W + 1.45, oy + 0.8, oz + 0.2),
          bevel=m(0.2), segments=1)
    b.box("plug_red", V(WALL_W + 1.45, oy - 0.25, oz - 0.6), V(WALL_W + 1.55, oy + 0.25, oz - 0.1))
    b.box("cord_white", V(WALL_W + 0.25, oy - 0.5, oz + 0.5), V(WALL_W + 1.15, oy + 0.5, oz + 1.4),
          bevel=m(0.12), segments=1)
    # white charger cord: down beside the black plug, over the splash, south along the
    # splash foot (behind the faucet) to the charger base
    cord(b, "cord_white", [(171.9, oy, oz + 0.5), (171.7, oy + 0.9, oz + 0.1), (171.5, oy + 1.2, oz - 2.5),
                           (171.5, oy + 1.2, 37.0), (171.6, oy + 1.2, 35.93), (172.0, oy + 1.2, 35.93),
                           (172.14, oy + 1.2, 35.2), (172.14, oy + 1.1, 32.3), (172.15, oy + 0.4, 32.0),
                           (172.15, 235.0, 32.0), (172.15, 225.0, 32.0), (172.15, 215.0, 32.0),
                           (172.15, 208.0, 32.0), (172.3, 205.8, 32.0), (172.7, 205.0, 32.1)],
         r=0.1, n=5, samples=2)


# --- towels -------------------------------------------------------------------------------

def hand_towel(b):
    """Tan hand towel pulled through the towel ring; PHOTO frames 84, 99, 109."""
    x, y, zc, r = RING
    zb = zc - r - 0.2
    cone(b, "towel_brown_a", (x - 2.3, y, zb), (x + 2.3, y, zb), 0.85, seg=10)
    back = drape(x - 2.3, x + 2.3, y - 0.8, zb, y - 1.05, 40.0, 7, 7, 0.12, 2.6, normal=(0, 1),
                 x0b=x - 3.0, x1b=x + 4.2, hem_wave=0.3)
    sheet(b, "towel_brown_a", back, (0, 1, 0), 0.35)
    front = drape(x - 2.3, x + 2.3, y + 0.8, zb, y + 1.1, 45.0, 5, 6, 0.3, 2.2, phase=1.3,
                  normal=(0, 1), x0b=x - 3.4, x1b=x + 1.9, hem_wave=0.4)
    sheet(b, "towel_brown_a", front, (0, 1, 0), 0.35)
    PROJ["towel_brown_a"] = ("plane", Vector((x + 4.5, 0, 39.5)), Vector((-1, 0, 0)), Vector((0, 0, 1)), 9.0, 15.0)


# --- toilet ---------------------------------------------------------------------------------

def trigger_spray(b, x, y, heading, body, neck, head, lbl, z0=TANK_TOP):
    """32 oz trigger-spray bottle: wide side and label facing `heading` (deg, 0 = east)."""
    ol = rrect(2.5, 4.0, 0.6)
    sh = rrect(2.0, 2.6, 0.8)
    nk = circle(0.65, len(ol))
    loft(b, [body, body, neck], [(ol, z0), (ol, z0 + 6.8), (sh, z0 + 7.6), (nk, z0 + 8.4)],
         c=(x, y), heading=heading)
    cone(b, neck, (x, y, z0 + 8.4), (x, y, z0 + 9.0), 0.65, seg=12)
    box(b, head, (x, y, z0 + 9.0), (3.2, 1.3, 1.5), heading=heading, bevel=0.35, local=(0.4, 0.0))
    box(b, head, (x, y, z0 + 9.3), (0.6, 0.9, 0.8), heading=heading, bevel=0.15, local=(2.2, 0.0))
    box(b, head, (x, y, z0 + 7.9), (0.4, 0.7, 1.2), heading=heading, bevel=0.12, local=(1.2, 0.0))
    label(b, lbl, (x, y, z0 + 1.0), heading, 2.9, 5.2, 1.26)


def toilet_top(b):
    # three cleaner sprays south of the flush button (PHOTO frames 151-155, 200-207)
    trigger_spray(b, 179.4, 261.2, 0.0, "s1_body", "s1_head", "s1_head", "lbl_s1")
    trigger_spray(b, 176.5, 261.9, 5.0, "s2_body", "s2_neck", "s2_head", "lbl_s2")
    trigger_spray(b, 173.75, 263.8, 0.0, "s3_body", "s3_head", "s3_head", "lbl_s3")
    # bamboo paper-towel stand with a roll and a hanging sheet (PHOTO frames 153, 205, 206)
    x, y = 176.4, 273.0
    cone(b, "bamboo", (x, y, TANK_TOP), (x, y, TANK_TOP + 0.6), 3.2, seg=20)
    cone(b, "bamboo", (x, y, TANK_TOP + 0.6), (x, y, TANK_TOP + 11.8), 0.45, seg=8)
    sphere(b, "bamboo", (x, y, TANK_TOP + 12.4), 0.85)
    z0, z1, R = TANK_TOP + 0.7, TANK_TOP + 11.5, 2.2
    cone(b, "ptowel", (x, y, z0), (x, y, z1), R, seg=18, cap="ptowel_end")
    PROJ["ptowel_end"] = ("disc",)
    a = math.radians(40)                                   # the sheet leaves the roll at NE
    cA, sA = math.cos(a), math.sin(a)
    tng = Vector((sA, -cA, 0))
    grid = []
    rows, cols = 7, 4
    for i in range(rows):
        s = i / (rows - 1)
        z = z1 - 0.3 - (z1 - 0.3 - (z0 + 0.1)) * s
        width = 1.0 + 3.6 * s
        row = []
        for j in range(cols):
            u = j / (cols - 1) * width
            p = Vector((x + (R + 0.08) * cA, y + (R + 0.08) * sA, z)) + tng * u + \
                Vector((cA, sA, 0)) * (0.35 * u * s)
            row.append(tuple(p))
        grid.append(row)
    sheet(b, "ptowel", grid, (cA, sA, 0), 0.08)


def tp_rack(b):
    """Chrome wire rack hooked on the tank's south side holding three toilet rolls
    (PHOTO frames 111, 153, 156-166). Rolls SPEC 4.4 dia x 4.0, axis east-west."""
    y, xw, xe = 255.7, 172.9, 177.3
    for z in (18.3, 22.8, 27.3):
        cone(b, "paper", (173.1, y, z), (177.1, y, z), 2.2, seg=16, cap="tp_end")
    PROJ["tp_end"] = ("disc",)
    ys, yn, zb, zt = 253.3, 258.1, 15.9, 30.0
    for x in (xw, xe):
        wire_loop(b, "chrome", [(x, ys, zb), (x, yn, zb), (x, yn, zt), (x, ys, zt)])
    for yy in (254.7, 256.7):
        cone(b, "chrome", (xe + 0.1, yy, zb), (xe + 0.1, yy, zt), 0.08, seg=5)
    for yy in (ys, yn):
        cone(b, "chrome", (xw, yy, zb), (xe, yy, zb), 0.09, seg=5)
    for x in (173.8, 176.4):
        cord(b, "chrome", [(x, yn, zt - 0.5), (x, yn, 31.2), (x, 258.8, 31.35), (x, 259.4, 31.05)],
             r=0.09, n=5, samples=2)
        cone(b, "chrome", (x, yn, zt), (x, yn, zt - 0.6), 0.09, seg=5)


# --- floor ------------------------------------------------------------------------------------

def bath_mat(b):
    """Blue-grey shag mat in front of the vanity; PHOTO frames 70-79, 109-119 rectified on the
    floor (x 193.2..213.7, y 207..243, +-2)."""
    cx, cy, w, d = 203.45, 225.0, 20.5, 36.0
    ol = rrect(w, d, 1.8, seg=3)
    inset = rrect(w - 0.7, d - 0.7, 1.5, seg=3)
    loft(b, ["mat_side", "mat_side"], [(ol, 0.0), (ol, 0.45), (inset, 0.75)], c=(cx, cy),
         top_region="mat_top")
    PROJ["mat_top"] = ("plane", Vector((cx - w / 2, cy - d / 2, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)), w, d)


def wastebasket(b):
    """Small tapered white bin with a white liner bag cuffed over the rim, under the towel
    bar against the north wall; PHOTO frames 213-231 (x +-3)."""
    x, y = 222.5, 281.6
    bot = rrect(7.8, 5.8, 1.5)
    rim = rrect(9.0, 6.8, 1.85)
    cuff0 = rrect(9.2, 7.0, 1.9)
    cuff1 = rrect(9.4, 7.2, 1.95)
    in0 = rrect(8.7, 6.5, 1.75)
    in1 = rrect(7.9, 5.8, 1.5)
    loft(b, ["bin_white", "bin_white", "bag_white", "bag_white", "bag_white"],
         [(bot, 0.0), (rim, 9.0), (cuff0, 9.0), (cuff1, 10.5), (in0, 10.5), (in1, 5.5)],
         c=(x, y), top_region="bag_white")
    for (dx, dy, dz, r, reg) in ((-1.5, 0.6, 6.4, 1.4, "trash_tan"), (1.4, -0.4, 6.6, 1.6, "bag_white"),
                                 (0.3, 1.2, 7.4, 1.1, "trash_tan")):
        sphere(b, reg, (x + dx, y + dy, dz), r, seg=7, rings=5, scale=(1.0, 0.8, 0.6))


def pedal_bin(b):
    """Round stainless step bin in the corner between the north wall and the tub apron,
    black pedal toward the room; PHOTO frames 216-225, 263-266."""
    x, y, r = 240.3, 278.3, 4.3
    cone(b, "black", (x, y, 0.0), (x, y, 0.4), r + 0.05, seg=20)
    cone(b, "stainless", (x, y, 0.4), (x, y, 11.2), r, seg=20)
    cone(b, "stainless", (x, y, 11.2), (x, y, 11.8), r + 0.05, r - 0.4, seg=20)
    cone(b, "stainless", (x, y, 11.8), (x, y, 12.0), r - 0.4, r - 1.3, seg=20)
    ang = math.degrees(math.atan2(-0.15, -1.0))
    box(b, "black", (x, y, 0.25), (2.0, 2.8, 0.5), heading=ang, bevel=0.2, local=(r + 0.6, 0.0))
    box(b, "black", (x, y, 10.8), (0.8, 2.2, 1.1), heading=ang, bevel=0.2, local=(-r - 0.2, 0.0))


def brush_and_plunger(b):
    """Toilet brush and plunger in their white holders in the corner between the tank and
    the north wall; PHOTO frames 168-199, floor rectified in fl181.png."""
    x, y = 178.8, 282.2                                    # brush holder
    cone(b, "holder_white", (x, y, 0.0), (x, y, 5.6), 2.0, 1.95, seg=16)
    cone(b, "lbl_holder", (x, y, 1.5), (x, y, 4.2), 2.03, 1.99, seg=16)
    PROJ["lbl_holder"] = ("wrap", (x, y), 1.5, 4.2, 0.0)
    cone(b, "holder_white", (x, y, 5.6), (x, y, 5.9), 1.95, 1.7, seg=16)
    cone(b, "bristle", (x, y, 5.55), (x, y, 5.85), 1.6, seg=16)
    cone(b, "handle_taupe", (x, y, 5.85), (x, y, 6.2), 0.6, 0.35, seg=8)
    cone(b, "handle_taupe", (x, y, 6.2), (x - 0.1, y + 0.1, 15.8), 0.3, 0.28, seg=8)
    cone(b, "handle_taupe", (x - 0.1, y + 0.1, 15.8), (x - 0.1, y + 0.1, 17.0), 0.28, 0.55, seg=8)
    cone(b, "handle_taupe", (x - 0.1, y + 0.1, 17.0), (x - 0.1, y + 0.1, 17.2), 0.55, 0.45, seg=8)
    x, y = 174.5, 282.0                                    # plunger caddy
    cone(b, "holder_white", (x, y, 0.0), (x, y, 0.6), 2.6, seg=16)
    cone(b, "holder_white", (x, y, 0.6), (x, y, 5.5), 2.6, 2.2, seg=16)
    cone(b, "holder_white", (x, y, 5.5), (x, y, 6.3), 2.2, 1.1, seg=16)
    cone(b, "handle_taupe", (x, y, 6.2), (x + 0.1, y - 0.1, 22.5), 0.35, 0.3, seg=8)
    cone(b, "handle_taupe", (x + 0.1, y - 0.1, 22.5), (x + 0.1, y - 0.1, 23.8), 0.3, 0.6, seg=8)
    cone(b, "handle_taupe", (x + 0.1, y - 0.1, 23.8), (x + 0.1, y - 0.1, 24.0), 0.6, 0.5, seg=8)


# --- build / texture ----------------------------------------------------------------------------

def build(coll):
    PROJ.clear()
    b = common.Builder(REGIONS)
    toothbrush(b)
    teal_jar(b)
    mouthwash(b)
    soap_dispenser(b)
    organizer(b)
    brush_cup(b)
    hand_mirror(b)
    counter_jars(b)
    north_counter(b)
    front_counter(b)
    hair_dryer(b)
    hand_towel(b)
    toilet_top(b)
    tp_rack(b)
    bath_mat(b)
    wastebasket(b)
    pedal_bin(b)
    brush_and_plunger(b)
    return [b.to_object(NAME, coll)]


def _project(ob):
    """Overwrite UVs for regions with a registered projection (labels, towels, mat, ends)."""
    me = ob.data
    uvl = me.uv_layers["UVMap"]
    regions = [mt.name.split(".")[0] for mt in me.materials]
    for p in me.polygons:
        reg = regions[p.material_index]
        spec = PROJ.get(reg)
        if spec is None:
            continue
        u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, reg)
        cos = [me.vertices[me.loops[li].vertex_index].co / IN for li in p.loop_indices]
        kind = spec[0]
        if kind == "plane":
            _, o, ua, va, w, h = spec
            fu = [(c - o).dot(ua) / w for c in cos]
            fv = [(c - o).dot(va) / h for c in cos]
        elif kind == "wrap":
            _, (cx, cy), z0, z1, front = spec
            if abs(p.normal.z) > 0.9:                       # sleeve rims: background colour
                fu = [0.03] * len(cos)
                fv = [0.5] * len(cos)
            else:
                fu = [((math.atan2(c.y - cy, c.x - cx) - math.radians(front) + math.pi)
                       % (2 * math.pi)) / (2 * math.pi) for c in cos]
                if max(fu) - min(fu) > 0.5:
                    fu = [min(1.0, f + 1.0) if f < 0.5 else f for f in fu]
                fv = [(c.z - z0) / (z1 - z0) for c in cos]
        else:                                               # "disc": each face its own disc
            cen = sum(cos, Vector()) / len(cos)
            rad = max((c - cen).length for c in cos) or 1.0
            n = p.normal
            a = n.orthogonal().normalized()
            bb = n.cross(a).normalized()
            fu = [0.5 + (c - cen).dot(a) / (2 * rad) for c in cos]
            fv = [0.5 + (c - cen).dot(bb) / (2 * rad) for c in cos]
        for li, fu_, fv_ in zip(p.loop_indices, fu, fv):
            fu_ = min(1.0, max(0.0, fu_))
            fv_ = min(1.0, max(0.0, fv_))
            uvl.data[li].uv = (u0 + fu_ * (u1 - u0), v0 + fv_ * (v1 - v0))


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    # preview only: show the clear plastic as see-through in the Blender renders
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    common.atlas_uvs(ob, ATLAS)
    _project(ob)
    common.collapse_materials(ob, {r: (clear if r == CLEAR else mat) for r in REGIONS})
