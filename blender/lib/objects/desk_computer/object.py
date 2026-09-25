"""Desk computer set: a black mid-tower PC (tinted glass side, diagonal green LED strip on
the front, faint interior glow), two black-bezel monitors on stands, an open laptop at
the far end, keyboard, mouse on a patterned pad, a small six-key button pad and a webcam
on the west monitor. Screens are plain dark glass (own material desk_computer_screen).

Built in the DESK's local frame so it shares the desk's placement: origin on the floor
at the desk footprint centre, desk front faces -Y, desk top at z 29.5. In the room:
plan (175.4, 14.5), rotation 180 (local +X = world west, local -Y = world north).
World -> local: lx = 175.4 - wx, ly = 14.5 - wy.
"""

import math

from mathutils import Matrix

import common

IN = 0.0254


def m(v):
    return v * IN


TOP = 29.5                       # desk top (desk package)
TOWER_C = (24.4, -2.5)           # SCAN tower world (151, 17)
TOWER = (9.0, 18.0, 19.0)        # SCAN w, d, h (world x 142..160 incl. noise, top z ~48.5)
MON_W, MON_H, MON_T = 21.4, 12.8, 0.7   # EST 24 in 16:9 panels; SCAN screens x 157.5..198, z 37..49
MON_Z0 = 36.3                    # SCAN bottom of panels
MON_CX = (8.1, -12.4)            # SCAN world x 167.3, 187.8
MON_Y = 5.0                      # SCAN panel plane at world y ~9.5
MON_TOE = 7.0                    # EST degrees each monitor turns toward the middle
BEZEL = 0.35                     # EST
LAPTOP_C = (-30.1, 1.5)          # SCAN/A east end, world (205.5, 13)
LAPTOP = (13.5, 9.2, 0.7)        # EST 14 in laptop base
LID_T, LID_ANG = 0.25, 108.0     # EST
KB_C = (-14.6, -5.5)             # PHOTO keyboard east of the mouse pad, world (190, 20)
KB = (17.3, 5.4, 1.0)            # EST full-size keyboard
PAD_C = (2.9, -4.0)              # SCAN splat: light patch x 167.5..177, y 14.4..22.4 -> world (172.5, 18.5)
PAD = (9.25, 7.75, 0.12)         # PHOTO aspect 1.19-1.21 (rectified) = standard 9.25 x 7.75 pad; SCAN ~9.5 x 8
PAD_R = 0.85                     # PHOTO rounded corners
DECK_C = (9.4, -6.5)             # PHOTO small button pad, world (166, 21)

NAME = "desk_computer"
ATLAS = {
    "name": "desk_computer",
    "size": 1024,
    "regions": {
        "black": (0, 0, 128, 128),
        "tower_front": (128, 0, 128, 256),
        "tower_glass": (256, 0, 128, 256),
        "keyboard": (0, 256, 256, 128),
        "mousepad": (512, 0, 512, 430),
        "spare": (384, 0, 128, 128),
        "deck": (384, 128, 128, 128),
        "vent": (0, 128, 128, 128),
        "grey": (256, 256, 128, 128),
        "laptop": (384, 256, 128, 128),
        "screen": (0, 384, 128, 128),
    },
}
SCREEN_ATLAS = {"name": "desk_computer_screen", "size": 256, "regions": {"screen": (0, 0, 256, 256)}}
REGIONS = list(ATLAS["regions"])
MATERIALS = {
    "desk_computer": {"atlas": "desk_computer", "mode": "opaque", "tiled": False},
    "desk_computer_screen": {"atlas": "desk_computer_screen", "mode": "opaque", "tiled": False},
}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front_r", 25, 22, 0.7), ("photo_front_l", 340, 30, 0.75), ("tower_close", 30, 12, 0.45)]


def _local(cx, cy, ang_deg, z=0.0):
    return Matrix.Translation((m(cx), m(cy), m(z))) @ Matrix.Rotation(math.radians(ang_deg), 4, "Z")


