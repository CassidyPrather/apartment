"""Kitchen clutter: everything on the kitchen counters and on top of the fridge, as seen
in the living-room/kitchen LiDAR capture (frames wide_20260925_0037..0044). Only things
that are visible in the capture frames are modelled.

  west counter, south end   dish rack (grey tray, chrome wire rack) holding a steel pot
                            lid, an empty yellow tin can and a small clear lid; a yellow
                            funnel lying by the backsplash; a blue hand towel hanging on
                            the upper cabinet door above
  sink                      foaming soap pump behind the north bowl; dish brush on its
                            round black stand and a small black-and-chrome tool north of
                            the sink
  west counter, north end   dish-soap bottle (clear, blue soap, blank label), a small white
                            cup, a clear produce bag of potatoes, a bamboo knife block in
                            the corner, a round loaf in a clear bag, a flat green pizza box
                            with a mesh bag of onions on it
  north counter, west       black gooseneck kettle on its base, the rice cooker's glass lid
                            lying on the counter, the white rice cooker (lid off, black
                            pot), a small glass bowl; the kettle and rice cooker cords
  north counter, east       kraft coffee box with a black bag on it, a black drip coffee
                            maker (lid flipped up, glass carafe; parody "Mister Sippy"), a
                            steel hand grinder lying in front, a black single-serve maker
                            and its round drip tray, a clear tub of coffee beans, a yellow
                            spray bottle, a paper-towel holder with its roll, two small
                            blank cards
  fridge top                three shrink-wrapped napkin packs stacked (parody "Napsody"),
                            a pink box behind them, a pack of paper plates, a bag of basket
                            coffee filters, a sleeve of filters lying on its side, a sleeve
                            of navy paper cups and the big 12-roll paper-towel pack
                            (parody "Soakington")

No real brand, text or personal information: labels are blank colour blocks or parody
marks drawn from scratch (logos/*.svg).

Source of truth: scripted. FRAME: PLAN COORDINATES, like bedroom_cables: object X = plan x
(east), Y = plan y (north), Z up from the floor, metres; the package goes on a marker at
the plan origin with no rotation. Items sit on the MODELLED surfaces of the neighbouring
packages (read-only): the counter top z 36 and backsplash (kitchen_cabinets), the sink rim
deck z 36.12, the upper door face x 13.0 (kitchen_cabinets), the fridge top z 66 over
x 102-130.5, y 253.5-285 (fridge at plan (116.25, 267.5)). Positions along those surfaces
come from the capture (splat/LiDAR top views + the photos), sizes are standard sizes (EST)
proportioned against the counter, sink and appliances in the photos.

Provenance tags: SCAN = measured on the registered capture points (+-1.5 in: the frame
poses drift a few inches), PHOTO = proportioned from the capture photos, EST = standard
product size or guess, MODEL = taken from a neighbouring package.
"""

import math

import bmesh
from mathutils import Matrix, Vector

import common

NAME = "kitchen_clutter"
IN = 0.0254


def m(v):
    return v * IN


# --- surfaces (plan inches) ----------------------------------------------------------
CZ = 36.0                   # MODEL kitchen_cabinets TOP_Z1 (counter top)
SINK_DECK = 36.12           # MODEL sink rim deck (top + 0.12)
SPLASH_X = 0.75             # MODEL west backsplash face
SPLASH_Y = 285.25           # MODEL north backsplash face
WALL_Y = 286.0              # MODEL north wall (above the 4 in splash)
SPLASH_TOP = 40.0           # MODEL splash height 4
DOOR_FACE_X = 13.0          # MODEL upper door face (UP_D 13), west run
PULL_Z = 56.5               # MODEL upper pull centre (z0 53 + 3.5)
FZ = 66.0                   # MODEL fridge top (H 66)

# --- item placement (plan inches; provenance) ----------------------------------------
RACK = (2.0, 18.5, 187.0, 206.0)        # SCAN/PHOTO tray x0, x1, y0, y1 (16.5 x 19, matched to 004026/003853)
LID = ((7.4, 191.2, 41.7), (0.62, 0.45, 0.64), 5.5)   # PHOTO centre, face normal; EST r 5.5
CAN = (10.0, 196.5, 25.0)               # SCAN base x, y; PHOTO tilt (top toward the SSW); EST 4.2 x 5.8
CLEAR_LID = (6.2, 202.6, 2.6)           # PHOTO x, y; EST radius
FUNNEL = ((6.8, 212.6), (2.8, 210.9))   # SCAN/PHOTO mouth centre, spout direction point
TOWEL_Y = 202.0                         # SCAN towel centre (see report: the modelled pull is at 212.4)
SOAP_PUMP = (2.6, 244.6)                # PHOTO behind the north bowl, on the sink deck
BRUSH = ((5.4, 248.3), (9.4, 255.4))    # PHOTO head, handle end
TOOL = (2.6, 249.6)                     # PHOTO black/chrome tool by the backsplash
STOPPER = (2.3, 236.3)                  # PHOTO sink stopper lying on the deck by the faucet
DISH_SOAP = (4.8, 259.2)                # PHOTO
WHITE_CUP = (2.6, 261.8)                # PHOTO
PRODUCE = (7.2, 264.6, 60.0)            # PHOTO x, y, heading
KNIFE_BLOCK = (7.6, 277.0, 45.0)        # SCAN/PHOTO x, y, heading (slope faces the room corner)
BREAD = (13.2, 269.8, 30.0)             # PHOTO
PIZZA = (19.4, 275.6, -12.0)            # PHOTO/SCAN (under the onions)
ONIONS = (18.8, 277.2)                  # SCAN/PHOTO
KETTLE = (30.6, 277.6)                  # SCAN
GLASS_LID = (36.3, 272.6)               # PHOTO
RICE = (41.5, 279.0)                    # SCAN
BOWL = (47.0, 272.8)                    # PHOTO
OUTLET = (35.5, 44.5)                   # EST x, z of the wall outlet the cords go to
COFFEE_BOX = (81.8, 280.6)              # PHOTO
DRIP = (86.3, 279.8)                    # SCAN
GRINDER = ((90.0, 276.0), (88.3, 271.2))  # PHOTO ends
POD = (92.8, 280.6)                     # SCAN
DRIP_TRAY = (93.2, 274.9)               # PHOTO
BEANS = (97.3, 281.5, 10.0)             # PHOTO
SPRAY = (98.0, 277.4)                   # PHOTO
TOWEL_ROLL = (96.8, 270.8)              # SCAN
CARDS = [(98.4, 262.4, 10.0), (98.8, 258.6, -15.0)]   # PHOTO
NAPKINS = (106.3, 265.5)                # SCAN/PHOTO stack centre
PINK_BOX = (105.8, 272.0)               # SCAN/PHOTO
PLATES = (114.6, 267.8)                 # PHOTO
FILTER_BAG = (113.8, 258.4)             # PHOTO
FILTER_SLEEVE = (122.3, 257.6)          # PHOTO
CUPS = (127.8, 257.3)                   # PHOTO
TOWEL_PACK = (119.6, 130.3, 262.2, 284.8, 83.7)   # SCAN x0, x1, y0, y1, top (under the cabinet at 84)

