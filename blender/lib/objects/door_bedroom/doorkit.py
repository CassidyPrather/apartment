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
into the mesh so the export stays at rotation zero.

The shell (shell.py) already draws the casings on both wall faces and leaves the reveal as
bare drywall, so these packages add the jamb liner, stops, leaf and hardware only.
"""

import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

import common

IN = 0.0254


def m(v):
    return v * IN


def mv(p):
    return tuple(m(c) for c in p)


# One shared 512 px atlas for every door package ("doors"); flat finishes only.
ATLAS = {
    "name": "doors",
    "size": 512,
    "regions": {
        "paint": (0, 0, 256, 256),        # white semi-gloss door/jamb paint
        "nickel": (256, 0, 128, 128),     # brushed nickel knobs, hinges
        "bronze": (384, 0, 128, 128),     # dark lever set (bedroom)
        "vinyl": (256, 128, 128, 128),    # patio door frame (white vinyl, EST)
        "dark": (384, 128, 128, 128),     # weatherstrip, track slots, pulls
        "glass": (0, 256, 128, 128),      # patio glazing (own transparent material)
        "aluminum": (128, 256, 128, 128),  # closet track
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


def builder():
    return common.Builder(REGIONS)


def box(b, region, lo, hi, bevel=0.0, segments=1, matrix=None):
    return b.box(region, mv(lo), mv(hi), bevel=m(bevel), segments=segments, matrix=matrix)


def cyl(b, region, c, r, depth, axis="Y", seg=12, bevel=0.0):
    return b.cylinder(region, Vector(mv(c)), m(r), m(depth), axis=axis, segments=seg,
                      bevel=m(bevel))


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


def panel_leaf(b, x0, x1, z0, z1, y0, y1, rails, cols, stile=4.5, mullion=4.5,
               region="paint", flush=False):
    """A stile-and-rail leaf, x0..x1, z0..z1, thickness y0..y1 (y0 < y1).

    rails: list of (za, zb) rail spans in leaf-local height (0 = leaf bottom), bottom to
    top, including the bottom and top rails. cols: number of panel columns between rails
    (1 or 2), per bay as a list. Panels fill every bay between consecutive rails."""
    h = z1 - z0
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


def knob(b, region, x, z, y_face, sign, style="knob"):
    """Knob or lever on the face at y_face; sign = -1 for the -Y face, +1 for +Y.
    Lever handles point toward the hinge (the caller mirrors via `lever_dir`)."""
    rose_t, rose_r = 0.35, 1.3
    cyl(b, region, (x, y_face + sign * rose_t / 2, z), rose_r, rose_t, seg=16, bevel=0.1)
    if style == "knob":
        cyl(b, region, (x, y_face + sign * (rose_t + 0.6), z), 0.45, 1.2, seg=10)
        cyl(b, region, (x, y_face + sign * (rose_t + 1.9), z), 1.05, 1.3, seg=16, bevel=0.45)
    return y_face + sign * rose_t


def lever(b, region, x, z, y_face, sign, direction):
    """Lever set: rose, neck and a gently curved lever pointing `direction` (+1/-1 in X)."""
    y = knob(b, region, x, z, y_face, sign, style="lever")
    cyl(b, region, (x, y + sign * 0.9, z), 0.45, 1.8, seg=10)
    yl = y + sign * 1.9
    pts = [(x, yl, z), (x + direction * 1.8, yl, z - 0.15), (x + direction * 3.6, yl - sign * 0.2, z - 0.1),
           (x + direction * 4.6, yl - sign * 0.5, z + 0.35)]
    pts = [Vector(mv(p)) for p in common.smooth_path(pts, 3)]
    prof = [(m(0.32) * math.cos(a), m(0.2) * math.sin(a)) for a in
            [2 * math.pi * i / 6 for i in range(6)]]
    b.sweep(region, pts, prof, up=(0, 1, 0))


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


def hinged(coll, name, width, height, wall_t, leaf_t, hand, open_deg, rails, cols,
           handle="knob", flush=False, extras=None):
    """A hinged door: frame object (jamb, stops, hinge knuckles) + leaf object.

    width: clear opening (in); hand: +1 opening extends to +X, -1 to -X; open_deg: how far
    the leaf is swung toward -Y (0 = closed). Returns [frame, leaf, grab marker]."""
    s = hand
    y_face = -wall_t / 2                     # leaf's front face sits flush with the jamb edge
    pin = (s * (JAMB_T + GAP / 2), y_face - 0.15, 0.0)
    # frame
    f = builder()
    jamb(f, width, height, wall_t, hand=s, stops=True, stop_y=y_face + leaf_t)
    hinge_z = [11.0, (11.0 + height - 7.0) / 2, height - 7.0]    # EST standard spacing
    for hz in hinge_z:
        cyl(f, "nickel", (pin[0], pin[1], hz), 0.3, 3.5, axis="Z", seg=8)
    frame = f.to_object(name, coll)
    # leaf
    b = builder()
    lx0, lx1 = sorted((s * (JAMB_T + GAP), s * (width - JAMB_T - GAP)))
    lz0, lz1 = FLOOR_GAP, height - JAMB_T - GAP
    panel_leaf(b, lx0, lx1, lz0, lz1, y_face, y_face + leaf_t, rails, cols, flush=flush)
    latch_x = s * (width - JAMB_T - GAP - BACKSET)
    for sign, yf in ((-1, y_face), (1, y_face + leaf_t)):
        if handle == "lever":
            lever(b, "bronze", latch_x, KNOB_Z, yf, sign, direction=-s)
        else:
            knob(b, "nickel", latch_x, KNOB_Z, yf, sign)
    if extras:
        extras(b, lx0, lx1, lz0, lz1, y_face, y_face + leaf_t)
    grab = (latch_x, y_face - 2.4, KNOB_Z)
    if open_deg:
        rotate_about(b, pin, -s * open_deg)
        g = Matrix.Rotation(math.radians(-s * open_deg), 3, "Z") @ (Vector(grab) - Vector(pin)) + Vector(pin)
        grab = tuple(g)
    leaf = b.to_object(name + "_leaf", coll, origin=mv(pin))
    mk = marker(coll, name + "_leaf_grab", grab)
    return [frame, leaf, mk]


# --- texturing / materials ---------------------------------------------------------

def texture(objs):
    import bpy
    mat = common.atlas_material("doors", ATLAS)
    glass = None
    for ob in objs:
        if ob.type != "MESH":
            continue
        common.atlas_uvs(ob, ATLAS)
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
