"""Dining clutter: everything on the dining table top, plus the two jackets hung over the
south chair, as seen in the living/dining LiDAR capture (Reference/lidarseries-splat/
LidarSeries_20260925_003335_763, frames wide_20260925_003708..003922 and 004332..004401).
Only items visible in those frames are modelled; nothing is invented.

On the table (south half, west to east, then the north end):
  - sticker-covered black water bottle with a sage flip lid and lilac ring (stickers
    redrawn as plain abstract die-cut shapes, no characters, no text)
  - white shaker-style cylinder with a pink and blue blossom print
  - blue-and-white patterned plate holding a white bowl with a navy band, full of frosted
    animal crackers, with wrapped candies round the bowl; one loose wrapper on the table
  - two tall white speckled lime seltzer cans ("Limeyish" parody label)
  - an oval fish tin, yellow/red band, pull-tab lid ("Sardeen Machine" parody)
  - spice group: an all-purpose seasoning shaker, yellow label and red cap ("Pinchy"
    parody), a black-label seasoning jar with a white cap (blank label), a small white
    capped container, two small glass spice jars with black caps (flakes, pepper)
  - black wire napkin holder with white napkins
  - red seltzer can ("Glacier Burp" parody), tall grey plastic tumbler
  - two closed laptops stacked at the south-east corner: a sky-blue one ("Kumquat" parody
    mark, lid only, screen never visible) turned 25 degrees on a black one (blank white
    sticker, blank corner badge), which lies on a plain tan folder with a blank white
    sheet peeking out on the west side
  - north-east: a white cereal bowl with crumbs and a fork, a crumpled paper towel
On the south chair (dining_chair__s): a quilted navy puffer jacket and a rust-brown canvas
jacket over it (its cartoon back print left off for now: plain canvas), both hung over
the top rail, one sleeve of each hanging down the back.

Source of truth: scripted. Frame: PLAN coordinates (+X east, +Y north, Z up, metres, origin
plan (0, 0, 0)); the package goes on a marker at (0, 0, 0) with no rotation.

Positions were measured in the capture's plan frame (Reference/living_survey/transform.json)
on orthophotos of the table plane from the posed frames 003750/003751/003752/003753/003754
and triangulated across the three near-overhead views (tops -> base and height; see
Reference/dining_clutter_work/tri.py). The capture puts the table top at x 65.7..102.3,
y 174.6..236.6, the modelled table (dining_table at (85, 205), 38 x 61, top z 29.5) spans
x 66..104, y 174.5..235.5, so centres are mapped edge-to-edge onto the modelled top by
tbl(); sizes stay as measured. The jackets are anchored to the modelled chair's back posts.

Dimensions (inches). SCAN = triangulated/orthophoto from the capture, SPEC = standard size of
that kind of product, EST = judged from the photos against the cans.
  can 12 oz: 2.6 dia x 4.83                                         SPEC
  lime cans 2.6 dia x 6.1 (taller than the red can, as tall as the shaker)  SCAN 5.8-6.2
  seasoning shaker 2.6 dia x 5.8; black-label jar 2.9 x 4.9;
  white capped container 2.4 x 4.6; glass spice jars 1.8 sq x 3.9          SCAN heights, EST dias
  fish tin 5.9 x 3.4 x 1.9 (oval), turned 24 deg                            SCAN plan, EST height
  water bottle 3.3 dia x 10.5                                              EST (1.9 x the print cylinder)
  print cylinder 2.2 dia x 5.5                                             SCAN
  plate 10.5 dia; bowl 6.4 dia x 2.6                                       SCAN
  napkin holder 3.4 x 6.4, 6.3 tall, grid faces east/west                   SCAN/EST
  tumbler rim 4.4, base 3.4, 6.75 tall                                     SCAN rim, EST height
  sky-blue laptop 12.0 x 8.5 x 0.45 at 25.5 deg                             SCAN (12.1 x 8.8)
  black laptop 15.0 x 10.0 x 0.8, long side north-south                    SCAN (15.1 x 9.9)
  tan folder 10.6 x 15.4 x 0.12                                            SCAN (strip visible S + E)
  north bowl 6.0 dia x 2.6                                                 SCAN
  jackets: navy x 75.75..93.25 (hem 21 wide), hems z 27 front / 7 back;
           brown x 77.25..87.75 (hem 13 wide), hems z 22 front / 4 back         PHOTO/EST (block-in)
"""

import math
import random
import bpy
import os

import bmesh
from mathutils import Matrix, Vector

import atlas_layout
import common

NAME = "dining_clutter"
IN = 0.0254


def m(inches):
    return inches * IN


TOP = 29.5                                   # dining_table top surface
CAP_X, CAP_Y = (65.7, 102.3), (174.6, 236.6)  # SCAN table top in the capture frame
MOD_X, MOD_Y = (66.0, 104.0), (174.5, 235.5)  # modelled table top


