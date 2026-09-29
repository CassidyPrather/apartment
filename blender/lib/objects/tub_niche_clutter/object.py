"""Bathroom clutter in and around the tub, and everything stored in the linen niche.

Tub (from the bathroom LiDAR capture, frames 281-309, 383-392 caddy; 281-294 rim bottle;
210-263, 460-469 towels):
  shower_caddy     black wire caddy hung from the shower arm on the north (faucet) wall:
                   two baskets, a hook bar, two curled end hooks and two suction cups;
                   upper basket: two gold-pump bottles; lower basket: two sage bottles
                   with brown caps, a dark blue bottle and a clear purple bottle; a razor
                   on the hook bar; a blue and an orange mesh loofah on the end hooks
  tub_rim_bottle   navy spray bottle (orange trigger) on the back ledge of the tub
  bath_towels      two pale-yellow bath towels folded lengthwise over the towel bar
Linen niche (frames 0-65: shelves between the south wall and the tub's stub wall):
  niche_floor      crumpled blue toilet-paper wrappers, white rags, a bagged stack of
                   white shop towels
  niche_shelf_1    grey mask box with mask packets, pill and vitamin bottles, cotton-swab
                   pack, a clear "first aid" bin packed with medicine boxes, and a clear
                   container behind it
  niche_shelf_2    gel nail polishes, lotion and small bottles, a grey board leaning at
                   the back, a makeup-remover wipes box, two perfumes, a cotton-ball bag,
                   a white disc, small cosmetics (spray, jar, palettes, lipstick)
  niche_shelf_3    white earring stand with earrings, scrunchies, a purple studded collar,
                   black and kraft boxes, a white box, a hand mirror, a grey pouch, a teal
                   scarf, small boxes
  niche_shelf_4    two upright pest-control boxes, flat white boxes, a white tote bag, a
                   clear lidded bin of blue gloves, a black massage gun, a black mesh bag,
                   a white plastic bag, two small white bottles

Source of truth: scripted. Frame: PLAN coordinates (+X east, +Y north, Z up, metres from
inches, origin plan (0, 0, 0)); every object is placed at (0, 0, 0) with no rotation.
Anchored to the modelled surfaces: the bathtub package placed at (260.45, 257.05, rot 270)
and bath_fixtures placed 6.45 in west (niche shelves, towel bar). Relative placement
from the capture's splat (Reference/bathroom-splat, registered with
Reference/bathroom_survey/frame.py; survey x = model x + 7.3 near the tub, + 6.45 in the
niche and at the towel bar; survey y = model y + 3.9).

Dimensions (inches, model plan):
  tub north unit wall inner face y 284.75, back wall x 274.2, rim z 17.4    bathtub package
  shower arm x 260.7, z 81.2..82.0, y 279.5..286                            bathtub package
  caddy centre x 261.0, 11 wide, 4.4 deep, hook z 82.3 .. end hooks z 54.8  SCAN (splat) +-1
  caddy baskets z 69.5..73.0 and 59.5..62.8                                 SCAN/PHOTO +-1
  loofahs: blue (256.6, 282.1, 51.8) r 2.6, orange (266.2, 282.3, 51.4) r 2.4  SCAN
  rim bottle (273.3, 260.4) on z 17.4, 1.9 dia x 7.3                        SCAN / EST size
  towel bar x 210.55..235.55, y 283.6, z 60.75                              bath_fixtures
  towels x 209.3..222.6 and 223.0..236.0, hems z 32.8 / 33.4               SCAN
  niche x 260.95..274.6, y 202.5..222.55, shelf tops 22.5/40.1/58.0/75.9   bath_fixtures
  niche item sizes                                                          EST from photos
                                                                            (shelf width 20.05
                                                                            as the scale)
No brands: parody wordmarks on the big labels (see textures.py), blank prints elsewhere.
"""

import math
import random

import bmesh
from mathutils import Matrix, Vector

import atlas_layout
import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "tub_niche_clutter"

# --- anchors (inches, model plan) -----------------------------------------------------
TUB_N_FACE = 284.75            # bathtub: north end unit wall, inner face (plan y)
TUB_BACK_X = 274.2             # bathtub: back unit wall, inner face (plan x)
TUB_RIM = 17.4                 # bathtub: rim height
ARM_X, ARM_Z = 260.7, 81.6     # bathtub: shower arm centreline
CADDY_X = 261.0                # SCAN caddy centre
RIM_BOTTLE = (273.3, 260.4)    # SCAN
BAR_X0, BAR_X1 = 210.55, 235.55   # bath_fixtures towel bar (placed 6.45 west)
BAR_Y, BAR_Z, BAR_R = 283.6, 60.75, 0.375
POSTS_X = (BAR_X0 + 0.6, BAR_X1 - 0.6)
TOWELS = [(209.3, 222.6, 32.8, 3), (223.0, 236.0, 33.4, 11)]   # SCAN x0, x1, front hem z, seed
NX0, NX1 = 260.95, 274.6       # niche front edge / east wall (plan x)
NY0, NY1 = 202.5, 222.55       # niche south wall / stub wall (plan y)
SHELF_TOPS = (22.5, 40.1, 58.0, 75.9)

