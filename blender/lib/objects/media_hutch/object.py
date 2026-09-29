"""Media hutch: the dark stained-pine bookcase in the living room's SE corner, with
everything on it. Lower section: two raised-panel doors and two drawers with brass bail
pulls; above them three open shelf bays, a scalloped arched valance over the top bay with a
rounded bead along the arch, and a stepped crown. On the shelves, each thing is its own
shape at its place in IMG_1506: parody board-game boxes stacked as in the photo, upright
parody books, the two feathered masks (fan of feather cards), the twisted cream lamp and
its cord, the glass vase in its black holder, the tarot deck, papers, notebook, magazines,
the postcard, two batteries, the wire spider and the little critter. On top (IMG_1507/1508):
two game stacks, the silver aluminium case, the pink woven box and the conical woven hat.
On the north (-X) side panel: the resistor colour-code chart and Cassidy's red linocut print.

Source of truth: scripted. Overall size from the living-room LiDAR survey (registered.npz,
layout inches); internal layout and every item from IMG_1506 (front), IMG_1507 (top, front),
IMG_1508 (north side) and the survey crops. All numbers live in layout.py with provenance.
Origin on the floor at the footprint centre; front faces -Y; +X is the hutch's right.
Place at plan (124.75, 17.75), rotation -90 (front faces west): the back sits on the center
wall face (x 134), the -X side faces north into the room.

Textures: media_hutch (2048, drawn from scratch: wood, parody box art, spines, chart) and
media_hutch_art (512, the linocut rectified from IMG_1508 with its QR code replaced; kept
out of git). The vase glass has its own transparent material.

The cassette player and its case are a separate package (cassette_player). This file
exports a `place_cassette_player` marker empty where they rest (front left of the bottom
bay, yaw -12 deg).
"""

import importlib.util
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

