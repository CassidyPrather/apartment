"""media_hutch atlases (headless GIMP, gimp_textures.py helpers in scope).

media_hutch (2048, committed; everything drawn from scratch):
  - wood: the dark stained knotty pine, painted procedurally in GIMP (base colour sampled
    from IMG_1506: valance median 99/65/47, grain 80/53/40 .. 125/84/59), stretched noise for
    grain, darker streaks, knots, and the dark flecks of the distressed finish.
  - every parody game box face, book spine and prop surface: vector art written here as one
    SVG (logos/media_hutch_boxart.svg, regenerated each build), loaded into GIMP as a layer
    over the wood, then given print grain in GIMP. Each box keeps the real one's colour
    scheme and layout feel, with a new silly title and new art; no real titles, logos,
    publisher names or cover art.
  - the resistor colour-code chart, redrawn as a generic chart (no company or copyright line).
media_hutch_art (512, git-ignored): Cassidy's red linocut print, rectified from IMG_1508, with
  the QR code replaced by a random non-scannable block pattern cut in the same style. The
  pencil edition number and signature stay as they are (Cassidy: don't blur artists' signatures).
"""

import importlib.util
import math
import os
import random

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "media_hutch")
_spec = importlib.util.spec_from_file_location("media_hutch_layout", os.path.join(_PKG, "layout.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)
ATLAS = L.ATLAS
ART_ATLAS = L.ART_ATLAS
SVG_PATH = os.path.join(_PKG, "logos", "media_hutch_boxart.svg")

WOOD = (74, 34, 17)
WOOD_DARK = (52, 24, 13)
WOOD_EDGE = (124, 70, 34)
STAIN = {"wood": (16.0, 70.0, -38.0), "wood_dark": (14.0, 70.0, -52.0), "wood_edge": (22.0, 62.0, -10.0)}


# ============================================================================================
# SVG vocabulary
# ============================================================================================

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rgb(c):
    return c if isinstance(c, str) else "#%02x%02x%02x" % tuple(c[:3])


def R(x, y, w, h, fill, rx=0, stroke=None, sw=0, op=1.0, extra=""):
    s = f' stroke="{rgb(stroke)}" stroke-width="{sw}"' if stroke else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{rgb(fill)}" opacity="{op}"{s} {extra}/>')


def C(cx, cy, r, fill, stroke=None, sw=0, op=1.0):
    s = f' stroke="{rgb(stroke)}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{rgb(fill)}" opacity="{op}"{s}/>'


def E(cx, cy, rx, ry, fill, stroke=None, sw=0, op=1.0, rot=0):
    s = f' stroke="{rgb(stroke)}" stroke-width="{sw}"' if stroke else ""
    t = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot else ""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{rgb(fill)}" '
            f'opacity="{op}"{s}{t}/>')


def P(d, fill, stroke=None, sw=0, op=1.0, extra=""):
    s = f' stroke="{rgb(stroke)}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if stroke else ""
    return f'<path d="{d}" fill="{rgb(fill) if fill != "none" else "none"}" opacity="{op}"{s} {extra}/>'


def poly(pts, fill, stroke=None, sw=0, op=1.0):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return P(d, fill, stroke, sw, op)


_EXT = {}


def measure(text, size, font, weight="normal", italic=False):
    """Rendered width in px, asked of GIMP's own font machinery (librsvg ignores textLength)."""
    fam = font.split(",")[0].strip().strip("'")
    style = ("Bold " if weight == "bold" else "") + ("Italic" if italic else "")
    style = style.strip() or "Regular"
    key = (text, fam, style)
    if key not in _EXT:
        w = None
        try:
            for name in (f"{fam} {style}", f"{fam} Regular", fam, f"{fam} Bold"):
                f = Gimp.Font.get_by_name(name)
                if f:
                    ok, w, _h, _a, _d = Gimp.text_get_extents_font(text, 100.0, f)
                    if ok:
                        break
                    w = None
        except Exception:
            w = None
        _EXT[key] = (w / 100.0) if w else 0.58 * len(text)
    return _EXT[key] * size


def T(x, y, text, size, fill, font="Arial", weight="normal", anchor="middle", stroke=None, sw=0,
      italic=False, ls=0, rot=0, op=1.0, width=None, stretch=1.08):
    """Text; `width` = the most horizontal room it may take: the run is squeezed to fit (and
    stretched a little, up to `stretch`, when it is short)."""
    st = f' stroke="{rgb(stroke)}" stroke-width="{sw}" paint-order="stroke"' if stroke else ""
    sty = ' font-style="italic"' if italic else ""
    tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ""
    core = (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size:.1f}" '
            f'font-weight="{weight}" text-anchor="{anchor}" fill="{rgb(fill)}" '
            f'letter-spacing="{ls}" opacity="{op}"{sty}{st}{tr}>{esc(text)}</text>')
    if width:
        est = measure(text, size, font, weight, italic) + ls * len(text)
        k = min(stretch, width / max(est, 1))
        return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f} 1) translate({-x:.1f} {-y:.1f})">{core}</g>'
    return core


