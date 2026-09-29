"""wall_plates atlas (512): glossy white plate plastic, plate faces drawn at true scale
(duplex receptacles, toggle openings, decora GFCI with TEST/RESET, 2- and 3-gang toggle
plates, the 2-gang toggle + GFCI combo), the line-voltage thermostat's face (dark window
with a slider), the wall smoke alarm's vented face, and the breaker panel cover in the
wall paint colour (corner screws, inner door groove, latch). No text, no brands.
Runs inside headless GIMP with the gimp_textures helpers in scope."""

ATLAS = {
    "name": "wall_plates",
    "size": 512,
    "regions": {
        "face_duplex": (0, 0, 64, 104),
        "face_toggle1": (64, 0, 64, 104),
        "face_gfci": (128, 0, 64, 104),
        "face_combo": (192, 0, 108, 104),
        "face_toggle2": (300, 0, 108, 104),
        "plate_white": (408, 0, 48, 48),
        "wall_paint": (456, 0, 48, 48),
        "dark": (408, 48, 32, 32),
        "lever": (440, 48, 32, 32),
        "metal": (472, 48, 32, 32),
        "almond": (408, 80, 32, 28),
        "face_toggle3": (0, 112, 152, 104),
        "face_thermo": (160, 112, 72, 104),
        "face_smoke": (240, 112, 88, 120),
        "face_panel": (336, 112, 176, 323),
    },
}

# region -> item size in inches (w, h), matching object.py
SIZE = {"face_duplex": (2.75, 4.5), "face_toggle1": (2.75, 4.5), "face_gfci": (2.75, 4.5),
        "face_combo": (4.56, 4.5), "face_toggle2": (4.56, 4.5), "face_toggle3": (6.375, 4.5),
        "face_thermo": (3.7, 4.8), "face_smoke": (4.25, 5.75), "face_panel": (15.25, 28.0)}

WHITE = (241, 239, 233)
IVORY = (236, 233, 223)
SLOT = (38, 36, 34)
SCREW = (196, 194, 186)
SHADE = (214, 211, 203)
PAINT = (206, 200, 191)          # shell_walls colour
PITCH = 1.8125                   # gang spacing


def P(a, reg, u, v):
    """Local inches (u right, v up, from the item centre) -> atlas pixel."""
    x, y, w, h = a.rect(reg)
    W, H = SIZE[reg]
    return x + (u + W / 2) / W * w, y + (H / 2 - v) / H * h


def box(a, reg, u0, v0, u1, v1, rgb, r=0):
    x0, y1 = P(a, reg, u0, v0)
    x1, y0 = P(a, reg, u1, v1)
    x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
    if r:
        fill_round_rect(a.img, a.lay, (x0, y0, x1, y1), r, rgb)
    else:
        fill_rect(a.img, a.lay, (x0, y0, max(1, x1 - x0), max(1, y1 - y0)), rgb)


def dot(a, reg, u, v, d, rgb):
    x, y = P(a, reg, u, v)
    pw = a.rect(reg)[2] / SIZE[reg][0] * d / 2
    fill_ellipse(a.img, a.lay, (round(x - pw), round(y - pw), round(x + pw), round(y + pw)), rgb)


def plate(a, reg):
    a.fill(reg, WHITE, 0.0, 0.62, noise=0.006)
    x, y, w, h = a.rect(reg)
    # a soft darker rim where the plate's edge rolls toward the wall
    fill_rect(a.img, a.lay, (x, y, w, 1), SHADE)
    fill_rect(a.img, a.lay, (x, y + h - 1, w, 1), SHADE)
    fill_rect(a.img, a.lay, (x, y, 1, h), SHADE)
    fill_rect(a.img, a.lay, (x + w - 1, y, 1, h), SHADE)


def receptacle(a, reg, u, v, scale=1.0):
    """One NEMA 5-15 face: rounded body, neutral (left, taller) and hot slots, ground below."""
    box(a, reg, u - 0.66 * scale, v - 0.6 * scale, u + 0.66 * scale, v + 0.6 * scale, SHADE, r=6)
    box(a, reg, u - 0.62 * scale, v - 0.56 * scale, u + 0.62 * scale, v + 0.56 * scale, IVORY, r=5)
    box(a, reg, u - 0.30 * scale, v - 0.10 * scale, u - 0.22 * scale, v + 0.32 * scale, SLOT)
    box(a, reg, u + 0.22 * scale, v - 0.05 * scale, u + 0.30 * scale, v + 0.28 * scale, SLOT)
    dot(a, reg, u, v - 0.33 * scale, 0.2 * scale, SLOT)


def toggle_opening(a, reg, u):
    box(a, reg, u - 0.2, -0.47, u + 0.2, 0.47, (226, 223, 214))
    box(a, reg, u - 0.17, -0.44, u + 0.17, 0.44, (205, 202, 192))
    dot(a, reg, u, 1.19, 0.17, SCREW)
    dot(a, reg, u, -1.19, 0.17, SCREW)


