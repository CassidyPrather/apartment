"""Bedroom fixtures: the small wall/ceiling things of the bedroom, all in one package.
  - vertical vane blinds in the bedroom's south window
  - two tracking base stations on swivel wall brackets (cable run down the wall)
  - ceiling smoke detector, thermostat on the center wall
  - all the wall art, textured from rectified capture photos (the six-panel flower print from
    Cassidy's close-up photo IMG_1515)
  - the six keychains by the plushes, modelled: acrylic slabs, metal rings/clasps/chains, a
    plush ball, wall pins

Source of truth: scripted, positions from the bedroom LiDAR survey (Reference/bedroom_survey).
Frame: PLAN coordinates. Origin = plan (0, 0, 0), +X east, +Y north, Z up, metres; the package
goes on a marker at (0, 0, 0) with no rotation. Wall pieces are built in a wall frame:
u = the plan coordinate along the wall, d = distance out from the wall surface into the room.

Dimensions (inches, plan):
  wall surfaces: center wall east face x 138.75, south y 0, east x 274.6, back y 158.4,
    closet south wall south face y 130.35, closet front wall west face x 247.7   S (survey)
  window x 171.25..205.45, sill 26.5, head 85                    M / layout
  blinds: carrier y -1.5 (inside the recess), headrail z 83.5..85, vanes 3.5 wide,
    to 0.75 above the sill, near-closed (8 deg)                  SCAN depth / EST
  base station SW centre (139.5, 25, 97), closet (260, 129.8, 96)  S +-2
  base station 3.4 x 3.4 x 3.0, bracket arm 2.0                  EST
  smoke detector (166, 142), 6 dia x 2, ceiling z 108            S
  thermostat y 110..114, z 45.5..50.5, 1.1 deep                  A (survey z 45..51)
  wall art: every piece's bounds are in ART below, measured on capture frames rectified onto
    the known wall plane (Reference/bedroom_fixtures_work/rect.py, final.py), +-0.5   SCAN
  frame widths: center 1.4 black, tree 0.4 black, south 1.1 white                   SCAN
  back wall six-panel flower print, unframed paper 19 x 13 (A3+; the capture gives 18.8 x 12.3
    and IMG_1515's aspect 1.46 = 19/13), centred on the capture at x 183.1, z 64.0 ->
    x 173.6..192.6, z 57.5..70.5; black band 16.9 x 5.5 inside it                SPEC / SCAN
  east-wall prints/cards by the plushes: positions re-checked on Cassidy's IMG_1517 through a
    homography anchored on the roller-skate poster (y 37.15..45.75, z 59.85..71.0); the cards
    agree with the capture within 0.2; the kraft card is 2.0 x 3.5 (y 43.15..45.15,
    z 55.7..59.2) and the sword print 8 x 10 (y 27.25..35.25, z 56.4..66.4)       PHOTO
  keychains (y 13..24, z 64..77): traced from IMG_1520 at 185 px/in, fitted to the capture's
    charm positions (residual < 0.5); outlines/rings/pins in charms.py; acrylic 3 mm (0.12),
    split rings 1.0..1.1 dia, wire 1.8 mm, plush ball 3.3 dia squashed to 2.6 deep   PHOTO / EST
Artwork textures are the real pictures, rectified from the capture photos, except: the holiday
tree is the artist's clean original file (Reference/CorVous_commission17.jpg, centre-cropped to
the frame opening's 15.8 x 19.4), the moon print is rectified from Cassidy's close-up IMG_1504
(white border kept, balanced off it), the flower print from IMG_1515, and the prints/cards and
charm faces by the plushes from IMG_1517..1521 (balanced off the wall / paper white). Signatures
are kept (Cassidy's request); only the space poster's game logo is blanked (see final.py).
"""

import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

import common


def m(inches):
    return inches * 0.0254


NAME = "bedroom_fixtures"

