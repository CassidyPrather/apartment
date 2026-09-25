"""Ceiling light bar atlas (512): brushed nickel and frosted white glass that glows warm
(emission on the lens region only). Runs inside headless GIMP."""

ATLAS = {
    "name": "ceiling_light_bar",
    "size": 512,
    "regions": {
        "metal": (0, 0, 256, 256),
        "lens": (256, 0, 256, 256),
    },
}


def build():
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("metal")
    a.fill("metal", (168, 168, 164), 1.0, 0.6, noise=0.08, blur=0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=30.0, angle=0.0)
    Gimp.Selection.none(a.img)
    a.fill("lens", (246, 243, 236), 0.0, 0.35, noise=0.01, blur=2.0)
    fill_rect(a.img, a.lay, (0, 256, 512, 256), (168, 168, 164))
    fill_rect(a.mimg, a.mlay, (0, 256, 512, 256), (255, 0, 0, 0.6))
    eimg, elay = a.glow_layer()
    fill_rect(eimg, elay, (0, 0, 512, 512), (0, 0, 0))
    fill_rect(eimg, elay, a.rect("lens"), (255, 214, 160))
    a.save()