ATLAS = {
    "name": NAME,
    "size": 1024,
    "regions": {
        # row of 64 px swatches
        "white_plastic": (0, 0, 64, 64),
        "black_plastic": (64, 0, 64, 64),
        "chrome": (128, 0, 64, 64),
        "steel": (192, 0, 64, 64),
        "rack_grey": (256, 0, 64, 64),
        "yellow_plastic": (320, 0, 64, 64),
        "clear": (384, 0, 64, 64),
        "blue_liquid": (448, 0, 64, 64),
        "pot_dark": (512, 0, 64, 64),
        "kraft": (576, 0, 64, 64),
        "beans": (640, 0, 64, 64),
        "potato": (704, 0, 64, 64),
        "cord_white": (768, 0, 64, 64),
        "paper_white": (832, 0, 64, 64),
        "glass_dark": (896, 0, 64, 64),
        "bristle": (960, 0, 64, 64),
        "onion": (0, 64, 64, 64),
        "bread": (64, 64, 64, 64),
        "label_white": (128, 64, 64, 64),
        "pink": (192, 64, 64, 64),
        "navy": (256, 64, 64, 64),
        "green_box": (320, 64, 64, 64),
        "bag_black": (384, 64, 64, 64),
        "cream": (448, 64, 64, 64),
        "filters_white": (512, 64, 64, 64),
        "rubber_black": (576, 64, 64, 64),
        "towel_edge": (640, 64, 64, 64),
        "mesh_red": (704, 64, 64, 64),
        "spray_white": (768, 64, 64, 64),
        "plates_blue": (832, 64, 64, 64),
        "napkin_white": (896, 64, 64, 64),
        "bamboo_end": (960, 64, 64, 64),
        # printed / patterned regions
        "towel_blue": (0, 128, 256, 256),
        "pizza_top": (256, 128, 256, 256),
        "tpack_side": (512, 128, 512, 256),
        "tpack_end": (0, 384, 256, 256),
        "napkin_side": (256, 384, 256, 128),
        "napkin_top": (256, 512, 128, 128),
        "plates_top": (384, 512, 128, 128),
        "plates_side": (512, 384, 256, 128),
        "pink_face": (768, 384, 256, 128),
        "cups": (512, 512, 256, 128),
        "can_label": (768, 512, 256, 128),
        "bamboo": (0, 640, 128, 128),
        "block_top": (128, 640, 128, 128),
        "coffee_front": (256, 640, 128, 128),
        "coffee_badge": (384, 640, 128, 64),
        "soap_label": (384, 704, 128, 64),
        "spray_label": (512, 640, 128, 128),
        "roll_side": (640, 640, 128, 128),
        "filters_side": (768, 640, 128, 128),
        "filter_label": (896, 640, 128, 64),
        "pizza_side": (896, 704, 128, 64),
        "rice_front": (0, 768, 128, 64),
        "kraft_print": (128, 768, 128, 128),
        "tray_ribs": (256, 768, 128, 128),
        "display": (384, 768, 128, 64),
        "pump_top": (384, 832, 128, 64),
        "filters_end": (512, 768, 128, 128),
        "cups_top": (640, 768, 128, 128),
        "tpack_top": (768, 768, 256, 128),
        "rice_top": (0, 832, 128, 64),
    },
}
REGIONS = list(ATLAS["regions"])
CLEAR_REGIONS = {"clear"}
CLEAR_ALPHA = 0.22
MATERIALS = {
    NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
    NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": CLEAR_ALPHA, "tiled": False},
}
COLLIDER = "none"
STATIC = True
VIEWS = [("from_dining", 20, 22, 0.55), ("from_dining_w", -25, 25, 0.55), ("down", 0, 60, 0.6)]

# faces with hand-made UVs: filled at the end of build(), applied in texture()
CUSTOM = []
_PENDING = []


# --- geometry helpers ------------------------------------------------------------------

def P(x, y, z):
    return Vector((m(x), m(y), m(z)))


def F(x, y, z, h=0.0):
    """Frame at plan (x, y, z) inches, turned h degrees about Z."""
    return Matrix.Translation(P(x, y, z)) @ Matrix.Rotation(math.radians(h), 4, "Z")


def RX(d):
    return Matrix.Rotation(math.radians(d), 4, "X")


def RY(d):
    return Matrix.Rotation(math.radians(d), 4, "Y")


def RZ(d):
    return Matrix.Rotation(math.radians(d), 4, "Z")


def S(sx, sy, sz):
    return Matrix.Diagonal((sx, sy, sz, 1.0))


def align_z(n):
    """Rotation taking local +Z onto direction n."""
    return Vector((0, 0, 1)).rotation_difference(Vector(n).normalized()).to_matrix().to_4x4()


def pbox(b, mat, x0, x1, y0, y1, z0, z1, regions):
    """Box of 6 separate quads with 0-1 UVs per face (u right, v up seen from outside;
    top: u +x, v +y). regions: {'+x'|'-x'|'+y'|'-y'|'+z'|'-z'|'all': region or
    (region, (u0, v0, u1, v1))}."""
    faces = {
        "-y": [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)],
        "+y": [(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)],
        "+x": [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)],
        "-x": [(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)],
        "+z": [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "-z": [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)],
    }
    out = []
    for key, pts in faces.items():
        spec = regions.get(key, regions.get("all"))
        if spec is None:
            continue
        reg, sub = (spec, (0, 0, 1, 1)) if isinstance(spec, str) else spec
        vs = [b.bm.verts.new(mat @ P(*p)) for p in pts]
        f = b.bm.faces.new(vs)
        b._tag([f], reg)
        u0, v0, u1, v1 = sub
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        _PENDING.append((f, reg, dict(zip(vs, uvs))))
        out.append(f)
    return out


