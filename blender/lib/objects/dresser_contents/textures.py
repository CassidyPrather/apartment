"""dresser_contents atlas (512): painted fabric and plastic, colours picked from the
open-drawer photos (Reference/cupboards_drawers 21-25, white balance corrected by eye).

No photo pixels: every print is drawn here (plaid stripes, denim twill, a black/cream lace print,
lace motif, openwork knit, sock stripes, keyboard keys, cables in clear bags). The mailer
bags are plain white: no labels, text or barcodes (privacy). No brands anywhere.
"""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dresser_contents", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)


ATLAS = _atlas()

FLAT = {  # region: (rgb, smoothness, noise)
    "tee_white": ((200, 202, 198), 0.15, 0.05),
    "tee_purple": ((84, 70, 100), 0.15, 0.05),
    "tee_grey": ((150, 152, 156), 0.15, 0.05),
    "black": ((22, 22, 24), 0.2, 0.03),
    "mailer": ((236, 236, 232), 0.35, 0.02),
    "pink_cable": ((226, 120, 160), 0.45, 0.0),
    "blue_cloth": ((70, 170, 215), 0.15, 0.05),
    "white_box": ((232, 232, 228), 0.3, 0.01),
    "pale_blue": ((184, 210, 222), 0.15, 0.05),
    "hot_pink": ((214, 64, 112), 0.15, 0.05),
    "blush": ((226, 186, 186), 0.15, 0.05),
    "beige": ((200, 170, 138), 0.15, 0.05),
    "rust": ((156, 72, 38), 0.15, 0.05),
    "sock_white": ((228, 228, 224), 0.12, 0.05),
    "lavender": ((176, 170, 210), 0.15, 0.05),
    "teal": ((0, 108, 128), 0.2, 0.05),
    "navy": ((36, 74, 130), 0.2, 0.05),
    "kbd_body": ((18, 18, 20), 0.35, 0.01),
    "black_soft": ((32, 30, 34), 0.15, 0.04),
    "brown": ((110, 74, 50), 0.15, 0.05),
}


CLIP = [None]


def ell(img, lay, box, rgb):
    """fill_ellipse clipped to the current print's rect (CLIP[0]) so prints don't bleed."""
    x, y, w, h = CLIP[0]
    x0, y0, x1, y1 = box
    x0, y0, x1, y1 = max(x0, x), max(y0, y), min(x1, x + w), min(y1, y + h)
    if x1 - x0 >= 2 and y1 - y0 >= 2:
        fill_ellipse(img, lay, (x0, y0, x1, y1), rgb)


