"""Living wall art atlas (1024). The framed picture and the canvas are the real images,
rectified from the living-room capture frames by Reference/bedroom_fixtures_work/final.py
(local-only). The town-map poster and the certificate are neutral stand-ins (privacy): a
plain abstract print and a blank cream sheet. Runs inside headless GIMP."""

import os

exec(open(os.path.join(ROOT, "blender", "lib", "objects", "living_wall_art", "layout.py"),
          encoding="utf-8").read())
FINAL = os.path.join(REF, "living_wall_art_work", "final")


def photo(a, region, smooth):
    x, y, w, h = a.rect(region)
    src = load(os.path.join(FINAL, region + ".png"))
    src.scale(w, h)
    add_layer_from(a.img, src, region, x, y)
    src.delete()
    a.material(region, 0.0, smooth)


def map_standin(a):
    # soft abstract on cream paper: a lavender band and pale green blocks, no streets or text
    x, y, w, h = a.rect("map_standin")
    fill_rect(a.img, a.lay, (x, y, w, h), (236, 233, 222))
    fill_rect(a.img, a.lay, (x + 16, y + 16, w - 32, h - 32), (222, 220, 212))
    for i in range(8):
        fill_ellipse(a.img, a.lay, (x + 200 + i * 22, y + 10 + i * 18, x + 250 + i * 22, y + 40 + i * 18), (150, 146, 196))
    for bx, by in ((60, 110), (140, 150), (240, 120), (300, 170), (100, 190)):
        fill_rect(a.img, a.lay, (x + bx, y + by, 50, 26), (196, 214, 150))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x + 16, y + 16, w - 32, h - 32)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=4.0, std_dev_y=4.0)
    Gimp.Selection.none(a.img)
    a.material("map_standin", 0.0, 0.2)


def build():
    a = Atlas(ATLAS)
    photo(a, "pic_west", 0.6)
    photo(a, "canvas", 0.2)
    map_standin(a)
    a.fill("canvas_side", (150, 160, 175), 0.0, 0.2)
    a.fill("frame_black", (20, 20, 22), 0.0, 0.45)
    a.fill("frame_cherry", (70, 24, 22), 0.0, 0.55, noise=0.03, blur=1.0)
    a.fill("mat_black", (22, 22, 24), 0.0, 0.2)
    a.fill("diploma_sheet", (238, 232, 212), 0.0, 0.2, noise=0.01)
    a.fill("tassel", (120, 40, 36), 0.0, 0.3)
    a.fill("paper", (240, 238, 230), 0.0, 0.2)
    a.save()