def lathe(b, region, mat, prof, seg=16, uv=False, cap_top=None, cap_bot=None):
    """Revolve [(r, z)] (inches, bottom to top) about local Z. r == 0 makes a pole.
    uv=True duplicates the seam and records cylindrical UVs (u around, v along the
    profile). cap_top / cap_bot: region for a flat cap on an open end (None = open)."""
    L = [0.0]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        L.append(L[-1] + math.hypot(r1 - r0, z1 - z0))
    tot = L[-1] or 1.0
    n = seg + 1 if uv else seg
    rings = []
    uvmap = {}
    for (r, z), l in zip(prof, L):
        if r == 0:
            v = b.bm.verts.new(mat @ P(0, 0, z))
            rings.append([v] * n)
            uvmap[v] = (0.5, l / tot)
            continue
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / seg
            v = b.bm.verts.new(mat @ P(r * math.cos(a), r * math.sin(a), z))
            ring.append(v)
            uvmap[v] = (i / seg, l / tot)
        rings.append(ring)
    faces = []
    for k in range(len(rings) - 1):
        A, B = rings[k], rings[k + 1]
        for i in range(seg):
            j = i + 1 if uv else (i + 1) % seg
            quad = [A[i], A[j], B[j], B[i]]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                faces.append(b.bm.faces.new(uniq))
    b._tag(faces, region)
    if uv:
        for f in faces:
            _PENDING.append((f, region, {v: uvmap[v] for v in f.verts}))
    for reg, ring, top in ((cap_top, rings[-1], True), (cap_bot, rings[0], False)):
        if reg and len(set(ring)) > 2:
            vs = ring[:seg]
            f = b.bm.faces.new(vs if top else list(reversed(vs)))
            b._tag([f], reg)
            faces.append(f)
    return faces


def cyl(b, region, mat, r, z0, z1, seg=12, cap=None, uv=False):
    """Closed cylinder along local Z (caps in `cap` or the same region)."""
    c = cap or region
    return lathe(b, region, mat, [(r, z0), (r, z1)], seg=seg, uv=uv, cap_top=c, cap_bot=c)


def wire(b, region, pts, r, sides=4, samples=0):
    """Round-ish wire swept through plan-inch points."""
    q = [P(*p) for p in pts]
    if samples:
        q = common.smooth_path(q, samples)
    return b.sweep(region, q, common.circle_profile(m(r), sides))


def lbox(b, region, mat, x0, x1, y0, y1, z0, z1, bevel=0.0):
    """Builder box in a local frame (inches)."""
    return b.box(region, (m(x0), m(y0), m(z0)), (m(x1), m(y1), m(z1)), bevel=m(bevel),
                 segments=1, matrix=mat)


def sweep_uv(b, region, pts, prof, up=(0, 0, 1)):
    """Builder sweep with recorded UVs: u around the profile, v along the path."""
    faces = b.sweep(region, pts, prof, up=up)
    nseg, mp = len(pts) - 1, len(prof)
    for idx, f in enumerate(faces[:nseg * mp]):
        i, j = divmod(idx, mp)
        vs = list(f.verts)
        uvs = [(j / mp, i / nseg), ((j + 1) / mp, i / nseg), ((j + 1) / mp, (i + 1) / nseg), (j / mp, (i + 1) / nseg)]
        _PENDING.append((f, region, dict(zip(vs, uvs))))
    return faces


def rec_local(f, region, mat):
    """Record planar UVs for a face from its own local-frame bounds (inches)."""
    inv = mat.inverted()
    loc = {v: inv @ v.co for v in f.verts}
    n = (inv.to_3x3() @ f.normal).normalized() if f.normal.length else Vector((0, 0, 1))
    if abs(n.x) > 0.7:
        a, c = 1, 2
    elif abs(n.z) > 0.7:
        a, c = 0, 1
    else:
        a, c = 0, 2
    lo = [min(p[k] for p in loc.values()) for k in (a, c)]
    hi = [max(p[k] for p in loc.values()) for k in (a, c)]
    _PENDING.append((f, region, {v: ((p[a] - lo[0]) / max(hi[0] - lo[0], 1e-9),
                                    (p[c] - lo[1]) / max(hi[1] - lo[1], 1e-9)) for v, p in loc.items()}))


def cord(b, region, pts, r=0.09):
    """A cord lying on the counter and climbing the wall; the spline is kept off the top."""
    q = common.smooth_path([P(*p) for p in pts], 3)
    for v in q:
        if m(CZ - 1.0) < v.z < m(CZ + r + 0.02):
            v.z = m(CZ + r + 0.02)
    return b.sweep(region, q, common.circle_profile(m(r), 4))


# --- west counter, south: dish rack -------------------------------------------------------

def dish_rack(b):
    x0, x1, y0, y1 = RACK
    z = CZ
    I = Matrix.Identity(4)
    pbox(b, I, x0, x1, y0, y1, z, z + 0.8,
         {"+z": "tray_ribs", "all": "rack_grey"})
    rx0, rx1, ry0, ry1 = x0 + 0.7, x1 - 0.9, y0 + 0.6, y1 - 0.6
    zb = z + 1.3
    for xx, yy in ((rx0, ry0), (rx1, ry0), (rx0, ry1), (rx1, ry1)):
        cyl(b, "rubber_black", Matrix.Translation(P(xx, yy, 0)), 0.3, z + 0.8, zb, seg=6)
    n = 7
    for i in range(n):
        xx = rx0 + (rx1 - rx0) * i / (n - 1)
        wire(b, "chrome", [(xx, ry0, zb), (xx, ry1, zb)], 0.07, sides=3)
    for yy in (ry0, (ry0 + ry1) / 2, ry1):
        wire(b, "chrome", [(rx0, yy, zb), (rx1, yy, zb)], 0.07, sides=3)
    # rim and a middle rail (the back, against the wall, stands a little taller)
    for zr, zf in ((z + 5.4, z + 4.4), (z + 3.2, z + 2.9)):
        loop = [P(rx0, ry0, zr), P(rx1, ry0, zf), P(rx1, ry1, zf), P(rx0, ry1, zr)]
        b.sweep("chrome", loop, common.circle_profile(m(0.08), 3), closed=True)
    for xx, yy in ((rx0, ry0), (rx1, ry0), (rx0, ry1), (rx1, ry1),
                   (rx0, (ry0 + ry1) / 2), (rx1, (ry0 + ry1) / 2)):
        top = z + 5.4 if xx == rx0 else z + 4.4
        wire(b, "chrome", [(xx, yy, zb), (xx, yy, top)], 0.07, sides=3)
    # plate dividers: arched wires across the rack (x), in the middle of its length
    for i in range(11):
        yy = ry0 + 5.2 + i * 0.95
        wire(b, "chrome", [(rx0 + 1.5, yy, zb), (rx0 + 2.4, yy, zb + 3.9), (rx0 + 5.0, yy, zb + 3.2),
                           (rx0 + 8.2, yy, zb + 1.2), (rx0 + 9.0, yy, zb)], 0.06, sides=3, samples=2)
    # tall U-wire loops fencing the north end
    for i in range(5):
        xx = rx0 + 1.4 + i * (rx1 - rx0 - 2.8) / 4
        wire(b, "chrome", [(xx - 0.9, ry1, zb), (xx - 0.9, ry1 + 0.3, zb + 5.6), (xx + 0.9, ry1 + 0.3, zb + 5.6),
                           (xx + 0.9, ry1, zb)], 0.06, sides=3, samples=2)
    return zb


