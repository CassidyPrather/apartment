"""Kitchen cabinet interiors, plan inches (x east, y north, z up; same frame as object.py).

Pure Python (no bpy): the kitchen_cabinets package builds its hollow carcasses, shelves and
drawer boxes from these numbers, and the contents packages import them to place things.
Keys and ids are stable; values may be refined (re-read at build time).

CABINETS[id] (static cabinet interiors, the empty space inside the carcass):
    "run":     "W" (west wall, fronts face +x), "N" (north wall, fronts face -y),
               "C" (45-degree upper corner, front faces south-east)
    "x", "y":  interior extent (inside faces of back/side panels and the back of the face
               frame); for "C" see "poly"
    "z":       (floor_top_z, ceiling_z): top surface of the cabinet floor, underside of the
               top panel (base cabinets: underside of the counter or of the drawer box above)
    "shelves": shelf TOP-surface z values, bottom to top (shelves are SHELF_T thick)
    "shelf_depth": None = full interior depth (front edge FRONT_SETBACK behind the face
               frame), else inches from the back wall
    "poly":    (optional) interior outline in plan, counter-clockwise; shelves follow it
    "shelf_poly": (optional) shelf outline when the shelf is not the full interior
    "partitions": (optional) [(a0, a1)] vertical panels across the full depth splitting
               the interior (along x for "N" runs)
    "front":   the plane of the face frame's back (y for "N", x for "W"): stuff must stay
               behind it so the doors close ("corner" also has "front_w" for its west leg)
DRAWERS[id]: the INSIDE of each drawer box when CLOSED (x, y extents; z = (inside bottom top
    surface, top edge of the sides)). Contents go in a separate `<drawer object>_contents`
    object placed for the closed position.
SINK_OBSTACLES: boxes (name, (x0,x1), (y0,y1), (z0,z1)) under the sink to keep clear
    (sink bowls, disposal, drain/P-trap).

Photos: Reference/cupboards_drawers/PXL_20261023_*.jpg, sorted index: 0 wu1, 1 wu2, 2 wu3,
3 cu, 4 nu1 (east bay), 5 nu2, 6 nu3, 7 sink, 8 corner (bifold door, L cabinet), 9-12 d1-d4,
13 ed, 14 eb.
Shelf heights are PHOTO (proportioned on the back wall, perspective-corrected by eye);
carcass panel sizes are EST (standard 1/2 in sides/back, 3/4 in floor, 3/4 in face frame).
"""

SHELF_T = 0.75          # EST shelf thickness (white melamine, white edge)
FRONT_SETBACK = 0.5     # EST shelf front edge behind the face frame
PANEL = 0.5             # EST side/back panels
FLOOR_T = 0.75          # EST cabinet floor
FRAME_T = 0.75          # EST oak face frame thickness
DOOR_T = 0.75           # same as object.py

# --- uppers: z 53-97.5 (short ones over the sink 70 and microwave 76), depth 13 ----------
UP_Z1 = 97.5
W_UP_FACE = 13.0                       # west uppers door face plane x (doors 12.25-13)
W_UP_FRONT = W_UP_FACE - DOOR_T - FRAME_T   # 11.5: back of the face frame
N_UP_FACE = 273.0                      # north uppers door face plane y (doors 273-273.75)
N_UP_FRONT = N_UP_FACE + DOOR_T + FRAME_T   # 274.5
WALL_N, WALL_W = 286.0, 0.0


def _up(z0):
    return (z0 + FLOOR_T, UP_Z1 - PANEL)


# --- base: carcass z 4 (toe kick) to 34.5 (counter underside) -------------------------
BASE_FLOOR = 4.0 + FLOOR_T             # 4.75
COUNTER_UNDER = 34.5
W_BASE_FRONT = 24.75 - FRAME_T         # 24.0: west base face frame back (doors 24.75-25.5)
N_BASE_FRONT = 259.5 + FRAME_T         # 260.25: north base face frame back (doors 258.75-259.5)