def tbl(x, y):
    """Capture-frame plan (in) -> modelled table plan (in)."""
    fx = (x - CAP_X[0]) / (CAP_X[1] - CAP_X[0])
    fy = (y - CAP_Y[0]) / (CAP_Y[1] - CAP_Y[0])
    return (MOD_X[0] + fx * (MOD_X[1] - MOD_X[0]), MOD_Y[0] + fy * (MOD_Y[1] - MOD_Y[0]))


# --- item positions (capture frame, inches) ----------------------------------------------
BOTTLE = (68.2, 185.0)
PRINT_CYL = (70.56, 189.69)
PLATE = (75.86, 183.0)
LIME_A = (70.49, 201.19)
LIME_B = (78.73, 198.46)
TIN = (81.05, 194.66, 24.0)
SHAKER = (85.17, 192.79)
BLACK_JAR = (83.15, 191.89)
WHITE_JAR = (84.82, 190.2)
SPICE_FLAKES = (81.16, 189.64)
SPICE_PEPPER = (82.57, 189.42)
NAPKINS = (84.6, 185.6)
RED_CAN = (83.32, 179.01)
TUMBLER = (87.95, 179.19)
LAPTOP_BLUE = (98.25, 182.8, 25.5)
LAPTOP_BLACK = (98.05, 183.95)
FOLDER = (98.4, 183.6)
LOOSE_WRAPPER = (76.75, 188.75)
BOWL_N = (97.4, 227.6)
TOWEL_N = (95.6, 231.4)

# south chair (shell_layout dining_chair__s (85, 176) rot 180; dining_chair package)
CHAIR_X, CHAIR_Y = 85.0, 176.0
POST_TOP_Y = CHAIR_Y - 9.75          # back post centre at the top, plan y 166.25
RAIL_TOP = 37.5