def pot_lid(b, zb):
    (cx, cy, cz), nrm, r = LID
    mat = Matrix.Translation(P(cx, cy, cz)) @ align_z(nrm)
    prof = [(0, 0.95), (1.4, 0.9), (3.2, 0.62), (4.6, 0.3), (r, 0.05), (r, -0.05),
            (4.6, 0.2), (3.2, 0.52), (1.4, 0.8), (0, 0.85)]
    # outer dome top then back underneath (thin steel shell, both faces)
    lathe(b, "chrome", mat, list(reversed(prof)), seg=20)
    knob = [(0, 0.9), (0.55, 0.9), (0.45, 1.5), (0.95, 1.7), (0.9, 2.15), (0, 2.25)]
    lathe(b, "black_plastic", mat, knob, seg=10)


def tin_can(b, zb):
    x, y, tilt = CAN
    mat = Matrix.Translation(P(x, y, zb)) @ RZ(60) @ RY(-tilt)
    R, H = 2.1, 5.8
    lathe(b, "can_label", mat, [(R, 0.25), (R, H - 0.25)], seg=16, uv=True)
    lathe(b, "steel", mat, [(0, 0), (R - 0.1, 0), (R, 0.25)], seg=16)
    lathe(b, "steel", mat, [(R, H - 0.25), (R - 0.05, H), (R - 0.12, H), (R - 0.12, 0.3), (0, 0.3)], seg=16)


def clear_lid(b, zb):
    x, y, r = CLEAR_LID
    mat = Matrix.Translation(P(x, y, zb + r * 0.87)) @ RY(-62)
    lathe(b, "clear", mat, [(0, 0.35), (r - 0.2, 0.35), (r, 0.3), (r, -0.3), (r - 0.2, -0.1), (0, -0.1)], seg=14)


def funnel(b):
    (mx, my), (sx, sy) = FUNNEL
    d = Vector((sx - mx, sy - my, 0)).normalized()
    h = math.degrees(math.atan2(d.y, d.x))
    th = math.degrees(math.atan(1.85 / 6.0))          # rests on the mouth rim and the spout tip
    R0 = 2.2
    cz = CZ + R0 * math.cos(math.radians(th))
    mat = Matrix.Translation(P(mx, my, cz)) @ RZ(h) @ RY(90 + th)
    lathe(b, "yellow_plastic", mat, [(R0 - 0.1, 0.0), (R0, 0.0), (R0 - 0.1, 0.35), (0.42, 3.2), (0.3, 3.2),
                                     (R0 - 0.22, 0.35), (R0 - 0.1, 0.0)], seg=14)
    lathe(b, "black_plastic", mat, [(0.36, 3.0), (0.3, 6.0), (0.2, 6.0), (0.26, 3.1)], seg=8)
    # hanging tab on the rim
    lbox(b, "yellow_plastic", mat, -0.25, 0.25, R0 - 0.1, R0 + 0.6, -0.05, 0.1)


def hand_towel(b):
    """A blue terry hand towel hanging off the upper door by its fold: both halves hang
    down the door face, the front one lower, with soft vertical folds."""
    y = TOWEL_Y
    x = DOOR_FACE_X
    back = [(x + 0.35, y, 47.2), (x + 0.3, y, 52.0), (x + 0.35, y, 56.2), (x + 0.7, y, 57.6)]
    front = [(x + 1.2, y, 57.4), (x + 1.5, y, 55.0), (x + 1.7, y, 50.0), (x + 1.9, y, 45.5), (x + 2.0, y, 42.8)]
    pts = [P(*p) for p in common.smooth_path([Vector(p) for p in back + front], 2)]
    half = 3.3                                    # PHOTO ~6.5 in wide as it hangs (bunched)
    off = [0.0, 0.45, -0.1, 0.55, 0.05, 0.4, 0.0]
    k = len(off)
    outer = [(-m(o + 0.15), m(-half + 2 * half * i / (k - 1))) for i, o in enumerate(off)]
    inner = [(-m(o - 0.15), m(-half + 2 * half * i / (k - 1))) for i, o in reversed(list(enumerate(off)))]
    sweep_uv(b, "towel_blue", pts, outer + inner, up=(0, 1, 0))


# --- sink and west counter, north ---------------------------------------------------------

def soap_pump(b):
    x, y = SOAP_PUMP
    mat = Matrix.Translation(P(x, y, SINK_DECK))
    lathe(b, "clear", mat, [(0, 0), (1.3, 0), (1.35, 0.3), (1.35, 4.2), (1.0, 4.6), (0.9, 4.6)], seg=12)
    lathe(b, "blue_liquid", mat, [(0, 0.15), (1.15, 0.15), (1.15, 2.4), (0, 2.4)], seg=10)
    lathe(b, "pump_top", mat, [(1.0, 4.5), (1.05, 5.4), (0.85, 5.6), (0.5, 5.7), (0.5, 6.4), (0, 6.45)],
          seg=12, uv=True)
    lbox(b, "pump_top", mat, 0.3, 1.3, -0.3, 0.3, 5.9, 6.3)          # nozzle


def sink_stopper(b):
    x, y = STOPPER
    mat = Matrix.Translation(P(x, y, SINK_DECK))
    lathe(b, "rubber_black", mat, [(0, 0), (1.15, 0), (1.2, 0.25), (0.9, 0.4), (0, 0.4)], seg=12)
    lathe(b, "chrome", mat, [(0, 0.4), (0.35, 0.4), (0.3, 1.0), (0.45, 1.1), (0, 1.3)], seg=8)


def dish_brush(b):
    (hx, hy), (ex, ey) = BRUSH
    d = Vector((ex - hx, ey - hy, 0))
    L = d.length
    h = math.degrees(math.atan2(d.y, d.x))
    mat = F(hx, hy, CZ, h)
    # round black stand under the head
    cyl(b, "rubber_black", F(hx + 0.3, hy + 0.2, CZ), 1.5, 0, 0.35, seg=14)
    lbox(b, "bristle", mat, -1.3, 1.0, -0.8, 0.8, 0.35, 1.6, bevel=0.2)          # white bristles
    lbox(b, "black_plastic", mat, 1.0, 2.4, -0.55, 0.55, 0.45, 1.3, bevel=0.2)    # head collar
    b.sweep("black_plastic", [mat @ P(2.4, 0, 0.9), mat @ P(L * 0.55, 0, 0.55), mat @ P(L, 0, 0.45)],
            [(-m(0.35), -m(0.28)), (m(0.35), -m(0.28)), (m(0.35), m(0.28)), (-m(0.35), m(0.28))])
    cyl(b, "chrome", mat @ Matrix.Translation(P(L - 0.35, 0, 0.45)) @ RY(90), 0.18, -0.3, 0.3, seg=6)


