"""floor_lamp atlas (256): satin black metal, a darker slotted socket, frosted white
glass. Emission: warm white on the bowl, brighter on the inside face."""

ATLAS = {
    "name": "floor_lamp",
    "size": 256,
    "regions": {
        "black": (0, 0, 128, 128),
        "socket": (128, 0, 128, 128),
        "glass_out": (0, 128, 128, 128),
        "glass_in": (128, 128, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("black", (26, 26, 28), 0.3, 0.45, noise=0.02)
    x, y, w, h = a.rect("socket")
    fill_rect(a.img, a.lay, (x, y, w, h), (30, 30, 32))
    for i in range(0, w, 12):
        fill_rect(a.img, a.lay, (x + i, y + 20, 4, h - 40), (10, 10, 10))
    a.material("socket", 0.0, 0.35)
    a.fill("glass_out", (242, 240, 236), 0.0, 0.3, noise=0.01, blur=2.0)
    a.fill("glass_in", (250, 246, 238), 0.0, 0.3)
    eimg, elay = a.glow_layer()
    fill_rect(eimg, elay, (0, 0, 256, 256), (0, 0, 0))
    fill_rect(eimg, elay, a.rect("glass_out"), (236, 214, 178))
    fill_rect(eimg, elay, a.rect("glass_in"), (255, 232, 196))
    a.save()
