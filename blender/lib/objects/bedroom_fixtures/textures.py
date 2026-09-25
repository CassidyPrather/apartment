"""Bedroom fixtures atlas (1024). Every picture is a simple stand-in painted from scratch
(no copyrighted artwork, no people): a moon over the sea, a space scene, a holiday tree,
a black-and-white landscape, a green botanical, a purple abstract, an abstract colour
strip in place of the photo strip, and bright abstract cards. Plus blinds, base stations,
smoke detector and thermostat. Runs inside headless GIMP."""

import math
import random

ATLAS = {
    "name": "bedroom_fixtures",
    "size": 1024,
    "regions": {
        "art_moon": (0, 0, 352, 240),
        "art_space": (352, 0, 240, 340),
        "art_tree": (592, 0, 256, 313),
        "art_center": (848, 0, 160, 194),
        "art_strip": (0, 250, 340, 130),
        "art_purple": (0, 400, 224, 150),
        "art_south": (224, 400, 106, 128),
        "mid_poster": (352, 368, 144, 192),
        "card_a": (512, 368, 64, 92),
        "card_b": (576, 368, 64, 92),
        "card_c": (640, 368, 40, 64),
        "card_d": (704, 368, 64, 88),
        "corner_poster": (768, 368, 116, 160),
        "charms": (896, 368, 128, 160),
        "vane": (0, 640, 128, 384),
        "rail": (128, 640, 128, 128),
        "carrier": (128, 768, 64, 64),
        "wand": (192, 768, 64, 64),
        "frame_black": (256, 640, 64, 64),
        "mat_white": (320, 640, 64, 64),
        "paper": (384, 640, 64, 64),
        "bs_body": (448, 640, 64, 64),
        "bs_face": (512, 640, 128, 128),
        "bracket": (640, 640, 64, 64),
        "cable": (704, 640, 64, 64),
        "smoke": (768, 640, 128, 128),
        "thermo": (896, 640, 64, 64),
        "thermo_face": (896, 704, 128, 128),
        "ring": (960, 640, 64, 64),
    },
}

WHITE = (240, 238, 232)


def lerp(c0, c1, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))


def vgrad(a, rect, c0, c1, band=3):
    x, y, w, h = rect
    for r in range(0, h, band):
        fill_rect(a.img, a.lay, (x, y + r, w, min(band, h - r)), lerp(c0, c1, r / max(1, h - 1)))


CLIP = [None]


def clip(a, region):
    CLIP[0] = a.rect(region)


def _fill_sel(a, rgb):
    if CLIP[0] is not None:
        x, y, w, h = CLIP[0]
        a.img.select_rectangle(Gimp.ChannelOps.INTERSECT, x, y, w, h)
    if not Gimp.Selection.is_empty(a.img):
        Gimp.context_set_foreground(color(tuple(rgb[:3])))
        Gimp.context_set_opacity(100.0 * (rgb[3] if len(rgb) == 4 else 1.0))
        a.lay.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.context_set_opacity(100.0)
    Gimp.Selection.none(a.img)


def ell(a, cx, cy, rx, ry, rgb):
    a.img.select_ellipse(Gimp.ChannelOps.REPLACE, cx - rx, cy - ry, 2 * rx, 2 * ry)
    _fill_sel(a, rgb)


def poly(a, pts, rgb):
    flat = [float(v) for p in pts for v in p]
    a.img.select_polygon(Gimp.ChannelOps.REPLACE, flat)
    _fill_sel(a, rgb)


def blur(a, rect, s):
    x, y, w, h = rect
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=s, std_dev_y=s)
    Gimp.Selection.none(a.img)


def border(a, rect, px, rgb=WHITE):
    x, y, w, h = rect
    fill_rect(a.img, a.lay, (x, y, w, px), rgb)
    fill_rect(a.img, a.lay, (x, y + h - px, w, px), rgb)
    fill_rect(a.img, a.lay, (x, y, px, h), rgb)
    fill_rect(a.img, a.lay, (x + w - px, y, px, h), rgb)


def stars(a, rect, n, rgb, rmax=1.6):
    x, y, w, h = rect
    for _ in range(n):
        r = random.uniform(0.6, rmax)
        ell(a, x + random.uniform(4, w - 4), y + random.uniform(4, h - 4), r, r, rgb)


def star5(a, cx, cy, r, rgb):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    poly(a, pts, rgb)