CABINETS = {
    # west uppers (fronts +x)
    "wu1": {"run": "W", "x": (WALL_W + PANEL, W_UP_FRONT), "y": (189.5, 213.5), "z": _up(53.0),
            "shelves": [65.0, 74.5], "shelf_depth": None, "front": W_UP_FRONT},       # photo 0
    "wu2": {"run": "W", "x": (WALL_W + PANEL, W_UP_FRONT), "y": (214.5, 245.5), "z": _up(70.0),
            "shelves": [83.5], "shelf_depth": None, "front": W_UP_FRONT},             # photo 1
    "wu3": {"run": "W", "x": (WALL_W + PANEL, W_UP_FRONT), "y": (246.5, 263.5), "z": _up(53.0),
            "shelves": [64.0, 75.5, 87.0], "shelf_depth": None, "front": W_UP_FRONT}, # photo 2
    # 45-degree corner upper: door face (13,264)-(22,273); interior pentagon
    "cu": {"run": "C", "x": (0.5, 21.5), "y": (264.5, 285.5), "z": _up(53.0),
           "poly": [(0.5, 264.5), (11.38, 264.5), (21.5, 274.62), (21.5, 285.5), (0.5, 285.5)],
           "shelves": [64.5, 75.0, 86.5], "shelf_depth": None,
           "front": ((13.0, 264.0), (22.0, 273.0))},                                   # photo 3
    # north uppers (fronts -y)
    "nu1": {"run": "N", "x": (22.5, 49.0), "y": (N_UP_FRONT, WALL_N - PANEL), "z": _up(53.0),
            "partitions": [(35.5, 36.0)],   # two bays, each door hinged on its west side (photo 4)
            "shelves": [63.5, 72.5, 86.5], "shelf_depth": None, "front": N_UP_FRONT},  # photo 4
    "nu2": {"run": "N", "x": (50.0, 79.0), "y": (N_UP_FRONT, WALL_N - PANEL), "z": _up(76.0),
            "shelves": [], "shelf_depth": None, "front": N_UP_FRONT},                  # photo 5
    "nu3": {"run": "N", "x": (80.0, 97.5), "y": (N_UP_FRONT, WALL_N - PANEL), "z": _up(53.0),
            "shelves": [64.0, 73.5, 88.5], "shelf_depth": None, "front": N_UP_FRONT},  # photo 6
    # (no "fu": the box over the fridge is only a facade)
    # base, west run (fronts +x)
    "sink": {"run": "W", "x": (WALL_W + PANEL, W_BASE_FRONT), "y": (213.0, 248.0),
             "z": (BASE_FLOOR, COUNTER_UNDER),   # bowls hang to z 27.5: see SINK_OBSTACLES
             "shelves": [], "shelf_depth": None, "front": W_BASE_FRONT},               # photo 7
    # L-shaped blind-corner cabinet behind the single bifold corner door (photo 8): the west
    # leg (y 249-260.25 behind the door's outer panel, the old "wb") plus the north part. "x"/"y"
    # are its bounding box; "poly" is the exact L; "front" (north opening, y) and "front_w"
    # (west opening, x) are the face-frame backs.
    "corner": {"run": "N", "x": (0.5, 35.75), "y": (249.0, WALL_N - PANEL),
               "z": (BASE_FLOOR, COUNTER_UNDER),
               "poly": [(0.5, 249.0), (W_BASE_FRONT, 249.0), (W_BASE_FRONT, N_BASE_FRONT),
                        (35.75, N_BASE_FRONT), (35.75, WALL_N - PANEL), (0.5, WALL_N - PANEL)],
               "shelves": [17.5], "shelf_depth": None, "front": N_BASE_FRONT, "front_w": W_BASE_FRONT,
               # photo 8: one L shelf: a ~12 in strip along the west wall (behind the outer panel),
               # a ~12 in strip along the north wall, a full-depth leg by the drawers, rounded
               # inside corners (the front-left cut-out leaves the corner floor free)
               "shelf_poly": [(0.5, 285.5), (0.5, 249.5), (12.5, 249.5), (12.5, 270.0), (12.9, 271.8),
                              (14.0, 273.0), (16.0, 273.5), (24.0, 273.5), (26.0, 273.2),
                              (27.6, 272.3), (28.5, 271.0), (28.8, 269.5),
                              (28.8, N_BASE_FRONT + FRONT_SETBACK),
                              (35.75, N_BASE_FRONT + FRONT_SETBACK), (35.75, 285.5)]},
    # under the east drawer (fronts -y)
    "eb": {"run": "N", "x": (80.0, 99.5), "y": (N_BASE_FRONT, WALL_N - PANEL),
           "z": (BASE_FLOOR, 26.5),
           "shelves": [14.0], "shelf_depth": None, "front": N_BASE_FRONT},             # photo 14
}

# --- drawers: inside of the box, closed position --------------------------------------
DRAWER_SIDE = 0.5        # EST melamine sides/back
DRAWER_BOTTOM = 0.5      # EST
DRAWER_BACK_Y = 281.5    # EST box back (outer) for the north run (21.25 in deep boxes)


def _dr(x0, x1, zb, zt):
    """Inside of a north-run drawer box with outer x span x0..x1 (box bottom underside zb,
    side top edge zt)."""
    return {"x": (x0 + DRAWER_SIDE, x1 - DRAWER_SIDE),
            "y": (N_BASE_FRONT - FRAME_T + DRAWER_SIDE, DRAWER_BACK_Y - DRAWER_SIDE),
            "z": (zb + DRAWER_BOTTOM, zt)}


DRAWERS = {
    # four-drawer bank x 36.5-49.5 (fronts at z 28.5-34.5 / 20.5-28.5 / 12.5-20.5 / 4-12.5)
    "d1": _dr(37.75, 48.25, 29.0, 33.5),     # photo 9 (utensils)
    "d2": _dr(37.75, 48.25, 21.0, 27.5),     # photo 10
    "d3": _dr(37.75, 48.25, 13.0, 19.5),     # photo 11
    "d4": _dr(37.75, 48.25, 5.0, 11.5),      # photo 12
    # east drawer x 79.5-100, front z 27-34.5
    "ed": _dr(81.0, 98.5, 27.5, 33.5),       # photo 13 (cutlery tray)
}

# --- under the sink ------------------------------------------------------------------
SINK_OBSTACLES = [
    ("bowls", (3.5, 21.0), (214.5, 245.5), (27.5, COUNTER_UNDER)),
    ("disposal", (8.75, 15.75), (218.6, 225.6), (15.5, 27.5)),      # black cylinder under the south bowl (photo 7)
    ("drain", (1.0, 14.5), (235.0, 242.0), (12.0, 27.5)),          # tailpiece + P-trap under the north bowl into the back wall
    ("waste_arm", (11.25, 13.25), (225.0, 239.5), (22.0, 24.2)),   # white pipe from the disposal across to the tee
    ("supplies", (0.5, 3.5), (225.0, 236.0), (12.5, 34.5)),        # chrome stops on the back wall + braided lines up
]
