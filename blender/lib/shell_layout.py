"""The apartment's shell layout: walls, rooms, openings. Inches as measured, converted
to meters where used (the builder calls m()).

Coordinates (plan directions): origin at the interior south-west corner where the
living room's window wall meets the entry wall; +X east toward the bedroom, +Y north
toward the kitchen and bath, Z up from the finished floor. Rectangles are
(x0, x1, y0, y1). Every entry carries a confidence tag:
  M  measured directly (tape)
  D  derived from measurements
  A  assumed or estimated; check these
Source: Cassidy's layout notes in Reference/ (local-only), corrected by the room captures
(tag S: measured from a registered LiDAR capture, about +-1 in).
"""

IN = 0.0254


def m(v):
    return v * IN


CEILING = 108.0                      # M
INTERIOR_WALL = 4.75                 # M
EXTERIOR_WALL = 6.0                  # A (not measured)
INTERIOR_W, INTERIOR_D = 274.6, 286.0    # S / S: the bedroom capture puts the east wall at
                                         # x 274.6 (tape sum 282.75; the bath door, 28 in from the
                                         # east wall by tape, lands where the capture sees it);
                                         # the living capture puts the north wall at y 286
DOOR_H = 80.0                        # A for every door unless noted
DOOR_TRIM = 3.0                      # M (entry door casing width)
WINDOW_SILL, WINDOW_HEAD = 26.5, 85.0    # M

# Walls: name -> ((x0, x1, y0, y1), confidence). Height is floor to ceiling.
WALLS = {
    "ext_west":       ((-6.0, 0.0, -6.0, 292.0), "A"),
    "ext_east":       ((274.6, 280.6, -6.0, 292.0), "S/A"),
    "ext_south":      ((-6.0, 280.6, -6.0, 0.0), "A"),
    "ext_north":      ((-6.0, 280.6, 286.0, 292.0), "S/A"),
    "center":         ((134.0, 138.75, 0.0, 286.0), "D"),
    "kitchen_stub":   ((0.0, 26.0, 180.5, 186.0), "S"),       # ends flush with the counter front
    "bedroom_back":   ((138.75, 211.2, 158.4, 163.15), "S"),
    "hall_west":      ((206.45, 211.2, 163.15, 197.75), "S"),
    "closet_south":   ((247.7, 274.6, 130.35, 135.1), "S"),
    "closet_front":   ((247.7, 252.45, 135.1, 197.75), "S"),
    "bath_south":     ((138.75, 274.6, 197.75, 202.5), "D/A"),
    "bath_west":      ((166.55, 171.3, 202.5, 286.0), "D"),      # bath 103.3 wide (bath capture)
    "laundry_divider": ((166.55, 171.3, 163.15, 197.75), "A"),
}

