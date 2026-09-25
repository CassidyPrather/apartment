"""kitchen_cabinets atlas (runs in headless GIMP with gimp_textures.py's helpers in scope).

Oak: photo-derived from the flat centre panel of one upper door in the photo through the
bedroom door (only the panel, no people or objects), lighting flattened to the sampled
honey-oak colour, made seamless and tiled across the oak region with alternate columns
offset by half a tile to hide the repeat. Everything else is a flat fill; the counter,
steel and appliance colours are guesses (the photo doesn't show them clearly).
"""

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
OAK = (178, 116, 58)             # honey oak: the photo doors under warm light sample 180,117,64 (shaded) to 236,173,102 (lit)
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
    a.fill("counter", (208, 202, 190), 0.0, 0.35, noise=0.14, blur=0.7)
    a.fill("steel", (172, 174, 176), 1.0, 0.55, noise=0.05, blur=0.5)
    a.fill("nickel", (182, 180, 174), 1.0, 0.6, noise=0.04, blur=0.5)
    a.fill("toe", (74, 52, 32), 0.0, 0.2, noise=0.05, blur=1.0)
    a.fill("white", (234, 234, 230), 0.0, 0.6)
    a.fill("panel_black", (30, 30, 32), 0.0, 0.5)
    a.fill("drain", (70, 70, 72), 1.0, 0.4)
    # unused corner of the atlas: neutral
    fill_rect(a.img, a.lay, (512, 960, 128, 64), (128, 128, 128))
    fill_rect(a.img, a.lay, (640, 832, 128, 192), (128, 128, 128))
    fill_rect(a.img, a.lay, (768, 896, 256, 128), (128, 128, 128))
    a.save()
