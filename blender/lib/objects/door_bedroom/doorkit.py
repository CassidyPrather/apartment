"""Shared door parts for the door_* packages (hinged, pocket, bypass sliding, patio slider).

Source of truth: scripted. Everything is in inches here and converted with m() once, where
vertices are made. Local frame for every door package:
  - the opening runs along X, the wall thickness along Y, Z up from the finished floor;
  - the door's "front" faces -Y: a hinged leaf swings toward -Y;
  - hinged doors: origin on the floor at the hinge-side edge of the clear opening, on the
    wall's centreline; the opening extends to +X (hand=+1, hinge on the left seen from the
    front) or to -X (hand=-1, hinge on the right seen from the front);
  - sliding, pocket and patio doors: origin on the floor at the opening's centre.
The leaf of a hinged door is its own object with its origin on the hinge pin, so a later
pass can swing it (Unity rotates it about its local Z/up axis). Any "open" pose is baked
into the mesh so the export stays at rotation zero. Hardware that moves with a leaf is
built into the leaf; hardware fixed to the frame (the middle hinge knuckle, the jamb hinge
plate, pin tips, strike plates) stays in the frame object.

Hardware (read from IMG_1523, IMG_1498, IMG_1502 and the living/bedroom LiDAR frames):
  - 3.5 in square-corner butt hinges, three per door: a frame plate on the jamb, a leaf plate
    on the door's hinge edge, a 0.5 in barrel split into three knuckles (the middle one on
    the frame, the outer two on the leaf) and a button pin tip on top;
  - lever sets: a stepped round rose and a scroll ("tulip") lever that curls out of the
    rose, runs toward the hinge and flicks up at the tip (IMG_1523, IMG_1498);
  - knob sets: a stepped rose and a ball knob (IMG_1502); bifold mushroom knobs (IMG_1523);
  - latch faceplate and bolt on the leaf's latch edge, strike plate on the jamb;
  - deadbolt (entry): rose + thumb turn inside, rose + key cylinder outside, faceplate and
    strike (living capture frames 0/36).
Wear: every leaf's painted faces use the "leaf" atlas region, UV-mapped by leaf_uvs() so
u runs from the hinge (or far) edge to the handle edge and v from the leaf bottom to top.
textures.py paints faint hand smudges around the handle height on the handle edge and
scuffs/dings along the bottom rail there (IMG_1523, IMG_1498, living frame 48).

The shell (shell.py) already draws the casings on both wall faces and leaves the reveal as
bare drywall, so these packages add the jamb liner, stops, leaf and hardware only.
"""

import math

import bmesh
from mathutils import Matrix, Vector

import common

IN = 0.0254


def m(v):
    return v * IN


def mv(p):
    return tuple(m(c) for c in p)


# One shared 512 px atlas for every door package ("doors"). Flat finishes, plus the
# "leaf" region (the whole leaf face, with wear) and the entry door's blind and lite.
ATLAS = {
    "name": "doors",
    "size": 512,
    "regions": {
        "paint": (0, 0, 256, 256),        # white semi-gloss door/jamb paint
        "nickel": (256, 0, 128, 128),     # brushed nickel knobs, hinges
        "bronze": (384, 0, 128, 128),     # dark lever set and hinges (bedroom)
        "vinyl": (256, 128, 128, 128),    # patio door frame (white vinyl, EST)
        "dark": (384, 128, 128, 128),     # weatherstrip, track slots, pulls
        "glass": (0, 256, 128, 128),      # patio glazing (own transparent material)
        "aluminum": (128, 256, 128, 128),  # closet track
        "leaf": (256, 256, 256, 256),     # leaf faces: paint + smudges/scuffs (leaf_uvs)
        "brass": (0, 384, 128, 128),      # entry lever set and deadbolt (polished brass)
        "slat": (128, 384, 64, 128),      # entry door's 2 in blind: slats, rails, cords
        "lite": (192, 384, 64, 128),      # entry door's lite glass (opaque, dark, glossy)
    },
}
REGIONS = list(ATLAS["regions"])
OPAQUE = [r for r in REGIONS if r != "glass"]