ATLAS = {
    "name": "tub_niche_clutter",
    "size": 1024,
    "regions": {
        "palette": (0, 0, 256, 256),
        "pump_label": (256, 0, 256, 128),
        "blue_label": (512, 0, 128, 128),
        "sage_label": (640, 0, 128, 128),
        "purple_label": (768, 0, 128, 128),
        "spray_label": (896, 0, 128, 128),
        "loofah_blue": (256, 128, 128, 128),
        "loofah_orange": (384, 128, 128, 128),
        "remover_box": (512, 128, 256, 128),
        "towel": (768, 128, 256, 256),
        "tp_wrap": (0, 256, 256, 128),
        "cotton_bag": (0, 384, 256, 128),
        "insect_box": (256, 256, 128, 256),
        "ant_box": (384, 256, 128, 256),
        "shop_towels": (512, 256, 256, 128),
        "mask_box": (512, 384, 128, 128),
        "med_white": (640, 384, 128, 128),
        "med_orange": (768, 384, 128, 128),
        "med_red": (896, 384, 128, 128),
        "earrings": (0, 512, 256, 128),
        "collar": (0, 640, 128, 128),
        "mesh_black": (128, 640, 128, 128),
        "tote": (256, 512, 256, 256),
        "scarf": (512, 512, 128, 128),
        "kraft_band": (640, 512, 128, 128),
        "blister": (768, 512, 128, 128),
        "rag": (896, 512, 128, 128),
        "vitamin_label": (512, 640, 128, 128),
        "amber_label": (640, 640, 128, 128),
        "lotion": (768, 640, 256, 128),
        "clear": (0, 768, 256, 256),
        "board": (256, 768, 256, 256),
        "palettes": (512, 768, 256, 128),
        "gloves": (512, 896, 256, 128),
    },
}
# 8 x 8 swatches of 32 px in the palette region: name -> (rgb, metallic, smoothness)
PALETTE = {
    "wire_black": ((34, 34, 36), 0.4, 0.45),
    "gold": ((206, 164, 78), 1.0, 0.6),
    "white_plastic": ((238, 236, 230), 0.0, 0.5),
    "cream": ((232, 220, 190), 0.0, 0.4),
    "brown_cap": ((112, 76, 48), 0.0, 0.45),
    "sage": ((208, 214, 198), 0.0, 0.45),
    "navy": ((30, 42, 96), 0.0, 0.5),
    "purple_dark": ((66, 36, 104), 0.0, 0.6),
    "teal": ((52, 176, 196), 0.0, 0.5),
    "lavender": ((206, 192, 232), 0.0, 0.45),
    "orange": ((240, 118, 30), 0.0, 0.45),
    "cord_white": ((240, 240, 236), 0.0, 0.1),
    "amber": ((150, 78, 22), 0.0, 0.7),
    "magenta_glass": ((196, 44, 112), 0.0, 0.85),
    "pink": ((232, 150, 172), 0.0, 0.3),
    "light_blue": ((156, 192, 232), 0.0, 0.3),
    "black_plastic": ((22, 22, 24), 0.0, 0.4),
    "grey": ((150, 150, 152), 0.0, 0.3),
    "kraft": ((196, 158, 104), 0.0, 0.15),
    "burgundy": ((140, 28, 54), 0.0, 0.35),
    "red_dark": ((100, 20, 30), 0.0, 0.6),
    "silver": ((192, 192, 198), 1.0, 0.6),
    "green": ((60, 140, 84), 0.0, 0.3),
    "blue": ((40, 110, 200), 0.0, 0.35),
    "royal": ((30, 76, 186), 0.0, 0.5),
    "paper": ((246, 246, 242), 0.0, 0.1),
    "teal_dark": ((40, 120, 132), 0.0, 0.4),
    "rose_gold": ((206, 150, 128), 0.8, 0.55),
    "purple": ((122, 62, 170), 0.0, 0.35),
    "yellow": ((224, 204, 90), 0.0, 0.3),
    "charcoal": ((58, 58, 62), 0.0, 0.35),
    "beige": ((222, 212, 192), 0.0, 0.2),
    "clear_white": ((236, 238, 240), 0.0, 0.8),
    "red": ((200, 40, 44), 0.0, 0.4),
    "navy_soft": ((40, 44, 80), 0.0, 0.1),
    "acrylic": ((244, 244, 244), 0.0, 0.8),
    "towel_yellow": ((232, 214, 132), 0.0, 0.05),
    "scarlet": ((168, 24, 44), 0.0, 0.1),
    "chrome_grey": ((170, 172, 176), 1.0, 0.7),
}
PAL_NAMES = list(PALETTE)
MATERIALS = {
    NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
    NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": 0.35, "tiled": False},
}
COLLIDER = "none"
STATIC = True
VIEWS = [("plan_top", 0, 89.9, 1.0)]
SLOTS = ["opaque", "clear"]


# --- builder with direct UVs --------------------------------------------------------------

