"""Portable cassette recorder and Cassidy's mixtape in its clear case, as they lie on the media
hutch's bottom shelf (IMG_1506): the recorder flat on its back, window up, with the case on top
and the wrist strap draped over the shelf edge.

cassette_player: black body with a pyramid-knurled face, a smoked window strip over the reels,
  a silver stripe, the parody "Humdinger" badge and "Mini Mumbler" lettering in orange (the
  real brand's round monogram and model text are replaced), three black keys and an orange
  one on the button side, a speaker grille underneath, and the braided wrist strap.
cassette_case: a Norelco-style clear case with Cassidy's own J-card (the "Crow / Bunny" photo
  card and the handwritten "Caramel Sea Salt Mix" spine, rectified from IMG_1513/IMG_1509),
  the cassette shell inside. Its own mesh, placed on top of the player.

Source of truth: scripted. Sizes: the case is the standard 110 x 70 x 17 mm (SPEC); the
recorder is scaled from the case in IMG_1513 and IMG_1514 (EST 5.3 x 3.8 x 1.45 in). Layout
of the face from IMG_1513 (square-on), keys from IMG_1513/1514, strap from IMG_1510/1513.

Frame (inches, converted with m()): origin on the resting surface under the recorder's
centre; the recorder lies face up (+Z); its long axis is X with the badge end at +X, the
key side toward +Y, the front (-Y) faces the room. Place at the media hutch's
`place_cassette_player` marker (hutch frame (-8.0, -6.55, 31.0), yaw -12 deg; plan
(118.2, 25.75, 31.0) with the hutch at plan (124.75, 17.75) rotated -90). The strap drape
assumes the shelf's front edge sits 0.6 in in front of the strap lug, as it does there.
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import common
from atlas_layout import uv_rect

IN = 0.0254


def m(v):
    return v * IN


# recorder body                                                    provenance
PL, PW, PT = 5.3, 3.8, 1.35     # EST scaled from the case in IMG_1513/1514/1511 (+-0.2)
CORNER = 0.14                   # EST edge radius
KEYS = [(-0.85, -0.3, "black"), (-0.25, 0.3, "black"), (0.35, 0.9, "black"), (0.98, 1.48, "orange")]
KEY_Z = (0.4, 0.92)             # EST, keys protrude 0.18 from the +Y side
# case (SPEC Norelco 110 x 70 x 17 mm) and its place on the recorder (PHOTO IMG_1506)
CL, CW, CT = 4.33, 2.76, 0.67
CASE_AT = (0.55, -0.35, PT, 5.0)   # x, y, z, yaw deg

NAME = "cassette_player"
ATLAS = {
    "name": "cassette_player",
    "size": 1024,
    "regions": {
        "face": (0, 0, 1024, 734),
        "back": (0, 740, 400, 284),
        "side_front": (410, 740, 512, 140),
        "black": (410, 890, 32, 32), "orange": (446, 890, 32, 32), "chrome": (482, 890, 32, 32),
        "strap": (518, 890, 32, 32), "clear": (554, 890, 32, 32), "shell": (590, 890, 32, 32),
        "grey": (626, 890, 32, 32), "cream": (662, 890, 32, 32),
    },
}
ART_ATLAS = {
    "name": "cassette_player_art",
    "size": 512,
    "regions": {"label_front": (0, 0, 512, 322), "label_spine": (0, 330, 512, 74)},
}
ART_REGIONS = list(ART_ATLAS["regions"])
REGIONS = list(ATLAS["regions"]) + ART_REGIONS
CLEAR_ALPHA = 0.14
MATERIALS = {
    "cassette_player": {"atlas": "cassette_player", "mode": "opaque", "tiled": False},
    "cassette_player_art": {"atlas": "cassette_player_art", "mode": "opaque", "tiled": False},
    "cassette_case_clear": {"atlas": "cassette_player", "mode": "transparent", "alpha": CLEAR_ALPHA,
                            "tiled": False},
}
COLLIDER = "box"
STATIC = False
VIEWS = [("shelf_view", 10, 30, 0.9), ("face_top", 0, 80, 0.8), ("key_side", 160, 20, 0.9)]

# planar regions: region -> (axis, (u range), (v range)) in the owning object's frame, inches
PLANAR = {
    "face": ("+Z", (-PL / 2, PL / 2), (-PW / 2, PW / 2)),
    "back": ("-Z", (-PL / 2, PL / 2), (-PW / 2, PW / 2)),
    "side_front": ("-Y", (-PL / 2, PL / 2), (0.0, PT)),
    "label_front": ("+Z", (-2.1, 2.1), (-1.32, 1.32)),
    "label_spine": ("-Y", (-2.1, 2.1), (0.04, 0.63)),
}
AXES = {"+Z": ((1, 0, 0), (0, 1, 0)), "-Z": ((1, 0, 0), (0, -1, 0)), "-Y": ((1, 0, 0), (0, 0, 1))}


def bx(b, region, lo, hi, bevel=0.0, seg=2):
    return b.box(region, tuple(map(m, lo)), tuple(map(m, hi)), bevel=m(bevel), segments=seg)


def retag(b, faces_before, region_by_normal):
    """Re-tag the faces created since `faces_before` by their normal direction."""
    b.bm.normal_update()
    for f in b.bm.faces:
        if f.index >= faces_before:
            for (ax, sgn), reg in region_by_normal.items():
                if f.normal[ax] * sgn > 0.95:
                    f.material_index = b.idx(reg)


def player(coll):
    b = common.Builder(REGIONS)
    bm = b.bm
    # body (the parting line between the face and base shells is painted on the sides)
    bm.faces.index_update()
    n0 = len(bm.faces)
    bx(b, "black", (-PL / 2, -PW / 2, 0.0), (PL / 2, PW / 2, PT), CORNER)
    bm.faces.index_update()
    retag(b, n0, {(2, 1): "face", (2, -1): "back", (1, -1): "side_front"})
    # keys along the +Y side and the pause slider at the badge end
    for x0, x1, reg in KEYS:
        bx(b, reg, (x0, PW / 2 - 0.1, KEY_Z[0]), (x1, PW / 2 + 0.18, KEY_Z[1]), 0.04, 1)
    bx(b, "orange", (PL / 2 - 0.05, 0.6, 0.35), (PL / 2 + 0.08, 1.1, 0.6), 0.02, 1)
    # strap lug at the badge end, front corner, and the braided strap draped over the shelf edge
    lug = Vector((PL / 2 - 0.25, -PW / 2 + 0.05, PT * 0.5))
    bx(b, "black", (lug.x - 0.2, lug.y - 0.18, lug.z - 0.18), (lug.x + 0.2, lug.y + 0.1, lug.z + 0.18), 0.05, 1)
    path = [(2.4, -1.85, 0.75), (2.46, -2.2, 0.5), (2.55, -2.5, 0.12), (2.62, -2.72, -0.1),
            (2.72, -3.0, -0.6), (2.82, -3.1, -1.6), (2.95, -3.12, -2.25), (3.1, -3.08, -1.6),
            (3.02, -2.95, -0.6), (2.9, -2.66, -0.08), (2.8, -2.42, 0.2), (2.62, -2.1, 0.55),
            (2.55, -1.85, 0.75)]
    b.sweep("strap", [tuple(map(m, p)) for p in common.smooth_path(path, 3)],
            common.circle_profile(m(0.07), 6), up=(0, 0, 1))
    ob = b.to_object(NAME, coll)
    return ob


def case(coll):
    b = common.Builder(REGIONS)
    # J-card: front panel under the lid and the spine panel behind the front wall
    bx(b, "cream", (-2.1, -1.32, CT - 0.05), (2.1, 1.32, CT - 0.03))
    b.bm.faces.index_update()
    n0 = len(b.bm.faces)
    bx(b, "cream", (-2.1, -1.34, 0.04), (2.1, -1.32, 0.63))
    b.bm.faces.index_update()
    retag(b, n0, {(1, -1): "label_spine"})
    b.bm.normal_update()
    for f in b.bm.faces:
        if f.index < n0:
            if f.normal.z > 0.95:
                f.material_index = b.idx("label_front")
    # the cassette shell inside
    bx(b, "shell", (-1.97, -1.24, 0.1), (1.97, 1.24, 0.57), 0.05, 1)
    # clear case (lid + tray as one box)
    bx(b, "clear", (-CL / 2, -CW / 2, 0.0), (CL / 2, CW / 2, CT), 0.04, 1)
    ob = b.to_object("cassette_case", coll)
    x, y, z, yaw = CASE_AT
    ob.location = (m(x), m(y), m(z))
    ob.rotation_euler = (0.0, 0.0, math.radians(yaw))
    return ob


def build(coll):
    return [player(coll), case(coll)]


def _uvs(ob):
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    regions = [s.name.split(".")[0] for s in me.materials]
    for p in me.polygons:
        reg = regions[p.material_index]
        atlas = ART_ATLAS if reg in ART_REGIONS else ATLAS
        u0, v0, u1, v1 = uv_rect(atlas, reg)
        if reg in PLANAR:
            axis, (a0, a1), (c0, c1) = PLANAR[reg]
            ua, va = map(Vector, AXES[axis])
            for li in p.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co / IN
                fu = min(max((co.dot(ua) - a0) / (a1 - a0), 0), 1)
                fv = min(max((co.dot(va) - c0) / (c1 - c0), 0), 1)
                uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))
        else:
            for li in p.loop_indices:        # flat colour cells
                uvl.data[li].uv = ((u0 + u1) / 2, (v0 + v1) / 2)


def texture(objs):
    main = common.atlas_material(NAME, ATLAS)
    art = common.atlas_material("cassette_player_art", ART_ATLAS)
    clear = common.atlas_material("cassette_case_clear", ATLAS)
    bsdf = next(n for n in clear.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = CLEAR_ALPHA
    if hasattr(clear, "surface_render_method"):
        clear.surface_render_method = "BLENDED"
    else:
        clear.blend_method = "BLEND"
    slots = {r: (art if r in ART_REGIONS else clear if r == "clear" else main) for r in REGIONS}
    for ob in objs:
        _uvs(ob)
        common.collapse_materials(ob, slots)
