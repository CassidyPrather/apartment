"""media_hutch layout: dimensions, every shelf item, and the two atlas layouts.

Shared by object.py (Blender) and textures.py (GIMP), so the atlas regions and the geometry
agree. Pure Python, no bpy/Gimp imports.

Frame: the hutch's own frame in INCHES. Origin on the floor at the footprint centre, front
faces -Y, +X is the hutch's right as seen from the front (plan south once placed), -X its
left (plan north: the side panel that faces the room, with the chart and the print).

Provenance tags: SCAN (living-room LiDAR survey), PHOTO (measured in IMG_1506/1507/1508 at
~25.5 px/in on the shelf-contents plane, ~28 px/in at the crown), SPEC (published size of the
standard item), EST (judged).
"""

import math
import random

# --- carcass ------------------------------------------------------------------------------
W = 31.0            # SCAN side panels at y 2.5 and 33.0 in the LiDAR
D = 18.5            # SCAN face frame x 116.8 to the wall
H = 79.5            # SCAN side top ~76-80; PHOTO crown 4.5 in over the valance
BASE_H = 4.0        # EST plinth
LOWER_TOP = 24.75   # PHOTO/SCAN lower doors top (drawer band above)
RAIL_TOP = 31.0     # SCAN bottom bay floor (top of the drawer band)
SHELVES = (44.0, 57.5)   # SCAN shelf tops (bay 2 floor, bay 1 floor)
VAL_TOP = 75.0      # PHOTO valance board top / crown bottom
STILE = 2.0         # PHOTO face-frame stile width
SIDE_T = 0.75       # EST
DOOR_T = 0.75       # EST
DOOR_LATCH_DOWN = 6.0  # PHOTO (capture frames 003528/003541): latch plates ~1/3 down the doors
X0, X1 = -W / 2, W / 2
Y0, Y1 = -D / 2, D / 2
FY = Y0 + 0.75                    # carcass front (behind the face frame)
IX0, IX1 = X0 + STILE, X1 - STILE  # face-frame opening
INX0, INX1 = X0 + SIDE_T, X1 - SIDE_T   # inside faces of the side panels
BACK_Y = Y1 - 0.5                 # front face of the back panel

# Scalloped valance lower edge, right half, (x from centre, depth below VAL_TOP). PHOTO
# (IMG_1506 arch crop, 47.2 crop px/in): a small point at the centre, a hump each side,
# a little hook at x 7, then a long sweep down to the springs at the stiles.
ARCH_HALF = [(0.0, 3.5), (0.7, 3.3), (1.33, 3.07), (2.8, 2.65), (4.7, 2.44), (5.7, 2.52),
             (6.4, 2.75), (6.85, 3.05), (7.0, 3.28), (7.4, 3.6), (8.4, 3.85), (9.5, 4.13),
             (10.6, 4.65), (11.6, 5.4), (12.4, 6.0), (13.1, 6.57), (13.5, 6.7)]


def arch_points():
    """Full arch lower edge left to right as (x, z)."""
    right = [(x, VAL_TOP - d) for x, d in ARCH_HALF]
    left = [(-x, z) for x, z in reversed(right[1:])]
    return left + right


# --- shelf items --------------------------------------------------------------------------
# Game boxes: id -> (x0, x1, y0, y1, z0, h, yaw_deg, art_faces, colour, parody title)
#   art_faces: faces that carry painted box art ("mY" front, "mX" the -X end, "pZ" top).
#   Every other face gets the flat colour.  Positions PHOTO (IMG_1506 at 25.5 px/in, centre
#   x 545 px); depths EST from the usual box sizes.
B1, B2, B3 = SHELVES[1], SHELVES[0], RAIL_TOP
TOP = H

