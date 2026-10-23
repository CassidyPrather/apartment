"""Kitchen base contents: everything inside the kitchen BASE cabinets and drawers, from
Cassidy's cupboard photos (Reference/cupboards_drawers, sorted index):

  7  sink    under the sink, south bay: green dishwasher-detergent box, white bleach jug,
             dark blue glass-cleaner bottle, white trigger sprayer, pink air-freshener
             spray, light blue fabric spray, blue dish soap, purple-headed spray, two
             white duster cans; north bay: white plastic dish tub, red jug, steel wool,
             a small steel cup; a stained floor liner
  8  corner  blind corner, on the L shelf: pressure cooker, steel steamer/pot stack, red
             bits, three white baking dishes; on the floor: an open cardboard box holding a
             blue snack box and a chip bag, a cereal-type box standing by the drawers
  9  d1      top drawer: box grater, two scissors (red/black), teal can opener, pizza
             cutter on a green jar-opener disc, black spatula, black peeler, measuring
             spoons on a ring, white mandoline/peeler, whetstone box, twine ball
  10 d2      dark grey saucepan, yellow silicone spoon, wooden spoon, black ladle, black
             slotted turner, steel turner, tongs, measuring cup, white scoop, black spatula
  11 d3      two cream oven gloves with blue stripe print, round and square black pot
             holders with red trim, blue towel, electric knife sharpener
  12 d4      trash-bag rolls (white, yellow drawstrings), crumpled bags, zip-bag box
  13 ed      grey cutlery tray: forks, spoons, soup spoons, knives; cream serving spoons,
             white soup spoon, chopsticks in the back slot; a mint-capped tape roll
  14 eb      shelf: two glass lids leaning, a skillet under a steel-rimmed lid, a pan
             behind; floor: a black saucepan with a long steel handle; stained floor liner

No brand, text or logo anywhere: packaging is flat colour blocks in the real colours.

Objects (see the cupboards brief's moving-part conventions):
  kitchen_base_contents_sink / _corner / _eb      static, inside the door cupboards
  kitchen_cabinets_drawer_<id>_contents  (d1 d2 d3 d4 ed)   placed in the CLOSED drawer;
      Unity reparents each under kitchen_cabinets_drawer_<id> so it slides with it.
The package is STATIC = False because the five drawer-contents objects move.

Source of truth: scripted. FRAME: PLAN COORDINATES (object X = plan x east, Y = plan y
north, Z up from the floor, metres): place the package at the plan origin, no rotation.
Interiors come from kitchen_cabinets/interior.py (read-only, re-imported at build time).

Provenance tags: PHOTO = proportioned from the cupboard photos against the interior
sizes, EST = standard product size or guess, MODEL = from kitchen_cabinets/interior.py.
"""

import contextlib
import importlib
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

import common

NAME = "kitchen_base_contents"
IN = 0.0254


def m(v):
    return v * IN


# --- interiors (MODEL: kitchen_cabinets/interior.py) -------------------------------------

def _interior():
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(os.path.dirname(here), "kitchen_cabinets")
    if d not in sys.path:
        sys.path.insert(0, d)
    import interior
    importlib.reload(interior)
    return interior


INT = _interior()

# --- sizes (inches) ------------------------------------------------------------------------
# EST standard product sizes, proportioned against each other in the photos (PHOTO)
DET_BOX = (3.0, 7.0, 9.5)        # EST dishwasher-detergent box d x w x h
BLEACH = (6.0, 5.2, 10.5)        # EST gallon-ish jug w x d x h (PHOTO lower than a full gallon)
BOTTLE_H = 9.0                   # EST spray / cleaner bottles
DISHPAN = (12.5, 14.0, 5.5)      # EST dish tub w x l x h
RED_JUG = (4.4, 6.2, 11.0)       # EST 1 gal; PHOTO about as tall as the bleach jug
P_COOKER = (5.0, 9.0)            # EST radius, height with lid (PHOTO behind/right of the steamer)
STEAMER_R = 4.6                  # EST
BAKING = (9.0, 6.0, 2.4)         # EST 2-qt rectangular dish
CEREAL = (7.5, 2.6, 11.5)        # EST; PHOTO top almost touches the shelf
CARTON = (11.0, 10.5, 7.0)       # EST cardboard box
GRATER = (3.3, 6.8, 11.5)        # EST blade w, blade l, total l
SCISSORS_L = 8.5                 # EST
GLOVE = (4.4, 10.0, 1.4)         # PHOTO two side by side fill the drawer width; EST length
POTHOLDER_R = 3.4                # PHOTO ~0.7 of the drawer width
TRAY = (14.5, 16.5, 2.0)         # PHOTO ~0.88 of the drawer width; EST depth, height
LID_R = (5.6, 4.7)               # EST 11 and 9.5 in glass lids
SKILLET_R = 5.5                  # EST 11 in skillet
SAUCEPAN_R = 4.0                 # EST