ATLAS = {
    "name": "dining_clutter",
    "size": 1024,
    "regions": {
        "laptop_lid": (0, 0, 256, 192),
        "black_lid": (256, 0, 128, 192),
        "tan": (384, 0, 64, 64),
        "paper": (448, 0, 64, 64),
        "blue_metal": (512, 0, 64, 64),
        "black_plastic": (576, 0, 64, 64),
        "steel": (640, 0, 64, 64),
        "ceramic": (704, 0, 64, 64),
        "gray_plastic": (768, 0, 64, 64),
        "wire": (832, 0, 64, 64),
        "napkin": (896, 0, 64, 64),
        "paper_towel": (960, 0, 64, 64),
        "red_cap": (384, 64, 64, 64),
        "white_cap": (448, 64, 64, 64),
        "lid_green": (512, 64, 64, 64),
        "lid_lilac": (576, 64, 64, 64),
        "glass_flakes": (640, 64, 64, 64),
        "glass_pepper": (704, 64, 64, 64),
        "black_cap": (768, 64, 64, 64),
        "coral": (832, 64, 64, 64),
        "cup_inside": (896, 64, 64, 64),
        "candy_0": (384, 128, 32, 32), "candy_1": (416, 128, 32, 32),
        "candy_2": (448, 128, 32, 32), "candy_3": (480, 128, 32, 32),
        "candy_4": (384, 160, 32, 32), "candy_5": (416, 160, 32, 32),
        "candy_6": (448, 160, 32, 32), "candy_7": (480, 160, 32, 32),
        "lime_label": (0, 192, 256, 128),
        "red_label": (256, 192, 256, 128),
        "shaker_label": (512, 192, 256, 128),
        "jar_label": (768, 192, 256, 128),
        "blossom": (0, 320, 256, 128),
        "bottle": (256, 320, 384, 192),
        "tin_side": (640, 320, 256, 64),
        "tin_top": (640, 384, 256, 128),
        "can_top": (896, 320, 128, 128),
        "plate": (0, 512, 256, 256),
        "cookies": (256, 512, 192, 192),
        "bowl_band": (448, 512, 128, 64),
        "crumbs": (448, 576, 128, 128),
        "grid_face": (576, 512, 128, 128),
        "navy": (0, 768, 256, 256),
        "brown": (256, 768, 384, 256),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "none"
STATIC = True
VIEWS = [("table_top", 0, 80, 0.45), ("from_sw", 225, 30, 0.5), ("from_se", 135, 25, 0.5)]


# --- a small mesh builder with explicit UVs ----------------------------------------------

class MB:
    """Geometry in plan inches with per-loop UVs written straight into atlas rects."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.rects = {r: atlas_layout.uv_rect(ATLAS, r) for r in REGIONS}

    def _uv(self, region, u, v):
        u0, v0, u1, v1 = self.rects[region]
        return (u0 + min(max(u, 0.0), 1.0) * (u1 - u0), v0 + min(max(v, 0.0), 1.0) * (v1 - v0))

    def face(self, verts, uvs, region):
        try:
            f = self.bm.faces.new(verts)
        except ValueError:
            return None
        f.material_index = REGIONS.index(region)
        for loop, (u, v) in zip(f.loops, uvs):
            loop[self.uv].uv = self._uv(region, u, v)
        return f

    def grid(self, pts, region, uvf, wrap=False):
        """pts[i][j] Vectors; faces (i,j)-(i+1,j)-(i+1,j+1)-(i,j+1); uvf(i, j) -> (u, v)
        (for wrap, uvf is called with i == n for the seam column)."""
        n, mm = len(pts), len(pts[0])
        vs = [[self.bm.verts.new(p) for p in row] for row in pts]
        for i in range(n if wrap else n - 1):
            i2 = (i + 1) % n
            for j in range(mm - 1):
                reg = region(j) if callable(region) else region
                self.face([vs[i][j], vs[i2][j], vs[i2][j + 1], vs[i][j + 1]],
                          [uvf(i, j, reg), uvf(i + 1, j, reg), uvf(i + 1, j + 1, reg), uvf(i, j + 1, reg)], reg)
        return vs

    def lathe(self, prof, regions, M, seg=20, modes=None, radius_uv=None, phase=0.0):
        """Surface of revolution about local Z. prof [(r, z)] from the bottom centre out,
        up and back in (outward normals). regions[k] for span k; modes {region: 'wrap' |
        'planar'}; 'wrap' spans u = angle, v over that region's z range; 'planar' maps
        x, y over +-radius_uv."""
        modes = modes or {}
        R = radius_uv or max(r for r, z in prof)
        zr = {}
        for k, reg in enumerate(regions):
            z0, z1 = prof[k][1], prof[k + 1][1]
            lo, hi = zr.get(reg, (1e9, -1e9))
            zr[reg] = (min(lo, z0, z1), max(hi, z0, z1))
        rings = []
        for r, z in prof:
            if r < 1e-6:
                rings.append([self.bm.verts.new(M @ Vector((0, 0, z)))])
            else:
                rings.append([self.bm.verts.new(M @ Vector((r * math.cos(phase + 2 * math.pi * i / seg),
                                                            r * math.sin(phase + 2 * math.pi * i / seg), z)))
                              for i in range(seg)])

        def uvf(reg, i, k):
            r, z = prof[k]
            if modes.get(reg, "wrap") == "planar":
                a = 2 * math.pi * i / seg
                return (0.5 + 0.5 * r * math.cos(a) / R, 0.5 + 0.5 * r * math.sin(a) / R)
            z0, z1 = zr[reg]
            return (i / seg, (z - z0) / max(z1 - z0, 1e-6))

        for k, reg in enumerate(regions):
            a, b = rings[k], rings[k + 1]
            for i in range(seg):
                i2 = (i + 1) % seg
                if len(a) == 1 and len(b) == 1:
                    continue
                if len(a) == 1:
                    self.face([a[0], b[i2], b[i]],
                              [uvf(reg, i + 0.5, k), uvf(reg, i + 1, k + 1), uvf(reg, i, k + 1)], reg)
                elif len(b) == 1:
                    self.face([a[i], a[i2], b[0]], [uvf(reg, i, k), uvf(reg, i + 1, k), uvf(reg, i + 0.5, k + 1)], reg)
                else:
                    self.face([a[i], a[i2], b[i2], b[i]],
                              [uvf(reg, i, k), uvf(reg, i + 1, k), uvf(reg, i + 1, k + 1), uvf(reg, i, k + 1)], reg)

    def box(self, lo, hi, region, M=Matrix.Identity(4), top=None, faces_uv=None):
        (x0, y0, z0), (x1, y1, z1) = lo, hi
        c = [M @ Vector(p) for p in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
        v = [self.bm.verts.new(p) for p in c]
        sq = [(0, 0), (1, 0), (1, 1), (0, 1)]
        self.face([v[4], v[5], v[6], v[7]], sq, top or region)          # top (+z)
        self.face([v[3], v[2], v[1], v[0]], sq, region)                 # bottom
        self.face([v[0], v[1], v[5], v[4]], sq, region)                 # -y
        self.face([v[1], v[2], v[6], v[5]], sq, region)                 # +x
        self.face([v[2], v[3], v[7], v[6]], sq, region)                 # +y
        self.face([v[3], v[0], v[4], v[7]], sq, region)                 # -x
        return v

    def prism(self, outline, z0, z1, side, top, bottom, M):
        """Closed prism from a CCW outline; top/bottom mapped planar over the outline's box."""
        xs = [p[0] for p in outline]
        ys = [p[1] for p in outline]
        bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
        n = len(outline)
        per = [0.0]
        for i in range(n):
            a, b = outline[i], outline[(i + 1) % n]
            per.append(per[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        bot = [self.bm.verts.new(M @ Vector((x, y, z0))) for x, y in outline]
        tp = [self.bm.verts.new(M @ Vector((x, y, z1))) for x, y in outline]
        for i in range(n):
            i2 = (i + 1) % n
            u0, u1 = per[i] / per[-1], per[i + 1] / per[-1]
            self.face([bot[i], bot[i2], tp[i2], tp[i]], [(u0, 0), (u1, 0), (u1, 1), (u0, 1)], side)
        pu = lambda x, y: ((x - bx0) / (bx1 - bx0), (y - by0) / (by1 - by0))
        self.face(tp, [pu(x, y) for x, y in outline], top)
        self.face(bot[::-1], [pu(x, y) for x, y in outline[::-1]], bottom)

    def blob(self, M, sx, sy, sz, region, seed, rough=0.25, subdiv=2):
        """Crumpled lump (paper towel, wrappers): a noisy flattened icosphere, planar UVs."""
        rnd = random.Random(seed)
        r = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=1.0)
        verts = r["verts"]
        for v in verts:
            k = 1.0 + rnd.uniform(-rough, rough)
            v.co = Vector((v.co.x * sx * k, v.co.y * sy * k, max(v.co.z, -0.6) * sz * k))
        faces = list({f for v in verts for f in v.link_faces})
        for f in faces:
            f.material_index = REGIONS.index(region)
            for loop in f.loops:
                co = loop.vert.co
                loop[self.uv].uv = self._uv(region, 0.5 + 0.5 * co.x / (sx * 1.3), 0.5 + 0.5 * co.y / (sy * 1.3))
        zmin = min(v.co.z for v in verts)
        for v in verts:
            v.co = M @ (v.co - Vector((0, 0, zmin)))

    def slab(self, pts, thick, region, uvf, normals):
        """Cloth panel: outer grid pts[i][j] plus an inner copy offset by -normal*thick,
        closed round the edges."""
        n, mm = len(pts), len(pts[0])
        outer = pts
        inner = [[pts[i][j] - normals[i][j] * thick for j in range(mm)] for i in range(n)]
        vo = [[self.bm.verts.new(p) for p in row] for row in outer]
        vi = [[self.bm.verts.new(p) for p in row] for row in inner]
        for i in range(n - 1):
            for j in range(mm - 1):
                uvs = [uvf(i, j), uvf(i + 1, j), uvf(i + 1, j + 1), uvf(i, j + 1)]
                self.face([vo[i][j], vo[i + 1][j], vo[i + 1][j + 1], vo[i][j + 1]], uvs, region)
                self.face([vi[i][j + 1], vi[i + 1][j + 1], vi[i + 1][j], vi[i][j]], uvs[::-1], region)
        edge = ([(i, 0) for i in range(n)] + [(n - 1, j) for j in range(1, mm)] +
                [(i, mm - 1) for i in range(n - 2, -1, -1)] + [(0, j) for j in range(mm - 2, 0, -1)])
        for k in range(len(edge)):
            (a, b), (c, d) = edge[k], edge[(k + 1) % len(edge)]
            u = uvf(a, b)
            self.face([vo[a][b], vi[a][b], vi[c][d], vo[c][d]], [u, u, uvf(c, d), uvf(c, d)], region)

    def to_object(self, name, coll):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces)
        bmesh.ops.scale(self.bm, vec=(IN, IN, IN), verts=self.bm.verts)
        me = bpy_mesh(name)
        self.bm.to_mesh(me)
        self.bm.free()
        import bpy
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        for r in REGIONS:
            me.materials.append(common.placeholder_material(r))
        return ob


def bpy_mesh(name):
    import bpy
    return bpy.data.meshes.new(name)


def at(x, y, z=TOP, rot=0.0, capture=True):
    if capture:
        x, y = tbl(x, y)
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rot), 4, "Z")