MATERIALS = {
    "doors": {"atlas": "doors", "mode": "opaque", "tiled": False},
}
MATERIALS_GLASS = {
    "doors_glass": {"atlas": "doors", "mode": "transparent", "alpha": 0.25, "tiled": False},
}

# Common door hardware and clearances (inches). All EST (standard US interior doors).
JAMB_T = 0.5          # EST jamb liner thickness inside the opening
GAP = 0.125           # EST leaf-to-jamb gap
FLOOR_GAP = 0.75      # EST undercut above the floor (carpet)
STOP_W, STOP_T = 1.25, 0.5   # EST door stop
KNOB_Z = 36.0         # EST knob/lever centre height
BACKSET = 2.375       # EST knob centre from the leaf's latch edge
HINGE_H = 3.5         # EST 3.5 in butt hinge (IMG_1523: square corners)
HINGE_W = 1.4         # EST visible width of each hinge plate
BARREL_R = 0.25       # EST
DEADBOLT_UP = 5.5     # EST standard deadbolt centre above the latch

# Leaf UV mapping for the wear texture, filled in by register_leaf() during build():
# object name -> (x_zero, x_one, z0, z1, pin_xy, angle_deg, u_scale), inches.
LEAF_UV = {}


def builder():
    return common.Builder(REGIONS)


def box(b, region, lo, hi, bevel=0.0, segments=1, matrix=None):
    lo, hi = [min(a, c) for a, c in zip(lo, hi)], [max(a, c) for a, c in zip(lo, hi)]
    return b.box(region, mv(lo), mv(hi), bevel=m(bevel), segments=segments, matrix=matrix)


def cyl(b, region, c, r, depth, axis="Y", seg=12, bevel=0.0):
    return b.cylinder(region, Vector(mv(c)), m(r), m(depth), axis=axis, segments=seg,
                      bevel=m(bevel))


def lathe(b, region, c, profile, axis="Y", sign=1, seg=12):
    """Revolve profile [(radius, distance along the axis), ...] (inches) about an axis
    through c. axis "Y" runs out of a door face (sign -1 = toward -Y), "Z" is vertical.
    A radius of 0 closes that end to a point; otherwise the ends get flat caps."""
    bm = b.bm
    ax = {"Y": Vector((0, sign, 0)), "Z": Vector((0, 0, sign)), "X": Vector((sign, 0, 0))}[axis]
    e1 = Vector((1, 0, 0)) if axis != "X" else Vector((0, 1, 0))
    e2 = Vector((0, 0, 1)) if axis == "Y" else (Vector((0, 1, 0)) if axis == "Z" else Vector((0, 0, 1)))
    c = Vector(c)
    rings = []
    for r, d in profile:
        base = c + ax * d
        if r <= 1e-6:
            rings.append([bm.verts.new(mv(base))])
            continue
        rings.append([bm.verts.new(mv(base + e1 * (r * math.cos(a)) + e2 * (r * math.sin(a))))
                      for a in (2 * math.pi * i / seg for i in range(seg))])
    faces = []
    for ra, rb in zip(rings, rings[1:]):
        if len(ra) == 1 and len(rb) == 1:
            continue
        if len(ra) == 1:
            faces += [bm.faces.new((ra[0], rb[(j + 1) % seg], rb[j])) for j in range(seg)]
        elif len(rb) == 1:
            faces += [bm.faces.new((ra[j], ra[(j + 1) % seg], rb[0])) for j in range(seg)]
        else:
            faces += [bm.faces.new((ra[j], ra[(j + 1) % seg], rb[(j + 1) % seg], rb[j]))
                      for j in range(seg)]
    if len(rings[0]) > 1:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
    if len(rings[-1]) > 1:
        faces.append(bm.faces.new(rings[-1]))
    b._tag(faces, region)
    return faces


