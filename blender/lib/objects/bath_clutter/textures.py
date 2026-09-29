"""bath_clutter atlas (1024): the bathroom's everyday items outside the tub and the linen
niche. Painted from scratch, no photo pixels:
  - a blue-grey shag bath mat (large planar region)
  - a tan terry hand towel with a dobby band near the hem
  - parody labels: Slatherby lotion, Swishco mouthwash, Scrubtastic / Germinator /
    Gunk-B-Gone cleaner sprays, Smudgebuster wipes, Wallaboo hair spray, Mist
    Opportunity setting spray (SVG logos in logos/, drawn from scratch)
  - a 7-day pill box lid strip, a steel makeup palette, toilet-paper and paper-towel
    roll ends, and a 64 px swatch per flat colour.
No real text anywhere: fine print is painted as grey bars.
Runs inside headless GIMP with the gimp_textures helpers in scope; the top level is
plain Python so object.py can read ATLAS from this file.
"""

import os
import random

# (name, rgb, metallic, smoothness) -- one 64 px swatch each
SWATCHES = [
    ("tb_white", (236, 236, 233), 0.0, 0.55), ("tb_blue", (40, 120, 205), 0.0, 0.55),
    ("teal", (140, 208, 208), 0.0, 0.6), ("teal_dark", (96, 168, 176), 0.0, 0.55),
    ("mw_liquid", (92, 18, 38), 0.0, 0.8), ("clear", (226, 232, 236), 0.0, 0.85),
    ("black", (24, 24, 26), 0.0, 0.4), ("soap_body", (122, 136, 160), 0.0, 0.6),
    ("dark_grey", (72, 74, 78), 0.0, 0.45), ("strt_blue", (38, 150, 232), 0.0, 0.6),
    ("lotion_yellow", (240, 224, 140), 0.0, 0.55), ("pump_blue", (36, 66, 168), 0.0, 0.55),
    ("white", (240, 240, 238), 0.0, 0.5), ("orange", (245, 160, 40), 0.0, 0.5),
    ("deo_blue", (40, 110, 200), 0.0, 0.5), ("deo_light", (140, 192, 236), 0.0, 0.5),
    ("paste_white", (246, 246, 246), 0.0, 0.5), ("lip_gold", (205, 165, 85), 0.8, 0.6),
    ("lip_black", (32, 32, 34), 0.0, 0.6), ("lip_rose", (190, 112, 112), 0.3, 0.5),
    ("rose_gold", (205, 145, 125), 0.8, 0.55), ("tan", (215, 172, 132), 0.0, 0.2),
    ("mirror_face", (210, 214, 218), 1.0, 0.95), ("jar_purple", (112, 72, 202), 0.0, 0.6),
    ("jar_purple_dark", (72, 42, 122), 0.0, 0.5), ("purple_body", (122, 62, 192), 0.0, 0.6),
    ("purple_cap", (170, 130, 225), 0.0, 0.6), ("black_matte", (30, 30, 32), 0.0, 0.3),
    ("jar_blue", (44, 74, 184), 0.0, 0.6), ("jar_blue_dark", (30, 50, 132), 0.0, 0.5),
    ("pill_white", (236, 236, 240), 0.0, 0.5), ("bag_black", (26, 26, 29), 0.0, 0.25),
    ("bag_tan", (176, 132, 92), 0.0, 0.35), ("zipper", (52, 52, 54), 0.3, 0.4),
    ("metal", (172, 172, 175), 0.9, 0.6), ("beige", (216, 176, 140), 0.0, 0.5),
    ("navy", (30, 40, 92), 0.0, 0.55), ("wipes_blue", (152, 192, 236), 0.0, 0.45),
    ("silver", (192, 197, 203), 0.6, 0.55), ("cord_white", (236, 236, 233), 0.0, 0.4),
    ("outlet_white", (236, 233, 224), 0.0, 0.4), ("plug_red", (200, 32, 30), 0.0, 0.5),
    ("tag", (242, 242, 238), 0.0, 0.2), ("mat_side", (78, 92, 128), 0.0, 0.05),
    ("bin_white", (238, 238, 236), 0.0, 0.45), ("bag_white", (246, 246, 246), 0.0, 0.35),
    ("trash_tan", (226, 192, 152), 0.0, 0.1), ("stainless", (186, 186, 190), 0.9, 0.6),
    ("holder_white", (236, 234, 230), 0.0, 0.45), ("handle_taupe", (126, 106, 96), 0.0, 0.45),
    ("bristle", (226, 226, 222), 0.0, 0.2), ("chrome", (205, 205, 210), 1.0, 0.8),
    ("paper", (246, 246, 243), 0.0, 0.1), ("bamboo", (206, 166, 112), 0.0, 0.35),
    ("ptowel", (249, 249, 246), 0.0, 0.1), ("s1_body", (162, 212, 242), 0.0, 0.7),
    ("s1_head", (30, 80, 202), 0.0, 0.55), ("s2_body", (150, 206, 236), 0.0, 0.7),
    ("s2_neck", (212, 40, 40), 0.0, 0.6), ("s2_head", (244, 244, 244), 0.0, 0.5),
    ("s3_body", (245, 245, 242), 0.0, 0.6), ("s3_head", (246, 246, 246), 0.0, 0.5),
    ("steel_edge", (180, 182, 186), 0.9, 0.55), ("towel_edge", (205, 190, 110), 0.0, 0.05),
]