import common
from atlas_layout import uv_rect

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("media_hutch_layout", os.path.join(_HERE, "layout.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

IN = 0.0254


def m(v):
    return v * IN


NAME = "media_hutch"
ATLAS = L.ATLAS
ART_ATLAS = L.ART_ATLAS
ART_REGIONS = list(ART_ATLAS["regions"])
REGIONS = list(ATLAS["regions"]) + ART_REGIONS
GLASS_ALPHA = 0.22
MATERIALS = {
    "media_hutch": {"atlas": "media_hutch", "mode": "opaque", "tiled": False},
    "media_hutch_art": {"atlas": "media_hutch_art", "mode": "opaque", "tiled": False},
    "media_hutch_glass": {"atlas": "media_hutch", "mode": "transparent", "alpha": GLASS_ALPHA,
                          "tiled": False},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front", 0, 6, 0.62), ("north_side", 280, 8, 0.75),
         ("front_high", 0, 30, 0.7), ("bay_close", 12, 10, 0.4)]

# cassette player resting place, hutch frame (inches, degrees)
CASSETTE_PLACE = (-8.0, -6.55, L.RAIL_TOP, -12.0)

# physical size (across, along the grain) that each wood region represents, inches
WOOD_PHYS = {"wood": (16.0, 34.0), "wood_dark": (8.0, 16.0), "wood_edge": (2.0, 8.0),
             "interior": (24.0, 24.0), "straw": (14.0, 14.0)}

# per-face UV axes in the part's local frame: dir -> ((axis, sign) for u, (axis, sign) for v)
FACE_AXES = {"mY": ((0, 1), (2, 1)), "pY": ((0, -1), (2, 1)), "mX": ((1, -1), (2, 1)),
             "pX": ((1, 1), (2, 1)), "pZ": ((0, 1), (1, 1)), "mZ": ((0, 1), (1, -1))}


def _dir(n):
    ax = max(range(3), key=lambda i: abs(n[i]))
    return ("m" if n[ax] < 0 else "p") + "XYZ"[ax]


class Hutch:
    """common.Builder plus per-part UV specs (a face int layer records the part)."""

    def __init__(self):
        self.b = common.Builder(REGIONS)
        self.bm = self.b.bm
        self.layer = self.bm.faces.layers.int.new("part")
        self.parts = [None]

    def _claim(self, region, mode="fit", grain=None, R=None, c=None, art=None, uvbox=None):
        pid = len(self.parts)
        self.parts.append({"region": region, "mode": mode, "grain": grain,
                           "R": R or Matrix.Identity(3), "c": c or Vector((0, 0, 0)),
                           "art": art or {}, "uvbox": uvbox})
        for f in self.bm.faces:
            if f[self.layer] == 0:
                f[self.layer] = pid
        return pid

    # --- primitives, inches in, metres in the mesh ---------------------------------------
    def box(self, region, lo, hi, bevel=0.0, yaw=0.0, art=None, mode="fit", grain=None,
            uvbox=None, rot=None):
        lo_m, hi_m = Vector(map(m, lo)), Vector(map(m, hi))
        c = (lo_m + hi_m) / 2
        R = Matrix.Identity(3)
        mat = None
        if yaw:
            R = Matrix.Rotation(math.radians(yaw), 3, "Z")
        if rot is not None:          # (pivot inches, 3x3 rotation)
            piv, Rr = rot
            piv = Vector(map(m, piv))
            R = Rr @ R
            mat = Matrix.Translation(piv) @ Rr.to_4x4() @ Matrix.Translation(-piv) @ \
                Matrix.Translation(c) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Translation(-c)
            c = piv + Rr @ (c - piv)
        elif yaw:
            mat = Matrix.Translation(c) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ Matrix.Translation(-c)
        self.b.box(region, lo_m, hi_m, bevel=m(bevel), matrix=mat,
                   segments=2 if region in ("brass", "chrome") else 1)
        if uvbox is not None:
            uvbox = (Vector(map(m, uvbox[0])) - c, Vector(map(m, uvbox[1])) - c)
        return self._claim(region, mode, grain, R, c, art, uvbox)

    def cyl(self, region, center, r, depth, axis="Z", segments=12, cap_region=None, mode="fit"):
        self.b.cylinder(region, Vector(map(m, center)), m(r), m(depth), axis=axis,
                        segments=segments, cap_region=cap_region)
        return self._claim(region, mode, c=Vector(map(m, center)))

    def sweep(self, region, pts, profile, up=(0, 0, 1), closed=False):
        self.b.sweep(region, [tuple(map(m, p)) for p in pts],
                     [(m(a), m(b)) for a, b in profile], up=up, closed=closed)
        return self._claim(region)

    def card(self, region, outline, thick, M, art_region=None):
        """Flat shape: outline [(u, v)] inches in the card plane, `thick` inches, placed by
        M (4x4, inches). Both faces map `art_region` (or region) over the outline bounds."""
        faces = self.b.prism(region, [(m(u), m(v)) for u, v in outline], -m(thick) / 2, m(thick) / 2)
        verts = {v for f in faces for v in f.verts}
        Mm = M.copy()
        Mm.translation = Vector(map(m, M.translation))
        bmesh.ops.transform(self.bm, matrix=Mm, verts=list(verts))
        art = {"pZ": art_region or region, "mZ": art_region or region}
        return self._claim(region, "fit", R=Mm.to_3x3().normalized(), c=Mm.translation.copy(), art=art)

    def rings(self, region, rings, closed_ends=(True, True), mode="fit", loop=False):
        """Loft through rings of points (inches), each ring the same count, quads between."""
        vs = [[self.bm.verts.new(tuple(map(m, p))) for p in ring] for ring in rings]
        n = len(vs[0])
        for a, b in zip(vs, vs[1:] + (vs[:1] if loop else [])):
            for j in range(n):
                self.bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
        if closed_ends[0] and not loop:
            self.bm.faces.new(list(reversed(vs[0])))
        if closed_ends[1] and not loop:
            self.bm.faces.new(vs[-1])
        idx = self.b.idx(region)
        for f in self.bm.faces:
            if f[self.layer] == 0:
                f.material_index = idx
        return self._claim(region, mode)

    # --- UVs --------------------------------------------------------------------------------
    def finish(self, coll):
        bm = self.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        ngons = [f for f in bm.faces if len(f.verts) > 4]
        if ngons:
            bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.normal_update()
        uvl = bm.loops.layers.uv.new("UVMap")
        by_part = {}
        for f in bm.faces:
            by_part.setdefault(f[self.layer], []).append(f)
        for pid, faces in by_part.items():
            self._uv_part(self.parts[pid], faces, uvl, pid)
        return self.b.to_object(NAME, coll)

    def _uv_part(self, spec, faces, uvl, pid):
        Rt = spec["R"].transposed()
        c = spec["c"]
        loc = {}
        for f in faces:
            for v in f.verts:
                if v not in loc:
                    loc[v] = Rt @ (v.co - c)
        if spec["uvbox"]:
            lo, hi = spec["uvbox"]
        else:
            pts = list(loc.values())
            lo = Vector([min(p[i] for p in pts) for i in range(3)])
            hi = Vector([max(p[i] for p in pts) for i in range(3)])
        ext = [max(hi[i] - lo[i], 1e-6) for i in range(3)]
        rng = L.seeded(f"part{pid}")
        offs = {}
        for f in faces:
            d = _dir(Rt @ f.normal)
            region = spec["art"].get(d)
            if region is not None:
                f.material_index = self.b.idx(region)
            else:
                region = spec["region"]
            atlas = ART_ATLAS if region in ART_REGIONS else ATLAS
            u0, v0, u1, v1 = uv_rect(atlas, region)
            (ua, us), (va, vs) = FACE_AXES[d]
            wood = spec["mode"] == "wood" and region in WOOD_PHYS and region not in spec["art"].values()
            if wood:
                g = "xyz".index(spec["grain"]) if spec["grain"] else None
                if g not in (ua, va):
                    g = ua if ext[ua] > ext[va] else va
                a = va if g == ua else ua
                across, along = WOOD_PHYS[region]
                su = min(1.0, ext[a] / m(across))
                sv = min(1.0, ext[g] / m(along))
                key = (d, a, g)
                if key not in offs:
                    offs[key] = (rng.random() * (1 - su), rng.random() * (1 - sv))
                ou, ov = offs[key]
            for lp in f.loops:
                p = loc[lp.vert]
                if wood:
                    fu = ou + su * (p[a] - lo[a]) / ext[a]
                    fv = ov + sv * (p[g] - lo[g]) / ext[g]
                else:
                    fu = (p[ua] - lo[ua]) / ext[ua]
                    fv = (p[va] - lo[va]) / ext[va]
                    if us < 0:
                        fu = 1 - fu
                    if vs < 0:
                        fv = 1 - fv
                fu = min(max(fu, 0.0), 1.0)
                fv = min(max(fv, 0.0), 1.0)
                lp[uvl].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))


