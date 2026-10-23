"""Everything on the shelves of the kitchen upper cabinets (photos
Reference/cupboards_drawers/PXL_20261023_*.jpg, sorted index 0-6), one static object per
cabinet:

  kitchen_upper_contents_wu1  photo 0  west run, south cabinet: food-storage containers
                              (clear with red lids, a teal clip-lid box), a big white
                              serving bowl, side plates, dinner plates, a stack of bowls
  kitchen_upper_contents_wu2  photo 1  over the sink: a row of blue beer cans, protein-shake
                              bottles, an orange gift box, foil / wrap / red boxes
  kitchen_upper_contents_wu3  photo 2  pantry: a cookie jar, a snack bag and a pasta box;
                              a row of soup / vegetable / pasta cans and a purple bag; mac &
                              cheese boxes, a cup-mac box, small tins; stacked sausage cans,
                              a green bag, gelatin boxes, papers
  kitchen_upper_contents_cu   photo 3  45-degree corner cabinet: cup noodles, a noodle bowl,
                              a white tub; a clear lidded tub, a bag of rice noodles; spices,
                              pasta sauce, a pepper grinder, a yellow bag; kosher salt, flour,
                              a powder tub, cans, a waffle box
  kitchen_upper_contents_nu1  photo 4  north run, EAST bay only (the west bay has no photo
                              and is left empty): stacked clear containers, a white platter;
                              the pink dish-rack tub and tray, glass prep bowls; a yellow
                              coffee canister, a blue baking dish, a small jar; round clear
                              containers and two red lids
  kitchen_upper_contents_nu2  photo 5  over the microwave: corn starch, bouillon tub, olive
                              oil, a yellow oil jug, a baking-powder can, cooking spray,
                              balsamic vinegar, a syrup bottle, a cereal box
  kitchen_upper_contents_nu3  photo 6  plastic cutlery bags and small lids; a travel mug,
                              an ice tray, a coffee press with a water bottle on it, tea and
                              cocoa boxes, straws; blue tumblers, a tea ball, tea boxes, a
                              funnel; mugs, a drink-mix box

Source of truth: scripted. FRAME: PLAN COORDINATES (x east, y north, z up; inches -> metres,
origin plan (0, 0, 0)); every object is placed at (0, 0, 0) with no rotation, like
kitchen_cabinets. Shelf heights and interior extents come from
blender/lib/objects/kitchen_cabinets/interior.py (re-read at build time); items are laid
out per cabinet in a viewer frame: u = inches from the interior's left side as seen from
the room, w = inches back from the face frame's back plane, z on the shelf top. A check at
build time asserts every vertex lies inside its cabinet interior (behind the face frame,
under the next shelf).

Dimensions (inches): every item size is PHOTO, proportioned against known sizes in the
same photo (12 oz can 4.83 x 2.6, 8 oz shake bottle 6.3 x 2.4, dinner plate 10.5, the
cabinet interiors from interior.py) or EST (standard product size: 28 oz can 4.75 x 4.1,
18.8 oz can 4.9 x 3.4, 2 L oil bottle 11.5 tall, mugs 3.5 x 4). Hidden back rows are EST.

No brands: every package is flat colour blocks in its real colour scheme (kuc_layout.py),
no text, logos, faces or barcodes.
"""

import importlib
import math
import os
import random
import sys

import bmesh
from mathutils import Matrix, Vector

import atlas_layout
import common

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import kuc_layout  # noqa: E402

importlib.reload(kuc_layout)

IN = 0.0254


def m(v):
    return v * IN


NAME = kuc_layout.NAME
ATLAS = kuc_layout.ATLAS
MATERIALS = {
    NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
    NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": 0.35, "tiled": False},
}
COLLIDER = "none"
STATIC = True
# (name, azimuth, elevation, distance scale) around the whole set; az 0 = from the south
VIEWS = [("from_se_low", 35, -12, 0.8), ("from_s_low", 10, -15, 0.8)]
SLOTS = ["opaque", "clear"]

CAB_DIR = os.path.join(os.path.dirname(HERE), "kitchen_cabinets")


def _interior():
    if CAB_DIR not in sys.path:
        sys.path.insert(0, CAB_DIR)
    import interior
    importlib.reload(interior)
    return interior


# --- builder with direct UVs --------------------------------------------------------------

def pal_uv(name):
    x, y = kuc_layout.pal_px(name)
    return (x / ATLAS["size"], 1.0 - y / ATLAS["size"])


