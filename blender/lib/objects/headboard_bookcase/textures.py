"""headboard_bookcase atlas (headless GIMP, gimp_textures.py helpers in scope).

Golden oak, photo-derived: the cathedral grain of the back panel (turned upright for the
vertical-grain side stiles, divider and apron), from the scan3 close-up keyframe 88399009696
(rotated copy: Reference/headboard_bookcase_work/s3_175.jpg), lighting flattened, tinted
to the bookcase's oak and made seamless. Edges (shelves, divider) a touch lighter with a
few soft rubbed spots, as the photos show on the rounded edges. Plain white power strip,
matte black plastics and cables, a white cable, a muted green strap, and flat cloth
colours for the clothes in the bays. No markings anywhere."""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "headboard_bookcase", "object.py")
SRC = os.path.join(REF, "headboard_bookcase_work", "s3_175.jpg")
BACK_BOX = (250, 150, 700, 290)     # cathedral grain, back panel of the right bay
OAK = (180, 122, 66)


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
R = random.Random(9)


def patch(box, w, h, tint, sigma=30, rotate=False):
    img = load(SRC)
    l, t, r, btm = box
    img.crop(r - l, btm - t, l, t)
    flatten_lighting(img, sigma, tint, detail=90.0)
    if rotate:
        img.rotate(Gimp.RotationType.DEGREES90)
    img.scale(w, h)
    gegl(img.get_layers()[0], "gegl:tile-seamless")
    return img


def tile_into(a, region, box, tw, th, tint, rotate=False):
    x, y, w, h = a.rect(region)
    img = patch(box, tw, th, tint, rotate=rotate)
    for yy in range(y, y + h, th):
        for xx in range(x, x + w, tw):
            add_layer_from(a.img, img, region, xx, yy)
    a.lay = flatten(a.img)
    img.delete()


def rubs(a, region, n, rgb, alpha):
    """Soft, paler rubbed spots on their own layer, blurred, then merged down."""
    x, y, w, h = a.rect(region)
    lay = Gimp.Layer.new(a.img, "rubs", a.size, a.size, Gimp.ImageType.RGBA_IMAGE, 100,
                         Gimp.LayerMode.NORMAL)
    a.img.insert_layer(lay, None, 0)
    lay.fill(Gimp.FillType.TRANSPARENT)
    for _ in range(n):
        cx, cy = x + R.randint(20, w - 20), y + R.randint(10, h - 10)
        rw, rh = R.randint(20, 50), R.randint(3, 8)
        fill_ellipse(a.img, lay, (cx - rw, cy - rh, cx + rw, cy + rh), rgb + (alpha,))
    gegl(lay, "gegl:gaussian-blur", std_dev_x=6.0, std_dev_y=2.0)
    a.lay = flatten(a.img)


def build():
    random.seed(9)
    a = Atlas(ATLAS)
    tile_into(a, "oak", BACK_BOX, 512, 256, OAK)
    a.material("oak", 0.0, 0.45)
    tile_into(a, "oak_v", BACK_BOX, 256, 512, OAK, rotate=True)
    a.material("oak_v", 0.0, 0.45)
    tile_into(a, "oak_edge", BACK_BOX, 256, 128, (190, 132, 74))
    rubs(a, "oak_edge", 6, (214, 170, 110), 0.25)          # rubbed, paler spots on the edges
    a.material("oak_edge", 0.0, 0.42)
    tile_into(a, "interior", BACK_BOX, 256, 128, (160, 108, 58))
    a.material("interior", 0.0, 0.35)
    a.fill("strip", (226, 224, 216), 0.0, 0.45, noise=0.02, blur=0.6)
    a.fill("plastic", (30, 30, 33), 0.0, 0.4, noise=0.03, blur=0.6)
    a.fill("cable", (22, 22, 24), 0.0, 0.5)
    a.fill("cable_white", (220, 220, 214), 0.0, 0.5)
    a.fill("accent", (120, 150, 60), 0.0, 0.2, noise=0.05, blur=0.8)
    a.fill("cloth_mauve", (150, 118, 124), 0.0, 0.08, noise=0.08, blur=2.0)
    a.fill("cloth_maroon", (92, 28, 34), 0.0, 0.08, noise=0.08, blur=2.0)
    a.fill("cloth_dark", (34, 32, 36), 0.0, 0.08, noise=0.06, blur=2.0)
    a.fill("strap", (36, 38, 40), 0.0, 0.15, noise=0.06, blur=1.0)
    a.fill("cushion", (48, 48, 52), 0.0, 0.08, noise=0.06, blur=1.0)
    a.save()
