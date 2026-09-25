"""Washer/dryer atlas: white enamel, dryer door with a generic caution sticker and pull
slot, control strip with knob surrounds, unreadable legend marks and the parody logo.

Runs inside headless GIMP with gimp_textures.py's helpers in scope:
    python blender/lib/textures/gimp_headless.py --object washer_dryer
Everything is drawn; no photo pixels (the photo is too dim and soft to use).
"""

import random as _random

ATLAS = {
    "name": "washer_dryer",
    "size": 1024,
    "regions": {
        "door": (0, 0, 512, 536),
        "panel": (0, 560, 1024, 180),
        "enamel": (512, 0, 256, 256),
        "knob": (768, 0, 128, 128),
        "knob_ring": (896, 0, 128, 128),
        "kick": (512, 256, 128, 128),
        "hinge": (640, 256, 128, 128),
    },
}
# same fractions as KNOBS in object.py
KNOBS_TEX = [(0.18, 3.3, "dial"), (0.39, 1.6, "small"), (0.47, 1.6, "small"),
             (0.70, 1.3, "button"), (0.87, 3.3, "dial")]
ENAMEL = (236, 236, 231)
PANEL_TINT = (232, 232, 226)
INK = (120, 122, 126)


def _marks(img, lay, x, y, rows, rng, width=40, h=3, gap=6, color=INK):
    """Rows of short blocks that read as fine print from a distance but spell nothing."""
    for r in range(rows):
        cx = x
        end = x + rng.randint(int(width * 0.6), width)
        while cx < end:
            w = rng.randint(3, 9)
            fill_rect(img, lay, (cx, y + r * gap, w, h), color)
            cx += w + rng.randint(2, 3)


def build():
    rng = _random.Random(7)
    a = Atlas(ATLAS)
    a.fill("enamel", ENAMEL, 0.0, 0.62, noise=0.012, blur=1.5)
    a.fill("knob", (226, 226, 222), 0.0, 0.45, noise=0.01)
    a.fill("knob_ring", (158, 159, 160), 0.0, 0.45, noise=0.01)
    a.fill("kick", (58, 58, 60), 0.0, 0.2, noise=0.02)
    a.fill("hinge", (205, 205, 202), 0.2, 0.5)

    # --- dryer door ------------------------------------------------------------
    x, y, w, h = a.rect("door")
    a.fill("door", (180, 181, 180), 0.0, 0.62)                     # edge band = the gap shade
    fill_round_rect(a.img, a.lay, (x + 6, y + 6, x + w - 6, y + h - 6), 14, ENAMEL)
    grain(a.img, a.lay, (x + 6, y + 6, w - 12, h - 12), 0.012, 1.5)
    # recessed pull slot on the right edge
    sx0, sx1 = x + int(0.90 * w), x + int(0.965 * w)
    sy0, sy1 = y + int(0.46 * h), y + int(0.76 * h)
    fill_round_rect(a.img, a.lay, (sx0, sy0, sx1, sy1), 6, (170, 171, 170))
    fill_round_rect(a.img, a.lay, (sx0 + 4, sy0 + 6, sx1 - 2, sy1 - 2), 5, (214, 214, 210))
    # generic caution sticker: amber label, pictogram box, blurred lines of nothing
    kx0, kx1 = x + int(0.30 * w), x + int(0.75 * w)
    ky0, ky1 = y + int(0.16 * h), y + int(0.27 * h)
    fill_rect(a.img, a.lay, (kx0, ky0, kx1 - kx0, ky1 - ky0), (196, 128, 40))
    fill_rect(a.img, a.lay, (kx0 + 2, ky0 + 2, kx1 - kx0 - 4, ky1 - ky0 - 4), (234, 176, 64))
    fill_rect(a.img, a.lay, (kx0 + 6, ky0 + 8, 36, ky1 - ky0 - 16), (30, 28, 24))
    fill_rect(a.img, a.lay, (kx0 + 10, ky0 + 12, 28, ky1 - ky0 - 24), (240, 236, 220))
    fill_rect(a.img, a.lay, (kx0 + 18, ky0 + 16, 12, ky1 - ky0 - 32), (30, 28, 24))
    fill_rect(a.img, a.lay, (kx0 + 60, ky0 + 7, 120, 5), (120, 70, 20))
    _marks(a.img, a.lay, kx0 + 50, ky0 + 20, 5, rng, width=kx1 - kx0 - 60, h=3, gap=7,
           color=(150, 96, 36))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, kx0 + 46, ky0 + 16, kx1 - kx0 - 50, ky1 - ky0 - 20)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=1.2, std_dev_y=1.2)
    Gimp.Selection.none(a.img)
    a.material("door", 0.0, 0.62)

    # --- control strip ---------------------------------------------------------
    x, y, w, h = a.rect("panel")
    a.fill("panel", PANEL_TINT, 0.0, 0.55, noise=0.012, blur=1.5)
    fill_rect(a.img, a.lay, (x, y, w, 4), (200, 200, 196))          # top seam under the dryer
    fill_rect(a.img, a.lay, (x, y + h - 4, w, 4), (190, 190, 186))  # lip underside shadow
    px_per_in = w / 23.9
    cy = y + h // 2
    for fx, dia, kind in KNOBS_TEX:
        cx = x + int(fx * w)
        r = int(dia * px_per_in / 2)
        if kind == "dial":
            # printed cycle ring around each timer: tick marks at even steps
            import math as _m
            for i in range(28):
                ang = 2 * _m.pi * i / 28
                rr = r + 12
                tx, ty = cx + rr * _m.cos(ang), cy + rr * _m.sin(ang)
                if y + 6 < ty < y + h - 8:
                    fill_rect(a.img, a.lay, (int(tx) - 2, int(ty) - 2, 4, 4), INK)
            _marks(a.img, a.lay, cx - r - 70, cy - 36, 3, rng, width=50)
            _marks(a.img, a.lay, cx + r + 18, cy - 30, 3, rng, width=50)
            _marks(a.img, a.lay, cx - r - 60, cy + 30, 2, rng, width=44)
            _marks(a.img, a.lay, cx + r + 18, cy + 34, 2, rng, width=44)
        elif kind == "small":
            _marks(a.img, a.lay, cx - 26, y + 18, 2, rng, width=52)
            fill_rect(a.img, a.lay, (cx - r - 6, cy - r - 8, 3, 3), INK)
            fill_rect(a.img, a.lay, (cx + r + 3, cy - r - 8, 3, 3), INK)
        else:
            _marks(a.img, a.lay, cx - 30, y + 20, 2, rng, width=60)
    # small status dot left of the washer timer, fine print at the right end
    fill_ellipse(a.img, a.lay, (x + 40, cy - 40, x + 48, cy - 32), (90, 92, 96))
    _marks(a.img, a.lay, x + w - 70, y + 16, 5, rng, width=56)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y + 6, w, h - 12)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=0.8, std_dev_y=0.8)
    Gimp.Selection.none(a.img)
    # parody wordmark, bottom centre between the small knobs and the push knob
    lg = load(os.path.join(LIB, "objects", "washer_dryer", "logos", "tumblewump.svg"))
    lw = 96
    lg.scale(lw, round(lg.get_height() * lw / lg.get_width()))
    add_layer_from(a.img, lg, "logo", x + int(0.455 * w) - lw // 2, y + h - 38)
    lg.delete()
    a.lay = flatten(a.img)
    a.material("panel", 0.0, 0.55)
    a.save()
