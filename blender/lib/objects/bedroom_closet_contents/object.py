"""Bedroom closet contents: the inside of the bypass-door closet east of the bedroom.

  joinery   a white melamine shelf on 1x4 cleats (back and both end walls) with a
            light pine hanging rod under it, socketed in the end cleats
  garments  a full rod: white plastic hangers (silver wire hooks on the north run, all-
            plastic further south, about one in four teal), clip hangers for the skirts and
            trousers at the north end, and the clothes as low-poly lofted cloth (shoulders
            sloping off the hanger arms, hanging sleeve tubes on the tops and jackets,
            vertical drape folds, softly flared wavy hems, a small lean each):
            dark coats, a white dress with black leaf sprays, a long crimson dress with
            gold glitter swirls, a crimson top, a pink shirt, a blue gingham shirt, a
            floral shirt, a breton stripe, a red plaid flannel, a tan blazer (black
            sleeve buttons), a white puffer, a magenta cardigan, a cream blouse, a beige
            knit, navy and grey tees, denim on a chrome multi-hook at the south end
  shelf     hats and caps (plain: no text), a black bag with a tan leather handle, a
            beige towel and an orange pouch hanging over the edge, a light blue fleece
            scarf hanging down past the rod, a pink/yellow/teal knit, black piles, white
            folded fabric, a closed paper parasol standing in the south-east corner
  floor     black strappy shoes, a black wedge boot, brown leather shoes, sneakers (dark
            grey, grey, pink-grey), a grey collapsible laundry hamper with dark denim in it,
            a pale plastic bag and a black bag
All generic, no logos or text (the caps' print, the tee's chest print, the jeans' patch and
the sneakers' side marks are left out).

Source of truth: scripted. Photos Reference/cupboards_drawers sorted index 19 (north half:
the leaves are slid south, the north jamb's strike plate shows at the left) and 20 (south
half: the leaves are slid north, the south leaf's round finger cup shows at the left, and
the black tote on the closet's south wall hangs at the right edge; that tote belongs to
hanging_bags). Positions along the rod are read off the photos linearly (photo 19 px ->
y 197.75 .. 167.75, photo 20 px -> y 167 .. 135), hem heights from the rod (z 64) and the
floor in each photo.

Frame: PLAN coordinates (inches here, metres in the mesh). Origin = plan (0, 0, 0), +X east,
+Y north, Z up; the package goes on a marker at (0, 0, 0) with no rotation.

Dimensions (inches, plan):
  closet interior x 252.45 .. 274.6, y 135.1 .. 197.75 (shell_layout WALLS)       S
  shelf top z 67, 0.75 thick, front edge x 260.6 (14 deep), wall to wall          EST/PHOTO
  cleats 0.75 x 3.5 under the shelf on the back and end walls                     EST
  rod 1.375 dia, centre x 263.0, z 63.75 (1.9 in under the shelf)                 EST/PHOTO
  hangers 17 wide, neck z 61, hook wire 0.16 (metal) / 0.24 (plastic)             EST
  garments 14-21 wide, 0.6-5 thick; hems z 0-42 per the photos (+-3)             PHOTO
  hamper 18 x 12.5 x 21, centre (261.0, 148.0), turned 12 deg                     EST/PHOTO
  parasol ~31 long standing at (271.6, 137.4)                                      EST
  shoes 9-10.5 long, toes west toward the doors                                    EST/PHOTO
Hidden backs (behind the front garments, the back of the shelf piles) are guessed.
"""

import math
import os
import random
import sys

import bmesh
from mathutils import Matrix, Vector

import atlas_layout
import common

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closet_data  # noqa: E402

NAME = "bedroom_closet_contents"
ATLAS = closet_data.ATLAS
REGIONS = list(ATLAS["regions"])
FLAT = set(closet_data.FLAT)
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "none"
STATIC = True
VIEWS = [("from_bedroom", 270, 8, 0.75), ("from_bedroom_high", 250, 30, 0.8)]

IN = 0.0254

# --- closet (inches, plan) ---------------------------------------------------------------
X_FRONT, X_BACK = 252.45, 274.6        # S: closet front wall east face, east exterior wall
Y_S, Y_N = 135.1, 197.75               # S: closet south wall north face, bath wall south face
SHELF_TOP, SHELF_T, SHELF_FRONT = 67.0, 0.75, 260.6
CLEAT_T, CLEAT_H = 0.75, 3.5
ROD_X, ROD_Z, ROD_R = 263.0, 63.75, 0.6875
NECK_Z = 61.0
HANGER_HALF, HANGER_DROP = 8.5, 2.4