def tool(b):
    """Small black-handled tool with a chrome head lying by the backsplash (can opener?)."""
    x, y = TOOL
    mat = F(x, y, CZ, 80)
    lbox(b, "black_plastic", mat, -2.8, 1.0, -0.55, -0.1, 0.0, 0.45, bevel=0.15)
    lbox(b, "black_plastic", mat, -2.6, 1.0, 0.1, 0.55, 0.0, 0.45, bevel=0.15)
    lbox(b, "chrome", mat, 1.0, 2.6, -0.8, 0.8, 0.0, 0.7, bevel=0.2)
    cyl(b, "black_plastic", mat @ Matrix.Translation(P(1.8, 0, 0.7)), 0.55, 0.0, 0.4, seg=8)


def dish_soap(b):
    x, y = DISH_SOAP
    mat = Matrix.Translation(P(x, y, CZ))
    body = [(0, 0), (1.25, 0), (1.35, 0.3), (1.35, 5.2), (1.15, 6.6), (0.6, 7.6), (0.5, 7.7)]
    lathe(b, "clear", mat, body, seg=14)
    lathe(b, "blue_liquid", mat, [(0, 0.1), (1.22, 0.1), (1.22, 3.6), (0, 3.6)], seg=10)
    lathe(b, "soap_label", mat, [(1.37, 1.0), (1.37, 4.6)], seg=14, uv=True)
    lathe(b, "white_plastic", mat, [(0.55, 7.6), (0.58, 8.4), (0.4, 8.7), (0.25, 9.1), (0, 9.15)], seg=10)


def white_cup(b):
    x, y = WHITE_CUP
    mat = Matrix.Translation(P(x, y, CZ))
    lathe(b, "white_plastic", mat, [(0, 0), (1.3, 0), (1.5, 2.6), (1.4, 2.6), (1.2, 0.2), (0, 0.2)], seg=12)


def produce_bag(b):
    x, y, h = PRODUCE
    mat = F(x, y, CZ, h)
    for px, py, r, s in ((-1.6, 0.4, 1.6, 1.35), (0.9, -0.3, 1.5, 1.4), (2.6, 0.8, 1.3, 1.3), (0.3, 1.9, 1.35, 1.3)):
        lathe(b, "potato", mat @ Matrix.Translation(P(px, py, r * 0.8)) @ S(s, 1.0, 0.8),
              [(0, -r), (r * 0.7, -r * 0.7), (r, 0), (r * 0.7, r * 0.7), (0, r)], seg=8)
    lathe(b, "clear", mat @ Matrix.Translation(P(0.5, 0.6, 0)) @ S(1.55, 1.0, 1.0),
          [(0, 0.02), (3.4, 0.02), (3.1, 2.4), (2.2, 3.2), (0, 3.4)], seg=10)
    # the knotted neck of the bag, flopped toward the room
    b.sweep("clear", [mat @ P(4.8, 0.9, 1.0), mat @ P(6.6, 1.6, 0.35), mat @ P(8.0, 1.2, 0.15)],
            [(-m(1.6), -m(0.05)), (m(1.6), -m(0.05)), (m(1.6), m(0.05)), (-m(1.6), m(0.05))], up=(0, 0, 1))


def knife_block(b):
    x, y, h = KNIFE_BLOCK
    mat = F(x, y, CZ, h)
    W, D, Hf, Hb = 4.6, 8.0, 4.8, 9.6
    # side profile (local y, z): front at -y is low, top slopes up to the back
    outline_yz = [(-D / 2, 0), (D / 2, 0), (D / 2, Hb), (D / 2 - 1.2, Hb), (-D / 2, Hf)]
    # build as prism along local x: outline in (y, z), extrude x
    vs0 = [b.bm.verts.new(mat @ P(-W / 2, yy, zz)) for yy, zz in outline_yz]
    vs1 = [b.bm.verts.new(mat @ P(W / 2, yy, zz)) for yy, zz in outline_yz]
    n = len(outline_yz)
    side_faces = []
    for i in range(n):
        j = (i + 1) % n
        side_faces.append(b.bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i])))
    caps = [b.bm.faces.new(vs0), b.bm.faces.new(list(reversed(vs1)))]
    b._tag(side_faces, "bamboo")
    b._tag(caps, "bamboo")
    # the sloped top (edge from (D/2-1.2, Hb) to (-D/2, Hf)) carries the slots
    b._tag([side_faces[3]], "block_top")
    for f in side_faces + caps:
        rec_local(f, "block_top" if f is side_faces[3] else "bamboo", mat)
    # knife handles standing out of the slots, leaning back with the slope normal
    for i, (u, s) in enumerate(((-1.4, 0.25), (-0.45, 0.45), (0.5, 0.65), (1.4, 0.35), (-0.9, 0.8))):
        yy = -D / 2 + (D - 1.2) * s
        zz = Hf + (Hb - Hf) * s
        hm = mat @ Matrix.Translation(P(u, yy, zz)) @ RX(-22 - 4 * i)
        lbox(b, "black_plastic", hm, -0.28, 0.28, -0.42, 0.42, 0.0, 4.4, bevel=0.14)
        lbox(b, "chrome", hm, -0.3, 0.3, -0.44, 0.44, 0.0, 0.35)
    # honing steel: round black handle
    hm = mat @ Matrix.Translation(P(1.5, -D / 2 + (D - 1.2) * 0.85, Hf + (Hb - Hf) * 0.85)) @ RX(-30)
    cyl(b, "black_plastic", hm, 0.45, 0.0, 4.0, seg=8)


def bread(b):
    x, y, h = BREAD
    mat = F(x, y, CZ, h)
    lathe(b, "bread", mat @ S(1.18, 1.0, 1.0),
          [(0, 0.05), (3.3, 0.05), (3.7, 0.8), (3.5, 2.4), (2.6, 3.7), (1.3, 4.3), (0, 4.45)], seg=14)
    # white round sticker on the top
    lathe(b, "label_white", mat @ Matrix.Translation(P(-1.0, 0.3, 0)) @ RY(-22),
          [(0, 4.45), (1.25, 4.45), (1.25, 4.5), (0, 4.5)], seg=10)
    # loose bag tail toward the counter front
    b.sweep("clear", [mat @ P(4.2, -0.5, 1.2), mat @ P(6.4, -1.6, 0.4), mat @ P(8.4, -2.2, 0.15)],
            [(-m(2.2), -m(0.05)), (m(2.2), -m(0.05)), (m(2.2), m(0.05)), (-m(2.2), m(0.05))], up=(0, 0, 1))


def pizza_box(b):
    x, y, h = PIZZA
    mat = F(x, y, CZ, h)
    s = 11.4 / 2
    pbox(b, mat, -s, s, -s, s, 0.0, 1.6, {"+z": "pizza_top", "-z": "green_box", "all": "pizza_side"})
    return CZ + 1.6