# wall: (axis index of the normal, surface coordinate, outward sign, planar axis name)
WALLS = {
    "center_e": (0, 138.75, +1, "+X"),
    "south": (1, 0.0, +1, "+Y"),
    "east": (0, 274.6, -1, "-X"),
    "back": (1, 158.4, -1, "-Y"),
    "closet_s": (1, 130.35, -1, "-Y"),
    "closet_fw": (0, 247.7, -1, "-X"),
}

import layout  # noqa: E402  (package dir is on sys.path during builds)
import charms as CH  # noqa: E402

ATLAS = layout.ATLAS
REGIONS = list(ATLAS["regions"])
CLEAR_ALPHA = 0.3
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque"},
             NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": CLEAR_ALPHA}}
CLEAR_REGIONS = {"ch_clear"}
COLLIDER = "none"
STATIC = True
VIEWS = [("east_wall", 270, 8, 0.45), ("south_wall", 0, 8, 0.45), ("north_side", 180, 10, 0.45)]

PLANAR = {}

# (region, wall, u0, u1, z0, z1, style)   style: paper | frame_black | frame_thin | frame_white
# Bounds re-measured on the rectified capture frames (Reference/bedroom_fixtures_work/final).
ART = [
    ("art_center", "center_e", 67.7, 82.1, 53.7, 71.0, "frame_black"),
    ("art_south", "south", 162.0, 169.8, 58.2, 69.7, "frame_white"),
    ("card_s", "south", 156.75, 160.0, 65.4, 70.25, "paper"),
    ("art_flowers", "back", 173.6, 192.6, 57.5, 70.5, "paper"),
    ("art_moon", "east", 91.75, 117.0, 52.0, 67.1, "paper"),
    ("art_tree", "east", 70.8, 87.4, 51.3, 71.5, "frame_thin"),
    ("mid_poster", "east", 37.15, 45.75, 59.85, 71.0, "paper"),
    ("card_a", "east", 45.9, 50.1, 52.25, 58.6, "paper"),
    ("card_b", "east", 45.6, 50.25, 45.0, 51.15, "paper"),
    ("card_c", "east", 43.15, 45.15, 55.7, 59.2, "paper"),          # kraft card, 2 x 3.5 (IMG_1517)
    ("card_d", "east", 39.5, 43.6, 48.5, 54.65, "paper"),
    ("drawing_bw", "east", 27.25, 35.25, 56.4, 66.4, "paper"),      # 8 x 10 print (IMG_1517/1519)
    ("corner_poster", "east", 6.0, 12.75, 67.5, 77.75, "paper"),
    ("art_space", "closet_s", 248.4, 266.5, 65.5, 89.75, "paper"),   # above the bag hooks (z 61.5)
    ("art_purple", "closet_fw", 137.3, 153.8, 85.8, 98.1, "paper"),
]
def plan_box(wall, u, d, z):
    """(u0,u1),(d0,d1),(z0,z1) in a wall frame -> plan lo/hi in metres."""
    ax, s0, sign, _ = WALLS[wall]
    dd = sorted((s0 + sign * d[0], s0 + sign * d[1]))
    if ax == 0:
        lo, hi = (dd[0], u[0], z[0]), (dd[1], u[1], z[1])
    else:
        lo, hi = (u[0], dd[0], z[0]), (u[1], dd[1], z[1])
    return tuple(map(m, lo)), tuple(map(m, hi))


def panel(b, region, wall, u, d, z, side_region=None, planar=False):
    """Wall-frame box; with side_region, only the face toward the room keeps `region`."""
    lo, hi = plan_box(wall, u, d, z)
    faces = b.box(region, lo, hi)
    if side_region:
        ax, _, sign, axis = WALLS[wall]
        n = Vector((0, 0, 0))
        n[ax] = sign
        for f in faces:
            f.normal_update()
            if f.normal.dot(n) < 0.9:
                f.material_index = b.idx(side_region)
    if planar:
        ax, _, sign, axis = WALLS[wall]
        # u bounds in the direction the planar projection reads left-to-right
        ub = (m(u[0]), m(u[1])) if axis in ("+X", "-Y") else (-m(u[1]), -m(u[0]))
        PLANAR[region] = (axis, ub, (m(z[0]), m(z[1])))
    return faces


