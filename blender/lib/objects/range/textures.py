"""range atlas (headless GIMP, gimp_textures.py helpers in scope).

Everything is painted from scratch; colours sampled by eye from the survey crops and the
close capture frames (wide_..._003907/003908/003909 cooktop and backguard from above,
_004105/_004111 door and handle). Wear only where the photos show it: burnt brown rings
and spatter around the burner openings, dark crusted drip pans inside a chrome rim, rust
specks on the yellowed handle and along the door-to-drawer seam, faint smudges near the
knobs. The backguard's printing is unreadable tick marks and grey label blobs; the maker
badge is the parody "grumbleworks" (logos/grumbleworks.svg). The clock digits are plain
green bars on the emission map.
"""

import ast
import math
import os
import random

_OBJ = os.path.join(ROOT, "blender", "lib", "objects", "range", "object.py")
_LOGOS = os.path.join(ROOT, "blender", "lib", "objects", "range", "logos")


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
rnd = random.Random(7)

WHITE = (234, 234, 230)
BURN = (104, 60, 28)
RUST = (138, 82, 40)
CREAM = (230, 222, 200)


def blot(img, lay, cx, cy, rx, ry, rgb, alpha, feather=0.0):
    img.select_ellipse(Gimp.ChannelOps.REPLACE, cx - rx, cy - ry, 2 * rx, 2 * ry)
    if feather:
        Gimp.Selection.feather(img, feather)
    if not Gimp.Selection.is_empty(img):
        _fill(lay, tuple(rgb) + (alpha,))
    Gimp.Selection.none(img)


def ring(img, lay, cx, cy, r0, r1, rgb, alpha, feather=0.0, sy=1.0):
    img.select_ellipse(Gimp.ChannelOps.REPLACE, cx - r1, cy - r1 * sy, 2 * r1, 2 * r1 * sy)
    img.select_ellipse(Gimp.ChannelOps.SUBTRACT, cx - r0, cy - r0 * sy, 2 * r0, 2 * r0 * sy)
    if feather:
        Gimp.Selection.feather(img, feather)
    if not Gimp.Selection.is_empty(img):
        _fill(lay, tuple(rgb) + (alpha,))
    Gimp.Selection.none(img)


def line(lay, pts, rgb, size):
    """pts: flat [x0, y0, x1, y1, ...]"""
    Gimp.context_set_foreground(color(rgb))
    Gimp.context_set_brush_size(size)
    Gimp.pencil(lay, [float(v) for v in pts])


def specks(img, lay, rect, n, rgb, rmin, rmax, amin, amax):
    x, y, w, h = rect
    for _ in range(n):
        r = rnd.uniform(rmin, rmax)
        blot(img, lay, x + rnd.uniform(0, w), y + rnd.uniform(0, h), r, r * rnd.uniform(0.6, 1.2), rgb,
             rnd.uniform(amin, amax))


# --- regions ------------------------------------------------------------------------

def cooktop(a):
    x, y, w, h = a.rect("cooktop")
    y0, y1 = C["TOP_Y"]
    px = lambda X: x + (X + W / 2) / W * w
    py = lambda Y: y + (y1 - Y) / (y1 - y0) * h
    s = w / W
    a.fill("cooktop", WHITE, 0.0, 0.72, noise=0.012, blur=1.0)
    # raised rim: a soft grey line an inch in from the edges
    for r0, al in ((0.9, 0.35), (1.05, 0.2)):
        img, lay = a.img, a.lay
        img.select_round_rectangle(Gimp.ChannelOps.REPLACE, x + r0 * s, y + r0 * s, w - 2 * r0 * s, h - 2 * r0 * s, 20, 20)
        img.select_round_rectangle(Gimp.ChannelOps.SUBTRACT, x + (r0 + 0.12) * s, y + (r0 + 0.12) * s,
                                   w - 2 * (r0 + 0.12) * s, h - 2 * (r0 + 0.12) * s, 20, 20)
        Gimp.Selection.feather(img, 3)
        _fill(lay, (170, 172, 172, al))
        Gimp.Selection.none(img)
    for bx, by, r in C["BURNERS"]:
        cx, cy = px(bx), py(by)
        rp = (r + C["PAN_RIM"]) * s
        # burnt ring hugging the pan opening, uneven, plus spatter further out
        for k in range(10):
            ang = rnd.uniform(0, 2 * math.pi)
            d = rp + rnd.uniform(-0.05, 0.35) * s
            blot(a.img, a.lay, cx + math.cos(ang) * d, cy + math.sin(ang) * d, rnd.uniform(0.3, 0.9) * s,
                 rnd.uniform(0.2, 0.5) * s, BURN, rnd.uniform(0.25, 0.5), 3)
        ring(a.img, a.lay, cx, cy, rp - 2, rp + 0.3 * s, BURN, 0.55, 3)
        for k in range(28):
            ang = rnd.uniform(0, 2 * math.pi)
            d = rp + abs(rnd.gauss(0, 1.3)) * s
            rr = rnd.uniform(0.6, 2.2)
            blot(a.img, a.lay, cx + math.cos(ang) * d, cy + math.sin(ang) * d, rr, rr, RUST, rnd.uniform(0.35, 0.8))
    # general light spatter and a couple of dull smudges
    specks(a.img, a.lay, (x + 20, y + 20, w - 40, h - 40), 60, RUST, 0.6, 1.8, 0.2, 0.6)
    specks(a.img, a.lay, (x + 60, y + 60, w - 120, h - 120), 6, (190, 180, 160), 10, 22, 0.06, 0.12)


