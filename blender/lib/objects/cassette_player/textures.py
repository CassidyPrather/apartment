"""cassette_player atlases (headless GIMP, gimp_textures.py helpers in scope).

cassette_player (1024, committed; drawn from scratch as one SVG, logos/cassette_player_face.svg,
  composited in GIMP with a little grain): the recorder's knurled face laid out as in IMG_1513
  (window strip with the two reels and the tape counter window, the silver stripe, the key-side
  band), the parody "Humdinger" badge and "Mini Mumbler" lettering in orange replacing the real
  monogram and model text, the speaker grille underneath, the front edge with a small badge,
  and flat colour cells.
cassette_player_art (512, git-ignored): Cassidy's own J-card, rectified from the photos: the
  "Crow / Bunny" photo card from IMG_1513 (square-on) and the handwritten "Caramel Sea Salt
  Mix" spine from IMG_1509.
"""

import ast
import os

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "cassette_player")
SVG_PATH = os.path.join(_PKG, "logos", "cassette_player_face.svg")


def _const(name):
    tree = ast.parse(open(os.path.join(_PKG, "object.py"), encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise RuntimeError(name)


ATLAS = _const("ATLAS")
ART_ATLAS = _const("ART_ATLAS")
ORANGE = "#f0a020"


def badge(cx, cy, r, col=ORANGE):
    """Humdinger badge: a ring holding a curly H whose uprights are two tape reels."""
    s = r
    return (f'<circle cx="{cx}" cy="{cy}" r="{s}" fill="none" stroke="{col}" stroke-width="{s * 0.14}"/>'
            f'<circle cx="{cx - s * 0.38}" cy="{cy}" r="{s * 0.26}" fill="none" stroke="{col}" stroke-width="{s * 0.12}"/>'
            f'<circle cx="{cx + s * 0.38}" cy="{cy}" r="{s * 0.26}" fill="none" stroke="{col}" stroke-width="{s * 0.12}"/>'
            f'<path d="M{cx - s * 0.12} {cy} Q{cx} {cy - s * 0.25} {cx + s * 0.12} {cy}" fill="none" stroke="{col}" stroke-width="{s * 0.12}"/>'
            f'<circle cx="{cx - s * 0.38}" cy="{cy}" r="{s * 0.06}" fill="{col}"/>'
            f'<circle cx="{cx + s * 0.38}" cy="{cy}" r="{s * 0.06}" fill="{col}"/>')


def face(W, H):
    """Face seen from above: +X (badge end) right, +Y (key side) up."""
    o = [f'<defs><pattern id="knurl" width="8" height="8" patternUnits="userSpaceOnUse">'
         f'<rect width="8" height="8" fill="#1b1b1d"/>'
         f'<path d="M0 0 L8 0 L4 4 Z" fill="#3a3a3e"/><path d="M0 0 L4 4 L0 8 Z" fill="#2c2c30"/>'
         f'<path d="M8 0 L8 8 L4 4 Z" fill="#101012"/><path d="M0 8 L4 4 L8 8 Z" fill="#0a0a0c"/>'
         f'</pattern>'
         f'<linearGradient id="win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26262a"/>'
         f'<stop offset="1" stop-color="#0c0c0e"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="#161618"/>',
         f'<rect x="{W * 0.03}" y="{H * 0.2}" width="{W * 0.93}" height="{H * 0.75}" fill="url(#knurl)"/>',
         f'<rect x="0" y="0" width="{W}" height="{H * 0.18}" fill="#1c1c1e"/>',
         f'<rect x="0" y="{H * 0.175}" width="{W}" height="3" fill="#050506"/>']
    # silver stripe
    o.append(f'<rect x="{W * 0.07}" y="{H * 0.27}" width="{W * 0.86}" height="{H * 0.025}" fill="#d8d4c4"/>')
    o.append(f'<rect x="{W * 0.45}" y="{H * 0.27}" width="{W * 0.18}" height="{H * 0.025}" fill="#e8b8d0" opacity="0.5"/>')
    # window strip
    x0, x1, y0, y1 = W * 0.1, W * 0.95, H * 0.47, H * 0.8
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#win)" stroke="#2a2a2e" stroke-width="3"/>')
    cy = H * 0.61
    for cx, flip in ((W * 0.38, -1), (W * 0.64, 1)):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{H * 0.07}" fill="#101012" stroke="#e8e8e8" stroke-width="5"/>')
        o.append(f'<path d="M{cx} {cy - H * 0.07} q{flip * H * 0.09} {-H * 0.02} {flip * H * 0.12} {-H * 0.1}" fill="none" '
                 f'stroke="#e8e8e8" stroke-width="5"/>')
    o.append(f'<rect x="{W * 0.44}" y="{H * 0.55}" width="{W * 0.14}" height="{H * 0.12}" fill="#050506" stroke="#3a3a3e" stroke-width="2"/>')
    for i in range(9):
        L_ = H * (0.05 if i % 4 == 0 else 0.03)
        o.append(f'<rect x="{W * (0.455 + i * 0.013)}" y="{H * 0.66 - L_}" width="2" height="{L_}" fill="#dcdcdc"/>')
    lab = 'font-family="Arial" font-size="{s}" fill="#e0e0e0" font-weight="bold"'
    o.append(f'<text x="{W * 0.9}" y="{H * 0.76}" {lab.format(s=H * 0.035)} text-anchor="end">&#9664;&#9664; REWIND</text>')
    o.append(f'<text x="{W * 0.51}" y="{H * 0.76}" {lab.format(s=H * 0.03)} text-anchor="middle">&#9664; PLAY/RECORD</text>')
    o.append(f'<text x="{W * 0.3}" y="{H * 0.76}" {lab.format(s=H * 0.035)} text-anchor="end">FAST FWD &#9654;&#9654;</text>')
    for i, t in enumerate(("• Rewind-ish", "• Review", "• Preview", "• Auto Snooze")):
        o.append(f'<text x="{W * 0.115}" y="{H * (0.53 + i * 0.06)}" font-family="Arial" font-style="italic" '
                 f'font-size="{H * 0.04}" fill="#e8e8e8" font-weight="bold">{t}</text>')
    # parody badge and lettering at the badge end (reads along the short side)
    o.append(badge(W * 0.965, H * 0.37, H * 0.04))
    o.append(f'<g transform="translate({W * 0.955} {H * 0.46}) rotate(90)">'
             f'<text x="0" y="0" font-family="Arial Black" font-style="italic" font-size="{H * 0.055}" '
             f'fill="{ORANGE}">Mini Mumbler</text></g>')
    # key-side band: a groove and the door seam
    o.append(f'<rect x="{W * 0.18}" y="{H * 0.02}" width="2" height="{H * 0.14}" fill="#050506"/>')
    return "".join(o)


def back(W, H):
    o = [f'<rect width="{W}" height="{H}" fill="#18181a"/>',
         f'<rect x="{W * 0.05}" y="{H * 0.04}" width="{W * 0.9}" height="{H * 0.18}" fill="#222226"/>']
    cx, cy, r = W * 0.7, H * 0.55, H * 0.28
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#101012"/>')
    for i in range(-7, 8):
        for j in range(-7, 8):
            x, y = cx + i * r / 7.5, cy + j * r / 7.5
            if (x - cx) ** 2 + (y - cy) ** 2 < (r * 0.92) ** 2:
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#000"/>')
    for sx, sy in ((0.35, 0.3), (0.92, 0.3), (0.35, 0.9), (0.92, 0.9)):
        o.append(f'<circle cx="{W * sx}" cy="{H * sy}" r="4" fill="#060606"/>')
    o.append(f'<text x="{W * 0.88}" y="{H * 0.97}" font-family="Arial" font-weight="bold" font-size="{H * 0.05}" '
             f'fill="#e0e0e0" text-anchor="end">PAUSE &#9654;</text>')
    o.append(badge(W * 0.2, H * 0.6, H * 0.08, "#8a8a8a"))
    return "".join(o)


def side_front(W, H):
    o = [f'<rect width="{W}" height="{H}" fill="#161618"/>',
         f'<rect x="0" y="{H * 0.44}" width="{W}" height="2" fill="#050506"/>',
         f'<text x="{W * 0.3}" y="{H * 0.35}" font-family="Arial" font-weight="bold" font-size="{H * 0.12}" fill="#d0d0d0">PLAY</text>',
         badge(W * 0.8, H * 0.7, H * 0.13, "#9a9a9a"),
         f'<text x="{W * 0.86}" y="{H * 0.66}" font-family="Arial" font-size="{H * 0.08}" fill="#9a9a9a">HUMDINGER</text>',
         f'<circle cx="{W * 0.12}" cy="{H * 0.7}" r="{H * 0.07}" fill="#050505"/>']
    return "".join(o)


CELLS = {"black": "#141416", "orange": "#e8a020", "chrome": "#d0d2d6", "strap": "#18181a",
         "clear": "#e6eef0", "shell": "#9a4a20", "grey": "#5a5a5e", "cream": "#ece4cc"}


def make_svg():
    n = ATLAS["size"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{n}" height="{n}" viewBox="0 0 {n} {n}">',
             "<!-- cassette_player atlas art, drawn from scratch; regenerated by textures.py -->"]
    for name, (x, y, w, h) in ATLAS["regions"].items():
        fn = {"face": face, "back": back, "side_front": side_front}.get(name)
        body = fn(w, h) if fn else f'<rect width="{w}" height="{h}" fill="{CELLS[name]}"/>'
        parts.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden">{body}</svg>')
    parts.append("</svg>")
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return SVG_PATH


def label_art():
    """Cassidy's J-card: front from IMG_1513 (turned so the spine is at the bottom, as in
    IMG_1509) and the handwritten spine from IMG_1509."""
    b = Atlas(ART_ATLAS)
    for region, photo, quad in (
            # output TL, TR, BR, BL (full-res photo px)
            ("label_front", "IMG_1513.jpg", [(1005, 2335), (865, 1690), (1245, 1605), (1405, 2240)]),
            ("label_spine", "IMG_1509.jpg", [(622, 1593), (1276, 1193), (1282, 1239), (632, 1636)])):
        x, y, w, h = b.rect(region)
        img = rectify(os.path.join(REF, photo), quad, w, h)
        lay = img.get_layers()[0]
        gegl(lay, "gegl:stretch-contrast", keep_colors=True, perceptual=True)
        add_layer_from(b.img, img, region, x, y)
        img.delete()
        b.material(region, 0.0, 0.3)
    flatten(b.img)
    b.lay = b.img.get_layers()[0]
    b.save()


def build():
    a = Atlas(ATLAS)
    svg = load(make_svg())
    if svg.get_width() != a.size:
        svg.scale(a.size, a.size)
    add_layer_from(a.img, svg, "art", 0, 0)
    svg.delete()
    a.lay = flatten(a.img)
    for r in ("face", "back", "side_front"):
        grain(a.img, a.lay, a.rect(r), 0.03, 0.5)
    for r in ATLAS["regions"]:
        met, sm = {"chrome": (1.0, 0.7), "clear": (0.0, 0.92), "face": (0.0, 0.45), "orange": (0.0, 0.5),
                   "strap": (0.0, 0.15), "shell": (0.0, 0.55)}.get(r, (0.0, 0.4))
        a.material(r, met, sm)
    a.save()
    label_art()