BIG = {
    "mat_top": (0, 0, 512, 512),
    "towel_brown": (768, 0, 128, 256),
    "lbl_s1": (896, 0, 128, 256),
    "lbl_s2": (512, 256, 128, 256),
    "lbl_s3": (640, 256, 128, 256),
    "lbl_lotion": (768, 256, 128, 256),
    "lbl_mouthwash": (896, 256, 128, 256),
    "wipes_top": (0, 512, 256, 192),
    "pill_top": (256, 512, 128, 256),
    "palette_top": (384, 512, 128, 128),
    "lbl_purple": (384, 640, 128, 128),
    "lbl_black": (512, 512, 128, 128),
    "lbl_holder": (640, 512, 128, 64),
    "tp_end": (640, 576, 64, 64),
    "ptowel_end": (704, 576, 64, 64),
}
# regions that share pixels with another region (separate UV projections, same paint)
ALIASES = {"towel_brown_a": "towel_brown"}


def _regions():
    r = dict(BIG)
    for i, (name, _, _, _) in enumerate(SWATCHES):
        r[name] = ((i % 16) * 64, 768 + (i // 16) * 64, 64, 64) if i < 64 else \
                  (((i - 64) % 16) * 64, 704, 64, 64)
    for a, src in ALIASES.items():
        r[a] = r[src]
    return r


ATLAS = {"name": "bath_clutter", "size": 1024, "regions": _regions()}

HERE_LOGOS = ("blender", "lib", "objects", "bath_clutter", "logos")
GREY = (120, 120, 124)


def put_logo(a, name, x, y, w):
    lg = load(os.path.join(ROOT, *HERE_LOGOS, name + ".svg"))
    lg.scale(w, round(lg.get_height() * w / lg.get_width()))
    add_layer_from(a.img, lg, name, x, y)
    lg.delete()
    a.lay = flatten(a.img)


def fine_print(a, x, y, w, h, rng, col=GREY, pitch=7, bar=2):
    for j in range(0, h - bar, pitch):
        k = x
        while k < x + w - 6:
            L = rng.randint(5, 22)
            fill_rect(a.img, a.lay, (k, y + j, min(L, x + w - k), bar), col)
            k += L + rng.randint(3, 6)


def terry(a, region, base, band, rng):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    grain(a.img, a.lay, (x, y, w, h), 0.12, 0.6)
    # faint vertical ribs of the pile
    for i in range(x, x + w, 3):
        fill_rect(a.img, a.lay, (i, y, 1, h), tuple(max(0, c - 10) for c in base) + (0.35,))
    # dobby band near the hem (the bottom of the region is the hem)
    b0, b1 = band
    fill_rect(a.img, a.lay, (x, y + b0, w, b1 - b0), tuple(max(0, c - 22) for c in base))
    for j in range(y + b0 + 2, y + b1 - 1, 4):
        fill_rect(a.img, a.lay, (x, j, w, 1), tuple(min(255, c + 12) for c in base))
    fill_rect(a.img, a.lay, (x, y + h - 5, w, 5), tuple(max(0, c - 16) for c in base))
    a.material(region, 0.0, 0.03)


def build():
    rng = random.Random(1206)
    a = Atlas(ATLAS)
    for name, rgb, met, sm in SWATCHES:
        a.fill(name, rgb, met, sm, noise=0.01)

    # --- bath mat: blue-grey shag, mottled with darker swirls and pale tips ----------
    x, y, w, h = a.rect("mat_top")
    fill_rect(a.img, a.lay, (x, y, w, h), (88, 104, 142))
    for _ in range(260):
        cx, cy = rng.randint(x, x + w), rng.randint(y, y + h)
        rx, ry = rng.randint(6, 30), rng.randint(4, 18)
        col = (60, 72, 104, 0.35) if rng.random() < 0.55 else (150, 164, 196, 0.3)
        fill_ellipse(a.img, a.lay, (cx - rx, cy - ry, cx + rx, cy + ry), col)
    grain(a.img, a.lay, (x, y, w, h), 0.22, 1.6)
    grain(a.img, a.lay, (x, y, w, h), 0.08, 0.0)
    a.material("mat_top", 0.0, 0.02)

    # --- towels --------------------------------------------------------------------
    terry(a, "towel_brown", (202, 162, 112), (214, 238), rng)

    # --- cleaner sprays (front labels) ----------------------------------------------
    x, y, w, h = a.rect("lbl_s1")                      # Scrubtastic daily shower spray
    fill_rect(a.img, a.lay, (x, y, w, h), (176, 220, 246))
    fill_rect(a.img, a.lay, (x, y + 40, w, 16), (255, 210, 31))
    put_logo(a, "scrubtastic", x + 6, y + 70, w - 12)
    fill_rect(a.img, a.lay, (x + 10, y + 150, w - 20, 22), (200, 40, 90))
    fine_print(a, x + 16, y + 190, w - 32, 50, rng, (70, 110, 160))
    a.material("lbl_s1", 0.0, 0.7)

    x, y, w, h = a.rect("lbl_s2")                      # Germinator disinfectant spray
    fill_rect(a.img, a.lay, (x, y, w, h), (150, 206, 236))
    for _ in range(40):
        cx, cy, r = rng.randint(x, x + w), rng.randint(y, y + h), rng.randint(2, 7)
        fill_ellipse(a.img, a.lay, (cx - r, cy - r, cx + r, cy + r), (230, 246, 255, 0.6))
    fill_rect(a.img, a.lay, (x, y, w, 30), (212, 40, 40))
    put_logo(a, "germinator", x + 4, y + 80, w - 8)
    fill_rect(a.img, a.lay, (x + 14, y + 200, w - 28, 26), (255, 220, 60))
    fine_print(a, x + 18, y + 150, w - 36, 36, rng, (60, 100, 150))
    a.material("lbl_s2", 0.0, 0.7)

    x, y, w, h = a.rect("lbl_s3")                      # Gunk-B-Gone degreaser
    fill_rect(a.img, a.lay, (x, y, w, h), (246, 246, 243))
    put_logo(a, "gunk_b_gone", x + 6, y + 40, w - 12)
    fill_rect(a.img, a.lay, (x, y + 150, w, h - 150), (250, 212, 40))
    fine_print(a, x + 14, y + 170, w - 28, 60, rng, (90, 80, 40))
    a.material("lbl_s3", 0.0, 0.6)

    # --- lotion, mouthwash ----------------------------------------------------------
    x, y, w, h = a.rect("lbl_lotion")                  # Slatherby body lotion
    fill_rect(a.img, a.lay, (x, y, w, h), (240, 224, 140))
    put_logo(a, "slatherby", x + 6, y + 24, w - 12)
    fine_print(a, x + 20, y + 90, w - 40, 30, rng, (40, 60, 120))
    fill_rect(a.img, a.lay, (x, y + 168, w, h - 168), (196, 150, 70))    # gold swoosh
    fill_ellipse(a.img, a.lay, (x - 20, y + 186, x + w + 20, y + h + 110), (240, 224, 140))
    a.material("lbl_lotion", 0.0, 0.55)

    x, y, w, h = a.rect("lbl_mouthwash")               # Swishco mouthwash
    fill_rect(a.img, a.lay, (x, y, w, h), (248, 248, 246))
    put_logo(a, "swishco", x + 8, y + 20, w - 16)
    fine_print(a, x + 10, y + 90, w - 20, 110, rng)
    fill_rect(a.img, a.lay, (x + 30, y + 212, w - 60, 30), (255, 255, 255))
    for i in range(x + 34, x + w - 34, 3):             # blank barcode block (no digits)
        fill_rect(a.img, a.lay, (i, y + 214, 1 + (i % 2), 22), (40, 40, 40))
    a.material("lbl_mouthwash", 0.0, 0.6)

    # --- counter labels -------------------------------------------------------------
    x, y, w, h = a.rect("lbl_purple")                  # Wallaboo hair spray (wrap)
    fill_rect(a.img, a.lay, (x, y, w, h), (122, 62, 192))
    put_logo(a, "wallaboo", x + 36, y + 20, 56)
    fine_print(a, x + 40, y + 84, 48, 30, rng, (220, 200, 240))
    a.material("lbl_purple", 0.0, 0.6)

    x, y, w, h = a.rect("lbl_black")                   # Mist Opportunity setting spray
    fill_rect(a.img, a.lay, (x, y, w, h), (30, 30, 32))
    put_logo(a, "mist_opportunity", x + 38, y + 24, 52)
    fine_print(a, x + 42, y + 70, 44, 36, rng, (150, 150, 150))
    a.material("lbl_black", 0.0, 0.3)

    x, y, w, h = a.rect("wipes_top")                   # Smudgebuster makeup wipes
    fill_rect(a.img, a.lay, (x, y, w, h), (152, 192, 236))
    fill_round_rect(a.img, a.lay, (x + 20, y + 14, x + w - 20, y + 70), 18, (176, 210, 244))
    put_logo(a, "smudgebuster", x + 16, y + 86, w - 32)
    fine_print(a, x + 30, y + 150, w - 60, 28, rng, (60, 90, 150))
    a.material("wipes_top", 0.0, 0.5)

    x, y, w, h = a.rect("pill_top")                    # 7-day AM/PM pill box lids
    fill_rect(a.img, a.lay, (x, y, w, h), (200, 200, 206))
    for i in range(7):
        cy = y + 4 + i * 36
        for col, tab in ((0, (56, 140, 220)), (1, (120, 80, 190))):
            cx = x + 4 + col * 62
            fill_round_rect(a.img, a.lay, (cx, cy, cx + 58, cy + 32), 5, (238, 238, 242))
            tx = cx if col == 0 else cx + 50
            fill_rect(a.img, a.lay, (tx, cy + 2, 8, 28), tab)
            fill_rect(a.img, a.lay, (cx + 22, cy + 13, 14, 5), (150, 150, 160))   # blank day mark
    a.material("pill_top", 0.0, 0.6)

    x, y, w, h = a.rect("palette_top")                 # steel makeup palette
    fill_rect(a.img, a.lay, (x, y, w, h), (188, 190, 195))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.0)
    for j in range(y, y + h, 2):
        fill_rect(a.img, a.lay, (x, j, w, 1), (200, 202, 206, 0.4))
    fill_ellipse(a.img, a.lay, (x + 12, y + h - 40, x + 40, y + h - 12), (20, 20, 20))
    fill_ellipse(a.img, a.lay, (x + 17, y + h - 35, x + 35, y + h - 17), (188, 190, 195))
    a.material("palette_top", 0.9, 0.7)

    x, y, w, h = a.rect("lbl_holder")                  # toilet-brush holder band
    fill_rect(a.img, a.lay, (x, y, w, h), (150, 160, 128))
    fill_rect(a.img, a.lay, (x, y + 8, w, 4), (230, 230, 220))
    fill_rect(a.img, a.lay, (x, y + h - 12, w, 4), (230, 230, 220))
    a.material("lbl_holder", 0.0, 0.45)

    for region, core, hole in (("tp_end", (170, 130, 90), (40, 34, 30)),
                               ("ptowel_end", (170, 130, 90), (206, 166, 112))):
        x, y, w, h = a.rect(region)
        fill_rect(a.img, a.lay, (x, y, w, h), (246, 246, 243))
        for r in range(28, 12, -4):                    # faint winding rings
            fill_ellipse(a.img, a.lay, (x + 32 - r, y + 32 - r, x + 32 + r, y + 32 + r),
                         (236, 236, 232) if r % 8 else (246, 246, 243))
        fill_ellipse(a.img, a.lay, (x + 20, y + 20, x + 44, y + 44), core)
        fill_ellipse(a.img, a.lay, (x + 23, y + 23, x + 41, y + 41), hole)
        a.material(region, 0.0, 0.1)

    x, y, w, h = a.rect("tag")                         # cord warning tag, no text
    fill_rect(a.img, a.lay, (x + 4, y + 10, w - 8, 8), (200, 40, 40))
    fine_print(a, x + 6, y + 26, w - 12, 30, rng, (150, 150, 150), pitch=6)
    a.save()
