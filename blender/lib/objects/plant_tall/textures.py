"""plant_tall atlas, painted from scratch in GIMP (no photo pixels): three ficus
leaf-sprig cards on transparent ground (albedo alpha = cutout), terracotta pot, tan
bark and potting soil. Leaf greens are colour-matched by eye to the corner crops.

Runs inside headless GIMP with the gimp_textures helpers in scope:
    python blender/lib/textures/gimp_headless.py --object plant_tall
"""

import math
import random

ATLAS = {
    "name": "plant_tall",
    "size": 1024,
    "regions": {
        "sprig_a": (0, 0, 512, 512),
        "sprig_b": (512, 0, 512, 512),
        "sprig_c": (0, 512, 512, 512),
        "pot": (512, 512, 256, 256),
        "bark": (768, 512, 256, 256),
        "soil": (512, 768, 256, 256),
    },
}
SPRIGS = ["sprig_a", "sprig_b", "sprig_c"]

# Ficus greens from the crops: deep shaded leaves, mid leaves, lit upper faces.
GREENS = [(34, 58, 26), (44, 72, 32), (56, 88, 38), (70, 104, 46), (86, 118, 54)]
TWIG = (118, 104, 78)


def jitter(c, amt):
    k = random.uniform(-amt, amt)
    return tuple(max(0, min(255, round(v * (1 + k)))) for v in c)


def poly(img, lay, pts, rgb, clip):
    """Fill a polygon clipped to `clip` (x, y, w, h); skip empty selections."""
    flat = []
    for x, y in pts:
        flat += [float(x), float(y)]
    img.select_polygon(Gimp.ChannelOps.REPLACE, flat)
    cx, cy, cw, ch = clip
    img.select_rectangle(Gimp.ChannelOps.INTERSECT, cx, cy, cw, ch)
    if not Gimp.Selection.is_empty(img):
        Gimp.context_set_foreground(color(tuple(rgb[:3])))
        Gimp.context_set_opacity(100.0 * (rgb[3] if len(rgb) == 4 else 1.0))
        lay.edit_fill(Gimp.FillType.FOREGROUND)
        Gimp.context_set_opacity(100.0)
    Gimp.Selection.none(img)


def leaf_outline(x, y, ang, L, W, n=9, tipf=0.85):
    """Pointed-oval leaf from its base (x, y) toward angle `ang` (radians, image space)."""
    ca, sa = math.cos(ang), math.sin(ang)
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        half = W / 2 * math.sin(math.pi * t ** tipf) ** 0.8
        a = L * t
        left.append((x + ca * a - sa * half, y + sa * a + ca * half))
        right.append((x + ca * a + sa * half, y + sa * a - ca * half))
    return left + list(reversed(right))


def leaf(img, lay, x, y, ang, L, W, rgb, clip):
    poly(img, lay, leaf_outline(x, y, ang, L, W), rgb, clip)
    # lit half, then the midrib
    ca, sa = math.cos(ang), math.sin(ang)
    lit = tuple(min(255, round(v * 1.18)) for v in rgb)
    pts = [(x + ca * L * t + sa * 0.5 * W / 2 * math.sin(math.pi * t ** 0.85),
            y + sa * L * t - ca * 0.5 * W / 2 * math.sin(math.pi * t ** 0.85)) for t in [i / 8 for i in range(9)]]
    pts += [(x + ca * L * t, y + sa * L * t) for t in [i / 8 for i in range(8, -1, -1)]]
    poly(img, lay, pts, lit, clip)
    rib = tuple(min(255, round(v * 1.45)) for v in rgb)
    stem(img, lay, [(x, y), (x + ca * L * 0.85, y + sa * L * 0.85)], 1.2, 0.6, rib + (0.8,), clip)


def stem(img, lay, pts, w0, w1, rgb, clip):
    """A tapering stroke along a polyline, as one polygon per segment."""
    n = len(pts) - 1
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        wa = (w0 + (w1 - w0) * i / n) / 2
        wb = (w0 + (w1 - w0) * (i + 1) / n) / 2
        poly(img, lay, [(x0 + nx * wa, y0 + ny * wa), (x1 + nx * wb, y1 + ny * wb),
                        (x1 - nx * wb, y1 - ny * wb), (x0 - nx * wa, y0 - ny * wa)], rgb, clip)


def curve(x0, y0, ang0, length, turn, n=10):
    pts = [(x0, y0)]
    a = ang0
    x, y = x0, y0
    for i in range(n):
        a += turn / n
        x += math.cos(a) * length / n
        y += math.sin(a) * length / n
        pts.append((x, y))
    return pts