ATLAS = {
    "name": NAME,
    "size": 1024,
    "regions": {
        # 64 px flat swatches
        "white_plastic": (0, 0, 64, 64), "black_plastic": (64, 0, 64, 64),
        "steel": (128, 0, 64, 64), "steel_dark": (192, 0, 64, 64),
        "grey_plastic": (256, 0, 64, 64), "red_plastic": (320, 0, 64, 64),
        "teal": (384, 0, 64, 64), "yellow": (448, 0, 64, 64),
        "green_sil": (512, 0, 64, 64), "wood": (576, 0, 64, 64),
        "twine": (640, 0, 64, 64), "blue_cap": (704, 0, 64, 64),
        "navy_liquid": (768, 0, 64, 64), "aqua_liquid": (832, 0, 64, 64),
        "pink": (896, 0, 64, 64), "purple": (960, 0, 64, 64),
        "nonstick": (0, 64, 64, 64), "pot_black": (64, 64, 64, 64),
        "tray_dark": (128, 64, 64, 64), "tray_light": (192, 64, 64, 64),
        "ceramic": (256, 64, 64, 64), "cream_plastic": (320, 64, 64, 64),
        "trim_red": (384, 64, 64, 64), "trash_white": (448, 64, 64, 64),
        "trash_yellow": (512, 64, 64, 64), "foil": (576, 64, 64, 64),
        "mint": (640, 64, 64, 64), "tan": (704, 64, 64, 64),
        "glass": (768, 64, 64, 64), "clear_plastic": (832, 64, 64, 64),
        "red_jug": (896, 64, 64, 64), "light_blue": (960, 64, 64, 64),
        "rubber_black": (0, 128, 64, 64), "chrome": (64, 128, 64, 64),
        "white_lid": (128, 128, 64, 64), "green_box": (192, 128, 64, 64),
        "cardboard_in": (256, 128, 64, 64), "orange": (320, 128, 64, 64),
        "steel_wool": (384, 128, 64, 64), "black_glass": (448, 128, 64, 64),
        "dark_red": (512, 128, 64, 64),
        # painted regions (each piece gets the whole image, island-mapped)
        "glove": (0, 256, 256, 256),
        "glove_b": (0, 256, 256, 256),      # same print; the second glove's own top-down UVs
        "glove_in": (576, 128, 64, 64),
        "stain": (256, 256, 256, 256),
        "detergent": (512, 256, 128, 128),
        "bleach_label": (640, 256, 128, 128),
        "dish_label": (768, 256, 128, 128),
        "air_label": (896, 256, 128, 128),
        "spray_label": (512, 384, 128, 128),
        "duster_label": (640, 384, 128, 128),
        "jug_label": (768, 384, 128, 128),
        "whetstone": (896, 384, 128, 128),
        "cereal": (0, 512, 256, 256),
        "snack_box": (256, 512, 128, 128),
        "zip_box": (384, 512, 128, 128),
        "chip_bag": (512, 512, 128, 128),
        "trash_roll": (640, 512, 128, 128),
        "cardboard": (768, 512, 128, 128),
        "towel": (896, 512, 128, 128),
        "potholder": (0, 768, 128, 128),
        "slotted": (128, 768, 128, 128),
        "glass_cleaner": (256, 768, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
TOPDOWN = ("glove", "glove_b")   # one planar projection from above over each glove
PAINTED = ("stain", "detergent", "bleach_label", "dish_label", "air_label",
           "spray_label", "duster_label", "jug_label", "whetstone", "cereal", "snack_box",
           "zip_box", "chip_bag", "trash_roll", "cardboard", "towel", "potholder", "slotted",
           "glass_cleaner")
CLEAR_REGIONS = ("glass", "clear_plastic")
CLEAR_ALPHA = 0.28
MATERIALS = {
    NAME: {"atlas": NAME, "mode": "opaque", "tiled": False},
    NAME + "_clear": {"atlas": NAME, "mode": "transparent", "alpha": CLEAR_ALPHA, "tiled": False},
}
COLLIDER = "none"
STATIC = False          # the five drawer-contents objects slide with their drawers
# (name, azimuth, elevation, distance scale); az 0 = from the south
VIEWS = [("sink_from_e", 90, 15, 0.45), ("corner_from_se", 25, 25, 0.45),
         ("drawers_down", 0, 60, 0.45), ("eb_from_s", 0, 20, 0.45)]


# --- geometry kit (inches, in a local frame) ------------------------------------------------

def _rot(rz=0.0, ry=0.0, rx=0.0):
    return (Matrix.Rotation(math.radians(rz), 4, "Z") @ Matrix.Rotation(math.radians(ry), 4, "Y")
            @ Matrix.Rotation(math.radians(rx), 4, "X"))


class Kit:
    def __init__(self):
        self.b = common.Builder(REGIONS)
        self.bm = self.b.bm
        self.M = Matrix.Identity(4)

    @contextlib.contextmanager
    def at(self, x=0.0, y=0.0, z=0.0, rz=0.0, ry=0.0, rx=0.0):
        old = self.M
        self.M = old @ Matrix.Translation((m(x), m(y), m(z))) @ _rot(rz, ry, rx)
        try:
            yield
        finally:
            self.M = old

    @contextlib.contextmanager
    def seg(self, u0, v0, u1, v1, w=0.0, tilt=0.0):
        """Frame at (u0, v0, w) whose +x points to (u1, v1); tilt raises the far end (deg)."""
        a = math.degrees(math.atan2(v1 - v0, u1 - u0))
        with self.at(u0, v0, w, rz=a, ry=-tilt):
            yield math.hypot(u1 - u0, v1 - v0)

    def _mark(self):
        """Start a primitive in a scratch bmesh (bevels delete verts, so indices into the
        main bmesh can't track new geometry); _apply moves it by M and merges it."""
        main = self.b
        self.b = common.Builder(REGIONS)
        self.bm = self.b.bm
        return main

    def _apply(self, main):
        src = self.bm
        bmesh.ops.transform(src, matrix=self.M, verts=list(src.verts))
        vmap = {v: main.bm.verts.new(v.co) for v in src.verts}
        for f in src.faces:
            nf = main.bm.faces.new([vmap[v] for v in f.verts])
            nf.material_index = f.material_index
        src.free()
        self.b, self.bm = main, main.bm

    def box(self, r, x0, x1, y0, y1, z0, z1, bevel=0.0):
        n0 = self._mark()
        lo = (m(min(x0, x1)), m(min(y0, y1)), m(min(z0, z1)))
        hi = (m(max(x0, x1)), m(max(y0, y1)), m(max(z0, z1)))
        self.b.box(r, lo, hi, bevel=m(bevel), segments=1)
        self._apply(n0)

    def cbox(self, r, cx, cy, z0, w, d, h, bevel=0.0):
        self.box(r, cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0, z0 + h, bevel)

    def lathe(self, r, prof, seg=10, oval=(1.0, 1.0), regions=None, closed=False, capped=True):
        """Revolve [(radius, z)] about local Z, bottom to top; ends with radius > 0 get a
        cap. regions: optional per-band region list (len(prof) - 1)."""
        n0 = self._mark()
        bm = self.bm
        rings = []
        for rad, z in prof:
            if rad <= 1e-4:
                rings.append([bm.verts.new((0, 0, m(z)))])
            else:
                rings.append([bm.verts.new((m(rad * oval[0] * math.cos(2 * math.pi * i / seg)),
                                            m(rad * oval[1] * math.sin(2 * math.pi * i / seg)), m(z)))
                              for i in range(seg)])
        faces = []
        pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed else [])
        for k, (A, B) in enumerate(pairs):
            band = []
            for i in range(seg):
                q = [A[i % len(A)], A[(i + 1) % len(A)], B[(i + 1) % len(B)], B[i % len(B)]]
                uq = []
                for v in q:
                    if v not in uq:
                        uq.append(v)
                if len(uq) >= 3:
                    band.append(bm.faces.new(uq))
            self.b._tag(band, regions[k] if regions else r)
            faces += band
        caps = []
        if closed or not capped:
            pass
        elif len(rings[0]) > 1:
            caps.append(bm.faces.new(list(reversed(rings[0]))))
        if not closed and capped and len(rings[-1]) > 1:
            caps.append(bm.faces.new(rings[-1]))
        self.b._tag(caps, r)
        self._apply(n0)

    def cyl(self, r, rad, z0, h, seg=10, oval=(1.0, 1.0)):
        self.lathe(r, [(rad, z0), (rad, z0 + h)], seg=seg, oval=oval)

    def prism(self, r, outline, z0, z1):
        n0 = self._mark()
        self.b.prism(r, [(m(x), m(y)) for x, y in outline], m(z0), m(z1))
        self._apply(n0)

    def rrect(self, r, cx, cy, w, d, rad, z0, z1, seg=3):
        self.prism(r, common.rounded_rect(cx, cy, w, d, min(rad, w / 2 - 1e-3, d / 2 - 1e-3), seg), z0, z1)

    def tube(self, r, pts, rad, sides=6, samples=0, up=(0, 0, 1)):
        n0 = self._mark()
        q = [Vector((m(x), m(y), m(z))) for x, y, z in pts]
        if samples:
            q = common.smooth_path(q, samples)
        self.b.sweep(r, q, common.circle_profile(m(rad), sides), up=up)
        self._apply(n0)

    def flat(self, r, pts, w, t, z=0.0, samples=0):
        """Flat strap (w wide, t thick) along [(x, y, z)] lying on its broad side."""
        n0 = self._mark()
        q = [Vector((m(x), m(y), m(zz + z))) for x, y, zz in pts]
        if samples:
            q = common.smooth_path(q, samples)
        self.b.sweep(r, q, common.rect_profile(m(w), m(t)), up=(0, 0, 1))
        self._apply(n0)

    def loop(self, r, cx, cy, rx, ry, w, t, z=0.0, n=10, rot=0.0):
        """Closed flat ring (scissor finger loop, wire): a w x t strap round an ellipse."""
        main = self._mark()
        a0 = math.radians(rot)
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = rx * math.cos(a), ry * math.sin(a)
            pts.append(Vector((m(cx + x * math.cos(a0) - y * math.sin(a0)),
                               m(cy + x * math.sin(a0) + y * math.cos(a0)), m(z))))
        self.b.sweep(r, pts, common.rect_profile(m(w), m(t)), up=(0, 0, 1), closed=True)
        self._apply(main)

    def wire(self, r, pts, rad=0.05, sides=3, closed=False, samples=0):
        """Thin round wire through local points (inches)."""
        main = self._mark()
        q = [Vector((m(x), m(y), m(z))) for x, y, z in pts]
        if samples:
            q = common.smooth_path(q, samples)
        self.b.sweep(r, q, common.circle_profile(m(rad), sides), up=(0, 0, 1), closed=closed)
        self._apply(main)

    def blob(self, r, cx, cy, cz, sx, sy, sz, cuts=2, amp=0.12, seed=0, sq=0.45, freq=1.3):
        """Lumpy rounded box (fabric, bags): a subdivided cube pushed toward a sphere,
        scaled to sx, sy, sz and displaced with noise."""
        n0 = self._mark()
        bm = self.bm
        res = bmesh.ops.create_cube(bm, size=2.0)
        vs = res["verts"]
        edges = list({e for v in vs for e in v.link_edges})
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts, use_grid_fill=True)
        new = list(bm.verts)
        off = Vector((seed * 3.1, seed * 1.7, seed * 2.3))
        for v in new:
            p = v.co.copy()
            s = p.normalized()
            p = p * sq + s * (1 - sq)
            d = noise.noise(p * freq + off)
            p = p * (1 + amp * d)
            v.co = Vector((m(cx + p.x * sx / 2), m(cy + p.y * sy / 2), m(cz + p.z * sz / 2)))
        faces = list({f for v in new for f in v.link_faces})
        self.b._tag(faces, r)
        self._apply(n0)

    def obj(self, name, coll, origin):
        return self.b.to_object(name, coll, origin=tuple(m(c) for c in origin))


# --- reusable small things ----------------------------------------------------------------

def pot(k, r, rad, h, wall=0.18, seg=12, inner=None, base=0.25):
    """Open pot/pan: outer wall up, rim, inner wall down to the inner floor (closed solid)."""
    inner = inner or r
    k.lathe(r, [(rad - 0.4, 0), (rad, 0.35), (rad, h), (rad - wall, h), (rad - wall, base + 0.2),
                (rad - wall - 0.4, base), (0, base)], seg=seg,
            regions=[r, r, inner, inner, inner, inner])


def spray_bottle(k, body, label, head, h=BOTTLE_H, rad=1.4, oval=(1.0, 0.75), trigger=True):
    """Trigger spray bottle: shouldered body with a label band, neck, trigger head."""
    bh = h * 0.72
    k.lathe(body, [(rad * 0.9, 0), (rad, 0.3), (rad, bh * 0.2), (rad, bh * 0.8), (rad * 0.95, bh),
                   (rad * 0.5, bh + 0.8), (0.5, bh + 1.0)], seg=10, oval=oval,
            regions=[body, body, label, body, body, body])
    k.cyl(head, 0.6, bh + 1.0, 0.6, seg=8)
    if trigger:
        k.box(head, -0.6, 0.6, -0.5, 0.5, bh + 1.6, h - 0.4, bevel=0.15)
        k.box(head, 0.4, 1.9, -0.35, 0.35, h - 1.2, h - 0.2, bevel=0.1)    # nozzle
        k.box(head, 0.3, 0.7, -0.25, 0.25, bh + 1.5, h - 1.4)              # trigger
    else:
        k.cyl(head, 0.75, bh + 1.6, h - bh - 1.6, seg=8)


def scissors(k, u0, v0, u1, v1, w, ring="red_plastic", grip="black_plastic", blade="steel"):
    """Scissors lying flat from the handle end (u0, v0) to the tip (u1, v1)."""
    with k.seg(u0, v0, u1, v1, w) as L:
        hl = L * 0.42
        for side, big in ((0.95, 1.15), (-0.85, 0.95)):
            rx, ry = hl * 0.42 * big, 0.75 * big
            k.loop(grip, hl * 0.45, side, rx, ry, 0.32, 0.3, z=0.15, n=12)               # black loop
            k.loop(ring, hl * 0.45, side, rx - 0.22, ry - 0.22, 0.14, 0.34, z=0.15, n=12)  # red liner
            k.box(grip, hl * 0.8, hl + 0.2, side * 0.25 - 0.2, side * 0.25 + 0.2, 0.0, 0.3)  # neck
        k.prism(blade, [(hl, -0.45), (L, -0.05), (L, 0.05), (hl, 0.5)], 0.05, 0.18)
        k.prism(blade, [(hl, 0.45), (L * 0.97, 0.12), (L * 0.97, 0.2), (hl, -0.4)], 0.18, 0.3)
        with k.at(hl + 0.1, 0, 0.3):
            k.cyl("steel_dark", 0.25, 0, 0.1, seg=6)


def whisk(k, u0, v0, u1, v1, w, handle="black_plastic", R=1.0, loops=4):
    """Balloon whisk lying from its handle end to the wire tip."""
    with k.seg(u0, v0, u1, v1, w + R) as L:
        hl = L * 0.45
        k.rrect(handle, hl / 2, 0, hl, 0.7, 0.3, -0.3, 0.3, seg=2)
        wl = L - hl
        for i in range(loops):
            a = math.radians(i * 180 / loops)
            ca, sa = math.cos(a), math.sin(a)
            prof = [(0, 0.15), (0.3 * wl, 0.55 * R), (0.7 * wl, R), (0.95 * wl, 0.5 * R), (wl, 0.0),
                    (0.95 * wl, -0.5 * R), (0.7 * wl, -R), (0.3 * wl, -0.55 * R), (0, -0.15)]
            k.wire("steel", [(hl + x, y * ca, y * sa) for x, y in prof], rad=0.05, sides=3,
                   closed=True, samples=2)


def masher(k, u0, v0, u1, v1, w, handle="black_plastic"):
    """Potato masher lying on its side: handle, steel shaft, zigzag wire head (on edge)."""
    with k.seg(u0, v0, u1, v1, w + 1.7) as L:
        k.rrect(handle, 2.2, 0, 4.4, 0.9, 0.4, -0.35, 0.35, seg=2)
        k.box("steel", 4.4, L - 0.2, -0.15, 0.15, -0.1, 0.1)
        zig = [(L, -1.6 + i * 0.8, (0.7 if i % 2 else -0.7)) for i in range(5)]
        k.wire("steel", [(L, -1.6, 0.0)] + [(x, y, z * 2.2) for x, y, z in zig] + [(L, 1.6, 0.0)],
               rad=0.09, sides=4)
        k.wire("steel", [(L - 0.2, 0, 0), (L, -1.6, 0)], rad=0.09, sides=4)
        k.wire("steel", [(L - 0.2, 0, 0), (L, 1.6, 0)], rad=0.09, sides=4)


def utensil(k, u0, v0, u1, v1, w, handle, head, kind, head_l, head_w, handle_w=0.7,
            handle_t=0.35, tilt=0.0, head_region2=None):
    """Kitchen tool lying from its handle end (u0, v0) to its head end (u1, v1)."""
    with k.seg(u0, v0, u1, v1, w, tilt) as L:
        hl = L - head_l
        k.rrect(handle, hl / 2, 0, hl, handle_w, handle_w * 0.45, 0, handle_t, seg=2)
        c = hl + head_l / 2
        if kind == "turner":
            k.box(handle, hl - 0.3, hl + 0.6, -0.25, 0.25, 0.05, 0.2)
            k.rrect(head, c, 0, head_l, head_w, 0.5, 0.0, 0.16, seg=2)
        elif kind == "spoon":
            with k.at(c, 0, 0.3):
                k.lathe(head, [(0.01, -0.3), (head_w * 0.35, -0.22), (head_w / 2, 0.05),
                               (head_w / 2 - 0.12, 0.12), (0.01, -0.12)], seg=10,
                        oval=(head_l / head_w, 1.0))
        elif kind == "server":                       # pasta server: shallow bowl ringed with teeth
            with k.at(c, 0, 0.3):
                k.lathe(head, [(0.01, -0.3), (head_w * 0.35, -0.22), (head_w / 2, 0.05),
                               (head_w / 2 - 0.12, 0.12), (0.01, -0.12)], seg=10,
                        oval=(head_l / head_w, 1.0))
                for i in range(7):
                    a = math.radians(-60 + i * 20)
                    tx, ty = head_l / 2 * math.cos(a), head_w / 2 * math.sin(a)
                    k.box(head, tx - 0.12, tx + 0.12, ty - 0.12, ty + 0.12, 0.0, 0.55)
        elif kind == "ladle":
            k.box(handle, hl - 0.2, hl + head_l * 0.2, -0.25, 0.25, 0.1, 0.3)
            with k.at(c + head_l * 0.15, 0, head_w * 0.45):
                k.lathe(head, [(0.01, -head_w * 0.42), (head_w * 0.42, -head_w * 0.2),
                               (head_w / 2, 0.15), (head_w / 2 - 0.12, 0.15),
                               (head_w * 0.38, -head_w * 0.15), (0.01, -head_w * 0.3)], seg=10)
        elif kind == "fork":
            k.prism(head, [(hl, -0.3), (hl + head_l * 0.45, -head_w / 2), (hl + head_l * 0.55, -head_w / 2),
                           (hl + head_l * 0.55, head_w / 2), (hl + head_l * 0.45, head_w / 2), (hl, 0.3)],
                    0.02, 0.12)
            tw = head_w / 7
            for i in range(4):
                y = -head_w / 2 + tw / 2 + i * 2 * tw
                k.box(head, hl + head_l * 0.55, L, y - tw / 2, y + tw / 2, 0.02, 0.12)
        elif kind == "knife":
            k.prism(head, [(hl, -head_w / 2), (L - 1.2, -head_w / 2), (L, 0.0),
                           (L, head_w * 0.1), (hl, head_w / 2)], 0.05, 0.12)
        elif kind == "none":
            pass
        return L


# --- under the sink (photo 7) ---------------------------------------------------------------

def sink(coll):
    c = INT.CABINETS["sink"]
    (x0, x1), (y0, y1), (z0, _) = c["x"], c["y"], c["z"]
    xf = c["front"]
    k = Kit()
    # local frame: u along the run (south to north), v from the face frame back toward the
    # wall, w up from the cabinet floor; photo left = south
    with k.at(xf, y0, z0, rz=90):
        # (u, v) -> plan (xf - v, y0 + u)
        depth = xf - x0
        wid = y1 - y0
        # south bay, front to back, left to right
        with k.at(2.75, 5.5, 0.04, rz=68):                       # detergent box, broad face to the north
            k.cbox("detergent", 0, 0, 0, DET_BOX[1], DET_BOX[0], DET_BOX[2], bevel=0.08)
        with k.at(4.0, 3.2, 0.04):                               # dark blue glass cleaner
            k.lathe("glass_cleaner", [(1.2, 0), (1.35, 0.3), (1.35, 6.0), (1.1, 7.2), (0.5, 7.8)],
                    seg=10, oval=(1.0, 0.8))
            k.cyl("blue_cap", 0.55, 7.8, 1.0, seg=8)
        with k.at(7.5, 9.5, 0.04, rz=10):                        # bleach jug behind
            w_, d_, h_ = BLEACH
            k.cbox("bleach_label", 0, 0, 0, w_ - 0.5, d_, h_ * 0.62, bevel=0.6)
            k.lathe("white_plastic", [(2.3, h_ * 0.6), (2.0, h_ * 0.85), (0.8, h_ - 0.6)], seg=10,
                    oval=(1.15, 1.0))
            k.cyl("blue_cap", 0.85, h_ - 0.7, 0.9, seg=8)
            k.tube("white_plastic", [(1.8, 0, h_ * 0.62), (2.6, 0, h_ * 0.8), (1.3, 0, h_ * 0.92)],
                   0.45, sides=6, samples=2)
        with k.at(6.4, 7.0, 0.04, rz=-70):                       # white trigger sprayer
            spray_bottle(k, "white_plastic", "white_plastic", "white_plastic", h=11.0, rad=1.4)
        with k.at(7.8, 2.6, 0.04, rz=-80):                       # pink air freshener
            spray_bottle(k, "white_plastic", "air_label", "pink", h=9.3, rad=1.15, oval=(1.0, 0.8),
                         trigger=False)
        with k.at(9.0, 6.5, 0.04, rz=-80):                       # light blue fabric spray
            spray_bottle(k, "light_blue", "spray_label", "light_blue", h=9.8, rad=1.3)
        with k.at(10.8, 2.6, 0.04, rz=5):                        # blue dish soap, flip cap
            k.lathe("aqua_liquid", [(1.5, 0), (1.7, 0.4), (1.7, 3.0), (1.55, 6.5), (1.2, 8.0),
                                    (0.6, 8.7)], seg=10, oval=(1.0, 0.55),
                    regions=["aqua_liquid", "dish_label", "dish_label", "aqua_liquid", "aqua_liquid"])
            k.cyl("white_plastic", 0.5, 8.7, 0.9, seg=8)
        with k.at(12.6, 5.5, 0.04, rz=-75):                      # purple-headed spray
            spray_bottle(k, "light_blue", "spray_label", "purple", h=10.2, rad=1.35)
        for u, v, h in ((13.3, 9.0, 8.2), (15.0, 10.5, 8.0)):    # duster cans, red caps
            with k.at(u, v, 0.04):
                k.cyl("duster_label", 1.25, 0, h - 1.2, seg=10)
                k.lathe("red_plastic", [(1.0, h - 1.2), (0.9, h - 0.3), (0.3, h)], seg=8)
        with k.at(13.5, 13.5, 0.04, rz=-60):                     # small sprayer at the back
            spray_bottle(k, "white_plastic", "duster_label", "red_plastic", h=9.5, rad=1.2)
        # north bay: dish tub (open, a little skewed), red jug in front, steel wool
        tw, tl, th = DISHPAN
        with k.at(26.5, 13.0, 0.04, rz=8):
            t = 0.25
            k.box("white_plastic", -tw / 2, tw / 2, -tl / 2, tl / 2, 0, t, bevel=0.1)
            k.box("white_plastic", -tw / 2, -tw / 2 + t, -tl / 2, tl / 2, 0, th)
            k.box("white_plastic", tw / 2 - t, tw / 2, -tl / 2, tl / 2, 0, th)
            k.box("white_plastic", -tw / 2, tw / 2, -tl / 2, -tl / 2 + t, 0, th)
            k.box("white_plastic", -tw / 2, tw / 2, tl / 2 - t, tl / 2, 0, th)
            k.box("white_plastic", -tw / 2 - 0.4, tw / 2 + 0.4, -tl / 2 - 0.4, -tl / 2 + 0.05,
                  th - 0.4, th)
            k.box("white_plastic", -tw / 2 - 0.4, tw / 2 + 0.4, tl / 2 - 0.05, tl / 2 + 0.4,
                  th - 0.4, th)
        jw, jd, jh = RED_JUG
        with k.at(21.0, 3.6, 0.04, rz=-5):
            k.cbox("jug_label", 0, 0, 0, jw, jd, jh * 0.7, bevel=0.5)
            k.lathe("red_jug", [(1.9, jh * 0.68), (1.6, jh * 0.86), (0.75, jh - 0.9)], seg=10,
                    oval=(1.0, 1.35))
            k.cyl("black_plastic", 0.85, jh - 0.95, 1.0, seg=10)
            k.tube("red_jug", [(0, 1.6, jh * 0.45), (0, 2.9, jh * 0.6), (0, 2.6, jh * 0.85),
                               (0, 1.1, jh * 0.9)], 0.5, sides=6, samples=2)
        k.blob("steel_wool", 18.6, 3.3, 0.9, 2.8, 2.4, 1.6, cuts=2, amp=0.35, seed=3, freq=2.5)
        with k.at(18.4, 7.4, 0.04):                              # small steel cup / can
            k.cyl("steel", 1.1, 0, 2.6, seg=10)
    return k.obj(NAME + "_sink", coll, ((x0 + xf) / 2, (y0 + y1) / 2, z0))


# --- blind corner (photo 8) ---------------------------------------------------------------

def corner(coll):
    c = INT.CABINETS["corner"]
    (x0, x1), (y0, y1), (z0, _) = c["x"], c["y"], c["z"]
    zs = c["shelves"][0]
    k = Kit()
    # on the shelf's north strip (y 273.5-285.5): pressure cooker behind the door opening,
    # the steel steamer stack west of it, red bits on the west strip (x 0.5-12.5)
    pr, ph = P_COOKER
    with k.at(25.6, 279.6, zs):
        k.lathe("steel", [(pr - 0.4, 0), (pr, 0.4), (pr, ph * 0.62)], seg=14)
        k.lathe("black_plastic", [(pr + 0.25, ph * 0.62), (pr + 0.25, ph * 0.72), (pr * 0.85, ph * 0.9),
                                  (pr * 0.5, ph - 0.4), (0.01, ph - 0.3)], seg=14)
        k.box("black_plastic", -1.2, 1.2, -pr - 0.6, pr + 0.6, ph * 0.62, ph * 0.72)   # side handles
        k.box("black_plastic", -0.5, 0.5, -1.8, 1.8, ph - 0.4, ph + 0.4, bevel=0.2)    # lid knob
        k.box("steel_dark", pr - 0.1, pr + 0.05, -1.6, 1.6, 2.0, 4.5)                  # panel
    with k.at(15.8, 278.6, zs):
        pot(k, "steel", STEAMER_R, 3.4, seg=14)                                         # steamer base
        k.box("black_plastic", -0.4, 0.4, -STEAMER_R - 0.8, -STEAMER_R + 0.2, 2.2, 2.8)
        with k.at(0.3, -0.3, 3.4):
            pot(k, "steel", STEAMER_R + 0.6, 2.9, seg=14)                               # wide pot on top
        for a in (0, 120, 240):                                                         # little feet
            with k.at(STEAMER_R * 0.8 * math.cos(math.radians(a)), STEAMER_R * 0.8 * math.sin(math.radians(a)), -0.0):
                pass
    with k.at(11.2, 275.0, zs):                                                         # red cups + cord
        k.lathe("red_plastic", [(0.9, 0), (1.25, 1.8), (1.1, 1.8), (0.75, 0.2)], seg=8)
        with k.at(0.2, 1.5, 0, rx=70):
            k.lathe("red_plastic", [(0.8, 0), (1.15, 1.5), (1.0, 1.5), (0.65, 0.2)], seg=8)
        k.tube("black_plastic", [(-1.0, 3.5, 0.2), (0.5, 2.5, 0.3), (1.0, 0.8, 0.25), (-0.8, -0.6, 0.3),
                                 (-2.0, 1.5, 0.25)], 0.15, sides=4, samples=3)
    # the east leg (x 28.8-35.75): three white baking dishes stacked, long side front-to-back
    bl, bw, bh = BAKING
    for i, (dx, dy, dz, rz) in enumerate(((32.2, 266.5, 0.0, 2), (32.4, 267.0, bh - 0.3, -3),
                                          (32.0, 266.2, 2 * bh - 0.6, 4))):
        with k.at(dx, dy, zs + dz, rz=90 + rz):
            t = 0.3
            k.box("ceramic", -bl / 2 + 0.3, bl / 2 - 0.3, -bw / 2 + 0.3, bw / 2 - 0.3, 0, t, bevel=0.1)
            for sx in (-1, 1):
                k.box("ceramic", sx * (bl / 2) - (t if sx > 0 else 0), sx * (bl / 2) + (0 if sx > 0 else t),
                      -bw / 2, bw / 2, 0, bh, bevel=0.1)
                k.box("ceramic", -bl / 2, bl / 2, sx * (bw / 2) - (t if sx > 0 else 0),
                      sx * (bw / 2) + (0 if sx > 0 else t), 0, bh, bevel=0.1)
            for sx in (-1, 1):                                                          # end handles
                k.box("ceramic", sx * bl / 2 - (0 if sx > 0 else 1.0), sx * bl / 2 + (1.0 if sx > 0 else 0),
                      -bw / 2 + 1.0, bw / 2 - 1.0, bh - 0.5, bh - 0.15)
    # floor: open cardboard box with a blue snack box and a chip bag in it
    cw, cd, ch = CARTON
    with k.at(22.5, 268.5, z0, rz=-8):
        t = 0.15
        k.box("cardboard_in", -cw / 2, cw / 2, -cd / 2, cd / 2, 0, t)
        k.box("cardboard", -cw / 2, -cw / 2 + t, -cd / 2, cd / 2, 0, ch)
        k.box("cardboard", cw / 2 - t, cw / 2, -cd / 2, cd / 2, 0, ch)
        k.box("cardboard", -cw / 2, cw / 2, -cd / 2, -cd / 2 + t, 0, ch)
        k.box("cardboard", -cw / 2, cw / 2, cd / 2 - t, cd / 2, 0, ch)
        # flaps: front flap folded out and down, east flap up and out, west flap leaning out
        with k.at(0, -cd / 2, ch, rx=-120):
            k.box("cardboard", -cw / 2, cw / 2, -t, 0, 0, cd / 2 - 0.3)
        with k.at(cw / 2, 0, ch, ry=60):
            k.box("cardboard", 0, t, -cd / 2, cd / 2, 0, cw / 2 - 1.5)
        with k.at(-cw / 2, 0, ch, ry=-75):
            k.box("cardboard", -t, 0, -cd / 2, cd / 2, 0, cw / 2 - 2.5)
        with k.at(1.5, 0.5, t, rz=12, rx=-12):
            k.cbox("snack_box", 0, 0, 0, 7.5, 2.4, 6.8, bevel=0.05)
        k.blob("chip_bag", -2.8, 1.5, 5.6, 6.0, 4.0, 3.0, cuts=2, amp=0.25, seed=5, sq=0.3)
    # cereal-type box standing in front of the east leg, facing the door
    cw2, cd2, ch2 = CEREAL
    with k.at(31.6, 263.4, z0, rz=-25):
        k.cbox("cereal", 0, 0, 0, cw2, cd2, ch2, bevel=0.05)
    return k.obj(NAME + "_corner", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))


