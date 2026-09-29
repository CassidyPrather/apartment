"""kitchen_clutter atlas (1024): flat swatches for the plastics, metals and foods, plus the
printed and patterned regions - the blue terry towel, a pizza-box top drawn from scratch,
the paper-towel pack with the parody "Soakington" mark, the napkin packs with the parody
"Napsody" mark, the drip coffee maker's parody "Mister Sippy" badge, and blank labels
(tin can, dish soap, spray bottle, coffee filters, paper plates, pink box). No real text,
brand or logo anywhere: every mark is drawn here or in logos/*.svg."""

import ast
import os
import random

PKG = os.path.join(ROOT, "blender", "lib", "objects", "kitchen_clutter")


def _atlas():
    src = open(os.path.join(PKG, "object.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            d = {"NAME": "kitchen_clutter"}
            return eval(compile(ast.Expression(node.value), "object.py", "eval"), d)
    raise RuntimeError("ATLAS not found")


ATLAS = _atlas()
KLOGOS = os.path.join(PKG, "logos")


def put_logo(a, name, x, y, w):
    lg = load(os.path.join(KLOGOS, name + ".svg"))
    lg.scale(w, round(lg.get_height() * w / lg.get_width()))
    add_layer_from(a.img, lg, name, x, y)
    lg.delete()
    a.lay = flatten(a.img)


def ring(a, box, width, rgb, base):
    x0, y0, x1, y1 = box
    fill_ellipse(a.img, a.lay, box, rgb)
    fill_ellipse(a.img, a.lay, (x0 + width, y0 + width, x1 - width, y1 - width), base)


def build():
    rng = random.Random(11)
    a = Atlas(ATLAS)
    R = a.rect
    L = lambda: a.lay  # noqa: E731

    # --- swatches -----------------------------------------------------------------------
    a.fill("white_plastic", (236, 236, 232), 0.0, 0.55, noise=0.02)
    a.fill("black_plastic", (26, 26, 28), 0.0, 0.45, noise=0.02)
    a.fill("chrome", (205, 208, 212), 1.0, 0.85, noise=0.03)
    a.fill("steel", (176, 176, 172), 1.0, 0.6, noise=0.06, blur=0.6)
    a.fill("rack_grey", (92, 94, 98), 0.0, 0.35, noise=0.03)
    a.fill("yellow_plastic", (246, 204, 22), 0.0, 0.6)
    a.fill("clear", (228, 234, 238), 0.0, 0.9)
    a.fill("blue_liquid", (40, 140, 225), 0.0, 0.9)
    a.fill("pot_dark", (44, 44, 46), 0.2, 0.5, noise=0.03)
    a.fill("kraft", (168, 128, 88), 0.0, 0.15, noise=0.06)
    a.fill("beans", (58, 34, 22), 0.0, 0.5, noise=0.25, blur=1.5)
    a.fill("potato", (150, 78, 60), 0.0, 0.25, noise=0.12, blur=2.0)
    a.fill("cord_white", (228, 228, 224), 0.0, 0.4)
    a.fill("paper_white", (244, 244, 240), 0.0, 0.1, noise=0.02)
    a.fill("glass_dark", (60, 48, 38), 0.0, 0.9)
    a.fill("bristle", (238, 236, 228), 0.0, 0.2, noise=0.15, blur=0.5)
    a.fill("bread", (150, 86, 40), 0.0, 0.35, noise=0.08, blur=2.0)
    a.fill("label_white", (246, 246, 242), 0.0, 0.3)
    a.fill("pink", (236, 150, 190), 0.0, 0.3)
    a.fill("navy", (26, 40, 84), 0.0, 0.3)
    a.fill("green_box", (40, 124, 70), 0.0, 0.25)
    a.fill("bag_black", (22, 22, 24), 0.0, 0.55, noise=0.03)
    a.fill("cream", (236, 228, 206), 0.0, 0.4)
    a.fill("filters_white", (246, 244, 238), 0.0, 0.1)
    a.fill("rubber_black", (30, 30, 30), 0.0, 0.25)
    a.fill("towel_edge", (32, 78, 170), 0.0, 0.1)
    a.fill("mesh_red", (206, 70, 40), 0.0, 0.3)
    a.fill("spray_white", (242, 242, 240), 0.0, 0.5)
    a.fill("plates_blue", (54, 142, 210), 0.0, 0.35)
    a.fill("napkin_white", (246, 246, 244), 0.0, 0.2, noise=0.03)
    a.fill("bamboo_end", (206, 168, 110), 0.0, 0.3, noise=0.05)

    # onion skins: golden brown with the red mesh bag painted over them
    x, y, w, h = R("onion")
    fill_rect(a.img, L(), (x, y, w, h), (184, 124, 56))
    grain(a.img, L(), (x, y, w, h), 0.1, 1.5)
    for i in range(0, w, 12):
        fill_rect(a.img, L(), (x + i, y, 1, h), (176, 64, 34))
    for j in range(0, h, 12):
        fill_rect(a.img, L(), (x, y + j, w, 1), (176, 64, 34))
    a.material("onion", 0.0, 0.45)

    # --- towel: blue terry, woven diamond squares and a banded hem -----------------------
    x, y, w, h = R("towel_blue")
    fill_rect(a.img, L(), (x, y, w, h), (52, 108, 204))
    for i in range(0, w, 32):
        for j in range(0, h, 32):
            fill_rect(a.img, L(), (x + i + 4, y + j + 4, 24, 24), (30, 76, 168))
            fill_rect(a.img, L(), (x + i + 10, y + j + 10, 12, 12), (58, 118, 212))
    fill_rect(a.img, L(), (x, y, w, 14), (34, 80, 170))
    fill_rect(a.img, L(), (x, y + h - 14, w, 14), (34, 80, 170))
    grain(a.img, L(), (x, y, w, h), 0.07, 0.8)
    a.material("towel_blue", 0.0, 0.05)

    # --- pizza box: green, yellow band along one edge, a pizza drawn from scratch --------
    x, y, w, h = R("pizza_top")
    fill_rect(a.img, L(), (x, y, w, h), (38, 126, 70))
    fill_rect(a.img, L(), (x, y + h - 44, w, 36), (238, 206, 44))
    fill_rect(a.img, L(), (x + 16, y + h - 34, 120, 6), (38, 126, 70))      # plain stripe, no text
    cx, cy, r = x + 128, y + 104, 92
    fill_ellipse(a.img, L(), (cx - r, cy - r, cx + r, cy + r), (206, 150, 80))          # crust
    fill_ellipse(a.img, L(), (cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12), (196, 50, 36))   # sauce
    for _ in range(26):                                                                   # cheese
        px, py = cx + rng.randint(-66, 66), cy + rng.randint(-66, 66)
        if (px - cx) ** 2 + (py - cy) ** 2 < 70 ** 2:
            s = rng.randint(10, 22)
            fill_ellipse(a.img, L(), (px - s, py - s // 2, px + s, py + s // 2), (244, 206, 96))
    for _ in range(9):                                                                    # pepperoni
        px, py = cx + rng.randint(-58, 58), cy + rng.randint(-58, 58)
        if (px - cx) ** 2 + (py - cy) ** 2 < 62 ** 2:
            fill_ellipse(a.img, L(), (px - 11, py - 11, px + 11, py + 11), (150, 30, 30))
    for _ in range(12):                                                                   # green peppers
        px, py = cx + rng.randint(-60, 60), cy + rng.randint(-60, 60)
        if (px - cx) ** 2 + (py - cy) ** 2 < 62 ** 2:
            fill_rect(a.img, L(), (px, py, 10, 4), (60, 150, 60))
    a.material("pizza_top", 0.0, 0.35)
    x, y, w, h = R("pizza_side")
    fill_rect(a.img, L(), (x, y, w, h), (38, 126, 70))
    fill_rect(a.img, L(), (x, y + h // 2 - 8, w, 16), (238, 206, 44))
    a.material("pizza_side", 0.0, 0.3)

    # --- paper-towel pack: light blue swirl print, parody mark, rolls through the film -----
    x, y, w, h = R("tpack_side")
    base = (150, 212, 216)
    fill_rect(a.img, L(), (x, y, w, h), base)
    for i in range(20, w - 20, 44):
        for j in range(20, h - 20, 44):
            ox = (j // 44) % 2 * 20
            if i + ox + 18 < w:
                ring(a, (x + i + ox - 18, y + j - 18, x + i + ox + 18, y + j + 18), 3, (186, 232, 234), base)
    fill_rect(a.img, L(), (x, y, w, 12), (40, 70, 130))
    fill_rect(a.img, L(), (x, y + h - 12, w, 12), (40, 70, 130))
    fill_rect(a.img, L(), (x + w - 70, y + 30, 46, 196), (250, 250, 250))                  # count panel, blank
    fill_rect(a.img, L(), (x + w - 64, y + 40, 34, 60), (40, 70, 130))
    put_logo(a, "soakington", x + 20, y + 60, 400)
    a.material("tpack_side", 0.0, 0.7)
    x, y, w, h = R("tpack_end")
    fill_rect(a.img, L(), (x, y, w, h), (220, 236, 238))
    for i in range(2):
        for j in range(2):
            cx0, cy0 = x + 14 + i * 116, y + 14 + j * 116
            fill_ellipse(a.img, L(), (cx0, cy0, cx0 + 112, cy0 + 112), (246, 246, 244))
            ring(a, (cx0 + 8, cy0 + 8, cx0 + 104, cy0 + 104), 1, (224, 224, 222), (246, 246, 244))
            ring(a, (cx0 + 30, cy0 + 30, cx0 + 82, cy0 + 82), 1, (224, 224, 222), (246, 246, 244))
            fill_ellipse(a.img, L(), (cx0 + 44, cy0 + 44, cx0 + 68, cy0 + 68), (150, 120, 90))
            fill_ellipse(a.img, L(), (cx0 + 49, cy0 + 49, cx0 + 63, cy0 + 63), (70, 60, 50))
    fill_rect(a.img, L(), (x, y, w, 12), (40, 70, 130))
    fill_rect(a.img, L(), (x, y + h - 12, w, 12), (40, 70, 130))
    a.material("tpack_end", 0.0, 0.7)
    x, y, w, h = R("tpack_top")
    fill_rect(a.img, L(), (x, y, w, h), (150, 212, 216))
    for i in range(4):
        for j in range(2):
            cx0, cy0 = x + 8 + i * 62, y + 6 + j * 60
            fill_ellipse(a.img, L(), (cx0, cy0, cx0 + 56, cy0 + 56), (244, 244, 242))
    a.material("tpack_top", 0.0, 0.7)

    # --- napkin packs: quilted white, blue side band with the parody mark ------------------
    x, y, w, h = R("napkin_side")
    fill_rect(a.img, L(), (x, y, w, h), (60, 150, 214))
    fill_rect(a.img, L(), (x, y, w, 10), (246, 246, 244))
    fill_rect(a.img, L(), (x, y + h - 10, w, 10), (246, 246, 244))
    put_logo(a, "napsody", x + 40, y + 34, 176)
    a.material("napkin_side", 0.0, 0.6)
    x, y, w, h = R("napkin_top")
    fill_rect(a.img, L(), (x, y, w, h), (246, 246, 244))
    for i in range(0, w, 16):
        fill_rect(a.img, L(), (x + i, y, 1, h), (226, 226, 224))
        fill_rect(a.img, L(), (x, y + i, w, 1), (226, 226, 224))
    for k, col in enumerate(((242, 194, 48), (226, 71, 75), (87, 184, 90), (47, 134, 201))):
        fill_rect(a.img, L(), (x + 52 + k * 7, y + 50, 6, 26), col)          # plain colour bar
    a.material("napkin_top", 0.0, 0.6)

    # --- paper plates pack: blue band, white plates showing on top -------------------------
    x, y, w, h = R("plates_side")
    fill_rect(a.img, L(), (x, y, w, h), (54, 142, 210))
    fill_rect(a.img, L(), (x, y + 20, w, 40), (250, 250, 250))
    fill_rect(a.img, L(), (x + 170, y + 70, 60, 40), (250, 250, 250))                    # blank count badge
    a.material("plates_side", 0.0, 0.4)
    x, y, w, h = R("plates_top")
    fill_rect(a.img, L(), (x, y, w, h), (54, 142, 210))
    fill_ellipse(a.img, L(), (x + 6, y + 6, x + w - 6, y + h - 6), (250, 250, 250))
    ring(a, (x + 22, y + 22, x + w - 22, y + h - 22), 2, (226, 226, 226), (250, 250, 250))
    a.material("plates_top", 0.0, 0.4)

    # --- pink box: blank, a white wave band and a purple dot, blue edge strip ---------------
    x, y, w, h = R("pink_face")
    fill_rect(a.img, L(), (x, y, w, h), (236, 150, 190))
    fill_rect(a.img, L(), (x, y, 22, h), (70, 80, 170))
    for i in range(0, w - 22, 24):
        fill_ellipse(a.img, L(), (x + 22 + i, y + 70, x + 22 + i + 30, y + 96), (250, 246, 250))
    fill_ellipse(a.img, L(), (x + 180, y + 16, x + 230, y + 66), (130, 70, 170))
    a.material("pink_face", 0.0, 0.3)

    # --- navy paper cups with white chevron rows -------------------------------------------
    x, y, w, h = R("cups")
    fill_rect(a.img, L(), (x, y, w, h), (26, 40, 84))
    for j in range(8, h, 22):
        for i in range(0, w, 16):
            dy = 0 if (i // 16) % 2 == 0 else 5
            fill_rect(a.img, L(), (x + i + 2, y + j + dy, 11, 3), (240, 240, 240))
    a.material("cups", 0.0, 0.3)
    a.fill("cups_top", (244, 244, 242), 0.0, 0.3)

    # --- blank labels -----------------------------------------------------------------------
    x, y, w, h = R("can_label")
    fill_rect(a.img, L(), (x, y, w, h), (240, 186, 36))
    fill_rect(a.img, L(), (x, y + 8, w, 14), (222, 110, 30))
    fill_rect(a.img, L(), (x, y + h - 22, w, 14), (222, 110, 30))
    fill_ellipse(a.img, L(), (x + 70, y + 36, x + 180, y + 92), (250, 236, 200))
    a.material("can_label", 0.0, 0.5)
    x, y, w, h = R("soap_label")
    fill_rect(a.img, L(), (x, y, w, h), (32, 96, 206))
    for cx0, cy0, s in ((30, 22, 14), (52, 38, 9), (70, 20, 7), (96, 34, 12)):
        ring(a, (x + cx0 - s, y + cy0 - s, x + cx0 + s, y + cy0 + s), 2, (240, 246, 255), (32, 96, 206))
    a.material("soap_label", 0.0, 0.6)
    x, y, w, h = R("spray_label")
    fill_rect(a.img, L(), (x, y, w, h), (246, 204, 22))
    fill_round_rect(a.img, L(), (x + 14, y + 30, x + w - 14, y + 90), 12, (250, 250, 246))
    fill_rect(a.img, L(), (x + 24, y + 50, w - 48, 16), (40, 90, 190))
    a.material("spray_label", 0.0, 0.6)
    x, y, w, h = R("filter_label")
    fill_rect(a.img, L(), (x, y, w, h), (246, 244, 238))
    fill_ellipse(a.img, L(), (x + 34, y + 2, x + 94, y + 62), (30, 44, 90))
    fill_rect(a.img, L(), (x + 52, y + 24, 22, 18), (240, 240, 240))                       # cup glyph
    ring(a, (x + 70, y + 26, x + 80, y + 38), 2, (240, 240, 240), (30, 44, 90))
    a.material("filter_label", 0.0, 0.3)

    # --- coffee filters: white pleats -------------------------------------------------------
    x, y, w, h = R("filters_side")
    fill_rect(a.img, L(), (x, y, w, h), (246, 244, 238))
    for i in range(0, w, 6):
        fill_rect(a.img, L(), (x + i, y, 2, h), (226, 222, 214))
    a.material("filters_side", 0.0, 0.1)
    x, y, w, h = R("filters_end")
    fill_rect(a.img, L(), (x, y, w, h), (246, 244, 238))
    for k in range(6, 60, 8):
        ring(a, (x + 64 - k, y + 64 - k, x + 64 + k, y + 64 + k), 1, (224, 220, 212), (246, 244, 238))
    a.material("filters_end", 0.0, 0.1)

    # --- paper towel roll: embossed diamonds --------------------------------------------------
    x, y, w, h = R("roll_side")
    fill_rect(a.img, L(), (x, y, w, h), (246, 246, 244))
    for i in range(0, w, 12):
        for j in range(0, h, 12):
            ox = 6 if (j // 12) % 2 else 0
            fill_rect(a.img, L(), (x + i + ox, y + j, 3, 3), (226, 226, 224))
    a.material("roll_side", 0.0, 0.1)

    # --- bamboo knife block ----------------------------------------------------------------
    for reg in ("bamboo", "block_top"):
        x, y, w, h = R(reg)
        fill_rect(a.img, L(), (x, y, w, h), (206, 166, 108))
        for i in range(0, w, 18):
            fill_rect(a.img, L(), (x + i, y, 2, h), (180, 140, 86))
        grain(a.img, L(), (x, y, w, h), 0.06, 2.0)
        a.material(reg, 0.0, 0.35)
    x, y, w, h = R("block_top")
    for j in range(3):
        for i in range(4):
            fill_rect(a.img, L(), (x + 12 + i * 28, y + 20 + j * 36, 18, 6), (40, 30, 22))

    # --- appliances ---------------------------------------------------------------------------
    x, y, w, h = R("coffee_front")
    fill_rect(a.img, L(), (x, y, w, h), (26, 26, 28))
    a.material("coffee_front", 0.0, 0.45)
    x, y, w, h = R("coffee_badge")
    fill_rect(a.img, L(), (x, y, w, h), (20, 20, 20))
    put_logo(a, "mister_sippy", x + 4, y + 16, w - 8)
    a.material("coffee_badge", 0.0, 0.45)
    x, y, w, h = R("display")
    fill_rect(a.img, L(), (x, y, w, h), (30, 30, 32))
    fill_rect(a.img, L(), (x + 34, y + 14, 58, 22), (120, 132, 120))                       # blank LCD
    for i, bx in enumerate((10, 100, 112)):
        fill_ellipse(a.img, L(), (x + bx, y + 40, x + bx + 10, y + 50), (90, 90, 94))
    a.material("display", 0.0, 0.5)
    x, y, w, h = R("rice_front")
    fill_rect(a.img, L(), (x, y, w, h), (236, 236, 232))
    fill_round_rect(a.img, L(), (x + 30, y + 8, x + 98, y + 56), 8, (200, 200, 198))
    fill_ellipse(a.img, L(), (x + 44, y + 14, x + 54, y + 24), (230, 60, 40))            # cook light
    fill_ellipse(a.img, L(), (x + 74, y + 14, x + 84, y + 24), (240, 180, 40))           # warm light
    a.material("rice_front", 0.0, 0.5)
    a.fill("rice_top", (236, 236, 232), 0.0, 0.5)
    a.fill("pump_top", (62, 68, 76), 0.0, 0.5)
    x, y, w, h = R("kraft_print")
    fill_rect(a.img, L(), (x, y, w, h), (168, 128, 88))
    grain(a.img, L(), (x, y, w, h), 0.06, 1.0)
    fill_rect(a.img, L(), (x + 34, y + 30, 60, 60), (24, 24, 24))
    fill_ellipse(a.img, L(), (x + 50, y + 46, x + 78, y + 74), (240, 236, 228))
    a.material("kraft_print", 0.0, 0.15)
    x, y, w, h = R("tray_ribs")
    fill_rect(a.img, L(), (x, y, w, h), (96, 98, 102))
    for i in range(0, w, 10):
        fill_rect(a.img, L(), (x + i, y, 4, h), (80, 82, 86))
    a.material("tray_ribs", 0.0, 0.35)
    a.save()
