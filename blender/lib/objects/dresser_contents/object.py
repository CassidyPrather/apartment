"""Dresser drawer contents: one object per drawer, `dresser_drawer_<n>_contents`, sitting
inside the CLOSED drawer of the `dresser` package (Unity reparents each under its drawer
so it slides out with it). Origin of each object = its drawer's origin.

Built in the dresser's local frame (origin on the floor at the dresser's footprint centre,
front -Y), so it shares the dresser placement: plan (264.75, 18), rotation -90.
The drawer interiors come straight from the dresser package (`drawer_interior`), so the
two stay in sync: inside 30.5 W x 16 D x 8.9 deep (EST, see dresser/object.py).

Photos: Reference/cupboards_drawers, sorted index 21-25 = drawers 1 (top) .. 5 (bottom),
checked by counting the closed fronts above each open drawer (21: none, the top is right
above; 22: one; 23: two; 24: three; 25: four, the drawer nearly on the carpet).
  1  heap of clothes: light frayed denim, blue/navy plaid flannel, a grey-white tee,
     a dusty purple tee, a black shirt at the back                         PHOTO 21
  2  black keyboard (~17.5 x 5.5 x 1.2) at the back left, zip bags of dark cables, a
     pink cable, plain white mailer bags (labels removed: privacy), a zip bag with a
     purple zip strip over a blue cloth, small white boxes                 PHOTO 22
  3  black clothes laid flat, a pink/white/blue striped sock bundle         PHOTO 23
  4  small soft pieces (socks etc.) in pale blue, pink, blush, beige, rust, white,
     lavender and black: generic fabric lumps only                         PHOTO 24
  5  black lace and black/cream print fabric, cream openwork knit, teal and blue
     fabric: generic fabric lumps with print textures                      PHOTO 25
Sizes: garment heaps EST from the photos against the 30.5 in drawer width; fill heights
EST (drawer 1 ~5-6 in, 2 ~4-5, 3 ~2-3, 4 ~3-4, 5 ~3-4). Everything stays below the box
side's top edge.

Fabric = cubes subdivided, rounded, flattened, then displaced with noise and a few sine
folds (no cloth sim). UVs are written per piece (box projection over the piece's own
extent) so prints keep a garment-sized scale inside their atlas rect.
"""

import importlib.util
import math
import os
import random

import bmesh
from mathutils import Matrix, Vector, noise

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "dresser_contents"
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "dresser_object", os.path.join(_here, "..", "dresser", "object.py"))
DRESSER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DRESSER)