# --- items ---------------------------------------------------------------------------------

def can(b, M, h, r, label, phase=0.0):
    prof = [(0, 0.0), (r - 0.25, 0.0), (r, 0.3), (r, h - 0.55), (r - 0.28, h - 0.12),
            (r - 0.22, h), (r - 0.4, h - 0.02), (r - 0.45, h - 0.18), (0, h - 0.18)]
    regs = ["steel", "steel", label, "steel", "steel", "steel", "steel", "can_top"]
    b.lathe(prof, regs, M, seg=20, modes={"can_top": "planar"}, radius_uv=r - 0.45, phase=phase)


def jar(b, M, r, h, cap_h, body, cap, cap_r=None, shoulder=0.35):
    cr = cap_r or r * 0.98
    zb = h - cap_h
    prof = [(0, 0.0), (r - 0.1, 0.0), (r, 0.12), (r, zb - shoulder), (r * 0.9, zb),
            (cr, zb), (cr, h - 0.12), (cr - 0.12, h), (0, h)]
    regs = [body, body, body, body, cap, cap, cap, cap]
    b.lathe(prof, regs, M, seg=18, modes={cap: "wrap"})


def spice_jar(b, M, content):
    s = 0.9
    b.box((-s, -s, 0.0), (s, s, 3.25), content, M)
    b.lathe([(0, 3.1), (0.82, 3.1), (0.82, 3.9), (0, 3.9)], ["black_cap"] * 3, M, seg=12)