def art(b, region, wall, u0, u1, z0, z1, style):
    if style == "paper":
        panel(b, region, wall, (u0, u1), (0.0, 0.06), (z0, z1), "paper", True)
        return
    fw, dep, fr = {"frame_black": (1.4, 0.8, "frame_black"), "frame_thin": (0.4, 0.6, "frame_black"),
                   "frame_white": (1.1, 0.8, "frame_white")}[style]
    panel(b, fr, wall, (u0, u1), (0.0, dep), (z0, z1))
    # the photo covers everything inside the frame (mat and print), just proud of the frame
    panel(b, region, wall, (u0 + fw, u1 - fw), (dep - 0.2, dep + 0.03), (z0 + fw, z1 - fw), fr, True)


def charms(b):
    for k, reg in (("candy", "ch_candy"), ("boba", "ch_boba"), ("tall", "ch_tall"), ("hgroup", "ch_hgroup")):
        a = CH.ACRYLIC[k]
        acrylic(b, a["outer"], a["print"], reg, a["box"])
    # the brand charm, replaced by a plain pink acrylic heart (ring on top)
    h = CH.HEART
    outer = heart_outline(h["centre"], h["w"], h["h"])
    hu = [p[0] for p in outer]
    hz = [p[1] for p in outer]
    acrylic(b, outer, inset(outer, 0.1), "ch_pinkheart", (min(hu), max(hu), min(hz), max(hz)))
    plush(b)
    metal = {"candy": "rose_gold", "boba": "rose_gold", "plush": "gold", "tall": "nickel"}
    for k, (kind, c, r, stem) in CH.CLASPS.items():
        clasp(b, metal[k], kind, c, r, stem)
    for k, (c, r) in CH.RINGS.items():
        reg = "rose_gold" if k.startswith(("candy", "boba")) else "nickel"
        big = r > 0.2
        ring(b, reg, c, r, seg=10 if big else 5, wire=WIRE if big else 0.022, flat=big or k.endswith("jr2"))
    for k, pts in CH.CHAINS.items():
        if k == "plush":
            ball_chain(b, "gold", pts[0], pts[1])
        elif k == "tall":
            chain(b, "nickel", CH.CLASPS["tall"][3][1], pts[1])
        else:
            chain(b, "nickel", pts[0], pts[1], link=0.32 if k == "hgroup" else 0.25)
    for p in CH.PINS.values():
        pin(b, p)


# Keychain charms (east wall, y 13..24, z 64..77): real geometry, traced from Cassidy's close-up
# IMG_1520 (charms.py holds the outlines and ring/chain/pin positions). Acrylic charms are 3 mm
# slabs following their cut line, clear except the printed area on the front; rings, clasps and
# chains are modelled metal; the plush is a squashed ball on a ball chain; each hangs from a small
# wall pin. The brand charm (a clothing label's bunny-skull logo) is replaced by a plain pink
# acrylic heart of the same size.

EAST = 274.6
ACR_D = (0.08, 0.2)          # acrylic slab, inches out from the wall (3 mm)
RING_D = 0.12                # ring / chain centre-plane depth
WIRE = 0.035                 # ring wire radius (about 1.8 mm dia)


def wv(u, d, z):
    """east-wall frame (u = plan y, d = out from the wall, z) -> plan metres"""
    return Vector((m(EAST - d), m(u), m(z)))