class K:
    """common.Builder plus a UV layer; items are built in local inches, UV-mapped in their
    local frame, then moved into plan metres by a matrix. Tracks the cabinet and level so
    every item is checked against the interior."""

    def __init__(self, cab_id, ii):
        self.b = common.Builder(SLOTS)
        self.bm = self.b.bm
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.cab_id = cab_id
        self.cab = ii.CABINETS[cab_id]
        self.ii = ii
        c = self.cab
        self.levels = [c["z"][0]] + list(c["shelves"])
        self.ceils = [s - ii.SHELF_T for s in c["shelves"]] + [c["z"][1]]
        self.lvl = 0
        self.problems = []
        self.items = 0

    def at(self, lvl):
        self.lvl = lvl
        return self

    @property
    def z(self):
        return self.levels[self.lvl]

    def since(self):
        dv = self.bm.verts.layers.int.get("done") or self.bm.verts.layers.int.new("done")
        df = self.bm.faces.layers.int.get("done") or self.bm.faces.layers.int.new("done")
        vs = [v for v in self.bm.verts if not v[dv]]
        fs = [f for f in self.bm.faces if not f[df]]
        for v in vs:
            v[dv] = 1
        for f in fs:
            f[df] = 1
        return vs, fs

    def finish(self, look, M, clear=False, tag=""):
        vs, fs = self.since()
        self.bm.normal_update()
        apply_look(self, fs, look)
        for f in fs:
            f.material_index = 1 if clear else 0
        bmesh.ops.transform(self.bm, matrix=M, verts=vs)
        zmin, floor = min(v.co.z for v in vs), m(self.z)
        if zmin < floor:                  # tilted items: rest the low corner on the shelf
            for v in vs:
                v.co.z += floor - zmin
        self.check(vs, tag or look)
        self.items += 1
        return fs

    def check(self, vs, tag):
        """Every vertex inside the interior: behind the face frame, inside the side/back
        panels (or the corner polygon), above this level's surface, under the next shelf."""
        c, eps = self.cab, 0.02
        z0, z1 = self.levels[self.lvl] - eps, self.ceils[self.lvl] + eps
        bad = 0
        for v in vs:
            x, y, z = v.co.x / IN, v.co.y / IN, v.co.z / IN
            ok = z0 <= z <= z1
            if c["run"] == "C":
                ok = ok and _in_poly(x, y, c["poly"], eps)
            else:
                ok = ok and c["x"][0] - eps <= x <= c["x"][1] + eps and c["y"][0] - eps <= y <= c["y"][1] + eps
            if self.lvl > 0 and ok:
                # resting on a shelf: stay over the shelf (front edge FRONT_SETBACK back)
                if c["run"] == "W":
                    ok = x <= c["front"] - self.ii.FRONT_SETBACK + eps
                elif c["run"] == "N":
                    ok = y >= c["front"] + self.ii.FRONT_SETBACK - eps
            bad += not ok
        if bad:
            self.problems.append(f"{self.cab_id} L{self.lvl} {tag}: {bad} verts outside")

    def to_object(self, name, coll):
        for layers in (self.bm.verts.layers.int, self.bm.faces.layers.int):
            lay = layers.get("done")
            if lay is not None:
                layers.remove(lay)
        return self.b.to_object(name, coll)


def _in_poly(x, y, poly, eps):
    """Inside a convex counter-clockwise polygon, with tolerance eps."""
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        L = math.hypot(ex, ey)
        if (ex * (y - y0) - ey * (x - x0)) / L < -eps:
            return False
    return True


def apply_look(k, faces, look):
    """look: 'c:<palette>' solid; 'b:<region>' each face shows the whole region;
    'f:<region>:<palette>' faces looking along local Y (front/back) show the region, the
    rest solid; 'w:<region>:<palette>' sides wrap the region around Z, caps solid."""
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
    u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, region)
    pts = [v.co for f in faces for v in f.verts]
    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    ext = Vector([max(hi[i] - lo[i], 1e-6) for i in range(3)])
    cx, cy = (lo.x + hi.x) / 2, (lo.y + hi.y) / 2
    solid = pal_uv(parts[2]) if len(parts) > 2 else None
    for f in faces:
        n = f.normal
        if kind == "w" and abs(n.z) > 0.6 or kind == "f" and abs(n.y) < 0.6:
            for lp in f.loops:
                lp[uv].uv = solid
            continue
        if kind == "w":
            angs = [math.atan2(lp.vert.co.x - cx, -(lp.vert.co.y - cy)) for lp in f.loops]
            if max(angs) - min(angs) > math.pi:
                angs = [math.pi * 0.99] * len(angs)
            for lp, t in zip(f.loops, angs):
                c = lp.vert.co
                fu = min(max(0.5 + t / (2 * math.pi), 0.0), 1.0)
                lp[uv].uv = (u0 + fu * (u1 - u0), v0 + (c.z - lo.z) / ext.z * (v1 - v0))
            continue
        ax = max(range(3), key=lambda i: abs(n[i]))
        ua, va = [(1, 2), (0, 2), (0, 1)][ax]
        if kind == "f":     # whole item extent so the print spans the face
            flo, fhi = lo, hi
        else:
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


# --- placement ------------------------------------------------------------------------------

def P(k, u, w, dz=0.0, rot=0.0, tilt=(0.0, 0.0)):
    """Local inches -> plan metres for an item centred at viewer-frame (u, w), standing on
    the current level (+dz). Local +X = the viewer's right, local -Y = toward the room."""
    c = k.cab
    if c["run"] == "W":
        x, y, base = c["front"] - w, c["y"][0] + u, 90.0
    elif c["run"] == "N":
        x, y, base = c["x"][0] + u, c["front"] + w, 0.0
    else:
        (fx0, fy0), _ = c["front"]
        s = 1 / math.sqrt(2)
        back = k.ii.DOOR_T + k.ii.FRAME_T
        ox, oy = fx0 - back * s, fy0 + back * s
        x, y, base = ox + (u - w) * s, oy + (u + w) * s, 45.0
    z = k.z + dz
    return (Matrix.Translation((m(x), m(y), m(z))) @ Matrix.Rotation(math.radians(base + rot), 4, "Z")
            @ Matrix.Rotation(math.radians(tilt[0]), 4, "X") @ Matrix.Rotation(math.radians(tilt[1]), 4, "Y")
            @ Matrix.Scale(IN, 4))


# --- primitives in local inches (z0 = bottom) -------------------------------------------------

def box(k, look, w, d, h, M, bevel=0.0, z0=0.0, clear=False, tag=""):
    k.b.box("opaque", (-w / 2, -d / 2, z0), (w / 2, d / 2, z0 + h), bevel=bevel, segments=1)
    return k.finish(look, M, clear, tag)


def cyl(k, look, r, h, M, seg=10, z0=0.0, clear=False, tag="", sx=1.0):
    k.b.cylinder("opaque", (0, 0, z0 + h / 2), r, h, axis="Z", segments=seg)
    if sx != 1.0:
        vs, _ = _pending(k)
        for v in vs:
            v.co.x *= sx
    return k.finish(look, M, clear, tag)