# --- the hutch ------------------------------------------------------------------------------

def carcass(h):
    X0, X1, Y0, Y1, FY = L.X0, L.X1, L.Y0, L.Y1, L.FY
    IX0, IX1, INX0, INX1, BACK = L.IX0, L.IX1, L.INX0, L.INX1, L.BACK_Y
    VT, RT, LT, BH = L.VAL_TOP, L.RAIL_TOP, L.LOWER_TOP, L.BASE_H
    wz = dict(mode="wood", grain="z")
    wx = dict(mode="wood", grain="x")
    # side panels (the -X one faces the room), back, bay floors, shelves, top
    h.box("wood", (X0, FY, 0.0), (X0 + L.SIDE_T, Y1, VT), **wz)
    h.box("wood", (X1 - L.SIDE_T, FY, 0.0), (X1, Y1, VT), **wz)
    h.box("interior", (INX0, BACK, BH), (INX1, Y1, VT), mode="wood", grain="z")
    h.box("wood", (INX0, FY, RT - 0.75), (INX1, BACK, RT), **wx)
    for z in L.SHELVES:
        h.box("wood", (INX0, FY, z - 0.75), (INX1, BACK, z), **wx)
        h.box("wood", (IX0, Y0 + 0.2, z - 1.4), (IX1, FY + 0.6, z), bevel=0.12, **wx)
    h.box("interior", (INX0, FY, VT - 0.75), (INX1, BACK, VT), **wx)
    # plinth and base moulding (front and both sides)
    h.box("wood", (X0 - 0.2, Y0 - 0.2, 0.0), (X1 + 0.2, Y1, BH - 0.7), **wx)
    h.box("wood_dark", (X0 - 0.5, Y0 - 0.5, BH - 1.0), (X1 + 0.5, Y1, BH - 0.35), bevel=0.25, **wx)
    h.box("wood", (X0 - 0.3, Y0 - 0.3, BH - 0.4), (X1 + 0.3, Y1, BH), bevel=0.12, **wx)
    # face frame: stiles, centre stile below, rails
    h.box("wood", (X0, Y0, BH), (IX0, FY, VT), bevel=0.1, **wz)
    h.box("wood", (IX1, Y0, BH), (X1, FY, VT), bevel=0.1, **wz)
    h.box("wood", (-0.75, Y0, BH), (0.75, FY, RT - 1.5), bevel=0.08, **wz)
    h.box("wood", (IX0, Y0, BH), (IX1, FY, BH + 0.8), **wx)
    h.box("wood", (IX0, Y0, LT - 0.4), (IX1, FY, LT + 0.35), **wx)
    h.box("wood", (IX0, Y0 - 0.3, RT - 1.5), (IX1, FY, RT), bevel=0.2, **wx)
    # drawers: overlay fronts with a brass bail pull each
    for sgn in (-1, 1):
        a0, a1 = (IX0, -0.75) if sgn < 0 else (0.75, IX1)
        z0, z1 = LT + 0.45, RT - 1.65
        h.box("wood", (a0 + 0.1, Y0 - 0.7, z0), (a1 - 0.1, Y0 + 0.05, z1), bevel=0.25, **wx)
        cx, cz = (a0 + a1) / 2, (z0 + z1) / 2 + 0.2
        drawer_pull(h, cx, Y0 - 0.7, cz)
    # doors: stile-and-rail frame, raised panel, brass knob
    for sgn in (-1, 1):
        a0, a1 = (IX0, -0.75) if sgn < 0 else (0.75, IX1)
        a0, a1 = a0 + 0.1, a1 - 0.1
        z0, z1 = BH + 0.9, LT - 0.5
        dy0, dy1 = Y0 - 0.75, Y0 + 0.02
        f = 2.3
        h.box("wood", (a0, dy0, z0), (a1, dy1, z0 + f), bevel=0.1, **wx)
        h.box("wood", (a0, dy0, z1 - f), (a1, dy1, z1), bevel=0.1, **wx)
        h.box("wood", (a0, dy0, z0 + f), (a0 + f, dy1, z1 - f), bevel=0.1, **wz)
        h.box("wood", (a1 - f, dy0, z0 + f), (a1, dy1, z1 - f), bevel=0.1, **wz)
        h.box("wood", (a0 + f, dy0 + 0.3, z0 + f), (a1 - f, dy1, z1 - f), bevel=0.45, **wz)
        # moulded sticking round the panel, its finish rubbed lighter (orange in the photos)
        s = 0.4
        h.box("wood_edge", (a0 + f - s, dy0 + 0.02, z0 + f - s), (a1 - f + s, dy0 + 0.3, z0 + f), bevel=0.12, **wx)
        h.box("wood_edge", (a0 + f - s, dy0 + 0.02, z1 - f), (a1 - f + s, dy0 + 0.3, z1 - f + s), bevel=0.12, **wx)
        h.box("wood_edge", (a0 + f - s, dy0 + 0.02, z0 + f), (a0 + f, dy0 + 0.3, z1 - f), bevel=0.12, **wz)
        h.box("wood_edge", (a1 - f, dy0 + 0.02, z0 + f), (a1 - f + s, dy0 + 0.3, z1 - f), bevel=0.12, **wz)
        kx = a1 - 1.0 if sgn < 0 else a0 + 1.0
        door_latch(h, kx, dy0, z1 - L.DOOR_LATCH_DOWN)
    # scalloped valance: strips under the arch, continuous grain, and the rounded bead
    pts = L.arch_points()
    zmin = min(z for _x, z in pts)
    ub = ((IX0, Y0, zmin), (IX1, FY, VT))
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        outline = [(xa, za), (xb, zb), (xb, VT), (xa, VT)]
        faces = h.b.prism("wood", [(m(x), m(z)) for x, z in outline], 0.0, m(FY - Y0))
        verts = {v for f in faces for v in f.verts}
        for v in verts:
            x, zz, yy = v.co
            v.co = Vector((x, m(Y0) + yy, zz))
        h._claim("wood", "wood", "x", uvbox=(Vector(map(m, ub[0])), Vector(map(m, ub[1]))))
    bead = [(x, Y0 - 0.12, z + 0.05) for x, z in pts]
    bead = [(IX0 - 0.05, Y0 - 0.12, pts[0][1] - 0.6)] + bead + [(IX1 + 0.05, Y0 - 0.12, pts[-1][1] - 0.6)]
    h.sweep("wood_edge", bead, [(0.32 * math.cos(a), 0.3 * math.sin(a)) for a in
                                (math.radians(d) for d in (0, 60, 120, 180, 240, 300))], up=(0, -1, 0))
    # stepped crown: bead, cove steps, cap
    z = VT
    for dz, o, bev, reg in ((0.5, 0.3, 0.2, "wood_dark"), (0.6, 0.55, 0.15, "wood"),
                            (0.9, 0.95, 0.3, "wood_dark"), (0.9, 1.4, 0.3, "wood_dark"),
                            (0.7, 1.7, 0.25, "wood"), (L.H - VT - 3.6, 1.95, 0.3, "wood")):
        h.box(reg, (X0 - o, Y0 - o, z), (X1 + o, Y1, z + dz), bevel=bev, **wx)
        z += dz
    # paper on the -X side panel: the chart and the linocut print
    y0, y1, z0, z1 = L.CHART
    h.box("paper_white", (X0 - 0.03, y0, z0), (X0 - 0.005, y1, z1), art={"mX": "chart"})
    y0, y1, z0, z1 = L.PRINT
    h.box("paper_white", (X0 - 0.03, y0, z0), (X0 - 0.005, y1, z1), art={"mX": "print"})