def acrylic(b, outer, printed, face_region, box):
    """Clear slab along `outer`; its front face is split into the printed area (opaque,
    textured) and a clear border ring. outer/printed: matching point lists (u, z)."""
    bm = b.bm
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(outer, outer[1:] + outer[:1]))
    if area < 0:
        outer, printed = list(reversed(outer)), list(reversed(printed))
    d0, d1 = ACR_D
    back = [bm.verts.new(wv(u, d0, z)) for u, z in outer]
    front = [bm.verts.new(wv(u, d1, z)) for u, z in outer]
    inner = [bm.verts.new(wv(u, d1, z)) for u, z in printed]
    n = len(outer)
    faces = [bm.faces.new(back)]
    for i in range(n):
        k = (i + 1) % n
        faces.append(bm.faces.new((back[i], back[k], front[k], front[i])))
        faces.append(bm.faces.new((front[i], front[k], inner[k], inner[i])))
    b._tag(faces, "ch_clear")
    pf = bm.faces.new(list(reversed(inner)))
    b._tag([pf], face_region)
    u0, u1, z0, z1 = box
    PLANAR[face_region] = ("-X", (-m(u1), -m(u0)), (m(z0), m(z1)))


def wire_loop(b, region, path, radius, sides=4):
    """closed metal loop along a list of plan-metre points"""
    prof = [(radius * math.cos(2 * math.pi * k / sides), radius * math.sin(2 * math.pi * k / sides))
            for k in range(sides)]
    b.sweep(region, path, prof, up=(1, 0, 0), closed=True)


def ring(b, region, c, r, d=RING_D, seg=12, wire=WIRE, flat=True):
    """split / jump ring: a torus in the wall plane (flat) or edge-on to it"""
    if flat:
        path = [wv(c[0] + r * math.cos(2 * math.pi * k / seg), d, c[1] + r * math.sin(2 * math.pi * k / seg))
                for k in range(seg)]
    else:
        path = [wv(c[0], d + r * math.cos(2 * math.pi * k / seg), c[1] + r * math.sin(2 * math.pi * k / seg))
                for k in range(seg)]
    wire_loop(b, region, path, m(wire), sides=3)


def chain(b, region, p0, p1, link=0.25, wire=0.02):
    """diamond links from p0 down to p1, alternating flat / edge-on"""
    L = math.dist(p0, p1)
    n = max(1, round(L / link))
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        a = (p0[0] + (p1[0] - p0[0]) * t0, p0[1] + (p1[1] - p0[1]) * t0)
        c = (p0[0] + (p1[0] - p0[0]) * t1, p0[1] + (p1[1] - p0[1]) * t1)
        mu, mz = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
        w = L / n * 0.3
        if i % 2 == 0:
            path = [wv(a[0], RING_D, a[1]), wv(mu + w, RING_D, mz), wv(c[0], RING_D, c[1]), wv(mu - w, RING_D, mz)]
        else:
            path = [wv(a[0], RING_D, a[1]), wv(mu, RING_D + w, mz), wv(c[0], RING_D, c[1]), wv(mu, RING_D - w, mz)]
        wire_loop(b, region, path, m(wire), sides=3)


def ball_chain(b, region, p0, p1, pitch=0.12, r=0.035):
    L = math.dist(p0, p1)
    n = max(2, round(L / pitch))
    for i in range(n + 1):
        t = i / n
        u, z = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        res = bmesh.ops.create_icosphere(b.bm, subdivisions=0, radius=m(r))
        bmesh.ops.translate(b.bm, vec=wv(u, RING_D + 0.02, z), verts=res["verts"])
        b._tag(list({f for v in res["verts"] for f in v.link_faces}), region)


def clasp(b, region, kind, c, r, stem):
    """heart / star shaped clasp loop plus the lobster body down to the jump ring"""
    pts = []
    if kind == "heart_clasp":
        for k in range(14):
            t = 2 * math.pi * k / 14
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((c[0] - x / 17 * r, c[1] + y / 17 * r))
    elif kind.startswith("star_clasp"):
        for k in range(10):
            a = math.pi / 2 + math.pi * k / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)))
    if pts:
        wire_loop(b, region, [wv(u, RING_D, z) for u, z in pts], m(0.025), sides=3)
    (u0, z0), (u1, z1) = stem
    uc, zc = (u0 + u1) / 2, (z0 + z1) / 2
    h, w = abs(z0 - z1) / 2 + 0.03, 0.06
    lo, hi = wv(uc + w, RING_D + w, zc - h), wv(uc - w, RING_D - w, zc + h)
    b.box(region, tuple(min(lo[i], hi[i]) for i in range(3)), tuple(max(lo[i], hi[i]) for i in range(3)))