def _pending(k):
    dv = k.bm.verts.layers.int.get("done") or k.bm.verts.layers.int.new("done")
    df = k.bm.faces.layers.int.get("done") or k.bm.faces.layers.int.new("done")
    return [v for v in k.bm.verts if not v[dv]], [f for f in k.bm.faces if not f[df]]


def lathe(k, look, prof, M, seg=10, clear=False, tag="", sx=1.0, sy=1.0):
    """Surface of revolution from a profile [(r, z)]; r = 0 at either end makes a pole,
    otherwise the end is capped. Closed, so normals come out right."""
    bm = k.bm
    rings = []
    for r, z in prof:
        if r <= 1e-6:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * sx * math.cos(2 * math.pi * i / seg),
                                        r * sy * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    faces = []
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                faces.append(bm.faces.new((a[0], b[j], b[i])))
            elif len(b) == 1:
                faces.append(bm.faces.new((a[i], a[j], b[0])))
            else:
                faces.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    if len(rings[0]) > 1:
        faces.append(bm.faces.new(list(reversed(rings[0]))))
    if len(rings[-1]) > 1:
        faces.append(bm.faces.new(rings[-1]))
    k.b._tag(faces, "opaque")
    return k.finish(look, M, clear, tag)


def bowl(k, look, rt, rb, h, M, t=0.18, seg=10, clear=False, sx=1.0):
    """Open bowl with a wall thickness (a closed lathe)."""
    prof = [(0, 0), (rb, 0), (rb + (rt - rb) * 0.35, h * 0.3), (rt, h), (rt - t, h),
            (rb + (rt - rb) * 0.35 - t, h * 0.3 + t * 0.5), (rb - t, t), (0, t)]
    return lathe(k, look, prof, M, seg=seg, clear=clear, tag="bowl", sx=sx)


def plate(k, look, r, h, M, seg=12):
    prof = [(0, 0), (r * 0.62, 0), (r * 0.66, h * 0.35), (r * 0.72, h * 0.35), (r, h), (r - 0.25, h),
            (r * 0.7, h * 0.55), (0, h * 0.55)]
    return lathe(k, look, prof, M, seg=seg, tag="plate")


def bottle(k, label, r, body, neck_r, total, M, cap="cap_blue", cap_h=0.9, body_col="white",
           seg=8, shoulder=None, clear=False):
    """Body cylinder carrying the label, a shoulder/neck lathe, a cap."""
    cyl(k, f"w:{label}:{body_col}", r, body, M, seg=seg, clear=clear, tag=label)
    sh = shoulder if shoulder is not None else (total - cap_h - body) * 0.6
    neck_top = total - cap_h
    lathe(k, f"c:{body_col}", [(0, body), (r, body), (r * 0.8, body + sh * 0.6),
                                (neck_r, body + sh), (neck_r, neck_top), (0, neck_top)], M, seg=seg,
          clear=clear, tag=label + " neck")
    cyl(k, f"c:{cap}", neck_r * 1.1, cap_h, M, seg=seg, z0=neck_top, tag=label + " cap")


def can(k, label, r, h, M, seg=10):
    cyl(k, f"w:{label}:silver", r, h, M, seg=seg, tag=label)


def mug(k, col, r, h, M, inv=False, handle=1.0, seg=12):
    """Mug with a wall and a handle on the local +X side (handle=-1: -X). inv = upside
    down (mouth on the shelf)."""
    t = 0.2
    if inv:
        prof = [(0, h), (r * 0.94, h), (r, h * 0.8), (r, 0), (r - t, 0), (r - t, h - t), (0, h - t)]
    else:
        prof = [(0, 0), (r * 0.94, 0), (r, h * 0.2), (r, h), (r - t, h), (r - t, t), (0, t)]
    lathe(k, f"c:{col}", prof, M, seg=seg, tag="mug")
    s = handle
    zc = h * 0.5
    pts = [(s * (r - 0.1), 0, zc + h * 0.3), (s * (r + 0.9), 0, zc + h * 0.28),
           (s * (r + 1.1), 0, zc), (s * (r + 0.9), 0, zc - h * 0.28), (s * (r - 0.1), 0, zc - h * 0.3)]
    k.b.sweep("opaque", [Vector(p) for p in pts], common.rect_profile(0.45, 0.3), up=(0, 1, 0))
    k.finish(f"c:{col}", M, tag="mug handle")


def _noise(p, seed, amp, freq):
    rnd = random.Random(seed)
    s = 0.0
    for _ in range(4):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized()
        s += math.sin(d.dot(p) * freq * rnd.uniform(0.7, 1.4) + rnd.uniform(0, 6.3))
    return amp * s / 2.0


def blob(k, look, rx, ry, rz, M, seed=1, amp=0.15, freq=2.0, sub=2, clear=False):
    """Lumpy ellipsoid (a bag) resting on local z = 0."""
    res = bmesh.ops.create_icosphere(k.bm, subdivisions=sub, radius=1.0)
    for v in res["verts"]:
        d = v.co.normalized()
        s = 1.0 + _noise(d * 3.0, seed, amp, freq)
        v.co = Vector((d.x * rx * s, d.y * ry * s, d.z * rz + rz))
        if v.co.z < 0.04 * rz:
            v.co.z = max(v.co.z, 0.0) * 0.1
    k.b._tag([f for v in res["verts"] for f in v.link_faces], "opaque")
    return k.finish(look, M, clear, tag="blob")


