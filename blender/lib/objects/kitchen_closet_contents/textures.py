"""kitchen_closet_contents atlas (1024): what's stored in the kitchen-side closet (photo 15
of the 2026-10-23 cupboards set). Painted from scratch, no photo pixels, no text:
  - printed faces as plain colour blocks in each package's real colour scheme: the
    copy-paper case (blue band, white lower panel, blue arrow block), the grey cooler
    bag front (black lid band and strap, pocket, blank round sticker), the seat-massager
    box (white top band, grey seat silhouette; the printed person is a plain tan/blue
    block), the boot box (kraft, green tape, dark brown blob where the logo was), the
    moving carton (red bars where the arrows/warning print was), the open shipping box
    (blank white labels), the file box's blank label, the purifier's slotted grille
  - a 64 px swatch per flat colour.
Runs inside headless GIMP with the gimp_textures helpers in scope; the top level is
plain Python so object.py can read ATLAS from this file.
"""

import random

# (name, rgb, metallic, smoothness) -- one 64 px swatch each
SWATCHES = [
    ("shelf_paint", (224, 222, 216), 0.0, 0.35), ("rod_wood", (196, 152, 100), 0.0, 0.4),
    ("pack_black", (30, 30, 33), 0.0, 0.15), ("pack_grey", (62, 62, 66), 0.0, 0.2),
    ("zipper", (160, 160, 158), 0.7, 0.5), ("kraft", (182, 142, 100), 0.0, 0.1),
    ("kraft_dark", (150, 112, 78), 0.0, 0.1), ("label_white", (240, 240, 236), 0.0, 0.2),
    ("bag_white", (172, 180, 178), 0.0, 0.6), ("blue_case", (28, 84, 196), 0.0, 0.25),
    ("navy_case", (34, 48, 112), 0.0, 0.25), ("trim_black", (22, 22, 24), 0.0, 0.3),
    ("wheel", (34, 34, 36), 0.0, 0.35), ("catering", (100, 64, 54), 0.0, 0.1),
    ("purifier", (24, 24, 26), 0.0, 0.35), ("ream_blue", (30, 108, 200), 0.0, 0.15),
    ("ream_white", (238, 238, 236), 0.0, 0.15), ("cooler_grey", (118, 122, 128), 0.0, 0.3),
    ("cooler_black", (28, 28, 30), 0.0, 0.3), ("file_black", (22, 22, 24), 0.0, 0.5),
    ("clear", (222, 228, 232), 0.0, 0.85), ("lid_white", (236, 236, 234), 0.0, 0.45),
    ("lid_grey", (188, 192, 196), 0.0, 0.55), ("hanger", (234, 232, 224), 0.0, 0.45),
    ("mail_white", (238, 236, 232), 0.0, 0.15), ("mail_red", (190, 40, 46), 0.0, 0.2),
    ("bench_grey", (150, 150, 146), 0.0, 0.05), ("bench_leg", (30, 26, 24), 0.0, 0.3),
    ("massager_black", (32, 32, 34), 0.0, 0.2), ("red_box", (200, 40, 42), 0.0, 0.2),
    ("orange_box", (230, 112, 40), 0.0, 0.2), ("teal", (64, 188, 200), 0.0, 0.4),
    ("lock_black", (26, 26, 28), 0.0, 0.4), ("alu", (182, 184, 188), 0.8, 0.5),
    ("duffel_red", (196, 32, 36), 0.0, 0.2), ("duffel_black", (24, 24, 26), 0.0, 0.2),
    ("duffel_grey", (132, 134, 138), 0.0, 0.2), ("navy_bag", (30, 42, 92), 0.0, 0.25),
    ("tan_bag", (190, 160, 104), 0.0, 0.15), ("black_bag", (24, 24, 26), 0.0, 0.15),
    ("cord", (20, 20, 20), 0.0, 0.4), ("box_brown", (98, 68, 52), 0.0, 0.1),
    ("blanket", (176, 168, 150), 0.0, 0.05), ("green_tape", (96, 140, 70), 0.0, 0.2),
]

BIG = {
    "ream_end": (0, 0, 256, 192),
    "cooler_front": (256, 0, 256, 320),
    "massager_front": (512, 0, 256, 320),
    "rugged_front": (768, 0, 256, 192),
    "moving_front": (768, 192, 256, 160),
    "purifier_grille": (0, 192, 256, 256),
    "kraft_front": (256, 320, 256, 192),
    "ream_side": (512, 320, 256, 128),
    "file_label": (0, 448, 128, 96),
    "redbox_front": (128, 448, 128, 128),
    "rugged_top": (768, 352, 256, 160),
}


