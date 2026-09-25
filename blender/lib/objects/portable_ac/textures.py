"""portable_ac atlas (512), painted from scratch in GIMP: charcoal plastic body, the
black louvre, a corrugated black duct (ribs run across v), a control strip with plain
unlabelled buttons and dots, the slider panel's off-white plastic, bright trim and
black rubber. No logo, no text.

    python blender/lib/textures/gimp_headless.py --object portable_ac
"""

ATLAS = {
    "name": "portable_ac",
    "size": 512,
    "regions": {
        "body": (0, 0, 256, 256),
        "grille": (256, 0, 256, 256),
        "hose": (0, 256, 256, 256),
        "controls": (256, 256, 128, 128),
        "panel": (384, 256, 128, 128),
        "chrome": (256, 384, 128, 128),
        "rubber": (384, 384, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("body", (38, 38, 41), 0.0, 0.45, noise=0.03, blur=1.5)
    # Louvre: horizontal slats with dark gaps, a centre divider.
    x, y, w, h = a.rect("grille")
    fill_rect(a.img, a.lay, (x, y, w, h), (12, 12, 13))
    for j in range(8, h - 4, 16):
        fill_rect(a.img, a.lay, (x, y + j, w, 9), (46, 46, 50))
        fill_rect(a.img, a.lay, (x, y + j, w, 2), (70, 70, 74))
    fill_rect(a.img, a.lay, (x + w // 2 - 4, y, 8, h), (40, 40, 44))
    a.material("grille", 0.0, 0.35)
    # Duct: dark ribs with a soft highlight crest, 4 ribs per region (v).
    x, y, w, h = a.rect("hose")
    fill_rect(a.img, a.lay, (x, y, w, h), (14, 14, 15))
    for j in range(0, h, 64):
        fill_rect(a.img, a.lay, (x, y + j + 14, w, 36), (34, 34, 37))
        fill_rect(a.img, a.lay, (x, y + j + 26, w, 10), (62, 62, 66))
    grain(a.img, a.lay, (x, y, w, h), 0.02, 2.0)
    a.material("hose", 0.0, 0.35)
    # Controls: black strip, small grey buttons and a couple of status dots.
    x, y, w, h = a.rect("controls")
    fill_rect(a.img, a.lay, (x, y, w, h), (24, 24, 26))
    for i in range(7):
        bx = x + 8 + i * 17
        fill_ellipse(a.img, a.lay, (bx, y + 70, bx + 9, y + 79), (92, 92, 96))
    for bx in (x + 30, x + 90):
        fill_ellipse(a.img, a.lay, (bx, y + 44, bx + 4, y + 48), (150, 150, 150))
    a.material("controls", 0.0, 0.6)
    a.fill("panel", (214, 212, 204), 0.0, 0.25, noise=0.02)
    a.fill("chrome", (196, 198, 202), 1.0, 0.8, noise=0.02)
    a.fill("rubber", (20, 20, 21), 0.0, 0.15, noise=0.02)
    a.save()
