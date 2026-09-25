"""Light stand atlas (256): satin black powder-coat, black plastic knobs, rubber feet,
the base station's matte body and its glossy dark face. Runs inside headless GIMP."""

ATLAS = {
    "name": "light_stand",
    "size": 256,
    "regions": {
        "metal": (0, 0, 128, 128),
        "plastic": (128, 0, 128, 128),
        "rubber": (0, 128, 128, 128),
        "box": (128, 128, 64, 128),
        "face": (192, 128, 64, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("metal", (30, 30, 32), 0.3, 0.45, noise=0.02, blur=1.0)
    a.fill("plastic", (24, 24, 25), 0.0, 0.35, noise=0.02, blur=1.0)
    a.fill("rubber", (18, 18, 18), 0.0, 0.15)
    a.fill("box", (28, 28, 30), 0.0, 0.3, noise=0.015, blur=1.0)
    a.fill("face", (12, 12, 14), 0.0, 0.85)
    a.save()