# --- brass hardware (frame 003528-003541 of the living capture, lower section) ------------
# Drawer pull: a cast Chippendale "batwing" backplate with a swan-neck bail hanging from two
# posts. Door latch: a small upright scrolled escutcheon plate with a knob, near each
# door's meeting edge. Right halves (x >= 0), inches, centred; PHOTO proportions against the
# drawer width, EST sizes.
BATWING_HALF = [(0.0, 0.58), (0.3, 0.72), (0.62, 0.56), (0.98, 0.56), (1.34, 0.66), (1.66, 0.8),
                (1.92, 0.62), (1.8, 0.28), (1.92, -0.08), (1.7, -0.42), (1.3, -0.36), (0.9, -0.52),
                (0.45, -0.7), (0.0, -0.6)]
LATCH_HALF = [(0.0, 1.12), (0.16, 1.02), (0.24, 0.82), (0.38, 0.66), (0.3, 0.38), (0.24, 0.0),
              (0.3, -0.38), (0.38, -0.66), (0.24, -0.82), (0.16, -1.02), (0.0, -1.12)]


def _mirror(half):
    """Full CCW outline from a right half listed top to bottom."""
    left = [(-x, y) for x, y in half[1:-1]]
    return list(reversed(half)) + left


def plate(h, region, outline, thick, cx, yf, cz, scale=1.0):
    """Flat cast plate standing on the front plane y = yf: outline (x, z) inches, star-shaped
    about its centre, so each face is a centre fan (the concave scallops would otherwise
    triangulate across themselves)."""
    bm = h.bm
    idx = h.b.idx(region)
    front, back = [], []
    for x, z in outline:
        front.append(bm.verts.new((m(cx + x * scale), m(yf - thick), m(cz + z * scale))))
        back.append(bm.verts.new((m(cx + x * scale), m(yf), m(cz + z * scale))))
    cf = bm.verts.new((m(cx), m(yf - thick), m(cz)))
    cb = bm.verts.new((m(cx), m(yf), m(cz)))
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        for f in (bm.faces.new((front[i], cf, front[j])), bm.faces.new((back[j], cb, back[i])),
                  bm.faces.new((front[i], front[j], back[j], back[i]))):
            f.material_index = idx
    return h._claim(region)