def drippan(a):
    x, y, w, h = a.rect("drippan")
    cx, cy, R = x + w / 2, y + h / 2, w / 2 - 2
    a.fill("drippan", (60, 52, 46), 0.0, 0.3)
    # chrome rim and sloping wall, then crusted bowl
    ring(a.img, a.lay, cx, cy, R * 0.80, R, (196, 198, 202), 1.0)
    ring(a.img, a.lay, cx, cy, R * 0.80, R * 0.9, (150, 146, 140), 0.8, 4)
    for k in range(40):
        ang = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0.2, 0.82) * R
        blot(a.img, a.lay, cx + math.cos(ang) * d, cy + math.sin(ang) * d, rnd.uniform(4, 14), rnd.uniform(3, 9),
             rnd.choice([(78, 56, 38), (38, 32, 28), (92, 70, 48)]), rnd.uniform(0.25, 0.55), 3)
    for k in range(12):   # rust at the rim edge
        ang = rnd.uniform(0, 2 * math.pi)
        d = R * rnd.uniform(0.8, 0.9)
        blot(a.img, a.lay, cx + math.cos(ang) * d, cy + math.sin(ang) * d, rnd.uniform(3, 8), rnd.uniform(2, 5), RUST, 0.6, 2)
    a.material("drippan", 0.0, 0.35)
    # metallic only on the rim
    img = a.mimg
    img.select_ellipse(Gimp.ChannelOps.REPLACE, cx - R, cy - R, 2 * R, 2 * R)
    img.select_ellipse(Gimp.ChannelOps.SUBTRACT, cx - R * 0.8, cy - R * 0.8, 1.6 * R, 1.6 * R)
    _fill(a.mlay, (255, 0, 0, 0.7))
    Gimp.Selection.none(img)


def coil(a):
    x, y, w, h = a.rect("coil")
    cx, cy, R = x + w / 2, y + h / 2, w / 2 - 2
    a.fill("coil", (40, 35, 32), 0.0, 0.25)       # pan shadow between the turns
    n = 5
    for i in range(n):
        r1 = R * (1.0 - i * 0.18)
        ring(a.img, a.lay, cx, cy, r1 - R * 0.11, r1, (16, 16, 18), 1.0)
        ring(a.img, a.lay, cx, cy, r1 - R * 0.07, r1 - R * 0.04, (92, 92, 96), 0.55, 1)   # glint along each turn
    # the spiral's crossing and support spokes
    line(a.lay, [cx - R * 0.95, cy, cx - R * 0.2, cy], (22, 22, 24), 6)
    line(a.lay, [cx, cy + R * 0.2, cx, cy + R * 0.95], (40, 38, 36), 4)
    specks(a.img, a.lay, (x, y, w, h), 25, (120, 110, 100), 1, 3, 0.2, 0.5)   # burnt-on crumbs
    a.material("coil", 0.2, 0.3)


