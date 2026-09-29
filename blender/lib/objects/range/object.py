"""Freestanding 30 in electric coil range: white enamel body, backguard with four skirted
knobs and a grey clock/oven panel, four black coil burners in chrome drip pans, oven door
with a cream vent band, a towel-bar handle with curled end brackets and a smoked window,
storage drawer at the bottom.

Source of truth: scripted. Size from the living-room/kitchen LiDAR survey; layout, hardware
and wear from the survey photo crops and the close capture frames (wide_..._003908 backguard
and cooktop from above, _004105/_004111 door and handle, kitchen_base_north_3 front):
- backguard, left to right: two skirted knobs (front, rear), a cream oven-light rocker, a grey
  panel (green clock display, four touch pads, oven dial), a red indicator, two knobs; a small
  maker badge under the left knobs (parody "grumbleworks")
- burners: 8 in coils at left-back and right-front, 6 in at left-front and right-back
- wear, as seen: brown burnt rings and spatter around the burner openings, darkened drip
  pans with a chrome rim, a yellowed handle with rust specks, rust grime along the
  door-to-drawer seam
Origin on the floor at the centre of the body footprint (backguard and handle included);
front faces -Y. Place at plan (64.5, 272), rotation 0: the 49.5-79.5 in gap on the north wall.
"""

import math

from mathutils import Vector

import common

IN = 0.0254


def m(v):
    return v * IN


W = 29.875          # EST standard 30 in slot range
D = 28.0            # EST body incl. backguard, door front to back
H = 36.0            # EST cooktop height (matches the counters)
GUARD_H = 8.0       # PHOTO backguard rises to ~44
GUARD_D = 3.0       # EST
DRAWER = (1.0, 8.5)      # PHOTO storage drawer z (kitchen_base_north_3: ~7.5 in drawer)
DOOR = (9.0, 34.8)       # PHOTO oven door z, incl. the cream vent band at its top
VENT = (33.2, 34.8)      # PHOTO cream vent band with a slot
WINDOW = (21.0, 29.0, 7.5)   # PHOTO window z0, z1 and half width
HANDLE_Z = 31.1          # PHOTO bar centre, below the vent band; brackets meet the door at ~32.6
KNOB_Z = H + 4.1         # PHOTO
KNOBS_X = (-12.4, -9.2, 9.2, 12.4)   # PHOTO (003908, kitchen_base_north_3)
DIAL_X = 3.8             # PHOTO oven dial at the right end of the grey panel
PANEL = (-5.4, 5.4, H + 2.3, H + 6.0)   # PHOTO grey control panel x0, x1, z0, z1
ROCKER_X = -6.7          # PHOTO cream oven-light rocker
BURNERS = [(-7.0, -5.5, 3.0), (7.0, -5.5, 4.0), (-7.0, 6.0, 4.0), (7.0, 6.0, 3.0)]  # PHOTO x, y, coil radius
PAN_RIM = 1.1            # EST chrome drip pan beyond the coil

# decal extents (texture planar projections; textures.py paints in these frames)
TOP_Y = (-13.5, 11.0)                        # cooktop plate front to backguard
GUARD_UV = (-W / 2 + 0.4, W / 2 - 0.4, H + 0.8, H + 7.5)
FRONT_Z = (0.0, 35.0)