def branch(img, lay, clip, pts, spacing, Lr, Wr, width, droop=0.35, side0=1):
    """A twig with alternate leaves; returns nothing. Leaves drawn after the twig."""
    stem(img, lay, pts, width, width * 0.35, TWIG, clip)
    # walk along the polyline
    acc, side = 0.0, side0
    seglens = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    total = sum(seglens)
    d = spacing * 0.6
    leaves = []
    while d < total - 4:
        # locate
        s, i = d, 0
        while i < len(seglens) - 1 and s > seglens[i]:
            s -= seglens[i]
            i += 1
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        f = s / max(seglens[i], 1e-6)
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        ta = math.atan2(y1 - y0, x1 - x0)
        la = ta + side * random.uniform(0.6, 1.05)
        # droop: pull the leaf direction toward straight down (+y in image space)
        la = math.atan2(math.sin(la) + droop, math.cos(la))
        scale = 0.7 + 0.3 * (1 - d / total) + random.uniform(-0.1, 0.1)
        L = random.uniform(*Lr) * scale
        W = random.uniform(*Wr) * scale
        pet = 7
        px, py = x + math.cos(la) * pet, y + math.sin(la) * pet
        stem(img, lay, [(x, y), (px, py)], 2.0, 1.2, TWIG, clip)
        leaves.append((px, py, la, L, W, jitter(random.choice(GREENS), 0.08)))
        side = -side
        d += spacing * random.uniform(0.8, 1.2)
    # terminal bud leaf
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    ta = math.atan2(yb - ya, xb - xa)
    leaves.append((xb, yb, ta, Lr[0] * 0.8, Wr[0] * 0.8, jitter(GREENS[3], 0.06)))
    for lf in leaves:
        leaf(img, lay, *lf[:5], lf[5], clip)


def sprig(a, region, style):
    x, y, w, h = a.rect(region)
    clip = (x + 2, y + 2, w - 4, h - 4)
    bx, by = x + w / 2, y + h - 3
    up = -math.pi / 2
    L, W = (70, 100), (30, 42)
    if style == "a":       # upright sprig with two side twigs
        main = curve(bx, by, up + 0.05, h * 0.9, -0.25)
        branch(a.img, a.lay, clip, curve(bx + 2, by - h * 0.33, up - 0.75, w * 0.42, 0.5), 30, L, W, 3.0, side0=-1)
        branch(a.img, a.lay, clip, curve(bx - 2, by - h * 0.5, up + 0.8, w * 0.38, -0.4), 30, L, W, 3.0)
        branch(a.img, a.lay, clip, main, 34, L, W, 4.5)
    elif style == "b":     # arching sprig, curving right, heavier leaves
        main = curve(bx - w * 0.15, by, up - 0.25, h * 0.95, 1.0)
        branch(a.img, a.lay, clip, curve(bx - w * 0.1, by - h * 0.35, up - 0.5, w * 0.35, -0.2), 28, L, W, 3.0, side0=-1)
        branch(a.img, a.lay, clip, main, 30, (78, 108), (32, 44), 4.5, droop=0.5)
    else:                  # fan of three short twigs, a dense clump
        for ang, ln, turn in ((up - 0.55, 0.62, 0.3), (up + 0.05, 0.85, -0.15), (up + 0.6, 0.66, -0.35)):
            branch(a.img, a.lay, clip, curve(bx, by, ang, h * ln, turn), 26, (62, 90), (28, 38), 3.5,
                   side0=random.choice((-1, 1)))
    a.material(region, 0.0, 0.28)


def build():
    random.seed(8401)
    a = Atlas(ATLAS)
    a.lay.add_alpha()
    for r in SPRIGS:
        x, y, w, h = a.rect(r)
        a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
        a.lay.edit_clear()
    Gimp.Selection.none(a.img)
    sprig(a, "sprig_a", "a")
    sprig(a, "sprig_b", "b")
    sprig(a, "sprig_c", "c")
    # Terracotta pot: warm orange clay, a lighter band at the top (rim) of the region.
    x, y, w, h = a.rect("pot")
    fill_rect(a.img, a.lay, (x, y, w, h), (172, 106, 70))
    for i in range(0, h, 8):
        fill_rect(a.img, a.lay, (x, y + i, w, 8), jitter((172, 106, 70), 0.04))
    fill_rect(a.img, a.lay, (x, y, w, round(h * 0.2)), (186, 120, 82))
    grain(a.img, a.lay, (x, y, w, h), 0.07, 1.2)
    a.material("pot", 0.0, 0.12)
    # Bark: pale tan stems with fine vertical streaks.
    x, y, w, h = a.rect("bark")
    fill_rect(a.img, a.lay, (x, y, w, h), (146, 126, 96))
    for i in range(40):
        sx = x + random.randint(0, w - 3)
        fill_rect(a.img, a.lay, (sx, y, random.randint(1, 3), h), jitter((120, 102, 76), 0.1) + (0.6,))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.8)
    a.material("bark", 0.0, 0.1)
    a.fill("soil", (58, 44, 34), 0.0, 0.05, noise=0.12, blur=1.0)
    a.save()
