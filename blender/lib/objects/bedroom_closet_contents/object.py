"""Bedroom closet contents: the inside of the bypass-door closet east of the bedroom.

  joinery   a white melamine shelf on 1x4 cleats (back and both end walls) with a
            light pine hanging rod under it, socketed in the end cleats
  garments  a full rod: white plastic hangers (silver wire hooks on the north run, all-
            plastic further south, about one in four teal), clip hangers for the skirts and
            trousers at the north end, and the clothes as cheap lumpy hanging panels:
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

    def lump(self, region, c, size, seed, rough=0.05, yaw=0.0, base=None, segs=(11, 6)):
        """A squashed, noisy sphere: fabric piles, bags, hat crowns. base = z below which
        the verts flatten onto the resting surface."""
        rng = random.Random(seed)
        r = bmesh.ops.create_uvsphere(self.bm, u_segments=segs[0], v_segments=segs[1], radius=1.0)
        verts = r["verts"]
        cy, sy = math.cos(yaw), math.sin(yaw)
        for v in verts:
            x, y, z = v.co
            k = 1.0 + rng.uniform(-rough, rough)
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
    ("puffer", 161.6, "puffer", 28.0, 9.0, 22, 22, "w"),
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


SECTION = [(1.0, -0.8), (0.45, -0.55), (-0.45, -0.55), (-1.0, -0.8), (-1.0, 0.8), (-0.45, 0.55),
           (0.45, 0.55), (1.0, 0.8)]


def garment(b, spec, seed):
    region, y, kind, hem, T, W, turn, _ = spec
    rng = random.Random(seed)
    # hanging bulk: sleeves at the sides and the fabric's drape make a garment fuller and
    # wider than its flat body; a little extra random turn breaks the rows up
    if kind == "top":
        T, W = T * 1.6 + 1.0, W + 1.5
    elif kind == "dress":
        T = T * 1.3 + 0.9
    turn += rng.uniform(-3, 3) if abs(turn) > 30 else rng.uniform(-8, 8)
    xf = _xf(y, turn)
    rings = []                                  # (z, half width, half thickness, shoulder drop)
    if kind == "clip":
        top = NECK_Z - 2.0 if spec is not DENIM else 53.0
        rings.append((top, W * 0.47, T * 0.25, 0.0))
        rings.append((top - 1.5, W * 0.5, T * 0.45, 0.0))
        body_top = top - 1.5
    else:
        top = NECK_Z + 0.2
        rings.append((top, W * 0.11, T * 0.3, 0.0))
        rings.append((NECK_Z - 1.2, W * 0.5, T * 0.42, HANGER_DROP + 0.3))
        body_top = NECK_Z - 5.0
        rings.append((body_top, W * 0.5, T * 0.5, 0.0))
    flare = {"dress": 1.35, "clip": 1.2 if W > 14 else 1.0, "top": 0.97, "puffer": 1.0}[kind]
    length = body_top - hem
    if kind == "puffer":
        n = max(3, int(length / 4.0))
        for i in range(1, n + 1):
            t = i / n
            pinch = 0.7 if i % 2 else 1.0
            rings.append((body_top - length * t, W * 0.5 * (1.0 - 0.04 * pinch), T * 0.5 * pinch, 0.0))
    else:
        n = 2 if length < 20 else 3
        for i in range(1, n + 1):
            t = i / n
            w = W * 0.5 * (1 + (flare - 1) * t ** 1.3) * (0.96 if (kind == "top" and t < 0.7) else 1.0)
            rings.append((body_top - length * t, w, T * 0.5 * (1.0 + 0.45 * t), 0.0))   # splays at the hem
    seg = 8
    verts, uvs = [], []
    wmax = max(r[1] for r in rings) * 2
    zt, zb = rings[0][0], rings[-1][0]
    phase = rng.uniform(0, 6.3)
    # u runs round the section from the middle of one face (0) to the middle of the other
    # (1) and back, so the print keeps its scale on the ends a visitor sees, with no seam
    pts = [Vector((px * W / 2, py * T / 2, 0)) for px, py in SECTION]
    d = [0.0]
    for k in range(seg):
        d.append(d[-1] + (pts[(k + 1) % seg] - pts[k]).length)
    P, d0 = d[-1], (d[1] + d[2]) / 2
    usec = [1 - abs(2 * (((d[k] - d0) / P) % 1.0) - 1) for k in range(seg)]
    for ri, (z, w, t, drop) in enumerate(rings):
        ring, ruv = [], []
        last = ri == len(rings) - 1
        for k in range(seg):
            # dumbbell section: the sleeves hanging at both ends make the ends (the side a
            # visitor sees from the doors) fuller than the middle
            px, py = SECTION[k]
            x, yy = w * px, t * py
            sa = py
            if ri > 0:
                x += rng.uniform(-0.35, 0.35)
                # folds: the faces ripple along the width
                yy += (0.35 + 0.15 * T) * math.sin(x * 0.45 + phase + ri * 1.7) * (1 if sa > 0 else -1)
                yy += rng.uniform(-0.12, 0.12) * T
            zz = z - drop * (abs(x) / max(w, 1e-3)) ** 1.2
            if last:
                zz += rng.uniform(-0.6, 0.6)
            elif ri > 1:
                zz += rng.uniform(-0.25, 0.25)
            ring.append(b.bm.verts.new(xf(x, yy, zz)))
            ruv.append((usec[k], (zz - zb) / max(zt - zb, 1e-3)))
        verts.append(ring)
        uvs.append(ruv)
    for i in range(len(verts) - 1):
        for k in range(seg):
            k1 = (k + 1) % seg
            f = b.bm.faces.new((verts[i][k], verts[i][k1], verts[i + 1][k1], verts[i + 1][k]))
            b.setuv(f, (uvs[i][k], uvs[i][k1], uvs[i + 1][k1], uvs[i + 1][k]), region)
    for i, rev in ((0, True), (len(verts) - 1, False)):
        idx = list(range(seg))[::-1] if rev else list(range(seg))
        f = b.bm.faces.new([verts[i][k] for k in idx])
        b.setuv(f, [uvs[i][k] for k in idx], region)
    if region == "tan_blazer":              # four black sleeve buttons (photo 19), on the face
        for j in range(4):
            p = xf(-W * 0.5 + 2.2, T * 0.5 + 0.1, hem + 2.5 + j * 0.9)
            f = b.cylinder("button_black", p, 0.35, 0.2, axis="Y", segments=6)
            b.boxmap(f, "button_black")


def hanger(b, y, turn, kind):
    xf = _xf(y, turn)
    c, s = math.cos(math.radians(turn)), math.sin(math.radians(turn))
    up = (-s, c, 0.0)                           # the hanger plane's normal
    metal = kind in ("wm", "c")
    body = {"t": "hanger_teal"}.get(kind, "hanger_white")
    hook_r = 0.08 if metal else 0.12
    hook = [(0.0, NECK_Z - 0.2), (-0.92, 62.9), (-0.72, 64.55), (0.3, 64.85), (0.98, 64.0)]
    b.sw("chrome" if metal else body, [xf(x, 0, z) for x, z in hook],
         common.circle_profile(hook_r, 6 if metal else 5), up=up)
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
    """A hanging fabric strip (scarf, towel end, strap) swept along pts in an x-z plane."""
    b.sw(region, [Vector(p) for p in pts], common.rect_profile(thick, width), up=(0, 1, 0))


def shelf_items(coll):
    b = B()
    # photo 19, north half, north -> south
    b.lump("black_warm", (268.0, 193.6, S), (11.5, 8.5, 10.0), 1, base=S)
    b.lump("black", (264.0, 190.4, S), (7.5, 5.5, 5.5), 2, base=S)
    b.lump("red_fabric", (262.6, 196.0, S), (4.0, 3.2, 2.4), 3, base=S)
    strip(b, "orange", [(265.5, 193.5, S + 0.4), (261.0, 193.5, S + 0.5), (260.2, 193.4, 64.5),
                        (260.0, 193.2, 60.0)], 4.5, 0.9)
    b.lump("towel_beige", (264.6, 188.2, S), (8.5, 7.0, 4.0), 4, base=S, rough=0.09)
    strip(b, "towel_beige", [(264.5, 185.2, S + 2.0), (260.9, 185.2, S + 0.6), (260.3, 185.0, 64.8),
                             (260.5, 184.7, 62.5)], 3.5, 0.8)
    b.lump("black", (268.6, 183.4, S), (9.0, 8.0, 7.5), 5, base=S)       # black bag
    arc = [(264.2 - 3.1 * math.sin(math.radians(a)), 183.4 + 3.6 * math.cos(math.radians(a)), S + 0.6)
           for a in range(0, 181, 30)]
    b.sw("leather_brown", [Vector(p) for p in arc], common.circle_profile(0.4, 6))   # its handle
    cap(b, "cap_black", (269.5, 183.0, S + 7.0), math.radians(200), 6, brim_region="black")
    cap(b, "cap_black", (268.0, 179.8, S + 5.0), math.radians(160), 7, brim_region="black")
    b.lump("stripe", (271.0, 178.4, S), (7.0, 5.5, 8.0), 8, base=S)
    cap(b, "denim_light", (265.4, 179.4, S + 0.6), math.radians(120), 9, tilt=1.2)
    b.lump("grey_fabric", (262.8, 176.6, S), (5.0, 5.0, 2.2), 10, base=S)
    b.lump("fleece_blue", (264.0, 175.4, S), (6.0, 5.0, 4.0), 11, base=S, rough=0.09)
    strip(b, "fleece_blue", [(264.5, 174.6, S + 3.0), (260.9, 174.3, S + 1.0), (259.9, 173.8, 64.0),
                             (259.4, 173.0, 58.0), (259.7, 172.0, 54.5)], 4.2, 1.4)
    b.lump("knit_multi", (266.6, 171.6, S), (7.5, 6.0, 5.0), 12, base=S, rough=0.09)
    b.lump("black", (268.5, 168.6, S), (7.5, 6.0, 5.0), 13, base=S)
    # photo 20, south half
    b.lump("knit_multi", (267.4, 165.0, S), (8.5, 5.0, 6.0), 14, base=S, rough=0.09)
    b.lump("black", (268.2, 160.2, S), (12.0, 9.0, 5.5), 15, base=S)
    b.lump("black_warm", (266.6, 154.2, S), (12.0, 8.0, 4.5), 16, base=S)
    for dy in (0.0, 0.9):
        strip(b, "black", [(264.0, 159.6 + dy, S + 1.5), (260.8, 159.6 + dy, S + 0.4),
                           (260.2, 159.5 + dy, 64.0), (260.5, 159.4 + dy, 61.5)], 0.9, 0.3)
    b.lump("white_fabric", (264.2, 151.0, S), (9.0, 7.0, 3.0), 17, base=S, rough=0.09)
    b.lump("black", (268.4, 145.6, S), (8.0, 7.0, 8.0), 18, base=S)
    b.lump("brown_print", (268.0, 145.2, S + 6.5), (6.5, 5.0, 3.0), 19, base=S + 6.5)
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
        b.lump(reg, (p.x, p.y, z), size, s, rough=0.09, yaw=yaw)


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
