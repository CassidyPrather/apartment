"""Apartment shell: walls with door and window openings, floors, ceiling, door casings,
baseboards and window glass, all from shell_layout.py.

Source of truth: scripted; every dimension comes from shell_layout (inches). Blender
frame = plan frame: origin at the interior south-west corner, +X east, +Y north, Z up.
One object per wall (clean per-object lightmaps in Unity), one per floor finish, one
ceiling, one for trim (casings and baseboards), one for glass.
"""

import importlib

import common
import shell_layout as L

importlib.reload(L)

m = L.m
H = L.CEILING
BASE_H, BASE_T = 3.5, 0.5          # A baseboard height and thickness (inches)
CASING_T = 0.75                    # A casing thickness proud of the wall
WALL_REGIONS = ["wall_paint"]
TRIM_REGIONS = ["trim_paint"]


def wall_axis(rect):
    x0, x1, y0, y1 = rect
    return "x" if (x1 - x0) >= (y1 - y0) else "y"


def openings_for(name):
    return [o for o in L.OPENINGS if o[0] == name]


def wall_pieces(rect, openings):
    """Split a wall box into solid pieces around its openings (inches)."""
    x0, x1, y0, y1 = rect
    ax = wall_axis(rect)
    lo, hi = (x0, x1) if ax == "x" else (y0, y1)
    ops = sorted(openings, key=lambda o: o[2][0])
    pieces, cur = [], lo
    for _, _, (a0, a1), (z0, z1), _, _ in ops:
        if a0 > cur:
            pieces.append((cur, a0, 0.0, H))
        if z0 > 0:
            pieces.append((a0, a1, 0.0, z0))
        if z1 < H:
            pieces.append((a0, a1, z1, H))
        cur = max(cur, a1)
    if cur < hi:
        pieces.append((cur, hi, 0.0, H))
    boxes = []
    for a0, a1, z0, z1 in pieces:
        if ax == "x":
            boxes.append(((a0, y0, z0), (a1, y1, z1)))
        else:
            boxes.append(((x0, a0, z0), (x1, a1, z1)))
    return boxes


def mb(lo, hi):
    return tuple(m(v) for v in lo), tuple(m(v) for v in hi)


def is_exterior(name):
    return name.startswith("ext_")


def interior_faces(name, rect):
    """Offsets (inches) of the wall faces that face into the apartment."""
    x0, x1, y0, y1 = rect
    ax = wall_axis(rect)
    a, b = (y0, y1) if ax == "x" else (x0, x1)       # the wall's thickness span
    if name == "ext_south":
        return [(b, +1)]
    if name == "ext_north":
        return [(a, -1)]
    if name == "ext_west":
        return [(b, +1)]
    if name == "ext_east":
        return [(a, -1)]
    return [(a, -1), (b, +1)]


def build_walls(coll):
    obs = []
    for name, (rect, _conf) in L.WALLS.items():
        b = common.Builder(WALL_REGIONS)
        for lo, hi in wall_pieces(rect, openings_for(name)):
            lo_m, hi_m = mb(lo, hi)
            b.box("wall_paint", lo_m, hi_m)
        obs.append(b.to_object(f"shell_wall_{name}", coll))
    return obs


def build_floors_ceiling(coll):
    obs = []
    finishes = {}
    for x0, x1, y0, y1, fin in L.FLOORS:
        finishes.setdefault(fin, []).append((x0, x1, y0, y1))
    # Floor through the wall thickness under every interior doorway (the room floors stop
    # at the wall faces, which left a gap); it takes the finish on the doorway's +side.
    for wall, ax, (a0, a1), (z0, z1), kind, _ in L.OPENINGS:
        if not kind.startswith("door") or is_exterior(wall):
            continue
        x0, x1, y0, y1 = L.WALLS[wall][0]
        rect = (x0, x1, a0, a1) if ax == "y" else (a0, a1, y0, y1)
        px, py = ((x1 + 1.0, (a0 + a1) / 2) if ax == "y" else ((a0 + a1) / 2, y1 + 1.0))
        fin = next((f for fx0, fx1, fy0, fy1, f in L.FLOORS if fx0 <= px <= fx1 and fy0 <= py <= fy1), "floor_vinyl")
        finishes.setdefault(fin, []).append(rect)
    for fin, rects in finishes.items():
        b = common.Builder([fin])
        for x0, x1, y0, y1 in rects:
            b.box(fin, (m(x0), m(y0), -0.01), (m(x1), m(y1), 0.0))
        obs.append(b.to_object(f"shell_{fin}", coll))
    b = common.Builder(["ceiling_paint"])
    b.box("ceiling_paint", (0.0, 0.0, m(H)), (m(L.INTERIOR_W), m(L.INTERIOR_D), m(H) + 0.1))
    obs.append(b.to_object("shell_ceiling", coll))
    return obs