# --- under the east drawer (photo 14) -----------------------------------------------------

def glass_lid(k, rad, handle=True):
    """Glass lid in its local XY plane: domed glass, steel rim, steel loop handle."""
    k.lathe("glass", [(rad - 0.12, 0.0), (rad * 0.85, 0.22), (rad * 0.55, 0.48), (0.01, 0.62)], seg=20,
            capped=False)                     # one surface: a single see-through layer
    k.lathe("steel", [(rad + 0.05, -0.1), (rad + 0.05, 0.12), (rad - 0.25, 0.12), (rad - 0.25, -0.1)],
            seg=20, closed=True)
    if handle:
        k.lathe("steel", [(0.75, 0.55), (0.7, 0.75), (0.01, 0.8)], seg=8)           # knob base plate
        k.tube("steel", [(-1.4, 0, 0.7), (-1.1, 0, 1.4), (1.1, 0, 1.4), (1.4, 0, 0.7)], 0.18, sides=4)
        for x in (-1.4, 1.4):
            with k.at(x, 0, 0.6):
                k.cyl("steel", 0.3, 0, 0.2, seg=6)


def pan(k, rad, h, handle_l, r="nonstick", grip="rubber_black", bend=20):
    """Skillet/saucepan with a long handle along local -y."""
    pot(k, r, rad, h, seg=14)
    with k.at(0, -rad + 0.2, h * 0.75, rx=-bend):
        k.box("steel", -0.4, 0.4, -handle_l * 0.45, 0, -0.15, 0.15)
        k.box(grip, -0.5, 0.5, -handle_l, -handle_l * 0.4, -0.25, 0.25, bevel=0.15)


