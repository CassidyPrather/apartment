"""Window blinds atlas (512): off-white PVC vanes with a faint vertical emboss, white
headrail, dark carrier slot, clear-ish wand. Runs inside headless GIMP."""

ATLAS = {
    "name": "window_blinds",
    "size": 512,
    "regions": {
        "vane": (0, 0, 256, 512),
        "rail": (256, 0, 256, 256),
        "carrier": (256, 256, 128, 128),
        "wand": (384, 256, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("vane", (232, 231, 224), 0.0, 0.25, noise=0.025, blur=3.0)
    a.fill("rail", (238, 238, 233), 0.0, 0.40, noise=0.015, blur=1.5)
    a.fill("carrier", (70, 70, 68), 0.0, 0.2)
    a.fill("wand", (214, 218, 216), 0.0, 0.7)
    fill_rect(a.img, a.lay, (256, 384, 256, 128), (238, 238, 233))
    fill_rect(a.mimg, a.mlay, (256, 384, 256, 128), (0, 0, 0, 0.4))
    a.save()
