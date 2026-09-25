"""plastic_drawers atlas (512): white plastic, a faint clear tint, folded clothes seen
through the drawers, a dark grey-brown board, black nylon, nickel zip pulls, a
blue-grey basket and a plain yellow/orange tissue box (no text)."""

import random

ATLAS = {
    "name": "plastic_drawers",
    "size": 512,
    "regions": {
        "white": (0, 0, 128, 128),
        "clear": (128, 0, 128, 128),
        "clothes": (256, 0, 256, 128),
        "board": (0, 128, 128, 128),
        "bag": (128, 128, 128, 128),
        "zip": (256, 128, 64, 64),
        "caster": (320, 128, 64, 64),
        "tissue": (384, 128, 128, 128),
        "basket": (0, 256, 128, 128),
        "box_lid": (128, 256, 128, 128),
    },
}


def build():
    random.seed(3)
    a = Atlas(ATLAS)
    a.fill("white", (232, 232, 228), 0.0, 0.5, noise=0.01)
    a.fill("clear", (225, 230, 232), 0.0, 0.85)
    x, y, w, h = a.rect("clothes")
    fill_rect(a.img, a.lay, (x, y, w, h), (60, 56, 58))
    for _ in range(50):
        c = random.choice([(30, 30, 34), (90, 70, 72), (120, 60, 70), (70, 80, 100), (150, 140, 130),
                           (200, 196, 190)])
        fill_rect(a.img, a.lay, (x + random.randint(0, w - 30), y + random.randint(0, h - 16),
                                 random.randint(20, 70), random.randint(8, 30)), c)
    grain(a.img, a.lay, (x, y, w, h), 0.05, 2.0)
    a.material("clothes", 0.0, 0.1)
    a.fill("board", (72, 66, 62), 0.0, 0.35, noise=0.02)
    a.fill("bag", (26, 26, 28), 0.0, 0.3, noise=0.05, blur=1.5)
    a.fill("zip", (190, 190, 186), 1.0, 0.6)
    a.fill("caster", (30, 30, 30), 0.0, 0.3)
    x, y, w, h = a.rect("tissue")
    fill_rect(a.img, a.lay, (x, y, w, h), (236, 196, 90))
    fill_rect(a.img, a.lay, (x, y + h // 2, w, h // 2), (232, 130, 60))
    a.material("tissue", 0.0, 0.3)
    a.fill("basket", (96, 122, 150), 0.0, 0.45, noise=0.02)
    a.fill("box_lid", (240, 240, 236), 0.0, 0.55)
    a.save()