def eb(coll):
    c = INT.CABINETS["eb"]
    (x0, x1), (y0, y1), (z0, _) = c["x"], c["y"], c["z"]
    zs = c["shelves"][0]
    k = Kit()
    # local frame: u east from x0, v north from the face frame back
    with k.at(x0, y0, z0):
        # floor: black saucepan at the back left, long steel handle out to the front left
        with k.at(5.8, 16.5, 0.04, rz=-20):
            pot(k, "pot_black", SAUCEPAN_R, 4.2, seg=12)
            with k.at(0, -SAUCEPAN_R + 0.2, 3.5, rx=-12):
                k.box("steel", -0.4, 0.4, -7.5, 0, -0.12, 0.12)
                k.box("steel", -0.3, 0.3, -7.5, -6.5, -0.12, 0.6)
    sh = zs - z0
    with k.at(x0, y0, zs):
        # back left: a dark pan on edge-ish, handle up toward the back
        with k.at(6.5, 17.0, 0.0, rz=10):
            pan(k, 5.0, 2.2, 7.0, r="nonstick", bend=-35)
        # right: skillet with its handle to the front, a steel-rimmed dark lid lying on it
        with k.at(13.0, 13.7, 0.0, rz=-12):
            pan(k, SKILLET_R, 1.9, 8.5, bend=-8)
            with k.at(-0.4, 0.8, 2.2, rx=8, ry=-6):
                k.lathe("black_glass", [(SKILLET_R + 0.2, 0.0), (SKILLET_R * 0.6, 0.5), (0.01, 0.7)], seg=14)
                k.lathe("steel", [(SKILLET_R + 0.45, -0.1), (SKILLET_R + 0.45, 0.12),
                                  (SKILLET_R + 0.15, 0.12), (SKILLET_R + 0.15, -0.1)], seg=14,
                        closed=True)
        # left: two glass lids leaning back against the pans
        with k.at(5.8, 8.5, 5.0, rz=15, rx=58):
            glass_lid(k, LID_R[0])
        with k.at(8.2, 7.2, 2.2, rz=-5, rx=28):
            glass_lid(k, LID_R[1])
    return k.obj(NAME + "_eb", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))