def raised_panel(b, region, x0, x1, z0, z1, y_front, y_back, slope=1.0, rise=0.2):
    """A molded raised panel filling the hole (x0..x1, z0..z1) between stiles and rails.

    y_front/y_back are the panel's outer-ring faces (recessed from the frame faces). The
    field sits `rise` proud of the ring on both faces, with a `slope`-wide bevel between."""
    bm = b.bm
    xi0, xi1, zi0, zi1 = x0 + slope, x1 - slope, z0 + slope, z1 - slope
    def ring(xa, xb, za, zb, y):
        return [bm.verts.new(mv(p)) for p in ((xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb))]
    fo = ring(x0, x1, z0, z1, y_front)
    fi = ring(xi0, xi1, zi0, zi1, y_front - rise)
    bo = ring(x0, x1, z0, z1, y_back)
    bi = ring(xi0, xi1, zi0, zi1, y_back + rise)
    faces = [bm.faces.new(fi), bm.faces.new(list(reversed(bi)))]
    for i in range(4):
        j = (i + 1) % 4
        faces.append(bm.faces.new((fo[i], fo[j], fi[j], fi[i])))
        faces.append(bm.faces.new((bo[j], bo[i], bi[i], bi[j])))
        faces.append(bm.faces.new((fo[j], fo[i], bo[i], bo[j])))
    b._tag(faces, region)
    return faces


def lite(b, region, x0, x1, z0, z1, y0, y1, mold=0.9, proud=0.15):
    """A glazed bay: an opaque dark-glass slab through the middle of the leaf and a lite
    frame (molding) on both faces overlapping the bay's edges by `mold`."""
    yc = (y0 + y1) / 2
    box(b, "lite", (x0, yc - 0.1, z0), (x1, yc + 0.1, z1))
    for ya, yb in ((y0 - proud, y0 + 0.45), (y1 - 0.45, y1 + proud)):
        box(b, region, (x0, ya, z0), (x0 + mold, yb, z1))
        box(b, region, (x1 - mold, ya, z0), (x1, yb, z1))
        box(b, region, (x0 + mold, ya, z0), (x1 - mold, yb, z0 + mold))
        box(b, region, (x0 + mold, ya, z1 - mold), (x1 - mold, yb, z1))


def panel_leaf(b, x0, x1, z0, z1, y0, y1, rails, cols, stile=4.5, mullion=4.5,
               region="leaf", flush=False, lite_bays=()):
    """A stile-and-rail leaf, x0..x1, z0..z1, thickness y0..y1 (y0 < y1).

    rails: list of (za, zb) rail spans in leaf-local height (0 = leaf bottom), bottom to
    top, including the bottom and top rails. cols: number of panel columns between rails
    (1 or 2), per bay as a list. Panels fill every bay between consecutive rails, except
    the bays listed in lite_bays, which are glazed (lite())."""
    t = y1 - y0
    groove = min(0.34, t * 0.25)
    box(b, region, (x0, y0, z0), (x0 + stile, y1, z1))
    box(b, region, (x1 - stile, y0, z0), (x1, y1, z1))
    for za, zb in rails:
        box(b, region, (x0 + stile, y0, z0 + za), (x1 - stile, y1, z0 + zb))
    for i in range(len(rails) - 1):
        za, zb = z0 + rails[i][1], z0 + rails[i + 1][0]
        n = cols[i]
        xa, xb = x0 + stile, x1 - stile
        if i in lite_bays:
            lite(b, region, xa, xb, za, zb, y0, y1)
            continue
        if n == 2:
            xm = (xa + xb) / 2
            box(b, region, (xm - mullion / 2, y0, za), (xm + mullion / 2, y1, zb))
            bays = [(xa, xm - mullion / 2), (xm + mullion / 2, xb)]
        else:
            bays = [(xa, xb)]
        for pa, pb in bays:
            if flush:
                box(b, region, (pa, y0 + groove, za), (pb, y1 - groove, zb))
            else:
                raised_panel(b, region, pa, pb, za, zb, y0 + groove * 1.6, y1 - groove * 1.6,
                             slope=0.6, rise=groove * 1.45)   # >35 deg so the slopes stay crisp