def gfci(a, reg, u):
    """Decora GFCI in its rectangular opening: two small receptacles, TEST (red) and RESET."""
    box(a, reg, u - 0.66, -1.31, u + 0.66, 1.31, SHADE)
    box(a, reg, u - 0.62, -1.27, u + 0.62, 1.27, IVORY)
    for v in (0.8, -0.8):
        box(a, reg, u - 0.30, v - 0.05, u - 0.23, v + 0.30, SLOT)
        box(a, reg, u + 0.23, v - 0.02, u + 0.30, v + 0.26, SLOT)
        dot(a, reg, u, v - 0.23, 0.16, SLOT)
    box(a, reg, u - 0.26, 0.02, u + 0.26, 0.30, (178, 42, 38), r=2)     # TEST
    box(a, reg, u - 0.26, -0.32, u + 0.26, -0.04, (44, 42, 40), r=2)    # RESET
    dot(a, reg, u, 1.9, 0.17, SCREW)
    dot(a, reg, u, -1.9, 0.17, SCREW)


def build():
    a = Atlas(ATLAS)
    a.fill("plate_white", WHITE, 0.0, 0.62, noise=0.006)
    a.fill("wall_paint", PAINT, 0.0, 0.18, noise=0.015)
    a.fill("dark", (34, 34, 36), 0.0, 0.5)
    a.fill("lever", IVORY, 0.0, 0.6)
    a.fill("metal", (150, 150, 146), 0.6, 0.45, noise=0.02)

    plate(a, "face_duplex")
    receptacle(a, "face_duplex", 0.0, 0.76, 1.15)
    receptacle(a, "face_duplex", 0.0, -0.76, 1.15)
    dot(a, "face_duplex", 0.0, 0.0, 0.17, SCREW)

    for reg, n in (("face_toggle1", 1), ("face_toggle2", 2), ("face_toggle3", 3)):
        plate(a, reg)
        for k in range(n):
            toggle_opening(a, reg, (k - (n - 1) / 2) * PITCH)

    plate(a, "face_gfci")
    gfci(a, "face_gfci", 0.0)

    plate(a, "face_combo")
    toggle_opening(a, "face_combo", -PITCH / 2)
    gfci(a, "face_combo", PITCH / 2)

    # line-voltage thermostat: white body, recessed dark window right of centre, slider slot
    a.fill("face_thermo", WHITE, 0.0, 0.5, noise=0.006)
    box(a, "face_thermo", -0.30, -1.55, 1.20, 1.35, (190, 188, 182))
    box(a, "face_thermo", -0.22, -1.47, 1.12, 1.27, (52, 53, 55))
    box(a, "face_thermo", -0.10, -1.35, 1.00, 1.15, (40, 41, 43))
    box(a, "face_thermo", 0.40, -1.1, 0.50, 0.9, (22, 22, 24))            # slider slot

    # wall smoke alarm: almond (aged) housing, a vent grille of short slots, two screws
    ALM = (216, 203, 166)
    a.fill("almond", (210, 197, 160), 0.0, 0.4, noise=0.01)
    a.fill("face_smoke", ALM, 0.0, 0.4, noise=0.01)
    box(a, "face_smoke", -1.25, -1.5, 1.25, 1.5, (206, 192, 154), r=3)
    for k in range(10):
        v = -1.3 + k * 0.28
        box(a, "face_smoke", -0.9, v, 0.9, v + 0.1, (150, 138, 108))
    dot(a, "face_smoke", 0.0, 2.25, 0.22, (170, 160, 128))
    dot(a, "face_smoke", 0.0, -2.25, 0.22, (170, 160, 128))

    # breaker panel cover, painted with the walls: bevelled rim, corner screws, door groove,
    # latch recess (the latch itself is geometry)
    a.fill("face_panel", PAINT, 0.0, 0.2, noise=0.012)
    x, y, w, h = a.rect("face_panel")
    fill_rect(a.img, a.lay, (x, y, w, 2), (186, 180, 171))
    fill_rect(a.img, a.lay, (x, y + h - 2, w, 2), (176, 170, 161))
    fill_rect(a.img, a.lay, (x, y, 2, h), (184, 178, 169))
    fill_rect(a.img, a.lay, (x + w - 2, y, 2, h), (180, 174, 165))
    for u in (-6.95, 6.95):
        for v in (-13.0, 13.0):
            dot(a, "face_panel", u, v, 0.35, (170, 165, 156))
            dot(a, "face_panel", u, v, 0.2, (190, 185, 176))
    # door groove (the door is a thin raised box; its face samples the inside of this)
    box(a, "face_panel", -4.2, -10.45, 4.2, 10.45, (168, 162, 153))
    box(a, "face_panel", -4.0, -10.25, 4.0, 10.25, (204, 198, 189))
    box(a, "face_panel", -3.1, 0.35, -1.7, 1.65, (160, 154, 146))
    a.save()