def container(k, w, d, h, M, lid="clear", lid_h=0.4, body_clear=True):
    """Food-storage box: a clear tub and a lid."""
    box(k, "c:clear", w, d, h - lid_h, M, bevel=0.35, clear=body_clear, tag="tub")
    box(k, f"c:{lid}", w + 0.2, d + 0.2, lid_h, M, bevel=0.12, z0=h - lid_h, clear=(lid == "clear"), tag="lid")


def round_container(k, rt, rb, h, M, lid="clear"):
    lathe(k, "c:clear", [(0, 0), (rb, 0), (rt, h - 0.35), (0, h - 0.35)], M, seg=12, clear=True, tag="round tub")
    cyl(k, f"c:{lid}", rt + 0.12, 0.35, M, seg=12, z0=h - 0.35, clear=(lid == "clear"), tag="round lid")


# --- cabinets -------------------------------------------------------------------------------

def wu1(k):
    """Photo 0. Bays split by the face-frame mullion at u ~12 (the shelves run through)."""
    k.at(0)
    for i in range(2):                                    # dinner plates (left)
        plate(k, "c:ceramic", 5.25, 0.95, P(k, 6.3, 5.6, i * 0.55))
    for i in range(4):                                    # bowl stack (right)
        bowl(k, "c:ceramic", 3.1, 1.8, 2.6, P(k, 17.5, 6.2, i * 0.62))
    k.at(1)
    for i in range(2):                                    # big serving bowls (left)
        bowl(k, "c:ceramic", 4.6, 2.6, 3.1, P(k, 6.8, 5.8, i * 0.45))
    for i in range(4):                                    # side plates (right)
        plate(k, "c:ceramic", 3.9, 0.55, P(k, 17.6, 6.2, i * 0.32))
    k.at(2)
    container(k, 8.0, 6.0, 3.0, P(k, 5.0, 5.0), lid="red_lid")          # clear, red lid
    container(k, 7.4, 5.6, 3.2, P(k, 4.8, 5.2, 3.05, rot=4))              # clear on top
    container(k, 6.6, 6.4, 1.9, P(k, 10.4, 6.6, rot=-3), lid="red_lid")  # shallow, red lid
    box(k, "c:red_lid", 6.8, 6.6, 0.3, P(k, 10.6, 6.4, 1.95, rot=6, tilt=(0, -4)), bevel=0.1)
    container(k, 4.4, 4.4, 1.9, P(k, 13.4, 3.4))                         # small clear (by the mullion)
    box(k, "c:teal", 6.0, 6.0, 2.9, P(k, 17.6, 5.6), bevel=0.4)          # teal clip-lid box
    box(k, "c:teal_dark", 6.3, 6.3, 0.6, P(k, 17.6, 5.6), z0=2.9, bevel=0.15)
    for ox, oy, rr in ((0.0, -3.22, 0), (0.0, 3.22, 0), (-3.22, 0.0, 90), (3.22, 0.0, 90)):
        Mc = P(k, 17.6, 5.6) @ Matrix.Translation((ox, oy, 0)) @ Matrix.Rotation(math.radians(rr), 4, "Z")
        box(k, "c:teal_dark", 1.6, 0.22, 1.4, Mc, z0=2.2, bevel=0.0, tag="clip")


def wu2(k):
    """Photo 1. Over the sink; mullion at u ~15.5."""
    k.at(1)
    for u in (3.0, 5.7, 8.4, 11.1, 13.8):                 # beer cans, front row
        can(k, "beer", 1.3, 4.83, P(k, u, 1.9))
    for u in (4.3, 7.0, 9.7, 12.4):                       # second row
        can(k, "beer", 1.3, 4.83, P(k, u, 4.7))
    box(k, "f:gift_orange:orange", 4.4, 3.4, 9.6, P(k, 17.8, 3.0, rot=-6))
    for u, w in ((20.8, 2.0), (23.6, 2.1), (22.2, 4.8), (25.0, 4.9)):   # shake bottles
        bottle(k, "shake", 1.2, 4.6, 0.75, 6.3, P(k, u, w), cap="cap_blue", cap_h=0.85)
    k.at(0)
    box(k, "f:foil:blue", 12.6, 2.6, 2.6, P(k, 8.2, 2.0))
    box(k, "f:wrap:lavender", 12.2, 2.4, 2.4, P(k, 8.6, 2.2, 2.6, rot=1))
    box(k, "f:red_box:red", 7.6, 3.2, 1.7, P(k, 11.0, 2.6, 5.0, rot=-2))
    for u in (4.2, 6.9, 9.6, 12.3):                       # shakes behind the boxes
        bottle(k, "shake", 1.2, 4.6, 0.75, 6.3, P(k, u, 6.4), cap="cap_blue", cap_h=0.85)
    box(k, "f:foil:blue", 11.6, 2.3, 2.3, P(k, 21.6, 2.0, rot=-1))
    for u in (18.2, 20.8):                                # two shakes standing on the foil box
        bottle(k, "shake", 1.1, 4.6, 0.7, 6.3, P(k, u, 2.0, 2.3), cap="cap_blue", cap_h=0.85)
    for u, w in ((24.6, 2.0), (26.9, 2.1), (29.2, 2.0), (25.7, 4.5), (28.0, 4.6)):  # the six-pack (one hidden)
        bottle(k, "shake", 1.2, 4.6, 0.75, 6.3, P(k, u, w), cap="cap_blue", cap_h=0.85)
    bottle(k, "shake", 1.2, 4.6, 0.75, 6.3, P(k, 29.4, 4.7), cap="cap_blue", cap_h=0.85)