class B(common.Builder):
    """Builder in inches with a UV layer written per part (flat colours map to the middle
    of their cell, prints get per-part box or garment projection)."""

    def __init__(self):
        super().__init__(REGIONS)
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def rect(self, region):
        u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, region)
        if region in FLAT:                 # keep to the cell's middle: no bleed at any mip
            cu, cv, hu, hv = (u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) * 0.3, (v1 - v0) * 0.3
            return cu - hu, cv - hv, cu + hu, cv + hv
        return u0, v0, u1, v1

    def boxmap(self, faces, region, along=None):
        """Per-face dominant-axis projection normalised to these faces' own bounds.
        along="y": every face maps u along Y, v along Z (rods, grain along the length)."""
        self._tag(faces, region)
        u0, v0, u1, v1 = self.rect(region)
        vs = {v for f in faces for v in f.verts}
        lo = [min(v.co[i] for v in vs) for i in range(3)]
        hi = [max(v.co[i] for v in vs) for i in range(3)]
        for f in faces:
            f.normal_update()
            if along == "y":
                ua, va = 1, 2
            else:
                ax = max(range(3), key=lambda i: abs(f.normal[i]))
                ua, va = [(1, 2), (0, 2), (0, 1)][ax]
            for lp in f.loops:
                co = lp.vert.co
                fu = (co[ua] - lo[ua]) / max(hi[ua] - lo[ua], 1e-6)
                fv = (co[va] - lo[va]) / max(hi[va] - lo[va], 1e-6)
                lp[self.uv].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))

    def setuv(self, face, uvs, region):
        u0, v0, u1, v1 = self.rect(region)
        face.material_index = self.idx(region)
        for lp, (fu, fv) in zip(face.loops, uvs):
            fu, fv = min(max(fu, 0.0), 1.0), min(max(fv, 0.0), 1.0)
            lp[self.uv].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))

    def finish(self, name, coll, clamp=False):
        if clamp:       # bunched cloth stops at the closet walls instead of poking through
            for v in self.bm.verts:
                v.co.x = min(max(v.co.x, X_FRONT + 0.25), X_BACK - 0.2)
                v.co.y = min(max(v.co.y, Y_S + 0.2), Y_N - 0.2)
        bmesh.ops.scale(self.bm, vec=(IN, IN, IN), verts=self.bm.verts)
        return self.to_object(name, coll)

    # parts --------------------------------------------------------------------------
    def bx(self, region, lo, hi, matrix=None):
        f = self.box(region, lo, hi, matrix=matrix)
        self.boxmap(f, region)
        return f

    def sw(self, region, pts, profile, up=(0, 0, 1), along=None):
        f = self.sweep(region, pts, profile, up=up)
        self.boxmap(f, region, along)
        return f

    def lump(self, region, c, size, seed, rough=0.05, yaw=0.0, base=None, segs=(11, 6), crumple=0.0):
        """A squashed, noisy sphere: fabric piles, bags, hat crowns. base = z below which
        the verts flatten onto the resting surface. crumple > 0 adds creased fabric: a few
        sharp ridges (|sin| bands in random directions) and a slumped, flatter top."""
        rng = random.Random(seed)
        r = bmesh.ops.create_uvsphere(self.bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
        verts = r["verts"]
        cy, sy = math.cos(yaw), math.sin(yaw)
        bands = [(Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.6, 0.6))).normalized(),
                  rng.uniform(2.2, 3.6), rng.uniform(0, 6.3)) for _ in range(3)]
        for v in verts:
            x, y, z = v.co
            k = 1.0 + rng.uniform(-rough, rough)
            if crumple:
                ridge = sum(abs(math.sin(f * d.dot(v.co) + ph)) - 0.64 for d, f, ph in bands)
                k += crumple * ridge
                if z > 0.3:                     # cloth slumps: the top flattens out
                    z = 0.3 + (z - 0.3) * 0.6
            x, y, z = x * size[0] / 2 * k, y * size[1] / 2 * k, z * size[2] / 2 * k
            x, y = x * cy - y * sy, x * sy + y * cy
            z = z + size[2] / 2
            v.co = Vector((c[0] + x, c[1] + y, c[2] + z))
            if base is not None and v.co.z < base:
                v.co.z = base
        faces = list({f for v in verts for f in v.link_faces})
        self.boxmap(faces, region)
        return faces

    def lathe(self, region, c, profile, seg=8, tilt=None):
        """Rings of (radius, z) around a vertical axis through c (x, y), closed both ends."""
        rings = []
        for rad, z in profile:
            ring = []
            for k in range(seg):
                a = 2 * math.pi * k / seg
                p = Vector((rad * math.cos(a), rad * math.sin(a), z))
                if tilt is not None:          # lean about the foot of the axis
                    p = tilt @ (p - Vector((0, 0, profile[0][1]))) + Vector((0, 0, profile[0][1]))
                ring.append(self.bm.verts.new((c[0] + p.x, c[1] + p.y, p.z)))
            rings.append(ring)
        faces = []
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(seg):
                faces.append(self.bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k])))
        faces.append(self.bm.faces.new(list(reversed(rings[0]))))
        faces.append(self.bm.faces.new(rings[-1]))
        self.boxmap(faces, region)
        return faces


# --- joinery -------------------------------------------------------------------------------

def joinery(coll):
    b = B()
    b.bx("shelf_white", (SHELF_FRONT, Y_S, SHELF_TOP - SHELF_T), (X_BACK, Y_N, SHELF_TOP))
    z0 = SHELF_TOP - SHELF_T - CLEAT_H
    b.bx("cleat_white", (X_BACK - CLEAT_T, Y_S + CLEAT_T, z0), (X_BACK, Y_N - CLEAT_T, SHELF_TOP - SHELF_T))
    for y0, y1 in ((Y_S, Y_S + CLEAT_T), (Y_N - CLEAT_T, Y_N)):
        b.bx("cleat_white", (SHELF_FRONT + 0.5, y0, z0), (X_BACK, y1, SHELF_TOP - SHELF_T))
    f = b.cylinder("pine", (ROD_X, (Y_S + Y_N) / 2, ROD_Z), ROD_R, Y_N - Y_S - 2 * CLEAT_T + 0.2,
                   axis="Y", segments=10)
    b.boxmap(f, "pine", along="y")
    # round white rod sockets on the end cleats
    for y in (Y_S + CLEAT_T + 0.15, Y_N - CLEAT_T - 0.15):
        f = b.cylinder("cleat_white", (ROD_X, y, ROD_Z), 1.15, 0.3, axis="Y", segments=10)
        b.boxmap(f, "cleat_white")
    return b.finish(NAME, coll)


