"""Window units atlas (512): white vinyl, a slightly grey sill track, the latch, the
raised blind's slat stack and rails, and a flat blue-grey for the glass (drawn
translucent through its own material). Runs inside headless GIMP with the
gimp_textures helpers in scope."""

ATLAS = {
    "name": "window_units",
    "size": 512,
    "regions": {
        "vinyl": (0, 0, 256, 256),
        "vinyl_track": (256, 0, 256, 256),
        "latch": (0, 256, 128, 128),
        "blind_slats": (128, 256, 128, 256),
        "blind_rail": (256, 256, 128, 128),
        "glass": (384, 256, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("vinyl", (238, 238, 233), 0.0, 0.40, noise=0.02, blur=2.0)
    a.fill("vinyl_track", (206, 206, 200), 0.0, 0.30, noise=0.03, blur=1.5)
    a.fill("latch", (226, 226, 222), 0.0, 0.50)
    a.fill("blind_rail", (240, 240, 236), 0.0, 0.35)
    a.fill("glass", (196, 212, 220), 0.0, 0.95)
    # Slat stack: ~1 in slats with a shaded lip and a thin gap line; the stack region
    # maps onto 5.5 in of height, so about 5-6 slats.
    x, y, w, h = a.rect("blind_slats")
    fill_rect(a.img, a.lay, (x, y, w, h), (236, 236, 231))
    n = 6
    for i in range(n):
        y0 = y + round(i * h / n)
        fill_rect(a.img, a.lay, (x, y0, w, 6), (178, 178, 172))
        fill_rect(a.img, a.lay, (x, y0 + 6, w, 10), (214, 214, 208))
    # ladder tapes
    for fx in (0.2, 0.8):
        fill_rect(a.img, a.lay, (x + round(fx * w) - 2, y, 4, h), (225, 225, 220))
    a.material("blind_slats", 0.0, 0.3)
    a.save()