def build_trim(coll):
    """Door casings on both faces of each hinged/entry door, and baseboards."""
    b = common.Builder(TRIM_REGIONS)
    t = L.DOOR_TRIM
    door_spans = {}
    for wall, ax, (a0, a1), (z0, z1), kind, _ in L.OPENINGS:
        if not kind.startswith("door"):
            continue
        rect = L.WALLS[wall][0]
        door_spans.setdefault(wall, []).append((a0, a1))
        if kind in ("door_sliding",):
            continue
        for off, sgn in interior_faces(wall, rect):
            d0, d1 = (off, off + sgn * CASING_T)
            d0, d1 = min(d0, d1), max(d0, d1)
            parts = [((a0 - t, a0), (0.0, z1 + t)), ((a1, a1 + t), (0.0, z1 + t)), ((a0 - t, a1 + t), (z1, z1 + t))]
            for (u0, u1), (w0, w1) in parts:
                if ax == "y":
                    lo, hi = (d0, u0, w0), (d1, u1, w1)
                else:
                    lo, hi = (u0, d0, w0), (u1, d1, w1)
                b.box("trim_paint", *mb(lo, hi))
    # Baseboards along every interior-facing wall face, broken at door openings.
    for name, (rect, _conf) in L.WALLS.items():
        ax = wall_axis(rect)
        x0, x1, y0, y1 = rect
        lo_a, hi_a = (x0, x1) if ax == "x" else (y0, y1)
        if is_exterior(name):                      # stop at the interior corners
            lo_a, hi_a = max(lo_a, 0.0), min(hi_a, L.INTERIOR_W if ax == "x" else L.INTERIOR_D)
        cuts = sorted(door_spans.get(name, []))
        spans, cur = [], lo_a
        for a0, a1 in cuts:
            if a0 - L.DOOR_TRIM > cur:
                spans.append((cur, a0 - L.DOOR_TRIM))
            cur = max(cur, a1 + L.DOOR_TRIM)
        if cur < hi_a:
            spans.append((cur, hi_a))
        for off, sgn in interior_faces(name, rect):
            d0, d1 = sorted((off, off + sgn * BASE_T))
            for s0, s1 in spans:
                if ax == "x":
                    lo, hi = (s0, d0, 0.0), (s1, d1, BASE_H)
                else:
                    lo, hi = (d0, s0, 0.0), (d1, s1, BASE_H)
                b.box("trim_paint", *mb(lo, hi))
    return [b.to_object("shell_trim", coll)]


def build_glass(coll):
    """Window panes set 1.5 in in from the exterior face of each window recess."""
    b = common.Builder(["window_glass"])
    for wall, ax, (a0, a1), (z0, z1), kind, _ in L.OPENINGS:
        if kind != "window":
            continue
        x0, x1, y0, y1 = L.WALLS[wall][0]
        if ax == "x":                       # south/north wall: pane in the XZ plane
            yc = (y0 + 1.5) if wall == "ext_south" else (y1 - 1.5)
            lo, hi = (a0, yc - 0.1, z0), (a1, yc + 0.1, z1)
        else:
            xc = (x0 + 1.5) if wall == "ext_west" else (x1 - 1.5)
            lo, hi = (xc - 0.1, a0, z0), (xc + 0.1, a1, z1)
        b.box("window_glass", *mb(lo, hi))
    return [b.to_object("shell_glass", coll)]


def build_markers(coll):
    """Where furniture and appliances stand; Unity drops their prefabs on these."""
    import math
    import bpy
    obs = []
    for name, (x, y, rot, *z) in L.PLACES.items():
        ob = bpy.data.objects.new(f"place_{name}", None)
        ob.empty_display_type = "ARROWS"
        ob.location = (m(x), m(y), m(z[0]) if z else 0.0)
        ob.rotation_euler = (0, 0, math.radians(rot))
        coll.objects.link(ob)
        obs.append(ob)
    return obs


def build(coll):
    # Window glass lives in the window_units package now; build_glass() stays for
    # quick previews of the bare shell.
    return build_walls(coll) + build_floors_ceiling(coll) + build_trim(coll) + build_markers(coll)


# region -> (texture set in Assets/Apartment/Textures, metres per tile)
FINISHES = {
    "wall_paint": ("shell_wall", 1.0),
    "ceiling_paint": ("shell_ceiling", 1.0),
    "trim_paint": ("shell_trim", 1.0),
    "floor_carpet": ("shell_carpet", 0.5),
    "floor_vinyl": ("shell_vinyl", 1.2192),     # seven ~7 in planks across a 48 in tile
}


def texture(obs):
    """Tiling GIMP materials for every finish; glass stays a flat placeholder until the
    exterior view is built."""
    import bpy
    tiles = {r: t for r, (_, t) in FINISHES.items()}
    tiles["window_glass"] = 1.0
    glass = bpy.data.materials.get("shell_glass") or bpy.data.materials.new("shell_glass")
    glass.use_nodes = True
    gb = next(n for n in glass.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    gb.inputs["Base Color"].default_value = (0.62, 0.72, 0.82, 1)
    gb.inputs["Roughness"].default_value = 0.05
    mats = {r: common.atlas_material(tex, tex, tiled=True) for r, (tex, _) in FINISHES.items()}
    mats["window_glass"] = glass
    for ob in obs:
        if ob.type != "MESH":
            continue
        common.atlas_uvs(ob, None, tiled=tiles)
        common.collapse_materials(ob, mats)