BOXES = {
    # bay 1 (top bay, under the arch), right-hand stack
    "mage_night":    (0.7, 14.3, -8.0, 2.4, B1, 3.5, 0.0, ("mY",), (120, 52, 38)),
    "avaloaf":       (1.7, 7.55, -7.8, -1.8, B1 + 3.5, 2.0, 1.5, ("mY",), (120, 116, 104)),
    "one_desk":      (7.6, 12.8, -7.7, -2.4, B1 + 3.5, 1.95, -1.0, ("mY",), (52, 54, 56)),
    "mascarpone":    (3.45, 7.55, -7.6, -2.4, B1 + 5.5, 1.6, 0.8, ("mY",), (112, 34, 36)),
    "maidens_quiche": (7.6, 12.45, -7.5, -3.9, B1 + 5.45, 1.75, 0.0, ("mY",), (150, 180, 206)),
    "dunno_now":     (2.25, 9.3, -6.6, 0.6, B1 + 7.2, 1.4, -1.2, ("mY",), (34, 44, 50)),
    "hula_hooper":   (2.25, 14.05, -7.8, 0.7, B1 + 8.6, 1.8, 0.6, ("mY",), (30, 30, 34)),
    # bay 2, left stack (spiral notebook and papers on top are separate)
    "sloths":        (-12.7, -3.15, -4.5, 5.5, B2, 1.8, 0.0, ("mY",), (28, 28, 30)),
    "sushi_no":      (-12.75, -3.15, -4.4, 5.5, B2 + 1.8, 2.4, -0.6, ("mY",), (200, 50, 44)),
    "tragic_maze":   (-12.8, -3.85, -4.6, 5.4, B2 + 4.2, 2.5, 0.8, ("mY",), (236, 234, 228)),
    "plain_black":   (-12.8, -5.6, -4.0, 5.0, B2 + 6.7, 1.2, 0.0, (), (24, 24, 26)),
    "exit_ish":      (-10.8, -5.75, -7.9, -6.2, B2, 6.9, -3.0, ("mY",), (22, 30, 46)),
    # bay 2, right stack (bottom to top) and the tarot deck standing in front
    "deceptiscone":  (3.3, 13.1, -4.8, 4.2, B2, 1.8, 0.0, ("mY",), (104, 30, 28)),
    "sidereal":      (2.85, 13.05, -4.9, 5.6, B2 + 1.8, 2.6, 0.7, ("mY",), (26, 30, 52)),
    "dixit_didnt":   (3.2, 12.9, -4.7, 6.8, B2 + 4.4, 2.0, -0.5, ("mY",), (204, 170, 110)),
    "raptoast":      (3.8, 13.8, -4.6, 3.4, B2 + 6.4, 2.7, 0.9, ("mY",), (96, 112, 48)),
    "valiant_snores": (3.05, 10.4, -4.5, 3.5, B2 + 9.1, 2.9, -0.8, ("mY",), (190, 120, 50)),
    "mild_tarot":    (9.95, 13.2, -7.4, -5.8, B2, 5.4, -4.0, ("mY",), (20, 20, 22)),
    # bay 3 (bottom bay), left stack under the magazines
    "quinoa":        (-11.95, -1.75, -2.9, 8.6, B3, 2.3, 0.0, ("mY",), (232, 226, 206)),
    "mellow_yawnzee": (-12.2, -1.75, -2.8, 8.6, B3 + 2.3, 2.6, 0.7, ("mY",), (200, 190, 80)),
    "tigers":        (-12.3, -1.75, -2.9, 8.6, B3 + 4.9, 2.3, -0.6, ("mY",), (46, 70, 118)),
    # bay 3, right: wooden organiser box, then the three town boxes on it
    "spirit_eyeland": (3.4, 12.7, -3.6, 5.6, B3, 5.8, 0.0, ("mY",), (214, 188, 150)),
    "frowns_villains": (2.8, 12.8, -3.9, 6.1, B3 + 5.8, 1.4, 0.4, ("mY",), (60, 70, 60)),
    "tiny_frowns":   (2.75, 12.8, -3.9, 6.6, B3 + 7.2, 2.5, -0.3, ("mY",), (110, 160, 190)),
    "frowns_fortune": (3.0, 12.4, -2.6, 6.8, B3 + 9.7, 0.9, 0.5, ("mY",), (70, 110, 60)),
    # on top of the hutch (IMG_1507/1508, ~28 px/in at the crown)
    "pink_box":      (-14.3, -3.6, -9.8, -2.3, TOP, 3.0, 0.0, (), (214, 140, 120)),
    "battletuck":    (-16.3, -3.0, -10.4, -1.9, TOP + 3.0, 3.0, 0.0, ("mY", "mX"), (24, 24, 28)),
    "decent":        (-13.6, -1.0, -1.6, 9.2, TOP, 3.4, 0.0, ("mX", "mY"), (24, 40, 64)),
    "soup_bowl":     (-14.2, -1.8, -1.2, 9.3, TOP + 3.4, 3.0, 3.0, ("mX", "mY"), (20, 20, 22)),
    "gold_triangle": (-0.6, 3.0, 0.8, 9.0, TOP, 4.8, 0.0, ("mY",), (18, 18, 20)),
    "clutter_splash": (2.3, 14.1, -9.2, -0.9, TOP + 2.75, 3.6, 0.8, ("mY",), (60, 40, 80)),
    "clutter_tubs":  (2.1, 13.6, -9.3, -1.0, TOP + 6.35, 3.6, -1.2, ("mY",), (40, 50, 110)),
    "clutter_snax":  (1.8, 12.9, -9.1, -0.8, TOP + 9.95, 3.5, 2.0, ("mY",), (46, 40, 90)),
    "clutter_lunch": (3.2, 12.0, -8.4, -1.6, TOP + 13.45, 2.0, -0.8, ("mY",), (30, 34, 70)),
}