def drawer_pull(h, cx, yf, cz):
    """Batwing backplate on the drawer face (front plane y = yf), posts, bail."""
    plate(h, "brass", _mirror(BATWING_HALF), 0.07, cx, yf, cz)
    y = yf - 0.07
    for sx in (-1, 1):
        h.cyl("brass", (cx + sx * 1.3, y - 0.14, cz + 0.12), 0.13, 0.28, axis="Y", segments=6)
        h.cyl("brass", (cx + sx * 1.3, y - 0.3, cz + 0.12), 0.2, 0.1, axis="Y", segments=8)
    half = [(1.3, y - 0.3, cz + 0.12), (1.5, y - 0.4, cz - 0.1), (1.35, y - 0.5, cz - 0.42),
            (0.95, y - 0.55, cz - 0.5), (0.5, y - 0.56, cz - 0.62)]
    bail = [(cx + x, yy, zz) for x, yy, zz in half] +         [(cx - x, yy, zz) for x, yy, zz in reversed(half)]
    h.sweep("brass", common.smooth_path(bail, 2), common.circle_profile(0.09, 5), up=(0, -1, 0))


def door_latch(h, cx, yf, cz):
    """Scrolled escutcheon plate with a small knob."""
    plate(h, "brass", _mirror(LATCH_HALF), 0.06, cx, yf, cz, scale=1.25)
    h.cyl("brass", (cx, yf - 0.2, cz + 0.25), 0.1, 0.3, axis="Y", segments=6)
    h.cyl("brass", (cx, yf - 0.38, cz + 0.25), 0.22, 0.16, axis="Y", segments=8)


def boxes(h):
    for bid, (x0, x1, y0, y1, z0, hh, yaw, faces, _col) in L.BOXES.items():
        art = {f: f"a_{bid}_{f}" for f in faces}
        h.box(f"c_{bid}", (x0, y0, z0), (x1, y1, z0 + hh), yaw=yaw, art=art)


def books(h):
    for bk, (x0, x1, sy, d, z0, hh, _col, lean) in L.BOOKS.items():
        art = {"mY": f"s_{bk}", "pZ": "paper_cream", "pY": "paper_cream"}
        rot = None
        if lean:
            rot = ((x1, sy, z0), Matrix.Rotation(math.radians(lean), 3, "Y"))
        h.box(f"c_{bk}", (x0, sy, z0), (x1, sy + d, z0 + hh), art=art, rot=rot)