# --- drawers -------------------------------------------------------------------------------

def _drawer_frame(did):
    d = INT.DRAWERS[did]
    (x0, x1), (y0, y1), (z0, z1) = d["x"], d["y"], d["z"]
    return x0, x1, y0, y1, z0, z1


def d1(coll):
    x0, x1, y0, y1, z0, z1 = _drawer_frame("d1")
    W, D = x1 - x0, y1 - y0
    k = Kit()
    with k.at(x0, y0, z0):
        # back: whetstone box (left) and a twine ball (right)
        k.box("whetstone", 0.3, 6.6, D - 2.9, D - 0.3, 0, 2.4, bevel=0.06)
        with k.at(W - 1.6, D - 1.6, 1.35):
            k.lathe("twine", [(0.01, -1.3), (1.0, -1.15), (1.45, -0.5), (1.45, 0.5), (1.0, 1.15),
                              (0.01, 1.3)], seg=10)
        # white mandoline/peeler across the back
        with k.seg(2.8, D - 3.6, W - 0.6, D - 5.6, 0.2) as L:
            k.rrect("white_plastic", L / 2, 0, L, 1.0, 0.4, 0, 0.35)
            k.box("steel", L - 2.4, L - 0.3, -0.7, 0.7, 0.0, 0.3)
        # green jar-opener disc with the pizza cutter on it (left middle)
        with k.at(3.0, 10.0, 0.0):
            k.cyl("green_sil", 2.0, 0, 0.12, seg=12)
        with k.seg(0.9, 4.0, 3.6, 9.3, 0.2, tilt=3) as L:          # pizza cutter lying flat
            k.rrect("black_plastic", L / 2, 0, L, 1.1, 0.5, 0.0, 0.6)
            with k.at(L + 1.2, 0, 0.15):
                k.cyl("steel", 1.5, 0, 0.12, seg=12)
                k.cyl("black_plastic", 0.45, 0.12, 0.35, seg=8)
        # black silicone turner along the left wall
        utensil(k, 1.2, 6.0, 1.5, 18.2, 0.15, "black_plastic", "black_plastic", "turner",
                4.2, 3.0, handle_w=0.8)
        # measuring spoons on a ring (right, behind the shears)
        for i in range(5):
            with k.seg(W - 1.0 - i * 0.12, 13.0 + i * 0.35, W - 3.8, 16.2 + i * 0.25, 0.35 + i * 0.08):
                k.box("steel", 0, 2.3, -0.2, 0.2, 0, 0.06)
                with k.at(3.0, 0, 0.1):
                    k.lathe("steel", [(0.01, -0.3), (0.65 - i * 0.07, -0.1), (0.7 - i * 0.07, 0.15),
                                      (0.01, 0.0)], seg=8)
        # box grater: yellow frame, steel blade, black handle toward the front
        gw, gl, gL = GRATER
        with k.seg(5.0, 2.8, 5.0, 2.8 + gL, 0.8, tilt=3):
            k.rrect("black_plastic", 2.5, 0, 5.0, 1.3, 0.55, -0.35, 0.45)
            k.rrect("yellow", gL - gl / 2 - 0.3, 0, gl + 0.6, gw + 0.5, 0.5, 0.0, 0.35)
            k.box("steel", gL - gl - 0.1, gL - 0.5, -gw / 2 + 0.15, gw / 2 - 0.15, 0.35, 0.42)
            k.box("red_plastic", 4.8, 5.6, 0.65, 1.25, 0.0, 0.5)
        # black-handled tool under the grater handle, black peeler right of it
        utensil(k, 6.6, 3.0, 7.0, 9.6, 0.1, "black_plastic", "steel", "none", 0.5, 1.0, handle_w=1.0,
                handle_t=0.45)
        utensil(k, 7.6, 5.5, 7.2, 12.8, 0.1, "black_plastic", "steel", "turner", 1.6, 0.8,
                handle_w=0.75, handle_t=0.4)
        # kitchen shears on the right, handles to the front
        scissors(k, W - 1.8, 5.2, W - 2.3, 13.4, 0.45)
        # teal can opener across the front
        with k.at(0.0, 0.0, 0.5):
            k.rrect("teal", 6.4, 5.4, 5.6, 0.75, 0.35, 0, 0.45)
            k.rrect("teal", 6.6, 3.9, 5.4, 0.75, 0.35, 0, 0.45)
            k.box("steel", 2.1, 4.0, 3.5, 5.8, 0.0, 0.5)
            with k.at(2.8, 4.6, 0.45):
                k.cyl("teal", 0.95, 0, 0.8, seg=10)
        # scissors at the very front, tip to the right
        scissors(k, 1.2, 1.9, W - 0.8, 2.3, 0.0)
        # small whisk lying over the middle, wires to the back
        whisk(k, 6.6, 10.8, 3.4, 16.6, 0.9, R=0.65, loops=3)
        # second peeler: black Y-peeler, blade at the back
        with k.seg(5.9, 12.0, 6.8, 17.4, 0.75) as L:
            k.rrect("black_plastic", 1.8, 0, 3.6, 0.8, 0.35, 0, 0.4)
            for sd in (-1, 1):
                k.box("black_plastic", 3.5, L - 0.2, sd * 0.9 - 0.15, sd * 0.9 + 0.15, 0.05, 0.3)
            k.box("steel", L - 0.4, L, -1.0, 1.0, 0.1, 0.2)
        # steel bottle opener (flat, with a hole) by the shears
        with k.seg(W - 3.0, 13.6, W - 2.7, 17.2, 0.55) as L:
            k.box("steel", 0, L - 1.2, -0.3, 0.3, 0, 0.08)
            k.loop("steel", L - 0.7, 0, 0.55, 0.5, 0.22, 0.08, z=0.04, n=10)
        # red-handled garlic press under the grater handle
        utensil(k, 8.2, 2.6, 5.8, 8.4, 0.05, "red_plastic", "steel", "turner", 1.6, 1.3,
                handle_w=0.7, handle_t=0.4)
    ob = k.obj("kitchen_cabinets_drawer_d1_contents", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))
    return ob


