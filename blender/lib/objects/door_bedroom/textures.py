"""Shared "doors" atlas (512 px) for every door_* package: flat finishes only; the panel
shading comes from the modelled raised panels. Runs inside headless GIMP via
gimp_headless.py --object door_bedroom (other door packages exec this file)."""

ATLAS = {
    "name": "doors",
    "size": 512,
    "regions": {
        "paint": (0, 0, 256, 256),
        "nickel": (256, 0, 128, 128),
        "bronze": (384, 0, 128, 128),
        "vinyl": (256, 128, 128, 128),
        "dark": (384, 128, 128, 128),
        "glass": (0, 256, 128, 128),
        "aluminum": (128, 256, 128, 128),
    },
}


def build():
    a = Atlas(ATLAS)
    a.fill("paint", (234, 233, 228), 0.0, 0.55, noise=0.015, blur=1.5)     # semi-gloss white
    x, y, w, h = a.rect("nickel")
    a.fill("nickel", (172, 170, 164), 1.0, 0.55, noise=0.08, blur=0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=30.0, angle=0.0)                 # brushed streaks
    Gimp.Selection.none(a.img)
    a.fill("bronze", (72, 68, 64), 0.85, 0.5, noise=0.04, blur=0)          # dark lever set
    a.fill("vinyl", (228, 228, 222), 0.0, 0.4, noise=0.01)
    a.fill("dark", (38, 38, 38), 0.0, 0.2)
    a.fill("glass", (196, 212, 212), 0.0, 0.92)
    a.fill("aluminum", (190, 192, 194), 0.9, 0.5, noise=0.03)
    # fill the unused corner so nothing samples black
    fill_rect(a.img, a.lay, (256, 256, 256, 256), (234, 233, 228))
    fill_rect(a.mimg, a.mlay, (256, 256, 256, 256), (0, 0, 0, 0.55))
    fill_rect(a.img, a.lay, (0, 384, 256, 128), (234, 233, 228))
    fill_rect(a.mimg, a.mlay, (0, 384, 256, 128), (0, 0, 0, 0.55))
    a.save()