def _plane(origin, yaw, tilt, roll=0.0):
    """Card frame: card u along the plane's right, v up, normal toward -Y before yaw.
    tilt leans the top back (+Y), yaw turns about Z; inches."""
    M = (Matrix.Translation(origin) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
         @ Matrix.Rotation(math.radians(90 - tilt), 4, "X") @ Matrix.Rotation(math.radians(roll), 4, "Z"))
    return M


def feather(length, width):
    w = width / 2
    return [(0.0, 0.0), (w * 0.8, length * 0.3), (w * 0.6, length * 0.85), (0.0, length),
            (-w, length * 0.6), (-w * 0.6, length * 0.15)]


def _at(base, right, up, front, spin=0.0):
    """Offset inside a card frame (right, up, toward the front), then spin about the normal."""
    return base @ Matrix.Translation((right, up, front)) @ Matrix.Rotation(math.radians(spin), 4, "Z")


def masks(h):
    B1 = L.SHELVES[1]
    rng = L.seeded("masks")
    # big feathered mask propped against the books, leaning back; feathers fan from a root
    base = _plane((-9.4, -2.6, B1 + 2.2), 0.0, 14.0)
    for i in range(7):                       # tall dark-red feathers at the back
        spin = -26 + i * 8 + rng.uniform(-3, 3)
        h.card("black", feather(rng.uniform(8.0, 9.6), 1.5), 0.04,
               _at(base, -1.0 + rng.uniform(-0.4, 0.4), 0.0, -0.35 - 0.02 * i, spin), "feather_red")
    for i in range(22):                      # the blue fan
        spin = -78 + i * (156 / 21) + rng.uniform(-3, 3)
        ln = 7.6 - 2.8 * abs(spin) / 80 + rng.uniform(-0.6, 0.6)
        h.card("black", feather(ln, rng.uniform(1.5, 2.0)), 0.04,
               _at(base, rng.uniform(-0.4, 0.4), 0.0, -0.1 + 0.01 * i, spin), "feather_blue")
    mask = [(-3.9, 0.9), (-3.2, 2.0), (-1.9, 2.5), (-0.6, 2.1), (0.0, 1.7), (0.6, 2.1),
            (1.9, 2.5), (3.2, 2.0), (3.9, 0.9), (3.4, -0.3), (2.1, -0.9), (0.9, -0.5),
            (0.0, -0.1), (-0.9, -0.5), (-2.1, -0.9), (-3.4, -0.3)]
    h.card("black", mask, 0.25, _at(base, 0.0, -1.3, 0.45), "mask_face")
    for i in range(16):                      # fluffy pale-blue feathers around the mask
        a = math.radians(i * 360 / 16 + rng.uniform(-8, 8))
        rx, ry = 3.3, 1.6
        h.card("black", feather(rng.uniform(2.2, 3.4), 1.6), 0.03,
               _at(base, -math.sin(a) * rx, -0.5 + math.cos(a) * ry, 0.3 + 0.005 * i, math.degrees(a)),
               "feather_light")
    # small holographic half mask lying against the right-hand books
    hm = [(-2.0, 0.3), (-1.6, 1.5), (-0.4, 2.0), (1.0, 1.9), (2.0, 1.2), (1.8, 0.2),
          (0.6, -0.5), (-0.8, -0.4)]
    h.card("black", hm, 0.06, _plane((-1.7, -1.2, B1 + 0.6), -8.0, 32.0, 12.0), "half_mask")


def lamp(h):
    """Twisted triangular column (cream, blue pattern) on bay 2, with its white cord."""
    B2 = L.SHELVES[0]
    cx, cy, r = 1.6, -4.2, 2.5
    rings = []
    n = 7
    for i in range(n):
        t = i / (n - 1)
        rot = math.radians(-20 + 70 * t)
        z = B2 + 0.35 + t * 9.4
        rr = r * (1 - 0.06 * math.sin(math.pi * t))
        rings.append([(cx + rr * math.cos(rot + k * 2 * math.pi / 3),
                       cy + rr * math.sin(rot + k * 2 * math.pi / 3), z) for k in range(3)])
    h.rings("lamp", rings)
    base = [[(cx + (r + 0.25) * math.cos(math.radians(-20) + k * 2 * math.pi / 3),
              cy + (r + 0.25) * math.sin(math.radians(-20) + k * 2 * math.pi / 3), z) for k in range(3)]
            for z in (B2, B2 + 0.35)]
    h.rings("white", base)
    # cord: from the lamp base, over the shelf edge, down in front of bay 3 and the drawer
    Y0 = L.Y0
    cord = [(cx + 0.6, cy - 1.6, B2 + 0.12), (3.0, -8.0, B2 + 0.12), (3.9, Y0 - 0.2, B2 - 0.3),
            (4.2, Y0 - 0.45, B2 - 3.0), (4.3, Y0 - 0.5, L.RAIL_TOP + 2.0),
            (4.5, Y0 - 0.55, L.RAIL_TOP - 1.0), (4.6, Y0 - 1.1, 27.2), (4.7, Y0 - 1.1, 24.0),
            (5.2, Y0 - 1.0, 12.0), (6.0, Y0 - 0.9, 0.2)]
    h.sweep("white", common.smooth_path(cord, 3), common.circle_profile(0.1, 4), up=(0, -1, 0))
    h.box("white", (4.25, Y0 - 1.5, 26.3), (5.05, Y0 - 0.7, 28.1), bevel=0.3)