# --- garments ------------------------------------------------------------------------------
# (region, y, kind, hem z, thickness, width, turn deg, hanger)
#   kind: top (shoulders on the hanger), dress (flares to the hem), clip (skirts and
#         trousers on a clip bar), puffer (quilted, thick)
#   hanger: wm white plastic + silver wire hook, w white plastic, t teal plastic,
#           c clip hanger (silver hook, white bar and clips), - none (on the multi-hook)
GARMENTS = [
    # photo 19, north half (north wall -> the leaves)
    ("grey_trousers", 196.9, "dress", 6.0, 1.2, 15, -8, "wm"),
    ("black", 195.6, "dress", 3.0, 1.4, 16, 6, "wm"),
    ("taupe", 194.2, "clip", 19.0, 1.0, 13, -5, "c"),
    ("black_warm", 193.4, "clip", 22.0, 1.0, 13, 4, "c"),
    ("charcoal", 192.4, "clip", 33.0, 1.6, 15, -10, "c"),
    ("white_shirt", 191.4, "top", 27.0, 0.7, 16, 5, "wm"),
    ("pink", 190.7, "top", 36.5, 0.9, 16, -12, "wm"),
    ("floral", 189.6, "top", 33.0, 0.9, 16, 10, "wm"),
    ("gingham", 188.5, "top", 15.0, 0.9, 17, -6, "wm"),
    ("leaf_print", 186.4, "dress", 16.0, 5.0, 18, 30, "wm"),
    ("navy", 184.9, "top", 40.0, 0.7, 16, -8, "wm"),
    ("charcoal", 183.8, "top", 35.0, 2.0, 18, 14, "wm"),
    ("sequin", 182.7, "dress", 1.0, 1.4, 15, 8, "wm"),
    ("white_shirt", 181.4, "top", 22.5, 0.7, 16, -10, "wm"),
    ("crimson", 180.5, "top", 25.5, 1.6, 17, 22, "wm"),
    ("stripe", 179.3, "dress", 7.0, 0.9, 15, -6, "wm"),
    ("black", 178.1, "dress", 1.5, 0.8, 16, 5, "wm"),
    ("plaid", 177.0, "top", 11.0, 0.5, 17, -10, "wm"),
    ("black_warm", 176.3, "top", 20.0, 0.8, 17, 6, "wm"),
    ("maroon", 175.6, "top", 11.5, 0.5, 16, -14, "wm"),
    ("grey_denim", 174.8, "top", 19.5, 0.8, 18, 10, "w"),
    ("tan_blazer", 173.0, "top", 21.0, 3.6, 18, -40, "w"),
    ("black", 171.1, "top", 18.0, 2.6, 19, 8, "w"),
    ("grey_puffy", 169.7, "top", 20.0, 3.0, 19, -10, "w"),
    ("beige_jacket", 168.4, "top", 19.0, 2.0, 18, 12, "t"),
    # photo 20, south half (the leaves -> south wall)
    ("black", 166.6, "top", 18.5, 2.4, 19, -6, "t"),
    ("cream_jacket", 165.3, "top", 27.0, 1.6, 18, 14, "t"),
    ("crimson", 164.2, "top", 42.5, 0.8, 16, -8, "t"),
    ("puffer", 161.6, "puffer", 28.0, 8.5, 20, 12, "w"),
    ("magenta", 159.7, "top", 19.0, 0.9, 16, -6, "t"),
    ("dark_grey", 158.7, "top", 20.5, 1.8, 18, 6, "w"),
    ("white_shirt", 157.7, "top", 41.5, 0.6, 16, -10, "w"),
    ("mauve", 157.0, "top", 22.0, 1.0, 16, 8, "w"),
    ("slate_blue", 155.8, "top", 23.5, 1.2, 17, 12, "w"),
    ("white_shirt", 154.9, "top", 41.0, 0.6, 16, -6, "t"),
    ("light_grey", 154.2, "top", 22.5, 0.8, 16, 4, "w"),
    ("cream_blouse", 152.4, "top", 29.5, 1.6, 17, 24, "w"),
    ("black", 151.0, "top", 24.0, 1.0, 16, -8, "w"),
    ("white_shirt", 150.2, "top", 34.0, 0.6, 16, 6, "t"),
    ("beige_knit", 148.6, "top", 24.0, 1.3, 17, 20, "w"),
    ("white_shirt", 147.3, "top", 25.0, 0.8, 16, -8, "t"),
    ("black", 146.4, "top", 23.0, 1.2, 16, 5, "w"),
    ("grey_tee", 145.4, "top", 39.5, 0.6, 17, -12, "w"),
    ("light_grey", 144.6, "top", 29.0, 0.8, 16, 8, "w"),
    ("navy_dark", 143.8, "top", 41.5, 0.8, 17, 15, "t"),
    ("navy_jacket", 140.4, "top", 23.5, 2.6, 19, 12, "w"),
]
EMPTY_HANGERS = [(142.8, 4, "w"), (142.3, -6, "w"), (141.8, 10, "t"), (186.0, -4, "wm"),
                 (170.6, 6, "w")]