# --- handles -----------------------------------------------------------------------

# Stepped round rose, 2.6 in across (IMG_1523: two rings and a dome into the neck).
ROSE = [(1.3, 0.0), (1.3, 0.1), (1.04, 0.22), (0.98, 0.32), (0.78, 0.38)]
# Ball knob on that rose (IMG_1502).
KNOB = ROSE + [(0.45, 0.5), (0.42, 1.05), (0.78, 1.3), (1.03, 1.7), (1.04, 2.05),
               (0.88, 2.4), (0.5, 2.62), (0.0, 2.68)]
# Bifold mushroom knob, 1.25 in across (IMG_1523).
MUSHROOM = [(0.42, 0.0), (0.42, 0.08), (0.2, 0.14), (0.17, 0.62), (0.45, 0.72),
            (0.62, 0.86), (0.62, 1.0), (0.44, 1.12), (0.0, 1.16)]


def knob(b, region, x, z, y_face, sign, style="knob"):
    """Knob set on the face at y_face; sign = -1 for the -Y face, +1 for +Y. style "knob"
    (ball knob on a rose), "mushroom" (small bifold knob) or "rose" (the rose alone, for
    a lever). Returns the y of the rose's outer face."""
    prof = {"knob": KNOB, "mushroom": MUSHROOM,
            "rose": ROSE + [(0.48, 0.5), (0.0, 0.64)]}[style]
    seg = {"mushroom": 12, "knob": 16, "rose": 12}[style]   # >= 11: smooth-by-angle (35)
    lathe(b, region, (x, y_face, z), prof, axis="Y", sign=sign, seg=seg)
    return y_face + sign * 0.38


def lever(b, region, x, z, y_face, sign, direction):
    """Lever set: stepped rose and a scroll lever that curls out of the rose, runs
    `direction` (+1/-1 in X, toward the hinge) and flicks up at the tip (IMG_1523)."""
    knob(b, region, x, z, y_face, sign, style="rose")
    d, s = direction, sign
    # (out of the face, along toward the hinge, up, half-thickness, half-height): a round
    # neck that turns toward the hinge, a slim blade, a flatter paddle at the up-turned tip;
    # every turn < 35 deg so it shades smooth
    path = [(0.4, 0.0, 0.0, 0.26, 0.26), (1.2, 0.0, 0.0, 0.25, 0.25),
            (1.68, 0.28, -0.04, 0.2, 0.25), (1.98, 0.85, -0.12, 0.16, 0.25),
            (2.06, 1.9, -0.2, 0.15, 0.24), (1.98, 3.3, -0.16, 0.14, 0.3),
            (1.87, 4.3, 0.0, 0.12, 0.36), (1.83, 4.85, 0.24, 0.1, 0.34)]
    pts = [Vector(mv((x + d * a, y_face + s * o, z + h))) for o, a, h, _, _ in path]
    scales = [(m(t), m(v)) for _, _, _, t, v in path]
    sweep_scaled(b, region, pts, scales, 11)


def sweep_scaled(b, region, pts, scales, n):
    """Sweep an ellipse (n points) along pts, with (half side, half up) per point. The
    ellipse's "up" axis stays near world Z (door hardware)."""
    bm = b.bm
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else t.orthogonal().normalized()
        up = side.cross(t).normalized()
        a, c = scales[i]
        rings.append([bm.verts.new(p + side * (a * math.cos(2 * math.pi * k / n))
                                   + up * (c * math.sin(2 * math.pi * k / n))) for k in range(n)])
    faces = [bm.faces.new((ra[k], ra[(k + 1) % n], rb[(k + 1) % n], rb[k]))
             for ra, rb in zip(rings, rings[1:]) for k in range(n)]
    faces += [bm.faces.new(list(reversed(rings[0]))), bm.faces.new(rings[-1])]
    b._tag(faces, region)


