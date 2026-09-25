"""Living wall art atlas (1024). The framed picture and the canvas are the real images,
rectified from the living-room capture frames by Reference/bedroom_fixtures_work/final.py
(local-only); the map poster (a fictional city from a 1985 text game) is rectified from
Cassidy's close-up photo IMG_1505 by Reference/living_wall_art_work/v2/photo_prep.py.

The diploma is painted here from scratch for a made-up school (nothing on it is real; the
graduate line reads "Cassidy Company" at Cassidy's request): blackletter school name and degree, italic body lines,
a gold foil seal, two signature squiggles, plus the mat's medallion, gold lettering and
the tassel. It is painted at 3x in its own image and scaled into the atlas.
Runs inside headless GIMP."""

import math
import os
import random

exec(open(os.path.join(ROOT, "blender", "lib", "objects", "living_wall_art", "layout.py"),
          encoding="utf-8").read())
FINAL = os.path.join(REF, "living_wall_art_work", "final")

SCHOOL = "Quillmere Polytechnic Institute"
GRADUATE = "Cassidy Company"
DEGREE = "Bachelor of Science"
INK = (34, 30, 28)
GOLD = (200, 162, 78)
GOLD_DK = (140, 104, 40)
GOLD_LT = (236, 208, 132)
CREAM = (240, 234, 216)

FONTS = {}


def font(name):
    if name not in FONTS:
        FONTS[name] = Gimp.fonts_get_list(name)[0]
    return FONTS[name]


def text(img, s, face, size, rgb, cx, y, anchor="c"):
    """One line of text; cx is the centre x (anchor c), left x (l) or right x (r)."""
    t = Gimp.TextLayer.new(img, s, font(face), float(size), Gimp.Unit.pixel())
    img.insert_layer(t, None, 0)
    t.set_color(color(rgb))
    w = t.get_width()
    x = {"c": cx - w / 2, "l": cx, "r": cx - w}[anchor]
    t.set_offsets(round(x), round(y))
    return t


def stroke(img, lay, pts, size, rgb):
    Gimp.context_set_foreground(color(rgb))
    Gimp.context_set_brush_size(size)
    Gimp.context_set_opacity(100.0)
    flat = [c for p in pts for c in p]
    Gimp.paintbrush_default(lay, flat)


def squiggle(img, lay, x0, y0, w, h, seed):
    """A made-up signature: a tall looped capital, then running cursive humps of random
    heights, a second capital part-way, and an underline flick. Spells nothing."""
    rnd = random.Random(seed)
    pts = []
    # capital: a tall slanted loop
    for i in range(41):
        a = 2 * math.pi * i / 40
        pts.append((x0 + w * 0.06 + w * 0.05 * math.sin(a) + h * 0.25 * (1 - math.cos(a)) * 0.3,
                    y0 + h * 0.55 - h * 0.5 * math.sin(a / 2) ** 2 * 1.1 + h * 0.08 * math.cos(a)))
    x, k = x0 + w * 0.1, 0
    while x < x0 + w * 0.95:
        k += 1
        tall = rnd.random() < 0.18 or k == 5
        hh = h * (0.85 if tall else rnd.uniform(0.22, 0.42))
        step = w * rnd.uniform(0.045, 0.07)
        for i in range(1, 13):
            t = i / 12
            pts.append((x + step * t - step * 0.25 * math.sin(2 * math.pi * t),
                        y0 + h * 0.62 - hh * math.sin(math.pi * t)))
        x += step
    pts = [(px + (py - y0) * 0.25, py) for px, py in pts]      # right slant
    stroke(img, lay, pts, 4.0, (40, 44, 70))
    fl = [(x0 + w * 0.05, y0 + h * 0.95), (x0 + w * 0.55, y0 + h * 0.86), (x0 + w * 1.02, y0 + h * 0.7)]
    stroke(img, lay, fl, 3.0, (40, 44, 70))


