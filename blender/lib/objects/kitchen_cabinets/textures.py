"""kitchen_cabinets atlas (runs in headless GIMP with gimp_textures.py's helpers in scope).

Oak: photo-derived from the flat centre panel of one upper door in the photo through the
bedroom door (only the panel, no people or objects), lighting flattened to the sampled
honey-oak colour, made seamless and tiled across the oak region with alternate columns
offset by half a tile to hide the repeat. Everything else is a flat fill sampled by eye from the survey crops (white laminate top,
light vinyl toe kick, brushed steel sink, brushed nickel pulls).

Wear (only what the capture frames show, e.g. wide_..._004113/004115 close on the base
run): "oak_worn" (every drawer front, whole image per front) is the same oak tile turned
to run the grain across, with a paler worn band along the top edge and around the knob,
small pale nicks, and grime along the bottom edge; "oak_edge" (the stile each base-door
pull is mounted on) is the oak tile with a paler worn patch where hands grab below the
pull, pale scratches and grime at the foot. The uppers stay clean and glossy, as seen.
"""

import random

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "kitchen_cabinets", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
rnd = random.Random(21)
OAK = (192, 126, 60)             # honey oak: the photo doors under warm light sample 180,117,64 (shaded) to 236,173,102 (lit)
PANEL = (2190, 290, 95, 280)     # x, y, w, h: centre panel of the wide west-wall upper door
TILE = (128, 384)                # ~7.6 px/in in the atlas, close to the photo's own scale


def oak_tile():
    img = load(os.path.join(REF, "IMG_1498.jpg"))
    x, y, w, h = PANEL
    img.crop(w, h, x, y)
    lay = img.get_layers()[0]
    gegl(lay, "gegl:gaussian-blur", std_dev_x=0.7, std_dev_y=0.7)     # JPEG blocking
    flatten_lighting(img, 18, OAK, detail=100.0)
    img.scale(*TILE)
    lay = img.get_layers()[0]
    gegl(lay, "gegl:tile-seamless")
    return img


def build():
    a = Atlas(ATLAS)
    tile = oak_tile()
    ox, oy, ow, oh = a.rect("oak")
    tw, th = TILE
    for i in range(ow // tw):
        off = -(th // 2) * (i % 2)
        for j in range(-1, oh // th + 2):
            yy = oy + off + j * th
            if yy >= oy + oh or yy + th <= oy:
                continue
            add_layer_from(a.img, tile, "oak", ox + i * tw, yy)
    a.lay = flatten(a.img)
    # the tiles spill past the oak region; the fills below cover the spill
    a.material("oak", 0.0, 0.32)
    a.fill("counter", (232, 230, 222), 0.0, 0.4, noise=0.08, blur=0.7)   # survey crops: white laminate
    a.fill("steel", (168, 166, 160), 0.6, 0.42, noise=0.07, blur=0.5)   # worn stainless (frames 003853/003858); fully metallic mirrored the brown room
    a.fill("nickel", (182, 180, 174), 1.0, 0.6, noise=0.04, blur=0.5)
    a.fill("toe", (168, 164, 154), 0.0, 0.25, noise=0.04, blur=1.0)   # light vinyl base in the crops
    a.fill("oak_dark", (128, 78, 36), 0.0, 0.3, noise=0.06, blur=1.0)   # shadowed oak frame in the reveals
    a.fill("panel_black", (30, 30, 32), 0.0, 0.5)
    a.fill("drain", (70, 70, 72), 1.0, 0.4)
    # unused corner of the atlas: neutral
    fill_rect(a.img, a.lay, (512, 960, 128, 64), (128, 128, 128))
    worn(a, tile)
    a.save()


def _blot(img, lay, cx, cy, rx, ry, rgb, alpha, feather=0.0):
    img.select_ellipse(Gimp.ChannelOps.REPLACE, cx - rx, cy - ry, 2 * rx, 2 * ry)
    if feather:
        Gimp.Selection.feather(img, feather)
    if not Gimp.Selection.is_empty(img):
        _fill(lay, tuple(rgb) + (alpha,))
    Gimp.Selection.none(img)


def _clip(img, rect):
    x, y, w, h = rect
    img.select_rectangle(Gimp.ChannelOps.INTERSECT, x, y, w, h)


def _soft_rect(a, rect, clip, rgb, alpha, feather):
    x, y, w, h = rect
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    Gimp.Selection.feather(a.img, feather)
    _clip(a.img, clip)
    if not Gimp.Selection.is_empty(a.img):
        _fill(a.lay, tuple(rgb) + (alpha,))
    Gimp.Selection.none(a.img)


def _nicks(a, rect, n, horizontal):
    x, y, w, h = rect
    Gimp.context_set_brush_size(1)
    for _ in range(n):
        cx, cy = x + rnd.uniform(3, w - 3), y + rnd.uniform(3, h - 3)
        L = rnd.uniform(2, 6)
        Gimp.context_set_foreground(color(rnd.choice([(226, 196, 150), (214, 180, 128), (232, 208, 170)])))
        dx, dy = (L, rnd.uniform(-1, 1)) if horizontal else (rnd.uniform(-1, 1), L)
        Gimp.pencil(a.lay, [float(cx), float(cy), float(cx + dx), float(cy + dy)])


def worn(a, tile):
    """Worn-finish regions: oak_worn (drawer fronts, grain across) and oak_edge (pull stiles)."""
    # oak_worn: the tile turned 90 degrees
    x, y, w, h = a.rect("oak_worn")
    rot = tile.duplicate()
    rot.rotate(Gimp.RotationType.DEGREES90)
    add_layer_from(a.img, rot, "oak_worn", x, y)
    rot.delete()
    x2, y2, w2, h2 = a.rect("oak_edge")
    add_layer_from(a.img, tile, "oak_edge", x2, y2)
    a.lay = flatten(a.img)
    pale = (224, 168, 104)
    grime = (74, 46, 24)
    r = (x, y, w, h)
    _soft_rect(a, (x - 10, y - 10, w + 20, 16), r, pale, 0.4, 8)          # top edge rubbed by fingers
    _blot(a.img, a.lay, x + w / 2, y + h / 2, 46, 30, pale, 0.16, 14)     # around the knob
    _soft_rect(a, (x - 10, y + h - 8, w + 20, 18), r, grime, 0.35, 8)     # bottom edge grime
    _soft_rect(a, (x - 10, y - 10, 12, h + 20), r, grime, 0.18, 6)
    _soft_rect(a, (x + w - 2, y - 10, 12, h + 20), r, grime, 0.18, 6)
    _nicks(a, (x, y, w, 24), 6, True)
    _nicks(a, (x, y + 24, w, h - 24), 4, True)
    r2 = (x2, y2, w2, h2)
    _blot(a.img, a.lay, x2 + w2 / 2, y2 + h2 * 0.36, 58, 46, pale, 0.3, 16)   # grab zone under the pull
    _soft_rect(a, (x2 - 10, y2 + h2 - 10, w2 + 20, 20), r2, grime, 0.35, 8)
    _soft_rect(a, (x2 - 10, y2 - 10, w2 + 20, 12), r2, pale, 0.25, 6)
    _nicks(a, (x2, y2 + 10, w2, h2 - 20), 10, False)
    a.material("oak_worn", 0.0, 0.26)
    a.material("oak_edge", 0.0, 0.26)