def laptops(b):
    # tan folder, blank white sheet peeking out west, black laptop, sky-blue laptop
    fx, fy = tbl(*FOLDER)
    b.box((-5.15, -7.65, 0.04), (5.15, 7.65, 0.16), "tan", at(fx, fy, capture=False))
    px, py = tbl(LAPTOP_BLACK[0] - 0.8, 184.0)
    b.box((-4.25, -5.5, 0.0), (4.25, 5.5, 0.04), "paper", at(px, py, rot=2.0, capture=False))
    kx, ky = tbl(*LAPTOP_BLACK)
    M = at(kx, ky, TOP + 0.16, capture=False)
    b.prism(common.rounded_rect(0, 0, 10.0, 15.0, 0.45, seg=3), 0.0, 0.8, "black_plastic", "black_lid",
            "black_plastic", M)
    x, y, rot = LAPTOP_BLUE
    M = at(x, y, TOP + 0.96, rot)
    b.prism(common.rounded_rect(0, 0, 12.0, 8.5, 0.55, seg=3), 0.0, 0.45, "blue_metal", "laptop_lid",
            "blue_metal", M)


def napkin_holder(b):
    M = at(*NAPKINS)
    b.box((-1.45, -3.1, 0.25), (1.45, 3.1, 6.55), "napkin", M)
    for s in (-1, 1):
        x0 = s * 1.55
        b.box((min(x0, x0 + s * 0.12), -3.2, 0.1), (max(x0, x0 + s * 0.12), 3.2, 6.3), "grid_face",
              M @ Matrix.Rotation(0, 4, "Z"))
    b.box((-1.7, -3.2, 0.0), (1.7, 3.2, 0.25), "wire", M)


def plate_and_bowl(b, rnd):
    M = at(*PLATE)
    prof = [(0, 0.05), (3.3, 0.05), (3.5, 0.0), (3.7, 0.2), (5.25, 0.62), (5.25, 0.72),
            (3.6, 0.34), (0, 0.34)]
    regs = ["ceramic", "ceramic", "ceramic", "ceramic", "plate", "plate", "plate"]
    b.lathe(prof, regs, M, seg=28, modes={"plate": "planar"}, radius_uv=5.25)
    Mb = M @ Matrix.Translation((0.2, 0.1, 0.34))
    prof = [(0, 0.0), (1.4, 0.0), (1.5, 0.3), (2.6, 0.9), (3.2, 2.2), (3.2, 2.35),
            (2.95, 2.25), (2.3, 2.45), (1.2, 2.7), (0, 2.8)]
    regs = ["ceramic", "ceramic", "ceramic", "bowl_band", "bowl_band", "bowl_band", "cookies", "cookies", "cookies"]
    b.lathe(prof, regs, Mb, seg=24, modes={"cookies": "planar"}, radius_uv=3.0)
    # wrapped candies round the bowl on the plate rim (colours follow 003750/003751)
    for k in range(11):
        a = 2 * math.pi * k / 11 + rnd.uniform(-0.15, 0.15)
        rr = rnd.uniform(3.9, 4.6)
        z = 0.34 + (rr - 3.6) * 0.25
        Mc = M @ Matrix.Translation((rr * math.cos(a), rr * math.sin(a), z)) @ \
            Matrix.Rotation(a + rnd.uniform(-0.8, 0.8), 4, "Z")
        b.box((-0.7, -0.35, 0.0), (0.7, 0.35, 0.38), "candy_%d" % (k % 8), Mc)
    b.blob(at(*LOOSE_WRAPPER, rot=30), 0.9, 0.55, 0.35, "candy_7", 4, rough=0.3, subdiv=1)


def water_bottle(b):
    M = at(*BOTTLE, rot=200)
    r = 1.65
    prof = [(0, 0.0), (r - 0.15, 0.0), (r, 0.2), (r, 7.7), (r - 0.05, 8.05), (1.55, 8.1), (1.55, 8.5),
            (1.6, 8.55), (1.6, 10.0), (1.35, 10.5), (0, 10.55)]
    regs = ["bottle", "bottle", "bottle", "bottle", "lid_lilac", "lid_lilac", "lid_green", "lid_green",
            "lid_green", "lid_green"]
    b.lathe(prof, regs, M, seg=20, modes={"lid_green": "wrap"})
    # the coral latch tab on the lid front
    b.box((-0.35, 1.5, 8.8), (0.35, 1.72, 9.9), "coral", M @ Matrix.Rotation(math.radians(-90), 4, "Z"))


