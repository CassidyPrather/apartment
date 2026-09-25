"""bath_fixtures atlas (512): flat fills in the bathroom survey's albedo colours, with an
emission map lit only on the opal glass (light-bar shades and ceiling lamps). Runs inside
headless GIMP:

    python blender/lib/textures/gimp_headless.py --object bath_fixtures
"""

ATLAS = {
    "name": "bath_fixtures",
    "size": 512,
    "regions": {
        "trim": (0, 0, 128, 128),
        "plate": (128, 0, 128, 128),
        "nickel": (256, 0, 128, 128),
        "chrome": (384, 0, 128, 128),
        "mirror": (0, 128, 128, 128),
        "dark": (128, 128, 128, 128),
        "glow": (256, 128, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    fill_rect(a.img, a.lay, (0, 0, 512, 512), (235, 230, 220))
    a.fill("trim", (235, 230, 220), 0.0, 0.35, noise=0.01)        # survey white trim #ebe6dc
    a.fill("plate", (238, 236, 231), 0.0, 0.45, noise=0.005)
    a.fill("nickel", (168, 166, 160), 1.0, 0.55, noise=0.03)      # survey nickel #a8a6a0
    a.fill("chrome", (212, 214, 218), 1.0, 0.9, noise=0.01)
    a.fill("mirror", (188, 196, 200), 1.0, 0.97)
    a.fill("dark", (30, 29, 28), 0.0, 0.35, noise=0.01)
    a.fill("glow", (244, 242, 238), 0.0, 0.6)                    # survey opal glass #f4f2ee
    eimg, elay = a.glow_layer()
    fill_rect(eimg, elay, (0, 0, 512, 512), (0, 0, 0))
    fill_rect(eimg, elay, a.rect("glow"), (255, 236, 205))
    a.save()
