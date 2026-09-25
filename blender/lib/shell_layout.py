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
INTERIOR_W, INTERIOR_D = 282.75, 286.0   # D / S: the living capture puts the north wall at
                                         # y 286 (tape sum 289.9; kitchen depth 100 agrees with 286)
DOOR_H = 80.0                        # A for every door unless noted
DOOR_TRIM = 3.0                      # M (entry door casing width)
WINDOW_SILL, WINDOW_HEAD = 26.5, 85.0    # M

# Walls: name -> ((x0, x1, y0, y1), confidence). Height is floor to ceiling.
WALLS = {
    "ext_west":       ((-6.0, 0.0, -6.0, 292.0), "A"),
    "ext_east":       ((282.75, 288.75, -6.0, 292.0), "A"),
    "ext_south":      ((-6.0, 288.75, -6.0, 0.0), "A"),
    "ext_north":      ((-6.0, 288.75, 286.0, 292.0), "S/A"),
    "center":         ((134.0, 138.75, 0.0, 286.0), "D"),
    "kitchen_stub":   ((0.0, 26.0, 180.5, 186.0), "S"),       # ends flush with the counter front
    "bedroom_back":   ((138.75, 209.75, 159.5, 164.25), "D"),
    "hall_west":      ((205.0, 209.75, 164.25, 197.75), "D/A"),
    "closet_south":   ((255.55, 282.75, 130.5, 135.25), "D"),
    "closet_front":   ((255.55, 260.3, 135.25, 197.75), "A"),
    "bath_south":     ((138.75, 282.75, 197.75, 202.5), "D/A"),
    "bath_west":      ((173.0, 177.75, 202.5, 286.0), "D"),
    "laundry_divider": ((173.0, 177.75, 164.25, 197.75), "A"),
}

# Openings: (wall, axis the opening runs along, (a0, a1) along that axis, (z0, z1), kind, confidence).
OPENINGS = [
    ("ext_west",     "y", (144.5, 180.5), (0.0, DOOR_H), "door_entry", "S/A"),
    ("ext_west",     "y", (42.5, 77.25), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_west",     "y", (101.75, 136.5), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (38.5, 108.5), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (171.25, 205.45), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (220.75, 256.75), (0.0, DOOR_H), "door_patio", "M/A"),
    ("center",       "y", (119.5, 153.5), (0.0, DOOR_H), "door", "S"),
    ("center",       "y", (206.0, 253.0), (0.0, DOOR_H), "door_closet_double", "S"),   # kitchen closet A
    ("bath_south",   "x", (220.0, 251.75), (0.0, DOOR_H), "door_pocket", "M/A"),
    ("hall_west",    "y", (166.0, 196.0), (0.0, DOOR_H), "door", "A"),
    ("closet_front", "y", (137.0, 196.0), (0.0, 81.5), "door_sliding", "A"),
]

# Floors: (x0, x1, y0, y1, finish). Carpet in the living room and the bedroom side; vinyl
# in the kitchen/dining, the entry landing and the bath. The living capture shows an L
# boundary: y 153 from the center wall to x 36, then south to y 134 and west to the wall (S).
FLOORS = [
    (0.0, 36.0, 0.0, 134.0, "floor_carpet"),            # living, west strip
    (36.0, 134.0, 0.0, 153.0, "floor_carpet"),          # living
    (0.0, 36.0, 134.0, 286.0, "floor_vinyl"),           # entry landing, kitchen west
    (36.0, 134.0, 153.0, 286.0, "floor_vinyl"),         # dining, kitchen
    (138.75, 282.75, 0.0, 197.75, "floor_carpet"),      # bedroom, hall, closets
    (138.75, 282.75, 197.75, 286.0, "floor_vinyl"),     # bath and kitchen closet A
]

# Where things stand: name -> (x, y of the footprint centre, rotation about Z in degrees
# from the object's front = -Y[, z of the origin]). The shell exports a place_<name>
# marker for each, and Unity drops the <name> prefab on it; a "__N" suffix places another
# copy of the same prefab.
PLACES = {
    # Bedroom side of the center wall, south of the bedroom door, drawers facing east.
    "filing_cabinet_set": (138.75 + 13.25 + 0.5, 95.0, 90.0),   # A: from photos
    # Laundry closet: against its west wall, facing the door in the hall wall (east).
    "washer_dryer": (177.75 + 13.75 + 0.5, (164.25 + 197.75) / 2, 90.0),   # A
    # Kitchen (from the plan illustration and the photo through the bedroom door; A).
    "kitchen_cabinets": (0.0, 0.0, 0.0),        # built in plan coordinates
    "dishwasher": (12.75, 200.5, 90.0),         # S
    "range": (64.5, 272.0, 0.0),                # S
    "microwave": (64.0, 276.5, 0.0, 58.0),      # S
    "fridge": (116.25, 267.5, 0.0),             # S
    # Doors: hinged ones on the hinge-side edge of the opening at the wall centreline;
    # sliding, pocket and patio at the opening centre.
    "door_bedroom": (136.375, 153.5, 90.0),        # hinged north (from photo), open 90 deg into the bedroom
    "door_laundry": (207.375, 196.0, 90.0),        # hinged north (from photo), swings into the hall
    "door_entry": (-3.0, 180.5, 90.0),             # hinge side A
    "door_bath_pocket": (235.875, 200.125, 0.0),   # pocket side A
    "door_closet_sliding": (257.925, 166.5, -90.0),
    "door_patio": (238.75, -3.0, 180.0),           # which panel slides: A
    # Bathroom, layout B (confirmed by the bathroom capture, S): tub along the east wall,
    # faucet at the north wall, the 33 in stub wall at its south foot.
    "bathtub": (267.75, 257.05, 270.0),
    "toilet": (193.9, 268.5, 90.0),
    "vanity": (189.1, 227.55, 90.0),
    # Built in the building's own coordinates.
    "door_kitchen_closet": (134.0, 229.5, -90.0),   # S
    # Living room and dining (living capture, S).
    "couch": (24.5, 74.5, 90.0),
    "couch_blankets": (24.5, 74.5, 90.0),
    "media_hutch": (118.0, 27.0, -90.0),
    "wall_tv": (134.0, 72.5, -90.0),
    "wall_heater": (134.0, 86.0, -90.0),
    "toolboxes": (118.0, 85.0, -90.0),
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
    "bath_fixtures": (0.0, 0.0, 0.0),           # built in plan coordinates
    "window_units": (0.0, 0.0, 0.0),
    "exterior_view": (0.0, 0.0, 0.0),
}