def d2(coll):
    x0, x1, y0, y1, z0, z1 = _drawer_frame("d2")
    W, D = x1 - x0, y1 - y0
    k = Kit()
    with k.at(x0, y0, z0):
        # back: clear measuring cup, white scoop, black spatula
        with k.at(2.2, D - 2.6, 0.0):
            k.lathe("clear_plastic", [(1.2, 0), (1.55, 2.6), (1.4, 2.6), (1.05, 0.15)], seg=10)
        utensil(k, 3.2, D - 0.8, 6.8, D - 2.4, 0.4, "white_plastic", "white_plastic", "spoon",
                2.6, 2.2, handle_w=0.6)
        utensil(k, 1.2, 11.0, 3.6, 19.0, 0.6, "black_plastic", "black_plastic", "turner", 3.0, 2.0,
                handle_w=0.8)
        # steel turner and slotted black turner (back, middle-right)
        utensil(k, 6.2, 2.0, 5.0, 17.8, 0.9, "steel", "steel", "turner", 4.2, 2.6, handle_w=0.7,
                handle_t=0.2)
        utensil(k, 6.9, 1.2, 6.6, 19.8, 1.4, "steel", "slotted", "turner", 4.0, 2.8, handle_w=0.6,
                handle_t=0.2)
        # black ladle on the right, bowl at the back
        utensil(k, 8.4, 1.0, 6.9, 13.8, 1.6, "black_plastic", "black_plastic", "ladle", 3.8, 3.6,
                handle_w=0.8)
        # tongs: steel arms, black tips, lying corner to corner
        with k.seg(7.2, 1.2, 3.6, 13.5, 1.6) as L:
            for s in (-0.35, 0.35):
                k.box("steel", 0, L - 2.5, s - 0.3, s + 0.3, 0, 0.12)
                k.box("black_plastic", L - 2.5, L, s * 1.6 - 0.35, s * 1.6 + 0.35, 0, 0.25)
        # wooden spoon on the left, handle to the front right
        utensil(k, 8.6, 0.6, 1.6, 11.5, 2.3, "wood", "wood", "spoon", 3.2, 1.9, handle_w=0.55,
                handle_t=0.45, tilt=-4)
        # yellow silicone spoon
        utensil(k, 4.4, 0.4, 1.8, 13.8, 1.8, "yellow", "yellow", "spoon", 3.8, 2.4, handle_w=0.75,
                handle_t=0.45, tilt=-3)
        # small dark grey saucepan on top, handle to the front left
        with k.at(5.5, 9.8, 1.9, rz=-45, rx=-6):
            pot(k, "grey_plastic", 2.3, 2.2, seg=12)
            with k.at(0, -2.2, 1.6):
                k.rrect("grey_plastic", 0, -2.5, 0.85, 5.2, 0.4, -0.15, 0.2)
        # more black utensils behind the pan: slotted spoon, pasta server, whisk, potato masher
        utensil(k, 1.4, 3.0, 2.8, 19.6, 2.7, "black_plastic", "slotted", "spoon", 3.4, 2.4,
                handle_w=0.75, handle_t=0.3)
        utensil(k, 9.0, 3.5, 7.8, 19.4, 0.8, "black_plastic", "black_plastic", "server", 3.2, 2.4,
                handle_w=0.75, handle_t=0.3)
        whisk(k, 8.2, 6.5, 4.6, 19.6, 2.2, R=1.05, loops=4)
        masher(k, 0.9, 6.0, 2.9, 17.6, 1.0)
        # wooden rod down the right side
        with k.seg(W - 0.6, 4.0, W - 0.6, 14.5, 0.3) as L:
            k.box("wood", 0, L, -0.3, 0.3, -0.3, 0.3)
    return k.obj("kitchen_cabinets_drawer_d2_contents", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))