# Openings: (wall, axis the opening runs along, (a0, a1) along that axis, (z0, z1), kind, confidence).
OPENINGS = [
    ("ext_west",     "y", (144.5, 180.5), (0.0, DOOR_H), "door_entry", "S/A"),
    ("ext_west",     "y", (42.5, 77.25), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_west",     "y", (101.75, 136.5), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (38.5, 108.5), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (171.25, 205.45), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (212.5, 249.0), (0.0, DOOR_H), "door_patio", "S"),       # hinged, half glass (head 82 in the capture)
    ("center",       "y", (119.5, 153.5), (0.0, DOOR_H), "door", "S"),
    ("center",       "y", (206.0, 253.0), (0.0, DOOR_H), "door_closet_double", "S"),   # kitchen closet A
    ("bath_south",   "x", (214.0, 244.5), (0.0, DOOR_H), "door", "S"),           # hinged west
    ("hall_west",    "y", (164.0, 196.5), (0.0, DOOR_H), "door", "S"),           # a pair meeting in the middle
    ("closet_front", "y", (138.0, 196.5), (0.0, 81.5), "door_sliding", "S"),
]

# Floors: (x0, x1, y0, y1, finish). Carpet in the living room and the bedroom side; vinyl
# in the kitchen/dining, the entry landing and the bath. The living capture shows an L
# boundary: y 153 from the center wall to x 36, then south to y 134 and west to the wall (S).
FLOORS = [
    (0.0, 36.0, 0.0, 134.0, "floor_carpet"),            # living, west strip
    (36.0, 134.0, 0.0, 153.0, "floor_carpet"),          # living
    (0.0, 36.0, 134.0, 286.0, "floor_vinyl"),           # entry landing, kitchen west
    (36.0, 134.0, 153.0, 286.0, "floor_vinyl"),         # dining, kitchen
    (138.75, 274.6, 0.0, 197.75, "floor_carpet"),      # bedroom, hall, closets
    (138.75, 274.6, 197.75, 286.0, "floor_vinyl"),     # bath and kitchen closet A
]

# Where things stand: name -> (x, y of the footprint centre, rotation about Z in degrees
# from the object's front = -Y[, z of the origin]). The shell exports a place_<name>
# marker for each, and Unity drops the <name> prefab on it; a "__N" suffix places another
# copy of the same prefab.
PLACES = {
    # Bedroom side of the center wall, south of the bedroom door, drawers facing east.
    "filing_cabinet_set": (152.6, 73.75, 90.0),   # S: bedroom capture
    # Laundry closet: against its west wall, facing the door in the hall wall (east).
    "washer_dryer": (171.3 + 13.75 + 0.5, (163.15 + 197.75) / 2, 90.0),   # A
    # Kitchen (from the plan illustration and the photo through the bedroom door; A).
    "kitchen_cabinets": (0.0, 0.0, 0.0),        # built in plan coordinates
    "dishwasher": (12.75, 200.5, 90.0),         # S
    "range": (64.5, 272.0, 0.0),                # S
    "microwave": (64.0, 276.5, 0.0, 58.5),      # S
    "fridge": (116.25, 267.5, 0.0),             # S
    # Doors: hinged ones on the hinge-side edge of the opening at the wall centreline;
    # sliding, pocket and patio at the opening centre.
    "door_bedroom": (136.375, 153.5, 90.0),        # hinged north (from photo), open 90 deg into the bedroom
    "door_laundry": (208.825, 196.5, 90.0),        # hinged north, swings into the hall (really a pair: A)
    "door_entry": (-3.0, 180.5, 90.0),             # hinge side A
    "door_laundry__bath": (214.0, 200.125, 180.0),  # S: hinged west, swings into the bath
    "door_closet_sliding": (250.075, 167.25, -90.0),
    "door_entry__patio": (212.5, -3.0, 180.0),     # S: half-glass hinged door (entry door stands in; real hinge is east),
    # Bathroom, layout B (confirmed by the bathroom capture, S): tub along the east wall
    # faucet at the north wall, the 33 in stub wall at its south foot.
    "bathtub": (260.45, 257.05, 270.0),       # bath capture, shifted with the east wall
    "toilet": (186.6, 268.5, 90.0),
    "vanity": (181.8, 227.55, 90.0),
    # Built in the building's own coordinates.
    "door_kitchen_closet": (134.0, 229.5, -90.0),   # S
    # Living room and dining (living capture, S).
    "couch": (22.5, 69.0, 90.0),            # SCAN: 87 in long, back at x 3
    "couch_blankets": (22.5, 69.0, 90.0),
    "media_hutch": (124.75, 17.75, -90.0),      # SCAN: 31 x 18.5 x 80, square to the wall
    "wall_tv": (134.0, 72.5, -90.0, 39.5),      # origin at the back face bottom
    "wall_heater": (134.0, 97.5, -90.0),
    "toolboxes": (128.0, 75.0, -90.0),
    "dining_table": (85.0, 205.0, 0.0),
    "dining_chair__w": (63.0, 211.5, 90.0),
    "dining_chair__e": (92.5, 199.0, -90.0),     # pushed under
    "dining_chair__n": (107.5, 237.5, 0.0),
    "dining_chair__s": (75.5, 176.0, 180.0),     # pulled out
    "plant_tall": (16.5, 16.5, 0.0),
    "plant_broadleaf": (68.0, 15.0, 0.0),
    "portable_ac": (12.5, 125.0, 90.0),
    "bean_bag": (91.0, 16.5, 0.0),
    "trash_can": (30.5, 183.0, 90.0),
    "window_blinds": (0.0, 0.0, 0.0),
    "living_wall_art": (0.0, 0.0, 0.0),         # built in plan coordinates
    # Bedroom (bedroom capture, S).
    "wall_heater__bedroom": (138.75, 104.0, 90.0),
    "bed": (224.5, 107.5, -90.0),
    "headboard_bookcase": (267.9, 105.25, -90.0),
    "desk": (175.4, 14.5, 180.0),
    "desk_computer": (175.4, 14.5, 180.0),
    "office_chair": (185.5, 49.5, 0.0),         # faces the desk (south)
    "dresser": (264.75, 18.0, -90.0),
    "dresser_items": (264.75, 18.0, -90.0),
    "floor_lamp": (265.0, 42.0, -90.0),
    "plastic_drawers": (265.0, 75.0, -90.0),
    "floor_boxes": (266.5, 53.5, -90.0),
    "light_stand__center": (143.5, 104.5, 90.0),   # origin at the pole; box faces east
    "light_stand__patio": (235.0, 12.0, 180.0),    # box faces north
    "bedroom_fixtures": (0.0, 0.0, 0.0),
    # Light fixtures hang from their origin at the ceiling (z 108).
    "ceiling_light_bar": (68.0, 235.0, 0.0, 108.0),        # S
    "ceiling_dome_light__dining": (67.0, 152.0, 0.0, 108.0),   # A: near the entry, per the survey
    "ceiling_dome_light__hall": (229.0, 183.5, 0.0, 108.0),    # S
    "bath_fixtures": (-7.3, 0.0, 0.0),          # built in plan coordinates for the old east wall
    "window_units": (0.0, 0.0, 0.0),
    "exterior_view": (0.0, 0.0, 0.0),
}