def grad(gid, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{rgb(c)}"/>' for o, c in stops)
    return (f'<defs><linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}'
            f'</linearGradient></defs>')


def rgrad(gid, stops, cx=0.5, cy=0.5, r=0.5):
    s = "".join(f'<stop offset="{o}" stop-color="{rgb(c)}" stop-opacity="{a}"/>' for o, c, a in stops)
    return f'<defs><radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient></defs>'


_gid = [0]


def gid(prefix):
    _gid[0] += 1
    return f"{prefix}{_gid[0]}"


def stars(W, H, n, rng, col="#ffffff"):
    return "".join(C(rng.uniform(0, W), rng.uniform(0, H), rng.choice((0.5, 0.7, 1.0, 1.4)), col,
                     op=rng.uniform(0.4, 1.0)) for _ in range(n))


def stones(W, H, rng, base=(120, 116, 104)):
    out = [R(0, 0, W, H, base)]
    y = 0
    while y < H:
        sh = rng.uniform(H * 0.14, H * 0.24)
        x = rng.uniform(-20, 0)
        while x < W:
            sw_ = rng.uniform(H * 0.25, H * 0.5)
            v = rng.randint(-26, 22)
            c = tuple(max(0, min(255, b + v)) for b in base)
            out.append(R(x + 1.5, y + 1.5, sw_ - 3, sh - 3, c, rx=4, stroke=(70, 66, 58), sw=1.2))
            x += sw_
        y += sh
    return "".join(out)


def bricks(W, H, rng, base, mortar, bh=None):
    bh = bh or H / 6
    out = [R(0, 0, W, H, mortar)]
    row = 0
    y = 0
    while y < H:
        x = -(bh * 1.2 if row % 2 else 0)
        while x < W:
            v = rng.randint(-14, 14)
            c = tuple(max(0, min(255, b + v)) for b in base)
            out.append(R(x + 1, y + 1, bh * 2.4 - 2, bh - 2, c))
            x += bh * 2.4
        y += bh
        row += 1
    return "".join(out)


def seigaiha(W, H, r, fg, bg):
    out = [R(0, 0, W, H, bg)]
    row = 0
    y = H + r
    while y > -r:
        off = r if row % 2 else 0
        x = -off
        while x < W + r * 2:
            for k, rr in enumerate((r, r * 0.72, r * 0.44)):
                out.append(C(x, y, rr, bg if k % 2 else fg))
            out.append(C(x, y, r * 0.2, fg))
            x += r * 2
        y -= r * 0.5
        row += 1
    return "".join(out)


def chibi(x, y, s, hair, coat, skin=(244, 214, 192), eyes=(40, 30, 40), hoop=None, hat=None):
    """Tiny cartoon figure, head centre (x, y), head radius s."""
    out = [P(f"M{x - s * 0.9:.1f} {y + s * 3.2:.1f} L{x - s * 0.75:.1f} {y + s * 0.9:.1f} "
             f"Q{x:.1f} {y + s * 0.6:.1f} {x + s * 0.75:.1f} {y + s * 0.9:.1f} L{x + s * 0.9:.1f} {y + s * 3.2:.1f} Z",
             coat)]
    out.append(C(x, y, s, skin))
    out.append(P(f"M{x - s * 1.08:.1f} {y + s * 0.5:.1f} Q{x - s * 1.2:.1f} {y - s * 1.3:.1f} {x:.1f} {y - s * 1.15:.1f} "
                 f"Q{x + s * 1.2:.1f} {y - s * 1.3:.1f} {x + s * 1.08:.1f} {y + s * 0.5:.1f} "
                 f"Q{x + s * 0.7:.1f} {y - s * 0.5:.1f} {x:.1f} {y - s * 0.35:.1f} Q{x - s * 0.7:.1f} {y - s * 0.5:.1f} "
                 f"{x - s * 1.08:.1f} {y + s * 0.5:.1f} Z", hair))
    out.append(C(x - s * 0.36, y + s * 0.18, s * 0.14, eyes))
    out.append(C(x + s * 0.36, y + s * 0.18, s * 0.14, eyes))
    out.append(P(f"M{x - s * 0.2:.1f} {y + s * 0.55:.1f} Q{x:.1f} {y + s * 0.7:.1f} {x + s * 0.2:.1f} {y + s * 0.55:.1f}",
                 "none", (150, 70, 70), s * 0.07))
    if hat:
        out.append(P(f"M{x - s:.1f} {y - s * 0.8:.1f} Q{x:.1f} {y - s * 2.6:.1f} {x + s * 1.3:.1f} {y - s * 1.6:.1f} "
                     f"L{x + s:.1f} {y - s * 0.8:.1f} Z", hat))
        out.append(C(x + s * 1.35, y - s * 1.6, s * 0.22, (240, 240, 240)))
    if hoop:
        out.append(E(x, y + s * 2.3, s * 1.7, s * 0.45, "none", hoop, s * 0.18, rot=-8))
    return "".join(out)


def sword(x0, x1, y, t, blade=(210, 214, 220), hilt=(90, 80, 70)):
    L_ = x1 - x0
    return (poly([(x0 + L_ * 0.22, y - t), (x1 - t * 2, y - t), (x1, y), (x1 - t * 2, y + t),
                  (x0 + L_ * 0.22, y + t)], blade, (90, 94, 100), 1)
            + R(x0 + L_ * 0.2, y - t * 3, t * 1.4, t * 6, (170, 150, 90), rx=2)
            + R(x0 + L_ * 0.05, y - t * 0.7, L_ * 0.16, t * 1.4, hilt, rx=2)
            + C(x0 + L_ * 0.04, y, t * 1.3, (255, 226, 120))
            + C(x0 + L_ * 0.04, y, t * 3.2, (255, 226, 120), op=0.25))


# ============================================================================================
# box fronts (W x H px, drawn left-to-right as the face is seen)
# ============================================================================================

def art_mage_night(W, H):
    g = gid("mk")
    out = [grad(g, [(0, (150, 70, 50)), (0.5, (118, 48, 34)), (1, (84, 32, 26))], 0, 0, 1, 1),
           R(0, 0, W, H, f"url(#{g})")]
    out.append(E(W * 0.12, H * 0.4, W * 0.18, H * 0.5, (190, 110, 80), op=0.25))
    out.append(sword(W * 0.2, W * 0.72, H * 0.6, H * 0.045))
    out.append(T(W * 0.03, H * 0.24, "FOR 1-4 NAPPERS", H * 0.13, (240, 232, 220), "Copperplate Gothic Bold",
                 anchor="start", width=W * 0.24))
    out.append(T(W * 0.5, H * 0.25, "A DROWSY WIZARD", H * 0.12, (238, 230, 214), "Copperplate Gothic Bold", width=W * 0.2))
    out.append(T(W * 0.47, H * 0.72, "MAGE NIGHT-LIGHT", H * 0.46, (52, 30, 26), "Bernard MT Condensed",
                 stroke=(236, 226, 206), sw=2.2, width=W * 0.6))
    out.append(T(W * 0.72, H * 0.9, "BOARD GAME", H * 0.12, (238, 230, 214), "Copperplate Gothic Bold"))
    out.append(R(W * 0.02, H * 0.78, W * 0.1, H * 0.16, (40, 40, 44), rx=3))
    out.append(T(W * 0.07, H * 0.9, "WHIZ-ISH", H * 0.1, (255, 255, 255), "Arial Black"))
    return "".join(out)


def art_avaloaf(W, H):
    rng = L.seeded("avaloaf")
    out = [stones(W, H, rng, (128, 124, 110))]
    # a bread loaf wearing a knight's helmet, on the left
    out.append(E(W * 0.14, H * 0.72, W * 0.1, H * 0.26, (196, 140, 70), stroke=(120, 76, 30), sw=1.5))
    for k in range(3):
        out.append(P(f"M{W * (0.09 + k * 0.035):.1f} {H * 0.6:.1f} l{W * 0.02:.1f} {H * 0.18:.1f}", "none", (150, 96, 40), 1.6))
    out.append(P(f"M{W * 0.07:.1f} {H * 0.5:.1f} Q{W * 0.14:.1f} {H * 0.02:.1f} {W * 0.21:.1f} {H * 0.5:.1f} Z",
                 (150, 154, 160), (70, 72, 76), 1.2))
    out.append(R(W * 0.09, H * 0.34, W * 0.1, H * 0.05, (40, 40, 44)))
    out.append(R(0, 0, W * 0.012, H, (60, 58, 52)))
    out.append(T(W * 0.63, H * 0.2, "THE RESISTANCE TO CARBS", H * 0.1, (238, 228, 200), "Copperplate Gothic Bold"))
    out.append(T(W * 0.63, H * 0.66, "AVALOAF", H * 0.5, (222, 180, 70), "Castellar", "bold",
                 stroke=(90, 64, 20), sw=2.0, width=W * 0.6))
    out.append(T(W * 0.63, H * 0.88, "bake responsibly", H * 0.11, (236, 230, 214), "Georgia", italic=True))
    return "".join(out)


def art_one_desk(W, H):
    rng = L.seeded("onedesk")
    out = [bricks(W, H, rng, (58, 60, 62), (40, 42, 44), H / 5)]
    out.append(poly([(W * 0.07, H * 0.5), (W * 0.09, H * 0.3), (W * 0.11, H * 0.5), (W * 0.09, H * 0.62)], (230, 140, 60)))
    out.append(T(W * 0.4, H * 0.45, "ONE DESK", H * 0.26, "none", "Agency FB", "bold").replace('fill="none"', 'fill="none" stroke="#e8e8e8" stroke-width="1.4"'))
    out.append(T(W * 0.4, H * 0.76, "DUNGEON", H * 0.3, (232, 232, 232), "Agency FB", "bold", ls=1))
    for i, sym in enumerate(("clock", "folks")):
        x = W * (0.72 + i * 0.13)
        out.append(R(x, H * 0.22, W * 0.1, H * 0.56, "none", stroke=(210, 210, 210), sw=1.2))
        if sym == "clock":
            out.append(C(x + W * 0.05, H * 0.47, H * 0.15, "none", (210, 210, 210), 1.4))
        else:
            out.append(C(x + W * 0.035, H * 0.44, H * 0.08, (210, 210, 210)))
            out.append(C(x + W * 0.065, H * 0.44, H * 0.08, (210, 210, 210)))
    return "".join(out)


def art_mascarpone(W, H):
    out = [R(0, 0, W, H, (112, 32, 34)), R(3, 3, W - 6, H - 6, "none", stroke=(200, 160, 90), sw=1.2)]
    out.append(T(W * 0.46, H * 0.24, "a very creamy game", H * 0.11, (220, 190, 130), "Georgia", italic=True))
    out.append(T(W * 0.46, H * 0.62, "Mascarpone", H * 0.38, (232, 196, 120), "Edwardian Script ITC", "bold",
                 width=W * 0.72))
    out.append(P(f"M{W * 0.25:.1f} {H * 0.8:.1f} q{W * 0.1:.1f} {H * 0.12:.1f} {W * 0.2:.1f} 0 t{W * 0.2:.1f} 0",
                 "none", (220, 180, 110), 1.4))
    out.append(R(W * 0.84, H * 0.3, W * 0.1, H * 0.4, (150, 190, 70)))
    out.append(C(W * 0.89, H * 0.5, H * 0.1, (250, 240, 200)))
    return "".join(out)


def art_maidens_quiche(W, H):
    out = [R(0, 0, W, H, (156, 186, 212)), R(W * 0.2, 0, W * 0.2, H, (116, 36, 50))]
    out.append(R(W * 0.21, 0, W * 0.005, H, (220, 190, 120)))
    out.append(R(W * 0.39, 0, W * 0.005, H, (220, 190, 120)))
    # a whisk rampant
    x, y = W * 0.3, H * 0.52
    out.append(R(x - 2, y + H * 0.05, 4, H * 0.32, (230, 196, 110), rx=2))
    for k in (-1, -0.4, 0.4, 1):
        out.append(P(f"M{x:.1f} {y + H * 0.08:.1f} Q{x + k * W * 0.05:.1f} {y - H * 0.25:.1f} {x:.1f} {y - H * 0.38:.1f}",
                     "none", (230, 196, 110), 1.6))
    out.append(T(W * 0.68, H * 0.5, "Maiden's", H * 0.34, (210, 176, 90), "Edwardian Script ITC", "bold", width=W * 0.42))
    out.append(T(W * 0.72, H * 0.84, "QUICHE", H * 0.26, (210, 176, 90), "Castellar", width=W * 0.3))
    return "".join(out)


def art_dunno_now(W, H):
    out = [R(0, 0, W, H, (30, 40, 46)), R(0, 0, W * 0.25, H, (60, 90, 100), op=0.6)]
    out.append(T(W * 0.62, H * 0.72, "DUNNO NOW", H * 0.6, (200, 206, 210), "Agency FB", width=W * 0.55))
    out.append(C(W * 0.93, H * 0.5, H * 0.25, "none", (200, 206, 210), 1.5))
    out.append(poly([(W * 0.925, H * 0.38), (W * 0.95, H * 0.5), (W * 0.925, H * 0.62)], (200, 206, 210)))
    return "".join(out)


def art_hula_hooper(W, H):
    rng = L.seeded("hooper")
    g = gid("lp")
    out = [grad(g, [(0, (30, 30, 34)), (1, (46, 50, 60))], 0, 0, 0, 1), R(0, 0, W, H, f"url(#{g})")]
    hairs = [(30, 30, 36), (230, 230, 236), (40, 30, 30), (90, 60, 40), (160, 70, 40), (240, 210, 120),
             (60, 40, 60), (30, 30, 50), (220, 190, 120)]
    coats = [(236, 236, 240), (200, 200, 206), (240, 236, 230), (40, 40, 46), (40, 40, 46), (50, 50, 56),
             (40, 40, 46), (30, 30, 36), (60, 60, 66)]
    hoops = [(240, 90, 120), (90, 200, 240), (250, 210, 60), (120, 220, 120)]
    for i in range(9):
        x = W * (0.04 + i * 0.075)
        out.append(chibi(x, H * 0.3, H * 0.14, hairs[i], coats[i], hoop=hoops[i % 4]))
    out.append(T(W * 0.83, H * 0.4, "TRAGEDY", H * 0.16, (210, 210, 214), "Engravers MT"))
    out.append(T(W * 0.83, H * 0.68, "Hula-Hooper", H * 0.3, (230, 230, 234), "Harrington", "bold", width=W * 0.22))
    for k in range(3):
        out.append(R(W * (0.93 + k * 0.022), H * 0.3, W * 0.018, H * 0.3, (180, 180, 186), rx=2))
    return "".join(out)


def art_sloths(W, H):
    rng = L.seeded("sloths")
    out = [R(0, 0, W, H, (26, 26, 28))]
    for _ in range(26):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        out.append(P(f"M{x:.1f} {y:.1f} q{rng.uniform(-30, 30):.1f} {rng.uniform(-10, 10):.1f} "
                     f"{rng.uniform(-60, 60):.1f} {rng.uniform(-14, 14):.1f}", "none", (200, 200, 204), rng.uniform(0.5, 1.6),
                     op=rng.uniform(0.3, 0.8)))
    out.append(T(W * 0.72, H * 0.8, "SLOTHS", H * 0.7, (238, 238, 240), "Algerian", width=W * 0.42))
    out.append(C(W * 0.2, H * 0.5, H * 0.3, (180, 180, 184), stroke=(90, 90, 94), sw=1.5))
    out.append(C(W * 0.2, H * 0.5, H * 0.12, (60, 60, 64)))
    return "".join(out)


def art_sushi_no(W, H):
    out = [seigaiha(W, H, H * 0.14, (220, 70, 60), (196, 44, 40)), R(0, 0, W, H * 0.08, (120, 200, 190))]
    # a cheerful rice ball, a chicken, and a sulking rice ball
    for cx, sad in ((W * 0.12, False), (W * 0.62, True)):
        out.append(P(f"M{cx - H * 0.3:.1f} {H * 0.95:.1f} Q{cx:.1f} {H * 0.05:.1f} {cx + H * 0.3:.1f} {H * 0.95:.1f} Z",
                     (250, 250, 248), (180, 180, 180), 1))
        out.append(R(cx - H * 0.18, H * 0.66, H * 0.36, H * 0.3, (30, 40, 34)))
        out.append(C(cx - H * 0.09, H * 0.5, H * 0.03, (30, 30, 30)))
        out.append(C(cx + H * 0.09, H * 0.5, H * 0.03, (30, 30, 30)))
        mouth = "Q{0:.1f} {1:.1f}".format(cx, H * (0.52 if sad else 0.64))
        out.append(P(f"M{cx - H * 0.06:.1f} {H * 0.58:.1f} {mouth} {cx + H * 0.06:.1f} {H * 0.58:.1f}", "none", (30, 30, 30), 1.4))
    out.append(C(W * 0.84, H * 0.55, H * 0.3, (250, 250, 250), (200, 200, 200), 1))
    out.append(poly([(W * 0.82, H * 0.22), (W * 0.84, H * 0.1), (W * 0.86, H * 0.22)], (230, 50, 50)))
    out.append(poly([(W * 0.8, H * 0.58), (W * 0.76, H * 0.62), (W * 0.8, H * 0.66)], (250, 190, 40)))
    out.append(T(W * 0.37, H * 0.62, "SUSHI", H * 0.26, (255, 255, 255), "Cooper Black"))
    out.append(T(W * 0.37, H * 0.9, "NO-PARTY", H * 0.2, (255, 236, 120), "Cooper Black"))
    out.append(R(W * 0.94, H * 0.28, W * 0.045, H * 0.44, (255, 255, 255), rx=4))
    out.append(T(W * 0.962, H * 0.56, "8+", H * 0.14, (200, 40, 40), "Arial Black"))
    return "".join(out)


def art_tragic_maze(W, H):
    out = [R(0, 0, W, H, (238, 236, 230))]
    out.append(R(W * 0.06, H * 0.12, H * 0.62, H * 0.62, (230, 200, 150), stroke=(170, 120, 60), sw=1.5))
    x0, y0, s = W * 0.06, H * 0.12, H * 0.62
    for k in range(4):
        out.append(P(f"M{x0 + s * 0.15:.1f} {y0 + s * (0.2 + k * 0.2):.1f} h{s * (0.7 - (k % 2) * 0.3):.1f}", "none", (60, 110, 60), 2))
    out.append(T(W * 0.3, H * 0.4, "TRAGIC", H * 0.2, (60, 60, 64), "Eras Bold ITC", anchor="start"))
    out.append(T(W * 0.3, H * 0.68, "MAZE", H * 0.2, (60, 60, 64), "Eras Bold ITC", anchor="start"))
    out.append(T(W * 0.3, H * 0.88, "a game of getting lost together", H * 0.09, (120, 120, 124), "Arial", anchor="start"))
    cx = W * 0.86
    out.append(C(cx, H * 0.33, H * 0.2, (206, 34, 40)))
    out.append(T(cx, H * 0.39, "ZZZ", H * 0.14, (255, 255, 255), "Arial Black"))
    out.append(poly([(cx - H * 0.14, H * 0.5), (cx + H * 0.14, H * 0.5), (cx + H * 0.2, H * 0.78), (cx - H * 0.2, H * 0.78)], (206, 34, 40)))
    out.append(R(cx - H * 0.3, H * 0.78, H * 0.6, H * 0.12, (230, 196, 60)))
    out.append(T(cx, H * 0.875, "NAP OF THE YEAR", H * 0.07, (120, 30, 30), "Arial Black"))
    return "".join(out)


def art_exit_ish(W, H):
    """Upright box front (W x H portrait)."""
    g1, g2 = gid("ex"), gid("ex")
    out = [grad(g1, [(0, (26, 34, 52)), (1, (12, 14, 20))], 0, 0, 0, 1), R(0, 0, W, H, f"url(#{g1})")]
    out.append(rgrad(g2, [(0, (255, 214, 140), 0.9), (0.5, (230, 150, 60), 0.35), (1, (60, 40, 20), 0)]))
    out.append(C(W * 0.45, H * 0.5, W * 0.4, f"url(#{g2})"))
    out.append(C(W * 0.72, H * 0.52, W * 0.2, (150, 130, 110), op=0.85))
    out.append(C(W * 0.66, H * 0.48, W * 0.2, (40, 40, 50), op=0.35))
    out.append(R(W * 0.43, H * 0.46, W * 0.04, H * 0.12, (240, 230, 200)))
    out.append(P(f"M{W * 0.45:.1f} {H * 0.46:.1f} q{-W * 0.02:.1f} {-H * 0.04:.1f} 0 {-H * 0.07:.1f} "
                 f"q{W * 0.02:.1f} {H * 0.03:.1f} 0 {H * 0.07:.1f}", (255, 220, 120)))
    out.append(R(0, H * 0.62, W, H * 0.2, (60, 44, 32), op=0.9))
    out.append(R(W * 0.1, H * 0.66, W * 0.3, H * 0.06, (120, 40, 36)))
    out.append(R(W * 0.45, H * 0.68, W * 0.35, H * 0.1, (230, 220, 190), op=0.9))
    out.append(R(W * 0.06, H * 0.08, W * 0.46, H * 0.16, (40, 52, 60), stroke=(120, 200, 220), sw=3))
    out.append(T(W * 0.29, H * 0.2, "EXIT-ish", H * 0.08, (225, 245, 250), "Arial Black", width=W * 0.4))
    out.append(T(W * 0.06, H * 0.32, "The Professor's Lost Keys", H * 0.04, (240, 240, 240), "Arial", "bold",
                 anchor="start", width=W * 0.7))
    out.append(T(W * 0.6, H * 0.1, "Can you find them before", H * 0.022, (220, 220, 220), "Arial", anchor="start", italic=True))
    out.append(T(W * 0.6, H * 0.13, "the professor finds lunch?", H * 0.022, (220, 220, 220), "Arial", anchor="start", italic=True))
    out.append(R(W * 0.86, H * 0.62, W * 0.14, H * 0.38, (40, 90, 170)))
    out.append(f'<g transform="translate({W * 0.95:.1f} {H * 0.96:.1f}) rotate(-90)">'
               + T(0, 0, "COSMOSS", W * 0.08, (255, 255, 255), "Arial Black", anchor="start") + "</g>")
    out.append(R(W * 0.06, H * 0.9, W * 0.4, H * 0.035, "none", stroke=(220, 220, 220), sw=1))
    return "".join(out)


def art_deceptiscone(W, H):
    out = [R(0, 0, W, H, (104, 30, 28)), R(0, 0, W, H * 0.06, (70, 20, 20))]
    for i in range(4):
        out.append(R(W * (0.04 + i * 0.05), H * 0.12, W * 0.035, H * 0.22, "none", stroke=(220, 200, 190), sw=1))
    out.append(T(W * 0.52, H * 0.66, "DECEPTISCONE", H * 0.4, (236, 228, 220), "Bodoni MT", "bold", width=W * 0.7))
    out.append(T(W * 0.52, H * 0.86, "MUFFINS IN THE KITCHEN", H * 0.1, (200, 170, 160), "Bodoni MT", ls=3))
    out.append(E(W * 0.08, H * 0.7, H * 0.2, H * 0.14, (200, 150, 90)))
    return "".join(out)


def art_sidereal(W, H):
    rng = L.seeded("sidereal")
    out = [R(0, 0, W, H, (24, 28, 50)), stars(W, H, 90, rng)]
    out.append(E(W * 0.35, H * 0.45, W * 0.5, H * 0.05, (160, 170, 230), op=0.25, rot=-4))
    out.append(T(W * 0.44, H * 0.47, "SIDEREAL", H * 0.34, (236, 236, 244), "Tw Cen MT", ls=8, width=W * 0.62))
    out.append(T(W * 0.44, H * 0.83, "CONFUSION", H * 0.34, (236, 236, 244), "Tw Cen MT", ls=8, width=W * 0.62))
    out.append(T(W * 0.52, H * 0.95, "?", H * 0.14, (250, 200, 80), "Arial Black"))
    return "".join(out)


def art_dixit_didnt(W, H):
    g = gid("dx")
    out = [grad(g, [(0, (214, 180, 120)), (0.5, (196, 150, 96)), (1, (130, 170, 190))], 0, 0, 1, 0),
           R(0, 0, W, H, f"url(#{g})")]
    out.append(P(f"M{W * 0.04:.1f} {H:.1f} V{H * 0.35:.1f} Q{W * 0.08:.1f} {H * 0.05:.1f} {W * 0.12:.1f} {H * 0.35:.1f} V{H:.1f} Z",
                 (150, 80, 60)))
    out.append(P(f"M{W * 0.15:.1f} {H:.1f} V{H * 0.3:.1f} L{W * 0.17:.1f} {H * 0.1:.1f} L{W * 0.19:.1f} {H * 0.3:.1f} V{H:.1f} Z",
                 (130, 170, 200)))
    out.append(E(W * 0.23, H * 0.6, W * 0.012, H * 0.16, (240, 236, 226)))
    out.append(E(W * 0.235, H * 0.36, W * 0.006, H * 0.1, (240, 236, 226)))
    out.append(E(W * 0.225, H * 0.36, W * 0.006, H * 0.1, (240, 236, 226)))
    out.append(T(W * 0.53, H * 0.74, "Dixit Didn't", H * 0.52, (60, 90, 90), "Harrington", "bold",
                 stroke=(250, 240, 220), sw=2.5, width=W * 0.55))
    out.append(P(f"M{W * 0.84:.1f} {H:.1f} V{H * 0.4:.1f} h{W * 0.03:.1f} v{-H * 0.15:.1f} h{W * 0.03:.1f} v{H * 0.25:.1f} h{W * 0.03:.1f} V{H:.1f} Z",
                 (90, 130, 170)))
    return "".join(out)


def art_raptoast(W, H):
    out = [R(0, 0, W, H, (98, 112, 50))]
    out.append(R(W * 0.02, H * 0.55, W * 0.06, H * 0.35, (240, 190, 60)))
    out.append(R(W * 0.09, H * 0.6, W * 0.13, H * 0.28, (60, 60, 70)))
    for i, t in enumerate(("10+", "2", "30'")):
        out.append(T(W * (0.11 + i * 0.045), H * 0.8, t, H * 0.14, (255, 255, 255), "Arial Black"))
    out.append(chibi(W * 0.2, H * 0.3, H * 0.16, (200, 60, 40), (220, 170, 60)))
    out.append(R(W * 0.19, H * 0.26, W * 0.035, H * 0.08, (40, 40, 40), rx=3))
    out.append(T(W * 0.5, H * 0.62, "RAPTOAST", H * 0.42, (190, 90, 60), "Showcard Gothic",
                 stroke=(90, 40, 30), sw=1.5, width=W * 0.34))
    # dino head with a slice of toast
    x, y = W * 0.84, H * 0.5
    out.append(P(f"M{x - W * 0.1:.1f} {y + H * 0.4:.1f} Q{x - W * 0.08:.1f} {y - H * 0.4:.1f} {x:.1f} {y - H * 0.35:.1f} "
                 f"L{x + W * 0.1:.1f} {y - H * 0.1:.1f} L{x + W * 0.02:.1f} {y + H * 0.05:.1f} L{x - W * 0.02:.1f} {y + H * 0.4:.1f} Z",
                 (90, 140, 70), (40, 70, 30), 1.5))
    out.append(C(x - W * 0.01, y - H * 0.2, H * 0.06, (250, 220, 60)))
    out.append(C(x - W * 0.01, y - H * 0.2, H * 0.025, (20, 20, 20)))
    out.append(R(x + W * 0.04, y - H * 0.02, W * 0.05, H * 0.34, (220, 170, 90), rx=5, stroke=(150, 100, 40), sw=2))
    return "".join(out)


def art_valiant_snores(W, H):
    g = gid("vw")
    out = [grad(g, [(0, (220, 170, 90)), (1, (170, 100, 40))], 0, 0, 0, 1), R(0, 0, W, H, f"url(#{g})"),
           R(4, 4, W - 8, H - 8, "none", stroke=(120, 70, 30), sw=2.5)]
    out.append(chibi(W * 0.16, H * 0.42, H * 0.18, (240, 240, 240), (170, 60, 50), hat=(90, 120, 200)))
    out.append(chibi(W * 0.82, H * 0.42, H * 0.18, (90, 50, 40), (80, 80, 90), hat=(200, 80, 120)))
    out.append(T(W * 0.26, H * 0.3, "z", H * 0.14, (255, 255, 255), "Comic Sans MS", "bold"))
    out.append(T(W * 0.92, H * 0.25, "z z", H * 0.12, (255, 255, 255), "Comic Sans MS", "bold"))
    out.append(P(f"M{W * 0.34:.1f} {H * 0.18:.1f} H{W * 0.66:.1f} L{W * 0.64:.1f} {H * 0.72:.1f} L{W * 0.5:.1f} {H * 0.88:.1f} "
                 f"L{W * 0.36:.1f} {H * 0.72:.1f} Z", (170, 40, 40), (240, 200, 90), 2))
    out.append(T(W * 0.5, H * 0.47, "VALIANT", H * 0.24, (250, 214, 90), "Cooper Black", stroke=(90, 40, 20), sw=1.5))
    out.append(T(W * 0.5, H * 0.7, "SNORES", H * 0.2, (255, 255, 255), "Cooper Black", stroke=(90, 40, 20), sw=1.5))
    return "".join(out)


def art_mild_tarot(W, H):
    """Upright deck box front (portrait)."""
    g = gid("tr")
    out = [R(0, 0, W, H, (18, 18, 20))]
    rng = L.seeded("tarot")
    out.append(stars(W, H, 40, rng, "#cfcfcf"))
    out.append(grad(g, [(0, (220, 60, 60)), (0.3, (240, 170, 50)), (0.55, (80, 170, 80)),
                        (0.8, (60, 110, 200)), (1, (150, 70, 170))], 0, 0, 1, 1))
    out.append(C(W * 0.5, H * 0.6, W * 0.42, f"url(#{g})", op=0.85))
    cx, cy = W * 0.5, H * 0.6
    for k in range(48):
        a = 2 * math.pi * k / 48
        out.append(P(f"M{cx + math.cos(a) * W * 0.14:.1f} {cy + math.sin(a) * W * 0.14:.1f} "
                     f"L{cx + math.cos(a) * W * 0.36:.1f} {cy + math.sin(a) * W * 0.36:.1f}", "none", (245, 245, 245), 1.2))
    out.append(C(cx, cy, W * 0.14, (245, 245, 245)))
    out.append(C(cx, cy, W * 0.1, (20, 20, 20)))
    for k in range(6):
        a = 2 * math.pi * k / 6
        out.append(C(cx + math.cos(a) * W * 0.05, cy + math.sin(a) * W * 0.05, W * 0.018, (245, 245, 245)))
    out.append(T(W * 0.5, H * 0.11, "THE MILD UNKNOWN", W * 0.075, (230, 230, 230), "Engravers MT", width=W * 0.72))
    out.append(T(W * 0.5, H * 0.22, "TAROT", W * 0.2, (240, 240, 240), "Bodoni MT", "bold"))
    out.append(T(W * 0.5, H * 0.94, "a gentle deck", W * 0.06, (200, 200, 200), "Engravers MT"))
    return "".join(out)


def art_quinoa(W, H):
    out = [R(0, 0, W, H, (180, 40, 36)), R(W * 0.012, H * 0.06, W * 0.976, H * 0.88, (236, 232, 214))]
    out.append(P(f"M{W * 0.05:.1f} {H * 0.9:.1f} V{H * 0.55:.1f} L{W * 0.08:.1f} {H * 0.45:.1f} L{W * 0.11:.1f} {H * 0.55:.1f} "
                 f"L{W * 0.1:.1f} {H * 0.4:.1f} L{W * 0.13:.1f} {H * 0.3:.1f} L{W * 0.16:.1f} {H * 0.4:.1f} L{W * 0.15:.1f} {H * 0.55:.1f} "
                 f"L{W * 0.18:.1f} {H * 0.45:.1f} L{W * 0.21:.1f} {H * 0.55:.1f} V{H * 0.9:.1f} Z", (160, 150, 130)))
    out.append(E(W * 0.06, H * 0.78, W * 0.022, H * 0.12, (220, 120, 40)))
    out.append(T(W * 0.5, H * 0.8, "QUINOA", H * 0.66, (226, 170, 40), "Algerian", stroke=(130, 70, 20), sw=2.5,
                 width=W * 0.52))
    # a bowl of grains instead of a crane
    out.append(P(f"M{W * 0.76:.1f} {H * 0.55:.1f} Q{W * 0.82:.1f} {H * 0.95:.1f} {W * 0.88:.1f} {H * 0.55:.1f} Z", (90, 60, 40)))
    rng = L.seeded("quinoa")
    for _ in range(40):
        out.append(C(rng.uniform(W * 0.765, W * 0.875), rng.uniform(H * 0.45, H * 0.56), 1.4, (236, 220, 170)))
    out.append(R(W * 0.93, H * 0.2, W * 0.05, H * 0.3, (60, 120, 180)))
    return "".join(out)


def art_mellow_yawnzee(W, H):
    rng = L.seeded("mellow")
    out = [R(0, 0, W, H, (226, 214, 120))]
    for i in range(7):
        y = H * (0.3 + i * 0.1)
        out.append(P(f"M0 {y + rng.uniform(-6, 6):.1f} Q{W * 0.25:.1f} {y - H * 0.2:.1f} {W * 0.5:.1f} {y:.1f} "
                     f"T{W:.1f} {y + rng.uniform(-8, 8):.1f} V{H:.1f} H0 Z",
                     rng.choice([(120, 160, 70), (90, 140, 60), (180, 190, 80), (70, 120, 90)]), op=0.55))
    out.append(T(W * 0.5, H * 0.12, "A RIVER OF NAPS", H * 0.07, (120, 60, 30), "Georgia", ls=2))
    out.append(T(W * 0.5, H * 0.44, "MELLOW", H * 0.32, (190, 40, 30), "Bookman Old Style", "bold",
                 stroke=(250, 240, 200), sw=1.5, width=W * 0.52))
    out.append(T(W * 0.5, H * 0.58, "&", H * 0.14, (190, 40, 30), "Georgia"))
    out.append(T(W * 0.5, H * 0.88, "YAWNZEE", H * 0.32, (190, 40, 30), "Bookman Old Style", "bold",
                 stroke=(250, 240, 200), sw=1.5, width=W * 0.56))
    return "".join(out)


def art_tigers(W, H):
    rng = L.seeded("tigers")
    out = [bricks(W, H, rng, (48, 76, 130), (30, 44, 80), H / 7)]
    out.append(R(0, H * 0.9, W, H * 0.1, (200, 170, 90)))
    for i in range(30):
        out.append(R(i * W / 30 + 2, H * 0.92, W / 60, H * 0.06, (40, 60, 110)))
    # a striped cat relief
    x, y = W * 0.3, H * 0.55
    out.append(P(f"M{x - W * 0.1:.1f} {y + H * 0.25:.1f} L{x - W * 0.08:.1f} {y - H * 0.05:.1f} Q{x:.1f} {y - H * 0.2:.1f} "
                 f"{x + W * 0.08:.1f} {y - H * 0.05:.1f} L{x + W * 0.12:.1f} {y - H * 0.3:.1f} L{x + W * 0.13:.1f} {y + H * 0.02:.1f} "
                 f"L{x + W * 0.1:.1f} {y + H * 0.25:.1f} Z", (200, 150, 80), (120, 80, 30), 1))
    for k in range(5):
        out.append(P(f"M{x - W * 0.06 + k * W * 0.035:.1f} {y - H * 0.08:.1f} l{W * 0.01:.1f} {H * 0.2:.1f}", "none", (90, 50, 20), 2))
    out.append(T(W * 0.12, H * 0.56, "A GAME OF", H * 0.07, (240, 236, 220), "Georgia", "bold"))
    out.append(T(W * 0.12, H * 0.66, "TACT, TALK &", H * 0.07, (240, 236, 220), "Georgia", "bold"))
    out.append(T(W * 0.12, H * 0.76, "TACTFULNESS", H * 0.07, (240, 236, 220), "Georgia", "bold"))
    out.append(T(W * 0.56, H * 0.38, "TIGERS", H * 0.28, (236, 206, 130), "Perpetua Titling MT", "bold", width=W * 0.3))
    out.append(T(W * 0.56, H * 0.49, "&", H * 0.1, (236, 206, 130), "Georgia"))
    out.append(T(W * 0.56, H * 0.76, "EUPHEMISMS", H * 0.28, (236, 206, 130), "Perpetua Titling MT", "bold", width=W * 0.44))
    return "".join(out)


def art_spirit_eyeland(W, H):
    """Engraved birch-ply organiser box with finger joints."""
    rng = L.seeded("spirit")
    out = [R(0, 0, W, H, (222, 198, 160))]
    for _ in range(26):
        y = rng.uniform(0, H)
        out.append(P(f"M0 {y:.1f} Q{W * 0.3:.1f} {y + rng.uniform(-10, 10):.1f} {W * 0.6:.1f} {y:.1f} T{W:.1f} {y + rng.uniform(-6, 6):.1f}",
                     "none", (196, 168, 126), rng.uniform(0.6, 1.6), op=0.6))
    for i in range(8):
        out.append(R(W * (0.02 + i * 0.13), 0, W * 0.065, H * 0.035, (120, 90, 60)))
        out.append(R(W * (0.02 + i * 0.13), H * 0.965, W * 0.065, H * 0.035, (120, 90, 60)))
    out.append(P(f"M0 {H * 0.52:.1f} H{W * 0.36:.1f} Q{W * 0.5:.1f} {H * 0.4:.1f} {W * 0.64:.1f} {H * 0.52:.1f} H{W:.1f}",
                 "none", (110, 80, 50), 1.5))
    out.append(T(W * 0.5, H * 0.56, "SPIRIT EYELAND", H * 0.08, (40, 30, 24), "Jokerman", width=W * 0.32, rot=0))
    out.append(C(W * 0.44, H * 0.64, H * 0.03, "none", (40, 30, 24), 1.2))
    out.append(T(W * 0.52, H * 0.66, "GREATER THAN", H * 0.045, (40, 30, 24), "Arial Black"))
    out.append(T(W * 0.52, H * 0.715, "GNOMES", H * 0.045, (40, 30, 24), "Arial Black"))
    return "".join(out)


def _town_band(W, H, sky, ground, rng):
    g = gid("tt")
    return (grad(g, [(0, sky), (0.7, (180, 220, 230)), (1, ground)], 0, 0, 0, 1) + R(0, 0, W, H, f"url(#{g})")
            + "".join(E(rng.uniform(0, W), H * rng.uniform(0.75, 1.0), W * 0.06, H * 0.3,
                        (80, 140, 70), op=0.8) for _ in range(8)))


def art_tiny_frowns(W, H):
    rng = L.seeded("tinytowns")
    out = [_town_band(W, H, (120, 180, 220), (100, 150, 70), rng)]
    out.append(R(0, 0, W * 0.06, H, (240, 240, 240)))
    for i in range(3):
        out.append(R(W * 0.008, H * (0.08 + i * 0.3), W * 0.044, H * 0.24, (40, 40, 44), rx=3))
    # timber-frame house with a frowning window
    x = W * 0.12
    out.append(R(x, H * 0.35, W * 0.14, H * 0.65, (238, 232, 216), stroke=(90, 60, 40), sw=2))
    out.append(poly([(x - W * 0.01, H * 0.36), (x + W * 0.07, H * 0.02), (x + W * 0.15, H * 0.36)], (180, 60, 50)))
    for k in range(3):
        out.append(R(x + W * (0.015 + k * 0.045), H * 0.5, W * 0.025, H * 0.16, (90, 120, 150), stroke=(90, 60, 40), sw=1.5))
    out.append(P(f"M{x + W * 0.04:.1f} {H * 0.86:.1f} Q{x + W * 0.07:.1f} {H * 0.76:.1f} {x + W * 0.1:.1f} {H * 0.86:.1f}",
                 "none", (60, 40, 30), 2))
    out.append(C(W * 0.4, H * 0.55, H * 0.3, (70, 130, 60)))
    # wooden signboard title
    out.append(R(W * 0.56, H * 0.12, W * 0.3, H * 0.74, (120, 80, 44), rx=8, stroke=(70, 44, 24), sw=3))
    out.append(T(W * 0.71, H * 0.48, "TINY", H * 0.3, (240, 200, 90), "Harrington", "bold"))
    out.append(T(W * 0.71, H * 0.76, "FROWNS", H * 0.22, (240, 200, 90), "Harrington", "bold", width=W * 0.22))
    out.append(P(f"M{W * 0.9:.1f} {H * 0.12:.1f} h{W * 0.07:.1f} v{H * 0.4:.1f} l{-W * 0.035:.1f} {H * 0.14:.1f} l{-W * 0.035:.1f} {-H * 0.14:.1f} Z",
                 (190, 40, 40), (250, 250, 250), 2))
    out.append(T(W * 0.935, H * 0.42, "EGG", H * 0.16, (255, 255, 255), "Arial Black"))
    return "".join(out)


def art_frowns_villains(W, H):
    rng = L.seeded("villains")
    out = [R(0, 0, W, H, (60, 70, 64))]
    for i in range(5):
        out.append(R(W * (0.2 + i * 0.13), H * 0.1, W * 0.11, H * 0.8, rng.choice([(90, 80, 70), (70, 60, 90), (110, 90, 60)]), rx=4))
    out.append(chibi(W * 0.5, H * 0.35, H * 0.2, (100, 90, 190), (110, 100, 200), skin=(150, 140, 220)))
    out.append(C(W * 0.7, H * 0.5, H * 0.3, (170, 60, 40), op=0.8))
    out.append(R(W * 0.03, H * 0.15, W * 0.14, H * 0.7, (120, 80, 44), rx=4))
    out.append(T(W * 0.1, H * 0.5, "TINY FROWNS", H * 0.18, (240, 200, 90), "Harrington", "bold", width=W * 0.12))
    out.append(T(W * 0.1, H * 0.8, "VILLAIN-AGERS", H * 0.14, (255, 255, 255), "Arial", "bold", width=W * 0.12))
    out.append(P(f"M{W * 0.91:.1f} {H * 0.08:.1f} h{W * 0.06:.1f} v{H * 0.55:.1f} l{-W * 0.03:.1f} {H * 0.2:.1f} l{-W * 0.03:.1f} {-H * 0.2:.1f} Z",
                 (190, 40, 40), (250, 250, 250), 2))
    return "".join(out)


def art_frowns_fortune(W, H):
    rng = L.seeded("fortune")
    out = [_town_band(W, H, (140, 180, 110), (90, 130, 60), rng)]
    out.append(R(W * 0.02, 0, W * 0.2, H, (240, 240, 240)))
    out.append(R(W * 0.5, H * 0.05, W * 0.16, H * 0.9, (120, 80, 44), rx=4))
    out.append(T(W * 0.58, H * 0.6, "TINY FROWNS", H * 0.4, (240, 200, 90), "Harrington", "bold", width=W * 0.14))
    out.append(P(f"M{W * 0.78:.1f} {H * 0.9:.1f} Q{W * 0.83:.1f} {H * 0.0:.1f} {W * 0.88:.1f} {H * 0.9:.1f} Z", (220, 170, 90)))
    return "".join(out)


def art_battletuck_mY(W, H):
    g = gid("bt")
    out = [R(0, 0, W, H, (20, 20, 24)),
           rgrad(g, [(0, (90, 110, 200), 0.9), (0.6, (60, 40, 120), 0.5), (1, (20, 20, 24), 0)], 0.35, 0.5, 0.5),
           R(W * 0.1, 0, W * 0.5, H, f"url(#{g})")]
    # a stocky mech tucked into a blanket
    x = W * 0.36
    out.append(R(x - W * 0.07, H * 0.15, W * 0.14, H * 0.45, (70, 70, 90), rx=6))
    out.append(R(x - W * 0.035, H * 0.03, W * 0.07, H * 0.16, (90, 90, 110), rx=4))
    out.append(C(x, H * 0.1, H * 0.03, (240, 60, 60)))
    out.append(P(f"M{x - W * 0.12:.1f} {H:.1f} Q{x - W * 0.1:.1f} {H * 0.45:.1f} {x:.1f} {H * 0.5:.1f} Q{x + W * 0.1:.1f} {H * 0.45:.1f} {x + W * 0.12:.1f} {H:.1f} Z",
                 (150, 60, 60)))
    out.append(R(W * 0.03, H * 0.28, W * 0.08, H * 0.25, (200, 170, 40)))
    out.append(T(W * 0.07, H * 0.46, "CATNAP", H * 0.1, (20, 20, 20), "Arial Black"))
    out.append(T(W * 0.07, H * 0.7, "3500Z", H * 0.1, (200, 170, 40), "Arial", "bold"))
    out.append(T(W * 0.72, H * 0.66, "BATTLETUCK", H * 0.34, (240, 240, 240), "Arial Black", width=W * 0.5))
    out.append(poly([(W * 0.535, H * 0.4), (W * 0.55, H * 0.66), (W * 0.52, H * 0.66)], (230, 180, 40)))
    return "".join(out)


def art_battletuck_mX(W, H):
    out = [R(0, 0, W, H, (22, 22, 26)), C(W * 0.18, H * 0.5, H * 0.28, "none", (220, 220, 220), 2)]
    out.append(poly([(W * 0.18, H * 0.3), (W * 0.26, H * 0.66), (W * 0.1, H * 0.66)], (230, 180, 40)))
    out.append(T(W * 0.62, H * 0.62, "BATTLETUCK", H * 0.26, (230, 230, 230), "Arial Black", width=W * 0.6))
    return "".join(out)


def art_decent_mX(W, H):
    g = gid("dc")
    out = [grad(g, [(0, (30, 60, 80)), (1, (18, 28, 50))], 0, 0, 1, 0), R(0, 0, W, H, f"url(#{g})")]
    out.append(chibi(W * 0.1, H * 0.35, H * 0.14, (200, 180, 120), (40, 110, 130)))
    out.append(R(W * 0.14, H * 0.5, W * 0.03, H * 0.03, (200, 60, 50)))
    out.append(T(W * 0.55, H * 0.46, "DECENT:", H * 0.38, (150, 196, 220), "Colonna MT", "bold",
                 stroke=(20, 40, 60), sw=1.5, width=W * 0.6))
    out.append(T(W * 0.55, H * 0.66, "JOURNEYS IN THE MILDLY DIM", H * 0.12, (200, 220, 230), "Georgia", width=W * 0.6))
    out.append(T(W * 0.55, H * 0.86, "A BOARD GAME OF DUNGEON DAWDLING", H * 0.08, (230, 230, 230), "Georgia"))
    return "".join(out)


def art_decent_mY(W, H):
    out = [R(0, 0, W, H, (20, 32, 56))]
    out.append(T(W * 0.5, H * 0.72, "D", H * 0.6, (150, 196, 220), "Colonna MT", "bold"))
    return "".join(out)


def art_soup_bowl_mX(W, H):
    out = [R(0, 0, W, H, (22, 22, 24))]
    # armoured helmet over a steaming bowl
    x = W * 0.12
    out.append(P(f"M{x - W * 0.09:.1f} {H * 0.95:.1f} Q{x:.1f} {H * 1.2:.1f} {x + W * 0.09:.1f} {H * 0.95:.1f} Z", (180, 60, 40)))
    out.append(E(x, H * 0.95, W * 0.09, H * 0.06, (230, 150, 70)))
    out.append(P(f"M{x - W * 0.07:.1f} {H * 0.72:.1f} Q{x:.1f} {H * 0.0:.1f} {x + W * 0.07:.1f} {H * 0.72:.1f} Z", (120, 120, 130), (60, 60, 64), 1.5))
    out.append(R(x - W * 0.05, H * 0.42, W * 0.1, H * 0.06, (30, 30, 30)))
    for k in (-1, 0, 1):
        out.append(P(f"M{x + k * W * 0.03:.1f} {H * 0.82:.1f} q{-W * 0.01:.1f} {-H * 0.05:.1f} 0 {-H * 0.1:.1f}", "none", (220, 220, 220), 1.2))
    out.append(T(W * 0.56, H * 0.5, "BLOOD BOWL OF SOUP", H * 0.26, (236, 236, 236), "Georgia", "bold", width=W * 0.68))
    out.append(T(W * 0.56, H * 0.72, "THE GAME OF FANTASY BRUNCH", H * 0.1, (220, 220, 220), "Georgia", width=W * 0.5))
    out.append(R(W * 0.25, H * 0.8, W * 0.6, H * 0.06, (120, 30, 30)))
    return "".join(out)


def art_soup_bowl_mY(W, H):
    out = [R(0, 0, W, H, (22, 22, 24)), R(0, H * 0.75, W, H * 0.25, (110, 28, 28))]
    out.append(T(W * 0.5, H * 0.55, "BLOOD BOWL OF SOUP", H * 0.24, (236, 236, 236), "Georgia", "bold", width=W * 0.8))
    return "".join(out)


def art_gold_triangle(W, H):
    out = [R(0, 0, W, H, (18, 18, 20))]
    out.append(poly([(W * 0.5, H * 0.3), (W * 0.64, H * 0.62), (W * 0.36, H * 0.62)], "none", (200, 160, 70), 3))
    out.append(C(W * 0.5, H * 0.52, H * 0.04, (200, 160, 70)))
    return "".join(out)


def _clutter(W, H, subtitle, bg, sub_col, hair, coat, seed, big=False):
    rng = L.seeded(seed)
    g = gid("ic")
    out = [grad(g, [(0, bg), (1, tuple(max(0, c - 30) for c in bg))], 0, 0, 1, 1), R(0, 0, W, H, f"url(#{g})")]
    for _ in range(14):
        a = rng.uniform(0, 2 * math.pi)
        out.append(P(f"M{W * 0.65:.1f} {H * 0.5:.1f} l{math.cos(a) * W * 0.5:.1f} {math.sin(a) * H:.1f} "
                     f"l{math.cos(a + 0.08) * W * 0.05:.1f} {math.sin(a + 0.08) * H * 0.1:.1f} Z", (255, 255, 255), op=0.12))
    out.append(R(0, 0, W * 0.06, H, (240, 240, 240)))
    for i in range(3):
        out.append(R(W * 0.01, H * (0.1 + i * 0.28), W * 0.04, H * 0.22, (40, 40, 50), rx=2))
    out.append(T(W * 0.35, H * 0.12, "A BUBBLE BATH GAME", H * 0.06, (220, 220, 230), "Arial"))
    out.append(P(f"M{W * 0.14:.1f} {H * 0.3:.1f} L{W * 0.56:.1f} {H * 0.24:.1f} L{W * 0.52:.1f} {H * 0.52:.1f} L{W * 0.18:.1f} {H * 0.55:.1f} Z",
                 (200, 30, 40), op=0.9))
    out.append(T(W * 0.35, H * 0.5, "ICONOCLUTTER", H * 0.22, (255, 255, 255), "Impact", stroke=(30, 30, 60), sw=2,
                 width=W * 0.4, italic=True))
    out.append(T(W * 0.35, H * 0.78, subtitle, H * 0.16, sub_col, "Showcard Gothic", stroke=(30, 30, 40), sw=1.2,
                 width=W * 0.36))
    out.append(chibi(W * 0.8, H * 0.42, H * 0.2, hair, coat))
    out.append(P(f"M{W * 0.72:.1f} {H * 0.18:.1f} L{W * 0.8:.1f} {H * 0.02:.1f} L{W * 0.88:.1f} {H * 0.18:.1f} Z", hair))
    return "".join(out)


def art_clutter_splash(W, H):
    return _clutter(W, H, "CASTLE SPLASH", (150, 60, 80), (120, 220, 250), (120, 210, 230), (230, 240, 250), "splash")


def art_clutter_tubs(W, H):
    return _clutter(W, H, "BATHTUBGROUNDS", (60, 70, 150), (255, 255, 255), (80, 110, 200), (140, 150, 170), "tubs")


def art_clutter_snax(W, H):
    return _clutter(W, H, "LEVEL SNAX", (60, 50, 120), (250, 220, 60), (240, 120, 40), (200, 60, 50), "snax")


def art_clutter_lunch(W, H):
    return _clutter(W, H, "LUNCH BREAK", (40, 46, 96), (250, 190, 60), (40, 40, 50), (70, 70, 90), "lunch")


BOX_ART = {
    "a_mage_night_mY": art_mage_night, "a_avaloaf_mY": art_avaloaf, "a_one_desk_mY": art_one_desk,
    "a_mascarpone_mY": art_mascarpone, "a_maidens_quiche_mY": art_maidens_quiche,
    "a_dunno_now_mY": art_dunno_now, "a_hula_hooper_mY": art_hula_hooper,
    "a_sloths_mY": art_sloths, "a_sushi_no_mY": art_sushi_no, "a_tragic_maze_mY": art_tragic_maze,
    "a_exit_ish_mY": art_exit_ish, "a_deceptiscone_mY": art_deceptiscone,
    "a_sidereal_mY": art_sidereal, "a_dixit_didnt_mY": art_dixit_didnt, "a_raptoast_mY": art_raptoast,
    "a_valiant_snores_mY": art_valiant_snores, "a_mild_tarot_mY": art_mild_tarot,
    "a_quinoa_mY": art_quinoa, "a_mellow_yawnzee_mY": art_mellow_yawnzee, "a_tigers_mY": art_tigers,
    "a_spirit_eyeland_mY": art_spirit_eyeland, "a_frowns_villains_mY": art_frowns_villains,
    "a_tiny_frowns_mY": art_tiny_frowns, "a_frowns_fortune_mY": art_frowns_fortune,
    "a_battletuck_mY": art_battletuck_mY, "a_battletuck_mX": art_battletuck_mX,
    "a_decent_mX": art_decent_mX, "a_decent_mY": art_decent_mY,
    "a_soup_bowl_mX": art_soup_bowl_mX, "a_soup_bowl_mY": art_soup_bowl_mY,
    "a_gold_triangle_mY": art_gold_triangle, "a_clutter_splash_mY": art_clutter_splash,
    "a_clutter_tubs_mY": art_clutter_tubs, "a_clutter_snax_mY": art_clutter_snax,
    "a_clutter_lunch_mY": art_clutter_lunch,
}

# ============================================================================================
# book spines: id -> (title, text colour, font, extras)
# ============================================================================================
SPINES = {
    "sherapy": ("Sherapy", (70, 60, 110), "Georgia", {"sub": "R. Rugg", "size": 0.55}),
    "noodles": ("UNSUPERVISED INSTANT NOODLES", (80, 80, 84), "Arial", {"size": 0.3}),
    "grey_small": ("", None, None, {"band": (230, 230, 230)}),
    "grey_hidden": ("", None, None, {}),
    "damp_1": ("Slightly Dampened", (238, 238, 238), "Georgia", {"italic": True, "size": 0.52, "num": "1"}),
    "damp_2": ("Slightly Dampened", (238, 238, 238), "Georgia", {"italic": True, "size": 0.52, "num": "2"}),
    "damp_3": ("Slightly Dampened", (210, 238, 210), "Georgia", {"italic": True, "size": 0.52, "num": "3"}),
    "thin_dark": ("", None, None, {}),
    "feelings": ("Feelings, Probably", (60, 60, 64), "Arial", {"size": 0.5}),
    "tidies": ("Symphony of Shifting Tidies", (240, 230, 160), "Georgia",
               {"grad": ((40, 80, 160), (200, 190, 90)), "size": 0.5, "sub": "A. Moth"}),
    "hatfull": ("Symphony of Hat-full Truths", (230, 220, 140), "Georgia", {"size": 0.5, "sub": "A. Moth"}),
    "cods": ("Awakened Cods", (170, 210, 90), "Algerian", {"size": 0.62, "sub": "B. Gill"}),
    "crowbar": ("CROWBAR: THE BOOK OF LEVERS", (200, 200, 200), "Arial", {"size": 0.55}),
    "eleanor": ("ELEANOR'S HUM", (230, 230, 230), "Arial", {"size": 0.6}),
    "sofa": ("The Sofa", (220, 120, 90), "Georgia", {"size": 0.7}),
    "pheasants": ("BIRTHDAY PHEASANTS", (220, 220, 230), "Arial", {"size": 0.55}),
    "weekend": ("MONSTER OF THE WEEKEND", (245, 245, 245), "Impact", {"size": 0.5}),
    "thin_orange": ("", None, None, {}), "thin_red": ("", None, None, {}), "thin_blue": ("", None, None, {}),
    "blue_one": ("The Blue One", (30, 40, 70), "Arial", {"size": 0.6}),
    "navy_plain": ("", None, None, {"band": (200, 190, 150)}),
    "armadillo": ("ARMADILLO", (20, 20, 20), "Impact", {"size": 0.6, "sub": "R. MADILLO"}),
    "prune": ("PRUNE", (60, 40, 30), "Georgia", {"size": 0.45, "sub": "S. Andworm"}),
    "leviathin": ("LEVIATHIN CRUST", (230, 230, 230), "Perpetua Titling MT", {"size": 0.5}),
    "squeal_21": ("Teach Yourself SQUEAL in 21 Naps", (250, 250, 250), "Arial Black",
                  {"top": (200, 30, 40), "size": 0.34}),
    "squeal_ref": ("SQUEAL INSTANT REVERENCE", (236, 196, 60), "Arial Black", {"size": 0.55}),
    "house_leeks": ("HOUSE OF LEEKS", (20, 20, 20), "Perpetua Titling MT", {"tiles": True, "size": 0.2}),
}


def spine(bk, W, H):
    title, col, font, ex = SPINES[bk]
    base = L.BOOKS[bk][6]
    out = []
    if "grad" in ex:
        g = gid("sp")
        out += [grad(g, [(0, ex["grad"][0]), (1, ex["grad"][1])], 0, 0, 0, 1), R(0, 0, W, H, f"url(#{g})")]
    else:
        out.append(R(0, 0, W, H, base))
    out.append(R(0, 0, W * 0.06, H, (0, 0, 0), op=0.18))
    out.append(R(W * 0.94, 0, W * 0.06, H, (0, 0, 0), op=0.18))
    if "band" in ex:
        out.append(R(0, H * 0.08, W, H * 0.03, ex["band"]))
        out.append(R(0, H * 0.89, W, H * 0.03, ex["band"]))
    if "top" in ex:
        out.append(P(f"M0 0 H{W:.1f} V{H * 0.22:.1f} Q{W / 2:.1f} {H * 0.28:.1f} 0 {H * 0.22:.1f} Z", ex["top"]))
    if ex.get("tiles"):
        rng = L.seeded(bk)
        for i in range(8):
            y = H * (0.03 + i * 0.12)
            out.append(R(W * 0.14, y, W * 0.72, H * 0.1, (20, 20, 22)))
            if i == 2:
                out.append(T(W * 0.5, y + H * 0.045, "HOUSE", W * 0.14, (230, 230, 230), "Perpetua Titling MT"))
                out.append(T(W * 0.5, y + H * 0.07, "OF LEEKS", W * 0.14, (230, 230, 230), "Perpetua Titling MT"))
            else:
                out.append(R(W * 0.2, y + H * 0.01, W * 0.6, H * 0.075, rng.choice([(90, 130, 170), (200, 180, 120), (110, 150, 90)])))
                out.append(R(W * 0.44, y + H * 0.02, W * 0.08, H * 0.06, (60, 140, 60)))
        return "".join(out)
    if title:
        size = W * ex.get("size", 0.6)
        y1 = 0.8 if "sub" in ex or "num" in ex else 0.94
        y0 = 0.3 if "top" in ex else 0.06
        cx, cy = W / 2 + size * 0.34, H * (y0 + y1) / 2
        wt = "bold" if font in ("Arial", "Georgia") else "normal"
        est = measure(title, size, font, wt, ex.get("italic", False))
        k = min(1.3, H * (y1 - y0) / max(est, 1))
        out.append(f'<g transform="translate({cx:.1f} {cy:.1f}) rotate(90) scale({k:.3f} 1)">'
                   + T(0, 0, title, size, col, font, "bold" if font in ("Arial", "Georgia") else "normal",
                       italic=ex.get("italic", False)) + "</g>")
        if "sub" in ex:
            out.append(f'<g transform="translate({W / 2 + W * 0.15:.1f} {H * 0.9:.1f}) rotate(90)">'
                       + T(0, 0, ex["sub"], W * 0.42, col, font) + "</g>")
        if "num" in ex:
            out.append(T(W / 2, H * 0.93, ex["num"], W * 0.6, col, "Georgia", "bold"))
    return "".join(out)


# ============================================================================================
# props and the chart
# ============================================================================================

def art_chart(W, H):
    """Generic resistor colour-code chart, laid out like the sheet on the hutch (redrawn)."""
    out = [R(0, 0, W, H, (246, 246, 242))]
    s = W / 8.5                          # px per inch of paper
    out.append(T(W / 2, s * 0.65, "RESISTOR COLOR CODE GUIDE", s * 0.42, (20, 20, 20), "Arial Black", width=W * 0.84))

    def resistor(cx, cy, bands, length=2.2):
        o = [R(cx - s * 2.1, cy - 2, s * 4.2, 4, (150, 150, 150)),
             R(cx - s * length / 2, cy - s * 0.2, s * length, s * 0.4, (226, 206, 170), rx=s * 0.18)]
        for i, bc in enumerate(bands):
            o.append(R(cx - s * length * 0.3 + i * s * 0.28, cy - s * 0.2, s * 0.12, s * 0.4, bc))
        return "".join(o)

    colours = [("Black", (20, 20, 20), "0", "1", ""), ("Brown", (120, 70, 40), "1", "10", "± 1%"),
               ("Red", (210, 40, 40), "2", "100", "± 2%"), ("Orange", (240, 140, 40), "3", "1K", ""),
               ("Yellow", (246, 226, 60), "4", "10K", ""), ("Green", (60, 160, 70), "5", "100K", ""),
               ("Blue", (60, 110, 210), "6", "1M", ""), ("Violet", (140, 80, 170), "7", "10M", ""),
               ("Gray", (150, 150, 150), "8", "", ""), ("White", (250, 250, 250), "9", "", ""),
               ("Gold", (212, 176, 60), "", "0.1", "± 5%"), ("Silver", (196, 196, 196), "", "0.01", "± 10%"),
               ("None", (246, 246, 242), "", "", "± 20%")]
    out.append(T(W / 2, s * 1.05, "4-Band Code", s * 0.16, (40, 40, 40), "Arial"))
    out.append(resistor(W / 2, s * 1.3, [(120, 70, 40), (20, 20, 20), (210, 40, 40), (212, 176, 60)]))
    tx0, ty0, rh = s * 0.25, s * 2.0, s * 0.19
    cols = [0.0, 1.1, 2.3, 3.5, 4.7, 7.0, 8.0]
    heads = ["Color", "1st Band", "2nd Band", "3rd Band", "Multiplier", "Tolerance"]
    out.append(R(tx0, ty0, W - 2 * tx0, rh, (210, 210, 210), stroke=(40, 40, 40), sw=0.8))
    for i, hd in enumerate(heads):
        out.append(T(tx0 + s * (cols[i] + 0.1), ty0 + rh * 0.75, hd, s * 0.13, (20, 20, 20), "Arial", "bold",
                     anchor="start", italic=True))
    for r_, (nm, c, dig, mul, tol) in enumerate(colours):
        y = ty0 + rh * (r_ + 1)
        out.append(R(tx0, y, s * 7.0, rh, c, stroke=(60, 60, 60), sw=0.5))
        out.append(R(tx0 + s * 7.0, y, W - 2 * tx0 - s * 7.0, rh, (226, 226, 226), stroke=(60, 60, 60), sw=0.5))
        tc = (255, 255, 255) if nm in ("Black", "Brown", "Blue", "Violet") else (20, 20, 20)
        out.append(T(tx0 + s * 0.1, y + rh * 0.78, nm, s * 0.13, tc, "Arial", "bold", anchor="start"))
        for k in range(3):
            if dig and not (k == 0 and dig == "0"):
                out.append(T(tx0 + s * (cols[k + 1] + 0.5), y + rh * 0.78, dig, s * 0.13, tc, "Arial"))
        if mul:
            out.append(T(tx0 + s * 5.8, y + rh * 0.78, mul, s * 0.13, tc, "Arial"))
        if tol:
            out.append(T(tx0 + s * 7.4, y + rh * 0.78, tol, s * 0.13, (20, 20, 20), "Arial"))
    y = ty0 + rh * (len(colours) + 1)
    out.append(resistor(W / 2, y + s * 0.8, [(246, 226, 60), (140, 80, 170), (60, 160, 70), (20, 20, 20), (120, 70, 40)]))
    out.append(T(W / 2, y + s * 1.35, "5-Band Code", s * 0.16, (40, 40, 40), "Arial"))
    out.append(R(tx0, y + s * 1.6, W - 2 * tx0, 1.2, (60, 60, 60)))
    out.append(T(W / 2, y + s * 1.95, "Calculation", s * 0.2, (20, 20, 20), "Arial", "bold"))
    out.append(resistor(W * 0.42, y + s * 2.5, [(210, 40, 40), (20, 20, 20), (246, 226, 60), (196, 196, 196)]))
    lines = ["First Band  Red ........ 2", "Second Band  Black ...... 0", "Multiplier  Yellow ... x10,000",
             "Tolerance  Silver ..... 10 %"]
    for i, ln in enumerate(lines):
        out.append(T(s * 0.6, y + s * (3.05 + i * 0.2), ln, s * 0.12, (30, 30, 30), "Arial", anchor="start"))
    out.append(T(s * 4.3, y + s * 3.1, "The gold or silver band always goes on the right;", s * 0.1, (30, 30, 30), "Arial", anchor="start"))
    out.append(T(s * 4.3, y + s * 3.25, "read the value from left to right.", s * 0.1, (30, 30, 30), "Arial", anchor="start"))
    out.append(R(s * 0.6, y + s * 3.9, s * 3.0, s * 1.0, "none", stroke=(40, 40, 40), sw=1))
    out.append(T(s * 0.75, y + s * 4.2, "20 x 10,000 = 200,000", s * 0.12, (30, 30, 30), "Arial", anchor="start"))
    out.append(T(s * 0.75, y + s * 4.5, "Resistor = 200 kOhm, 10 %", s * 0.12, (30, 30, 30), "Arial", "bold", anchor="start"))
    return "".join(out)


def art_paper_news(W, H):
    rng = L.seeded("news")
    out = [R(0, 0, W, H, (240, 238, 232))]
    for col in range(3):
        for i in range(14):
            out.append(R(W * (0.04 + col * 0.32), H * (0.08 + i * 0.06), W * rng.uniform(0.18, 0.28), H * 0.018, (120, 120, 124)))
    out.append(R(W * 0.66, H * 0.1, W * 0.14, H * 0.3, (200, 226, 236)))
    out.append(R(W * 0.82, H * 0.1, W * 0.14, H * 0.3, (246, 238, 190)))
    return "".join(out)


def art_magazines(W, H):
    rng = L.seeded("mags")
    out = [R(0, 0, W, H, (236, 236, 232))]
    for _ in range(16):
        out.append(R(rng.uniform(0, W * 0.8), rng.uniform(0, H * 0.8), rng.uniform(W * 0.1, W * 0.4), rng.uniform(H * 0.05, H * 0.3),
                     rng.choice([(40, 90, 170), (60, 140, 90), (200, 70, 50), (230, 230, 220), (120, 170, 210), (210, 190, 120)]),
                     op=0.9))
    for i in range(20):
        out.append(R(0, i * H / 20, W, 1.2, (255, 255, 255), op=0.5))
    return "".join(out)


def art_notebook(W, H):
    out = [R(0, 0, W, H, (238, 238, 240))]
    for i in range(24):
        out.append(R(0, i * H / 24, W, 1.4, (200, 200, 206)))
    for i in range(20):
        out.append(C(W * (0.04 + i * 0.048), H * 0.05, 3, (80, 80, 90)))
    return "".join(out)


def art_lamp(W, H):
    """Cream shade with a hand-drawn blue branching pattern (random walk of little squares)."""
    rng = L.seeded("lamp")
    out = [R(0, 0, W, H, (236, 226, 190))]
    for strand in range(3):
        x, y = W * (0.2 + strand * 0.3), H
        d = []
        while y > 0:
            nx = x + rng.choice((-1, 1)) * rng.uniform(4, 12)
            ny = y - rng.uniform(4, 12)
            d.append(f"M{x:.1f} {y:.1f} L{nx:.1f} {ny:.1f}")
            if rng.random() < 0.3:
                d.append(f"M{nx:.1f} {ny:.1f} l{rng.uniform(-10, 10):.1f} {rng.uniform(-6, 6):.1f}")
            if rng.random() < 0.18:
                out.append(R(nx - 4, ny - 4, 8, 8, "none", stroke=(40, 70, 170), sw=2))
            x, y = min(max(nx, 6), W - 6), ny
        out.append(P(" ".join(d), "none", (40, 70, 170), 2.2))
    out.append(R(0, 0, W, 4, (40, 70, 170)))
    return "".join(out)


def art_straw(W, H):
    out = [R(0, 0, W, H, (214, 200, 160))]
    for i in range(0, int(W), 6):
        out.append(R(i, 0, 2, H, (190, 174, 130)))
    for j in range(0, int(H), 12):
        out.append(R(0, j, W, 1.2, (170, 156, 116)))
    return "".join(out)


def art_pink_weave(W, H):
    out = [R(0, 0, W, H, (214, 140, 120))]
    for i in range(-int(H), int(W), 12):
        out.append(P(f"M{i} 0 l{H} {H}", "none", (236, 170, 150), 3))
        out.append(P(f"M{i + H} 0 l{-H} {H}", "none", (190, 116, 98), 2))
    return "".join(out)


def art_aluminium(W, H):
    out = [R(0, 0, W, H, (196, 198, 202))]
    for j in range(0, int(H), 5):
        out.append(R(0, j, W, 1.5, (226, 228, 232)))
        out.append(R(0, j + 2.5, W, 1.0, (160, 162, 168)))
    out.append(R(0, H * 0.48, W, 3, (110, 112, 118)))
    return "".join(out)


def art_mask_face(W, H):
    """Pale-blue feathered eye mask with sequin-rimmed black eye holes (card is 7.8 x 3.4 in)."""
    rng = L.seeded("maskface")
    out = [R(0, 0, W, H, (120, 162, 206))]
    for _ in range(90):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        out.append(P(f"M{x:.1f} {y:.1f} q{rng.uniform(-12, 12):.1f} {rng.uniform(-10, 10):.1f} {rng.uniform(-24, 24):.1f} {rng.uniform(-8, 8):.1f}",
                     "none", rng.choice([(210, 230, 246), (170, 205, 232), (120, 160, 210)]), rng.uniform(1, 2.5)))
    for cx in (W * 0.3, W * 0.7):
        out.append(E(cx, H * 0.45, W * 0.13, H * 0.2, (18, 18, 22), (60, 60, 70), 5))
    return "".join(out)


def art_feather(W, H, main, dark, stripes=False):
    out = [R(0, 0, W, H, main)]
    for i in range(0, int(H), 6):
        out.append(P(f"M{W / 2:.1f} {i:.1f} l{-W / 2:.1f} {6:.1f} M{W / 2:.1f} {i:.1f} l{W / 2:.1f} {6:.1f}", "none", dark, 1, op=0.5))
    if stripes:
        for i in range(0, int(H), 14):
            out.append(R(0, i, W, 6, (40, 20, 20), op=0.6))
    out.append(R(W / 2 - 1.5, 0, 3, H, (230, 230, 236)))
    return "".join(out)


def art_half_mask(W, H):
    g = gid("hm")
    return (grad(g, [(0, (60, 150, 190)), (0.4, (200, 220, 230)), (0.7, (90, 120, 190)), (1, (160, 200, 180))], 0, 0, 1, 1)
            + R(0, 0, W, H, f"url(#{g})") + E(W * 0.55, H * 0.45, W * 0.16, H * 0.18, (20, 30, 40))
            + R(0, 0, W, H, "none", stroke=(220, 220, 226), sw=4))


def art_postcard(W, H):
    g = gid("pc")
    return (grad(g, [(0, (150, 190, 220)), (1, (230, 230, 210))], 0, 0, 0, 1) + R(0, 0, W, H, f"url(#{g})")
            + P(f"M0 {H * 0.6:.1f} Q{W * 0.3:.1f} {H * 0.4:.1f} {W * 0.6:.1f} {H * 0.55:.1f} T{W:.1f} {H * 0.5:.1f} V{H:.1f} H0 Z", (90, 130, 70))
            + P(f"M0 {H * 0.8:.1f} Q{W * 0.5:.1f} {H * 0.65:.1f} {W:.1f} {H * 0.85:.1f} V{H:.1f} H0 Z", (130, 160, 80)))


def art_flame(W, H, seed, n=5, col=(34, 14, 6)):
    """Cathedral grain of flat-sawn pine: nested arches along the grain (overlay only)."""
    rng = L.seeded(seed)
    out = []
    for _ in range(n):
        xc, yc = rng.uniform(0.1, 0.9) * W, rng.uniform(0.05, 0.95) * H
        half = rng.uniform(0.04, 0.09) * W
        tall = rng.uniform(0.12, 0.3) * H
        for k in range(rng.randint(5, 9)):
            hw = half * (1 + k * 0.45)
            out.append(P(f"M{xc - hw:.1f} {yc + tall * (1 + k * 0.6):.1f} Q{xc - hw:.1f} {yc - tall * 0.2 + k * 3:.1f} {xc:.1f} {yc + k * 6:.1f} "
                         f"Q{xc + hw:.1f} {yc - tall * 0.2 + k * 3:.1f} {xc + hw:.1f} {yc + tall * (1 + k * 0.6):.1f}",
                         "none", col, rng.uniform(2.5, 6.0), op=rng.uniform(0.14, 0.28)))
    return "".join(out)


def art_battery(W, H):
    return (R(0, 0, W, H, (30, 30, 32)) + R(W * 0.72, 0, W * 0.28, H, (190, 130, 60))
            + R(W * 0.1, H * 0.35, W * 0.4, H * 0.3, (90, 90, 96)))


def art_critter(W, H):
    rng = L.seeded("critter")
    return R(0, 0, W, H, (74, 72, 70)) + "".join(C(rng.uniform(0, W), rng.uniform(0, H), 1.5, (100, 98, 94)) for _ in range(40))


PROP_ART = {"chart": art_chart, "paper_news": art_paper_news, "magazines": art_magazines,
            "notebook": art_notebook, "lamp": art_lamp, "straw": art_straw, "pink_weave": art_pink_weave,
            "aluminium": art_aluminium, "mask_face": art_mask_face, "half_mask": art_half_mask,
            "postcard": art_postcard,
            "wood": lambda W, H: art_flame(W, H, "wood", 7), "wood_dark": lambda W, H: art_flame(W, H, "wdark", 3), "battery": art_battery, "critter": art_critter,
            "feather_blue": lambda W, H: art_feather(W, H, (44, 66, 150), (26, 34, 90)),
            "feather_red": lambda W, H: art_feather(W, H, (140, 36, 50), (90, 20, 30), stripes=True),
            "feather_light": lambda W, H: art_feather(W, H, (150, 190, 226), (100, 140, 196))}

FLAT = {"brass": (176, 140, 72), "chrome": (210, 212, 216), "glass": (170, 184, 188), "black": (20, 20, 22),
        "white": (240, 240, 238), "paper_cream": (236, 228, 204), "wire": (190, 192, 196),
        "spider_red": (190, 30, 40), "paper_white": (246, 246, 242), "gold": (200, 160, 70)}


def make_svg():
    regs = ATLAS["regions"]
    n = ATLAS["size"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{n}" height="{n}" viewBox="0 0 {n} {n}">',
             "<!-- media_hutch parody box art, spines and props. Drawn from scratch; "
             "regenerated by textures.py. -->"]
    for name, (x, y, w, h) in regs.items():
        body = None
        if name in BOX_ART:
            body = BOX_ART[name](w, h)
        elif name.startswith("s_"):
            body = spine(name[2:], w, h)
        elif name in PROP_ART:
            body = PROP_ART[name](w, h)
        elif name.startswith("c_"):
            key = name[2:]
            col = L.BOXES[key][8] if key in L.BOXES else L.BOOKS[key][6]
            body = R(0, 0, w, h, col)
        elif name in FLAT:
            body = R(0, 0, w, h, FLAT[name])
        if body:
            parts.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" overflow="hidden">'
                         f"{body}</svg>")
    parts.append("</svg>")
    os.makedirs(os.path.dirname(SVG_PATH), exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return SVG_PATH


# ============================================================================================
# GIMP painting
# ============================================================================================

def paint_wood(a, region, base, grain_amt=0.32, knots=2, flecks=60, seed=0):
    """Stained knotty pine: grain runs along the region's height (v)."""
    rng = random.Random(seed)
    x, y, w, h = a.rect(region)
    fill_rect(a.img, a.lay, (x, y, w, h), base)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:noise-rgb", correlated=False, independent=False, red=grain_amt, green=grain_amt,
         blue=grain_amt, gaussian=True, seed=rng.randint(0, 99999))
    try:
        gegl(a.lay, "gegl:gaussian-blur", std_dev_x=0.6, std_dev_y=max(20.0, h * 0.08), abyss_policy="clamp")
    except Exception:
        gegl(a.lay, "gegl:gaussian-blur", std_dev_x=0.6, std_dev_y=max(20.0, h * 0.08))
    Gimp.Selection.none(a.img)
    dark = tuple(max(0, int(c * 0.62)) for c in base)
    light = tuple(min(255, int(c * 1.3)) for c in base)
    # long wavy grain streaks
    for _ in range(max(6, w // 14)):
        sx = x + rng.uniform(0, w)
        sw_ = rng.uniform(1.5, 5.0)
        col = dark if rng.random() < 0.65 else light
        a.img.select_rectangle(Gimp.ChannelOps.REPLACE, int(sx), y, max(1, int(sw_)), h)
        _fill(a.lay, col + (rng.uniform(0.3, 0.6),))
    Gimp.Selection.none(a.img)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:ripple", amplitude=4.0, period=float(max(80, h // 4)), phi=rng.uniform(0, 1), angle=0.0)
    Gimp.Selection.none(a.img)
    # knots: dark ellipses with a lighter ring, stretched along the grain
    for _ in range(knots):
        cx, cy = x + rng.uniform(w * 0.15, w * 0.85), y + rng.uniform(h * 0.1, h * 0.9)
        rx, ry = rng.uniform(w * 0.02, w * 0.035), rng.uniform(h * 0.012, h * 0.022)
        fill_ellipse(a.img, a.lay, (cx - rx * 1.8, cy - ry * 2.4, cx + rx * 1.8, cy + ry * 2.4), dark + (0.35,))
        fill_ellipse(a.img, a.lay, (cx - rx, cy - ry, cx + rx, cy + ry), tuple(int(c * 0.6) for c in base) + (0.6,))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=0.8, std_dev_y=1.6)
    Gimp.Selection.none(a.img)
    # the filters above wash the colour toward grey: re-stain the region from its luminance
    hue, sat, lit = STAIN[region]
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    a.lay.colorize_hsl(hue, sat, lit)
    Gimp.Selection.none(a.img)
    # distressing flecks
    for _ in range(flecks):
        fx, fy = x + rng.uniform(0, w), y + rng.uniform(0, h)
        r = rng.uniform(0.6, 1.8)
        fill_ellipse(a.img, a.lay, (fx - r, fy - r * 0.7, fx + r, fy + r * 0.7), (30, 16, 10, rng.uniform(0.5, 0.9)))


def paint_interior(a):
    x, y, w, h = a.rect("interior")
    fill_rect(a.img, a.lay, (x, y, w, h), (36, 30, 30))
    grain(a.img, a.lay, (x, y, w, h), 0.05, 0.8)
    for i in range(0, w, 16):
        fill_rect(a.img, a.lay, (x + i, y, 2, h), (18, 15, 16))
        fill_rect(a.img, a.lay, (x + i + 2, y, 1, h), (54, 46, 44))


def rectify_print():
    """Cassidy's linocut from IMG_1508 -> the art atlas; QR swapped, signature kept."""
    b = Atlas(ART_ATLAS)
    x, y, w, h = b.rect("print")
    # paper corners in IMG_1508 (full-res px): TL, TR, BR, BL
    quad = [(840, 2083), (1207, 2097), (1226, 2682), (828, 2688)]
    img = rectify(os.path.join(REF, "IMG_1508.jpg"), quad, w, h)
    lay = img.get_layers()[0]
    # even out the soft window light without losing the ink colour: a gentle levels stretch
    gegl(lay, "gegl:stretch-contrast", keep_colors=True, perceptual=True)
    # the QR code area (inside the carved frame): a fresh random block pattern, no finder
    # squares, no timing lines - cut in the same red ink on the same paper white
    qx0, qy0, qx1, qy1 = 0.155, 0.285, 0.845, 0.74
    red = (178, 64, 56)
    paper = (232, 222, 210)
    qx, qy, qw, qh = int(w * qx0), int(h * qy0), int(w * (qx1 - qx0)), int(h * (qy1 - qy0))
    fill_rect(img, lay, (qx, qy, qw, qh), paper)
    fill_rect(img, lay, (qx + 6, qy + 6, qw - 12, qh - 12), red)
    rng = random.Random(8080)
    n = 17
    cw, ch = (qw - 24) / n, (qh - 24) / n
    for i in range(n):
        for j in range(n):
            if rng.random() < 0.42:
                fill_rect(img, lay, (int(qx + 12 + i * cw + 1), int(qy + 12 + j * ch + 1), int(cw - 1), int(ch - 1)), paper)
    img.select_rectangle(Gimp.ChannelOps.REPLACE, qx, qy, qw, qh)
    gegl(lay, "gegl:noise-rgb", correlated=False, independent=False, red=0.06, green=0.06, blue=0.06,
         gaussian=True, seed=11)
    gegl(lay, "gegl:gaussian-blur", std_dev_x=0.9, std_dev_y=0.9)
    Gimp.Selection.none(img)
    add_layer_from(b.img, img, "print", x, y)
    flatten(b.img)
    b.lay = b.img.get_layers()[0]
    b.material("print", 0.0, 0.08)
    b.save()


SMOOTH = {"brass": (1.0, 0.6), "chrome": (1.0, 0.75), "aluminium": (1.0, 0.55), "glass": (0.0, 0.92),
          "wood": (0.0, 0.42), "wood_dark": (0.0, 0.38), "wood_edge": (0.0, 0.45), "interior": (0.0, 0.2),
          "battery": (0.3, 0.5), "straw": (0.0, 0.1), "pink_weave": (0.0, 0.15), "black": (0.0, 0.45),
          "paper_news": (0.0, 0.08), "notebook": (0.0, 0.08), "chart": (0.0, 0.08), "magazines": (0.0, 0.3),
          "lamp": (0.0, 0.35), "wire": (1.0, 0.6), "half_mask": (0.6, 0.6)}


def build():
    random.seed(1492)
    a = Atlas(ATLAS)
    paint_wood(a, "wood", WOOD, knots=3, flecks=140, seed=3)
    paint_wood(a, "wood_dark", WOOD_DARK, knots=1, flecks=50, seed=5)
    paint_wood(a, "wood_edge", WOOD_EDGE, knots=0, flecks=20, seed=7)
    paint_interior(a)
    svg = load(make_svg())
    if svg.get_width() != a.size:
        svg.scale(a.size, a.size)
    lay = add_layer_from(a.img, svg, "boxart", 0, 0)
    svg.delete()
    lay = flatten(a.img)
    a.lay = lay
    # printed-card grain and a touch of softness on everything painted from the SVG
    for name, (x, y, w, h) in ATLAS["regions"].items():
        if name.startswith(("a_", "s_")) or name in ("chart", "magazines", "paper_news", "postcard"):
            grain(a.img, a.lay, (x, y, w, h), 0.035, 0.5)
    for name in ATLAS["regions"]:
        met, sm = SMOOTH.get(name, (0.0, 0.4 if name.startswith("a_") else 0.3))
        a.material(name, met, sm)
    a.save()
    rectify_print()