def onions(b, ztop):
    x, y = ONIONS
    spots = [(-2.4, -0.9, 1.55), (0.6, -1.4, 1.6), (3.1, -0.2, 1.5), (-1.2, 1.7, 1.5), (1.8, 1.9, 1.55),
             (0.1, 0.3, 1.45)]
    for i, (dx, dy, r) in enumerate(spots):
        z0 = ztop + (2.3 if i == 5 else 0.0)
        mat = F(x + dx, y + dy, z0, 30 * i) @ RY(12 * ((i % 3) - 1))
        lathe(b, "onion", mat, [(0, 0.1), (r * 0.7, r * 0.3), (r, r * 0.95), (r * 0.75, r * 1.6), (0.25, r * 2.0),
                                (0.08, r * 2.25), (0, r * 2.3)], seg=9)
    # the red mesh bag is painted onto the onion skins (see textures.py)
    # paper tag on the top
    lbox(b, "label_white", F(x - 1.0, y - 0.2, ztop + 5.3, 25) @ RX(-35), -1.4, 1.4, -0.9, 0.9, 0.0, 0.05)


# --- north counter, west ----------------------------------------------------------------

def kettle(b):
    x, y = KETTLE
    base = Matrix.Translation(P(x, y, CZ))
    lbox(b, "black_plastic", base, -3.3, 3.3, -3.3, 3.3, 0.0, 0.8, bevel=0.35)      # square base plate
    body = Matrix.Translation(P(x + 0.2, y, CZ + 0.75))
    lathe(b, "black_plastic", body, [(0, 0), (2.7, 0), (2.9, 0.3), (2.9, 4.2), (2.5, 5.3), (1.3, 5.9), (1.25, 6.3),
                                     (0.4, 6.4), (0.35, 7.0), (0, 7.1)], seg=16)
    # gooseneck spout from the low front (west) of the body, rising and bending out
    sp = [(x - 2.4, y, CZ + 1.6), (x - 3.4, y, CZ + 2.6), (x - 4.2, y, CZ + 5.4), (x - 4.6, y, CZ + 7.3),
          (x - 5.3, y, CZ + 7.9), (x - 6.3, y, CZ + 7.4)]
    b.sweep("black_plastic", [P(*p) for p in common.smooth_path([Vector(p) for p in sp], 3)],
            common.circle_profile(m(0.28), 6))
    # handle on the east side
    hd = [(x + 2.8, y, CZ + 1.8), (x + 4.4, y, CZ + 2.6), (x + 4.7, y, CZ + 4.8), (x + 4.2, y, CZ + 6.0),
          (x + 2.9, y, CZ + 5.6)]
    b.sweep("black_plastic", [P(*p) for p in common.smooth_path([Vector(p) for p in hd], 3)],
            [(-m(0.35), -m(0.45)), (m(0.35), -m(0.45)), (m(0.35), m(0.45)), (-m(0.35), m(0.45))],
            up=(0, 1, 0))
    # cord from the base's back to the wall outlet
    ox, oz = OUTLET
    cord(b, "black_plastic", [(x + 0.6, y + 3.3, CZ + 0.3), (x + 1.2, y + 5.2, CZ + 0.1), (ox - 2.5, SPLASH_Y - 0.4, CZ + 0.1),
                              (ox - 1.5, SPLASH_Y - 0.2, SPLASH_TOP - 0.5), (ox - 0.6, WALL_Y - 0.5, oz - 1.4),
                              (ox - 0.6, WALL_Y - 0.9, oz - 0.6)])
    lbox(b, "black_plastic", Matrix.Identity(4), ox - 1.2, ox, WALL_Y - 1.1, WALL_Y, oz - 0.7, oz + 0.4)


def glass_lid(b):
    x, y = GLASS_LID
    mat = Matrix.Translation(P(x, y, CZ))
    lathe(b, "chrome", mat, [(3.85, 0.0), (4.15, 0.0), (4.15, 0.35), (3.85, 0.4)], seg=18)
    lathe(b, "clear", mat, [(3.85, 0.35), (2.5, 0.9), (0.9, 1.15), (0, 1.2), (0, 1.1), (0.9, 1.05), (2.5, 0.8),
                            (3.85, 0.25)], seg=18)
    lathe(b, "black_plastic", mat, [(0, 1.15), (0.5, 1.15), (0.4, 1.5), (0.8, 1.7), (0.75, 2.0), (0, 2.05)], seg=8)


def rice_cooker(b):
    x, y = RICE
    mat = Matrix.Translation(P(x, y, CZ))
    lathe(b, "white_plastic", mat, [(0, 0), (3.6, 0), (4.1, 0.5), (4.3, 1.6), (4.3, 6.4), (4.1, 7.1), (3.75, 7.3)],
          seg=20)
    # black inner pot rim and inside
    lathe(b, "pot_dark", mat, [(3.75, 7.3), (3.7, 7.5), (3.55, 7.5), (3.5, 3.2), (0, 3.2)], seg=20)
    # front control panel (faces the room, -y)
    pbox(b, F(x, y - 4.05, CZ), -1.4, 1.4, -0.5, 0.2, 1.2, 4.8, {"-y": "rice_front", "all": "white_plastic"})
    lbox(b, "black_plastic", F(x, y - 4.55, CZ), -0.45, 0.45, -0.35, 0.0, 1.6, 2.6, bevel=0.1)   # switch
    # side lugs
    for s in (-1, 1):
        lbox(b, "white_plastic", F(x + s * 4.4, y, CZ), -0.5, 0.5, -1.3, 1.3, 5.2, 6.4, bevel=0.2)
    # white cord curling out to the west and back to the wall
    ox, oz = OUTLET
    cord(b, "cord_white", [(x - 3.9, y + 1.8, CZ + 1.0), (x - 4.8, y + 2.6, CZ + 0.1), (x - 6.2, y + 0.5, CZ + 0.1),
                           (x - 6.8, y - 3.2, CZ + 0.1), (x - 4.2, y - 5.6, CZ + 0.1), (x - 8.4, y - 5.2, CZ + 0.1),
                           (x - 7.6, y + 3.8, CZ + 0.1), (ox + 0.4, SPLASH_Y - 0.4, CZ + 0.1),
                           (ox + 0.6, SPLASH_Y - 0.2, SPLASH_TOP - 0.5), (ox + 0.7, WALL_Y - 0.5, oz - 1.4),
                           (ox + 0.7, WALL_Y - 0.9, oz - 0.6)])
    lbox(b, "white_plastic", Matrix.Identity(4), ox + 0.1, ox + 1.3, WALL_Y - 1.1, WALL_Y, oz - 0.7, oz + 0.4)


def glass_bowl(b):
    x, y = BOWL
    mat = Matrix.Translation(P(x, y, CZ))
    lathe(b, "clear", mat, [(0, 0), (1.3, 0), (1.8, 2.2), (1.65, 2.2), (1.2, 0.25), (0, 0.25)], seg=12)


# --- north counter, east ----------------------------------------------------------------