def creases(a, region, rgb, rnd, n=7):
    """Painted fold shading: thin dark creases with a light ridge beside each."""
    CLIP[0] = a.rect(region)
    x, y, w, h = CLIP[0]
    dark = tuple(max(0, round(c * 0.55)) for c in rgb) + (0.6,)
    light = tuple(min(255, round(c * 1.15 + 18)) for c in rgb) + (0.45,)
    for _ in range(n):
        cx, cy = rnd.randint(x, x + w), rnd.randint(y, y + h)
        hw, hh = rnd.randint(w // 5, w // 2), rnd.randint(1, 3)
        if rnd.random() < 0.5:
            ell(a.img, a.lay, (cx - hw, cy - hh, cx + hw, cy + hh), dark)
            ell(a.img, a.lay, (cx - hw + 4, cy + hh, cx + hw - 4, cy + hh + 3), light)
        else:
            ell(a.img, a.lay, (cx - hh, cy - hw, cx + hh, cy + hw), dark)
            ell(a.img, a.lay, (cx + hh, cy - hw + 4, cx + hh + 3, cy + hw - 4), light)


def stripes(a, region, base, bands, vertical=False):
    """bands: list of (offset px, width px, rgba) repeated every `period` set by the list."""
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    for off, width, rgba in bands:
        width = min(width, (w if vertical else h) - off)
        if width <= 0:
            continue
        if vertical:
            fill_rect(a.img, a.lay, (x + off, y, width, h), rgba)
        else:
            fill_rect(a.img, a.lay, (x, y + off, w, width), rgba)


def build():
    a = Atlas(ATLAS)
    rnd = random.Random(7)
    for reg, (rgb, sm, nz) in FLAT.items():
        a.fill(reg, rgb, 0.0, sm, noise=nz)
        if reg not in ("mailer", "white_box", "pink_cable", "kbd_body"):
            creases(a, reg, rgb, rnd)

    # denim: light washed blue, fine twill noise, paler frayed patches
    x, y, w, h = a.rect("denim")
    CLIP[0] = (x, y, w, h)
    a.fill("denim", (124, 160, 198), 0.0, 0.12, noise=0.08, blur=0.6)
    for _ in range(10):
        cx, cy, r = rnd.randint(x, x + w), rnd.randint(y, y + h), rnd.randint(8, 22)
        ell(a.img, a.lay, (cx - r, cy - r // 2, cx + r, cy + r // 2), (200, 220, 236, 0.35))
    for i in range(0, w, 3):   # diagonal-ish twill lines
        fill_rect(a.img, a.lay, (x + i, y, 1, h), (110, 146, 180, 0.25))

    creases(a, "denim", (124, 160, 198), rnd, 9)

    # plaid flannel: navy / mid blue / white checks
    x, y, w, h = a.rect("plaid")
    CLIP[0] = (x, y, w, h)
    fill_rect(a.img, a.lay, (x, y, w, h), (52, 92, 132))
    for k in range(0, 128, 32):
        for vert in (False, True):
            r1 = (x + k, y, 12, h) if vert else (x, y + k, w, 12)
            r2 = (x + k + 18, y, 3, h) if vert else (x, y + k + 18, w, 3)
            r3 = (x + k + 24, y, 4, h) if vert else (x, y + k + 24, w, 4)
            fill_rect(a.img, a.lay, r1, (22, 34, 66, 0.55))
            fill_rect(a.img, a.lay, r2, (226, 228, 222, 0.6))
            fill_rect(a.img, a.lay, r3, (120, 170, 200, 0.45))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.6)
    creases(a, "plaid", (52, 92, 132), rnd, 8)
    a.material("plaid", 0.0, 0.12)

    # clear zip bags packed with black cables: dark coils, grey plastic sheen
    x, y, w, h = a.rect("cable_bag")
    CLIP[0] = (x, y, w, h)
    fill_rect(a.img, a.lay, (x, y, w, h), (34, 35, 38))
    for _ in range(30):
        cx, cy = rnd.randint(x + 6, x + w - 6), rnd.randint(y + 6, y + h - 6)
        rx, ry = rnd.randint(8, 24), rnd.randint(6, 18)
        ell(a.img, a.lay, (cx - rx, cy - ry, cx + rx, cy + ry), (58, 60, 64))
        ell(a.img, a.lay, (cx - rx + 2, cy - ry + 2, cx + rx - 2, cy + ry - 2), (30, 31, 34))
    for _ in range(9):   # plastic highlights and wrinkles
        cx, cy = rnd.randint(x, x + w), rnd.randint(y, y + h)
        ell(a.img, a.lay, (cx - 20, cy - 3, cx + 20, cy + 3), (200, 206, 212, 0.35))
    fill_rect(a.img, a.lay, (x, y + 4, w, 5), (200, 204, 210, 0.7))   # zip seal
    a.material("cable_bag", 0.0, 0.7)

    # clear zip bag with a purple zip strip, blue cloth showing through
    x, y, w, h = a.rect("zip_bag")
    CLIP[0] = (x, y, w, h)
    fill_rect(a.img, a.lay, (x, y, w, h), (190, 206, 220))
    fill_rect(a.img, a.lay, (x, y + 70, w, 58), (90, 170, 210, 0.7))
    fill_rect(a.img, a.lay, (x, y + 14, w, 12), (150, 60, 140))
    fill_rect(a.img, a.lay, (x, y + 26, w, 4), (200, 120, 190))
    for _ in range(5):
        cx, cy = rnd.randint(x, x + w), rnd.randint(y + 30, y + h)
        ell(a.img, a.lay, (cx - 20, cy - 4, cx + 20, cy + 4), (240, 244, 246, 0.55))
    a.material("zip_bag", 0.0, 0.75)

    # keyboard top: black deck, black keys with grey edges (main block, arrows, numpad)
    x, y, w, h = a.rect("keys")
    CLIP[0] = (x, y, w, h)
    fill_rect(a.img, a.lay, (x, y, w, h), (12, 12, 14))
    k = 10   # key pitch (px); the 17.5 in keyboard spans 256 px, ~22 key columns

    def key(kx, ky, kw=1.0):
        fill_round_rect(a.img, a.lay, (kx, ky, kx + round(kw * k) - 2, ky + k + 2), 2, (62, 62, 66))
        fill_round_rect(a.img, a.lay, (kx + 1, ky + 1, kx + round(kw * k) - 3, ky + k + 1), 2,
                        (26, 26, 29))
    rows = [[1.0] * 13 + [2.0], [1.5] + [1.0] * 12 + [1.5], [1.8] + [1.0] * 11 + [2.2],
            [2.3] + [1.0] * 10 + [2.7], [1.3] * 3 + [6.2] + [1.3] * 4]
    for r, widths in enumerate(rows):
        kx, ky = x + 6, y + 30 + r * (k + 6)
        for kw in widths:
            key(kx, ky, kw)
            kx += round(kw * k)
    for c in range(12):                       # function row
        key(x + 6 + c * 12, y + 10)
    for r in range(2):                        # nav block
        for c in range(3):
            key(x + 166 + c * 10, y + 30 + r * 16)
    for c in range(3):                        # arrows
        key(x + 166 + c * 10, y + 94)
    key(x + 176, y + 78)
    for r in range(5):                        # numpad
        for c in range(4):
            key(x + 206 + c * 11, y + 30 + r * 16)
    a.material("keys", 0.0, 0.35)

    # striped socks: pink / white / light blue bands
    stripes(a, "sock_stripe", (232, 232, 230), [
        (k + o, 10, c) for k in range(0, 128, 40)
        for o, c in ((0, (226, 70, 130)), (13, (226, 70, 130)), (27, (120, 180, 226)))])
    grain(a.img, a.lay, a.rect("sock_stripe"), 0.04, 0.6)
    a.material("sock_stripe", 0.0, 0.12)

    # black lace with a cream pattern: cream ground packed with black blotches so the
    # cream reads as a squiggly network
    x, y, w, h = a.rect("leopard")
    CLIP[0] = (x, y, w, h)
    fill_rect(a.img, a.lay, (x, y, w, h), (206, 200, 188))
    for gy in range(0, h + 8, 9):
        for gx in range(0, w + 8, 9):
            cx = x + gx + rnd.randint(-3, 3)
            cy = y + gy + rnd.randint(-3, 3)
            rx, ry = rnd.randint(3, 6), rnd.randint(2, 5)
            ell(a.img, a.lay, (cx - rx, cy - ry, cx + rx, cy + ry), (18, 17, 18))
    for _ in range(10):   # solid black patches
        cx, cy = rnd.randint(x, x + w), rnd.randint(y, y + h)
        ell(a.img, a.lay, (cx - 10, cy - 7, cx + 10, cy + 7), (18, 17, 18))
    a.material("leopard", 0.0, 0.2)

    # black lace: black ground, a loose grey floral net
    x, y, w, h = a.rect("lace")
    CLIP[0] = (x, y, w, h)
    fill_rect(a.img, a.lay, (x, y, w, h), (16, 16, 18))
    for gx in range(0, w, 8):
        for gy in range(0, h, 8):
            ell(a.img, a.lay, (x + gx + 2, y + gy + 2, x + gx + 5, y + gy + 5), (60, 58, 62))
    for _ in range(14):
        cx, cy = rnd.randint(x + 8, x + w - 8), rnd.randint(y + 8, y + h - 8)
        for k in range(5):
            ang = k / 5 * 6.283
            px, py = cx + round(7 * math.cos(ang)), cy + round(7 * math.sin(ang))
            ell(a.img, a.lay, (px - 4, py - 3, px + 4, py + 3), (70, 66, 70))
        ell(a.img, a.lay, (cx - 3, cy - 3, cx + 3, cy + 3), (10, 10, 12))
    a.material("lace", 0.0, 0.3)

    # openwork knit net: diagonal cream and tan bands with a grid of dark holes
    x, y, w, h = a.rect("crochet")
    CLIP[0] = (x, y, w, h)
    for k in range(0, h, 32):
        fill_rect(a.img, a.lay, (x, y + k, w, 16), (226, 220, 206))
        fill_rect(a.img, a.lay, (x, y + k + 16, w, 16), (176, 150, 118))
    for gx in range(0, w, 7):
        for gy in range(0, h, 7):
            ell(a.img, a.lay, (x + gx + 1, y + gy + 1, x + gx + 6, y + gy + 6), (60, 50, 42))
    grain(a.img, a.lay, (x, y, w, h), 0.04, 0.5)
    a.material("crochet", 0.0, 0.12)
    a.save()