def glove(k, region, seed, fingers=True, thumb_side=1):
    """Flat quilted oven glove in local XY, cuff at -y, fingers toward +y: a cuff tube with
    an inner opening, a puffy palm, four splayed fingers and a thumb, all soft ellipsoids
    (UVs are a top-down projection over the whole glove, so the stripe print runs across it)."""
    gw, gl, gt = GLOVE
    # cuff: flattened tube along y, slightly flared, the dark opening at the front
    with k.at(0, -gl / 2, gt / 2, rx=-90):
        rr = 1.0
        k.lathe(region, [(rr * 1.06, 0.0), (rr * 1.08, 0.3), (rr * 1.0, 1.4), (rr * 0.97, 3.6)], seg=12,
                oval=(gw / 2 * 1.04, gt / 2))
        k.lathe("glove_in", [(rr * 0.85, -0.04), (rr * 0.85, -0.015)], seg=12, oval=(gw / 2 * 1.04, gt / 2))
    # palm / back of the hand
    k.blob(region, 0, gl * 0.05, gt / 2, gw, gl * 0.48, gt, cuts=3, amp=0.06, seed=seed, sq=0.0)
    if fingers:
        fw = gw / 4.2
        for i in range(4):
            fx = -gw / 2 + fw * (i + 0.55)
            fl = (2.6, 3.2, 3.0, 2.4)[i]
            with k.at(fx, gl * 0.2, gt * 0.45, rz=(1.5 - i) * 5):
                k.blob(region, 0, fl / 2, 0, fw * 0.92, fl + 0.6, gt * 0.72, cuts=2, amp=0.05, sq=0.0,
                       seed=seed + 2 + i)
    else:                                   # folded over: the fingers tucked under as a roll
        k.blob(region, 0, gl * 0.27, gt * 0.5, gw * 0.95, 2.2, gt * 1.05, cuts=2, amp=0.06, sq=0.0,
               seed=seed + 2)
    with k.at(thumb_side * gw * 0.42, -gl * 0.06, gt * 0.45, rz=-thumb_side * 38):
        k.blob(region, 0, 1.3, 0, 1.25, 3.2, gt * 0.75, cuts=2, amp=0.05, seed=seed + 7, sq=0.0)


def d3(coll):
    x0, x1, y0, y1, z0, z1 = _drawer_frame("d3")
    W, D = x1 - x0, y1 - y0
    k = Kit()
    with k.at(x0, y0, z0):
        # electric knife sharpener at the back right
        with k.at(W - 2.0, D - 3.6, 0.0):
            k.cbox("black_plastic", 0, 0, 0, 2.8, 6.4, 1.2, bevel=0.3)
            k.cbox("chrome", 0, -0.3, 1.2, 2.5, 5.0, 1.3, bevel=0.5)
            for i in range(3):
                k.cbox("black_plastic", 0, -1.6 + i * 1.3, 2.45, 2.2, 0.25, 0.08)
        # blue towel folded flat under everything
        k.blob("towel", 4.7, 7.5, 0.6, 8.6, 12.0, 1.2, cuts=3, amp=0.12, seed=11)
        # square black pot holder at the back left, leaning on the back items, red trim
        with k.at(2.6, 15.8, 1.6, rx=-28):
            k.rrect("potholder", 0, 0, 4.2, 6.0, 0.5, 0, 0.3)
            k.rrect("trim_red", 0, -2.9, 4.2, 0.5, 0.2, -0.05, 0.35)
        # round black pot holder with red trim, tilted on the towel
        with k.at(4.8, 10.2, 2.7, rx=-16, ry=4):
            k.cyl("potholder", POTHOLDER_R - 0.2, 0, 0.3, seg=16)
            k.lathe("trim_red", [(POTHOLDER_R - 0.25, -0.05), (POTHOLDER_R, 0.05),
                                 (POTHOLDER_R, 0.3), (POTHOLDER_R - 0.25, 0.4)], seg=16, closed=True)
            k.blob("trim_red", 0, -POTHOLDER_R - 0.3, 0.15, 0.9, 0.8, 0.3, cuts=1, amp=0.05)
        # two cream oven gloves with the blue stripe print at the front
        with k.at(2.6, 5.8, 1.0, rz=4):
            glove(k, "glove", 21, fingers=True, thumb_side=1)
        with k.at(7.0, 5.6, 1.4, rz=-4, ry=6):
            glove(k, "glove_b", 31, fingers=False, thumb_side=-1)
    return k.obj("kitchen_cabinets_drawer_d3_contents", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))


def d4(coll):
    x0, x1, y0, y1, z0, z1 = _drawer_frame("d4")
    W, D = x1 - x0, y1 - y0
    k = Kit()
    with k.at(x0, y0, z0):
        # big trash-bag roll across the back left, drawstring end to the right
        with k.at(0.6, 15.5, 2.0, ry=90):
            k.lathe("trash_roll", [(2.0, 0), (2.0, 6.0)], seg=12)
            k.lathe("trash_yellow", [(2.0, 6.0), (2.05, 7.2), (0.01, 7.25)], seg=12)
        # white bags/paper behind it
        k.blob("trash_white", 4.2, D - 1.8, 1.5, 6.5, 2.8, 3.0, cuts=2, amp=0.2, seed=41)
        # two smaller rolls lying front to back on the left, yellow ends at the front
        for i, u in enumerate((1.5, 4.3)):
            with k.at(u, 0.7, 1.35, rx=-90, rz=0):
                k.lathe("trash_yellow", [(0.01, -0.05), (1.35, 0.0), (1.35, 1.6)], seg=10)
                k.lathe("trash_roll", [(1.35, 1.6), (1.35, 8.4 - i * 0.6)], seg=10)
        # crumpled white bags in the middle
        for i, (u, v, sx, sy, sz) in enumerate(((6.7, 2.6, 2.6, 3.8, 2.6), (6.1, 6.0, 3.0, 3.6, 3.2),
                                                (6.6, 9.4, 2.8, 3.6, 2.4))):
            k.blob("trash_white", u, v, sz / 2 + 0.1, sx, sy, sz, cuts=2, amp=0.4, seed=43 + i, freq=2.2, sq=0.1)
        # zip-bag box lying flat on the right, red end at the front
        with k.at(W - 1.7, 6.2, 0.0, rz=90):
            k.cbox("zip_box", 0, 0, 0, 9.4, 2.7, 3.4, bevel=0.04)
        # grey mesh/foil wad at the back right
        k.blob("foil", W - 2.0, 15.5, 1.85, 3.2, 4.5, 3.0, cuts=2, amp=0.3, seed=47, freq=2.0)
    return k.obj("kitchen_cabinets_drawer_d4_contents", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))


def fork(k, u0, v0, u1, v1, w, tilt=0):
    utensil(k, u0, v0, u1, v1, w, "steel", "steel", "fork", 2.6, 1.0, handle_w=0.5, handle_t=0.12,
            tilt=tilt)


def spoon(k, u0, v0, u1, v1, w, big=False, tilt=0):
    utensil(k, u0, v0, u1, v1, w, "steel", "steel", "spoon", 2.8 if big else 2.4,
            1.6 if big else 1.35, handle_w=0.5, handle_t=0.12, tilt=tilt)


def knife(k, u0, v0, u1, v1, w, tilt=0):
    utensil(k, u0, v0, u1, v1, w, "steel", "steel", "knife", 4.0, 0.8, handle_w=0.55, handle_t=0.2,
            tilt=tilt)