# Upright books: id -> (x0, x1, spine_y, depth, z0, h, colour, lean_deg)
#   spine_y = the front (spine) face; the book runs back from there.  PHOTO widths/heights.
BOOKS = {
    # bay 1, left group behind the masks
    "sherapy":        (-14.65, -13.3, 3.0, 5.5, B1, 8.2, (176, 170, 206), 0),
    "noodles":        (-13.28, -12.3, 2.6, 6.0, B1, 8.8, (236, 234, 230), 0),
    "grey_small":     (-12.28, -11.5, 2.6, 6.0, B1, 9.1, (150, 150, 152), 0),
    "grey_hidden":    (-11.45, -9.65, 1.0, 7.5, B1, 9.5, (60, 58, 60), 0),
    "damp_1":         (-9.6, -8.75, 0.3, 8.3, B1, 11.2, (22, 22, 24), 0),
    "damp_2":         (-8.73, -7.84, 0.3, 8.3, B1, 11.2, (22, 22, 24), 0),
    "damp_3":         (-7.8, -6.88, 0.3, 8.3, B1, 11.2, (22, 22, 24), 0),
    "thin_dark":      (-6.84, -6.52, 0.6, 8.0, B1, 11.3, (30, 30, 34), 0),
    "feelings":       (-6.04, -5.58, 3.6, 5.0, B1, 6.5, (210, 208, 200), 0),
    "tidies":         (-5.3, -4.36, 2.6, 6.0, B1, 8.8, (40, 70, 140), 0),
    "hatfull":        (-4.34, -3.62, 2.6, 6.0, B1, 8.8, (70, 50, 110), 0),
    "cods":           (-3.6, -2.8, 2.6, 6.0, B1, 8.7, (34, 36, 48), 0),
    "crowbar":        (-2.78, -2.32, 3.4, 5.2, B1, 7.6, (40, 40, 42), 0),
    "eleanor":        (-2.3, -1.66, 3.4, 5.2, B1, 7.7, (26, 26, 28), 0),
    "sofa":           (-1.64, -1.44, 3.4, 5.2, B1, 7.7, (60, 52, 44), 0),
    "pheasants":      (-1.42, -0.78, 3.1, 5.5, B1, 8.0, (30, 40, 90), 0),
    "weekend":        (-0.76, 0.5, 2.1, 6.5, B1, 9.1, (22, 22, 22), 0),
    "thin_orange":    (0.52, 0.76, 2.4, 6.2, B1, 9.0, (210, 110, 50), 4),
    "thin_red":       (0.78, 1.02, 2.4, 6.2, B1, 9.0, (170, 40, 44), 5),
    "thin_blue":      (1.04, 1.3, 2.4, 6.2, B1, 9.1, (50, 80, 160), 6),
    # bay 2, between the left stack and the lamp
    "blue_one":       (-3.3, -2.88, 2.4, 6.0, B2, 8.8, (120, 150, 190), 0),
    "navy_plain":     (-2.86, -2.48, 2.4, 6.0, B2, 8.8, (30, 36, 70), 0),
    "armadillo":      (-2.46, -1.66, 2.4, 6.0, B2, 8.5, (232, 232, 228), 0),
    "prune":          (-1.64, -0.56, 2.6, 5.0, B2, 8.0, (196, 170, 120), 0),
    "leviathin":      (-0.54, 0.6, 2.6, 5.6, B2, 8.0, (20, 20, 22), 0),
    # bay 3, right of the left stack
    "squeal_21":      (-1.45, 0.18, -0.6, 7.4, B3, 9.2, (24, 24, 26), 0),
    "squeal_ref":     (0.2, 1.08, -0.2, 7.0, B3, 8.2, (28, 28, 30), 0),
    "house_leeks":    (2.1, 3.3, -6.0, 7.6, B3, 10.0, (238, 238, 234), 0),
}

