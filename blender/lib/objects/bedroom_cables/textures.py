"""bedroom_cables atlas (256): matte black cable jacket and plastic, white ethernet
jacket, off-white wall plates (duplex outlet face and a cable plate with screws),
brass-ish metal, the power strip's top (a row of six receptacles) and side, and a blue
LED / red switch. Emission: the blue LED and a faint glow on the switch.
Runs inside headless GIMP with the gimp_textures helpers in scope."""

ATLAS = {
    "name": "bedroom_cables",
    "size": 256,
    "regions": {
        "cable_black": (0, 0, 64, 64),
        "cable_white": (64, 0, 64, 64),
        "plastic_black": (128, 0, 64, 64),
        "plate_white": (192, 0, 64, 64),
        "outlet_face": (0, 64, 64, 96),
        "coax_face": (64, 64, 64, 96),
        "metal": (128, 64, 64, 64),
        "led_blue": (192, 64, 32, 32),
        "switch_red": (224, 64, 32, 32),
        "strip_top": (0, 160, 256, 48),
        "strip_side": (0, 208, 256, 48),
        "rubber": (192, 96, 64, 64),
    },
}

PLATE = (236, 233, 224)
SLOT = (40, 38, 36)
STRIP_LEN = 10.49            # inches, object.py S_LEN
SLOTS = [1.3, 2.7, 4.1, 5.5, 6.9, 8.3]


def build():
    a = Atlas(ATLAS)
    a.fill("cable_black", (24, 24, 25), 0.0, 0.35, noise=0.02)
    a.fill("cable_white", (226, 226, 222), 0.0, 0.3, noise=0.01)
    a.fill("plastic_black", (22, 22, 23), 0.0, 0.3, noise=0.015)
    a.fill("plate_white", PLATE, 0.0, 0.4, noise=0.008)
    a.fill("metal", (176, 150, 96), 0.9, 0.55, noise=0.02)
    a.fill("rubber", (30, 30, 30), 0.0, 0.2)
    a.fill("led_blue", (70, 110, 255), 0.0, 0.8)
    a.fill("switch_red", (190, 30, 28), 0.0, 0.6)

    # duplex outlet face (plate seen from the room): two receptacles, centre screw
    x, y, w, h = a.rect("outlet_face")
    a.fill("outlet_face", PLATE, 0.0, 0.4, noise=0.008)
    for cy in (y + 26, y + 70):                               # upper / lower receptacle
        fill_round_rect(a.img, a.lay, (x + 14, cy - 13, x + 50, cy + 13), 7, (244, 242, 236))
        fill_rect(a.img, a.lay, (x + 23, cy - 8, 3, 11), SLOT)
        fill_rect(a.img, a.lay, (x + 38, cy - 9, 3, 13), SLOT)
        fill_ellipse(a.img, a.lay, (x + 29, cy + 4, x + 35, cy + 10), SLOT)
    fill_ellipse(a.img, a.lay, (x + 29, y + 45, x + 35, y + 51), (170, 168, 160))

    # cable plate: plain, a screw above and below the connector
    x, y, w, h = a.rect("coax_face")
    a.fill("coax_face", PLATE, 0.0, 0.4, noise=0.008)
    for cy in (y + 14, y + 82):
        fill_ellipse(a.img, a.lay, (x + 29, cy - 3, x + 35, cy + 3), (170, 168, 160))

    # strip side and top: satin black, the top with its receptacle row along u
    a.fill("strip_side", (28, 28, 30), 0.0, 0.35, noise=0.015)
    x, y, w, h = a.rect("strip_top")
    a.fill("strip_top", (30, 30, 32), 0.0, 0.35, noise=0.015)
    for s in SLOTS:
        cx = x + round(2 + (w - 4) * s / STRIP_LEN)
        cy = y + h // 2
        fill_round_rect(a.img, a.lay, (cx - 9, cy - 11, cx + 9, cy + 11), 4, (40, 40, 42))
        fill_rect(a.img, a.lay, (cx - 6, cy - 7, 4, 2), (8, 8, 8))
        fill_rect(a.img, a.lay, (cx + 2, cy - 7, 4, 2), (8, 8, 8))
        fill_ellipse(a.img, a.lay, (cx - 2, cy + 2, cx + 2, cy + 6), (8, 8, 8))

    eimg, elay = a.glow_layer()
    fill_rect(eimg, elay, (0, 0, 256, 256), (0, 0, 0))
    fill_rect(eimg, elay, a.rect("led_blue"), (60, 100, 255))
    fill_rect(eimg, elay, a.rect("switch_red"), (70, 8, 6))
    a.save()
