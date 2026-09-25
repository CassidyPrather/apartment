"""media_hutch atlas (headless GIMP, gimp_textures.py helpers in scope).

Cherry wood: flat fill sampled from the survey crops (dark red-brown under warm light),
with stretched noise for grain. Games: eight plain box colours with a lighter band
(no titles, no art), one per box on the open shelves; loose boxes on top are muted
plain colours. Brass knobs; plain ceramic, dark and tin small objects.
"""

import ast
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "media_hutch", "object.py")


def _atlas():
    tree = ast.parse(open(_OBJ, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
CHERRY = (82, 28, 12)          # crops: 85-100, 42-52, 26-32 on the lit side panel
CHERRY_DARK = (58, 20, 9)
GAME_COLOURS = [(150, 40, 36), (38, 60, 110), (36, 90, 60), (200, 170, 70), (60, 44, 80),
                (180, 90, 40), (230, 225, 210), (30, 30, 34), (110, 140, 170), (140, 60, 90),
                (90, 110, 50), (200, 60, 50), (70, 70, 90), (160, 130, 90)]


def wood(a, region, rgb, noise=0.18):
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), rgb)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:noise-rgb", correlated=False, independent=False, red=noise, green=noise,
         blue=noise, gaussian=True, seed=random.randint(0, 99999))
    gegl(a.lay, "gegl:motion-blur-linear", length=60.0, angle=90.0)
    Gimp.Selection.none(a.img)


def games(a):
    """Plain game-box colours: a flat fill with a lighter band (no titles, no art)."""
    for i in range(8):
        col = GAME_COLOURS[(i * 5) % len(GAME_COLOURS)]
        x, y, w, h = a.rect(f"game_{i}")
        fill_rect(a.img, a.lay, (x, y, w, h), col)
        lc = tuple(min(255, v + 45) for v in col)
        fill_rect(a.img, a.lay, (x, y + h // 3, w, h // 6), lc)
        grain(a.img, a.lay, (x, y, w, h), 0.04, 0.8)
        a.material(f"game_{i}", 0.0, 0.35)


def build():
    random.seed(1492)
    a = Atlas(ATLAS)
    wood(a, "wood", CHERRY)
    a.material("wood", 0.0, 0.45)
    wood(a, "wood_end", CHERRY_DARK)
    a.material("wood_end", 0.0, 0.4)
    wood(a, "panel", (88, 31, 14))
    a.material("panel", 0.0, 0.45)
    a.fill("interior", (48, 26, 17), 0.0, 0.25, noise=0.06, blur=1.0)
    a.fill("ceramic", (226, 222, 212), 0.0, 0.7)
    a.fill("dark_obj", (40, 40, 44), 0.0, 0.4)
    a.fill("tin", (150, 152, 156), 0.8, 0.5, noise=0.04, blur=0.6)
    a.fill("brass", (176, 140, 72), 1.0, 0.6, noise=0.04, blur=0.5)
    x, y, w, h = a.rect("games_top")
    fill_rect(a.img, a.lay, (x, y, w, h), (60, 58, 64))
    for i, col in enumerate([(40, 44, 60), (120, 40, 38), (70, 90, 60), (150, 120, 80)]):
        fill_rect(a.img, a.lay, (x + (i % 2) * w // 2, y + (i // 2) * h // 2, w // 2, h // 2), col)
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.8)
    a.material("games_top", 0.0, 0.35)
    games(a)
    a.save()