def wu3(k):
    """Photo 2. Pantry, one door, 17 in wide."""
    k.at(0)
    box(k, "f:bars:brown", 2.6, 5.0, 2.2, P(k, 1.6, 3.0, rot=4), tag="bars")
    box(k, "c:paper", 3.4, 4.0, 1.6, P(k, 2.0, 3.2, 2.2, rot=-8, tilt=(0, 6)), tag="white packs")
    blob(k, "c:green_bag", 2.6, 2.6, 3.8, P(k, 5.6, 3.6, rot=10), seed=4, amp=0.38, freq=3.0)
    for i in range(3):                                    # sausage cans, front stack
        can(k, "vienna", 1.25, 2.1, P(k, 8.8, 1.8, i * 2.12))
    for i in range(2):
        can(k, "vienna", 1.25, 2.1, P(k, 9.2, 4.6, i * 2.12))
    can(k, "vienna", 1.25, 2.1, P(k, 11.2, 2.6))
    box(k, "f:jello:pink", 3.6, 2.4, 1.3, P(k, 11.6, 5.8, rot=-5))
    box(k, "f:jello:pink", 3.6, 2.4, 1.3, P(k, 14.4, 4.4, 1.0, rot=3), tag="jello 2")
    box(k, "c:kraft", 5.2, 5.6, 1.0, P(k, 14.3, 4.6, rot=2), tag="flat box")
    box(k, "c:paper", 5.0, 7.0, 0.25, P(k, 13.8, 4.2, 2.35, rot=-4, tilt=(-6, 0)), bevel=0.0, tag="papers")
    k.at(1)
    box(k, "f:yellow_box:yellow", 2.3, 5.6, 7.6, P(k, 1.5, 4.0))
    box(k, "b:snack_red", 3.0, 1.0, 8.4, P(k, 3.6, 3.6, rot=-10, tilt=(-8, 14)), tag="leaning bag")
    cyl(k, "w:fishtin:silver", 1.5, 1.6, P(k, 4.8, 2.1), tag="fish tin")
    box(k, "f:mac_big:blue", 4.6, 2.4, 7.8, P(k, 6.4, 5.2))
    box(k, "c:black", 8.6, 7.4, 0.25, P(k, 6.8, 5.6, 7.85, rot=-4, tilt=(0, -2)), bevel=0.0, tag="black board")
    cyl(k, "w:chowder:silver", 1.5, 3.6, P(k, 7.4, 2.1), tag="blue can")
    for i in range(4):                                    # small mac boxes, lying flat
        box(k, "f:mac_small:blue", 3.3, 7.0, 1.55, P(k, 10.0 + (i % 2) * 0.15, 4.2, i * 1.57, rot=(i % 2) * 2 - 1))
    box(k, "b:candy_yellow", 2.6, 0.8, 3.2, P(k, 12.2, 1.4, rot=8, tilt=(-10, 0)), tag="candy bag")
    box(k, "f:easymac:blue", 4.6, 3.6, 6.2, P(k, 14.3, 3.4, rot=-8))
    k.at(2)
    can(k, "tomato", 2.05, 4.75, P(k, 2.15, 2.6))
    can(k, "chunky", 1.7, 4.9, P(k, 5.6, 2.3))
    can(k, "beans", 1.55, 4.4, P(k, 8.6, 3.4))
    can(k, "ravioli", 1.7, 4.6, P(k, 11.0, 2.3))
    can(k, "chowder", 1.6, 3.6, P(k, 13.6, 2.1))
    blob(k, "c:purple", 2.0, 2.4, 4.0, P(k, 14.3, 6.2, rot=-20), seed=7, amp=0.22)
    can(k, "tomato", 2.05, 4.75, P(k, 3.0, 7.4))           # back row (EST)
    can(k, "chunky", 1.7, 4.9, P(k, 7.0, 6.8))
    k.at(3)
    box(k, "f:pasta_box:sky_blue", 3.4, 6.4, 4.6, P(k, 2.0, 4.6))
    box(k, "b:snack_red", 3.6, 1.6, 6.6, P(k, 6.6, 3.4, rot=-4, tilt=(-6, 0)), tag="snack bag")
    # cookie jar: clear barrel, red lid, crackers inside, a red round label
    jar = P(k, 11.2, 5.0)
    lathe(k, "c:clear", [(0, 0), (2.6, 0), (3.3, 1.2), (3.4, 3.6), (3.0, 6.2), (2.3, 7.1), (0, 7.1)], jar,
          seg=12, clear=True, tag="cookie jar")
    blob(k, "c:cookie", 2.7, 2.7, 1.3, jar, seed=3, amp=0.25)
    cyl(k, "c:red", 2.45, 1.1, jar, seg=12, z0=7.1, tag="jar lid")
    Ml = jar @ Matrix.Translation((0, -3.36, 3.0)) @ Matrix.Rotation(math.radians(90), 4, "X")
    cyl(k, "c:red", 1.5, 0.08, Ml, seg=12, tag="jar label")