def coffee_box(b):
    x, y = COFFEE_BOX
    mat = F(x, y, CZ, 90)                        # its printed face looks east at the maker
    pbox(b, mat, -2.5, 2.5, -1.6, 1.6, 0.0, 4.6, {"+y": "kraft_print", "-y": "kraft_print", "all": "kraft"})
    # black coffee bag lying on it, folded over
    lbox(b, "bag_black", mat @ RX(6), -2.9, 2.9, -1.7, 1.5, 4.6, 6.4, bevel=0.5)


def drip_maker(b):
    x, y = DRIP
    mat = F(x, y, CZ)
    W, D = 7.0, 9.4
    y0 = -D / 2
    # base with the warming plate and the front control strip
    lbox(b, "black_plastic", mat, -W / 2, W / 2, y0, D / 2, 0.0, 1.6, bevel=0.35)
    pbox(b, mat, -W / 2 + 0.4, W / 2 - 0.4, y0 - 0.05, y0 + 0.3, 0.25, 1.4, {"-y": "display", "all": "black_plastic"})
    # rear tower with the reservoir
    lbox(b, "black_plastic", mat, -W / 2, W / 2, D / 2 - 3.6, D / 2, 1.6, 10.6, bevel=0.5)
    # brew basket housing on the front of the tower (with the parody badge)
    bm_ = mat @ Matrix.Translation(P(0, 0.6, 7.3))
    lathe(b, "black_plastic", bm_, [(0, 0), (1.3, 0), (2.9, 2.2), (3.3, 3.2), (3.3, 3.35), (0, 3.35)], seg=14)
    pbox(b, bm_ @ Matrix.Translation(P(0, -2.72, 2.0)) @ RX(36), -1.6, 1.6, -0.12, 0.0, -0.45, 0.45,
         {"-y": "coffee_badge", "all": "black_plastic"})
    # lid flipped up at the back, standing on its hinge
    lm = mat @ Matrix.Translation(P(0, D / 2 - 1.4, 10.4)) @ RX(-88)
    lathe(b, "black_plastic", lm @ Matrix.Translation(P(0, -3.2, 0)),
          [(0, 0), (3.2, 0), (3.2, 0.5), (2.8, 0.8), (0, 0.8)], seg=14)
    # glass carafe on the plate: clear jug, black collar, lid and handle
    cm = mat @ Matrix.Translation(P(0, -1.3, 1.6))
    lathe(b, "glass_dark", cm, [(0, 0), (2.4, 0), (2.9, 0.8), (2.9, 3.4), (2.4, 4.6), (0, 4.6)], seg=14)
    lathe(b, "black_plastic", cm, [(2.45, 4.3), (2.6, 4.3), (2.6, 5.2), (0, 5.4)], seg=14)
    b.sweep("black_plastic", [cm @ P(2.5, -1.5, 4.9), cm @ P(3.4, -2.4, 4.6), cm @ P(3.6, -2.7, 2.6), cm @ P(2.2, -1.6, 1.2)],
            [(-m(0.3), -m(0.4)), (m(0.3), -m(0.4)), (m(0.3), m(0.4)), (-m(0.3), m(0.4))], up=(0, 0, 1))


def grinder(b):
    (ax, ay), (bx_, by_) = GRINDER
    d = Vector((bx_ - ax, by_ - ay, 0))
    h = math.degrees(math.atan2(d.y, d.x))
    r = 1.0
    mat = F(ax, ay, CZ + r, h) @ RY(90)
    lathe(b, "steel", mat, [(0, 0), (r, 0), (r, d.length - 1.0), (0, d.length - 1.0)], seg=12)
    lathe(b, "black_plastic", mat, [(0, d.length - 1.0), (r * 0.95, d.length - 1.0), (r * 0.9, d.length), (0, d.length)], seg=12)


def pod_maker(b):
    x, y = POD
    mat = F(x, y, CZ)
    W, D, H = 4.6, 8.8, 11.2
    y0 = -D / 2
    lbox(b, "black_plastic", mat, -W / 2, W / 2, y0 + 3.4, D / 2, 0.0, H - 1.6, bevel=0.5)     # tank body
    lbox(b, "black_plastic", mat, -W / 2 - 0.1, W / 2 + 0.1, y0 + 0.4, D / 2, H - 1.8, H, bevel=0.6)   # head/lid
    lbox(b, "black_plastic", mat, -W / 2, W / 2, y0 + 1.2, y0 + 3.6, 0.0, 0.9, bevel=0.3)      # cup stand
    cyl(b, "steel", mat @ Matrix.Translation(P(0, y0 + 1.6, H - 2.4)), 0.35, 0.0, 0.6, seg=6)  # nozzle
    tx, ty = DRIP_TRAY
    lathe(b, "black_plastic", Matrix.Translation(P(tx, ty, CZ)),
          [(0, 0), (1.9, 0), (1.95, 0.5), (1.7, 0.5), (1.6, 0.3), (0, 0.3)], seg=14)
    lathe(b, "rack_grey", Matrix.Translation(P(tx, ty, CZ)), [(0, 0.32), (1.6, 0.32), (0, 0.34)], seg=10)


def bean_tub(b):
    x, y, h = BEANS
    mat = F(x, y, CZ, h)
    lbox(b, "beans", mat, -1.8, 1.8, -2.3, 2.3, 0.1, 1.4, bevel=0.2)
    lbox(b, "clear", mat, -2.0, 2.0, -2.5, 2.5, 0.0, 2.4, bevel=0.3)


def spray_bottle(b):
    x, y = SPRAY
    mat = Matrix.Translation(P(x, y, CZ))
    lathe(b, "yellow_plastic", mat, [(0, 0), (1.45, 0), (1.55, 0.3), (1.55, 5.6), (1.0, 6.8), (0.6, 7.2)], seg=12)
    lathe(b, "spray_label", mat, [(1.57, 1.2), (1.57, 4.8)], seg=12, uv=True)
    lathe(b, "spray_white", mat, [(0.6, 7.1), (0.62, 7.8), (0.5, 7.8), (0, 7.85)], seg=8)
    sm = mat @ RZ(-110)
    lbox(b, "spray_white", sm, -0.55, 0.55, -0.6, 2.4, 7.8, 9.1, bevel=0.25)   # trigger head, nozzle toward the room
    lbox(b, "spray_white", sm, -0.3, 0.3, 0.6, 1.2, 6.2, 7.9, bevel=0.1)       # trigger


