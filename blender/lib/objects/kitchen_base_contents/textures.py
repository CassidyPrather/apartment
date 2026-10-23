"""kitchen_base_contents atlas (1024): flat swatches for the plastics, metals, wood and
ceramics, plus painted regions for the packaging (flat colour blocks in the real colour
schemes: no text, logo or barcode anywhere), the oven gloves' blue stripe print, the blue
towel, the knit pot holders and the stained cabinet-floor liner."""

import ast
import os
import random

PKG = os.path.join(ROOT, "blender", "lib", "objects", "kitchen_base_contents")


def _atlas():
    src = open(os.path.join(PKG, "object.py"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return eval(compile(ast.Expression(node.value), "object.py", "eval"),
                        {"NAME": "kitchen_base_contents"})
    raise RuntimeError("ATLAS not found")


ATLAS = _atlas()


def build():
    rng = random.Random(7)
    a = Atlas(ATLAS)
    R = a.rect

    def sub(region, fx0, fy0, fx1, fy1, rgb, ellipse=False, round_r=0):
        """Fill a fraction of a region (fractions of its width/height, from the top left)."""
        x, y, w, h = R(region)
        box = (round(x + fx0 * w), round(y + fy0 * h), round(x + fx1 * w), round(y + fy1 * h))
        # never an empty selection: GIMP fills the whole layer when nothing is selected
        box = (box[0], box[1], max(box[2], box[0] + 1), max(box[3], box[1] + 1))
        if ellipse:
            fill_ellipse(a.img, a.lay, box, rgb)
        elif round_r:
            fill_round_rect(a.img, a.lay, box, round_r, rgb)
        else:
            fill_rect(a.img, a.lay, (box[0], box[1], box[2] - box[0], box[3] - box[1]), rgb)

    def soften(region, amount=0.03, size=1.0):
        grain(a.img, a.lay, R(region), amount, size)

    # --- flat swatches ------------------------------------------------------------------
    a.fill("white_plastic", (232, 232, 228), 0.0, 0.5, noise=0.02)
    a.fill("black_plastic", (28, 28, 30), 0.0, 0.45, noise=0.02)
    a.fill("steel", (184, 186, 188), 1.0, 0.72, noise=0.05, blur=0.6)
    a.fill("steel_dark", (110, 112, 116), 1.0, 0.6, noise=0.04)
    a.fill("grey_plastic", (62, 64, 66), 0.0, 0.4, noise=0.02)
    a.fill("red_plastic", (200, 34, 38), 0.0, 0.55)
    a.fill("teal", (110, 178, 168), 0.0, 0.45)
    a.fill("yellow", (226, 214, 40), 0.0, 0.55)
    a.fill("green_sil", (24, 140, 62), 0.0, 0.4)
    a.fill("wood", (186, 140, 92), 0.0, 0.35, noise=0.08, blur=1.5)
    a.fill("twine", (214, 204, 182), 0.0, 0.1, noise=0.12, blur=0.8)
    a.fill("blue_cap", (30, 70, 160), 0.0, 0.55)
    a.fill("navy_liquid", (24, 40, 110), 0.0, 0.8)
    a.fill("aqua_liquid", (60, 160, 215), 0.0, 0.85)
    a.fill("pink", (226, 110, 140), 0.0, 0.55)
    a.fill("purple", (150, 70, 170), 0.0, 0.55)
    a.fill("nonstick", (36, 36, 38), 0.2, 0.45, noise=0.03)
    a.fill("pot_black", (22, 22, 24), 0.1, 0.5, noise=0.02)
    a.fill("tray_dark", (70, 72, 76), 0.0, 0.4, noise=0.02)
    a.fill("tray_light", (150, 152, 154), 0.0, 0.35, noise=0.03)
    a.fill("ceramic", (240, 240, 236), 0.0, 0.85)
    a.fill("cream_plastic", (232, 222, 196), 0.0, 0.55)
    a.fill("trim_red", (150, 24, 40), 0.0, 0.2, noise=0.05)
    a.fill("trash_white", (236, 236, 232), 0.0, 0.35, noise=0.04, blur=2.0)
    a.fill("trash_yellow", (240, 206, 70), 0.0, 0.35)
    a.fill("foil", (140, 142, 146), 0.6, 0.35, noise=0.15, blur=1.0)
    a.fill("mint", (160, 214, 186), 0.0, 0.5)
    a.fill("tan", (186, 150, 108), 0.0, 0.2, noise=0.08)
    a.fill("glass", (210, 222, 226), 0.0, 0.95)
    a.fill("clear_plastic", (226, 232, 236), 0.0, 0.9)
    a.fill("red_jug", (210, 30, 34), 0.0, 0.6)
    a.fill("light_blue", (150, 200, 235), 0.0, 0.6)
    a.fill("rubber_black", (30, 30, 32), 0.0, 0.25, noise=0.03)
    a.fill("chrome", (210, 212, 216), 1.0, 0.85)
    a.fill("white_lid", (244, 244, 242), 0.0, 0.5)
    a.fill("green_box", (22, 96, 58), 0.0, 0.3)
    a.fill("cardboard_in", (196, 160, 112), 0.0, 0.1, noise=0.05)
    a.fill("orange", (232, 120, 30), 0.0, 0.3)
    a.fill("steel_wool", (150, 150, 146), 0.7, 0.3, noise=0.35, blur=0.6)
    a.fill("black_glass", (40, 40, 44), 0.2, 0.9)
    a.fill("dark_red", (120, 20, 26), 0.0, 0.3)

    # --- oven glove: cream knit, blue silicone stripes (no wordmark). Mapped top-down over
    # each whole glove: image top = finger tips, bottom = cuff opening.
    a.fill("glove", (234, 226, 204), 0.0, 0.1, noise=0.10, blur=0.7)
    a.fill("glove_in", (150, 140, 118), 0.0, 0.05, noise=0.08)
    BL = (32, 72, 170)
    for j in range(7):                       # fingers: rows of short dashes across each finger
        for i in range(9):
            fx = 0.04 + i * 0.105 + (j % 2) * 0.03
            sub("glove", fx, 0.03 + j * 0.045, fx + 0.05, 0.03 + j * 0.045 + 0.018, BL)
    for b in range(4):                       # back of the hand: diagonal bands (stepped)
        for t in range(14):
            fx = 0.08 + b * 0.2 + t * 0.012
            fy = 0.36 + t * 0.022
            sub("glove", fx, fy, fx + 0.06, fy + 0.024, BL)
    for b in range(3):                       # cuff: long gently curving bands
        for t in range(12):
            fx = 0.18 + b * 0.26 + (0.03 if 3 < t < 9 else 0.0)
            fy = 0.68 + t * 0.026
            sub("glove", fx, fy, fx + 0.045, fy + 0.028, BL)
    sub("glove", 0.0, 0.95, 1.0, 0.975, (214, 204, 180))   # ribbed cuff edge
    soften("glove", 0.05, 0.8)

    # --- stained cabinet floor: off-white melamine with brown water rings and grit -------
    a.fill("stain", (226, 222, 210), 0.0, 0.3, noise=0.04)
    x, y, w, h = R("stain")
    for _ in range(26):
        cx, cy = x + rng.uniform(0.05, 0.95) * w, y + rng.uniform(0.1, 0.95) * h
        rx, ry = rng.uniform(8, 40), rng.uniform(5, 22)
        tone = rng.choice([(176, 150, 112, 0.35), (150, 120, 84, 0.3), (200, 182, 150, 0.4)])
        fill_ellipse(a.img, a.lay, (round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)), tone)
    for _ in range(140):
        cx, cy = x + rng.uniform(0, 1) * w, y + rng.uniform(0, 1) * h
        r = rng.uniform(1, 3)
        fill_ellipse(a.img, a.lay, (round(cx - r), round(cy - r), round(cx + r), round(cy + r)),
                     (100, 80, 60, 0.7))
    soften("stain", 0.05, 1.5)

    # --- packaging: flat colour blocks only --------------------------------------------
    # dishwasher-detergent box: dark green with a white panel, an orange-red badge, blue band
    a.fill("detergent", (20, 104, 62), 0.0, 0.35)
    sub("detergent", 0.15, 0.08, 0.85, 0.32, (240, 240, 236), round_r=10)
    sub("detergent", 0.32, 0.11, 0.68, 0.28, (226, 70, 36), ellipse=True)
    sub("detergent", 0.0, 0.62, 1.0, 0.70, (40, 110, 190))
    sub("detergent", 0.2, 0.76, 0.8, 0.92, (180, 210, 196))
    # bleach jug: white with a blue label and a red stripe
    a.fill("bleach_label", (238, 238, 234), 0.0, 0.5)
    sub("bleach_label", 0.08, 0.35, 0.92, 0.8, (40, 90, 180), round_r=8)
    sub("bleach_label", 0.08, 0.45, 0.92, 0.5, (210, 40, 40))
    sub("bleach_label", 0.25, 0.55, 0.75, 0.72, (236, 236, 232), round_r=6)
    # dish soap label: white oval on the blue liquid
    a.fill("dish_label", (60, 160, 215), 0.0, 0.85)
    sub("dish_label", 0.1, 0.15, 0.9, 0.85, (240, 244, 246), ellipse=True)
    sub("dish_label", 0.3, 0.3, 0.7, 0.55, (40, 120, 200), ellipse=True)
    # air freshener: white sleeve with pink flowers at the bottom and a green leaf patch
    a.fill("air_label", (240, 240, 240), 0.0, 0.5)
    sub("air_label", 0.0, 0.62, 1.0, 1.0, (234, 120, 150))
    for i in range(6):
        sub("air_label", 0.05 + i * 0.15, 0.55 + (i % 2) * 0.08, 0.2 + i * 0.15, 0.7 + (i % 2) * 0.08,
            (246, 170, 190), ellipse=True)
    sub("air_label", 0.3, 0.12, 0.7, 0.3, (90, 170, 80), round_r=4)
    # fabric spray: pale blue body, white label with a blue band
    a.fill("spray_label", (236, 240, 244), 0.0, 0.5)
    sub("spray_label", 0.0, 0.35, 1.0, 0.55, (40, 100, 190))
    sub("spray_label", 0.3, 0.62, 0.7, 0.8, (120, 180, 230), ellipse=True)
    # duster cans: white with a red band and a grey block
    a.fill("duster_label", (236, 236, 234), 0.0, 0.55)
    sub("duster_label", 0.0, 0.22, 1.0, 0.36, (205, 36, 40))
    sub("duster_label", 0.15, 0.5, 0.85, 0.62, (120, 120, 124))
    sub("duster_label", 0.15, 0.68, 0.55, 0.74, (30, 30, 30))
    # red jug: red with a silver-white label block
    a.fill("jug_label", (210, 30, 34), 0.0, 0.6)
    sub("jug_label", 0.3, 0.3, 0.7, 0.62, (226, 226, 230), round_r=6)
    sub("jug_label", 0.36, 0.36, 0.64, 0.42, (40, 40, 40))
    # whetstone box: grey-green with a black band
    a.fill("whetstone", (88, 100, 98), 0.0, 0.3, noise=0.03)
    sub("whetstone", 0.0, 0.35, 1.0, 0.6, (24, 26, 28))
    sub("whetstone", 0.1, 0.42, 0.22, 0.53, (230, 230, 230))
    # glass cleaner: dark blue bottle with a white label and a red stripe
    a.fill("glass_cleaner", (24, 40, 110), 0.0, 0.85)
    sub("glass_cleaner", 0.0, 0.3, 1.0, 0.7, (236, 240, 244))
    sub("glass_cleaner", 0.0, 0.42, 1.0, 0.5, (205, 40, 40))
    sub("glass_cleaner", 0.0, 0.5, 1.0, 0.58, (40, 90, 190))
    # cereal-type box: white side panel with grey rule lines, orange-red top band
    a.fill("cereal", (240, 238, 232), 0.0, 0.2)
    sub("cereal", 0.0, 0.0, 1.0, 0.12, (226, 90, 36))
    sub("cereal", 0.0, 0.12, 1.0, 0.16, (240, 180, 40))
    for i in range(14):
        sub("cereal", 0.12, 0.24 + i * 0.045, 0.62, 0.24 + i * 0.045 + 0.01, (90, 90, 90))
    sub("cereal", 0.68, 0.3, 0.9, 0.55, (200, 200, 196))
    sub("cereal", 0.12, 0.88, 0.5, 0.95, (180, 180, 176))
    # snack box: blue with a yellow disc and a white band
    a.fill("snack_box", (40, 90, 190), 0.0, 0.3)
    sub("snack_box", 0.0, 0.62, 1.0, 0.74, (240, 240, 240))
    sub("snack_box", 0.6, 0.66, 0.9, 0.95, (246, 210, 30), ellipse=True)
    sub("snack_box", 0.1, 0.12, 0.6, 0.45, (150, 60, 40), round_r=6)
    # zip-bag box: blue top with a dark window, red band, white rules
    a.fill("zip_box", (30, 70, 180), 0.0, 0.35)
    sub("zip_box", 0.0, 0.7, 1.0, 1.0, (205, 30, 40))
    sub("zip_box", 0.25, 0.12, 0.75, 0.62, (40, 40, 64))
    sub("zip_box", 0.0, 0.66, 1.0, 0.7, (240, 240, 240))
    # chip bag: gold with silver blocks
    a.fill("chip_bag", (200, 160, 60), 0.4, 0.6, noise=0.06)
    sub("chip_bag", 0.0, 0.0, 1.0, 0.25, (160, 160, 166))
    sub("chip_bag", 0.2, 0.4, 0.8, 0.7, (120, 70, 40), ellipse=True)
    # trash-bag roll: white film with faint rule lines
    a.fill("trash_roll", (238, 238, 234), 0.0, 0.35, noise=0.03, blur=2.0)
    # cardboard: kraft with a fold crease and darker edge
    a.fill("cardboard", (180, 140, 96), 0.0, 0.1, noise=0.06, blur=1.0)
    sub("cardboard", 0.0, 0.0, 1.0, 0.04, (150, 112, 74))
    # blue terry towel with a darker border stripe
    a.fill("towel", (40, 130, 200), 0.0, 0.05, noise=0.15, blur=0.7)
    sub("towel", 0.0, 0.82, 1.0, 0.9, (26, 96, 160))
    soften("towel", 0.08, 0.6)
    # knit pot holder: black with a dark grey grid
    a.fill("potholder", (30, 30, 32), 0.0, 0.1, noise=0.08, blur=0.6)
    for i in range(16):
        sub("potholder", i / 16, 0, i / 16 + 0.015, 1, (52, 52, 56))
        sub("potholder", 0, i / 16, 1, i / 16 + 0.015, (52, 52, 56))
    # slotted turner head: black with a grid of steel-grey holes
    a.fill("slotted", (30, 30, 32), 0.0, 0.4)
    for j in range(6):
        for i in range(5):
            sub("slotted", 0.1 + i * 0.17, 0.08 + j * 0.15, 0.1 + i * 0.17 + 0.1,
                0.08 + j * 0.15 + 0.08, (90, 90, 92), ellipse=True)
    a.save()