def pin(b, p):
    """small wall pin: a short stub standing out from the wall under the ring"""
    u, z = p
    b.cylinder("pin", wv(u, 0.22, z), m(0.07), m(0.44), axis="X", segments=5)


def heart_outline(c, w, h, n=24):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((c[0] - x / 32 * w, c[1] + (y + 2.5) / 30 * h))
    return pts


def inset(pts, d):
    """offset a closed outline inward by d (miter, capped), same vertex count"""
    pts = list(pts)
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(pts, pts[1:] + pts[:1]))
    s = 1.0 if area > 0 else -1.0
    n, out = len(pts), []
    for i in range(n):
        a, p, c = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        e1, e2 = (p - a).normalized(), (c - p).normalized()
        n1, n2 = Vector((-e1.y, e1.x)) * s, Vector((-e2.y, e2.x)) * s
        nm = n1 + n2
        nm = n1 if nm.length < 1e-6 else nm.normalized()
        k = min(2.0, 1.0 / max(0.3, nm.dot(n1)))
        q = p + nm * d * k
        out.append((q.x, q.y))
    return out


def plush(b):
    c, r = CH.PLUSH["centre"], CH.PLUSH["radius"]
    depth = r * 0.78
    res = bmesh.ops.create_uvsphere(b.bm, u_segments=12, v_segments=7, radius=1.0)
    verts = res["verts"]
    # squashed toward the wall: radius r in the wall plane, `depth` out from it
    mat = Matrix.Translation(wv(c[0], depth + 0.02, c[1])) @ Matrix.Diagonal((m(depth), m(r), m(r * 0.97), 1.0))
    bmesh.ops.transform(b.bm, matrix=mat, verts=verts)
    b._tag(list({f for v in verts for f in v.link_faces}), "ch_plush")
    u0, u1, z0, z1 = CH.PLUSH["box"]
    PLANAR["ch_plush"] = ("-X", (-m(u1), -m(u0)), (m(z0), m(z1)))
    # the sewn-in loop at the top that the ball chain passes through
    ring(b, "gold", (c[0], c[1] + r + 0.02), 0.08, d=0.35, seg=6, wire=0.02, flat=False)


# --- blinds (south window, as window_blinds does it) --------------------------------

WIN_X = (171.25, 205.45)
SILL, HEAD = 26.5, 85.0
VANE_W, VANE_PITCH, VANE_T = 3.5, 3.0, 0.06
TILT = 8.0


def south_box(b, region, x, y, z, tilt=0.0):
    (x0, x1), (y0, y1), (z0, z1) = x, y, z
    c = Vector((m((x0 + x1) / 2), m((y0 + y1) / 2), m((z0 + z1) / 2)))
    hx, hy, hz = m(x1 - x0) / 2, m(y1 - y0) / 2, m(z1 - z0) / 2
    mat = Matrix.Translation(c) @ Matrix.Rotation(math.radians(tilt), 4, "Z")
    b.box(region, (-hx, -hy, -hz), (hx, hy, hz), matrix=mat)


def blinds(b):
    dc = -1.5
    u0, u1 = WIN_X[0] + 0.25, WIN_X[1] - 0.25
    south_box(b, "rail", (u0, u1), (-2.6, 0.2), (83.5, HEAD))
    south_box(b, "carrier", (u0 + 0.5, u1 - 0.5), (dc - 0.3, dc + 0.3), (83.2, 83.5))
    n = int(round((u1 - u0 - VANE_W) / VANE_PITCH)) + 1
    pitch = (u1 - u0 - VANE_W) / (n - 1)
    zb, zv = SILL + 0.75, 83.2
    for i in range(n):
        cu = u0 + VANE_W / 2 + i * pitch
        dd = dc + (0.04 if i % 2 else -0.04)
        south_box(b, "vane", (cu - VANE_W / 2, cu + VANE_W / 2), (dd - VANE_T / 2, dd + VANE_T / 2),
                  (zb, zv), tilt=TILT)
    # tilt wand and pull chain at the west end, room side
    south_box(b, "wand", (u0 + 0.6, u0 + 0.95), (-0.2, 0.15), (zv - 30.0, zv))