def moon(a):
    clip(a, "art_moon")
    r = a.rect("art_moon")
    x, y, w, h = r
    inner = (x + 12, y + 12, w - 24, h - 24)
    ix, iy, iw, ih = inner
    vgrad(a, inner, (22, 26, 78), (58, 92, 170))
    stars(a, inner, 40, (250, 236, 170))
    for sx, sy, sr in ((0.12, 0.3, 14), (0.3, 0.18, 7), (0.72, 0.15, 8), (0.9, 0.2, 7), (0.2, 0.62, 6)):
        star5(a, ix + iw * sx, iy + ih * sy, sr, (250, 214, 120))
    # sea band
    fill_rect(a.img, a.lay, (ix, iy + round(ih * 0.72), iw, ih - round(ih * 0.72)), (20, 30, 70))
    for i in range(12):
        fill_rect(a.img, a.lay, (ix + random.randint(0, iw - 40), iy + round(ih * 0.74) + i * 4, random.randint(15, 40), 1),
                  (90, 120, 190))
    # crescent moon
    cx, cy, rr = ix + iw * 0.47, iy + ih * 0.42, ih * 0.33
    ell(a, cx, cy, rr, rr, (246, 200, 110))
    ell(a, cx + rr * 0.35, cy - rr * 0.18, rr * 0.85, rr * 0.85, (36, 46, 108))
    # big pale flower at the right, small flowers at the lower left
    for k in range(6):
        ang = k * math.pi / 3
        ell(a, ix + iw * 0.78 + 22 * math.cos(ang), iy + ih * 0.62 + 20 * math.sin(ang), 24, 22, (206, 208, 240))
    ell(a, ix + iw * 0.78, iy + ih * 0.62, 12, 12, (236, 236, 250))
    for k in range(7):
        ell(a, ix + random.uniform(8, iw * 0.3), iy + random.uniform(ih * 0.72, ih - 6), 7, 6, (150, 150, 210))
    blur(a, inner, 1.2)
    border(a, r, 12)
    a.material("art_moon", 0.0, 0.25)


def space(a):
    clip(a, "art_space")
    r = a.rect("art_space")
    x, y, w, h = r
    inner = (x + 12, y + 12, w - 24, h - 24)
    ix, iy, iw, ih = inner
    vgrad(a, inner, (18, 20, 58), (40, 40, 96))
    # nebula streaks
    for _ in range(40):
        cx, cy = ix + random.uniform(0, iw), iy + random.uniform(ih * 0.2, ih * 0.9)
        ell(a, cx, cy, random.uniform(12, 30), random.uniform(3, 7),
            random.choice([(170, 60, 110, 0.35), (90, 60, 160, 0.35), (60, 110, 170, 0.3)]))
    blur(a, inner, 4.0)
    stars(a, inner, 70, (230, 236, 255), 1.4)
    # ringed planet and a moon
    ell(a, ix + iw * 0.5, iy + ih * 0.33, 34, 34, (120, 170, 190))
    ell(a, ix + iw * 0.44, iy + ih * 0.29, 22, 22, (160, 205, 215))
    ell(a, ix + iw * 0.5, iy + ih * 0.33, 58, 8, (210, 225, 230, 0.8))
    ell(a, ix + iw * 0.5, iy + ih * 0.33, 46, 5, (40, 40, 96))
    ell(a, ix + iw * 0.2, iy + ih * 0.6, 12, 12, (150, 150, 190))
    ell(a, ix + iw * 0.8, iy + ih * 0.52, 9, 9, (190, 120, 160))
    # forest silhouette at the bottom
    for k in range(18):
        tx = ix + k * iw / 17
        th = random.uniform(30, 60)
        poly(a, [(tx - 9, iy + ih), (tx, iy + ih - th), (tx + 9, iy + ih)], (12, 22, 40))
    fill_rect(a.img, a.lay, (ix, iy + ih - 14, iw, 14), (12, 22, 40))
    border(a, r, 12)
    a.material("art_space", 0.0, 0.25)