def tumbler(b):
    M = at(*TUMBLER)
    prof = [(0, 0.0), (1.6, 0.0), (1.7, 0.1), (2.2, 6.75), (2.1, 6.75), (1.6, 0.3), (0, 0.3)]
    regs = ["gray_plastic", "gray_plastic", "gray_plastic", "gray_plastic", "cup_inside", "cup_inside"]
    b.lathe(prof, regs, M, seg=20)


def north_bowl(b):
    M = at(*BOWL_N)
    prof = [(0, 0.0), (1.3, 0.0), (1.4, 0.3), (2.6, 1.2), (3.0, 2.6), (2.85, 2.6), (2.45, 1.3),
            (1.3, 0.45), (0, 0.4)]
    regs = ["ceramic"] * 6 + ["crumbs", "crumbs"]
    b.lathe(prof, regs, M, seg=22, modes={"crumbs": "planar"}, radius_uv=2.6)
    # fork: tines in the bowl bottom, handle up over the north rim (003753/003757)
    Mf = M @ Matrix.Rotation(math.radians(95), 4, "Z")
    pts = [Vector((-1.0, 0.0, 0.55)), Vector((0.6, 0.0, 0.6)), Vector((2.2, 0.0, 1.7)),
           Vector((3.1, 0.0, 2.75)), Vector((5.4, 0.0, 3.2))]
    for i in range(len(pts) - 1):
        a, c = pts[i], pts[i + 1]
        d = c - a
        L = d.length
        w = 0.5 if i == 0 else 0.22
        R = Matrix.Translation(a) @ Matrix.Rotation(-math.atan2(d.z, d.x), 4, "Y")
        b.box((0, -w, -0.04), (L, w, 0.04), "steel", Mf @ R)
    # crumpled paper towel north-west of the bowl, draped against its rim
    b.blob(at(*TOWEL_N, rot=15), 2.6, 1.5, 1.2, "paper_towel", 11, rough=0.3)
    b.blob(at(BOWL_N[0] - 2.6, BOWL_N[1] + 1.6, rot=60), 1.3, 0.9, 1.7, "paper_towel", 12, rough=0.3, subdiv=1)