MULTI_HOOK_Y = 139.0
DENIM = ("denim", 139.6, "clip", 22.5, 2.6, 14, 6, "-")     # jeans folded over the hook's rungs


def _xf(y, turn):
    """Local (across, along, z) -> plan, turned about the vertical through the rod."""
    c, s = math.cos(math.radians(turn)), math.sin(math.radians(turn))

    def f(x, yy, z):
        return Vector((ROD_X + x * c - yy * s, y + x * s + yy * c, z))
    return f


SEG = 14          # body section points (7 a face: room for two or three folds)
SLEEVE_SEG = 6


def _section(seg):
    """Lens-shaped body section (unit half-width/half-thickness), counter-clockwise."""
    out = []
    for k in range(seg):
        a = 2 * math.pi * (k + 0.5) / seg
        ca, sa = math.cos(a), math.sin(a)
        out.append((math.copysign(abs(ca) ** 0.85, ca), sa))
    return out


SECTION = _section(SEG)


def _mirror_u(pts):
    """u round a closed section: 0 at the middle of one face, 1 at the other, and back, so
    a print keeps its scale all the way round with no seam."""
    n = len(pts)
    d = [0.0]
    for k in range(n):
        d.append(d[-1] + (pts[(k + 1) % n] - pts[k]).length)
    P = d[-1]
    d0 = d[n // 4]                      # about the middle of the -y face
    return [1 - abs(2 * (((d[k] - d0) / P) % 1.0) - 1) for k in range(n)]


def _loft(b, rings, uvs, region):
    """Quads between consecutive rings of equal size, both ends capped."""
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for k in range(n):
            k1 = (k + 1) % n
            f = b.bm.faces.new((rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]))
            b.setuv(f, (uvs[i][k], uvs[i][k1], uvs[i + 1][k1], uvs[i + 1][k]), region)
    for i, rev in ((0, True), (len(rings) - 1, False)):
        idx = list(range(n))[::-1] if rev else list(range(n))
        f = b.bm.faces.new([rings[i][k] for k in idx])
        b.setuv(f, [uvs[i][k] for k in idx], region)


def _shoulder_drop(x):
    """How far below the neck the cloth sits at |x| across: it follows the hanger arm out to
    its tip, then rolls off over the end."""
    r = abs(x) / HANGER_HALF
    return HANGER_DROP * min(r, 1.0) + 2.2 * max(0.0, r - 1.0) ** 1.3