def deadbolt(b, region, x, z, y_front, y_back):
    """Deadbolt: rose + thumb turn on the -Y (inside) face, rose + key cylinder on +Y."""
    rose = [(1.1, 0.0), (1.1, 0.1), (1.0, 0.2), (0.85, 0.28), (0.75, 0.4), (0.0, 0.42)]
    lathe(b, region, (x, y_front, z), rose, axis="Y", sign=-1, seg=12)
    box(b, region, (x - 0.16, y_front - 1.1, z - 0.62), (x + 0.16, y_front - 0.3, z + 0.62))
    cyl = [(1.1, 0.0), (1.1, 0.1), (0.95, 0.2), (0.62, 0.3), (0.58, 0.72), (0.5, 0.8), (0.0, 0.8)]
    lathe(b, region, (x, y_back, z), cyl, axis="Y", sign=1, seg=12)
    box(b, "dark", (x - 0.05, y_back + 0.79, z - 0.28), (x + 0.05, y_back + 0.82, z + 0.28))


def latch(b, region, x_edge, s, z, y0, y1, bolt=0.4):
    """Latch faceplate (1 x 2.25) on the leaf's latch edge at x_edge (outward normal +s),
    and the bolt standing `bolt` out of it."""
    yc = (y0 + y1) / 2
    box(b, region, (x_edge - s * 0.02, yc - 0.5, z - 1.125), (x_edge + s * 0.03, yc + 0.5, z + 1.125))
    if bolt:
        box(b, region, (x_edge, yc - 0.28, z - 0.32), (x_edge + s * bolt, yc + 0.28, z + 0.32))


def strike(b, region, x_jamb, s, z, y0, y1, h=2.75):
    """Strike plate on the latch jamb's face at x_jamb (the face looks toward -s, into the
    opening), spanning y0..y1, with its dark latch hole."""
    yc = (y0 + y1) / 2
    box(b, region, (x_jamb + s * 0.02, y0, z - h / 2), (x_jamb - s * 0.03, y1, z + h / 2))
    box(b, "dark", (x_jamb - s * 0.03, yc - 0.3, z - 0.5), (x_jamb - s * 0.045, yc + 0.3, z + 0.5))


def hinge(frame, leaf, region, pin, hz, s, y_back):
    """One butt hinge centred at height hz on the pin (x, y). The frame gets the jamb plate
    (on the jamb face at x = s*JAMB_T), the middle knuckle and the pin tips; the leaf gets
    the edge plate (on the door's hinge edge at x = s*(JAMB_T + GAP)) and the outer two
    knuckles. Plates run back from the pin to y_back."""
    px, py = pin
    h2 = HINGE_H / 2
    xj, xe = s * JAMB_T, s * (JAMB_T + GAP)
    box(frame, region, (xj - s * 0.02, py, hz - h2), (xj + s * 0.035, y_back, hz + h2))
    box(leaf, region, (xe + s * 0.02, py, hz - h2), (xe - s * 0.035, y_back, hz + h2))
    k = HINGE_H / 3
    cyl(frame, region, (px, py, hz), BARREL_R, k - 0.06, axis="Z", seg=8)
    for zc in (hz - k, hz + k):
        cyl(leaf, region, (px, py, zc), BARREL_R, k - 0.06, axis="Z", seg=8)
    # button tip on top (IMG_1523 shows one at the top; the bottom end reads plain)
    cyl(frame, region, (px, py, hz + h2 + 0.06), 0.17, 0.14, axis="Z", seg=5)


def rotate_about(b, pivot, deg, verts=None):
    """Rotate geometry about the vertical axis through pivot (inches)."""
    verts = verts if verts is not None else list(b.bm.verts)
    bmesh.ops.rotate(b.bm, verts=verts, cent=Vector(mv(pivot)),
                     matrix=Matrix.Rotation(math.radians(deg), 3, "Z"))


