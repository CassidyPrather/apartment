"""dresser atlas (1024): photo-derived honey oak.

Each drawer front is rectified from the sharp capture frame of the dresser front
(Reference/dresser_work/src_front.jpg, the rotated crop of wide_..011937) and pasted where
the planar front mapping puts that drawer, so every drawer keeps its own real cathedral
grain and wear. The top reuses two drawer crops (grain along X); the sides come from a
clean stretch of the left side panel (src_side.jpg, wide_..012006, between the lamp pole
and the lamp shade). Lighting is flattened and tinted to the dresser's oak. The only
painted wear is a slightly paler, worn strip along the top's front edge, as in the photo.
"""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dresser", "object.py")
WORK = os.path.join(REF, "dresser_work")


def _consts():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                names = [t] if isinstance(t, ast.Name) else getattr(t, "elts", [])
                try:
                    vals = ast.literal_eval(node.value)
                except ValueError:
                    continue
                if len(names) == 1:
                    out[names[0].id] = vals
                else:
                    for n, v in zip(names, vals):
                        out[n.id] = v
    return out


C = _consts()
ATLAS = C["ATLAS"]
OAK_TINT = (150, 108, 70)
EDGE = (168, 116, 70)

# drawer fronts in src_front.jpg (TL, TR, BR, BL), top drawer first
DRAWER_QUADS = [
    [(318, 652), (1340, 560), (1336, 824), (350, 1000)],
    [(358, 1034), (1328, 855), (1264, 1082), (385, 1323)],
    [(390, 1354), (1262, 1110), (1206, 1301), (407, 1548)],
    [(411, 1578), (1202, 1328), (1156, 1484), (426, 1743)],
    [(431, 1773), (1152, 1508), (1126, 1628), (445, 1892)],
]
SIDE_BOX = (482, 950, 1036, 1400)       # clean side panel patch in src_side.jpg


def shrink(quad, f):
    """Pull the top and bottom edges of a quad toward each other by fraction f."""
    tl, tr, br, bl = quad
    lerp = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    return [lerp(tl, bl, f), lerp(tr, br, f), lerp(br, tr, f), lerp(bl, tl, f)]


def photo(quad, w, h, sigma):
    img = rectify(os.path.join(WORK, "src_front.jpg"), quad, w, h)
    flatten_lighting(img, sigma, OAK_TINT, detail=95.0)
    return img


def paste(a, src, x, y):
    add_layer_from(a.img, src, "p", x, y)
    a.lay = flatten(a.img)
    src.delete()


def build():
    a = Atlas(ATLAS)
    W, H, T, KICK, GAP, N = C["W"], C["H"], C["T"], C["KICK"], C["GAP"], C["N_DRAWERS"]
    # front: base oak everywhere, then each drawer's own photo in its slot
    fx, fy, fw, fh = a.rect("front")
    a.fill("front", OAK_TINT, 0.0, 0.42, noise=0.03)
    ih = (H - T - KICK - GAP * N) / N
    px = lambda x: fx + round((x + W / 2) / W * fw)
    py = lambda z: fy + round((H - z) / H * fh)
    x0, x1 = px(-W / 2 + T), px(W / 2 - T)
    for i, quad in enumerate(DRAWER_QUADS):
        z0 = KICK + GAP / 2 + (N - 1 - i) * (ih + GAP) - 0.1
        z1 = z0 + ih + 0.2
        w, h = x1 - x0, py(z0) - py(z1)
        paste(a, photo(quad, w, h, 40), x0, py(z1))
        # the bevelled underside reads as the dark finger-pull gap under each front
        ub = py(z0 + 0.1) - py(z0 + 0.1 + C["UNDERCUT"] * 0.8 + 0.05)
        fill_rect(a.img, a.lay, (x0, py(z0 + 0.1) - ub, w, ub + 2), (40, 26, 16, 0.8))
    a.material("front", 0.0, 0.42)
    # top: two drawer crops stacked, grain along X
    tx, ty, tw, th = a.rect("top")
    paste(a, photo(shrink(DRAWER_QUADS[1], 0.1), tw, th // 2, 40), tx, ty)
    paste(a, photo(shrink(DRAWER_QUADS[2], 0.1), tw, th - th // 2, 40), tx, ty + th // 2)
    fill_rect(a.img, a.lay, (tx, ty + th - 8, tw, 8), EDGE + (0.35,))   # worn front edge
    a.material("top", 0.0, 0.40)
    # sides: the clean side-panel patch, made seamless and repeated up the panel
    sx, sy, sw, sh = a.rect("side")
    img = load(os.path.join(WORK, "src_side.jpg"))
    l, t, r, btm = SIDE_BOX
    img.crop(r - l, btm - t, l, t)
    flatten_lighting(img, 50, OAK_TINT, detail=80.0)
    img.scale(sw, sh // 2)
    gegl(img.get_layers()[0], "gegl:tile-seamless")
    for k in range(2):
        add_layer_from(a.img, img, "side", sx, sy + k * (sh // 2))
    a.lay = flatten(a.img)
    img.delete()
    a.material("side", 0.0, 0.40)
    a.fill("dark", (46, 30, 18), 0.0, 0.2, noise=0.03)
    a.fill("edge", EDGE, 0.0, 0.4, noise=0.05)
    a.save()