def garment(b, spec, seed):
    """One garment on its hanger, scripted: a lofted body (sloped shoulders on the hanger
    arms, gentle vertical folds that deepen toward a softly flared, wavy hem), hanging
    sleeve tubes at the sides for tops/jackets/coats, and a small lean so neighbours
    overlap."""
    region, y, kind, hem, T, W, turn, _ = spec
    rng = random.Random(seed)
    turn += rng.uniform(-3, 3) if abs(turn) > 30 else rng.uniform(-8, 8)
    xf0 = _xf(y, turn)
    lean_x, lean_y = rng.uniform(-0.025, 0.025), rng.uniform(-0.07, 0.07)

    def P(x, yy, z):
        d = max(0.0, NECK_Z - z)
        return xf0(x + lean_x * d, yy + lean_y * d, z)

    sleeves = kind in ("top", "puffer")
    Tb = {"top": T * 1.1 + 0.4, "dress": T * 1.2 + 0.7}.get(kind, T)
    flare = {"dress": 1.35, "clip": 1.18 if W > 14 else 1.04, "top": 1.05, "puffer": 1.02}[kind]
    rings = []                                  # (z, half width, half thickness, follows shoulder)
    if kind == "clip":
        top = 53.0 if spec is DENIM else NECK_Z - 2.0
        rings.append((top, W * 0.48, Tb * 0.22, False))
        body_top = top - 1.2
        rings.append((body_top, W * 0.5, Tb * 0.4, False))
    else:
        rings.append((NECK_Z + 0.2, W * 0.12, Tb * 0.28, False))
        rings.append((NECK_Z - 0.8, W * 0.5, Tb * 0.38, True))
        body_top = NECK_Z - 5.5
        rings.append((body_top, W * 0.5, Tb * 0.5, True))
    length = body_top - hem
    if kind == "puffer":
        n = max(3, int(length / 4.0))
        for i in range(1, n + 1):
            pinch = 0.6 if i % 2 else 1.0              # quilted baffles: stitched lines pinch in
            hemband = 0.9 if i == n else 1.0           # elastic hem
            rings.append((body_top - length * i / n, W * 0.5 * (0.95 if i % 2 else 1.0) * hemband,
                          Tb * 0.5 * pinch * hemband, False))
    else:
        n = max(2, int(length / 9.0))
        for i in range(1, n + 1):
            t = i / n
            w = W * 0.5 * (1 + (flare - 1) * t ** 1.6)
            rings.append((body_top - length * t, w, Tb * 0.5 * (1.0 + 0.4 * t), False))
    zt, zb = rings[0][0], rings[-1][0]
    span = max(zt - zb, 1e-3)
    fq, ph, ph2 = rng.uniform(0.5, 0.8), rng.uniform(0, 6.3), rng.uniform(0, 6.3)
    usec = _mirror_u([Vector((px * W / 2, py * Tb / 2, 0)) for px, py in SECTION])
    verts, uvs = [], []
    for ri, (z, w, t, sh) in enumerate(rings):
        down = max(0.0, (body_top - z) / max(length, 1e-3))
        last = ri == len(rings) - 1
        ring, ruv = [], []
        for k, (px, py) in enumerate(SECTION):
            x, yy = w * px, t * py
            zz = z
            if sh:
                zz -= _shoulder_drop(x) * (1.0 if ri == 1 else 0.55)
            if ri >= 2:
                # vertical drape folds: the faces ripple across the width, deeper lower down
                amp = (0.45 + 0.12 * Tb) * (0.3 + 0.9 * down)
                yy += amp * math.sin(x * fq + ph) * (1 if py > 0 else -1)
                yy += 0.25 * amp * math.sin(x * fq * 2.3 + ph2)
                x += rng.uniform(-0.2, 0.2)
            if last:
                zz += 0.7 * math.sin(x * 0.7 + ph2) + rng.uniform(-0.3, 0.3)
            ring.append(b.bm.verts.new(P(x, yy, zz)))
            ruv.append((usec[k], (zz - zb) / span))
        verts.append(ring)
        uvs.append(ruv)
    _loft(b, verts, uvs, region)
    if not sleeves:
        return
    # sleeves: tubes hanging from the shoulder points, a little forward of the side seams
    long_ = hem < 36.0
    sr = 0.9 + 0.22 * T
    # print scale on the sleeves matches the body's (u spans half the body's girth)
    us = min(1.0, math.pi * sr / (W + Tb))
    sv = [us * (1 - abs(2 * k / SLEEVE_SEG - 1)) for k in range(SLEEVE_SEG)]
    for side in (-1, 1):
        sx = side * (W * 0.5 - 0.4)
        zs = NECK_Z - 0.8 - _shoulder_drop(sx) - 0.8
        L = min(23.0, zs - hem - 1.5) if long_ else 7.0
        L = max(L, 5.0)
        fwd = -(0.22 * Tb + 0.25)
        # the armhole starts inside the body, up under the shoulder, so no cap shows
        path = [(sx - side * 2.2, fwd * 0.2, zs + 1.6, sr * 0.5, sr * 0.6),
                (sx + side * 0.25, fwd * 0.8, zs - 1.5, sr * 0.85, sr * 1.05),
                (sx + side * 0.15, fwd * 1.15, zs - L * 0.6, sr * 0.8, sr * 0.92),
                (sx - side * 0.35, fwd * 1.25, zs - L, sr * (0.75 if long_ else 0.95), sr * (0.82 if long_ else 1.05))]
        rings, ruvs = [], []
        for cx, cy, cz, rx, ry in path:
            ring, ruv = [], []
            for k in range(SLEEVE_SEG):
                a = 2 * math.pi * (k + 0.5) / SLEEVE_SEG
                x = cx + rx * math.cos(a) + rng.uniform(-0.08, 0.08)
                yy = cy + ry * math.sin(a)
                zz = cz + (rng.uniform(-0.25, 0.25) if cz < zs else 0.0)
                ring.append(b.bm.verts.new(P(x, yy, zz)))
                ruv.append((sv[k], (zz - zb) / span))
            rings.append(ring)
            ruvs.append(ruv)
        _loft(b, rings, ruvs, region)
        if region == "tan_blazer" and side == -1:      # four black buttons above the cuff
            cx, cy, cz, rx, ry = path[-1]
            for j in range(4):
                p = P(cx - rx * 0.95, cy - ry * 0.3, cz + 1.4 + j * 0.85)
                b.lump("button_black", (p.x, p.y, p.z - 0.3), (0.6, 0.6, 0.6), 500 + j, rough=0.0,
                       segs=(6, 4))


def hanger(b, y, turn, kind):
    xf = _xf(y, turn)
    c, s = math.cos(math.radians(turn)), math.sin(math.radians(turn))
    up = (-s, c, 0.0)                           # the hanger plane's normal
    metal = kind in ("wm", "c")
    body = {"t": "hanger_teal"}.get(kind, "hanger_white")
    hook_r = 0.08 if metal else 0.12
    hook = [(0.0, NECK_Z - 0.2), (-0.95, 63.2), (-0.35, 64.75), (0.85, 64.3)]
    b.sw("chrome" if metal else body, [xf(x, 0, z) for x, z in hook],
         common.circle_profile(hook_r, 4), up=up)
    if kind == "c":                             # clip bar, post and two clips
        bar_z = NECK_Z - 1.6
        b.sw("hanger_white", [xf(-7.2, 0, bar_z), xf(7.2, 0, bar_z)], common.rect_profile(0.45, 0.3), up=up)
        b.sw("hanger_white", [xf(0, 0, NECK_Z - 0.1), xf(0, 0, bar_z)], common.rect_profile(0.35, 0.35), up=up)
        rot = Matrix.Translation(xf(0, 0, 0)) @ Matrix.Rotation(math.radians(turn), 4, "Z")
        for cx in (-6.4, 6.4):
            b.bx("hanger_white", (cx - 0.5, -0.4, bar_z - 1.6), (cx + 0.5, 0.4, bar_z), matrix=rot)
        return
    pts = [xf(-HANGER_HALF, 0, NECK_Z - HANGER_DROP), xf(0, 0, NECK_Z), xf(HANGER_HALF, 0, NECK_Z - HANGER_DROP)]
    b.sw(body, pts, common.rect_profile(0.32, 0.45), up=up)