def tree(a):
    clip(a, "art_tree")
    r = a.rect("art_tree")
    x, y, w, h = r
    vgrad(a, r, (250, 226, 214), (250, 236, 180))
    ell(a, x + w * 0.2, y + h * 0.25, 60, 14, (240, 170, 190, 0.6))
    blur(a, r, 6.0)
    fill_rect(a.img, a.lay, (x, y + round(h * 0.86), w, h - round(h * 0.86)), (190, 200, 220))
    cx = x + w * 0.52
    fill_rect(a.img, a.lay, (round(cx - 10), round(y + h * 0.78), 20, round(h * 0.1)), (110, 70, 45))
    for k, (top, bot, half) in enumerate(((0.1, 0.38, 50), (0.25, 0.58, 80), (0.42, 0.82, 110))):
        poly(a, [(cx, y + h * top), (cx - half, y + h * bot), (cx + half, y + h * bot)], (48, 110, 60))
        poly(a, [(cx, y + h * top), (cx + half, y + h * bot), (cx + half * 0.3, y + h * bot)], (38, 90, 50))
    star5(a, cx, y + h * 0.09, 12, (250, 220, 110))
    for _ in range(22):
        t = random.uniform(0.2, 0.8)
        half = 110 * (t - 0.08) / 0.74
        ell(a, cx + random.uniform(-half * 0.8, half * 0.8), y + h * t, 6, 6, (220, 60, 110))
    for gx, col in ((0.3, (200, 60, 70)), (0.7, (70, 90, 170)), (0.55, (230, 190, 90))):
        fill_rect(a.img, a.lay, (round(x + w * gx - 14), round(y + h * 0.85), 28, 22), col)
    blur(a, r, 0.8)
    a.material("art_tree", 0.0, 0.5)


def center_print(a):
    clip(a, "art_center")
    r = a.rect("art_center")
    x, y, w, h = r
    vgrad(a, r, (225, 222, 212), (180, 178, 170))
    # woodcut-style mountains and a sun, black on cream
    ell(a, x + w * 0.7, y + h * 0.25, 18, 18, (245, 242, 232))
    poly(a, [(x, y + h * 0.7), (x + w * 0.35, y + h * 0.3), (x + w * 0.6, y + h * 0.62), (x + w * 0.8, y + h * 0.45),
             (x + w, y + h * 0.65), (x + w, y + h), (x, y + h)], (60, 58, 55))
    poly(a, [(x, y + h * 0.85), (x + w * 0.5, y + h * 0.66), (x + w, y + h * 0.82), (x + w, y + h), (x, y + h)], (25, 24, 22))
    for i in range(10):
        fill_rect(a.img, a.lay, (x, y + 8 + i * 6, w, 1), (200, 198, 190))
    blur(a, r, 0.6)
    a.material("art_center", 0.0, 0.6)


def south_print(a):
    clip(a, "art_south")
    r = a.rect("art_south")
    x, y, w, h = r
    fill_rect(a.img, a.lay, r, (22, 34, 26))
    for _ in range(40):
        ell(a, x + random.uniform(10, w - 10), y + random.uniform(15, h - 25), random.uniform(6, 16),
            random.uniform(5, 12), random.choice([(150, 200, 90), (110, 170, 70), (180, 220, 130), (60, 110, 60)]))
    blur(a, r, 2.0)
    a.material("art_south", 0.0, 0.5)


def strip(a):
    clip(a, "art_strip")
    # abstract stand-in for a strip of photos: six soft colour panels on white card
    r = a.rect("art_strip")
    x, y, w, h = r
    fill_rect(a.img, a.lay, r, WHITE)
    cols = [((150, 200, 150), (230, 170, 190)), ((230, 180, 200), (140, 190, 140)), ((120, 180, 130), (200, 230, 190)),
            ((240, 190, 200), (170, 210, 160)), ((160, 210, 170), (230, 160, 180)), ((210, 230, 190), (130, 180, 140))]
    pw = (w - 14) / 6
    for i, (c0, c1) in enumerate(cols):
        px = round(x + 7 + i * pw + 2)
        vgrad(a, (px, y + 10, round(pw - 4), h - 20), c0, c1)
    blur(a, (x + 6, y + 9, w - 12, h - 18), 1.5)
    a.material("art_strip", 0.0, 0.3)


def purple(a):
    clip(a, "art_purple")
    r = a.rect("art_purple")
    x, y, w, h = r
    inner = (x + 10, y + 10, w - 20, h - 20)
    ix, iy, iw, ih = inner
    fill_rect(a.img, a.lay, inner, (110, 120, 60))
    for k in range(9):
        c = (130, 80, 170) if k % 2 == 0 else (230, 214, 130)
        x0 = ix + k * iw / 9 + 20
        poly(a, [(x0, iy + ih * 0.2), (x0 + iw / 9, iy + ih * 0.2), (x0 + iw / 9 - 40, iy + ih), (x0 - 40, iy + ih)], c)
    ell(a, ix + iw * 0.25, iy + ih * 0.45, 30, 28, (40, 40, 48))
    ell(a, ix + iw * 0.55, iy + ih * 0.4, 26, 26, (238, 222, 206))
    ell(a, ix + iw * 0.7, iy + ih * 0.12, 60, 16, (120, 80, 160))
    blur(a, inner, 1.5)
    border(a, r, 10)
    a.material("art_purple", 0.0, 0.25)


