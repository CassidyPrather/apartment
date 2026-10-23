"""vanity_contents atlas (512): flat colour swatches only, painted from scratch. Every
package here is a plain colour block in its real colour scheme: no names, logos, text
or barcodes. Runs inside headless GIMP with the gimp_textures helpers in scope; the top
level is plain Python so object.py can read ATLAS from this file.
"""

# (name, rgb, metallic, smoothness) -- one 32 px swatch each
SWATCHES = [
    # under the sink
    ("white", (238, 238, 234), 0.0, 0.55), ("off_white", (226, 222, 210), 0.0, 0.45),
    ("black", (26, 26, 28), 0.0, 0.5), ("navy", (28, 40, 104), 0.0, 0.55),
    ("mw_blue", (52, 132, 196), 0.0, 0.8), ("mw_label", (196, 214, 228), 0.2, 0.6),
    ("mw_band", (24, 70, 150), 0.0, 0.6), ("plum", (112, 34, 64), 0.0, 0.6),
    ("dark_red", (150, 28, 48), 0.0, 0.6), ("dent_green", (34, 128, 70), 0.0, 0.45),
    ("dent_dark", (20, 78, 44), 0.0, 0.45), ("dent_white", (236, 238, 232), 0.0, 0.35),
    ("rinse_blue", (36, 74, 160), 0.0, 0.6), ("silver", (180, 184, 190), 0.7, 0.6),
    ("jo_blue", (54, 150, 206), 0.0, 0.7), ("sanit_clear", (214, 226, 232), 0.0, 0.85),
    ("sanit_blue", (40, 128, 206), 0.0, 0.6), ("red", (196, 22, 40), 0.0, 0.6),
    ("gold", (198, 160, 88), 0.7, 0.6), ("jug_liquid", (232, 222, 172), 0.0, 0.85),
    ("label_white", (244, 244, 240), 0.0, 0.35), ("label_blue", (60, 120, 196), 0.0, 0.4),
    ("gc_blue", (36, 104, 196), 0.0, 0.8), ("bc_blue", (24, 72, 196), 0.0, 0.6),
    ("bc_teal", (96, 196, 206), 0.0, 0.6), ("tissue_navy", (30, 42, 96), 0.0, 0.3),
    ("tissue_blue", (88, 132, 200), 0.0, 0.3), ("pack_white", (236, 236, 230), 0.0, 0.4),
    ("tan_pouch", (150, 122, 74), 0.0, 0.35), ("lavender", (170, 140, 210), 0.0, 0.5),
    ("pale_blue", (176, 210, 236), 0.0, 0.6), ("tb_clear", (222, 230, 236), 0.0, 0.7),
    # in the top drawer
    ("swab_blue", (64, 178, 214), 0.0, 0.45), ("swab_white", (246, 246, 242), 0.0, 0.3),
    ("paste_white", (244, 244, 244), 0.0, 0.5), ("paste_red", (206, 30, 36), 0.0, 0.5),
    ("paste_blue", (30, 52, 130), 0.0, 0.5), ("orange", (244, 140, 30), 0.0, 0.55),
    ("bristle_teal", (70, 170, 170), 0.0, 0.3), ("coral", (222, 128, 100), 0.0, 0.45),
    ("coral_dark", (196, 106, 82), 0.0, 0.4), ("copper", (200, 126, 86), 0.8, 0.6),
    ("brush_dark", (40, 34, 34), 0.0, 0.3), ("band_blue", (62, 150, 210), 0.0, 0.4),
    ("razor_pink", (222, 46, 120), 0.0, 0.6), ("teal_box", (84, 176, 166), 0.0, 0.4),
    ("teal_card", (70, 168, 196), 0.0, 0.45), ("rose_gold", (210, 150, 128), 0.8, 0.6),
    ("jar_navy", (30, 56, 112), 0.0, 0.6), ("yellow", (240, 206, 40), 0.0, 0.5),
    ("floss_grey", (226, 228, 230), 0.0, 0.4), ("magenta", (214, 52, 120), 0.0, 0.5),
    ("lime", (170, 200, 70), 0.0, 0.4), ("bag_clear", (230, 236, 240), 0.0, 0.9),
]


def _regions():
    return {name: ((i % 16) * 32, (i // 16) * 32, 32, 32) for i, (name, _, _, _) in enumerate(SWATCHES)}


ATLAS = {"name": "vanity_contents", "size": 512, "regions": _regions()}


def build():
    a = Atlas(ATLAS)
    for name, rgb, met, sm in SWATCHES:
        a.fill(name, rgb, met, sm, noise=0.01)
    a.save()