def jamb(b, width, height, wall_t, hand=1, x_start=0.0, stops=True, stop_y=None,
         region="paint"):
    """Jamb liner inside the opening (legs + head) and optional stops at stop_y."""
    s = hand
    xa, xb = sorted((x_start, x_start + s * width))
    y0, y1 = -wall_t / 2, wall_t / 2
    box(b, region, (xa, y0, 0), (xa + JAMB_T, y1, height))
    box(b, region, (xb - JAMB_T, y0, 0), (xb, y1, height))
    box(b, region, (xa + JAMB_T, y0, height - JAMB_T), (xb - JAMB_T, y1, height))
    if stops:
        ya, yb = stop_y, stop_y + STOP_W
        box(b, region, (xa + JAMB_T, ya, 0), (xa + JAMB_T + STOP_T, yb, height - JAMB_T))
        box(b, region, (xb - JAMB_T - STOP_T, ya, 0), (xb - JAMB_T, yb, height - JAMB_T))
        box(b, region, (xa + JAMB_T + STOP_T, ya, height - JAMB_T - STOP_T),
            (xb - JAMB_T - STOP_T, yb, height - JAMB_T))


def marker(coll, name, loc_in):
    import bpy
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.03
    ob.location = mv(loc_in)
    coll.objects.link(ob)
    return ob


def register_leaf(name, x_zero, x_one, z0, z1, pin=(0.0, 0.0), angle=0.0, u_scale=1.0):
    """Record how the leaf object `name` maps onto the "leaf" wear region: u = 0 at
    x_zero, u = u_scale at x_one (the handle edge), v = 0..1 over z0..z1, all measured in
    the leaf's closed pose (geometry rotated by `angle` degrees about `pin` is unrotated
    first). u_scale < 1 keeps a leaf without a handle clear of the smudges near u = 1."""
    LEAF_UV[name] = (x_zero, x_one, z0, z1, tuple(pin), angle, u_scale)


def hinged(coll, name, width, height, wall_t, leaf_t, hand, open_deg, rails, cols,
           handle="knob", finish="nickel", hinge_finish=None, flush=False, extras=None,
           lite_bays=(), deadbolt_z=None):
    """A hinged door: frame object (jamb, stops, hinge plates and knuckles, strikes) + leaf
    object (leaf, hinge plates and knuckles, latch, handles).

    width: clear opening (in); hand: +1 opening extends to +X, -1 to -X; open_deg: how far
    the leaf is swung toward -Y (0 = closed). finish: atlas region of the handle set,
    hinge_finish of the hinges (default: the same). Returns [frame, leaf, grab marker]."""
    s = hand
    hinge_finish = hinge_finish or finish
    y_face = -wall_t / 2                     # leaf's front face sits flush with the jamb edge
    y_back = y_face + leaf_t
    pin = (s * (JAMB_T + GAP / 2), y_face - 0.15, 0.0)
    f = builder()
    b = builder()
    # frame
    jamb(f, width, height, wall_t, hand=s, stops=True, stop_y=y_back)
    hinge_z = [11.0, (11.0 + height - 7.0) / 2, height - 7.0]    # EST standard spacing
    for hz in hinge_z:
        hinge(f, b, hinge_finish, pin[:2], hz, s, y_face + 1.25)
    x_jamb = s * (width - JAMB_T)
    strike(f, finish, x_jamb, s, KNOB_Z, y_face + 0.08, y_back - 0.08)
    if deadbolt_z:
        strike(f, finish, x_jamb, s, deadbolt_z, y_face + 0.08, y_back - 0.08, h=2.9)
    # leaf
    lx0, lx1 = sorted((s * (JAMB_T + GAP), s * (width - JAMB_T - GAP)))
    lz0, lz1 = FLOOR_GAP, height - JAMB_T - GAP
    panel_leaf(b, lx0, lx1, lz0, lz1, y_face, y_back, rails, cols, flush=flush,
               lite_bays=lite_bays)
    x_edge = s * (width - JAMB_T - GAP)
    latch_x = x_edge - s * BACKSET
    for sign, yf in ((-1, y_face), (1, y_back)):
        if handle == "lever":
            lever(b, finish, latch_x, KNOB_Z, yf, sign, direction=-s)
        else:
            knob(b, finish, latch_x, KNOB_Z, yf, sign)
    latch(b, finish, x_edge, s, KNOB_Z, y_face, y_back)
    if deadbolt_z:
        deadbolt(b, finish, latch_x, deadbolt_z, y_face, y_back)
        latch(b, finish, x_edge, s, deadbolt_z, y_face, y_back, bolt=0.0)
    if extras:
        extras(b, lx0, lx1, lz0, lz1, y_face, y_back)
    grab = (latch_x, y_face - 2.4, KNOB_Z)
    if open_deg:
        rotate_about(b, pin, -s * open_deg)
        g = Matrix.Rotation(math.radians(-s * open_deg), 3, "Z") @ (Vector(grab) - Vector(pin)) + Vector(pin)
        grab = tuple(g)
    frame = f.to_object(name, coll)
    leaf = b.to_object(name + "_leaf", coll, origin=mv(pin))
    register_leaf(leaf.name, s * (JAMB_T + GAP), x_edge, lz0, lz1, pin[:2], -s * open_deg)
    mk = marker(coll, name + "_leaf_grab", grab)
    return [frame, leaf, mk]