def bright(a, region, palette, bord=5):
    clip(a, region)
    r = a.rect(region)
    x, y, w, h = r
    fill_rect(a.img, a.lay, r, palette[0])
    for _ in range(14):
        ell(a, x + random.uniform(0, w), y + random.uniform(0, h), random.uniform(w * 0.1, w * 0.3),
            random.uniform(h * 0.06, h * 0.2), random.choice(palette[1:]))
    blur(a, r, 1.5)
    if bord:
        border(a, r, bord)
    a.material(region, 0.0, 0.3)


def charms(a):
    r = a.rect("charms")
    x, y, w, h = r
    fill_rect(a.img, a.lay, r, (230, 200, 220))
    # patches under each charm (mapped over the cluster, left = north)
    pal = [(236, 140, 190), (150, 180, 230), (245, 245, 245), (40, 40, 44), (30, 30, 50), (230, 170, 120)]
    for i in range(6):
        fill_rect(a.img, a.lay, (x + (i % 3) * w // 3, y + (i // 3) * h // 2, w // 3, h // 2), pal[i])
    grain(a.img, a.lay, r, 0.08, 2.0)
    a.material("charms", 0.0, 0.8)


def build():
    random.seed(7)
    a = Atlas(ATLAS)
    moon(a)
    space(a)
    tree(a)
    center_print(a)
    south_print(a)
    strip(a)
    purple(a)
    bright(a, "mid_poster", [(240, 230, 90), (236, 120, 180), (80, 200, 190), (250, 250, 240), (120, 70, 150)], 0)
    bright(a, "card_a", [(30, 30, 40), (236, 110, 170), (120, 210, 220), (250, 220, 90)])
    bright(a, "card_b", [(90, 120, 90), (230, 200, 120), (120, 170, 200), (200, 150, 110)])
    bright(a, "card_c", [(210, 180, 130), (230, 210, 170), (180, 150, 110)], 3)
    bright(a, "card_d", [(80, 170, 230), (236, 110, 140), (250, 240, 230), (240, 200, 90)])
    bright(a, "corner_poster", [(90, 190, 210), (236, 120, 170), (250, 230, 100), (140, 90, 170)], 0)
    charms(a)
    CLIP[0] = None
    a.fill("vane", (232, 231, 224), 0.0, 0.25, noise=0.025, blur=3.0)
    a.fill("rail", (236, 236, 231), 0.0, 0.4, noise=0.015, blur=1.5)
    a.fill("carrier", (60, 60, 58), 0.0, 0.2)
    a.fill("wand", (214, 218, 216), 0.0, 0.7)
    a.fill("frame_black", (20, 20, 22), 0.0, 0.45)
    a.fill("mat_white", (242, 241, 236), 0.0, 0.2, noise=0.01)
    a.fill("paper", (244, 243, 238), 0.0, 0.2)
    a.fill("bs_body", (28, 28, 30), 0.0, 0.3, noise=0.015)
    a.fill("bs_face", (12, 12, 14), 0.0, 0.85)
    a.fill("bracket", (26, 26, 28), 0.0, 0.35)
    a.fill("cable", (40, 40, 42), 0.0, 0.3)
    a.fill("smoke", (238, 237, 232), 0.0, 0.35, noise=0.01)
    rx, ry, rw, rh = a.rect("smoke")
    for k in range(4):
        fill_rect(a.img, a.lay, (rx + 20, ry + 30 + k * 18, rw - 40, 4), (210, 209, 204))
    a.fill("thermo", (236, 235, 230), 0.0, 0.35)
    a.fill("thermo_face", (236, 235, 230), 0.0, 0.4)
    tx, ty, tw, th = a.rect("thermo_face")
    fill_rect(a.img, a.lay, (tx + 30, ty + 30, tw - 60, 36), (120, 132, 128))
    for k in range(3):
        fill_rect(a.img, a.lay, (tx + 30 + k * 26, ty + 86, 16, 10), (200, 200, 196))
    a.fill("ring", (190, 170, 150), 0.9, 0.7)
    a.save()