def gold_disc(img, lay, cx, cy, r, points=36):
    """Gold foil seal: serrated rim, rings of dots, a star in the middle."""
    for k in range(points):
        a = 2 * math.pi * k / points
        px, py = cx + r * 0.94 * math.cos(a), cy + r * 0.94 * math.sin(a)
        fill_ellipse(img, lay, (px - r * 0.11, py - r * 0.11, px + r * 0.11, py + r * 0.11), GOLD)
    fill_ellipse(img, lay, (cx - r * 0.95, cy - r * 0.95, cx + r * 0.95, cy + r * 0.95), GOLD)
    fill_ellipse(img, lay, (cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78), GOLD_DK)
    fill_ellipse(img, lay, (cx - r * 0.74, cy - r * 0.74, cx + r * 0.74, cy + r * 0.74), GOLD)
    for k in range(28):
        a = 2 * math.pi * k / 28
        px, py = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
        fill_ellipse(img, lay, (px - r * 0.035, py - r * 0.035, px + r * 0.035, py + r * 0.035), GOLD_DK)
    fill_ellipse(img, lay, (cx - r * 0.48, cy - r * 0.48, cx + r * 0.48, cy + r * 0.48), GOLD_LT)
    fill_ellipse(img, lay, (cx - r * 0.44, cy - r * 0.44, cx + r * 0.44, cy + r * 0.44), GOLD)
    star(img, lay, cx, cy, r * 0.36, r * 0.15, GOLD_DK)


def star(img, lay, cx, cy, ro, ri, rgb):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + math.pi * k / 5
        rr = ro if k % 2 == 0 else ri
        pts += [cx + rr * math.cos(a), cy + rr * math.sin(a)]
    img.select_polygon(Gimp.ChannelOps.REPLACE, pts)
    Gimp.context_set_foreground(color(rgb))
    lay.edit_fill(Gimp.FillType.FOREGROUND)
    Gimp.Selection.none(img)


def paint(a, region, w3, h3, draw):
    """Paint at 3x in a scratch image, flatten, and drop it into the atlas region."""
    img, lay = new_image(w3, h3, region)
    draw(img, lay, w3, h3)
    flatten(img)
    x, y, w, h = a.rect(region)
    img.scale(w, h)
    add_layer_from(a.img, img, region, x, y)
    img.delete()


def diploma(img, lay, W, H):
    fill_rect(img, lay, (0, 0, W, H), CREAM)
    grain(img, lay, (0, 0, W, H), 0.012, 1.5)
    # double rule border
    for inset, t in ((26, 5), (40, 2)):
        for r in ((inset, inset, W - 2 * inset, t), (inset, H - inset - t, W - 2 * inset, t),
                  (inset, inset, t, H - 2 * inset), (W - inset - t, inset, t, H - 2 * inset)):
            fill_rect(img, lay, r, (120, 96, 60))
    cx = W / 2
    text(img, SCHOOL, "Old English Text MT", 76, INK, cx, 96)
    text(img, "The Trustees, on the recommendation of the Faculty, have conferred upon",
         "Book Antiqua Italic", 30, INK, cx, 232)
    text(img, GRADUATE, "Old English Text MT", 74, INK, cx, 290)
    text(img, "the degree of", "Book Antiqua Italic", 30, INK, cx, 398)
    text(img, DEGREE, "Old English Text MT", 84, INK, cx, 446)
    text(img, "with all the rights, privileges and honours pertaining thereto.",
         "Book Antiqua Italic", 28, INK, cx, 566)
    text(img, "Given at Quillmere on the fourteenth day of June.", "Book Antiqua Italic", 28, INK, cx, 610)
    flatten(img)
    lay = img.get_layers()[0]
    # signature lines, squiggles and titles
    for sx, title, seed in ((150, "President of the Institute", 11), (W - 450, "Dean of the Faculty", 23)):
        squiggle(img, lay, sx + 20, 770, 260, 70, seed)
        fill_rect(img, lay, (sx, 860, 300, 3), INK)
        text(img, title, "Book Antiqua Italic", 24, INK, sx + 150, 870)
    # foil ribbon tails under the seal
    for dx in (-1, 1):
        img.select_polygon(Gimp.ChannelOps.REPLACE, [cx + dx * 30, 880, cx + dx * 80, 880,
                                                     cx + dx * 92, 962, cx + dx * 64, 940, cx + dx * 40, 964])
        Gimp.context_set_foreground(color((170, 40, 44)))
        lay.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.Selection.none(img)
    gold_disc(img, lay, cx, 830, 92)