def vase(h):
    B3 = L.RAIL_TOP
    cx, cy = -2.8, -5.4
    h.cyl("black", (cx, cy, B3 + 1.4), 2.5, 2.8, segments=16)
    prof_out = [(1.7, 0.05), (1.62, 2.4), (1.45, 4.4), (1.7, 6.4), (2.15, 8.1), (2.4, 8.95)]
    prof_in = [(2.3, 8.95), (2.05, 8.1), (1.6, 6.4), (1.35, 4.4), (1.52, 2.4), (1.6, 0.35)]
    seg = 12
    rings = []
    for rr, z in prof_out + prof_in:
        rings.append([(cx + rr * math.cos(2 * math.pi * k / seg), cy + rr * math.sin(2 * math.pi * k / seg),
                       B3 + 0.2 + z) for k in range(seg)])
    h.rings("glass", rings)


def critters(h):
    B2, B3 = L.SHELVES[0], L.RAIL_TOP
    # wire spider on bay 2: red body, silver head, eight wire legs
    sx, sy, sz = -2.6, -6.3, B2 + 1.3
    h.cyl("spider_red", (sx, sy, sz), 0.42, 0.5, segments=6)
    h.cyl("chrome", (sx - 0.5, sy - 0.3, sz), 0.25, 0.4, segments=6)
    for k in range(8):
        a = math.radians(20 + 45 * k)
        dx, dy = math.cos(a), math.sin(a)
        pts = [(sx, sy, sz), (sx + dx * 1.2, sy + dy * 1.0, sz + 0.5), (sx + dx * 2.3, sy + dy * 1.9, B2 + 0.05)]
        h.sweep("wire", pts, common.circle_profile(0.05, 3))
    # little dark critter on bay 3
    cx, cy, cz = 5.2, -7.2, B3 + 0.55
    rings = []
    for i, (fz, fr) in enumerate(((-0.5, 0.45), (-0.2, 0.95), (0.25, 0.9), (0.55, 0.45))):
        rings.append([(cx + 1.25 * fr * math.cos(2 * math.pi * k / 8), cy + 1.0 * fr * math.sin(2 * math.pi * k / 8),
                       cz + fz) for k in range(8)])
    h.rings("critter", rings)
    for k in range(8):
        a = math.radians(-60 + (k % 4) * 40 + (180 if k >= 4 else 0))
        dx, dy = math.cos(a), math.sin(a)
        pts = [(cx + dx * 0.9, cy + dy * 0.7, cz - 0.3), (cx + dx * 1.5, cy + dy * 1.2, B3 + 0.03)]
        h.sweep("wire", pts, common.circle_profile(0.03, 3))
    # two AA batteries lying in front of the wooden box
    for bx, by, yaw in ((6.3, -4.6, 8.0), (6.9, -5.4, -4.0)):
        pid = h.cyl("battery", (0, 0, 0), 0.28, 1.97, axis="X", segments=8)
        M = Matrix.Translation(Vector(map(m, (bx, by, B3 + 0.28)))) @ Matrix.Rotation(math.radians(yaw), 4, "Z")
        vs = {v for f in h.bm.faces if f[h.layer] == pid for v in f.verts}
        bmesh.ops.transform(h.bm, matrix=M, verts=list(vs))
        h.parts[pid]["R"] = M.to_3x3()
        h.parts[pid]["c"] = M.translation.copy()


def papers(h):
    B2, B3 = L.SHELVES[0], L.RAIL_TOP
    rng = L.seeded("papers")
    # bay 2: the folded newsletter bundle and the spiral notebook on the left stack
    h.box("paper_news", (-13.4, -6.2, B2 + 7.9), (-2.1, 3.0, B2 + 8.4), yaw=-1.0)
    h.box("notebook", (-13.8, -5.1, B2 + 8.4), (-4.8, 6.0, B2 + 9.7), yaw=0.8)
    # postcard lying at the front left of bay 2
    h.box("white", (-13.2, -8.3, B2), (-10.9, -6.7, B2 + 0.03), yaw=-7.0, art={"pZ": "postcard"})
    # bay 3: magazines piled on the left stack
    z = B3 + 7.2
    for i in range(7):
        t = 0.3 + rng.uniform(0.0, 0.15)
        jx, jy = rng.uniform(-0.5, 0.5), rng.uniform(-0.6, 0.4)
        h.box("magazines", (-12.3 + jx, -3.2 + jy, z), (-1.4 + jx, 5.6 + jy, z + t),
              yaw=rng.uniform(-3, 3))
        z += t