def pal_uv(name):
    i = PAL_NAMES.index(name)
    x, y = 32 * (i % 8) + 16, 32 * (i // 8) + 16
    return (x / 1024.0, 1.0 - y / 1024.0)


class K:
    """common.Builder plus a UV layer; every item is built in local inches, UV-mapped
    in its local frame, then moved into plan metres by a matrix."""

    def __init__(self):
        self.b = common.Builder(SLOTS)
        self.bm = self.b.bm
        self.uv = self.bm.loops.layers.uv.new("UVMap")

    def mark(self):
        return None

    def since(self, mk):
        """Geometry not yet claimed by an item (BMesh reuses freed slots after a bevel, so
        index ranges are not reliable); claims it."""
        dv = self.bm.verts.layers.int.get("done") or self.bm.verts.layers.int.new("done")
        df = self.bm.faces.layers.int.get("done") or self.bm.faces.layers.int.new("done")
        vs = [v for v in self.bm.verts if not v[dv]]
        fs = [f for f in self.bm.faces if not f[df]]
        for v in vs:
            v[dv] = 1
        for f in fs:
            f[df] = 1
        return vs, fs

    def finish(self, mk, look, M, clear=False):
        vs, fs = self.since(mk)
        self.bm.normal_update()
        apply_look(self, fs, look)
        for f in fs:
            f.material_index = 1 if clear else 0
        bmesh.ops.transform(self.bm, matrix=M, verts=vs)
        return fs

    def to_object(self, name, coll):
        for layers in (self.bm.verts.layers.int, self.bm.faces.layers.int):
            lay = layers.get("done")
            if lay is not None:
                layers.remove(lay)
        return self.b.to_object(name, coll)


def _rect(region):
    return atlas_layout.uv_rect(ATLAS, region)


def apply_look(k, faces, look):
    """look: 'c:<palette>' solid; 'b:<region>' each face shows the whole region;
    's:<region>:<palette>' sides show the region, top/bottom solid;
    'w:<region>:<palette>' sides wrap the region around Z (mirrored), caps solid;
    'z:<region>' planar from above (u = x, v = y over the item's bounds)."""
    uv = k.uv
    parts = look.split(":")
    kind = parts[0]
    if kind == "c":
        u = pal_uv(parts[1])
        for f in faces:
            for lp in f.loops:
                lp[uv].uv = u
        return
    region = parts[1]
    u0, v0, u1, v1 = _rect(region)
    pts = [v.co for f in faces for v in f.verts]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ext = Vector([max(hi[i] - lo[i], 1e-6) for i in range(3)])
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    cap = pal_uv(parts[2]) if len(parts) > 2 else None
    for f in faces:
        n = f.normal
        if kind in ("s", "w") and abs(n.z) > 0.6:
            for lp in f.loops:
                lp[uv].uv = cap
            continue
        if kind == "z":
            for lp in f.loops:
                c = lp.vert.co
                lp[uv].uv = (u0 + (c.x - lo.x) / ext.x * (u1 - u0), v0 + (c.y - lo.y) / ext.y * (v1 - v0))
            continue
        if kind == "w":
            # u = 0.5 at the item's front (-Y), seam at the back
            angs = [math.atan2(lp.vert.co.x - cx, -(lp.vert.co.y - cy)) for lp in f.loops]
            if max(angs) - min(angs) > math.pi:
                angs = [math.pi * 0.99] * len(angs)
            for lp, t in zip(f.loops, angs):
                c = lp.vert.co
                fu = min(max(0.5 + t / (2 * math.pi), 0.0), 1.0)
                lp[uv].uv = (u0 + fu * (u1 - u0), v0 + (c.z - lo.z) / ext.z * (v1 - v0))
            continue
        # per-face box projection over the face's own extent
        ax = max(range(3), key=lambda i: abs(n[i]))
        ua, va = [(1, 2), (0, 2), (0, 1)][ax]
        fl = [lp.vert.co for lp in f.loops]
        flo = [min(c[i] for c in fl) for i in range(3)]
        fhi = [max(c[i] for c in fl) for i in range(3)]
        for lp in f.loops:
            c = lp.vert.co
            fu = (c[ua] - flo[ua]) / max(fhi[ua] - flo[ua], 1e-6)
            fv = (c[va] - flo[va]) / max(fhi[va] - flo[va], 1e-6)
            if ax == 1 and n[1] > 0 or ax == 0 and n[0] < 0:
                fu = 1 - fu
            lp[uv].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def MT(x, y, z, rot=0.0, tilt=(0.0, 0.0)):
    """Local inches -> plan metres at plan point (x, y, z), heading rot (deg about Z),
    tilt (deg about local X, local Y)."""
    return (Matrix.Translation((m(x), m(y), m(z))) @ Matrix.Rotation(math.radians(rot), 4, "Z")
            @ Matrix.Rotation(math.radians(tilt[0]), 4, "X") @ Matrix.Rotation(math.radians(tilt[1]), 4, "Y")
            @ Matrix.Scale(IN, 4))


def NM(level_z, a, b, rot=0.0, tilt=(0.0, 0.0)):
    """Niche placement: a = depth from the shelf front edge (toward the east wall),
    b = distance from the stub wall (toward the south wall). Local +X runs along b
    (south), local +Y along a (east), so an item's -Y face looks out of the niche."""
    return MT(NX0 + a, NY1 - b, level_z, -90.0 + rot, tilt)


# --- primitives in local inches ---------------------------------------------------------

def box(k, look, w, d, h, M, bevel=0.06, z0=0.0, clear=False):
    mk = k.mark()
    k.b.box("opaque", (-w / 2, -d / 2, z0), (w / 2, d / 2, z0 + h), bevel=bevel, segments=1)
    return k.finish(mk, look, M, clear)


def cyl(k, look, r, h, M, seg=10, z0=0.0, axis="Z", clear=False):
    mk = k.mark()
    c = (0, 0, z0 + h / 2) if axis == "Z" else (0, 0, z0)
    k.b.cylinder("opaque", c, r, h, axis=axis, segments=seg)
    return k.finish(mk, look, M, clear)


def oval(k, look, w, d, h, M, z0=0.0, seg=12, taper=1.0):
    """Rounded-oval prism (bottle body), optional top taper."""
    mk = k.mark()
    ring = [(w / 2 * math.cos(2 * math.pi * i / seg), d / 2 * math.sin(2 * math.pi * i / seg))
            for i in range(seg)]
    ring = [(x * (1 + 0.12 * (1 - abs(math.cos(4 * math.pi * i / seg)))), y) for i, (x, y) in enumerate(ring)]
    faces = k.b.prism("opaque", ring, z0, z0 + h)
    if taper != 1.0:
        top = [v for f in faces for v in f.verts if abs(v.co.z - (z0 + h)) < 1e-6]
        for v in set(top):
            v.co.x *= taper
            v.co.y *= taper
    return k.finish(mk, look, M)


def wire(k, pts, M, r=0.09, look="c:wire_black", sides=4, closed=False, prof=None):
    mk = k.mark()
    prof = prof or [(r * math.cos(2 * math.pi * (i + 0.5) / sides),
                     r * math.sin(2 * math.pi * (i + 0.5) / sides)) for i in range(sides)]
    k.b.sweep("opaque", pts, prof, up=(0, 0, 1), closed=closed)
    return k.finish(mk, look, M)


def _noise(p, seed, amp, freq):
    rnd = random.Random(seed)
    s = 0.0
    for _ in range(4):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized()
        s += math.sin(d.dot(p) * freq * rnd.uniform(0.7, 1.4) + rnd.uniform(0, 6.3))
    return amp * s / 2.0


def blob(k, look, rx, ry, rz, M, seed=1, amp=0.18, freq=2.0, sub=2, floor=0.0, flat=True):
    """Lumpy ellipsoid (crumpled bag, rag heap, loofah) standing on local z = floor."""
    mk = k.mark()
    res = bmesh.ops.create_icosphere(k.bm, subdivisions=sub, radius=1.0)
    for v in res["verts"]:
        d = v.co.normalized()
        s = 1.0 + _noise(d * 3.0, seed, amp, freq)
        v.co = Vector((d.x * rx * s, d.y * ry * s, d.z * rz * s + rz))
        if flat and v.co.z < floor + 0.05 * rz:
            v.co.z = floor + max(v.co.z - floor, 0.0) * 0.08
    k.b._tag([f for v in res["verts"] for f in v.link_faces], "opaque")
    return k.finish(mk, look, M)


# --- tub ------------------------------------------------------------------------------------

def caddy(k):
    """Everything local to the caddy: x from CADDY_X, y = -(distance from the unit wall)."""
    M = MT(CADDY_X, TUB_N_FACE, 0.0)
    ax = ARM_X - CADDY_X
    D = 0.7                                          # standoff of the frame (suction cups)
    zs = [78.4, 76.5, 73.0, 69.0, 65.0, 61.0, 57.8, 56.2]
    hw = [2.0, 3.4, 4.7, 5.3, 5.5, 5.3, 4.9, 4.9]
    for s in (-1, 1):
        pts = [(s * w, -D, z) for w, z in zip(hw, zs)]
        pts += [(s * 4.95, -1.3, 55.2), (s * 4.95, -2.1, 55.35), (s * 4.95, -2.45, 56.0)]
        wire(k, common.smooth_path(pts, 3)[:-1] + [pts[-1]], M, r=0.1)
        cyl(k, "c:wire_black", 0.2, 0.4, M @ Matrix.Translation((s * 4.95, -2.45, 56.0)), seg=6)
    # hanger: joins the rail tops, rises and loops over the shower arm (x-z plane)
    wire(k, [(-2.0, -D, 78.4), (2.0, -D, 78.4)], M, r=0.1)
    hook = [(ax, -D, 78.4), (ax - 0.55, -D, 80.6)]
    for i in range(7):
        t = math.pi * (1 - i / 6)
        hook.append((ax + 0.62 * math.cos(t), -D, ARM_Z + 0.62 * math.sin(t)))
    hook.append((ax + 0.62, -D, ARM_Z - 0.35))
    wire(k, hook, M, r=0.1)
    # suction cups on the unit wall behind the lower basket
    for s in (-1, 1):
        cyl(k, "c:clear_white", 0.8, 0.3, M @ Matrix.Translation((s * 3.2, -0.2, 60.6)),
            seg=10, axis="Y", clear=True)
        wire(k, [(s * 3.2, -0.3, 60.6), (s * 3.2, -D, 60.6)], M, r=0.12)

    def basket(zb, zt, w, dep):
        n = 14

        def rim(z, hw_, d0, d1):
            pts = []
            for i in range(n):          # front arc from -x to +x
                t = i / (n - 1)
                x = -hw_ + 2 * hw_ * t
                bow = math.sin(math.pi * t)
                pts.append((x, -(d0 + (d1 - d0) * (0.55 + 0.45 * bow)), z))
            return pts
        bot = rim(zb, w, D, D + dep)
        top = rim(zt, w + 0.35, D, D + dep + 0.5)
        for ring in (bot, top):
            wire(k, [(ring[0][0], -D, ring[0][2])] + ring + [(ring[-1][0], -D, ring[-1][2])], M, r=0.1)
        wire(k, [(-w - 0.35, -D, zt), (w + 0.35, -D, zt)], M, r=0.09)
        for i in range(0, n, 1):
            wire(k, [bot[i], top[i]], M, r=0.07)
        for s in (-1, 1):                # side bars
            for f in (0.35, 0.7):
                p0 = (s * w, -(D + (bot[0 if s < 0 else -1][1] * -1 - D) * f), zb)
                p1 = (s * (w + 0.35), -(D + (top[0 if s < 0 else -1][1] * -1 - D) * f), zt)
                wire(k, [p0, p1], M, r=0.07)
        for f in (0.3, 0.6, 0.85):     # floor wires
            dd = D + dep * f
            wire(k, [(-w, -dd, zb), (w, -dd, zb)], M, r=0.07)
    basket(69.5, 73.0, 5.0, 3.9)
    basket(59.5, 62.8, 5.1, 4.1)
    # hook bar with a row of small J hooks
    wire(k, [(-4.9, -1.0, 57.8), (4.9, -1.0, 57.8)], M, r=0.09)
    for x in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0):
        wire(k, [(x, -1.0, 57.8), (x, -1.0, 56.9), (x, -1.45, 56.5), (x, -1.85, 56.95)], M, r=0.07)

    # upper basket: two gold-pump bottles
    for x in (-2.35, 2.35):
        Mb = M @ Matrix.Translation((x, -2.75, 69.6))
        oval(k, "w:pump_label:white_plastic", 3.3, 2.1, 7.2, Mb)
        oval(k, "c:white_plastic", 3.3, 2.1, 0.6, Mb, z0=7.2, taper=0.6)
        cyl(k, "c:gold", 0.42, 0.7, Mb, seg=8, z0=7.8)
        cyl(k, "c:gold", 0.55, 0.55, Mb, seg=8, z0=8.5)
        box(k, "c:gold", 0.35, 1.4, 0.35, Mb @ Matrix.Translation((0, -0.6, 8.75)), bevel=0.05)
    # lower basket: sage, sage, dark blue, clear purple (west to east)
    for x in (-3.75, -1.65):
        Mb = M @ Matrix.Translation((x, -2.7, 59.6))
        cyl(k, "w:sage_label:sage", 1.0, 5.6, Mb, seg=10)
        cyl(k, "c:sage", 0.75, 0.45, Mb, seg=10, z0=5.6)
        cyl(k, "c:brown_cap", 0.58, 1.1, Mb, seg=10, z0=6.05)
    Mb = M @ Matrix.Translation((0.75, -2.6, 59.6))
    box(k, "s:blue_label:navy", 2.5, 1.5, 6.6, Mb, bevel=0.3)
    box(k, "c:navy", 1.3, 1.1, 0.6, Mb, z0=6.6, bevel=0.15)
    Mb = M @ Matrix.Translation((3.35, -2.8, 59.6))
    oval(k, "w:purple_label:purple_dark", 2.3, 1.7, 7.0, Mb)
    cyl(k, "c:cream", 0.85, 0.9, Mb, seg=10, z0=7.0)
    # razor hanging on the hook bar: lavender head, teal handle
    wire(k, [(0.9, -1.55, 57.05), (2.6, -1.75, 56.85), (4.4, -1.85, 56.95)], M, r=0.28,
         look="c:teal", sides=6)
    box(k, "c:lavender", 1.5, 0.45, 0.8, M @ Matrix.Translation((0.25, -1.55, 56.65)), bevel=0.1)
    # loofahs on the end hooks, on white cords
    for x, look, r, z, seed in ((-4.4, "b:loofah_blue", 2.9, 51.6, 4), (5.2, "b:loofah_orange", 2.7, 51.3, 9)):
        s = -1 if x < 0 else 1
        wire(k, [(s * 4.95, -2.4, 55.9), (s * 4.95 + (x - s * 4.95) * 0.5, -2.55, z + r + 0.9),
                 (x, -2.6, z + r * 0.8)], M, r=0.1, look="c:cord_white", sides=4)
        blob(k, look, r, r * 0.8, r * 0.95, M @ Matrix.Translation((x, -2.7, z - r * 0.95)),
             seed=seed, amp=0.1, freq=4.0, sub=3, flat=False)


