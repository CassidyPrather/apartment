"""microwave atlas (headless GIMP, gimp_textures.py helpers in scope).

"front" is one planar decal over the whole front (1024 px across the 28 in width): plain
white top band with the parody wordmark "zapwhistle" (logos/zapwhistle.svg), seam lines,
the pale screened window with its shadowed top edge, and the keypad panel (black display,
pale pads with grey outlines and unreadable grey dashes for their labels, one pad outlined
in red). Colours sampled by eye from the capture frames (wide_..._004000/004016/004249).
The photos show no wear on the microwave, so none is painted.
"""

import ast
import os

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "microwave", "object.py")
_LOGOS = os.path.join(ROOT, "blender", "lib", "objects", "microwave", "logos")


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
W, H = C["W"], C["H"]
WHITE = (238, 239, 237)
SEAM = (196, 198, 198)
PAD = (224, 225, 225)
PAD_EDGE = (184, 186, 188)
INK = (150, 152, 156)


def build():
    a = Atlas(ATLAS)
    x, y, w, h = a.rect("front")
    s = w / W                                   # px per inch (same vertically: 640 / 17.5)
    px = lambda X: x + X * s                    # X measured from the left edge
    pz = lambda Z: y + (H - Z) * s
    rect = lambda X0, X1, Z0, Z1, rgb: fill_rect(a.img, a.lay, (int(px(X0)), int(pz(Z1)), max(1, int((X1 - X0) * s)),
                                                                max(1, int((Z1 - Z0) * s))), rgb)
    rrect = lambda X0, X1, Z0, Z1, r, rgb: fill_round_rect(a.img, a.lay, (px(X0), pz(Z1), px(X1), pz(Z0)), r, rgb)
    a.fill("front", WHITE, 0.0, 0.62, noise=0.008, blur=1.0)
    # seams: door panel outline, control column split, the column's top and bottom caps
    dx0, dx1, dz0, dz1 = C["DOOR"]
    rrect(dx0 - 0.08, dx1 + 0.08, dz0 - 0.08, dz1 + 0.08, 8, SEAM)
    rrect(dx0, dx1, dz0, dz1, 8, WHITE)
    rect(dx1 + 0.05, dx1 + 0.12, 0.3, H - 0.2, SEAM)
    rect(dx1 + 0.1, W - 0.3, 12.95, 13.02, SEAM)
    rect(dx1 + 0.1, W - 0.3, 2.0, 2.07, SEAM)
    # window: pale screen, shadowed top edge, thin darker rim
    wx0, wx1, wz0, wz1 = C["WINDOW"]
    rrect(wx0 - 0.1, wx1 + 0.1, wz0 - 0.1, wz1 + 0.1, 10, (176, 178, 180))
    rrect(wx0, wx1, wz0, wz1, 8, (206, 208, 208))
    rect(wx0 + 0.1, wx1 - 0.1, wz1 - 0.7, wz1 - 0.05, (150, 152, 154))
    grain(a.img, a.lay, (int(px(wx0)), int(pz(wz1 - 0.7)), int((wx1 - wx0) * s), int((wz1 - wz0 - 0.7) * s)), 0.02, 0.8)
    # keypad panel
    kx0, kx1, kz0, kz1 = C["PANEL"]
    rrect(kx0, kx1, kz0, kz1, 8, (206, 208, 208))
    rrect(kx0 + 0.06, kx1 - 0.06, kz0 + 0.06, kz1 - 0.06, 7, (236, 237, 235))
    rect(23.6, 25.2, 11.0, 11.7, (16, 17, 19))                    # display

    def pad(X0, X1, Z0, Z1, edge=PAD_EDGE):
        rect(X0, X1, Z0, Z1, edge)
        rect(X0 + 0.05, X1 - 0.05, Z0 + 0.05, Z1 - 0.05, PAD)
        cx, cz = (X0 + X1) / 2, (Z0 + Z1) / 2
        lw = min(0.5, (X1 - X0) * 0.55)
        rect(cx - lw / 2, cx + lw / 2, cz - 0.03, cz + 0.04, INK)

    rect(23.3, 25.5, 10.25, 10.32, INK)                            # section headings
    for i in range(3):
        pad(22.45 + i * 1.42, 23.75 + i * 1.42, 9.2, 9.7)
    for i in range(2):
        pad(22.45 + i * 2.13, 24.45 + i * 2.13, 8.5, 9.0)
    rect(23.5, 25.3, 8.0, 8.07, INK)
    for r in range(4):
        for c in range(3):
            pad(22.45 + c * 0.86, 23.2 + c * 0.86, 7.05 - r * 0.62, 7.55 - r * 0.62)
        pad(25.1, 26.4, 7.05 - r * 0.62, 7.55 - r * 0.62)
    pad(22.45, 24.35, 3.85, 4.4, edge=(196, 70, 70))                # cancel (red outline)
    pad(24.55, 26.4, 3.85, 4.4)
    for i in range(3):
        pad(22.45 + i * 1.33, 23.65 + i * 1.33, 2.95, 3.45)
    # parody wordmark centred in the top band over the door
    lg = load(os.path.join(_LOGOS, "zapwhistle.svg"))
    lw = int(3.0 * s)
    lg.scale(lw, int(lw * 100 / 420))
    add_layer_from(a.img, lg, "wordmark", int(px((dx0 + dx1) / 2) - lw / 2), int(pz(16.3)))
    lg.delete()
    a.lay = flatten(a.img)
    a.fill("white", WHITE, 0.0, 0.6)
    a.fill("under", (188, 188, 186), 0.0, 0.3)
    a.fill("vent", (48, 48, 50), 0.0, 0.2)
    vx, vy, vw, vh = a.rect("vent")
    for i in range(12):
        fill_rect(a.img, a.lay, (vx + 6 + i * 20, vy + 8, 10, vh - 16), (20, 20, 22))
    a.fill("lens", (245, 245, 238), 0.0, 0.8)
    fill_rect(a.img, a.lay, (896, 640, 128, 128), (128, 128, 128))
    fill_rect(a.img, a.lay, (0, 768, 1024, 256), (128, 128, 128))
    a.save()