# Parody names for the ledger / report, id -> (parody title, object description)
PARODY = {
    "mage_night": "Mage Night-Light", "avaloaf": "Avaloaf", "one_desk": "One Desk Dungeon",
    "mascarpone": "Mascarpone", "maidens_quiche": "Maiden's Quiche", "dunno_now": "Dunno Now",
    "hula_hooper": "Tragedy Hula-Hooper", "sloths": "SLOTHS", "sushi_no": "Sushi No-Party",
    "tragic_maze": "Tragic Maze", "exit_ish": "EXIT-ish: The Professor's Lost Keys",
    "deceptiscone": "Deceptiscone", "sidereal": "Sidereal Confusion",
    "dixit_didnt": "Dixit Didn't", "raptoast": "Raptoast", "valiant_snores": "Valiant Snores",
    "mild_tarot": "The Mild Unknown Tarot", "quinoa": "Quinoa",
    "mellow_yawnzee": "Mellow & Yawnzee", "tigers": "Tigers & Euphemisms",
    "spirit_eyeland": "Spirit Eyeland", "frowns_villains": "Tiny Frowns: Villain-agers",
    "tiny_frowns": "Tiny Frowns", "frowns_fortune": "Tiny Frowns: Fortune Cookie",
    "battletuck": "Battletuck", "decent": "Decent: Journeys in the Mildly Dim",
    "soup_bowl": "Blood Bowl of Soup", "clutter_splash": "Iconoclutter: Castle Splash",
    "clutter_tubs": "Iconoclutter: Bathtubgrounds", "clutter_snax": "Iconoclutter: Level Snax",
    "clutter_lunch": "Iconoclutter: Lunch Break",
}

# Paper on the north (-X) side panel. Chart PHOTO position (IMG_1508 at ~32 px/in and the
# survey crops), letter size SPEC; the print sheet PHOTO 6.25 x 9.5 (EST +-0.3).
CHART = (-4.6, 3.9, 63.0, 74.0)      # y0, y1, z0, z1 (on the -X face)
PRINT = (-3.45, 2.8, 50.5, 60.0)

# --- atlases ------------------------------------------------------------------------------
PPI = 32            # px per inch for box fronts and spines
ATLAS_SIZE = 2048
FIXED = [
    ("wood", 512, 1024), ("wood_dark", 256, 512), ("interior", 256, 256),
    ("chart", 408, 528), ("paper_news", 256, 192), ("magazines", 256, 256),
    ("notebook", 256, 192), ("lamp", 256, 256), ("straw", 256, 256),
    ("aluminium", 256, 128), ("pink_weave", 256, 128), ("mask_face", 256, 128),
    ("feather_blue", 64, 256), ("feather_red", 64, 256), ("feather_light", 64, 192),
    ("half_mask", 128, 64), ("postcard", 128, 96), ("wood_edge", 64, 256),
    ("battery", 64, 32), ("critter", 64, 64), ("brass", 32, 32), ("chrome", 32, 32),
    ("glass", 16, 16), ("black", 16, 16), ("white", 16, 16), ("paper_cream", 16, 16),
    ("wire", 16, 16), ("spider_red", 16, 16), ("paper_white", 16, 16), ("gold", 16, 16),
]


def _face_px(box, face):
    x0, x1, y0, y1, z0, h = box[:6]
    wx, wy = x1 - x0, y1 - y0
    w, hh = {"mY": (wx, h), "mX": (wy, h), "pZ": (wx, wy)}[face]
    return max(8, round(w * PPI)), max(8, round(hh * PPI))


def region_sizes():
    out = list(FIXED)
    for bid, box in BOXES.items():
        for f in box[7]:
            out.append((f"a_{bid}_{f}", *_face_px(box, f)))
        out.append((f"c_{bid}", 16, 16))
    for bk, b in BOOKS.items():
        x0, x1, _sy, _d, _z0, h = b[:6]
        out.append((f"s_{bk}", max(8, round((x1 - x0) * PPI)), round(h * PPI)))
        out.append((f"c_{bk}", 16, 16))
    return out


def pack(sizes, size, pad=4):
    """Shelf packing, tallest first, deterministic."""
    order = sorted(sizes, key=lambda s: (-s[2], -s[1], s[0]))
    regions, x, y, row = {}, 0, 0, 0
    for name, w, h in order:
        if x + w + pad > size:
            x, y, row = 0, y + row + pad, 0
        regions[name] = (x, y, w, h)
        x += w + pad
        row = max(row, h)
    if y + row > size:
        raise ValueError(f"atlas overflow: {y + row} > {size}")
    return regions


ATLAS = {"name": "media_hutch", "size": ATLAS_SIZE, "regions": pack(region_sizes(), ATLAS_SIZE)}
# Photo-derived art (Cassidy's linocut print): its own atlas, kept out of git.
ART_ATLAS = {"name": "media_hutch_art", "size": 512, "regions": {"print": (0, 0, 336, 512)}}


def seeded(key):
    return random.Random(sum(ord(c) * (i + 1) for i, c in enumerate(key)))


if __name__ == "__main__":
    r = ATLAS["regions"]
    used = sum(w * h for _x, _y, w, h in r.values())
    bottom = max(y + h for _x, y, _w, h in r.values())
    print(len(r), "regions, fill", round(used / ATLAS_SIZE ** 2, 3), "bottom", bottom)