def rim_bottle(k):
    x, y = RIM_BOTTLE
    M = MT(x, y, TUB_RIM, -70.0)
    cyl(k, "w:spray_label:navy", 0.95, 5.4, M, seg=10)
    cyl(k, "c:navy", 0.95, 0.5, M @ Matrix.Translation((0, 0, 5.4)), seg=10)
    cyl(k, "c:orange", 0.42, 0.6, M, seg=8, z0=5.9)
    box(k, "c:orange", 0.8, 1.9, 0.7, M @ Matrix.Translation((0, -0.35, 6.5)), bevel=0.12)
    box(k, "c:orange", 0.5, 0.35, 1.0, M @ Matrix.Translation((0, -0.95, 5.6)), bevel=0.08)


# --- towels ------------------------------------------------------------------------------

def towel(k, x0, x1, hem_front, seed):
    """One towel folded lengthwise and hung over the bar: back layer between the bar and
    the wall, over the bar, front layer hanging to the hem; vertical folds deepen toward
    the hem. Built directly in plan inches, UV over the whole region (hem bands at both
    ends of the length)."""
    rnd = random.Random(seed)
    R = BAR_R + 0.18
    T = 0.12                                       # half thickness
    hem_back = hem_front + 1.2
    path = []                                      # (y, z) back hem -> front hem
    nb, na, nf = 8, 5, 10
    for i in range(nb + 1):
        t = i / nb
        path.append((BAR_Y + R + 0.55 * (1 - t) ** 1.5, hem_back + (BAR_Z - hem_back) * t))
    for i in range(1, na):
        th = math.pi * i / na
        path.append((BAR_Y + R * math.cos(th), BAR_Z + R * math.sin(th)))
    for i in range(nf + 1):
        t = i / nf
        path.append((BAR_Y - R - 1.7 * t ** 1.4, BAR_Z + (hem_front - BAR_Z) * t))
    ns = len(path)
    arc = [0.0]
    for a, b in zip(path, path[1:]):
        arc.append(arc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    S = arc[-1]
    nx = 11
    ph = [rnd.uniform(0, 6.3) for _ in range(3)]
    lam = [rnd.uniform(3.0, 4.2), rnd.uniform(5.5, 7.5), rnd.uniform(1.8, 2.4)]
    u0, v0, u1, v1 = _rect("towel")

    def point(i, j, side):
        y, z = path[j]
        t = i / nx
        x = x0 + (x1 - x0) * t
        # distance down from the bar (0 at the top, 1 at the hem) on either layer
        drop = max(0.0, (BAR_Z - z) / (BAR_Z - min(hem_front, hem_back)))
        front = j > nb + na - 1
        fold = (math.sin(2 * math.pi * x / lam[0] + ph[0]) * 0.75
                + math.sin(2 * math.pi * x / lam[1] + ph[1]) * 0.5
                + math.sin(2 * math.pi * x / lam[2] + ph[2]) * 0.18)
        amp = (0.2 + 0.9 * drop ** 1.2) * (1.0 if front else 0.35)
        yy = y - amp * fold * (1 if front else -1) - (0.0 if front else 0.0)
        if not front:
            yy = min(yy, 285.75 - T)            # the wall is at 286
        zz = z
        if j in (0, ns - 1):
            zz += 0.35 * math.sin(2 * math.pi * x / lam[1] + ph[2])
        # sides flare slightly toward the hem
        if i in (0, nx):
            x += (-1 if i == 0 else 1) * 0.35 * drop + 0.15 * math.sin(z * 0.7)
        # in-plane normal of the path (y, z) for the thickness
        ja, jb = max(j - 1, 0), min(j + 1, ns - 1)
        ty, tz = path[jb][0] - path[ja][0], path[jb][1] - path[ja][1]
        L = math.hypot(ty, tz) or 1.0
        ny_, nz_ = tz / L, -ty / L                # points outward (away from the bar)
        return Vector((x, yy + side * T * ny_, zz + side * T * nz_))

    bm = k.bm
    mk = k.mark()
    outer = [[bm.verts.new(point(i, j, 1)) for i in range(nx + 1)] for j in range(ns)]
    inner = [[bm.verts.new(point(i, j, -1)) for i in range(nx + 1)] for j in range(ns)]
    uv = k.uv

    def face(vs, uvs):
        f = bm.faces.new(vs)
        for lp, c in zip(f.loops, uvs):
            lp[uv].uv = (u0 + c[0] * (u1 - u0), v0 + c[1] * (v1 - v0))
        return f

    def U(i, j):
        return (i / nx, arc[j] / S)
    for j in range(ns - 1):
        for i in range(nx):
            face([outer[j][i], outer[j][i + 1], outer[j + 1][i + 1], outer[j + 1][i]],
                 [U(i, j), U(i + 1, j), U(i + 1, j + 1), U(i, j + 1)])
            face([inner[j][i], inner[j + 1][i], inner[j + 1][i + 1], inner[j][i + 1]],
                 [U(i, j), U(i, j + 1), U(i + 1, j + 1), U(i + 1, j)])
    for j in range(ns - 1):
        for i, rev in ((0, True), (nx, False)):
            vs = [outer[j][i], outer[j + 1][i], inner[j + 1][i], inner[j][i]]
            uvs = [U(i, j), U(i, j + 1), U(i, j + 1), U(i, j)]
            if not rev:
                vs, uvs = vs[::-1], uvs[::-1]
            face(vs, uvs)
    for j, rev in ((0, False), (ns - 1, True)):
        for i in range(nx):
            vs = [outer[j][i], outer[j][i + 1], inner[j][i + 1], inner[j][i]]
            uvs = [U(i, j), U(i + 1, j), U(i + 1, j), U(i, j)]
            if rev:
                vs, uvs = vs[::-1], uvs[::-1]
            face(vs, uvs)
    vs, fs = k.since(mk)
    for f in fs:
        f.material_index = 0
    bmesh.ops.transform(bm, matrix=Matrix.Scale(IN, 4), verts=vs)


# --- linen niche -----------------------------------------------------------------------

def niche_floor(k):
    z = 0.0
    # bagged stack of white shop towels, front right, black label band on top
    box(k, "b:shop_towels", 8.8, 10.5, 5.4, NM(z, 5.6, 14.6, 4), bevel=0.5)
    # white rag heap on top of / behind it, and loose rags front left
    blob(k, "b:rag", 4.6, 4.4, 3.2, NM(z, 7.0, 14.6) @ Matrix.Translation((0, 0, 5.0)), seed=21, amp=0.25, freq=2.5)
    blob(k, "b:rag", 4.5, 3.0, 2.5, NM(z, 3.0, 5.0, 10), seed=22, amp=0.18, freq=2.8)
    # crumpled blue toilet-paper wrappers, tall heap left/centre behind the rags
    blob(k, "b:tp_wrap", 4.4, 3.9, 5.6, NM(z, 7.8, 6.8, 15), seed=24, amp=0.25, freq=2.2)
    blob(k, "b:tp_wrap", 3.4, 2.6, 2.8, NM(z, 4.0, 8.2, -25) @ Matrix.Translation((0, 0, 3.0)),
         seed=25, amp=0.25, freq=2.6)
    blob(k, "b:tp_wrap", 1.8, 1.4, 1.0, NM(z, 1.5, 2.5, 40), seed=26, amp=0.25, freq=2.4)


def shelf1(k):
    z = SHELF_TOPS[0]
    # grey mask box (north, front) with mask packets on top and behind it
    box(k, "b:mask_box", 4.4, 7.6, 8.3, NM(z, 4.2, 3.0), bevel=0.08)
    for a, b, rot, zz in ((5.0, 3.2, 8, 8.3), (6.2, 3.6, -12, 8.7), (10.8, 3.5, 20, 0.0), (10.5, 5.0, -5, 1.2)):
        blob(k, "c:paper", 3.2, 2.4, 0.45, NM(z, a, b, rot) @ Matrix.Translation((0, 0, zz)),
             seed=int(a * 10), amp=0.12, freq=2.0, sub=1)
    box(k, "c:paper", 1.1, 1.0, 3.8, NM(z, 1.0, 5.8, 5), bevel=0.2)      # cotton-swab pack
    # pill bottles
    for a, b in ((1.2, 7.1), (1.3, 8.9)):
        cyl(k, "w:amber_label:amber", 0.8, 2.6, NM(z, a, b), seg=10)
        cyl(k, "c:white_plastic", 0.86, 0.6, NM(z, a, b), seg=10, z0=2.6)
    cyl(k, "w:vitamin_label:burgundy", 1.25, 4.5, NM(z, 3.4, 9.2), seg=12)
    cyl(k, "c:white_plastic", 1.1, 0.8, NM(z, 3.4, 9.2), seg=12, z0=4.5)
    cyl(k, "c:red_dark", 1.05, 3.9, NM(z, 4.6, 6.9), seg=10)
    cyl(k, "c:white_plastic", 0.9, 0.7, NM(z, 4.6, 6.9), seg=10, z0=3.9)
    # clear first-aid bin on the south half, sticking out past the shelf front
    bx = NM(z, 2.0, 15.3)
    W, D, H, t = 9.4, 14.0, 9.0, 0.12
    box(k, "c:clear_white", W, D, 0.15, bx, bevel=0.0, clear=True)
    for sx in (-1, 1):
        box(k, "c:clear_white", t, D, H, bx @ Matrix.Translation((sx * (W / 2 - t / 2), 0, 0)), bevel=0.0, clear=True)
    for sy in (-1, 1):
        box(k, "c:clear_white", W, t, H, bx @ Matrix.Translation((0, sy * (D / 2 - t / 2), 0)), bevel=0.0, clear=True)
    box(k, "c:paper", 2.4, 0.05, 0.8, bx @ Matrix.Translation((0.8, -D / 2 - 0.05, 5.0)), bevel=0.0)  # blank label
    # contents: a jumble of boxes, blister packs and bottles filling the bin
    inside = [("b:med_white", 2.3, 1.4, 8.6, (-2.6, -4.8), (8, 12)),     # tall white box sticking up front
              ("b:blister", 4.6, 0.6, 3.4, (-0.2, -3.2), (-25, 0)),
              ("b:med_white", 3.0, 1.0, 6.8, (0.8, -0.5), (10, 30)),
              ("b:blister", 3.6, 0.5, 7.4, (-0.6, 0.8), (-15, 12)),
              ("c:paper", 3.2, 0.3, 8.8, (-1.8, 3.2), (20, -8)),
              ("b:med_orange", 2.0, 1.9, 8.4, (2.6, 4.8), (0, -4)),
              ("b:med_red", 3.6, 1.6, 2.2, (1.2, 3.2), (0, 20)),
              ("c:white_plastic", 1.1, 1.1, 4.6, (3.3, -3.8), (0, 0)),
              ("c:white_plastic", 1.2, 1.2, 3.8, (1.8, -4.9), (0, 0)),
              ("b:blister", 3.2, 0.5, 3.0, (-2.3, 1.8), (15, -10)),
              ("c:red", 1.4, 1.2, 3.6, (3.1, 0.8), (0, 5)),
              ("c:green", 2.2, 0.9, 3.2, (-1.4, -1.2), (-10, 0)),
              ("c:paper", 3.4, 2.8, 1.5, (-2.0, 4.4), (0, 0))]
    for look, w, d, h, (lx, ly), (rot, tl) in inside:
        box(k, look, w, d, h, bx @ Matrix.Translation((lx, ly, 0.2)) @ Matrix.Rotation(math.radians(rot), 4, "Z")
            @ Matrix.Rotation(math.radians(tl), 4, "X"), bevel=0.05)
    blob(k, "c:paper", 3.8, 3.4, 1.4, bx @ Matrix.Translation((-0.8, 2.0, 5.4)), seed=31, amp=0.2, freq=2.0, sub=1)
    # clear container at the back behind the bin
    bb = NM(z, 11.8, 13.8)
    box(k, "c:clear_white", 9.0, 3.6, 5.6, bb, bevel=0.3, clear=True)
    box(k, "c:pink", 2.2, 1.6, 1.4, NM(z, 11.6, 11.5, 10) @ Matrix.Translation((0, 0, 5.6)), bevel=0.3)


def shelf2(k):
    z = SHELF_TOPS[1]
    # gel nail polishes: tall black caps, bottles in dark and bright colours
    rnd = random.Random(12)
    cols = ["black_plastic", "navy", "clear_white", "teal_dark", "burgundy", "black_plastic", "pink",
            "red_dark", "navy", "black_plastic", "teal_dark", "purple_dark", "charcoal", "black_plastic"]
    spots = [(0.9, 0.8), (0.9, 2.0), (0.9, 3.2), (0.9, 4.4), (1.0, 5.6), (2.2, 1.3), (2.2, 2.6),
             (2.3, 3.8), (2.3, 5.0), (3.5, 0.9), (3.6, 2.1), (3.6, 3.3), (3.7, 4.5), (4.5, 1.0)]
    for (a, b), c in zip(spots, cols):
        Mp = NM(z, a + rnd.uniform(-0.15, 0.15), b + rnd.uniform(-0.15, 0.15), rnd.uniform(0, 40))
        box(k, "c:" + c, 1.05, 1.05, 1.5, Mp, bevel=0.2)
        cyl(k, "c:black_plastic", 0.36, 2.0, Mp, seg=8, z0=1.5)
    # lotion bottle (white, black cap), small white bottle, black charger
    oval(k, "w:lotion:white_plastic", 2.5, 1.7, 7.4, NM(z, 6.0, 2.6))
    cyl(k, "c:black_plastic", 0.6, 1.1, NM(z, 6.0, 2.6), seg=10, z0=7.4)
    cyl(k, "c:white_plastic", 0.8, 4.2, NM(z, 6.4, 5.0), seg=10)
    cyl(k, "c:white_plastic", 0.55, 0.9, NM(z, 6.4, 5.0), seg=10, z0=4.2)
    box(k, "c:black_plastic", 1.5, 1.2, 1.3, NM(z, 8.0, 6.8, 20), bevel=0.15)
    # grey speckled board leaning on the back wall
    box(k, "b:board", 10.5, 0.3, 10.2, NM(z, 12.0, 6.3, 0, (-8, 0)), bevel=0.02)
    # makeup-remover wipes box (open display box) with the wipes pack inside
    Mr = NM(z, 1.8, 8.6, 6)
    box(k, "s:remover_box:light_blue", 4.2, 3.2, 3.2, Mr, bevel=0.05)
    box(k, "c:light_blue", 3.4, 2.3, 1.6, Mr @ Matrix.Translation((0, 0.3, 3.0)) @ Matrix.Rotation(math.radians(-25), 4, "X"), bevel=0.5)
    # two perfumes
    for a, b in ((1.3, 11.6), (1.5, 13.5)):
        Mp = NM(z, a, b, 4)
        box(k, "c:magenta_glass", 1.7, 1.2, 3.5, Mp, bevel=0.15)
        cyl(k, "c:gold", 0.55, 1.3, Mp, seg=10, z0=3.5)
    # cotton-ball bag (back right) with a teal resealable bag on top, white disc behind
    box(k, "s:cotton_bag:paper", 6.8, 4.6, 10.2, NM(z, 8.8, 15.2, -6), bevel=0.9)
    blob(k, "c:teal", 3.0, 2.0, 1.2, NM(z, 9.0, 15.6, 15) @ Matrix.Translation((0, 0, 9.8)), seed=42, amp=0.2, freq=2.2, sub=1)
    cyl(k, "c:white_plastic", 3.4, 0.25, NM(z, 12.0, 15.0, 0, (-12, 0)) @ Matrix.Translation((0, 0, 3.4)),
        seg=14, axis="Y")
    # small cosmetics on the south half
    cyl(k, "c:charcoal", 0.6, 3.2, NM(z, 5.0, 13.6), seg=8)
    cyl(k, "c:black_plastic", 0.35, 1.2, NM(z, 5.0, 13.6), seg=8, z0=3.2)
    cyl(k, "c:black_plastic", 1.2, 1.3, NM(z, 4.6, 16.0), seg=12)
    box(k, "c:paper", 1.8, 1.2, 4.2, NM(z, 4.0, 18.6, -8), bevel=0.05)
    box(k, "b:palettes", 3.6, 2.0, 0.45, NM(z, 3.4, 12.8, 3), bevel=0.05)
    box(k, "b:palettes", 3.0, 2.0, 0.45, NM(z, 3.4, 12.9, -6) @ Matrix.Translation((0, 0, 0.45)), bevel=0.05)
    box(k, "c:silver", 3.2, 3.0, 0.45, NM(z, 1.6, 16.3, 0), bevel=0.05)
    box(k, "c:royal", 2.0, 2.2, 0.6, NM(z, 1.5, 19.0), bevel=0.1)
    cyl(k, "c:gold", 0.42, 3.0, NM(z, 1.4, 19.0, 70) @ Matrix.Translation((0, 0, 1.02)), seg=8, axis="X")


def shelf3(k):
    z = SHELF_TOPS[2]
    # white acrylic earring stand at the back: tray, dark backing with the earrings, tiers
    Ms = NM(z, 10.6, 12.6)
    box(k, "c:acrylic", 9.6, 4.2, 0.9, Ms @ Matrix.Translation((0, -1.8, 0)), bevel=0.2)
    box(k, "b:earrings", 8.8, 0.15, 4.6, Ms @ Matrix.Translation((0, 0.9, 0.9)), bevel=0.0)
    for zz in (1.6, 3.1, 4.7):
        box(k, "c:acrylic", 9.6, 0.5, 0.45, Ms @ Matrix.Translation((0, 0.55, zz)), bevel=0.08)
    for sx in (-1, 1):
        box(k, "c:acrylic", 0.35, 0.8, 5.4, Ms @ Matrix.Translation((sx * 4.8, 0.7, 0)), bevel=0.08)
    for dx in (-0.6, 0.6):   # red scrunchies in the tray
        blob(k, "c:scarlet", 1.0, 0.9, 0.55, Ms @ Matrix.Translation((dx, -2.4, 0.9)), seed=50, amp=0.25, freq=4.0, sub=1)
    blob(k, "c:cord_white", 0.9, 0.9, 0.5, Ms @ Matrix.Translation((-3.6, -2.2, 0.9)), seed=53, amp=0.3, freq=4.0, sub=1)
    # purple studded collar hanging off the stand's south end and lying across the front
    Mc = NM(z, 0.0, 0.0)
    strap = [(-0.5, -0.08), (0.5, -0.08), (0.5, 0.08), (-0.5, 0.08)]
    wire(k, common.smooth_path([(17.6, 11.0, 5.3), (18.6, 8.0, 1.6), (18.9, 5.5, 1.3), (18.6, 3.0, 1.3),
                                (18.2, 0.6, 1.3)], 3), Mc, look="b:collar", prof=strap)
    # black flat box (front right) and kraft box with a black elastic (front centre)
    box(k, "c:black_plastic", 5.8, 4.0, 1.2, NM(z, 2.3, 15.8, 3), bevel=0.05)
    box(k, "s:kraft_band:kraft", 6.4, 4.0, 1.7, NM(z, 2.4, 9.4, -2), bevel=0.05)
    # white box with a rose-gold lid and a black hand mirror at the back left
    box(k, "c:white_plastic", 3.6, 3.6, 2.8, NM(z, 10.2, 4.8, 8), bevel=0.05)
    box(k, "c:rose_gold", 3.3, 3.3, 0.06, NM(z, 10.2, 4.8, 8) @ Matrix.Translation((0, 0, 2.8)), bevel=0.0)
    Mm = NM(z, 12.0, 2.2, 0, (-12, 0))
    cyl(k, "c:black_plastic", 2.0, 0.35, Mm @ Matrix.Translation((0, 0, 3.4)), seg=14, axis="Y")
    box(k, "c:black_plastic", 0.7, 0.35, 2.4, Mm, bevel=0.1)
    # grey pouch, teal scarf, navy and white scrunchies, small boxes (front left)
    box(k, "c:grey", 4.6, 3.4, 1.0, NM(z, 6.6, 3.4, 12), bevel=0.45)
    blob(k, "b:scarf", 1.8, 2.0, 0.8, NM(z, 3.0, 2.6, 30), seed=51, amp=0.2, freq=3.0)
    blob(k, "c:navy_soft", 1.0, 1.0, 0.6, NM(z, 1.2, 1.4), seed=52, amp=0.2, freq=4.0, sub=1)
    box(k, "c:light_blue", 2.0, 2.0, 1.5, NM(z, 1.6, 5.0, 10), bevel=0.05)
    box(k, "c:black_plastic", 2.5, 2.0, 1.5, NM(z, 6.2, 4.4, -5) @ Matrix.Translation((0, 0, 1.0)), bevel=0.05)


def shelf4(k):
    z = SHELF_TOPS[3]
    # two upright pest-control boxes at the front of the north end
    box(k, "b:insect_box", 2.8, 3.8, 7.4, NM(z, 2.2, 1.7, -4), bevel=0.04)
    box(k, "b:ant_box", 2.1, 3.6, 7.0, NM(z, 2.1, 4.2, 3, (0, 6)), bevel=0.04)
    # two flat white boxes in front of the tote bag
    box(k, "b:med_orange", 5.8, 2.6, 1.1, NM(z, 1.5, 8.0, 2), bevel=0.04)
    box(k, "b:med_white", 5.4, 2.4, 1.0, NM(z, 2.1, 8.0, -8) @ Matrix.Translation((0, 0, 1.1)), bevel=0.04)
    # white tote bag leaning toward the north end
    box(k, "s:tote:paper", 8.0, 3.0, 15.0, NM(z, 7.9, 7.6, 5, (0, -10)), bevel=0.6)
    blob(k, "c:clear_white", 2.4, 1.4, 0.8, NM(z, 4.3, 8.4, 20), seed=64, amp=0.2, freq=2.5, sub=1)
    # clear bin with a white lid (blue gloves inside), the massage gun lying on the lid,
    # a round black attachment standing behind it
    Mb = NM(z, 3.6, 14.4)
    box(k, "z:gloves", 7.6, 5.2, 4.0, Mb @ Matrix.Translation((0, 0, 0.1)), bevel=0.3)
    box(k, "c:clear_white", 8.4, 6.0, 4.6, Mb, bevel=0.4, clear=True)
    box(k, "c:white_plastic", 8.8, 6.4, 0.5, Mb @ Matrix.Translation((0, 0, 4.6)), bevel=0.15)
    Mg = NM(z, 3.0, 14.2)
    cyl(k, "c:black_plastic", 1.3, 7.0, Mg @ Matrix.Translation((0, 0, 6.4)), seg=12, axis="X")
    cyl(k, "c:grey", 1.2, 0.2, Mg @ Matrix.Translation((-3.55, 0, 6.4)), seg=12, axis="X")
    cyl(k, "c:charcoal", 2.7, 1.6, NM(z, 6.0, 14.5, 0, (-6, 0)) @ Matrix.Translation((0, 0, 7.8)), seg=14, axis="Y")
    # black mesh bag in the back south corner, bagged white filter behind the bin
    blob(k, "b:mesh_black", 1.6, 2.6, 5.0, NM(z, 9.5, 18.4, 10), seed=62, amp=0.1, freq=2.0)
    blob(k, "c:paper", 2.6, 2.2, 3.2, NM(z, 10.5, 15.0), seed=63, amp=0.15, freq=2.5)
    # two small white bottles, front right beside the bin
    for a, b in ((1.2, 19.3), (2.8, 19.3)):
        cyl(k, "c:white_plastic", 0.75, 3.0, NM(z, a, b), seg=10)
        cyl(k, "c:white_plastic", 0.5, 0.6, NM(z, a, b), seg=10, z0=3.0)


# --- package ---------------------------------------------------------------------------

PIECES = [
    ("shower_caddy", caddy),
    ("tub_rim_bottle", rim_bottle),
    ("bath_towels", lambda k: [towel(k, *t) for t in TOWELS]),
    ("niche_floor", niche_floor),
    ("niche_shelf_1", shelf1),
    ("niche_shelf_2", shelf2),
    ("niche_shelf_3", shelf3),
    ("niche_shelf_4", shelf4),
]


def build(coll):
    objs = []
    for name, fn in PIECES:
        k = K()
        fn(k)
        objs.append(k.to_object(name, coll))
    return objs


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = MATERIALS[NAME + "_clear"]["alpha"]
    try:
        clear.surface_render_method = "BLENDED"
    except AttributeError:
        pass
    for ob in objs:
        uses_clear = any(p.material_index == 1 for p in ob.data.polygons)
        common.collapse_materials(ob, {"opaque": mat, "clear": clear if uses_clear else mat})