ATLAS = {
    "name": "dresser_contents",
    "size": 512,
    "regions": {
        # prints / textured (128 px)
        "denim": (0, 0, 128, 128),
        "plaid": (128, 0, 128, 128),
        "cable_bag": (256, 0, 128, 128),
        "zip_bag": (384, 0, 128, 128),
        "keys": (0, 128, 256, 128),
        "sock_stripe": (256, 128, 128, 128),
        "leopard": (384, 128, 128, 128),
        "lace": (0, 256, 128, 128),
        "crochet": (128, 256, 128, 128),
        # flat fabric / plastic colours (64 px)
        "tee_white": (256, 256, 64, 64),
        "tee_purple": (320, 256, 64, 64),
        "tee_grey": (384, 256, 64, 64),
        "black": (448, 256, 64, 64),
        "mailer": (256, 320, 64, 64),
        "pink_cable": (320, 320, 64, 64),
        "blue_cloth": (384, 320, 64, 64),
        "white_box": (448, 320, 64, 64),
        "pale_blue": (0, 384, 64, 64),
        "hot_pink": (64, 384, 64, 64),
        "blush": (128, 384, 64, 64),
        "beige": (192, 384, 64, 64),
        "rust": (256, 384, 64, 64),
        "sock_white": (320, 384, 64, 64),
        "lavender": (384, 384, 64, 64),
        "teal": (448, 384, 64, 64),
        "navy": (0, 448, 64, 64),
        "kbd_body": (64, 448, 64, 64),
        "black_soft": (128, 448, 64, 64),
        "brown": (192, 448, 64, 64),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dresser_contents": {"atlas": "dresser_contents", "mode": "opaque", "tiled": False}}
COLLIDER = "none"
STATIC = False          # every piece rides in a drawer
VIEWS = [("open_front", 340, 30, 0.8), ("open_high", 20, 55, 0.7)]


# --- piece builder -------------------------------------------------------------------

class Pieces:
    """Accumulates pieces into one Builder bmesh with a per-piece UVMap."""

    def __init__(self, n):
        self.b = common.Builder(REGIONS)
        self.uv = self.b.bm.loops.layers.uv.new("UVMap")
        x0, x1, y0, y1, zf, zt = DRESSER.drawer_interior(n)
        self.lim = (x0 + 0.15, x1 - 0.15, y0 + 0.15, y1 - 0.15, zf, zt - 0.4)
        self.rnd = random.Random(100 + n)

    def _emit(self, verts_local, faces, region, top_region, size, xform):
        """verts_local: piece coords (inches, piece frame); faces: index tuples."""
        bm, b = self.b.bm, self.b
        sx, sy, sz = size
        x0, x1, y0, y1, zf, zt = self.lim
        world = []
        for p in verts_local:
            w = xform @ p
            w.x = min(max(w.x, x0), x1)
            w.y = min(max(w.y, y0), y1)
            w.z = min(max(w.z, zf + 0.02), zt)
            world.append(bm.verts.new(tuple(map(m, w))))
        u0, v0, u1, v1 = common.uv_rect(ATLAS, region)
        tu0, tv0, tu1, tv1 = common.uv_rect(ATLAS, top_region or region)
        pad = 0.04
        for idx in faces:
            f = bm.faces.new([world[i] for i in idx])
            pts = [verts_local[i] for i in idx]
            nrm = (pts[1] - pts[0]).cross(pts[2] - pts[0])
            ax = max(range(3), key=lambda i: abs(nrm[i]))
            ua, va = [(1, 2), (0, 2), (0, 1)][ax]
            ext = (sx, sy, sz)
            if ax == 2 and nrm[2] > 0:
                r, reg = (tu0, tv0, tu1, tv1), (top_region or region)
            else:
                r, reg = (u0, v0, u1, v1), region
            f.material_index = b.idx(reg)
            for loop, p in zip(f.loops, pts):
                fu = min(max(p[ua] / max(ext[ua], 1e-3) + 0.5, 0.0), 1.0)
                fv = min(max(p[va] / max(ext[va], 1e-3) + 0.5, 0.0), 1.0)
                fu = pad + fu * (1 - 2 * pad)
                fv = pad + fv * (1 - 2 * pad)
                loop[self.uv].uv = (r[0] + fu * (r[2] - r[0]), r[1] + fv * (r[3] - r[1]))

    @staticmethod
    def _cube(cuts):
        tmp = bmesh.new()
        bmesh.ops.create_cube(tmp, size=1.0)
        if cuts:
            bmesh.ops.subdivide_edges(tmp, edges=tmp.edges[:], cuts=cuts, use_grid_fill=True)
        tmp.verts.index_update()
        verts = [v.co.copy() for v in tmp.verts]
        faces = [tuple(v.index for v in f.verts) for f in tmp.faces]
        tmp.free()
        return verts, faces

    def lump(self, region, centre, size, rot=0.0, cuts=3, round_=0.45, bumps=0.3,
             folds=3, fold_amp=0.45, tilt=(0.0, 0.0), top_region=None, ragged=0.2, sag=0.45):
        """A soft fabric lump resting on z = centre z: a subdivided box, rounded, with a
        ragged outline, edges sagging like draped cloth, noise bulges and a few creases."""
        sx, sy, sz = size
        verts, faces = self._cube(cuts)
        seed = Vector((self.rnd.uniform(0, 50), self.rnd.uniform(0, 50), self.rnd.uniform(0, 50)))
        fdirs = [(self.rnd.uniform(0, math.pi), self.rnd.uniform(1.0, 2.2),
                  self.rnd.uniform(0, 6.28)) for _ in range(folds)]
        out = []
        for p in verts:
            q = p.copy()
            if q.length > 1e-6:
                q = q * (1 - round_) + q.normalized() * 0.5 * round_ * 1.25
            ang = math.atan2(q.y, q.x)
            rn = noise.noise(seed + Vector((math.cos(ang) * 1.4, math.sin(ang) * 1.4, 0.0)))
            rr = min(1.0, math.hypot(q.x * 2, q.y * 2))
            t = q.z + 0.5                                   # 0 bottom .. 1 top
            q = Vector((q.x * sx * (1 + ragged * rn), q.y * sy * (1 + ragged * rn),
                        t * sz * (1 - sag * rr * rr * t)))
            k = min(max(t, 0.0), 1.0)                       # deform the top more
            n = noise.noise(seed + q * 0.22)
            n2 = noise.noise(seed * 1.7 + q * 0.6)
            q.z += (n * bumps * sz + n2 * 0.1 * sz) * k
            q.x += n2 * 0.05 * sx
            q.y += n * 0.05 * sy
            for fa, freq, ph in fdirs:
                d = q.x * math.cos(fa) + q.y * math.sin(fa)
                q.z += (0.5 - abs(math.sin(d * freq / 2.0 + ph))) * fold_amp * k
            out.append(q)
        zmin = min(q.z for q in out)
        local = [Vector((q.x, q.y, max(q.z - zmin, 0.0) - sz / 2)) for q in out]
        xf = (Matrix.Translation(Vector(centre) + Vector((0, 0, sz / 2)))
              @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Rotation(tilt[0], 4, "X")
              @ Matrix.Rotation(tilt[1], 4, "Y"))
        self._emit(local, faces, region, top_region, (sx, sy, sz), xf)

    def block(self, region, centre, size, rot=0.0, tilt=(0.0, 0.0), top_region=None):
        """A plain box (keyboard, small boxes); centre = bottom centre."""
        sx, sy, sz = size
        verts, faces = self._cube(0)
        local = [Vector((p.x * sx, p.y * sy, p.z * sz)) for p in verts]
        xf = (Matrix.Translation(Vector(centre) + Vector((0, 0, sz / 2)))
              @ Matrix.Rotation(rot, 4, "Z") @ Matrix.Rotation(tilt[0], 4, "X")
              @ Matrix.Rotation(tilt[1], 4, "Y"))
        self._emit(local, faces, region, top_region, size, xf)

    def cable(self, region, points, radius=0.12):
        pts = [tuple(map(m, p)) for p in common.smooth_path(points, 4)]
        faces = self.b.sweep(region, pts, [(m(a), m(c)) for a, c in common.circle_profile(radius, 6)])
        u0, v0, u1, v1 = common.uv_rect(ATLAS, region)
        for f in faces:
            for loop in f.loops:
                loop[self.uv].uv = ((u0 + u1) / 2, (v0 + v1) / 2)

    def floor(self):
        return self.lim[4]

    def finish(self, n, coll):
        org = tuple(map(m, DRESSER.drawer_origin(n)))
        return self.b.to_object(f"dresser_drawer_{n}_contents", coll, origin=org)


# --- the five drawers ------------------------------------------------------------------

def drawer_1(P):
    """Photo 21: plaid flannel heaped on the right, frayed denim on top centre-left, a
    grey-white tee in front of it, a purple tee front left, a black shirt at the back."""
    z = P.floor()
    P.lump("black", (1.0, 5.5, z), (13, 5.5, 4.0), 0.1)
    P.lump("tee_grey", (-9.0, 3.5, z), (10, 8, 2.5), 0.4, folds=2)
    P.lump("tee_purple", (-10.0, -4.0, z), (10.5, 8.5, 4.8), 0.3, fold_amp=0.9, bumps=0.4)
    P.lump("tee_white", (-2.5, -4.0, z), (11, 8.5, 5.0), -0.2, fold_amp=0.9, bumps=0.4)
    P.lump("denim", (-4.0, 1.0, z + 2.6), (12, 9.5, 4.6), 0.15, fold_amp=1.1, bumps=0.4, sag=0.5, ragged=0.3)
    P.lump("plaid", (7.5, 1.5, z), (15, 13, 7.8), -0.1, fold_amp=1.2, bumps=0.4, sag=0.5, folds=4)
    P.lump("plaid", (11.0, -4.5, z), (8.5, 6.5, 4.6), 0.5, fold_amp=0.5)


def drawer_2(P):
    """Photo 22: keyboard on a dark tangle at the back left, white mailers front left with a
    cable over them, a purple-zip bag on a blue cloth front centre, zip bags of black
    cables centre and back right, a pink cable, small white boxes."""
    z = P.floor()
    P.lump("black_soft", (-6.5, 3.0, z), (16, 8, 2.6), 0.0, bumps=0.2, folds=2)
    P.block("kbd_body", (-5.5, 3.6, z + 2.4), (17.5, 5.6, 1.1), math.radians(-5),
            tilt=(math.radians(-7), 0.0), top_region="keys")
    # plain white mailer bags (no labels)
    P.lump("mailer", (-10.0, -2.5, z), (9.0, 10.5, 2.4), -0.15, cuts=2, round_=0.3,
           bumps=0.12, folds=1, fold_amp=0.25, sag=0.25)
    P.lump("mailer", (-8.5, -4.0, z + 2.0), (10.5, 7.5, 2.4), 0.12, cuts=2, round_=0.3,
           bumps=0.12, folds=1, fold_amp=0.3, sag=0.25)
    P.lump("blue_cloth", (0.5, -4.0, z), (10.0, 7.0, 3.0), 0.05, folds=2)
    P.lump("zip_bag", (0.0, -4.0, z + 2.6), (10.0, 6.0, 1.4), -0.3, cuts=2, round_=0.3,
           bumps=0.12, folds=1, fold_amp=0.2, sag=0.2)
    P.lump("cable_bag", (1.5, 0.5, z), (10.5, 8.5, 3.6), -0.4, round_=0.3, bumps=0.2, folds=2, sag=0.6)
    P.lump("cable_bag", (9.5, 3.5, z), (10.0, 8.5, 3.4), 0.35, round_=0.3, bumps=0.2, folds=2, sag=0.6)
    P.lump("cable_bag", (11.0, -4.0, z), (8.0, 7.0, 2.4), 0.2, cuts=2, round_=0.3, bumps=0.2, sag=0.5)
    P.block("white_box", (6.5, -1.5, z), (3.0, 2.2, 1.8), 0.4)
    P.block("white_box", (6.0, -5.5, z), (3.2, 2.0, 1.4), -0.2)
    pts = []
    for i in range(13):
        a = i / 12 * 2 * math.pi * 1.6
        pts.append((4.0 + 2.2 * math.cos(a), 5.0 + 1.5 * math.sin(a), z + 4.3 + 0.3 * math.sin(3 * a)))
    P.cable("pink_cable", pts, 0.16)
    P.cable("black", [(-6.0, 0.5, z + 3.6), (-6.8, -2.0, z + 4.6), (-7.2, -5.0, z + 4.5),
                      (-6.0, -7.6, z + 2.0)], 0.13)


def drawer_3(P):
    """Photo 23: black clothes over most of the floor, a pink/white/blue striped sock
    bundle on the bare floor centre left."""
    z = P.floor()
    P.lump("black", (7.0, 2.0, z), (15, 11.5, 4.2), 0.1, fold_amp=1.0, bumps=0.4, folds=4)
    P.lump("black_soft", (9.0, -4.5, z), (12, 6.5, 2.6), 0.0, folds=2)
    P.lump("black_soft", (-8.5, -5.0, z), (13, 6.0, 2.4), -0.15, folds=2)
    P.lump("black", (0.5, 5.0, z), (9, 5.5, 2.2), 0.3, folds=2)
    P.lump("sock_stripe", (-6.5, 0.0, z), (6.5, 3.6, 2.4), 0.35, round_=0.6,
           bumps=0.2, folds=1, fold_amp=0.2, sag=0.3)
    P.lump("sock_stripe", (-4.0, 1.4, z), (5.5, 3.2, 2.0), -0.5, round_=0.6,
           bumps=0.2, folds=1, fold_amp=0.2, sag=0.3)


def drawer_4(P):
    """Photo 24: small soft pieces packed in, generic lumps in the photo's colours."""
    z = P.floor()
    P.lump("black", (0.0, 0.5, z), (30.0, 15.5, 1.8), 0.0, folds=3, fold_amp=0.3, sag=0.2)
    spots = [  # (region, x, y, w, d, h, rot)
        ("hot_pink", -11.5, -5.2, 6.5, 5.0, 3.2, 0.3),
        ("blush", -8.0, -6.0, 6.0, 3.8, 2.8, -0.4),
        ("black_soft", -12.5, 0.5, 6.0, 7.0, 3.0, 0.1),
        ("pale_blue", -7.0, -1.5, 9.0, 6.5, 4.0, 0.6),
        ("pale_blue", -1.5, -3.5, 7.5, 5.0, 3.4, -0.3),
        ("pale_blue", -2.5, 3.5, 7.5, 5.5, 3.4, 0.2),
        ("rust", 3.5, -2.0, 8.0, 2.4, 2.4, 0.8),
        ("rust", 6.5, -0.5, 7.0, 2.2, 2.2, -0.6),
        ("beige", 5.0, 3.0, 6.0, 4.0, 2.8, 0.2),
        ("lavender", -6.5, 4.5, 6.5, 4.5, 3.0, -0.2),
        ("sock_white", 10.5, 1.5, 5.5, 3.5, 3.0, 0.5),
        ("sock_white", 12.0, -3.5, 5.0, 3.5, 2.8, -0.3),
        ("brown", 1.5, 5.5, 5.0, 4.0, 2.6, 0.4),
        ("black_soft", 1.0, -6.0, 6.0, 4.0, 2.6, 0.0),
        ("blush", 9.5, 5.5, 5.0, 4.0, 2.6, 0.0),
        ("pale_blue", 10.0, -6.0, 5.0, 3.5, 2.4, 0.3),
    ]
    for reg, x, y, w, d, h, rot in spots:
        tilt = (P.rnd.uniform(-0.12, 0.12), P.rnd.uniform(-0.12, 0.12))
        P.lump(reg, (x, y, z + 1.0), (w * 1.1, d * 1.1, h * 0.9), rot, cuts=2, round_=0.85,
               bumps=0.2, folds=2, fold_amp=0.3, sag=0.5, ragged=0.3, tilt=tilt)


def drawer_5(P):
    """Photo 25: black/cream lace print centre, an openwork knit at the back, black lace
    pieces, teal and blue fabric front left."""
    z = P.floor()
    P.lump("black_soft", (0.0, 2.0, z), (28, 11, 1.8), 0.0, folds=3, fold_amp=0.3, sag=0.2)
    P.lump("teal", (-10.0, -4.5, z), (10.0, 7.0, 3.0), 0.2)
    P.lump("navy", (-5.5, -6.0, z), (10.0, 4.5, 2.6), -0.1, cuts=2)
    P.lump("leopard", (-1.5, -1.5, z + 0.8), (13.0, 9.5, 4.0), -0.3, fold_amp=0.6)
    P.lump("lace", (-9.5, -0.5, z + 0.8), (7.0, 6.5, 3.2), 0.4, cuts=2)
    P.lump("lace", (5.5, -4.0, z + 0.6), (7.0, 5.0, 2.6), 0.2, cuts=2)
    P.lump("crochet", (5.0, 3.5, z + 1.0), (12.0, 7.5, 3.8), 0.25)
    P.lump("lace", (11.5, 4.0, z + 0.8), (6.0, 5.0, 2.8), -0.3, cuts=2)
    P.block("white_box", (-1.0, 6.0, z + 0.4), (6.0, 3.5, 0.4), 0.15)   # plain white sheet


BUILDERS = [drawer_1, drawer_2, drawer_3, drawer_4, drawer_5]


def build(coll):
    objs = []
    for n, fn in enumerate(BUILDERS, start=1):
        P = Pieces(n)
        fn(P)
        objs.append(P.finish(n, coll))
    return objs


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        common.collapse_materials(ob, {r: mat for r in REGIONS})
