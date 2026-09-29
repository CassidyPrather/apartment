"""Window blinds atlas (512): off-white PVC vanes with a faint vertical emboss, white
headrail, dark carrier slot, clear-ish wand. Runs inside headless GIMP."""

import random

ATLAS = {
    "name": "window_blinds",
    "size": 512,
    "regions": {
        "vane": (0, 0, 256, 512),
        "rail": (256, 0, 256, 256),
        "carrier": (256, 256, 128, 128),
        "wand": (384, 256, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("vane", (232, 231, 224), 0.0, 0.25, noise=0.025, blur=3.0)
    # wear, subtle: vane-to-vane tint variation (the vanes box-project across the whole
    # blind set, so vertical streaks land on different vanes) and faint grime along the
    # bottoms where the vanes get pushed aside
    x, y, w, h = a.rect("vane")
    rnd = random.Random(5)
    for i in range(60):
        cx, cw = x + rnd.uniform(0, w), rnd.uniform(2, 6)
        tint = rnd.choice(((214, 208, 190), (240, 240, 236), (222, 218, 204)))
        fill_rect(a.img, a.lay, (round(cx), y, round(cw), h), tint + (rnd.uniform(0.08, 0.2),))
    for i in range(40):
        cx, cw = x + rnd.uniform(0, w), rnd.uniform(3, 12)
        ch = rnd.uniform(10, 36)
        fill_rect(a.img, a.lay, (round(cx), round(y + h - ch), round(cw), round(ch)),
                  (160, 154, 140, rnd.uniform(0.05, 0.12)))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x + 2, y + 2, w - 4, h - 4)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=1.2, std_dev_y=6.0)
    Gimp.Selection.none(a.img)
    a.fill("rail", (238, 238, 233), 0.0, 0.40, noise=0.015, blur=1.5)
    a.fill("carrier", (70, 70, 68), 0.0, 0.2)
    a.fill("wand", (214, 218, 216), 0.0, 0.7)
    fill_rect(a.img, a.lay, (256, 384, 256, 128), (238, 238, 233))
    fill_rect(a.mimg, a.mlay, (256, 384, 256, 128), (0, 0, 0, 0.4))
    a.save()
