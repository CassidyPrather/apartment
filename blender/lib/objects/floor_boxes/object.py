"""Floor boxes: two snack cases on the carpet between the floor lamp and the plastic
drawers. At the bottom, an open kraft tray of cellophane-wrapped snack bars (parody
brand "Crunchums"); resting across it, a closed orange case of instant-noodle cups
(parody brand "Noodle Goblin", logo on the long sides).

Source of truth: scripted from the LiDAR survey (stack plan x 259-274, y 45.5-61.5,
dense points up to z ~9-10) and the survey crops. Origin on the floor at the footprint
centre; front faces -Y, back (+Y) toward the east wall. Place at plan (266.5, 53.5),
rotation -90 (local +X is south).

Dimensions (inches):
  noodle case 16.5 L x 10.5 D x 6.5 H, resting on the bars at z 2.85   EST from photo / SCAN top ~9.5
  bar tray 15.5 L x 11 D x 3 H, bars two layers to z ~4.5      EST from photo
  overall footprint ~16.5 x 14.5                                SCAN 15.5 x 16
"""

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "floor_boxes"
CASE = (-7.5, -2.8, 2.85, 9.0, 7.7, 9.35)      # x0, y0, z0, x1, y1, z1
TRAY = (-8.2, -7.0, 0.0, 7.3, 4.0, 3.0)

ATLAS = {
    "name": "floor_boxes",
    "size": 1024,
    "regions": {
        "case_side": (0, 0, 1024, 384),       # long sides (-Y / +Y), logo + stripe
        "case_top": (0, 384, 512, 384),       # white panel, unreadable fine print
        "case_end": (512, 384, 512, 256),     # short ends
        "kraft": (512, 640, 256, 128),
        "tray_print": (768, 640, 256, 128),   # red print on the tray sides
        "wrapper": (0, 768, 512, 256),        # red/white bar wrappers, logo
        "bar_end": (512, 768, 256, 256),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"floor_boxes": {"atlas": "floor_boxes", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo", 20, 40, 0.8)]


def tag_by_normal(b, faces, table):
    """Retag box faces by their outward axis: table maps '+X','-X','+Y','-Y','+Z','-Z'."""
    for f in faces:
        f.normal_update()
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        key = ("+" if n[ax] > 0 else "-") + "XYZ"[ax]
        if key in table:
            f.material_index = b.idx(table[key])


def bx(b, r, lo, hi, bev=0.0):
    """Box; returns every face it made (bevel faces included)."""
    before = set(b.bm.faces)
    b.box(r, tuple(map(m, lo)), tuple(map(m, hi)), bevel=m(bev))
    return [f for f in b.bm.faces if f not in before]


def build(coll):
    b = common.Builder(REGIONS)
    # tray: base and four low walls, kraft inside, printed outside
    x0, y0, z0, x1, y1, z1 = TRAY
    t = 0.15
    bx(b, "kraft", (x0, y0, z0), (x1, y1, z0 + t))
    for lo, hi in (((x0, y0, z0), (x1, y0 + t, z1)), ((x0, y1 - t, z0), (x1, y1, z1)),
                   ((x0, y0, z0), (x0 + t, y1, z1)), ((x1 - t, y0, z0), (x1, y1, z1))):
        f = bx(b, "kraft", lo, hi)
        tag_by_normal(b, f, {"-Y": "tray_print", "+X": "tray_print", "-X": "tray_print"})
    # bars: two layers of wrapped bars lying front-to-back
    n = 9
    bw = (x1 - x0 - 0.5) / n
    for layer in range(2):
        for i in range(n - layer):
            bxx = x0 + 0.25 + i * bw + layer * bw / 2
            zb = z0 + t + layer * 1.35
            f = bx(b, "wrapper", (bxx + 0.05, y0 + 0.4, zb), (bxx + bw - 0.05, y1 - 0.4, zb + 1.35), 0.3)
            tag_by_normal(b, f, {"-Y": "bar_end", "+Y": "bar_end"})
    # noodle case resting on the bars
    cx0, cy0, cz0, cx1, cy1, cz1 = CASE
    f = bx(b, "case_side", (cx0, cy0, cz0), (cx1, cy1, cz1), 0.1)
    tag_by_normal(b, f, {"+Z": "case_top", "-Z": "case_end", "+X": "case_end", "-X": "case_end"})
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    cx0, cy0, cz0, cx1, cy1, cz1 = CASE
    planar = {
        "case_side": ("-Y", (m(cx0), m(cx1)), (m(cz0), m(cz1))),
        "case_top": ("+Z", (m(cx0), m(cx1)), (m(cy0), m(cy1))),
        "case_end": ("+X", (m(cy0), m(cy1)), (m(cz0), m(cz1))),
    }
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
