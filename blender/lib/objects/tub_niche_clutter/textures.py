"""tub_niche_clutter atlas (1024): a palette of flat swatches for plain plastic, glass,
metal and cloth; bottle labels and box prints with parody wordmarks (logos/*.svg:
Lathertron, Snowstopper, Sprig & Twig, Plumbubble, Smudgebuster, Fluffballs, Gnatnap,
Picnic Panic, Rolly Polly); terry cloth for the towels and rags; mesh for the loofahs and
the mesh bag; the earring stand's backing with painted earrings. Procedural, drawn from
scratch; medicine and pest boxes carry only unreadable fine-print bars and blank barcodes."""

import ast
import os
import random

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "tub_niche_clutter")


def _const(name):
    tree = ast.parse(open(os.path.join(_PKG, "object.py"), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise RuntimeError(name + " not found in object.py")


ATLAS = _const("ATLAS")
PALETTE = _const("PALETTE")
LOGOS = os.path.join(_PKG, "logos")
WHITE = (246, 246, 242)


def put_logo(a, name, cx, cy, w):
    lg = load(os.path.join(LOGOS, name + ".svg"))
    h = round(lg.get_height() * w / lg.get_width())
    lg.scale(w, h)
    add_layer_from(a.img, lg, name, int(cx - w / 2), int(cy - h / 2))
    lg.delete()
    a.lay = flatten(a.img)


def fine_print(a, x, y, w, h, rng, col=(120, 118, 116), pitch=7, bar=2):
    for j in range(2, h - 2, pitch):
        k = x + 2
        while k < x + w - 8:
            L = rng.randint(5, 26)
            fill_rect(a.img, a.lay, (k, y + j, min(L, x + w - 2 - k), bar), col)
            k += L + rng.randint(3, 7)


def barcode(a, x, y, w, h, rng):
    fill_rect(a.img, a.lay, (x, y, w, h), WHITE)
    i = 3
    while i < w - 3:
        t = rng.choice([1, 1, 2, 3])
        fill_rect(a.img, a.lay, (x + i, y + 3, t, h - 6), (30, 30, 30))
        i += t + rng.choice([1, 2, 2, 3])


def base(a, region, rgb, metallic=0.0, smooth=0.3, noise=0.0, blur=1.0):
    a.fill(region, rgb, metallic, smooth, noise=noise, blur=blur)
    return a.rect(region)


def palette(a):
    x0, y0, _, _ = a.rect("palette")
    for i, (name, (rgb, met, sm)) in enumerate(PALETTE.items()):
        r = (x0 + 32 * (i % 8), y0 + 32 * (i // 8), 32, 32)
        fill_rect(a.img, a.lay, r, rgb)
        fill_rect(a.mimg, a.mlay, r, (round(met * 255), 0, 0, max(sm, 1 / 255)))


def labels(a, rng):
    # gold-pump bottles: white, a gold panel down the front, wordmark at the top
    x, y, w, h = base(a, "pump_label", (240, 238, 232), 0.0, 0.55)
    fill_round_rect(a.img, a.lay, (x + 96, y + 44, x + 160, y + 116), 10, (214, 176, 96))
    fill_rect(a.img, a.lay, (x + 104, y + 52, 48, 10), (240, 226, 186))
    fill_ellipse(a.img, a.lay, (x + 114, y + 70, x + 142, y + 98), (246, 236, 214))
    put_logo(a, "lathertron", x + 128, y + 24, 104)
    fine_print(a, x + 100, y + 104, 56, 10, rng, (150, 120, 70))
    # dark blue bottle: navy, white panel with a teal band, wordmark
    x, y, w, h = base(a, "blue_label", (26, 40, 104), 0.0, 0.55)
    fill_rect(a.img, a.lay, (x + 10, y + 34, w - 20, 80), (244, 246, 248))
    fill_rect(a.img, a.lay, (x + 10, y + 34, w - 20, 16), (26, 150, 160))
    put_logo(a, "snowstopper", x + 64, y + 76, 100)
    fine_print(a, x + 14, y + 8, w - 28, 22, rng, (170, 190, 230))
    # sage bottles: pale sage, leaf sprig wordmark
    x, y, w, h = base(a, "sage_label", (210, 216, 200), 0.0, 0.45)
    put_logo(a, "sprig_twig", x + 64, y + 70, 70)
    fine_print(a, x + 20, y + 108, w - 40, 14, rng, (120, 130, 100))
    # clear purple body wash: pale clear top, violet liquid below, a violet label
    x, y, w, h = base(a, "purple_label", (214, 212, 222), 0.0, 0.8)
    fill_rect(a.img, a.lay, (x, y + 50, w, h - 50), (70, 34, 110))
    fill_round_rect(a.img, a.lay, (x + 34, y + 30, x + 94, y + 110), 8, (104, 60, 160))
    put_logo(a, "plumbubble", x + 64, y + 62, 58)
    # tub spray bottle: navy with a pink band and fine print
    x, y, w, h = base(a, "spray_label", (28, 30, 70), 0.0, 0.5)
    fill_rect(a.img, a.lay, (x, y + 96, w, 12), (230, 120, 170))
    fine_print(a, x + 40, y + 20, 48, 60, rng, (190, 190, 214))
    # lotion: white bottle with a violet-to-pink swoosh band
    x, y, w, h = base(a, "lotion", (240, 240, 236), 0.0, 0.5)
    fill_round_rect(a.img, a.lay, (x + 96, y + 46, x + 160, y + 96), 18, (150, 80, 170))
    fill_round_rect(a.img, a.lay, (x + 104, y + 60, x + 152, y + 84), 10, (230, 130, 190))
    fine_print(a, x + 100, y + 100, 56, 20, rng, (120, 100, 140))


def mesh(a, region, rgb, dark, light):
    x, y, w, h = base(a, region, rgb, 0.0, 0.25)
    for i in range(-h, w, 9):
        for j in range(0, h, 3):
            fill_rect(a.img, a.lay, (x + max(0, min(w - 2, i + j)), y + j, 2, 2), dark)
            fill_rect(a.img, a.lay, (x + max(0, min(w - 2, i + h - j)), y + j, 2, 2), light)
    grain(a.img, a.lay, (x, y, w, h), 0.08, 1.0)


def cloth(a, rng):
    # towel: pale yellow terry, a dobby border band near both ends of its length
    x, y, w, h = base(a, "towel", PALETTE["towel_yellow"][0], 0.0, 0.05, noise=0.12, blur=0.8)
    for yy in (y + 8, y + h - 24):
        fill_rect(a.img, a.lay, (x, yy, w, 16), (222, 200, 118))
        for k in range(0, 16, 4):
            fill_rect(a.img, a.lay, (x, yy + k, w, 1), (240, 224, 150))
        fill_rect(a.img, a.lay, (x, yy - 2, w, 2), (206, 184, 104))
        fill_rect(a.img, a.lay, (x, yy + 16, w, 2), (206, 184, 104))
    fill_rect(a.img, a.lay, (x, y, w, 3), (212, 190, 110))
    fill_rect(a.img, a.lay, (x, y + h - 3, w, 3), (212, 190, 110))
    grain(a.img, a.lay, (x, y, w, h), 0.06, 0.6)
    base(a, "rag", (236, 236, 232), 0.0, 0.05, noise=0.12, blur=0.8)
    mesh(a, "loofah_blue", (40, 150, 214), (22, 96, 160), (140, 206, 240))
    mesh(a, "loofah_orange", (246, 180, 120), (214, 130, 70), (252, 216, 170))
    mesh(a, "mesh_black", (26, 26, 28), (8, 8, 8), (110, 110, 114))
    # teal printed scarf: white clouds and small pink figures
    x, y, w, h = base(a, "scarf", (70, 176, 176), 0.0, 0.1)
    for _ in range(14):
        cx, cy = rng.randint(x + 16, x + w - 16), rng.randint(y + 6, y + h - 6)
        for dx in (-8, 0, 8):
            fill_ellipse(a.img, a.lay, (cx + dx - 7, cy - 5, cx + dx + 7, cy + 5), (236, 244, 240))
    for _ in range(6):
        cx, cy = rng.randint(x + 8, x + w - 8), rng.randint(y + 8, y + h - 8)
        fill_ellipse(a.img, a.lay, (cx - 4, cy - 6, cx + 4, cy + 6), (232, 150, 170))
    # purple studded collar
    x, y, w, h = base(a, "collar", (118, 58, 168), 0.0, 0.3)
    for i in range(8, w, 20):
        fill_ellipse(a.img, a.lay, (x + i - 5, y + h // 2 - 5, x + i + 5, y + h // 2 + 5), (200, 200, 206))
        fill_ellipse(a.img, a.lay, (x + i - 2, y + h // 2 - 2, x + i + 2, y + h // 2 + 2), (80, 40, 110))
    # blue nitrile gloves seen from above in the bin
    x, y, w, h = base(a, "gloves", (60, 100, 200), 0.0, 0.4)
    for _ in range(40):
        rx, ry = rng.randint(6, 22), rng.randint(3, 8)
        cx, cy = rng.randint(x + rx, x + w - rx), rng.randint(y + ry, y + h - ry)
        fill_ellipse(a.img, a.lay, (cx - rx, cy - ry, cx + rx, cy + ry),
                     rng.choice([(96, 140, 226), (40, 76, 170), (120, 160, 236)]))


def boxes(a, rng):
    # makeup-remover wipes box: light blue, navy stripe, wordmark on a white band
    x, y, w, h = base(a, "remover_box", (160, 196, 234), 0.0, 0.3)
    fill_rect(a.img, a.lay, (x, y + 70, w, 44), (244, 246, 250))
    fill_rect(a.img, a.lay, (x, y + 64, w, 6), (30, 44, 96))
    put_logo(a, "smudgebuster", x + 128, y + 92, 200)
    fine_print(a, x + 30, y + 14, w - 60, 40, rng, (90, 110, 150))
    # cotton-ball bag: white with a teal band and the wordmark
    x, y, w, h = base(a, "cotton_bag", (246, 246, 244), 0.0, 0.35)
    fill_rect(a.img, a.lay, (x + 70, y + 70, 116, 14), (40, 176, 190))
    put_logo(a, "fluffballs", x + 128, y + 44, 150)
    fine_print(a, x + 80, y + 92, 96, 24, rng, (80, 100, 110))
    # blue toilet-paper wrapper: royal blue, white waves, the wordmark
    x, y, w, h = base(a, "tp_wrap", (36, 86, 196), 0.0, 0.55)
    for j in range(0, h, 28):
        for i in range(0, w, 16):
            fill_ellipse(a.img, a.lay, (x + i, y + j + 18, x + i + 16, y + j + 24), (226, 236, 250))
    put_logo(a, "rolly_polly", x + 128, y + 56, 180)
    # insect trap box: white top, purple lower, wordmark
    x, y, w, h = base(a, "insect_box", (246, 246, 246), 0.0, 0.3)
    fill_rect(a.img, a.lay, (x, y + 120, w, 110), (150, 60, 170))
    fill_rect(a.img, a.lay, (x, y + 230, w, 26), (240, 240, 244))
    put_logo(a, "gnatnap", x + 64, y + 70, 110)
    fine_print(a, x + 16, y + 180, w - 32, 36, rng, (230, 200, 240))
    # ant bait box: orange with a blue band and the wordmark
    x, y, w, h = base(a, "ant_box", (240, 120, 36), 0.0, 0.3)
    fill_rect(a.img, a.lay, (x, y + 150, w, 60), (26, 70, 170))
    fill_rect(a.img, a.lay, (x, y + 20, w, 110), (246, 244, 240))
    put_logo(a, "picnic_panic", x + 64, y + 76, 100)
    fine_print(a, x + 16, y + 220, w - 32, 30, rng, (250, 220, 190))
    # shop towels: a stack of folded white towels in clear plastic, black label band
    x, y, w, h = base(a, "shop_towels", (238, 238, 234), 0.0, 0.6)
    for j in range(6, h, 9):
        fill_rect(a.img, a.lay, (x, y + j, w, 2), (196, 196, 194))
    fill_rect(a.img, a.lay, (x, y, w, 30), (24, 26, 32))
    fill_rect(a.img, a.lay, (x, y + 30, w, 4), (40, 100, 180))
    fill_ellipse(a.img, a.lay, (x + w - 60, y + 3, x + w - 36, y + 27), (60, 130, 200))
    fine_print(a, x + 16, y + 6, 120, 18, rng, (150, 150, 160))
    # grey mask box: orange warning bars, fine print, blank barcode
    x, y, w, h = base(a, "mask_box", (170, 170, 172), 0.0, 0.25)
    for yy in (y + 10, y + 56):
        fill_rect(a.img, a.lay, (x + 8, yy, w - 16, 6), (232, 130, 50))
        fine_print(a, x + 8, yy + 8, w - 16, 36, rng, (80, 80, 84))
    barcode(a, x + 80, y + 100, 40, 22, rng)
    # medicine boxes
    x, y, w, h = base(a, "med_white", WHITE, 0.0, 0.3)
    fill_rect(a.img, a.lay, (x, y + 20, w, 24), (40, 90, 190))
    fill_rect(a.img, a.lay, (x + 90, y + 60, 30, 30), (60, 170, 80))
    fine_print(a, x + 8, y + 52, 76, 60, rng)
    barcode(a, x + 8, y + 100, 44, 20, rng)
    x, y, w, h = base(a, "med_orange", (236, 130, 40), 0.0, 0.3)
    fill_round_rect(a.img, a.lay, (x + 44, y + 30, x + 84, y + 110), 10, WHITE)
    fill_rect(a.img, a.lay, (x + 54, y + 18, 20, 14), WHITE)
    fill_rect(a.img, a.lay, (x + 8, y + 112, w - 16, 10), (30, 60, 150))
    x, y, w, h = base(a, "med_red", (200, 40, 44), 0.0, 0.3)
    fill_rect(a.img, a.lay, (x, y + 50, w, 34), WHITE)
    fine_print(a, x + 8, y + 54, w - 16, 26, rng)
    # blister packs: silver foil, clear bubbles, red print
    x, y, w, h = base(a, "blister", (200, 200, 206), 0.7, 0.6, noise=0.08)
    for j in range(10, h - 10, 22):
        for i in range(10, w - 10, 22):
            fill_ellipse(a.img, a.lay, (x + i, y + j, x + i + 14, y + j + 14), (236, 236, 240))
    fill_rect(a.img, a.lay, (x + 6, y + 4, w - 12, 4), (200, 50, 60))
    # pill bottle labels
    x, y, w, h = base(a, "vitamin_label", (138, 28, 56), 0.0, 0.4)
    fill_rect(a.img, a.lay, (x, y, w, 20), (244, 244, 240))
    fill_rect(a.img, a.lay, (x + 40, y + 40, 48, 40), (240, 236, 232))
    fine_print(a, x + 44, y + 44, 40, 32, rng, (138, 28, 56))
    x, y, w, h = base(a, "amber_label", (150, 78, 22), 0.0, 0.7)
    fill_rect(a.img, a.lay, (x + 24, y + 30, 80, 70), (246, 246, 242))
    fine_print(a, x + 28, y + 34, 72, 40, rng, (150, 150, 150))
    fill_rect(a.img, a.lay, (x + 28, y + 80, 72, 14), (246, 246, 242))
    # kraft box with a black elastic band
    x, y, w, h = base(a, "kraft_band", PALETTE["kraft"][0], 0.0, 0.15, noise=0.05)
    fill_rect(a.img, a.lay, (x + 56, y, 8, h), (20, 20, 20))
    # eyeshadow palettes: black lids with a strip of colour pans
    x, y, w, h = base(a, "palettes", (26, 26, 28), 0.0, 0.5)
    cols = [(220, 180, 170), (190, 120, 110), (230, 210, 190), (120, 80, 70), (240, 170, 190), (90, 60, 60)]
    for i, c in enumerate(cols):
        fill_rect(a.img, a.lay, (x + 16 + i * 38, y + 40, 30, 48), c)
    # tote bag: white, soft fold shading, a black abstract arc print
    x, y, w, h = base(a, "tote", (244, 244, 242), 0.0, 0.1)
    for i in range(0, w, 40):
        fill_rect(a.img, a.lay, (x + i + 12, y, 6, h), (228, 228, 226))
    for i in range(5):      # a band of black wave blobs (abstract print, no letters)
        fill_ellipse(a.img, a.lay, (x + 40 + i * 36, y + 130 + (i % 2) * 14, x + 76 + i * 36, y + 170 + (i % 2) * 14),
                     (24, 24, 26))
    # grey speckled board
    x, y, w, h = base(a, "board", (150, 148, 144), 0.0, 0.2, noise=0.06)
    for _ in range(90):
        cx, cy = rng.randint(x, x + w - 6), rng.randint(y, y + h - 6)
        r = rng.randint(1, 4)
        fill_ellipse(a.img, a.lay, (cx, cy, cx + r * 2, cy + r * 1.5), (40, 40, 44))
    a.fill("clear", (232, 236, 240), 0.0, 0.85)


def earrings(a, rng):
    x, y, w, h = base(a, "earrings", (22, 22, 26), 0.0, 0.2)
    # three rows of hook holes (white acrylic bars are separate geometry)
    for row, yy in enumerate((y + 10, y + 52, y + 94)):
        for i in range(8, w - 8, 12):
            fill_ellipse(a.img, a.lay, (x + i, yy, x + i + 3, yy + 3), (200, 200, 200))
    # orange skeleton earrings (left), silver dangles, blue leaf pair, studs, chains
    for ox in (10, 24):
        fill_ellipse(a.img, a.lay, (x + ox, y + 14, x + ox + 12, y + 26), (250, 120, 40))
        fill_rect(a.img, a.lay, (x + ox + 4, y + 26, 4, 30), (250, 120, 40))
        fill_rect(a.img, a.lay, (x + ox, y + 32, 12, 3), (250, 120, 40))
        fill_rect(a.img, a.lay, (x + ox + 1, y + 56, 3, 18), (250, 120, 40))
        fill_rect(a.img, a.lay, (x + ox + 8, y + 56, 3, 18), (250, 120, 40))
    for ox in (46, 60, 74, 88):
        fill_rect(a.img, a.lay, (x + ox + 3, y + 12, 1, 8), (200, 200, 206))
        fill_ellipse(a.img, a.lay, (x + ox, y + 20, x + ox + 8, y + 50), (186, 186, 194))
    for ox in (108, 122):
        fill_ellipse(a.img, a.lay, (x + ox, y + 60, x + ox + 9, y + 82), (110, 140, 200))
    for ox in range(140, 240, 14):
        c = rng.choice([(200, 200, 206), (212, 170, 90), (120, 170, 190), (190, 120, 90)])
        L = rng.randint(10, 34)
        fill_rect(a.img, a.lay, (x + ox + 3, y + 54, 2, L), c)
        fill_ellipse(a.img, a.lay, (x + ox, y + 54 + L, x + ox + 8, y + 62 + L), c)
    for ox in range(20, 230, 16):
        fill_ellipse(a.img, a.lay, (x + ox, y + 100, x + ox + 5, y + 105),
                     rng.choice([(210, 210, 214), (212, 170, 90), (60, 90, 170)]))
    fill_rect(a.img, a.lay, (x + 150, y + 10, 70, 30), (220, 150, 70))    # a card behind


def build():
    rng = random.Random(11)
    a = Atlas(ATLAS)
    palette(a)
    labels(a, rng)
    cloth(a, rng)
    boxes(a, rng)
    earrings(a, rng)
    a.save()