def guard(a):
    x, y, w, h = a.rect("guard_face")
    gx0, gx1, gz0, gz1 = C["GUARD_UV"]
    sx, sz = w / (gx1 - gx0), h / (gz1 - gz0)
    px = lambda X: x + (X - gx0) * sx
    pz = lambda Z: y + (gz1 - Z) * sz
    a.fill("guard_face", WHITE, 0.0, 0.7, noise=0.01, blur=1.0)
    grey = (120, 122, 126)
    kz = C["KNOB_Z"]

    def dial(kx, r_in, r_out):
        cx, cy = px(kx), pz(kz)
        for j in range(11):
            ang = math.radians(-135 + 27 * j) - math.pi / 2
            line(a.lay, [cx + math.cos(ang) * r_in * sx, cy + math.sin(ang) * r_in * sz,
                         cx + math.cos(ang) * r_out * sx, cy + math.sin(ang) * r_out * sz], grey, 2)
        fill_rect(a.img, a.lay, (int(cx - 0.35 * sx), int(pz(kz + 1.55)), int(0.7 * sx), int(0.18 * sz)), grey)   # "OFF"
        fill_rect(a.img, a.lay, (int(cx - 0.45 * sx), int(pz(kz - 1.45)), int(0.9 * sx), int(0.16 * sz)), grey)  # label

    for kx in C["KNOBS_X"]:
        dial(kx, 1.15, 1.4)
    # grey panel with display, touch pads, dial ring; its fine print as grey dashes
    px0, px1, pz0, pz1 = C["PANEL"]
    fill_round_rect(a.img, a.lay, (px(px0), pz(pz1), px(px1), pz(pz0)), 10, (182, 184, 186))
    fill_round_rect(a.img, a.lay, (px(px0) + 3, pz(pz1) + 3, px(px1) - 3, pz(pz0) - 3), 8, (192, 194, 196))
    fill_rect(a.img, a.lay, (int(px(-3.6)), int(pz(kz + 0.55)), int(2.6 * sx), int(1.1 * sz)), (16, 18, 16))
    for i in range(2):
        for j in range(2):
            fill_round_rect(a.img, a.lay, (px(-0.6 + i * 0.75), pz(kz + 0.6 - j * 0.7), px(-0.1 + i * 0.75),
                                           pz(kz + 0.15 - j * 0.7)), 3, (160, 162, 166))
    for i in range(4):
        fill_rect(a.img, a.lay, (int(px(-4.9 + i * 2.4)), int(pz(pz1 - 0.35)), int(1.6 * sx), 2), (130, 132, 136))
        fill_rect(a.img, a.lay, (int(px(-4.9 + i * 2.4)), int(pz(pz0 + 0.45)), int(1.8 * sx), 2), (130, 132, 136))
    dial(C["DIAL_X"], 1.0, 1.2)
    blot(a.img, a.lay, px(6.8), pz(kz + 0.2), 0.14 * sx, 0.14 * sz, (160, 30, 28), 1.0)   # indicator
    fill_rect(a.img, a.lay, (int(px(6.3)), int(pz(kz - 0.3)), int(1.0 * sx), 2), grey)
    # parody maker badge under the left knobs
    lg = load(os.path.join(_LOGOS, "grumbleworks.svg"))
    bw = int(1.5 * sx)
    lg.scale(bw, max(4, int(bw * 0.25)))
    add_layer_from(a.img, lg, "badge", int(px(-10.8) - bw / 2), int(pz(H + 1.9)))
    lg.delete()
    a.lay = flatten(a.img)
    # fingerprint smudges around the knobs
    for kx in C["KNOBS_X"] + (C["DIAL_X"],):
        for _ in range(3):
            blot(a.img, a.lay, px(kx + rnd.uniform(-1.5, 1.5)), pz(kz + rnd.uniform(-1.5, 1.0)), rnd.uniform(6, 12),
                 rnd.uniform(4, 9), (180, 176, 164), rnd.uniform(0.1, 0.2), 4)
    # clock: green bars on the emission map and the albedo
    eimg, elay = a.glow_layer()
    for i in range(4):
        gx = px(-3.3 + i * 0.6 + (0.2 if i > 1 else 0))
        for lay_, img_ in ((a.lay, a.img), (elay, eimg)):
            fill_rect(img_, lay_, (int(gx), int(pz(kz + 0.35)), int(0.4 * sx), int(0.7 * sz)), (60, 220, 90))
            fill_rect(img_, lay_, (int(gx + 3), int(pz(kz + 0.35)) + 4, int(0.4 * sx) - 6, int(0.7 * sz) - 8), (16, 18, 16))