def medallion(img, lay, W, H):
    fill_rect(img, lay, (0, 0, W, H), (22, 22, 24))
    c, r = W / 2, W / 2 - 6
    fill_ellipse(img, lay, (c - r, c - r, c + r, c + r), GOLD)
    fill_ellipse(img, lay, (c - r * 0.86, c - r * 0.86, c + r * 0.86, c + r * 0.86), GOLD_DK)
    fill_ellipse(img, lay, (c - r * 0.82, c - r * 0.82, c + r * 0.82, c + r * 0.82), CREAM)
    # crest: a red shield with a gold quill and a star
    sw, top = r * 0.9, c - r * 0.5
    img.select_polygon(Gimp.ChannelOps.REPLACE, [c - sw / 2, top, c + sw / 2, top, c + sw / 2, top + r * 0.55,
                                                 c, top + r * 1.05, c - sw / 2, top + r * 0.55])
    Gimp.context_set_foreground(color((168, 36, 40)))
    lay.edit_fill(Gimp.FillType.FOREGROUND)
    Gimp.Selection.none(img)
    stroke(img, lay, [(c - sw * 0.2, top + r * 0.78), (c + sw * 0.28, top + r * 0.15)], 6.0, GOLD)
    star(img, lay, c - sw * 0.18, top + r * 0.25, r * 0.16, r * 0.07, GOLD_LT)


def plate(img, lay, W, H):
    fill_rect(img, lay, (0, 0, W, H), (22, 22, 24))
    t = text(img, SCHOOL, "Old English Text MT", 60, GOLD, W / 2, 0)
    t.set_offsets(round((W - t.get_width()) / 2), round((H - t.get_height()) / 2))


def tassel(img, lay, W, H):
    fill_rect(img, lay, (0, 0, W, H), (30, 28, 30))
    # glass tube: pale edges
    fill_rect(img, lay, (6, 0, W - 12, H), (58, 56, 60))
    # red cord strands, gathered under a gold charm near the top
    rnd = random.Random(5)
    for k in range(18):
        x = W * 0.3 + rnd.uniform(0, W * 0.4)
        stroke(img, lay, [(W / 2, H * 0.16), (x, H * 0.3), (x + rnd.uniform(-4, 4), H * 0.93)], 5.0,
               (150 + rnd.randint(-20, 20), 30, 34))
    fill_rect(img, lay, (W * 0.3, H * 0.12, W * 0.4, H * 0.06), (170, 36, 40))
    fill_round_rect(img, lay, (W * 0.2, H * 0.04, W * 0.8, H * 0.12), 8, GOLD)
    fill_rect(img, lay, (W * 0.48, 0, W * 0.04, H * 0.05), GOLD_DK)
    fill_rect(img, lay, (0, H * 0.95, W, H * 0.05), (220, 218, 210))     # the tube's end cap
    fill_rect(img, lay, (8, 0, 5, H), (150, 150, 156))                  # glass glint
    fill_rect(img, lay, (W - 16, 0, 3, H), (110, 110, 116))


def photo(a, region, smooth):
    x, y, w, h = a.rect(region)
    src = load(os.path.join(FINAL, region + ".png"))
    src.scale(w, h)
    add_layer_from(a.img, src, region, x, y)
    src.delete()
    a.material(region, 0.0, smooth)


def build():
    a = Atlas(ATLAS)
    photo(a, "pic_west", 0.6)
    photo(a, "canvas", 0.2)
    photo(a, "map", 0.2)
    a.fill("canvas_side", (150, 160, 175), 0.0, 0.2)
    a.fill("frame_black", (20, 20, 22), 0.0, 0.45)
    a.fill("frame_cherry", (50, 18, 17), 0.0, 0.55, noise=0.03, blur=1.0)
    a.fill("mat_black", (22, 22, 24), 0.0, 0.2)
    a.fill("paper", (236, 234, 226), 0.0, 0.2)
    a.fill("tassel_side", (120, 36, 36), 0.0, 0.5)
    paint(a, "diploma_sheet", 1200, 1014, diploma)
    a.material("diploma_sheet", 0.0, 0.25)
    paint(a, "dip_seal", 360, 360, medallion)
    a.material("dip_seal", 0.0, 0.2)
    paint(a, "dip_plate", 828, 120, plate)
    a.material("dip_plate", 0.0, 0.2)
    paint(a, "tassel", 144, 1020, tassel)
    a.material("tassel", 0.0, 0.8)   # behind glass
    # gold foil reads metallic: the sheet's seal, the medallion rim and the lettering
    x, y, w, h = a.rect("diploma_sheet")
    sx, sy, sr = x + w / 2, y + 830 * h / 1014, 92 * w / 1200
    fill_ellipse(a.mimg, a.mlay, (sx - sr, sy - sr, sx + sr, sy + sr), (200, 0, 0, 0.6))
    x, y, w, h = a.rect("dip_seal")
    fill_ellipse(a.mimg, a.mlay, (x + 2, y + 2, x + w - 2, y + h - 2), (200, 0, 0, 0.6))
    a.material("dip_plate", 0.6, 0.5)
    a.save()