def ed(coll):
    x0, x1, y0, y1, z0, z1 = _drawer_frame("ed")
    W, D = x1 - x0, y1 - y0
    k = Kit()
    tw, td, th = TRAY
    tu0, tv0 = 0.6, 0.8
    with k.at(x0, y0, z0):
        # cutlery tray: grey floor, dark walls, five front slots and a long back slot
        with k.at(tu0, tv0, 0.0):
            t = 0.2
            k.box("tray_light", 0.1, tw - 0.1, 0.1, td - 0.1, 0, 0.15)
            k.box("tray_dark", 0, tw, 0, td, -0.0, 0.1)
            for a, b in ((0, t), (tw - t, tw)):
                k.box("tray_dark", a, b, 0, td, 0, th, bevel=0.06)
            for a, b in ((0, t), (td - t, td), (11.6, 11.6 + t)):
                k.box("tray_dark", 0, tw, a, b, 0, th, bevel=0.06)
            edges = [0, 2.9, 5.8, 8.3, 11.4, tw]
            for e in edges[1:-1]:
                k.box("tray_dark", e - t / 2, e + t / 2, 0, 11.6, 0, th - 0.15, bevel=0.06)
            # the plain middle slot's raised centre with an oval pad
            k.box("tray_light", 6.1, 8.0, 0.4, 11.2, 0.15, 0.35)
            # slot 1: forks; slot 2: spoons; slot 4: soup spoons; slot 5: knives
            for i in range(4):
                fork(k, 0.9 + i * 0.35, 0.8 + i * 0.6, 1.3 + i * 0.25, 9.6 + i * 0.6, 0.2 + i * 0.13)
            for i in range(3):
                spoon(k, 3.9 + i * 0.4, 0.9 + i * 0.4, 3.7 + i * 0.4, 9.8 - i * 0.6, 0.2 + i * 0.14)
            for i in range(6):
                spoon(k, 9.6 + i * 0.1, 0.8, 9.3 + i * 0.12, 10.4 - i * 0.05, 0.2 + i * 0.16, big=True)
            for i in range(4):
                knife(k, 12.4 + i * 0.25, 0.8 + i * 0.3, 12.6 - i * 0.3, 11.2, 0.2 + i * 0.15)
            # back slot: cream serving spoons, white soup spoon, black chopsticks
            for i, (a, b) in enumerate(((1.0, 13.6), (5.0, 12.6))):
                utensil(k, a + 7.0, b + 0.8 + i * 0.6, a, b + 1.6, 0.4 + i * 0.5, "cream_plastic",
                        "cream_plastic", "spoon", 3.6, 2.6, handle_w=0.7, handle_t=0.25)
            with k.at(4.2, 14.5, 0.7, rz=170):
                k.lathe("ceramic", [(0.01, -0.2), (0.8, 0.0), (0.9, 0.5), (0.75, 0.5), (0.01, 0.0)],
                        seg=10, oval=(1.6, 1.0))
                k.box("ceramic", 1.2, 4.0, -0.3, 0.3, 0.2, 0.45)
            for i in range(2):
                with k.seg(0.6, 13.0 + i * 0.4, 9.5, 14.6 + i * 0.3, 0.2 + i * 0.2):
                    k.box("black_plastic", 0, 8.9, -0.15, 0.15, -0.15, 0.15)
        # right of the tray: mint-capped tape roll and a white lid
        with k.at(W - 1.4, D - 3.6, 0.0):
            k.cyl("tan", 1.15, 0, 2.6, seg=10)
            k.cyl("mint", 1.25, 2.6, 0.9, seg=10)
            k.cyl("black_plastic", 0.35, 3.5, 0.3, seg=6)
        with k.at(W - 2.6, D - 1.3, 1.35, rx=70):
            k.cyl("white_lid", 1.3, -0.25, 0.5, seg=10)
    return k.obj("kitchen_cabinets_drawer_ed_contents", coll, ((x0 + x1) / 2, (y0 + y1) / 2, z0))


# --- build / texture --------------------------------------------------------------------------

def _check(objs):
    """Report each object's plan-inch bounds; drawer contents must stay inside the drawer."""
    bpy.context.view_layer.update()
    for ob in objs:
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        lo = [min(p[i] for p in pts) / IN for i in range(3)]
        hi = [max(p[i] for p in pts) / IN for i in range(3)]
        print(f"{ob.name}: x {lo[0]:.2f}-{hi[0]:.2f} y {lo[1]:.2f}-{hi[1]:.2f} z {lo[2]:.2f}-{hi[2]:.2f}")
        for did, d in INT.DRAWERS.items():
            if ob.name == f"kitchen_cabinets_drawer_{did}_contents":
                (ax0, ax1), (ay0, ay1), (az0, az1) = d["x"], d["y"], d["z"]
                tol = 0.1      # a hair into a wall or the floor is invisible; the top is strict
                bad = (lo[0] < ax0 - tol or hi[0] > ax1 + tol or lo[1] < ay0 - tol
                       or hi[1] > ay1 + tol or lo[2] < az0 - tol or hi[2] > az1 - 0.05)
                print("   inside drawer", did, (ax0, ax1), (ay0, ay1), (az0, az1),
                      "OVERFLOW" if bad else "ok")
                if bad:
                    for i, (a0, a1) in enumerate(((ax0, ax1), (ay0, ay1), (az0, az1 - 0.05))):
                        for p in pts:
                            q = p[i] / IN
                            if q < a0 - 0.1 or q > a1 + (0.1 if i < 2 else 0.0):
                                print("      axis", "xyz"[i], "at", [round(c / IN, 2) for c in p])
                                break


def build(coll):
    objs = [sink(coll), corner(coll), eb(coll), d1(coll), d2(coll), d3(coll), d4(coll), ed(coll)]
    _check(objs)
    return objs


def _island_uvs(ob, regions):
    """Per connected piece of each painted region, box-project every face onto the whole
    region rect using that piece's own bounds (as kitchen_cabinets._island_uvs)."""
    me = ob.data
    names = [mm.name.split(".")[0] for mm in me.materials]
    uvl = me.uv_layers["UVMap"]
    for region in regions:
        if region not in names:
            continue
        ri = names.index(region)
        polys = [p for p in me.polygons if p.material_index == ri]
        parent = {}

        def find(a):
            parent.setdefault(a, a)
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        for p in polys:
            r0 = find(p.vertices[0])
            for v in p.vertices[1:]:
                rv = find(v)
                if rv != r0:
                    parent[rv] = r0
        groups = {}
        for p in polys:
            groups.setdefault(find(p.vertices[0]), []).append(p)
        u0, v0, u1, v1 = common.uv_rect(ATLAS, region)
        for ps in groups.values():
            vids = {v for p in ps for v in p.vertices}
            rng = {}
            for p in ps:
                n = p.normal
                ax = max(range(3), key=lambda i: abs(n[i]))
                key = ("+" if n[ax] > 0 else "-") + "XYZ"[ax]
                ua, va = map(Vector, common._axes(key))
                if key not in rng:
                    us = [me.vertices[v].co.dot(ua) for v in vids]
                    vs = [me.vertices[v].co.dot(va) for v in vids]
                    rng[key] = (min(us), max(us) - min(us) or 1e-6, min(vs), max(vs) - min(vs) or 1e-6)
                umin, ur, vmin, vr = rng[key]
                for li in p.loop_indices:
                    co = me.vertices[me.loops[li].vertex_index].co
                    fu, fv = (co.dot(ua) - umin) / ur, (co.dot(va) - vmin) / vr
                    uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def _topdown_uvs(ob, regions):
    """Project each region's faces straight down onto its whole rect, over that region's
    XY bounds in the object (image up = +y, the glove's finger end)."""
    me = ob.data
    names = [mm.name.split(".")[0] for mm in me.materials]
    uvl = me.uv_layers["UVMap"]
    for region in regions:
        if region not in names:
            continue
        ri = names.index(region)
        polys = [p for p in me.polygons if p.material_index == ri]
        if not polys:
            continue
        vs = [me.vertices[v].co for p in polys for v in p.vertices]
        x0, x1 = min(v.x for v in vs), max(v.x for v in vs)
        y0, y1 = min(v.y for v in vs), max(v.y for v in vs)
        u0, v0, u1, v1 = common.uv_rect(ATLAS, region)
        for p in polys:
            for li in p.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                fu, fv = (co.x - x0) / (x1 - x0), (co.y - y0) / (y1 - y0)
                uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    clear = common.atlas_material(NAME + "_clear", ATLAS)
    # preview only: show the glass and clear plastic as see-through in the Blender renders
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    for ob in objs:
        common.atlas_uvs(ob, ATLAS)
        _island_uvs(ob, PAINTED)
        _topdown_uvs(ob, TOPDOWN)
        common.collapse_materials(ob, {r: (clear if r in CLEAR_REGIONS else mat) for r in REGIONS})
        me = ob.data
        used = {p.material_index for p in me.polygons}
        for i in reversed(range(len(me.materials))):
            if i not in used and i == len(me.materials) - 1:
                me.materials.pop(index=i)