def cu(k):
    """Photo 3. 45-degree corner cabinet; u along the door face, w straight in. The
    interior widens behind the face frame (pentagon in interior.py)."""
    k.at(0)
    box(k, "c:black", 3.2, 5.2, 2.0, P(k, -0.6, 4.2, rot=10), tag="dark packets")
    box(k, "f:bars:brown", 3.0, 5.0, 1.6, P(k, -0.4, 4.0, 2.0, rot=4), tag="packets 2")
    box(k, "f:flour:white", 5.8, 3.8, 8.6, P(k, 5.2, 6.4, rot=-6), bevel=0.4)
    box(k, "f:kosher:blue", 5.4, 3.2, 7.8, P(k, 2.8, 2.2, rot=-4))
    box(k, "f:maroon_box:maroon", 1.8, 3.0, 5.4, P(k, 6.4, 2.4))
    cyl(k, "w:plain_label:powder", 2.0, 6.0, P(k, 8.7, 2.6), seg=12, tag="powder tub")
    cyl(k, "c:grey", 1.6, 1.0, P(k, 8.7, 2.6), seg=12, z0=6.0, tag="tub cap")
    cyl(k, "w:plain_label:white", 1.5, 4.6, P(k, 11.0, 2.0), seg=10, tag="canister")
    can(k, "progresso", 1.65, 3.8, P(k, 12.0, 4.6))
    can(k, "vienna", 1.25, 2.1, P(k, 12.0, 4.6, 3.8))
    box(k, "f:waffle:red", 2.4, 6.0, 8.2, P(k, 12.8, 4.2, rot=2), tag="waffle box")
    can(k, "chowder", 1.6, 3.6, P(k, 9.0, 8.0))            # back (EST)
    box(k, "c:paper", 5.0, 3.0, 0.15, P(k, 9.6, 2.0, rot=8), bevel=0.0, tag="paper")
    k.at(1)
    box(k, "c:blue", 4.6, 2.8, 1.2, P(k, -0.2, 3.2, rot=12), tag="blue packet")
    for u, w, h in ((1.0, 6.6, 3.6), (2.6, 7.2, 4.2), (4.3, 7.0, 3.4)):   # spices behind
        cyl(k, "c:herb", 0.95, h, P(k, u, w), seg=8, tag="spice")
        cyl(k, "c:white", 1.0, 0.7, P(k, u, w), seg=8, z0=h, tag="spice cap")
    cyl(k, "c:herb", 1.0, 3.6, P(k, 3.4, 3.2), seg=8, tag="spice front")
    cyl(k, "c:red", 1.05, 0.9, P(k, 3.4, 3.2), seg=8, z0=3.6, tag="spice cap")
    cyl(k, "w:evapmilk:silver", 1.5, 3.0, P(k, 5.6, 6.4), tag="milk can")
    blob(k, "c:yellow", 3.8, 1.8, 0.95, P(k, 6.2, 3.0, rot=-6), seed=11, amp=0.1)
    box(k, "c:clear", 3.6, 0.3, 5.6, P(k, 7.4, 4.8, 1.0, rot=-30, tilt=(-25, 0)), bevel=0.0, clear=True,
        tag="clear packet")
    jarM = P(k, 9.6, 3.0)                                  # pasta sauce jar
    cyl(k, "w:sauce:sauce", 1.6, 6.4, jarM, seg=10, tag="sauce jar")
    lathe(k, "c:sauce", [(0, 6.4), (1.6, 6.4), (1.3, 7.0), (0, 7.0)], jarM, tag="jar shoulder")
    cyl(k, "c:gold", 1.35, 0.5, jarM, z0=7.0, tag="jar lid")
    cyl(k, "w:pepper:black", 1.0, 3.6, P(k, 11.5, 2.4), seg=8, tag="pepper")
    cyl(k, "c:black", 0.85, 1.1, P(k, 11.5, 2.4), seg=8, z0=3.6, tag="grinder")
    box(k, "f:tea_red2:red", 2.6, 2.4, 4.4, P(k, 13.0, 3.6, rot=-5), tag="red box")
    box(k, "c:paper", 3.0, 3.0, 5.6, P(k, 14.2, 7.6), tag="white box")
    k.at(2)
    box(k, "f:bars:black", 2.4, 5.6, 5.0, P(k, -1.6, 7.0, rot=8), tag="dark package")
    blob(k, "c:clear", 3.2, 3.0, 2.6, P(k, 2.6, 4.6), seed=5, amp=0.25, clear=True)
    blob(k, "c:noodle", 2.6, 2.3, 1.6, P(k, 2.7, 4.6), seed=6, amp=0.2)
    tubM = P(k, 10.3, 8.0)
    box(k, "c:clear", 11.0, 8.4, 7.4, tubM, bevel=0.5, clear=True, tag="clear tub")
    box(k, "c:clear", 11.4, 8.8, 0.6, tubM, z0=7.4, bevel=0.2, clear=True, tag="tub lid")
    box(k, "c:black", 11.4, 8.6, 0.35, tubM, z0=8.05, bevel=0.1, tag="black tray")
    k.at(3)
    cupM = P(k, 8.0, 8.2)
    lathe(k, "w:cupnoodle:white", [(0, 0), (1.45, 0), (1.85, 4.3), (0, 4.3)], cupM, seg=12, tag="cup noodle")
    cyl(k, "w:plain_label:white", 2.5, 4.0, P(k, 9.8, 12.2), seg=12, tag="white tub")
    lathe(k, "w:bowlnoodle:red", [(0, 0), (2.0, 0), (2.9, 3.2), (0, 3.2)], P(k, 12.6, 8.4), seg=12, tag="noodle bowl")


