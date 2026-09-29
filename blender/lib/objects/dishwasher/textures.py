"""dishwasher atlas (headless GIMP, gimp_textures.py helpers in scope).

"panel" is a planar decal over the control band's front: a yellowed almond frame around a
white inset panel, a row of long dark vent slots along the top rim, unreadable grey label
dashes around the dial and the rocker, and the parody maker badge "grumbleworks"
(logos/grumbleworks.svg) at the lower left. "door" is a planar decal over the door: flat
white with a faint grey smudge low on the right, as in the photos. Colours sampled by eye
from dishwasher_1-3 and wide_..._004117/004119.
"""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "dishwasher", "object.py")
_LOGOS = os.path.join(ROOT, "blender", "lib", "objects", "dishwasher", "logos")


def _consts():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    out = {}
    for node in tree.body:     # plain constant assignments, evaluated in order
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = eval(compile(ast.Expression(node.value), _OBJ, "eval"), {}, out)
            except Exception:
                pass
    return out


C = _consts()
ATLAS = C["ATLAS"]
W, H, PH, KICK = C["W"], C["H"], C["PANEL_H"], C["KICK_H"]
CREAM = (232, 224, 198)
WHITE = (230, 232, 230)
INK = (150, 150, 146)


def build():
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("panel")
    sx, sz = w / W, h / PH
    px = lambda X: x + (X + W / 2) * sx
    pz = lambda Z: y + (PH - Z) * sz            # Z measured up from the band's bottom
    rect = lambda X0, X1, Z0, Z1, rgb: fill_rect(a.img, a.lay, (int(px(X0)), int(pz(Z1)), max(1, int((X1 - X0) * sx)),
                                                                max(1, int((Z1 - Z0) * sz))), rgb)
    a.fill("panel", CREAM, 0.0, 0.45, noise=0.012, blur=1.0)
    # white inset panel with a thin shadow line on its top edge
    ix0, ix1, iz0, iz1 = -W / 2 + 1.8, W / 2 - 2.2, 1.0, PH - 1.9
    fill_round_rect(a.img, a.lay, (px(ix0) - 1, pz(iz1) - 2, px(ix1) + 1, pz(iz0) + 1), 6, (196, 190, 170))
    fill_round_rect(a.img, a.lay, (px(ix0), pz(iz1), px(ix1), pz(iz0)), 6, WHITE)
    # vent slots in the top rim (left of the latch) and one short slot right of it
    for X0, X1 in ((-W / 2 + 2.2, -6.6), (-6.3, -2.8), (-2.5, -0.4), (1.3, 4.6)):
        rect(X0, X1, PH - 1.35, PH - 0.95, (52, 50, 46))
    # labels: dashes fanned around the dial, a few lines by the rocker
    dx, dr, dz = C["DIAL"]
    dzb = dz - (H - PH)
    for i, (ox, oz) in enumerate(((-1.6, 1.2), (0.9, 1.5), (1.2, 1.05), (1.25, 0.6), (-1.7, -1.1), (0.9, -1.3))):
        rect(dx + ox, dx + ox + 1.1, dzb + oz, dzb + oz + 0.12, INK)
    rx = C["ROCKER_X"]
    rect(rx - 0.5, rx + 0.5, dzb + 0.75, dzb + 0.87, INK)
    rect(rx - 0.55, rx + 0.55, dzb - 0.85, dzb - 0.73, INK)
    # parody maker badge, lower left of the inset
    lg = load(os.path.join(_LOGOS, "grumbleworks.svg"))
    bw = int(1.9 * sx)
    lg.scale(bw, max(4, int(bw * 0.25)))
    add_layer_from(a.img, lg, "badge", int(px(-7.8) - bw / 2), int(pz(iz0 + 1.2)))
    lg.delete()
    a.lay = flatten(a.img)

    # door: white, a faint grey smudge low on the right
    x, y, w, h = a.rect("door")
    a.fill("door", WHITE, 0.0, 0.55, noise=0.01, blur=1.0)
    dzs = h / (H - PH - KICK)
    img = a.img
    img.select_ellipse(Gimp.ChannelOps.REPLACE, x + (W / 2 + 6.5) * (w / W), y + h - 6.5 * dzs, 3.2 * (w / W), 2.2 * dzs)
    Gimp.Selection.feather(img, 10)
    _fill(a.lay, (150, 150, 150, 0.22))
    Gimp.Selection.none(img)
    img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y + h - 10, w, 10)
    Gimp.Selection.feather(img, 6)
    _fill(a.lay, (170, 168, 160, 0.25))
    Gimp.Selection.none(img)

    a.fill("white", WHITE, 0.0, 0.5)
    a.fill("slot", (40, 40, 40), 0.0, 0.2)
    a.fill("tub", (150, 150, 150), 0.0, 0.3)
    a.fill("dial", (228, 220, 194), 0.0, 0.5)
    a.fill("cream", CREAM, 0.0, 0.45)
    fill_rect(a.img, a.lay, (0, 416, 512, 96), (128, 128, 128))
    fill_rect(a.img, a.lay, (256, 416, 256, 96), (128, 128, 128))
    a.save()
