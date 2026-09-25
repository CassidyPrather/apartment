"""floor_boxes atlas (1024): an orange noodle case with a blue stripe, a white cup
panel and the parody "Noodle Goblin" logo on the long sides; a white top panel with
unreadable fine-print blocks and a blank barcode box; kraft tray with a red band; red
and white bar wrappers with the parody "Crunchums" mark. No real text anywhere."""

import os
import random

ATLAS = {
    "name": "floor_boxes",
    "size": 1024,
    "regions": {
        "case_side": (0, 0, 1024, 384),
        "case_top": (0, 384, 512, 384),
        "case_end": (512, 384, 512, 256),
        "kraft": (512, 640, 256, 128),
        "tray_print": (768, 640, 256, 128),
        "wrapper": (0, 768, 512, 256),
        "bar_end": (512, 768, 256, 256),
    },
}
LOGOS = os.path.join(ROOT, "blender", "lib", "objects", "floor_boxes", "logos")
ORANGE = (236, 104, 46)
BLUE = (70, 160, 214)


def put_logo(a, name, x, y, w):
    lg = load(os.path.join(LOGOS, name + ".svg"))
    lg.scale(w, round(lg.get_height() * w / lg.get_width()))
    add_layer_from(a.img, lg, name, x, y)
    lg.delete()
    a.lay = flatten(a.img)


def fine_print(a, x, y, w, h, rng):
    fill_rect(a.img, a.lay, (x, y, w, h), (250, 250, 248))
    for j in range(6, h - 6, 9):
        k = x + 6
        while k < x + w - 20:
            L = rng.randint(8, 40)
            fill_rect(a.img, a.lay, (k, y + j, min(L, x + w - 6 - k), 3), (120, 118, 116))
            k += L + rng.randint(4, 10)


def build():
    rng = random.Random(7)
    a = Atlas(ATLAS)
    # long side: orange, blue band along the bottom, white cup panel, logo
    x, y, w, h = a.rect("case_side")
    fill_rect(a.img, a.lay, (x, y, w, h), ORANGE)
    fill_rect(a.img, a.lay, (x, y + h - 110, w, 60), BLUE)
    fill_rect(a.img, a.lay, (x, y + h - 104, w, 4), (255, 255, 255))
    fill_round_rect(a.img, a.lay, (x + 40, y + 40, x + 250, y + h - 30), 24, (250, 248, 244))
    fill_rect(a.img, a.lay, (x + 80, y + 80, 130, 150), (232, 60, 40))       # plain red cup
    fill_rect(a.img, a.lay, (x + 90, y + 120, 110, 50), (255, 255, 255))
    fill_ellipse(a.img, a.lay, (x + w - 190, y + h - 150, x + w - 90, y + h - 50), (250, 250, 248))
    fill_ellipse(a.img, a.lay, (x + w - 176, y + h - 136, x + w - 104, y + h - 64), (232, 60, 40))
    put_logo(a, "noodle_goblin", x + 300, y + 60, 520)
    a.material("case_side", 0.0, 0.25)
    # top: white panel with fine print and a blank barcode box
    x, y, w, h = a.rect("case_top")
    fill_rect(a.img, a.lay, (x, y, w, h), ORANGE)
    fine_print(a, x + 20, y + 20, 200, h - 40, rng)
    fill_rect(a.img, a.lay, (x + 240, y + 20, w - 260, h - 40), (250, 250, 248))
    fill_rect(a.img, a.lay, (x + 300, y + 240, 170, 90), (30, 30, 30))
    fill_rect(a.img, a.lay, (x + 306, y + 246, 158, 78), (250, 250, 248))
    for i in range(0, 150, 5):
        fill_rect(a.img, a.lay, (x + 312 + i, y + 252, rng.choice([1, 2, 3]), 56), (30, 30, 30))
    fill_rect(a.img, a.lay, (x + 380, y + 50, 90, 90), (232, 60, 40))       # plain count badge
    fill_ellipse(a.img, a.lay, (x + 395, y + 65, x + 455, y + 125), (250, 250, 248))
    a.material("case_top", 0.0, 0.25)
    # ends: orange with the blue band
    x, y, w, h = a.rect("case_end")
    fill_rect(a.img, a.lay, (x, y, w, h), ORANGE)
    fill_rect(a.img, a.lay, (x, y + h - 80, w, 45), BLUE)
    fine_print(a, x + 30, y + 30, 200, 90, rng)
    a.material("case_end", 0.0, 0.25)
    # tray
    a.fill("kraft", (176, 136, 96), 0.0, 0.1, noise=0.05)
    x, y, w, h = a.rect("tray_print")
    fill_rect(a.img, a.lay, (x, y, w, h), (176, 136, 96))
    fill_rect(a.img, a.lay, (x, y + 30, w, 70), (178, 40, 40))
    fill_rect(a.img, a.lay, (x + 80, y + 48, 100, 30), (176, 136, 96))
    a.material("tray_print", 0.0, 0.1)
    # wrappers: red with white and gold stripes, the parody mark
    x, y, w, h = a.rect("wrapper")
    fill_rect(a.img, a.lay, (x, y, w, h), (196, 38, 48))
    for i in range(0, w, 56):
        fill_rect(a.img, a.lay, (x + i + 8, y, 10, h), (240, 236, 230))
        fill_rect(a.img, a.lay, (x + i + 30, y, 6, h), (214, 170, 70))
    put_logo(a, "crunchums", x + 120, y + 90, 260)
    a.material("wrapper", 0.3, 0.75)
    a.fill("bar_end", (214, 200, 190), 0.2, 0.7, noise=0.05)
    a.save()
