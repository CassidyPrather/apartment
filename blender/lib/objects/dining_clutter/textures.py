"""dining_clutter atlas (1024). Every region is painted procedurally as one SVG (written to
a temp file, rasterised by GIMP's SVG loader), with the parody logos from logos/*.svg nested
in. No photo pixels: the table-top items carry real brands, stickers of third-party
characters, and possibly mail, so everything is redrawn from scratch.

Parodies: Kumquat (sky-blue laptop mark), Limeyish (lime seltzer), Glacier Burp (red
seltzer), Pinchy (seasoning shaker), Sardeen Machine (fish tin). Sticker art on the water
bottle is generic shapes, no characters and no text. The brown jacket's back print (a
cartoon character) is left off: plain canvas until a clear photo shows what to redraw."""

import ast
import os
import random
import re
import tempfile

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "dining_clutter")


def _atlas():
    tree = ast.parse(open(os.path.join(_PKG, "object.py"), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ATLAS":
            return ast.literal_eval(node.value)
    raise RuntimeError("ATLAS not found in object.py")


ATLAS = _atlas()
R = ATLAS["regions"]

FLAT = {
    # region: (colour, metallic, smoothness, grain)
    "tan": ("#c9a66a", 0.0, 0.25, 0.05), "paper": ("#efefeb", 0.0, 0.2, 0.01),
    "blue_metal": ("#a3b6cf", 0.6, 0.55, 0.01), "black_plastic": ("#1d1d20", 0.0, 0.35, 0.02),
    "steel": ("#bfc2c6", 1.0, 0.6, 0.02), "ceramic": ("#f2f0eb", 0.0, 0.8, 0.0),
    "gray_plastic": ("#c4bec1", 0.0, 0.4, 0.01), "wire": ("#161616", 0.3, 0.4, 0.0),
    "napkin": ("#f1efe9", 0.0, 0.05, 0.03), "paper_towel": ("#f3f2ee", 0.0, 0.05, 0.04),
    "red_cap": ("#d52429", 0.0, 0.45, 0.01), "white_cap": ("#eeeeeb", 0.0, 0.45, 0.01),
    "lid_green": ("#9dac85", 0.0, 0.35, 0.01), "lid_lilac": ("#dab7d8", 0.0, 0.35, 0.01),
    "black_cap": ("#19191a", 0.0, 0.4, 0.01), "coral": ("#e06a50", 0.0, 0.4, 0.0),
    "cup_inside": ("#aba5a8", 0.0, 0.4, 0.0),
    "candy_0": ("#f2d02b", 0.0, 0.8, 0.0), "candy_1": ("#ec5fa0", 0.0, 0.8, 0.0),
    "candy_2": ("#d6dce6", 0.3, 0.85, 0.0), "candy_3": ("#d23a3a", 0.0, 0.8, 0.0),
    "candy_4": ("#a9c6e8", 0.2, 0.85, 0.0), "candy_5": ("#f39a2b", 0.0, 0.8, 0.0),
    "candy_6": ("#b8458f", 0.0, 0.8, 0.0), "candy_7": ("#c9d8ee", 0.2, 0.85, 0.0),
}
MATS = {
    # painted regions: (metallic, smoothness, grain)
    "laptop_lid": (0.6, 0.55, 0.0), "black_lid": (0.0, 0.35, 0.0),
    "glass_flakes": (0.0, 0.75, 0.0), "glass_pepper": (0.0, 0.75, 0.0),
    "lime_label": (0.3, 0.6, 0.0), "red_label": (0.3, 0.6, 0.0), "shaker_label": (0.0, 0.5, 0.0),
    "jar_label": (0.0, 0.45, 0.0), "blossom": (0.0, 0.45, 0.0), "bottle": (0.0, 0.45, 0.0),
    "tin_side": (0.5, 0.55, 0.0), "tin_top": (0.9, 0.55, 0.0), "can_top": (1.0, 0.6, 0.0),
    "plate": (0.0, 0.8, 0.0), "cookies": (0.0, 0.2, 0.04), "bowl_band": (0.0, 0.8, 0.0),
    "crumbs": (0.0, 0.7, 0.0), "grid_face": (0.1, 0.2, 0.0), "navy": (0.0, 0.35, 0.0),
    "brown": (0.0, 0.1, 0.0),   # no grain: the drape UVs stretch v ~5x, grain turns into streaks
}


def _logo(name, x, y, w, h, rotate=0):
    s = open(os.path.join(_PKG, "logos", name + ".svg"), encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    inner = s[s.index(">") + 1: s.rindex("</svg>")]
    body = f'<svg x="0" y="0" width="{w}" height="{h}" viewBox="{vb}">{inner}</svg>'
    return f'<g transform="translate({x},{y}) rotate({rotate})">{body}</g>'


def _clip(region, body):
    x, y, w, h = R[region]
    return (f'<clipPath id="c_{region}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#c_{region})">{body}</g>')


def _rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def _blossom(cx, cy, r, fill):
    petals = "".join(f'<circle cx="{cx + r * 0.9 * __import__("math").cos(a * 1.2566):.1f}" '
                     f'cy="{cy + r * 0.9 * __import__("math").sin(a * 1.2566):.1f}" r="{r * 0.6:.1f}" fill="{fill}"/>'
                     for a in range(5))
    return petals + f'<circle cx="{cx}" cy="{cy}" r="{r * 0.35:.1f}" fill="#ffffff"/>'


def svg():
    import math
    rnd = random.Random(1492)
    o = []
    for reg, (c, *_ ) in FLAT.items():
        o.append(_rect(*R[reg], c))

    # sky-blue laptop lid: soft sheen + parody mark in the middle (lid is 12 x 8.5 in)
    x, y, w, h = R["laptop_lid"]
    o.append('<linearGradient id="gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#b3c5dc"/>'
             '<stop offset="1" stop-color="#9aaecb"/></linearGradient>')
    o.append(_rect(x, y, w, h, "url(#gl)"))
    o.append(_logo("kumquat", x + w / 2 - 12, y + h / 2 - 12, 24, 24))

    # black laptop lid (10 x 15 in, north up): blank white sticker near the NW corner,
    # small grey corner badge at the SE corner, no text
    x, y, w, h = R["black_lid"]
    o.append(_rect(x, y, w, h, "#1b1b1e"))
    o.append(_rect(x + 15, y + 6, 19, 38, "#eeeeea"))
    for k in range(6):
        o.append(_rect(x + 18, y + 11 + k * 5, 13 - (k % 3) * 2, 1.4, "#b8b8b4"))
    o.append(_rect(x + 110, y + 168, 9, 9, "#4a4a4e"))

    # glass spice jars: speckled contents seen through glass
    for reg, base, specks in (("glass_flakes", "#6b3322", ("#b5532e", "#d98b52", "#3a1a10")),
                              ("glass_pepper", "#3c3834", ("#1e1c1a", "#6d655c", "#8b8173"))):
        x, y, w, h = R[reg]
        o.append(_rect(x, y, w, h, base))
        for _ in range(140):
            o.append(f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(8, h):.1f}" '
                     f'r="{rnd.uniform(0.6, 1.6):.1f}" fill="{rnd.choice(specks)}"/>')
        o.append(_rect(x, y, w, 8, "#d8dcdc", 'opacity="0.6"'))

    # lime seltzer label (wraps once round the can): speckled white, green panel, lime art
    x, y, w, h = R["lime_label"]
    b = [_rect(x, y, w, h, "#e8ecea")]
    for _ in range(160):
        b.append(f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(0, h):.1f}" r="1.1" '
                 f'fill="{rnd.choice(["#9cc3e0", "#c4d9e8", "#b7cbd8"])}"/>')
    b.append(_rect(x + 96, y + 10, 64, 70, "#1f7a4f", 'rx="4"'))
    b.append(_logo("limeyish", x + 99, y + 30, 58, 23))
    b.append(_rect(x + 104, y + 62, 48, 3, "#e8f0e8"))
    for k in range(3):
        cx, cy = x + 108 + k * 20, y + 104
        b.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="#b9d46c" stroke="#7fa83f" stroke-width="2"/>')
        b.append(f'<path d="M{cx} {cy} l0 -10 M{cx} {cy} l9 5 M{cx} {cy} l-9 5" stroke="#e9f3c4" stroke-width="1.5"/>')
    b.append(_rect(x + 196, y + 18, 44, 70, "#f2f4f3"))           # blank facts panel
    for k in range(9):
        b.append(_rect(x + 200, y + 23 + k * 7, 34 - (k % 4) * 5, 1.5, "#a0a6a4"))
    o.append(_clip("lime_label", "".join(b)))

    # red seltzer label: red, a white wordmark running round, bubbles and a fruit patch
    x, y, w, h = R["red_label"]
    b = [_rect(x, y, w, h, "#c72a2e")]
    b.append(_logo("glacier_burp", x + 30, y + 44, 190, 51))
    for _ in range(40):
        b.append(f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(0, 36):.1f}" '
                 f'r="{rnd.uniform(1.5, 4):.1f}" fill="none" stroke="#ffffff" stroke-width="1.2"/>')
    b.append(f'<ellipse cx="{x + 60}" cy="{y + 112}" rx="26" ry="12" fill="#3f9a4a"/>')
    b.append(f'<ellipse cx="{x + 60}" cy="{y + 112}" rx="20" ry="8" fill="#f06a6a"/>')
    o.append(_clip("red_label", "".join(b)))

    # seasoning shaker label: yellow with the parody badge and a scatter of spice dots
    x, y, w, h = R["shaker_label"]
    b = [_rect(x, y, w, h, "#f2d24c")]
    b.append(_logo("pinchy", x + 70, y + 14, 116, 58))
    for _ in range(50):
        b.append(f'<circle cx="{x + 70 + rnd.uniform(0, 116):.1f}" cy="{y + rnd.uniform(80, 120):.1f}" '
                 f'r="{rnd.uniform(1, 2.5):.1f}" fill="{rnd.choice(["#c0392b", "#e67e22", "#7d5a2a"])}"/>')
    b.append(_rect(x + 2, y + 10, 50, 108, "#f7e7a0"))             # blank back panel
    for k in range(12):
        b.append(_rect(x + 6, y + 16 + k * 8, 40 - (k % 3) * 6, 1.5, "#9a8a50"))
    o.append(_clip("shaker_label", "".join(b)))

    # black-label seasoning jar: dark contents band at the top, blank black label
    x, y, w, h = R["jar_label"]
    b = [_rect(x, y, w, h, "#232427"), _rect(x, y, w, 14, "#3b3026")]
    b.append(_rect(x + 90, y + 34, 76, 1.5, "#d8d8d8"))
    for k in range(5):
        b.append(_rect(x + 96, y + 44 + k * 9, 60 - k * 6, 3, "#5a5d62"))
    o.append(_clip("jar_label", "".join(b)))

    # blossom print cylinder: white, pink blossoms above, light-blue ones low down
    x, y, w, h = R["blossom"]
    b = [_rect(x, y, w, h, "#f6f4f3")]
    for k in range(26):
        cx, cy = x + rnd.uniform(0, w), y + rnd.uniform(6, h - 6)
        col = "#8fc6e8" if cy > y + h * 0.7 else "#f1a9c3"
        b.append(_blossom(cx, cy, rnd.uniform(5, 8), col))
    o.append(_clip("blossom", "".join(b)))

    # water bottle body: matte black with generic die-cut sticker shapes (no characters,
    # no text); the speech-bubble sticker is left blank
    x, y, w, h = R["bottle"]
    b = [_rect(x, y, w, h, "#141416")]
    cols = ["#8b6dca", "#efe5d8", "#f3b5c8", "#f0e2a2", "#b9a3e6", "#ffffff"]
    for k in range(9):
        cx, cy = x + 30 + k * 40 + rnd.uniform(-8, 8), y + rnd.uniform(40, 160)
        rx, ry = rnd.uniform(16, 26), rnd.uniform(18, 30)
        c = cols[k % len(cols)]
        b.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx + 3:.0f}" ry="{ry + 3:.0f}" fill="#ffffff"/>')
        b.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{c}"/>')
        b.append(f'<circle cx="{cx - rx * 0.3:.0f}" cy="{cy - ry * 0.4:.0f}" r="{rx * 0.35:.0f}" fill="#ffffff" opacity="0.5"/>')
    b.append(_rect(x + 300, y + 20, 50, 22, "#ffffff", 'rx="6" stroke="#000" stroke-width="3"'))
    o.append(_clip("bottle", "".join(b)))

    # fish tin: yellow band with a red foot stripe and the parody mark; gold lid, red tab
    x, y, w, h = R["tin_side"]
    b = [_rect(x, y, w, h, "#f0c22e"), _rect(x, y + 44, w, 20, "#cc2a26"), _rect(x, y, w, 5, "#d8c07a")]
    b.append(_logo("sardeen_machine", x + 20, y + 12, 120, 30))
    b.append(_logo("sardeen_machine", x + 140, y + 12, 110, 28))
    o.append(_clip("tin_side", "".join(b)))
    x, y, w, h = R["tin_top"]
    b = [_rect(x, y, w, h, "#cbb27a"),
         f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2 - 10}" ry="{h / 2 - 8}" fill="none" stroke="#e6d6a6" stroke-width="3"/>',
         f'<ellipse cx="{x + w / 2}" cy="{y + h / 2}" rx="{w / 2 - 22}" ry="{h / 2 - 18}" fill="none" stroke="#a88f58" stroke-width="2"/>',
         _rect(x + w / 2 - 50, y + h / 2 - 10, 100, 20, "#d8322d", 'rx="4"'),
         f'<ellipse cx="{x + w - 40}" cy="{y + h / 2}" rx="12" ry="9" fill="none" stroke="#9c8650" stroke-width="3"/>']
    o.append(_clip("tin_top", "".join(b)))

    # can top: silver lid, a rim ring and the tab
    x, y, w, h = R["can_top"]
    cx, cy = x + w / 2, y + h / 2
    o.append(_rect(x, y, w, h, "#c6c9cc"))
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{w / 2 - 6}" fill="#b6b9bd" stroke="#8d9094" stroke-width="3"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy - 12}" rx="14" ry="20" fill="#d4d6d9" stroke="#8d9094" stroke-width="2"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy + 26}" rx="12" ry="8" fill="#55585c"/>')

    # plate (planar, radius 5.25 in = 128 px): white well, blue ring, navy patterned rim
    x, y, w, h = R["plate"]
    cx, cy = x + w / 2, y + h / 2
    b = [_rect(x, y, w, h, "#f3f1ec"),
         f'<circle cx="{cx}" cy="{cy}" r="126" fill="#223f7e"/>',
         f'<circle cx="{cx}" cy="{cy}" r="112" fill="#f3f1ec"/>',
         f'<circle cx="{cx}" cy="{cy}" r="104" fill="#2d57a0"/>',
         f'<circle cx="{cx}" cy="{cy}" r="92" fill="#f3f1ec"/>',
         f'<circle cx="{cx}" cy="{cy}" r="84" fill="none" stroke="#223f7e" stroke-width="3"/>']
    for k in range(24):
        a = 2 * math.pi * k / 24
        b.append(f'<circle cx="{cx + 108 * math.cos(a):.1f}" cy="{cy + 108 * math.sin(a):.1f}" r="4" fill="#223f7e"/>')
        b.append(f'<circle cx="{cx + 119 * math.cos(a + 0.13):.1f}" cy="{cy + 119 * math.sin(a + 0.13):.1f}" r="3" fill="#f3f1ec"/>')
    o.append(_clip("plate", "".join(b)))

    # bowl of frosted animal crackers (planar, radius 3.0 in = 96 px)
    x, y, w, h = R["cookies"]
    cx, cy = x + w / 2, y + h / 2
    b = [_rect(x, y, w, h, "#f2f0eb"), f'<circle cx="{cx}" cy="{cy}" r="74" fill="#e2b98e"/>']
    for _ in range(110):
        a, r = rnd.uniform(0, 2 * math.pi), 68 * math.sqrt(rnd.uniform(0, 1))
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        c = rnd.choice(["#f59ab8", "#fbf6ee", "#ee7fa4", "#fbe0e8", "#f2e6cf"])
        b.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rnd.uniform(7, 12):.1f}" ry="{rnd.uniform(4, 7):.1f}" '
                 f'transform="rotate({rnd.uniform(0, 180):.0f} {px:.1f} {py:.1f})" fill="{c}" stroke="#c9ab86" stroke-width="0.8"/>')
    o.append(_clip("cookies", "".join(b)))

    # bowl outside: white with a navy band under the rim (top of the region = rim)
    x, y, w, h = R["bowl_band"]
    o.append(_rect(x, y, w, h, "#f2f0eb"))
    o.append(_rect(x, y + 4, w, 9, "#223f7e"))
    o.append(_rect(x, y + 16, w, 2, "#2d57a0"))

    # north bowl inside: white with orange cereal crumbs and a small clump
    x, y, w, h = R["crumbs"]
    cx, cy = x + w / 2, y + h / 2
    b = [_rect(x, y, w, h, "#f2f0eb"), f'<ellipse cx="{cx - 18}" cy="{cy + 8}" rx="20" ry="16" fill="#dd9a45"/>']
    for _ in range(60):
        a, r = rnd.uniform(0, 2 * math.pi), 55 * math.sqrt(rnd.uniform(0, 1))
        b.append(f'<ellipse cx="{cx + r * math.cos(a):.1f}" cy="{cy + r * math.sin(a):.1f}" rx="{rnd.uniform(1.5, 3.5):.1f}" '
                 f'ry="1.3" fill="{rnd.choice(["#d98f3c", "#e5ad60", "#c8782c"])}"/>')
    o.append(_clip("crumbs", "".join(b)))

    # napkin holder face: napkins behind a black wire grid, 5 columns x 6 rows
    x, y, w, h = R["grid_face"]
    b = [_rect(x, y, w, h, "#efede7")]
    for k in range(6):
        b.append(_rect(x + 4 + k * 24, y, 5, h, "#141414"))
    for k in range(7):
        b.append(_rect(x, y + 4 + k * 20.3, w, 5, "#141414"))
    o.append(_clip("grid_face", "".join(b)))

    # quilted puffer: horizontal baffles (along u) with a dark stitch line and highlight
    x, y, w, h = R["navy"]
    b = [_rect(x, y, w, h, "#213f73")]
    for k in range(0, h, 12):
        b.append(_rect(x, y + k, w, 2, "#122544"))
        b.append(_rect(x, y + k + 4, w, 3, "#2f5290", 'opacity="0.7"'))
    b.append(_rect(x + 116, y + 150, 22, 30, "#e9e9e6"))          # blank inner tag
    o.append(_clip("navy", "".join(b)))

    # rust canvas jacket (back print left off, see the docstring)
    x, y, w, h = R["brown"]
    b = [_rect(x, y, w, h, "#9b5a2b")]
    for _ in range(900):
        b.append(_rect(x + rnd.uniform(0, w), y + rnd.uniform(0, h), 9, 1.5,
                       rnd.choice(["#8e5227", "#a6663a", "#94572b"])))
    b.append(_rect(x + w / 2 - 3, y, 6, h * 0.62, "#7c4520"))      # back seam
    o.append(_clip("brown", "".join(b)))

    n = ATLAS["size"]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n}" height="{n}" viewBox="0 0 {n} {n}">'
            + _rect(0, 0, n, n, "#808080") + "".join(o) + "</svg>")


def build():
    a = Atlas(ATLAS)
    path = os.path.join(tempfile.gettempdir(), "dining_clutter_atlas.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg())
    art = load(path)
    add_layer_from(a.img, art, "art", 0, 0)
    art.delete()
    a.lay = flatten(a.img)
    for reg, (c, met, sm, gr) in FLAT.items():
        if gr:
            grain(a.img, a.lay, R[reg], gr, 1.0)
        a.material(reg, met, sm)
    for reg, (met, sm, gr) in MATS.items():
        if gr:
            grain(a.img, a.lay, R[reg], gr, 1.0)
        a.material(reg, met, sm)
    a.save()