def build(coll):
    b = common.Builder(REGIONS)

    def bx(r, a, c, bev=0.0, mat=None, seg=1):
        return b.box(r, tuple(map(m, a)), tuple(map(m, c)), bevel=m(bev), segments=seg, matrix=mat)

    # --- PC tower: front faces -Y (world north), glass on -X (world east)
    tx, ty = TOWER_C
    w, d, h = TOWER
    x0, x1, y0, y1 = tx - w / 2, tx + w / 2, ty - d / 2, ty + d / 2
    bx("black", (x0 + 0.1, y0 + 0.8, TOP + 0.6), (x1, y1, TOP + h), 0.15)          # body
    bx("tower_glass", (x0, y0 + 1.2, TOP + 1.0), (x0 + 0.12, y1 - 0.4, TOP + h - 0.4))  # glass side
    bx("tower_front", (x0, y0, TOP + 0.6), (x1, y0 + 0.8, TOP + h), 0.12)          # front panel
    for sx in (x0 + 1.0, x1 - 1.0):                                                 # feet
        for sy in (y0 + 1.5, y1 - 1.5):
            bx("black", (sx - 0.7, sy - 1.0, TOP), (sx + 0.7, sy + 1.0, TOP + 0.6))
    bx("vent", (x0 + 1.2, y0 + 3.0, TOP + h), (x1 - 1.0, y1 - 2.0, TOP + h + 0.05))  # top mesh

    # --- monitors: panel + back hump + neck + base, toe-in toward the middle
    for i, cx in enumerate(MON_CX):
        ang = -MON_TOE if cx > 0 else MON_TOE
        M = _local(cx, MON_Y, ang)
        z0 = MON_Z0
        bx("black", (-MON_W / 2, -MON_T / 2, z0), (MON_W / 2, MON_T / 2, z0 + MON_H), 0.08, M)
        bx("screen", (-MON_W / 2 + BEZEL, -MON_T / 2 - 0.03, z0 + BEZEL + 0.35),
           (MON_W / 2 - BEZEL, -MON_T / 2, z0 + MON_H - BEZEL), 0.0, M)
        bx("black", (-7.0, MON_T / 2, z0 + 2.5), (7.0, MON_T / 2 + 1.3, z0 + 10.0), 0.4, M)   # hump
        bx("black", (-1.2, MON_T / 2 + 1.3, TOP + 0.4), (1.2, MON_T / 2 + 2.1, z0 + 8.0), 0.2, M)  # neck
        bx("black", (-4.5, -2.8, TOP), (4.5, 4.2, TOP + 0.4), 0.25, M)                        # base
        if cx > 0:   # webcam on the west monitor
            bx("black", (-1.8, -0.9, z0 + MON_H), (1.8, 0.5, z0 + MON_H + 1.1), 0.3, M)
            bx("black", (-0.8, -0.2, z0 + MON_H - 1.4), (0.8, 1.2, z0 + MON_H), 0.0, M)

    # --- laptop: base + lid hinged at the back edge, opened LID_ANG
    lx, ly = LAPTOP_C
    lw, ld, lh = LAPTOP
    M = _local(lx, ly, 0.0)
    bx("laptop", (-lw / 2, -ld / 2, TOP), (lw / 2, ld / 2, TOP + lh), 0.15, M)
    bx("grey", (-lw / 2 + 0.8, -ld / 2 + 3.2, TOP + lh), (lw / 2 - 0.8, ld / 2 - 0.6, TOP + lh + 0.02), 0.0, M)
    H = M @ Matrix.Translation((0, m(ld / 2), m(TOP + lh))) @ Matrix.Rotation(math.radians(LID_ANG - 90.0), 4, "X")
    lid_h = ld - 0.3
    bx("laptop", (-lw / 2, 0.0, 0.0), (lw / 2, LID_T, lid_h), 0.08, H)
    bx("screen", (-lw / 2 + 0.5, -0.03, 0.5), (lw / 2 - 0.5, 0.0, lid_h - 0.4), 0.0, H)

    # --- keyboard, mouse pad + mouse, button pad
    kx, ky = KB_C
    kw, kd, kh = KB
    bx("black", (kx - kw / 2, ky - kd / 2, TOP), (kx + kw / 2, ky + kd / 2, TOP + 0.55), 0.15)
    bx("keyboard", (kx - kw / 2 + 0.3, ky - kd / 2 + 0.3, TOP + 0.55), (kx + kw / 2 - 0.3, ky + kd / 2 - 0.3, TOP + kh), 0.05)
    px, py = PAD_C
    pw, pd, ph = PAD
    b.prism("mousepad", [(m(x), m(y)) for x, y in common.rounded_rect(px, py, pw, pd, PAD_R, 4)],
            m(TOP), m(TOP + ph))
    mz = TOP + ph
    bx("black", (px - 1.2, py - 2.4, mz), (px + 1.2, py + 2.2, mz + 1.35), 0.55, None, 2)
    dx, dy = DECK_C
    bx("black", (dx - 1.7, dy - 1.5, TOP), (dx + 1.7, dy + 1.5, TOP + 0.9), 0.2)
    bx("deck", (dx - 1.35, dy - 1.15, TOP + 0.9), (dx + 1.35, dy + 1.15, TOP + 0.95))
    return [b.to_object(NAME, coll)]


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    smat = common.atlas_material("desk_computer_screen", SCREEN_ATLAS)
    tower_c = TOWER_C
    w, d, h = TOWER
    pad = PAD
    planar = {
        # front seen from -Y: u = +x, v = z
        "tower_front": ("-Y", (m(tower_c[0] - w / 2), m(tower_c[0] + w / 2)), (m(TOP + 0.6), m(TOP + h))),
        # glass seen from -X: u runs -y
        "tower_glass": ("-X", (m(-(tower_c[1] + d / 2)), m(-(tower_c[1] - d / 2))), (m(TOP + 0.6), m(TOP + h))),
        "keyboard": ("+Z", (m(KB_C[0] - KB[0] / 2), m(KB_C[0] + KB[0] / 2)), (m(KB_C[1] - KB[1] / 2), m(KB_C[1] + KB[1] / 2))),
        "mousepad": ("+Z", (m(PAD_C[0] - pad[0] / 2), m(PAD_C[0] + pad[0] / 2)), (m(PAD_C[1] - pad[1] / 2), m(PAD_C[1] + pad[1] / 2))),
        "deck": ("+Z", (m(DECK_C[0] - 1.35), m(DECK_C[0] + 1.35)), (m(DECK_C[1] - 1.15), m(DECK_C[1] + 1.15))),
    }
    common.atlas_uvs(ob, ATLAS, planar=planar)
    common.collapse_materials(ob, {r: (smat if r == "screen" else mat) for r in REGIONS})
