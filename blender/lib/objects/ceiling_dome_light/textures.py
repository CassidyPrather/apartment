"""Ceiling dome light atlas (512): brushed nickel ring and frosted white glass diffuser
with a warm glow (emission on the diffuser region only). Runs inside headless GIMP."""

ATLAS = {
    "name": "ceiling_dome_light",
    "size": 512,
    "regions": {
        "metal": (0, 0, 256, 256),
        "diffuser": (256, 0, 256, 256),
    },
}


def build():
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("metal")
    a.fill("metal", (172, 170, 166), 1.0, 0.55, noise=0.08, blur=0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=30.0, angle=0.0)
    Gimp.Selection.none(a.img)
    a.fill("diffuser", (244, 242, 236), 0.0, 0.3, noise=0.01, blur=2.0)
    fill_rect(a.img, a.lay, (0, 256, 512, 256), (172, 170, 166))
    fill_rect(a.mimg, a.mlay, (0, 256, 512, 256), (255, 0, 0, 0.55))
    eimg, elay = a.glow_layer()
    fill_rect(eimg, elay, (0, 0, 512, 512), (0, 0, 0))
    fill_rect(eimg, elay, a.rect("diffuser"), (255, 222, 176))
    a.save()