# --- texturing / materials ---------------------------------------------------------

def leaf_uvs(ob):
    """Map the "leaf" faces of a registered leaf onto the wear region (see register_leaf)."""
    spec = LEAF_UV.get(ob.name)
    me = ob.data
    regions = [m_.name.split(".")[0] for m_ in me.materials]
    if spec is None or "leaf" not in regions:
        return
    x_zero, x_one, z0, z1, pin, angle, u_scale = spec
    u0, v0, u1, v1 = common.uv_rect(ATLAS, "leaf")
    rot = Matrix.Rotation(math.radians(-angle), 3, "Z")
    pv = Vector((pin[0], pin[1], 0.0))
    uvl = me.uv_layers["UVMap"]
    li = regions.index("leaf")
    loc = Vector(ob.location) / IN
    for p in me.polygons:
        if p.material_index != li:
            continue
        for l in p.loop_indices:
            co = Vector(me.vertices[me.loops[l].vertex_index].co) / IN + loc
            co = rot @ (co - pv) + pv
            fu = min(max((co.x - x_zero) / (x_one - x_zero), 0.0), 1.0) * u_scale
            fv = min(max((co.z - z0) / (z1 - z0), 0.0), 1.0)
            uvl.data[l].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def texture(objs):
    mat = common.atlas_material("doors", ATLAS)
    glass = None
    for ob in objs:
        if ob.type != "MESH":
            continue
        common.atlas_uvs(ob, ATLAS)
        leaf_uvs(ob)
        used = {m_.name.split(".")[0] for m_ in ob.data.materials}
        mapping = {r: mat for r in REGIONS}
        if "glass" in used:
            glass = glass or glass_material()
            mapping["glass"] = glass
        # drop unused placeholder slots before collapsing
        common.collapse_materials(ob, mapping)
        _drop_unused_slots(ob)


def _drop_unused_slots(ob):
    me = ob.data
    used = sorted({p.material_index for p in me.polygons})
    mats = [me.materials[i] for i in used]
    remap = {old: new for new, old in enumerate(used)}
    idx = [remap[p.material_index] for p in me.polygons]
    me.materials.clear()
    for mt in mats:
        me.materials.append(mt)
    me.polygons.foreach_set("material_index", idx)
    me.update()


def glass_material():
    mat = common.atlas_material("doors_glass", ATLAS)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = 0.25
    for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(mat, attr, val)
        except (AttributeError, TypeError):
            pass
    return mat