def jackets(b, rnd):
    """Two garments hung over the south chair's top rail (plan frame, not the table map).
    Each body is a closed cloth slab following a path over the rail: a short front flap on
    the seat side, the long back panel down the chair's back, widening toward the hem,
    with vertical folds and the side edges curling back toward the chair."""
    yt = POST_TOP_Y

    def drape(xc, w_top, w_hem, zf, zb, out, thick, region, nu, amp, nfold, seed, bulge=0.0):
        path = [(yt + 4.0, zf), (yt + 2.9, zf + 4.5), (yt + 1.9, RAIL_TOP - 0.8), (yt + 0.9, RAIL_TOP + 0.55),
                (yt - 0.6, RAIL_TOP + 0.6), (yt - 1.35, RAIL_TOP - 1.2), (yt - 1.6, RAIL_TOP - 7.0),
                (yt - 1.7, (RAIL_TOP - 7.0 + zb) / 2 + 1.0), (yt - 1.6, zb + 3.0), (yt - 1.5, zb)]
        pr = random.Random(seed)
        ph = [pr.uniform(0, 6.28) for _ in range(3)]
        hem = [pr.uniform(-1.2, 1.2) for _ in range(nu)]
        nv = len(path)
        pts, nrm = [], []
        for i in range(nu):
            fu = i / (nu - 1)
            e = (fu - 0.5) * 2.0                       # -1 .. 1 across the width
            row, nrow = [], []
            for j, (y, z) in enumerate(path):
                a, c = path[max(j - 1, 0)], path[min(j + 1, nv - 1)]
                ty, tz = c[0] - a[0], c[1] - a[1]
                L = math.hypot(ty, tz)
                ny, nz = tz / L, -ty / L               # tangent turned 90 deg: away from the chair
                hang = min(1.0, max(0.0, (RAIL_TOP - z) / 20.0))
                width = w_top + (w_hem - w_top) * hang
                fold = amp * hang * (math.sin(e * nfold * math.pi + ph[0])
                                     + 0.4 * math.sin(e * nfold * 2.3 + ph[1] + z * 0.15))
                curl = 2.2 * hang * e ** 4             # edges fall back toward the chair
                bunch = bulge * (1.0 - e * e) * max(0.0, 1.0 - abs(z - RAIL_TOP) / 5.0)
                o = max(out - thick + 0.15, out + fold - curl + bunch)
                if j in (0, nv - 1):
                    z += hem[i]
                row.append(Vector((xc + e * width / 2, y + ny * o, z + nz * o)))
                nrow.append(Vector((0.0, ny, nz)))
            pts.append(row)
            nrm.append(nrow)
        vs = [0.0]
        for j in range(1, nv):
            vs.append(vs[-1] + math.hypot(path[j][0] - path[j - 1][0], path[j][1] - path[j - 1][1]))
        b.slab(pts, thick, region, lambda i, j: (i / (nu - 1), vs[j] / vs[-1]), nrm)

    def sleeve(x0, x1, z0, r0, r1, y_off, region):
        """Tapered sleeve hanging down the back from the shoulder to the cuff."""
        yb = yt - 1.6 - y_off
        pts = [Vector((x0, yb, RAIL_TOP - 2.5)), Vector(((x0 + x1) / 2 + 0.4, yb - 0.4, (RAIL_TOP + z0) / 2)),
               Vector((x1, yb - 0.2, z0))]
        pts = common.smooth_path(pts, 3)
        rings = []
        n = len(pts)
        for k, p in enumerate(pts):
            t = (pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)]).normalized()
            side = t.cross(Vector((0, 1, 0))).normalized()
            up = side.cross(t).normalized()
            r = r0 + (r1 - r0) * k / (n - 1)
            rings.append([p + side * (r * math.cos(a)) + up * (0.7 * r * math.sin(a))
                          for a in [2 * math.pi * q / 8 for q in range(8)]])
        grid = [[rings[k][q] for k in range(n)] for q in range(8)]
        vs = b.grid(grid, region, lambda i, j, reg: (0.05 + 0.1 * i / 8, j / (n - 1)), wrap=True)
        b.face([vs[q][0] for q in range(8)][::-1], [(0.1, 0.0)] * 8, region)
        b.face([vs[q][n - 1] for q in range(8)], [(0.1, 1.0)] * 8, region)

    # navy puffer: the full width of the chair and a little past its west side
    drape(84.5, 17.5, 21.0, 27.0, 7.0, 1.0, 0.95, "navy", 14, 0.9, 2.5, 3, bulge=0.6)
    # rust canvas jacket over it, centre-left, hanging almost to the floor
    drape(82.5, 10.5, 13.0, 22.0, 4.0, 2.55, 0.4, "brown", 12, 1.0, 2.5, 7, bulge=1.6)
    sleeve(75.5, 74.2, 9.0, 1.6, 1.25, 2.0, "navy")
    sleeve(93.0, 94.5, 12.0, 1.6, 1.25, 2.0, "navy")
    sleeve(80.0, 81.0, 3.5, 1.4, 1.1, 3.4, "brown")


# The jackets are cloth simulations made in the live Blender (Blender MCP): each a T-shaped
# pattern (body folded over the chair's top rail at the shoulders, sleeves hanging beside
# the chair) dropped onto the modelled chair, the navy puffer first and the rust canvas
# jacket over it. Saved in blender/assets/dining_jackets.blend (plan frame, metres) with
# their flat-pattern UVs. jackets() above is kept as the fallback.
JACKETS_BLEND = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "dining_jackets.blend")
# sim object -> (atlas region, thickness in, stitch groove depth in, baffles along the length,
# solidify side). The rust jacket was simulated resting on the puffer's sim surface, so the
# puffer's quilting is pressed in (grooves at the stitch lines) and its thickness grows
# inward, while the rust jacket's grows outward: nothing pokes through it.
SIM_JACKETS = {"navy_puffer_final": ("navy", 1.0, 0.45, 12, -1.0), "rust_canvas_final": ("brown", 0.2, 0.0, 0, 1.0)}


RUST_CLEAR = 0.3      # in: the rust jacket is kept at least this far outside the puffer's final surface