def multi_hook(b):
    """Chrome multi-hanger hook at the south end of the rod: a hook over the rod and a
    vertical bar with rungs, with the jeans folded over it (photo 20)."""
    y = MULTI_HOOK_Y
    up = (0, 1, 0)
    hook = [(ROD_X, 46.0), (ROD_X, 62.8), (ROD_X - 0.9, 63.6), (ROD_X - 0.4, 64.6), (ROD_X + 0.5, 64.7),
            (ROD_X + 1.0, 63.9)]
    b.sw("chrome", [Vector((x, y, z)) for x, z in hook], common.circle_profile(0.14, 6), up=up)
    for z in (60.0, 55.5, 51.0):
        b.sw("chrome", [Vector((ROD_X - 1.6, y, z)), Vector((ROD_X + 1.6, y, z))],
             common.circle_profile(0.1, 6), up=(0, 0, 1))


def garments(coll):
    b = B()
    for i, spec in enumerate(GARMENTS):
        garment(b, spec, 100 + i)
        hanger(b, spec[1], spec[6], spec[7])
        if i % 2 and spec[2] != "clip":     # a second hanger with a thin garment hidden behind
            hanger(b, spec[1] + 0.5, spec[6] + 6, spec[7])
    for y, turn, kind in EMPTY_HANGERS:
        hanger(b, y, turn, kind)
    multi_hook(b)
    garment(b, DENIM, 999)
    return b.finish(NAME + "_garments", coll, clamp=True)


# --- top shelf -----------------------------------------------------------------------------
S = SHELF_TOP


def cap(b, region, c, yaw, seed, tilt=0.0, brim_region=None):
    """Baseball cap: a dome crown and a flat brim pointing along yaw."""
    b.lump(region, (c[0], c[1], c[2]), (6.6, 7.2, 4.4), seed, rough=0.05, base=c[2], segs=(11, 6))
    d = Vector((math.cos(yaw), math.sin(yaw), 0))
    n = Vector((-d.y, d.x, 0))
    o = Vector(c) + d * 3.0 + Vector((0, 0, 0.3 + tilt))
    out = [o + n * 3.0, o + d * 2.6 + n * 1.8, o + d * 3.1, o + d * 2.6 - n * 1.8, o - n * 3.0]
    outline = [(p.x, p.y) for p in out]
    f = b.prism(brim_region or region, outline, o.z, o.z + 0.25)
    b.boxmap(f, brim_region or region)


