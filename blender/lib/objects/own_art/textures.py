"""own_art atlas (2048): Cassidy's five pieces, each rectified straight-on from its best photo
in Reference/ with rectify(), colour-balanced with per-photo gains; the signatures are kept
(not blurred). The albedo is git-ignored on purpose: the art ships only in the VRChat upload.
Runs inside headless GIMP with gimp_textures.py's helpers in scope."""

import os

exec(open(os.path.join(ROOT, "blender", "lib", "objects", "own_art", "layout.py"),
          encoding="utf-8").read())

CHANNELS = (Gimp.HistogramChannel.RED, Gimp.HistogramChannel.GREEN, Gimp.HistogramChannel.BLUE)


def balance(lay, gains):
    """Scale each channel by its gain (levels with the white point pulled in)."""
    for ch, g in zip(CHANNELS, gains):
        lay.levels(ch, 0.0, min(1.0, 1.0 / g), True, 1.0, 0.0, 1.0, True)


def photo(a, region, smooth):
    x, y, w, h = a.rect(region)
    name, quad = PHOTOS[region]
    # warp at 2x, then scale down with LoHalo, so the big minification doesn't alias
    img = rectify(os.path.join(REF, name), quad, w * 2, h * 2)
    Gimp.context_set_interpolation(Gimp.InterpolationType.LOHALO)
    img.scale(w, h)
    lay = img.get_layers()[0]
    balance(lay, GAINS[name])
    for bx, by, bw, bh in BLURS.get(region, []):
        # feathered, so the blurred patch has no hard edge
        img.select_rectangle(Gimp.ChannelOps.REPLACE, bx, by, bw, bh)
        Gimp.Selection.feather(img, 14.0)
        for _ in range(3):
            gegl(lay, "gegl:gaussian-blur", std_dev_x=6.0, std_dev_y=6.0)
        Gimp.Selection.none(img)
    add_layer_from(a.img, img, region, x, y)
    img.delete()
    a.lay = flatten(a.img)
    a.material(region, 0.0, smooth)


def build():
    a = Atlas(ATLAS)
    photo(a, "cat", 0.3)            # acrylic on canvas
    photo(a, "abstract", 0.3)
    photo(a, "rabbit", 0.1)         # paper and mat
    photo(a, "waterfall", 0.12)
    photo(a, "isopod", 0.1)
    photo(a, "abstract_side", 0.3)
    for region, (rgb, smooth) in SOLIDS.items():
        a.fill(region, rgb, 0.0, smooth, noise=0.015 if region != "mat_white" else 0.0)
    a.save()