def door(a):
    x, y, w, h = a.rect("door_face")
    z0, z1 = C["FRONT_Z"]
    sx, sz = w / W, h / (z1 - z0)
    px = lambda X: x + (X + W / 2) * sx
    pz = lambda Z: y + (z1 - Z) * sz
    a.fill("door_face", WHITE, 0.0, 0.7, noise=0.012, blur=1.0)
    # cream vent band with its slot along the top of the door
    v0, v1 = C["VENT"]
    fill_rect(a.img, a.lay, (x, int(pz(v1)), w, int((v1 - v0) * sz)), CREAM)
    fill_rect(a.img, a.lay, (int(px(-W / 2 + 1.5)), int(pz(v0 + 0.95)), int((W - 3) * sx), max(2, int(0.25 * sz))), (70, 66, 60))
    # window recess: pale grey bezel around the glass
    wz0, wz1, wh = C["WINDOW"]
    img = a.img
    img.select_round_rectangle(Gimp.ChannelOps.REPLACE, px(-wh - 0.6), pz(wz1 + 0.6), (2 * wh + 1.2) * sx,
                               (wz1 - wz0 + 1.2) * sz, 18, 18)
    Gimp.Selection.feather(img, 5)
    _fill(a.lay, (200, 201, 202, 0.9))
    Gimp.Selection.none(img)
    # rust grime along the seam between door and drawer, and at the drawer's top groove
    d0, d1 = C["DRAWER"]
    for Z, al in ((d1 + 0.1, 0.7), (C["DOOR"][0] + 0.1, 0.45)):
        for _ in range(26):
            X = rnd.uniform(-W / 2 + 0.6, W / 2 - 0.6)
            blot(img, a.lay, px(X), pz(Z), rnd.uniform(2, 9), rnd.uniform(0.8, 2.0), RUST, rnd.uniform(0.3, al), 1)
    # specks near the handle brackets and on the band; faint scuffs low on the door
    specks(img, a.lay, (int(px(-13.5)), int(pz(34.6)), int(3 * sx), int(3 * sz)), 10, RUST, 0.8, 2.0, 0.4, 0.8)
    specks(img, a.lay, (int(px(10.5)), int(pz(34.6)), int(3 * sx), int(3 * sz)), 10, RUST, 0.8, 2.0, 0.4, 0.8)
    specks(img, a.lay, (x + 10, int(pz(34.8)), w - 20, int(1.6 * sz)), 25, RUST, 0.6, 1.6, 0.3, 0.7)
    specks(img, a.lay, (x + 20, int(pz(14)), w - 40, int(5 * sz)), 8, (170, 164, 150), 3, 8, 0.15, 0.3)
    specks(img, a.lay, (x + 20, int(pz(8)), w - 40, int(6 * sz)), 10, (160, 150, 134), 2, 7, 0.15, 0.3)


def glass(a):
    x, y, w, h = a.rect("glass")
    a.fill("glass", (200, 201, 202), 0.0, 0.85)
    fill_round_rect(a.img, a.lay, (x + 4, y + 4, x + w - 4, y + h - 4), 22, (108, 110, 114))
    fill_round_rect(a.img, a.lay, (x + 14, y + 12, x + w - 14, y + h - 12), 16, (96, 98, 102))
    # a pale top-edge sheen, as in the photos
    img = a.img
    img.select_round_rectangle(Gimp.ChannelOps.REPLACE, x + 16, y + 12, w - 32, 22, 10, 10)
    Gimp.Selection.feather(img, 8)
    _fill(a.lay, (150, 152, 156, 0.5))
    Gimp.Selection.none(img)


def handle(a):
    x, y, w, h = a.rect("handle")
    a.fill("handle", (228, 222, 204), 0.0, 0.55, noise=0.015, blur=1.0)
    specks(a.img, a.lay, (x + 4, y + 4, w - 8, h - 8), 30, RUST, 0.6, 1.8, 0.35, 0.8)
    specks(a.img, a.lay, (x + 4, y + 4, w - 8, h - 8), 6, (190, 176, 150), 5, 12, 0.2, 0.35)


def build():
    a = Atlas(ATLAS)
    cooktop(a)
    drippan(a)
    coil(a)
    guard(a)
    door(a)
    glass(a)
    handle(a)
    a.fill("enamel", WHITE, 0.0, 0.7, noise=0.01, blur=1.0)
    a.fill("knob", (238, 238, 234), 0.0, 0.5)
    a.fill("chrome", (196, 198, 200), 0.6, 0.6, noise=0.03, blur=0.5)
    a.fill("trim_black", (28, 28, 30), 0.0, 0.4)
    fill_rect(a.img, a.lay, (0, 832, 1024, 192), (128, 128, 128))   # unused
    a.save()