def nu1(k):
    """Photo 4. East bay (x 36-49) only: u from the partition."""
    pw = k.ii.CABINETS["nu1"]["partitions"][0][1]
    u0 = pw - k.cab["x"][0]

    def Q(u, w, dz=0.0, **kw):
        return P(k, u0 + u, w, dz, **kw)
    k.at(0)
    for i in range(2):
        round_container(k, 2.8, 2.5, 2.3, Q(7.6, 6.0, i * 2.3))
    round_container(k, 2.8, 2.5, 2.3, Q(9.6, 7.9))
    box(k, "c:red_lid", 5.0, 5.0, 0.5, Q(5.4, 3.0, rot=6), bevel=0.2, tag="red lid")
    box(k, "c:red_lid", 5.0, 5.0, 0.5, Q(9.9, 3.1, rot=-8), bevel=0.2, tag="red lid 2")
    k.at(1)
    can(k, "coffee_can", 2.9, 6.5, Q(3.2, 6.8), seg=12)
    box(k, "c:clear", 5.0, 5.0, 0.25, Q(3.0, 3.2), bevel=0.1, clear=True, tag="clear lid")
    bowl(k, "c:glass", 2.3, 1.6, 1.8, Q(2.8, 3.2, 0.25), clear=True)
    box(k, "c:blue_dish", 7.0, 5.4, 2.6, Q(7.4, 4.2), bevel=0.4, tag="blue dish")
    cyl(k, "c:clear", 1.25, 3.0, Q(11.2, 2.8), seg=10, clear=True, tag="small jar")
    cyl(k, "c:mint", 1.35, 0.8, Q(11.2, 2.8), seg=10, z0=3.0, tag="jar lid")
    k.at(2)
    cyl(k, "c:clear", 2.6, 0.25, Q(2.9, 3.2), seg=12, clear=True, tag="flat lid")
    box(k, "c:pink", 9.4, 7.4, 1.4, Q(5.4, 4.6, 0.25), bevel=0.3, tag="drip tray")
    box(k, "c:pink", 8.0, 6.4, 3.8, Q(5.0, 4.6, 1.65, rot=-4), bevel=0.4, tag="rack tub")
    box(k, "c:pink", 6.2, 0.9, 5.4, Q(4.6, 5.6, 2.45, rot=-4, tilt=(-10, 0)), bevel=0.15, tag="grid rack")
    box(k, "c:clear", 6.2, 5.2, 5.2, Q(9.3, 7.8, rot=10), bevel=0.4, clear=True, tag="clear box")
    box(k, "c:red_lid", 5.0, 4.4, 1.6, Q(9.3, 7.8, 0.3, rot=12), bevel=0.2, tag="red lids inside")
    for i in range(4):
        bowl(k, "c:glass", 2.2, 1.5, 1.8, Q(10.6, 3.0, i * 0.5), clear=True)
    k.at(3)
    box(k, "c:red_lid", 4.6, 4.6, 0.4, Q(2.6, 4.6), bevel=0.15, tag="red base")
    for i in range(3):
        container(k, 4.3, 4.3, 1.8, Q(2.6, 4.6, 0.4 + i * 1.75))
    bowl(k, "c:ceramic", 3.0, 2.2, 1.5, Q(8.4, 4.6), sx=1.35)
    box(k, "c:white", 5.0, 3.6, 2.4, Q(7.4, 8.6), bevel=0.3, tag="white box")


def nu2(k):
    """Photo 5. Over the microwave; mullion at u ~14.5."""
    k.at(0)
    box(k, "f:cornstarch:white", 5.4, 2.6, 7.6, P(k, 3.2, 1.9, rot=8))
    cyl(k, "c:white", 1.2, 7.4, P(k, 4.2, 5.0), tag="shaker")
    cyl(k, "c:red", 1.25, 1.2, P(k, 4.2, 5.0), z0=7.4, tag="shaker cap")
    cyl(k, "w:bouillon:cream", 2.2, 6.2, P(k, 7.8, 3.0), seg=12, tag="bouillon")
    cyl(k, "c:red", 2.25, 0.6, P(k, 7.8, 3.0), seg=12, z0=6.2, tag="bouillon lid")
    bottle(k, "oil", 2.1, 7.6, 0.7, 11.5, P(k, 11.4, 3.2), cap="green_bag", cap_h=1.0, body_col="olive_glass")
    bottle(k, "oil_jug", 2.2, 7.4, 0.8, 11.0, P(k, 12.2, 7.6), cap="cap_blue", cap_h=1.0, body_col="oil_yellow")
    cyl(k, "w:bakingpowder:yellow", 2.0, 4.6, P(k, 17.2, 2.6), seg=12, tag="powder can")
    cyl(k, "c:cap_blue", 2.05, 0.5, P(k, 17.2, 2.6), seg=12, z0=4.6, tag="powder lid")
    cyl(k, "w:spray:white", 1.05, 7.4, P(k, 20.0, 2.8), tag="spray")
    cyl(k, "c:cap_blue", 1.05, 1.9, P(k, 20.0, 2.8), z0=7.4, tag="spray cap")
    bottle(k, "vinegar", 1.25, 6.2, 0.5, 9.4, P(k, 22.6, 2.6), cap="gold", cap_h=0.8, body_col="dark_glass")
    box(k, "f:cereal:red", 7.4, 2.6, 10.4, P(k, 23.6, 7.6, rot=-4))
    bottle(k, "syrup", 1.5, 7.0, 0.55, 11.0, P(k, 26.4, 3.2), cap="cap_blue", cap_h=0.9, body_col="milky")
    cyl(k, "c:orange", 1.0, 3.8, P(k, 14.8, 3.8), tag="small bottle")


