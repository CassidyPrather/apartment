"""living_floor atlas (256): flat colours with a fine grain, painted from scratch in GIMP.
Colours matched by eye to the couch-side photo (Reference/couch_work/side_by_side.jpg).

    python blender/lib/textures/gimp_headless.py --object living_floor
"""

ATLAS = {
    "name": "living_floor",
    "size": 256,
    "regions": {
        "tub_white": (0, 0, 64, 64),
        "tube_clear": (64, 0, 64, 64),
        "mesh_white": (128, 0, 64, 64),
        "navy": (192, 0, 64, 64),
        "sole_white": (0, 64, 64, 64),
        "laces_white": (64, 64, 64, 64),
        "insole_grey": (128, 64, 64, 64),
    },
}
COLOURS = {
    "tub_white": ((236, 236, 232), 0.0, 0.45),
    "tube_clear": ((214, 204, 178), 0.0, 0.6),     # yellowed clear vinyl
    "mesh_white": ((228, 228, 226), 0.0, 0.1),
    "navy": ((34, 42, 72), 0.0, 0.2),
    "sole_white": ((238, 238, 234), 0.0, 0.25),
    "laces_white": ((230, 230, 228), 0.0, 0.1),
    "insole_grey": ((96, 98, 104), 0.0, 0.05),
}


def build():
    a = Atlas(ATLAS)
    for name, (rgb, metal, smooth) in COLOURS.items():
        x, y, w, h = a.rect(name)
        fill_rect(a.img, a.lay, (x, y, w, h), rgb)
        grain(a.img, a.lay, (x, y, w, h), 0.04, 0.6)
        a.material(name, metal, smooth)
    a.save()