def _regions():
    r = dict(BIG)
    for i, (name, _, _, _) in enumerate(SWATCHES):
        r[name] = ((i % 16) * 64, 704 + (i // 16) * 64, 64, 64)
    return r


ATLAS = {"name": "kitchen_closet_contents", "size": 1024, "regions": _regions()}

BLUE = (30, 108, 200)
WHITE = (240, 240, 238)


def build():
    rng = random.Random(15)
    a = Atlas(ATLAS)
    for name, rgb, met, sm in SWATCHES:
        a.fill(name, rgb, met, sm, noise=0.012)

    # copy-paper case end: blue band on top (a small red block where the store mark was),
    # white lower panel with a blue arrow block and a blue square; no text or barcode
    x, y, w, h = a.rect("ream_end")
    fill_rect(a.img, a.lay, (x, y, w, h), WHITE)
    fill_rect(a.img, a.lay, (x, y, w, int(h * 0.48)), BLUE)
    fill_rect(a.img, a.lay, (x + 10, y + 34, 46, 18), (210, 36, 40))
    fill_rect(a.img, a.lay, (x + 70, y + 30, 90, 26), (226, 236, 248))     # pale title block
    fill_rect(a.img, a.lay, (x + 180, y + 26, 60, 34), (226, 236, 248))
    fill_rect(a.img, a.lay, (x, y + int(h * 0.52), 90, 60), BLUE)            # arrow block
    for i in range(0, 30, 2):
        fill_rect(a.img, a.lay, (x + 90 + i, y + int(h * 0.52) + i, 2, 60 - 2 * i), BLUE)
    fill_rect(a.img, a.lay, (x + 132, y + int(h * 0.50), 70, 90), BLUE)      # count square
    fill_rect(a.img, a.lay, (x + 154, y + int(h * 0.56), 26, 50), (250, 250, 250))
    fill_rect(a.img, a.lay, (x + 210, y + int(h * 0.60), 38, 30), (205, 205, 205))   # blank code box
    grain(a.img, a.lay, (x, y, w, h), 0.03, 1.0)
    a.material("ream_end", 0.0, 0.15)
    x, y, w, h = a.rect("ream_side")
    fill_rect(a.img, a.lay, (x, y, w, h), WHITE)
    fill_rect(a.img, a.lay, (x, y, w, int(h * 0.48)), BLUE)
    fill_rect(a.img, a.lay, (x + 20, y + 20, 70, 16), (210, 36, 40))
    fill_rect(a.img, a.lay, (x + 110, y + 18, 120, 22), (226, 236, 248))
    a.material("ream_side", 0.0, 0.15)

    # cooler bag front: grey with a black lid band, black strap band, a darker pocket with
    # a zip line, blue accents, a blank round sticker
    x, y, w, h = a.rect("cooler_front")
    fill_rect(a.img, a.lay, (x, y, w, h), (120, 124, 130))
    fill_rect(a.img, a.lay, (x, y + 96, w, 30), (30, 30, 32))
    fill_rect(a.img, a.lay, (x + 40, y + 70, 12, 26), (40, 100, 190))
    fill_rect(a.img, a.lay, (x + w - 52, y + 70, 12, 26), (40, 100, 190))
    fill_rect(a.img, a.lay, (x + 14, y + 142, w - 28, h - 160), (106, 110, 116))
    fill_rect(a.img, a.lay, (x + 20, y + 150, w - 40, 6), (205, 208, 212))
    fill_rect(a.img, a.lay, (x + 54, y + 156, 4, 30), (40, 100, 190))
    fill_rect(a.img, a.lay, (x + 70, y + 210, 120, 14), (170, 174, 180))   # pale wordmark bar, no letters
    fill_ellipse(a.img, a.lay, (x + 168, y + 252, x + 222, y + 306), (236, 236, 230))
    fill_ellipse(a.img, a.lay, (x + 182, y + 266, x + 208, y + 292), (150, 170, 120))
    fill_rect(a.img, a.lay, (x, y + h - 10, w, 10), (30, 30, 32))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.8)
    a.material("cooler_front", 0.0, 0.3)

    # seat-massager box: white top band, light grey field, a dark seat-cushion silhouette;
    # the printed person replaced by a plain tan/blue colour block
    x, y, w, h = a.rect("massager_front")
    fill_rect(a.img, a.lay, (x, y, w, h), (218, 218, 216))
    fill_rect(a.img, a.lay, (x, y, w, 70), (246, 246, 244))
    fill_rect(a.img, a.lay, (x + 30, y + 16, 190, 16), (70, 70, 74))      # title bar, no letters
    fill_rect(a.img, a.lay, (x + 50, y + 42, 150, 10), (130, 130, 134))
    fill_ellipse(a.img, a.lay, (x + 4, y + 66, x + 44, y + 106), (210, 50, 40))
    fill_round_rect(a.img, a.lay, (x + 130, y + 100, x + 236, y + 300), 30, (60, 62, 66))
    fill_round_rect(a.img, a.lay, (x + 146, y + 120, x + 220, y + 290), 22, (82, 84, 90))
    fill_rect(a.img, a.lay, (x + 12, y + 150, 110, 170), (176, 146, 120))   # plain block, no person
    fill_rect(a.img, a.lay, (x + 12, y + 250, 110, 70), (222, 224, 230))
    fill_rect(a.img, a.lay, (x + 150, y + 130, 50, 8), (150, 150, 154))
    grain(a.img, a.lay, (x, y, w, h), 0.03, 1.0)
    a.material("massager_front", 0.0, 0.25)

    # boot box: kraft, green tape at the edges, a dark brown blob for the logo, a dark
    # green square mark (no letters)
    for reg in ("rugged_front", "rugged_top"):
        x, y, w, h = a.rect(reg)
        fill_rect(a.img, a.lay, (x, y, w, h), (186, 152, 108))
        fill_rect(a.img, a.lay, (x, y, 22, h), (96, 140, 70))
        fill_rect(a.img, a.lay, (x + w - 22, y, 22, h), (96, 140, 70))
        grain(a.img, a.lay, (x, y, w, h), 0.05, 1.0)
        a.material(reg, 0.0, 0.1)
    x, y, w, h = a.rect("rugged_front")
    fill_rect(a.img, a.lay, (x, y + h - 60, w, 60), (176, 142, 98))       # lid lip
    fill_rect(a.img, a.lay, (x, y + h - 62, w, 3), (120, 92, 62))
    fill_rect(a.img, a.lay, (x + 60, y + 50, 50, 34), (60, 104, 60))
    fill_rect(a.img, a.lay, (x + 124, y + 58, 90, 18), (70, 54, 40))
    x, y, w, h = a.rect("rugged_top")
    fill_ellipse(a.img, a.lay, (x + 90, y + 40, x + 170, y + 100), (70, 54, 40))

    # moving carton: kraft with red bars where the handling print was
    x, y, w, h = a.rect("moving_front")
    fill_rect(a.img, a.lay, (x, y, w, h), (184, 144, 102))
    fill_rect(a.img, a.lay, (x + 20, y + 20, w - 40, 30), (190, 46, 40))
    fill_rect(a.img, a.lay, (x + 30, y + 26, w - 60, 18), (184, 144, 102))
    for cx in (x + 70, x + 150):
        fill_rect(a.img, a.lay, (cx, y + 70, 10, 30), (190, 46, 40))
        for i in range(10):
            fill_rect(a.img, a.lay, (cx - 10 + i, y + 60 + i, 30 - 2 * i, 2), (190, 46, 40))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 1.0)
    a.material("moving_front", 0.0, 0.1)

    # open shipping box front: kraft, a dark printed square, two blank white labels
    x, y, w, h = a.rect("kraft_front")
    fill_rect(a.img, a.lay, (x, y, w, h), (184, 144, 102))
    fill_rect(a.img, a.lay, (x + 120, y + 30, 70, 100), (58, 56, 58))
    fill_rect(a.img, a.lay, (x + 10, y + 70, 46, 36), (242, 242, 238))
    fill_rect(a.img, a.lay, (x + 130, y + 80, 44, 56), (242, 242, 238))
    for j in range(6):
        fill_rect(a.img, a.lay, (x + 136, y + 88 + j * 8, rng.randint(14, 30), 2), (170, 170, 170))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 1.0)
    a.material("kraft_front", 0.0, 0.1)

    # purifier: black with staggered vertical slots, sparser toward the top
    x, y, w, h = a.rect("purifier_grille")
    fill_rect(a.img, a.lay, (x, y, w, h), (24, 24, 26))
    for col in range(0, w, 10):
        for row in range(0, h, 22):
            if rng.random() < 0.25 + 0.75 * row / h:
                fill_rect(a.img, a.lay, (x + col + 3, y + row + (col // 10 % 2) * 11, 3, 14), (66, 66, 70))
    a.material("purifier_grille", 0.0, 0.35)

    # file box label: pale blue frame, white panel, grey pictured box, no text
    x, y, w, h = a.rect("file_label")
    fill_rect(a.img, a.lay, (x, y, w, h), (240, 242, 246))
    fill_rect(a.img, a.lay, (x, y, w, 14), (40, 80, 170))
    fill_rect(a.img, a.lay, (x + 8, y + 22, 26, 10), (200, 40, 50))
    fill_rect(a.img, a.lay, (x + 30, y + 40, 70, 40), (140, 160, 190))
    fill_rect(a.img, a.lay, (x + 40, y + 50, 50, 22), (60, 70, 90))
    a.material("file_label", 0.0, 0.4)

    # tissue-style box: red upper half, white lower with a blue diagonal block
    x, y, w, h = a.rect("redbox_front")
    fill_rect(a.img, a.lay, (x, y, w, h), (246, 246, 244))
    fill_rect(a.img, a.lay, (x, y, w, int(h * 0.42)), (200, 40, 42))
    for i in range(30):
        fill_rect(a.img, a.lay, (x + 10 + i, y + 60 + i, 50, 2), (40, 110, 200))
    a.material("redbox_front", 0.0, 0.2)
    a.save()
