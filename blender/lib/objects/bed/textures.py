"""bed atlas (headless GIMP, gimp_textures.py helpers in scope).

Light aqua fleece with soft lighter/darker mottling (the pile catches light unevenly in
the photos) and fine grain; cool grey pillowcase; white sheet; dark grey skirt with
soft vertical pleat streaks; espresso frame; black casters. Colours from the survey
crops, lifted from their dim exposure (blanket ~#9cc0c4).

Wear: the fleece's crushed, matted pile (the swirly lighter/darker patches all over the
blanket in the photos) comes from the photo itself: a flat patch of the blanket top near
the foot in bedroom capture frame 012224, rectified, lighting flattened with a wide blur
so the matting survives, made seamless and tiled. Nothing but fleece is in the patch."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "bed", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
R = random.Random(23)
FLEECE_PHOTO = os.path.join(REF, "bedroom-lidar-splat", "LidarSeries_20260925_011425_918",
                            "COLMAP_Text_Model", "images", "wide_20260925_012224_928.jpg")
# flat blanket top just behind the foot edge (TL, TR, BR, BL in the unrotated frame)
FLEECE_QUAD = [(1030, 1109), (1030, 259), (1330, 139), (1330, 1279)]
FLEECE = (140, 180, 192)


def blur_region(a, region, sigma):
    x, y, w, h = a.rect(region)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=sigma, std_dev_y=sigma)
    Gimp.Selection.none(a.img)


def mottle(a, region, base, cols, n, rmin, rmax, sigma):
    x0, y0, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x0, y0, w, h), base)
    for _ in range(n):
        cx, cy = x0 + R.randint(0, w), y0 + R.randint(0, h)
        rx, ry = R.randint(rmin, rmax), R.randint(rmin, rmax)
        fill_ellipse(a.img, a.lay, (max(cx - rx, x0), max(cy - ry, y0),
                                    min(cx + rx, x0 + w), min(cy + ry, y0 + h)), R.choice(cols))
    blur_region(a, region, sigma)


def build():
    random.seed(23)
    a = Atlas(ATLAS)
    img, lay = a.img, a.lay

    # aqua fleece: photo patch (matted pile). One 512 x 256 tile covers ~53 x 27 in of
    # the ~80 in unfolded blanket, laid in offset rows so the repeat doesn't line up;
    # copies that spill past the region are painted over by the regions filled below.
    x, y, w, h = a.rect("blanket")
    fill_rect(img, lay, (x, y, w, h), FLEECE)
    tile = rectify(FLEECE_PHOTO, FLEECE_QUAD, 768, 384)
    tile.crop(768 - 24, 384 - 24, 12, 12)          # drop the warp's soft border rows
    flatten_lighting(tile, 90, FLEECE, detail=75.0)
    tw, th = 512, 256
    tile.scale(tw, th)
    gegl(tile.get_layers()[0], "gegl:tile-seamless")
    for j in range(3):
        off = -(j * 197) % tw
        for i in range(-1, 2):
            px = x + off + i * tw
            if px + tw > x and px < x + w:
                add_layer_from(a.img, tile, "fleece", px, y + j * th)
    a.lay = lay = flatten(a.img)
    tile.delete()
    for j in (1, 2):                                # soften the row joins
        img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y + j * th - 4, w, 8)
        gegl(lay, "gegl:gaussian-blur", std_dev_x=0.5, std_dev_y=3.0)
    Gimp.Selection.none(img)
    grain(img, lay, (x, y, w, h), 0.03, 0.8)
    a.material("blanket", 0.0, 0.06)

    # grey pillowcase with a few soft creases
    mottle(a, "pillow", (122, 124, 130), [(136, 138, 144, 0.5), (108, 110, 116, 0.5)], 30, 8, 30, 6.0)
    x, y, w, h = a.rect("pillow")
    for _ in range(7):
        cx = x + R.randint(20, w - 20)
        fill_rect(img, lay, (cx, y, R.randint(2, 4), h), (118, 120, 124, 0.5))
    blur_region(a, "pillow", 3.0)
    grain(img, lay, a.rect("pillow"), 0.03, 0.8)
    a.material("pillow", 0.0, 0.1)

    # white sheet
    mottle(a, "sheet", (214, 214, 212), [(226, 226, 224, 0.5), (196, 196, 196, 0.5)], 30, 8, 30, 5.0)
    grain(img, lay, a.rect("sheet"), 0.02, 0.8)
    a.material("sheet", 0.0, 0.12)

    # dark grey skirt with pleat streaks
    x, y, w, h = a.rect("skirt")
    fill_rect(img, lay, (x, y, w, h), (62, 62, 64))
    for k in range(0, w, 12):
        fill_rect(img, lay, (x + k + R.randint(0, 4), y, R.randint(3, 6), h),
                  R.choice([(52, 52, 54, 0.7), (74, 74, 76, 0.6)]))
    blur_region(a, "skirt", 2.5)
    grain(img, lay, (x, y, w, h), 0.03, 0.8)
    a.material("skirt", 0.0, 0.08)

    a.fill("frame", (40, 30, 24), 0.2, 0.35, noise=0.04, blur=1.0)
    a.fill("caster", (20, 20, 21), 0.0, 0.45, noise=0.02, blur=0.6)
    a.save()