def paper_towels(b):
    x, y = TOWEL_ROLL
    mat = Matrix.Translation(P(x, y, CZ))
    lathe(b, "white_plastic", mat, [(0, 0), (3.1, 0), (3.2, 0.2), (2.9, 0.55), (0.6, 0.6), (0, 0.6)], seg=16)
    cyl(b, "white_plastic", mat, 0.4, 0.6, 12.4, seg=8)
    lathe(b, "white_plastic", mat @ Matrix.Translation(P(0, 0, 12.4)),
          [(0, 0), (0.55, 0.2), (0.78, 0.75), (0.55, 1.3), (0, 1.5)], seg=10)
    R, H = 2.95, 11.0
    lathe(b, "roll_side", mat, [(R, 0.65), (R, 0.65 + H)], seg=16, uv=True)
    lathe(b, "paper_white", mat, [(0.8, 0.65), (R, 0.65)], seg=16)
    lathe(b, "paper_white", mat, [(R, 0.65 + H), (0.8, 0.65 + H)], seg=16)
    lathe(b, "kraft", mat, [(0.8, 0.65 + H), (0.8, 0.65)], seg=10)
    # the loose sheet peeling off the front-right of the roll
    zc = CZ + 0.65 + H / 2
    pts = []
    for i, a in enumerate((-50, -80, -100)):
        rr = R + 0.05 + i * 0.25
        pts.append(P(x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a)), zc))
    pts.append(P(x - 0.9, y - R - 1.6, zc))
    b.sweep("roll_side", pts, [(-m(0.03), -m(H / 2 - 0.1)), (m(0.03), -m(H / 2 - 0.1)), (m(0.03), m(H / 2 - 0.1)),
                              (-m(0.03), m(H / 2 - 0.1))], up=(0, 0, 1))


def cards(b):
    for x, y, h in CARDS:
        lbox(b, "paper_white", F(x, y, CZ, h), -1.2, 1.2, -1.7, 1.7, 0.0, 0.03)


# --- fridge top ------------------------------------------------------------------------

def napkins(b):
    x, y = NAPKINS
    z = FZ
    for i, (dx, dy, dh) in enumerate(((0.0, 0.0, 0.0), (0.2, -0.3, 3.0), (-0.1, 0.2, -4.0))):
        mat = F(x + dx, y + dy, z + i * 5.5, dh)
        pbox(b, mat, -3.7, 3.7, -4.2, 4.2, 0.0, 5.5,
             {"+z": "napkin_top", "-z": "napkin_white", "+x": "napkin_side", "-x": "napkin_side",
              "-y": "napkin_top", "+y": "napkin_top"})


def pink_box(b):
    x, y = PINK_BOX
    pbox(b, F(x, y, FZ), -3.5, 3.5, -1.4, 1.4, 0.0, 9.5,
         {"-y": "pink_face", "+y": "pink_face", "all": "pink"})


def plates(b):
    x, y = PLATES
    pbox(b, F(x, y, FZ, 2.0), -4.25, 4.25, -4.25, 4.25, 0.0, 7.0,
         {"+z": "plates_top", "-z": "plates_blue", "all": "plates_side"})


def filter_bag(b):
    x, y = FILTER_BAG
    mat = Matrix.Translation(P(x, y, FZ))
    lathe(b, "filters_side", mat, [(2.4, 0.0), (3.4, 3.4)], seg=16, uv=True)
    lathe(b, "filters_white", mat, [(0, 0.0), (2.4, 0.0)], seg=16)
    lathe(b, "filters_white", mat, [(3.4, 3.4), (0, 3.4)], seg=16)
    lathe(b, "clear", mat, [(0, 0.0), (2.6, 0.0), (3.65, 3.5), (3.2, 4.0), (0, 4.1)], seg=12)
    # round dark label on the front of the bag
    pbox(b, F(x, y - 3.05, FZ + 2.0) @ RX(17), -1.0, 1.0, -0.02, 0.02, -1.0, 1.0,
         {"-y": "filter_label", "all": "navy"})


def filter_sleeve(b):
    x, y = FILTER_SLEEVE
    r, L = 2.7, 6.4
    mat = Matrix.Translation(P(x, y - L / 2, FZ + r)) @ RX(-90)
    lathe(b, "filters_side", mat, [(r, 0.0), (r, L)], seg=16, uv=True)
    lathe(b, "filters_end", mat, [(0, 0.0), (r, 0.0)], seg=16, uv=True)
    lathe(b, "filters_end", mat, [(r, L), (0, L)], seg=16, uv=True)
    lathe(b, "navy", mat, [(r + 0.04, L * 0.35), (r + 0.04, L * 0.75)], seg=16)


def paper_cups(b):
    x, y = CUPS
    mat = Matrix.Translation(P(x, y, FZ))
    lathe(b, "cups", mat, [(1.5, 0.0), (1.95, 10.0)], seg=16, uv=True)
    lathe(b, "navy", mat, [(0, 0.0), (1.5, 0.0)], seg=12)
    lathe(b, "cups_top", mat, [(1.95, 10.0), (2.0, 10.25), (1.8, 10.25), (0, 10.1)], seg=16, uv=False)


def towel_pack(b):
    x0, x1, y0, y1, z1 = TOWEL_PACK
    pbox(b, Matrix.Identity(4), x0, x1, y0, y1, FZ, z1,
         {"-x": "tpack_side", "+x": "tpack_side", "-y": "tpack_end", "+y": "tpack_end",
          "+z": "tpack_top", "-z": "tpack_top"})


# --- build ------------------------------------------------------------------------------

def build(coll):
    _PENDING.clear()
    CUSTOM.clear()
    b = common.Builder(REGIONS)
    zb = dish_rack(b)
    pot_lid(b, zb)
    tin_can(b, zb)
    clear_lid(b, zb)
    funnel(b)
    hand_towel(b)
    soap_pump(b)
    sink_stopper(b)
    dish_brush(b)
    tool(b)
    dish_soap(b)
    white_cup(b)
    produce_bag(b)
    knife_block(b)
    bread(b)
    onions(b, pizza_box(b))
    kettle(b)
    glass_lid(b)
    rice_cooker(b)
    glass_bowl(b)
    coffee_box(b)
    drip_maker(b)
    grinder(b)
    pod_maker(b)
    bean_tub(b)
    spray_bottle(b)
    paper_towels(b)
    cards(b)
    napkins(b)
    pink_box(b)
    plates(b)
    filter_bag(b)
    filter_sleeve(b)
    paper_cups(b)
    towel_pack(b)
    b.bm.verts.index_update()
    b.bm.faces.index_update()
    for f, reg, uvs in _PENDING:
        CUSTOM.append((f.index, reg, {v.index: uv for v, uv in uvs.items()}))
    _PENDING.clear()
    return [b.to_object(NAME, coll)]


def texture(objs):
    import atlas_layout
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    # preview only: show the clear plastic and glass as see-through in the Blender renders
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    common.atlas_uvs(ob, ATLAS)
    me = ob.data
    uvl = me.uv_layers["UVMap"]
    for fi, reg, uvs in CUSTOM:
        u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, reg)
        p = me.polygons[fi]
        for li in p.loop_indices:
            fu, fv = uvs[me.loops[li].vertex_index]
            uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))
    common.collapse_materials(ob, {r: (clear if r in CLEAR_REGIONS else mat) for r in REGIONS})