def strip(b, region, pts, width, thick):
    """A hanging fabric strip (scarf, towel end, strap) swept along pts in an x-z plane:
    a soft lens section on a smoothed path that bends over the shelf edge, with a slight
    sway in y so it doesn't read as a board."""
    path = common.smooth_path(pts, samples=2 if width > 1.5 else 1)
    path = [p + Vector((0, 0.25 * width * math.sin(i * 1.3) / max(len(path), 1) * 2, 0))
            for i, p in enumerate(path)]
    n = 8 if width > 1.5 else 4
    prof = [(thick / 2 * math.cos(2 * math.pi * k / n) * (1.0 if k % 2 else 0.8),
             width / 2 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    b.sw(region, path, prof, up=(0, 1, 0))


def shelf_items(coll):
    b = B()
    # photo 19, north half, north -> south
    b.lump("black_warm", (268.0, 193.6, S), (11.5, 8.5, 10.0), 1, base=S, crumple=0.2, segs=(12, 7))
    b.lump("black", (264.0, 190.4, S), (7.5, 5.5, 5.5), 2, base=S, crumple=0.2, segs=(12, 7))
    b.lump("red_fabric", (262.6, 196.0, S), (4.0, 3.2, 2.4), 3, base=S, crumple=0.2, segs=(12, 7))
    strip(b, "orange", [(265.5, 193.5, S + 0.4), (261.0, 193.5, S + 0.5), (260.2, 193.4, 64.5),
                        (260.0, 193.2, 60.0)], 4.5, 0.9)
    b.lump("towel_beige", (264.6, 188.2, S), (8.5, 7.0, 4.0), 4, base=S, rough=0.09, crumple=0.2, segs=(12, 7))
    strip(b, "towel_beige", [(264.5, 185.2, S + 2.0), (260.9, 185.2, S + 0.6), (260.3, 185.0, 64.8),
                             (260.5, 184.7, 62.5)], 3.5, 0.8)
    b.lump("black", (268.6, 183.4, S), (9.0, 8.0, 7.5), 5, base=S)       # black bag
    arc = [(264.2 - 3.1 * math.sin(math.radians(a)), 183.4 + 3.6 * math.cos(math.radians(a)), S + 0.6)
           for a in range(0, 181, 30)]
    b.sw("leather_brown", [Vector(p) for p in arc], common.circle_profile(0.4, 6))   # its handle
    cap(b, "cap_black", (269.5, 183.0, S + 7.0), math.radians(200), 6, brim_region="black")
    cap(b, "cap_black", (268.0, 179.8, S + 5.0), math.radians(160), 7, brim_region="black")
    b.lump("stripe", (271.0, 178.4, S), (7.0, 5.5, 8.0), 8, base=S, crumple=0.2, segs=(12, 7))
    cap(b, "denim_light", (265.4, 179.4, S + 0.6), math.radians(120), 9, tilt=1.2)
    b.lump("grey_fabric", (262.8, 176.6, S), (5.0, 5.0, 2.2), 10, base=S, crumple=0.2, segs=(12, 7))
    b.lump("fleece_blue", (264.0, 175.4, S), (6.0, 5.0, 4.0), 11, base=S, rough=0.09, crumple=0.2, segs=(12, 7))
    strip(b, "fleece_blue", [(264.5, 174.6, S + 3.0), (260.9, 174.3, S + 1.0), (259.9, 173.8, 64.0),
                             (259.4, 173.0, 58.0), (259.7, 172.0, 54.5)], 4.2, 1.4)
    b.lump("knit_multi", (266.6, 171.6, S), (7.5, 6.0, 5.0), 12, base=S, rough=0.09, crumple=0.2, segs=(12, 7))
    b.lump("black", (268.5, 168.6, S), (7.5, 6.0, 5.0), 13, base=S, crumple=0.2, segs=(12, 7))
    # photo 20, south half
    b.lump("knit_multi", (267.4, 165.0, S), (8.5, 5.0, 6.0), 14, base=S, rough=0.09, crumple=0.2, segs=(12, 7))
    b.lump("black", (268.2, 160.2, S), (12.0, 9.0, 5.5), 15, base=S, crumple=0.2, segs=(12, 7))
    b.lump("black_warm", (266.6, 154.2, S), (12.0, 8.0, 4.5), 16, base=S, crumple=0.2, segs=(12, 7))
    for dy in (0.0, 0.9):
        strip(b, "black", [(264.0, 159.6 + dy, S + 1.5), (260.8, 159.6 + dy, S + 0.4),
                           (260.2, 159.5 + dy, 64.0), (260.5, 159.4 + dy, 61.5)], 0.9, 0.3)
    b.lump("white_fabric", (264.2, 151.0, S), (9.0, 7.0, 3.0), 17, base=S, rough=0.09, crumple=0.2, segs=(12, 7))
    b.lump("black", (268.4, 145.6, S), (8.0, 7.0, 8.0), 18, base=S, crumple=0.2, segs=(12, 7))
    b.lump("brown_print", (268.0, 145.2, S + 6.5), (6.5, 5.0, 3.0), 19, base=S + 6.5, crumple=0.2, segs=(12, 7))
    strip(b, "black", [(264.5, 141.6, S + 0.5), (261.0, 141.4, S + 0.5), (260.3, 141.0, 63.5)], 3.0, 0.5)
    # closed paper parasol standing in the south-east corner, leaning on the walls
    tilt = Matrix.Rotation(math.radians(4), 3, "X") @ Matrix.Rotation(math.radians(-3), 3, "Y")
    c = (271.6, 137.4)
    b.lathe("bamboo", c, [(0.35, S), (0.42, S + 1.2), (0.35, S + 6.5), (0.3, S + 7.5)], seg=6,
            tilt=tilt)
    b.lathe("umbrella", c, [(0.6, S + 7.0), (1.5, S + 12.0), (1.75, S + 22.0), (1.2, S + 29.0),
                            (0.25, S + 31.0)], seg=8, tilt=tilt)
    return b.finish(NAME + "_shelf_items", coll, clamp=True)


# --- floor ---------------------------------------------------------------------------------

def shoe(b, upper, sole, heel, toe, W, H, seed, boot=0.0):
    """Low-poly shoe: five rings heel -> toe of a rounded box, the sole region underneath."""
    rng = random.Random(seed)
    h0, t0 = Vector((heel[0], heel[1], 0)), Vector((toe[0], toe[1], 0))
    d = t0 - h0
    L = d.length
    d.normalize()
    n = Vector((-d.y, d.x, 0))
    stations = [(0.0, 0.72, 1.0), (0.22, 0.9, 0.95 + boot), (0.5, 1.0, 0.72), (0.78, 0.92, 0.5), (1.0, 0.5, 0.32)]
    rings = []
    for s, wf, hf in stations:
        w, h = W / 2 * wf, H * hf
        if boot and s <= 0.25:
            h = H * (1 + boot)
        c = h0 + d * (L * s)
        pts = [(w, 0.0), (w * 1.02, 0.5 * h), (0.5 * w, h), (-0.5 * w, h), (-w * 1.02, 0.5 * h), (-w, 0.0)]
        rings.append([b.bm.verts.new(c + n * u + Vector((0, 0, z + rng.uniform(0, 0.08)))) for u, z in pts])
    faces, soles = [], []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(6):
            k1 = (k + 1) % 6
            f = b.bm.faces.new((r0[k], r0[k1], r1[k1], r1[k]))
            (soles if k == 5 else faces).append(f)
    faces.append(b.bm.faces.new(list(reversed(rings[0]))))
    faces.append(b.bm.faces.new(rings[-1]))
    b.boxmap(faces, upper)
    b.boxmap(soles, sole)


def hamper(b):
    """Grey collapsible laundry hamper (photo 20): an open-top box with a light rim, a
    strap down each long side and a loop handle on each end; dark denim inside."""
    c, yaw = Vector((261.0, 148.0, 0)), math.radians(12)
    M = Matrix.Translation(c) @ Matrix.Rotation(yaw, 4, "Z")
    hx, hy, H, t = 6.25, 9.0, 21.0, 0.3
    b.bx("hamper", (-hx, -hy, 0), (hx, hy, 0.4), matrix=M)
    for lo, hi in (((-hx, -hy, 0), (-hx + t, hy, H)), ((hx - t, -hy, 0), (hx, hy, H)),
                   ((-hx, -hy, 0), (hx, -hy + t, H)), ((-hx, hy - t, 0), (hx, hy, H))):
        b.bx("hamper", lo, hi, matrix=M)
    for lo, hi in (((-hx - 0.1, -hy - 0.1, H - 0.8), (-hx + t + 0.1, hy + 0.1, H + 0.2)),
                   ((hx - t - 0.1, -hy - 0.1, H - 0.8), (hx + 0.1, hy + 0.1, H + 0.2)),
                   ((-hx - 0.1, -hy - 0.1, H - 0.8), (hx + 0.1, -hy + t + 0.1, H + 0.2)),
                   ((-hx - 0.1, hy - t - 0.1, H - 0.8), (hx + 0.1, hy + 0.1, H + 0.2))):
        b.bx("hamper_trim", lo, hi, matrix=M)
    for sx in (-1, 1):                           # straps down the long sides, with a buckle
        x = sx * (hx + 0.12)
        b.bx("hamper_trim", (x - 0.12, -1.0, 0.2), (x + 0.12, 1.0, H - 0.5), matrix=M)
        b.bx("chrome", (x - 0.2, -0.9, 9.0), (x + 0.2, 0.9, 10.0), matrix=M)
    for sy in (-1, 1):                           # loop handles on the ends
        y = sy * (hy + 0.2)
        pts = [M @ Vector((-2.5, y, H - 3.0)), M @ Vector((-2.2, y + sy * 0.6, H + 1.5)),
               M @ Vector((0.0, y + sy * 0.8, H + 2.6)), M @ Vector((2.2, y + sy * 0.6, H + 1.5)),
               M @ Vector((2.5, y, H - 3.0))]
        b.sw("hamper_trim", pts, common.rect_profile(1.0, 0.12), up=(0, 0, 1))
    b.bx("hamper_inside", (-hx + t + 0.05, -hy + t + 0.05, 0.4), (hx - t - 0.05, hy - t - 0.05, 0.45),
         matrix=M)
    # laundry: dark denim and a grey tee heaped near the top
    for (x, y, z), size, reg, s in (((-1.0, -2.0, 12.0), (10.0, 9.0, 8.0), "jeans_dark", 41),
                                    ((1.5, 4.0, 14.0), (8.5, 7.5, 6.0), "jeans_dark", 42),
                                    ((0.5, -5.5, 13.0), (8.0, 5.0, 4.0), "grey_tee", 43)):
        p = M @ Vector((x, y, 0))
        b.lump(reg, (p.x, p.y, z), size, s, rough=0.09, yaw=yaw, crumple=0.2, segs=(12, 7))


def floor_items(coll):
    b = B()
    # photo 19, north half: toes west toward the doors
    for y in (186.6, 184.8):
        shoe(b, "shoe_black", "shoe_black", (266.0, y), (256.8, y - 0.3), 3.4, 2.4, int(y * 10))
    shoe(b, "shoe_black", "shoe_black", (268.0, 182.5), (259.0, 182.2), 3.4, 3.4, 51, boot=1.2)
    for y in (180.4, 178.4):
        shoe(b, "shoe_brown", "shoe_black", (264.2, y), (254.6, y + 0.2), 3.6, 3.3, int(y * 10))
    for y in (176.2, 174.2):
        shoe(b, "sneaker_dark", "sole_light", (266.4, y), (256.0, y - 0.4), 4.0, 4.0, int(y * 10))
    for y in (172.0, 170.0):
        shoe(b, "sneaker_grey", "sole_light", (263.2, y), (252.9, y + 0.3), 4.0, 4.0, int(y * 10))
    # photo 20, south half
    for y in (165.0, 163.2):
        shoe(b, "sneaker_pink", "sole_light", (266.0, y), (256.0, y - 0.5), 3.8, 3.8, int(y * 10))
    for y in (160.6, 158.6):
        shoe(b, "sneaker_grey", "sole_light", (268.0, y), (257.4, y + 0.6), 4.0, 4.0, int(y * 10))
    shoe(b, "navy_dark", "sole_light", (265.4, 156.9), (256.0, 156.4), 3.8, 3.6, 61)
    hamper(b)
    b.lump("plastic_bag", (268.4, 137.8, 0), (7.0, 5.0, 9.0), 71, base=0.0, rough=0.1)
    b.lump("shoe_black", (256.6, 139.0, 0), (7.5, 5.0, 6.0), 72, base=0.0)
    return b.finish(NAME + "_floor_items", coll, clamp=True)


def build(coll):
    return [joinery(coll), garments(coll), shelf_items(coll), floor_items(coll)]


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.collapse_materials(ob, {r: mat for r in REGIONS})