def top(h):
    T = L.H
    # silver aluminium case: body, corner guards, latches, handle
    x0, x1, y0, y1, hh = -0.7, 15.4, -9.6, -1.35, 2.75
    h.box("aluminium", (x0, y0, T), (x1, y1, T + hh), bevel=0.15)
    for cx in (x0, x1):
        for cz in (T, T + hh):
            h.box("chrome", (cx - 0.35, y0 - 0.12, cz - 0.35), (cx + 0.35, y0 + 0.6, cz + 0.35), bevel=0.12)
    for lx in (x0 + 2.6, x1 - 2.6):
        h.box("chrome", (lx - 0.6, y0 - 0.25, T + 0.7), (lx + 0.6, y0, T + 2.0), bevel=0.08)
    mid = (x0 + x1) / 2
    handle = [(mid - 2.2, y0 - 0.1, T + 1.6), (mid - 2.0, y0 - 0.55, T + 1.1),
              (mid - 1.2, y0 - 0.7, T + 0.75), (mid + 1.2, y0 - 0.7, T + 0.75),
              (mid + 2.0, y0 - 0.55, T + 1.1), (mid + 2.2, y0 - 0.1, T + 1.6)]
    h.sweep("chrome", handle, common.circle_profile(0.2, 6), up=(0, -1, 0))
    for hx in (mid - 2.2, mid + 2.2):
        h.box("chrome", (hx - 0.3, y0 - 0.15, T + 1.35), (hx + 0.3, y0, T + 1.85), bevel=0.05)
    # conical woven hat resting on the soup-bowl box, tipped slightly forward
    soup = L.BOXES["soup_bowl"]
    base_z = soup[4] + soup[5]
    # IMG_1507/1508: just behind the Battletuck box, tipped up on its north side so its
    # underside shows from the room
    hx, hy, R, Hh = -8.8, -1.0, 7.15, 5.0
    tilt = Matrix.Rotation(math.radians(18.0), 3, "Y") @ Matrix.Rotation(math.radians(-6.0), 3, "X")
    seg = 20
    out, inn = [], []
    for rr, zz in ((R, 0.0), (R * 0.5, Hh * 0.5), (0.25, Hh - 0.05)):
        out.append([(rr * math.cos(2 * math.pi * k / seg), rr * math.sin(2 * math.pi * k / seg), zz)
                    for k in range(seg)])
    for rr, zz in ((0.2, Hh - 0.35), (R * 0.5 - 0.1, Hh * 0.5 - 0.25), (R - 0.12, -0.1)):
        inn.append([(rr * math.cos(2 * math.pi * k / seg), rr * math.sin(2 * math.pi * k / seg), zz)
                    for k in range(seg)])
    ring_pts = [[tuple(Vector((hx, hy, base_z + 0.3 + R * math.sin(math.radians(18.0)) * 0.9)) + tilt @ Vector(p)) for p in ring]
                for ring in out + inn]
    h.rings("straw", ring_pts, mode="fit", loop=True)


def build(coll):
    h = Hutch()
    carcass(h)
    boxes(h)
    books(h)
    masks(h)
    lamp(h)
    vase(h)
    critters(h)
    papers(h)
    top(h)
    ob = h.finish(coll)
    x, y, z, yaw = CASSETTE_PLACE
    e = bpy.data.objects.new("place_cassette_player", None)
    e.empty_display_type = "ARROWS"
    e.empty_display_size = 0.05
    e.location = (m(x), m(y), m(z))
    e.rotation_euler = (0.0, 0.0, math.radians(yaw))
    coll.objects.link(e)
    return [ob, e]


def texture(objs):
    ob = objs[0]
    main = common.atlas_material(NAME, ATLAS)
    art = common.atlas_material("media_hutch_art", ART_ATLAS)
    glass = common.atlas_material("media_hutch_glass", ATLAS)
    bsdf = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = GLASS_ALPHA
    if hasattr(glass, "surface_render_method"):
        glass.surface_render_method = "BLENDED"
    else:
        glass.blend_method = "BLEND"
    slots = {r: (art if r in ART_REGIONS else glass if r == "glass" else main) for r in REGIONS}
    common.collapse_materials(ob, slots)