NAME = "range"
ATLAS = {
    "name": "range",
    "size": 1024,
    "regions": {
        "cooktop": (0, 0, 512, 512),
        "door_face": (512, 0, 512, 416),
        "drippan": (512, 416, 256, 256),
        "coil": (768, 416, 256, 256),
        "guard_face": (0, 512, 512, 160),
        "glass": (0, 672, 256, 160),
        "enamel": (256, 672, 128, 128),
        "knob": (384, 672, 128, 128),
        "handle": (512, 672, 256, 128),
        "chrome": (768, 672, 128, 128),
        "trim_black": (896, 672, 128, 128),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"range": {"atlas": "range", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("plan_top", 0, 89, 1.0), ("photo_front", 12, 14, 0.75), ("photo_left", -28, 22, 0.75),
         ("cooktop", 0, 62, 0.55)]


def _knob(b, x, z, yface, r=1.0):
    """Skirted knob with a raised grip fin (white)."""
    b.cylinder("knob", (m(x), m(yface - 0.15), m(z)), m(r), m(0.3), axis="Y", segments=12)
    b.cylinder("knob", (m(x), m(yface - 0.6), m(z)), m(r * 0.62), m(0.7), axis="Y", segments=8)
    b.box("knob", (m(x - 0.14), m(yface - 1.15), m(z - r * 0.72)), (m(x + 0.14), m(yface - 0.3), m(z + r * 0.72)))


def build(coll):
    b = common.Builder(REGIONS)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    bx = lambda r, a, c, bev=0.0, seg=2: b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg)
    # body (behind the door and drawer fronts) and toe recess
    bx("enamel", (x0, y0 + 1.0, 1.0), (x1, y1, H - 0.6))
    bx("trim_black", (x0 + 1.0, y0 + 3.0, 0.0), (x1 - 1.0, y1 - 1.0, 1.0))
    # cooktop plate (stains and rim shading painted top-down), backguard
    bx("cooktop", (x0, y0 + 0.5, H - 0.6), (x1, y1 - GUARD_D, H), 0.3, 1)
    bx("enamel", (x0, y1 - GUARD_D, H - 0.6), (x1, y1, H + GUARD_H), 0.3, 1)
    gf = y1 - GUARD_D
    gx0, gx1, gz0, gz1 = GUARD_UV
    bx("guard_face", (gx0, gf - 0.03, gz0), (gx1, gf + 0.02, gz1))            # printed face
    px0, px1, pz0, pz1 = PANEL
    bx("guard_face", (px0, gf - 0.18, pz0), (px1, gf, pz1), 0.08, 1)          # raised grey panel
    for kx in KNOBS_X:
        _knob(b, kx, KNOB_Z, gf - 0.03)
    _knob(b, DIAL_X, KNOB_Z, gf - 0.18, r=0.85)
    bx("handle", (ROCKER_X - 0.3, gf - 0.3, KNOB_Z - 0.75), (ROCKER_X + 0.3, gf, KNOB_Z + 0.35), 0.06, 1)
    # burners: chrome drip pan under a black coil
    for bxp, byp, r in BURNERS:
        b.cylinder("drippan", (m(bxp), m(byp), m(H + 0.06)), m(r + PAN_RIM), m(0.14), segments=16)
        b.cylinder("coil", (m(bxp), m(byp), m(H + 0.3)), m(r), m(0.3), segments=16)
        bx("coil", (bxp - 0.25, byp + r - 0.2, H + 0.1), (bxp + 0.25, byp + r + PAN_RIM + 0.4, H + 0.4))   # terminal
    # oven door: printed face (vent band, recess, grime), smoked window, towel-bar handle
    dy = y0
    bx("door_face", (x0 + 0.1, dy, DOOR[0]), (x1 - 0.1, dy + 1.2, DOOR[1]), 0.35, 1)
    wz0, wz1, wh = WINDOW
    bx("glass", (-wh, dy - 0.04, wz0), (wh, dy + 0.3, wz1))
    hx = (W - 3.2) / 2
    pts = [(-hx, dy + 0.1, 32.6), (-hx - 0.3, dy - 1.2, 32.0), (-hx + 1.0, dy - 1.68, HANDLE_Z)]
    pts = pts + [(-x, y, z) for x, y, z in reversed(pts)]
    path = common.smooth_path([Vector(tuple(map(m, p))) for p in pts], samples=2)
    prof = [(m(0.45) * math.cos(a), m(0.55) * math.sin(a)) for a in [i * math.pi / 6 for i in range(12)]]
    b.sweep("handle", path, prof, up=(0, 0, 1))
    # storage drawer and the groove under the door
    bx("door_face", (x0 + 0.1, dy, DRAWER[0]), (x1 - 0.1, dy + 1.0, DRAWER[1]), 0.3, 1)
    bx("door_face", (x0 + 0.6, dy + 0.3, DRAWER[1]), (x1 - 0.6, dy + 1.0, DOOR[0]))
    return [b.to_object(NAME, coll)]


def _island_uvs(ob, atlas, regions):
    """Per connected piece of each region, box-project every face onto the whole region
    rect using that piece's own bounds (so each drip pan, coil or handle gets the full
    painted image). Axes as common._axes (seen from outside, image up = +Z or +Y)."""
    me = ob.data
    names = [mm.name.split(".")[0] for mm in me.materials]
    uvl = me.uv_layers["UVMap"]
    for region in regions:
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
        u0, v0, u1, v1 = common.uv_rect(atlas, region)
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


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    x0, x1 = m(-W / 2), m(W / 2)
    gx0, gx1, gz0, gz1 = GUARD_UV
    common.atlas_uvs(ob, ATLAS, planar={
        "cooktop": ("+Z", (x0, x1), (m(TOP_Y[0]), m(TOP_Y[1]))),
        "guard_face": ("-Y", (m(gx0), m(gx1)), (m(gz0), m(gz1))),
        "door_face": ("-Y", (x0, x1), (m(FRONT_Z[0]), m(FRONT_Z[1]))),
    })
    _island_uvs(ob, ATLAS, ["drippan", "coil", "glass", "handle"])
    common.collapse_materials(ob, {r: mat for r in REGIONS})