# --- base stations, smoke detector, thermostat -------------------------------------

# (wall, surface point (x, y), centre z, aim target in plan, cable bottom z)
BASE_STATIONS = [
    ("center_e", (139.5, 25.0), 97.0, (205.0, 80.0, 40.0), 30.0),
    ("closet_s", (260.0, 129.8), 96.0, (205.0, 70.0, 40.0), 40.0),
]


def base_station(b, wall, p, zc, target, cable_z):
    ax, s0, sign, _ = WALLS[wall]
    n = Vector((0, 0, 0))
    n[ax] = sign
    wp = Vector((p[0], p[1], zc))
    wp[ax] = s0
    # wall plate and arm
    along = 0 if ax == 1 else 1
    u = wp[along]
    panel(b, "bracket", wall, (u - 0.8, u + 0.8), (0.0, 0.3), (zc - 1.9, zc + 0.7))
    arm0 = wp + n * 0.3 + Vector((0, 0, -0.6))
    arm1 = wp + n * 2.2 + Vector((0, 0, -0.6))
    lo = Vector([min(arm0[i], arm1[i]) for i in range(3)]) - Vector((0.3, 0.3, 0.3))
    hi = Vector([max(arm0[i], arm1[i]) for i in range(3)]) + Vector((0.3, 0.3, 0.3))
    for i in range(3):
        if i != ax:
            lo[i], hi[i] = (arm0[i] - 0.3, arm0[i] + 0.3)
    b.box("bracket", tuple(map(m, lo)), tuple(map(m, hi)))
    # box centre out from the wall, aimed at the room (local -Y = face)
    c = wp + n * 4.0
    f = Vector(target) - c
    yaw = math.atan2(f.x, -f.y)
    pitch = math.atan2(-f.z, Vector((f.x, f.y)).length)
    mat = (Matrix.Translation(c * 0.0254) @ Matrix.Rotation(yaw, 4, "Z")
           @ Matrix.Rotation(pitch, 4, "X"))
    w, h, d = m(3.4) / 2, m(3.4) / 2, m(3.0) / 2
    b.box("bs_body", (-w, -d + m(0.2), -h), (w, d, h), bevel=m(0.25), segments=1, matrix=mat)
    b.box("bs_face", (-w + m(0.2), -d, -h + m(0.2)), (w - m(0.2), -d + m(0.25), h - m(0.2)), matrix=mat)
    # cable from under the box down the wall
    panel(b, "cable", wall, (u + 0.9, u + 1.15), (0.0, 0.25), (cable_z, zc - 1.0))


def smoke_detector(b):
    b.cylinder("smoke", (m(166.0), m(142.0), m(107.4)), m(3.0), m(1.2), segments=20)
    b.cylinder("smoke", (m(166.0), m(142.0), m(106.5)), m(2.4), m(0.7), segments=20)


def thermostat(b):
    panel(b, "thermo", "center_e", (110.0, 114.0), (0.0, 1.0), (45.5, 50.5))
    panel(b, "thermo_face", "center_e", (110.2, 113.8), (1.0, 1.1), (45.7, 50.3), "thermo", True)


def build(coll):
    PLANAR.clear()
    b = common.Builder(REGIONS)
    for a in ART:
        art(b, *a)
    charms(b)
    blinds(b)
    for bs in BASE_STATIONS:
        base_station(b, *bs)
    smoke_detector(b)
    thermostat(b)
    return [b.to_object(NAME, coll)]


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    # preview only: show the acrylic as see-through in the Blender renders
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    for ob in objs:
        common.atlas_uvs(ob, ATLAS, planar=dict(PLANAR))
        common.collapse_materials(ob, {r: (clear if r in CLEAR_REGIONS else mat) for r in REGIONS})