def sim_jackets(b):
    from mathutils.bvhtree import BVHTree
    with bpy.data.libraries.load(os.path.abspath(JACKETS_BLEND), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in SIM_JACKETS]
    under = None          # the puffer's thickened surface, for pushing the rust jacket clear of it
    for ob in sorted(dst.objects, key=lambda o: list(SIM_JACKETS).index(o.name)):
        region, thick, bulge, nbaf, side = SIM_JACKETS[ob.name]
        bpy.context.scene.collection.objects.link(ob)
        ob.modifiers.clear()
        me = ob.data
        if bulge:
            # quilted baffles: press the stitch lines in, leaving each band full (v runs along
            # the length)
            bm = bmesh.new()
            bm.from_mesh(me)
            bm.normal_update()
            uvl = bm.loops.layers.uv.active
            for v in bm.verts:
                vs = [l[uvl].uv.y for l in v.link_loops]
                vv = sum(vs) / len(vs) if vs else 0.0
                groove = bulge * (0.5 - 0.5 * math.cos(2 * math.pi * vv * nbaf)) ** 3
                v.co -= v.normal * m(groove)
            bm.to_mesh(me)
            bm.free()
        if under is not None:
            # where the sim let the rust jacket sink into the (now thicker) puffer, lift it
            # back out along the puffer's surface normal; the lifts are spread over the
            # neighbouring vertices so the cloth rises smoothly instead of tearing
            bm = bmesh.new()
            bm.from_mesh(me)
            lift = {}
            for v in bm.verts:
                hit = under.find_nearest(v.co, m(3.0))
                if hit[0] is None:
                    continue
                d = (v.co - hit[0]).dot(hit[1])
                if d < m(RUST_CLEAR):
                    lift[v] = hit[1] * (m(RUST_CLEAR) - d)
            for _ in range(4):
                nxt = dict(lift)
                for v in bm.verts:
                    ns = [lift[e.other_vert(v)] for e in v.link_edges if e.other_vert(v) in lift]
                    if not ns:
                        continue
                    avg = sum(ns, Vector()) * (0.5 / len(v.link_edges))
                    own = lift.get(v)
                    nxt[v] = avg if own is None or avg.length > own.length else own
                lift = nxt
            for v, dv in lift.items():
                v.co += dv
            bm.to_mesh(me)
            bm.free()
        sol = ob.modifiers.new("thick", "SOLIDIFY")
        sol.thickness = m(thick)
        sol.offset = side
        if under is None:
            # where the sim sheet folds back (a turned-up hem) its normal faces the chair and
            # the inward thickness would grow outward through the rust jacket: fade it out there
            vg = ob.vertex_groups.new(name="thick")
            r0 = Vector((m(CHAIR_X - 9.0), m(POST_TOP_Y), m(RAIL_TOP - 1.0)))
            r1 = Vector((m(CHAIR_X + 9.0), m(POST_TOP_Y), m(RAIL_TOP - 1.0)))
            for v in me.vertices:
                t = min(1.0, max(0.0, (v.co - r0).dot(r1 - r0) / (r1 - r0).length_squared))
                out = (v.co - (r0 + (r1 - r0) * t)).normalized()
                vg.add([v.index], min(1.0, max(0.0, 0.5 + 2.5 * out.dot(v.normal))), "REPLACE")
            sol.vertex_group = "thick"
            sol.thickness_vertex_group = 0.0
        dg = bpy.context.evaluated_depsgraph_get()
        ev = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        tmp = bmesh.new()
        tmp.from_mesh(ev)
        if under is None:
            under = BVHTree.FromBMesh(tmp)          # the puffer's final shell (plan frame, identity)
        uvl = tmp.loops.layers.uv.active
        vmap = {v: b.bm.verts.new(v.co / IN) for v in tmp.verts}      # the builder works in inches
        for f in tmp.faces:
            nf = b.face([vmap[v] for v in f.verts], [tuple(l[uvl].uv) for l in f.loops], region)
            if nf is not None:
                nf.smooth = True
        tmp.free()
        bpy.data.meshes.remove(ev)
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.meshes.remove(me)


def build(coll):
    rnd = random.Random(1492)
    b = MB()
    water_bottle(b)
    jar(b, at(*PRINT_CYL), 1.1, 5.5, 0.9, "blossom", "white_cap", cap_r=1.1, shoulder=0.01)
    plate_and_bowl(b, rnd)
    can(b, at(*LIME_A, rot=-35), 6.1, 1.3, "lime_label")
    can(b, at(*LIME_B, rot=-25), 6.1, 1.3, "lime_label")
    can(b, at(*RED_CAN, rot=0), 4.83, 1.3, "red_label")
    x, y, rot = TIN
    ov = [(2.95 * math.cos(a), 1.7 * math.sin(a)) for a in [2 * math.pi * k / 20 for k in range(20)]]
    b.prism(ov, 0.0, 1.9, "tin_side", "tin_top", "steel", at(x, y, rot=rot))
    jar(b, at(*SHAKER, rot=-35), 1.3, 5.8, 1.1, "shaker_label", "red_cap", cap_r=1.35)
    jar(b, at(*BLACK_JAR, rot=180), 1.45, 4.9, 0.95, "jar_label", "white_cap", cap_r=1.42)
    jar(b, at(*WHITE_JAR), 1.2, 4.6, 1.2, "white_cap", "white_cap", cap_r=1.18)
    spice_jar(b, at(*SPICE_FLAKES, rot=10), "glass_flakes")
    spice_jar(b, at(*SPICE_PEPPER, rot=-5), "glass_pepper")
    napkin_holder(b)
    tumbler(b)
    laptops(b)
    north_bowl(b)
    if os.path.exists(JACKETS_BLEND):
        sim_jackets(b)
    else:
        jackets(b, rnd)
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