def nu3(k):
    """Photo 6. One door, 17.5 in wide."""
    k.at(0)
    box(k, "f:drinkmix:sky_blue", 4.4, 2.6, 6.5, P(k, 3.0, 2.2, rot=6, tilt=(-6, 0)))
    can(k, "tin_cream", 1.8, 5.0, P(k, 2.4, 6.6))
    box(k, "c:black", 5.0, 1.5, 0.3, P(k, 2.6, 1.5, rot=-10), bevel=0.0, tag="packets")
    mug(k, "navy", 1.75, 4.2, P(k, 7.4, 3.0, rot=200))
    mug(k, "ceramic", 1.7, 4.4, P(k, 7.3, 3.0, 4.2, rot=30), inv=True)
    mug(k, "ceramic", 1.7, 3.6, P(k, 10.2, 2.4, rot=-30))
    mug(k, "ceramic", 1.8, 3.6, P(k, 10.5, 2.6, 3.6, rot=20))
    mug(k, "ceramic", 1.7, 3.8, P(k, 13.2, 3.0, rot=-20))
    cyl(k, "c:white", 2.2, 8.8, P(k, 10.4, 8.2), seg=12, tag="white roll")
    mug(k, "black", 1.7, 4.0, P(k, 6.6, 7.8, rot=150))
    box(k, "f:plain_label:white", 2.8, 2.2, 6.0, P(k, 15.6, 2.6))
    k.at(1)
    cyl(k, "c:sky_blue", 1.5, 6.4, P(k, 1.9, 7.2), seg=10, tag="tumbler")
    Mt = P(k, 4.6, 4.4, 1.65, rot=-60) @ Matrix.Rotation(math.radians(90), 4, "X")
    cyl(k, "c:sky_blue", 1.6, 7.0, Mt @ Matrix.Translation((0, 0, -3.5)), seg=10, tag="lying tumbler")
    cyl(k, "c:dark_grey", 1.2, 0.6, Mt @ Matrix.Translation((0, 0, 3.5)), seg=10, tag="tumbler lid")
    lathe(k, "c:mesh", [(0, 0), (0.7, 0.3), (1.0, 1.0), (0.7, 1.7), (0, 2.0)], P(k, 1.6, 1.8), seg=8, tag="tea ball")
    cyl(k, "c:black", 1.5, 3.0, P(k, 6.8, 2.2), seg=10, tag="coaster holder")
    cyl(k, "c:white", 1.3, 0.2, P(k, 6.8, 2.2), seg=10, z0=3.0, tag="coaster")
    box(k, "f:tea_red2:red", 3.8, 2.6, 2.6, P(k, 9.0, 2.6), tag="tea box")
    box(k, "f:tea_red2:red", 3.8, 2.6, 2.6, P(k, 9.0, 5.4, rot=4), tag="tea box 2")
    box(k, "f:tea_black:black", 4.4, 2.6, 2.4, P(k, 9.0, 5.4, 2.6), tag="tea box dark")
    box(k, "f:tea_red:red", 3.0, 2.8, 5.4, P(k, 11.4, 3.0, rot=-6))
    box(k, "f:mugbox:sky_blue", 4.0, 4.4, 4.4, P(k, 15.0, 3.6, rot=-6))
    lathe(k, "c:black", [(0, 0), (0.7, 0), (0.7, 0.9), (2.0, 2.6), (1.8, 2.7), (0.5, 1.0), (0, 1.0)],
          P(k, 14.8, 3.6, 4.4), seg=10, tag="funnel")
    k.at(2)
    mug(k, "olive_mug", 1.6, 6.0, P(k, 1.8, 3.2), handle=1.0)
    cyl(k, "c:black", 1.7, 1.2, P(k, 1.8, 3.2), z0=6.0, tag="travel lid")
    box(k, "f:greentea:white", 2.6, 3.4, 5.0, P(k, 4.4, 9.0))
    can(k, "tin_cream", 1.6, 3.8, P(k, 7.2, 9.0))
    box(k, "c:ice_blue", 6.5, 3.6, 1.3, P(k, 6.4, 5.9), bevel=0.2, tag="ice tray")
    cyl(k, "c:coffee_brown", 1.4, 3.8, P(k, 8.0, 2.5), seg=10, tag="coffee press")
    cyl(k, "c:coffee_brown", 1.9, 0.3, P(k, 8.0, 2.5), seg=10, z0=3.8, tag="press flange")
    cyl(k, "w:water_bottle:white", 1.5, 8.4, P(k, 8.0, 2.5, 4.1), seg=10, tag="water bottle")
    cyl(k, "c:black", 0.9, 1.0, P(k, 8.0, 2.5, 12.5), seg=8, tag="bottle cap")
    cyl(k, "c:teal_bottle", 1.4, 8.0, P(k, 9.8, 7.0), seg=10, tag="teal bottle")
    box(k, "f:cocoa:yellow", 3.3, 3.0, 8.0, P(k, 11.8, 2.8, rot=-3))
    box(k, "c:yellow", 3.3, 0.1, 1.6, P(k, 11.8, 4.3, 8.0, rot=-3, tilt=(-15, 0)), bevel=0.0, tag="flap")
    box(k, "b:straws", 3.6, 1.4, 9.2, P(k, 13.8, 3.2, 0.3, tilt=(-4, 6)), tag="straws")
    k.at(3)
    blob(k, "c:clear", 3.6, 2.6, 1.1, P(k, 4.4, 4.6, rot=8), seed=9, amp=0.2, clear=True)
    blob(k, "c:clear", 3.4, 2.4, 1.0, P(k, 9.6, 5.2, rot=-12), seed=10, amp=0.2, clear=True)
    for i, (u, w, r) in enumerate(((3.6, 4.4, 10), (5.0, 4.8, -20), (8.8, 5.0, 30), (10.4, 5.4, -5))):
        box(k, "c:grey", 4.6, 0.5, 0.3, P(k, u, w, 0.4, rot=r), bevel=0.0, tag="fork")
    for u, w in ((13.4, 2.6), (15.4, 3.6)):
        cyl(k, "c:ceramic", 1.6, 0.4, P(k, u, w), seg=12, tag="small lid")


CABS = [("wu1", wu1), ("wu2", wu2), ("wu3", wu3), ("cu", cu), ("nu1", nu1), ("nu2", nu2), ("nu3", nu3)]


def build(coll):
    ii = _interior()
    objs, problems = [], []
    for cid, fn in CABS:
        k = K(cid, ii)
        fn(k)
        problems += k.problems
        objs.append(k.to_object(f"{NAME}_{cid}", coll))
        print(f"{cid}: {k.items} parts")
    for p in problems:
        print("OUTSIDE:", p)
    print("interior check:", "OK" if not problems else f"{len(problems)} problems")
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
