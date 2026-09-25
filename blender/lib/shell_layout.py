"""The apartment's shell layout: walls, rooms, openings. Inches as measured, converted
to meters where used (the builder calls m()).

Coordinates (plan directions): origin at the interior south-west corner where the
living room's window wall meets the entry wall; +X east toward the bedroom, +Y north
toward the kitchen and bath, Z up from the finished floor. Rectangles are
(x0, x1, y0, y1). Every entry carries a confidence tag:
  M  measured directly (tape)
  D  derived from measurements
  A  assumed or estimated; check these
Source: Cassidy's layout notes in Reference/ (local-only).
"""

IN = 0.0254


def m(v):
    return v * IN


CEILING = 108.0                      # M
INTERIOR_WALL = 4.75                 # M
EXTERIOR_WALL = 6.0                  # A (not measured)
INTERIOR_W, INTERIOR_D = 282.75, 289.9   # D / M
DOOR_H = 80.0                        # A for every door unless noted
DOOR_TRIM = 3.0                      # M (entry door casing width)
WINDOW_SILL, WINDOW_HEAD = 26.5, 85.0    # M

# Walls: name -> ((x0, x1, y0, y1), confidence). Height is floor to ceiling.
WALLS = {
    "ext_west":       ((-6.0, 0.0, -6.0, 295.9), "A"),
    "ext_east":       ((282.75, 288.75, -6.0, 295.9), "A"),
    "ext_south":      ((-6.0, 288.75, -6.0, 0.0), "A"),
    "ext_north":      ((-6.0, 288.75, 289.9, 295.9), "A"),
    "center":         ((134.0, 138.75, 0.0, 289.9), "D"),
    "kitchen_stub":   ((0.0, 40.0, 185.0, 189.9), "M/A"),     # length assumed 40 in
    "bedroom_back":   ((138.75, 209.75, 159.5, 164.25), "D"),
    "hall_west":      ((205.0, 209.75, 164.25, 201.65), "D/A"),
    "closet_south":   ((255.55, 282.75, 130.5, 135.25), "D"),
    "closet_front":   ((255.55, 260.3, 135.25, 201.65), "A"),
    "bath_south":     ((138.75, 282.75, 201.65, 206.4), "D/A"),
    "bath_west":      ((173.0, 177.75, 206.4, 289.9), "D"),
    "laundry_divider": ((173.0, 177.75, 164.25, 201.65), "A"),
}

# Openings: (wall, axis the opening runs along, (a0, a1) along that axis, (z0, z1), kind, confidence).
OPENINGS = [
    ("ext_west",     "y", (145.0, 181.0), (0.0, DOOR_H), "door_entry", "M/A"),
    ("ext_west",     "y", (42.5, 77.25), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_west",     "y", (101.75, 136.5), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (38.5, 108.5), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (171.25, 205.45), (WINDOW_SILL, WINDOW_HEAD), "window", "M"),
    ("ext_south",    "x", (220.75, 256.75), (0.0, DOOR_H), "door_patio", "M/A"),
    ("center",       "y", (122.0, 156.0), (0.0, DOOR_H), "door", "M/A"),
    ("bath_south",   "x", (220.0, 251.75), (0.0, DOOR_H), "door_pocket", "M/A"),
    ("hall_west",    "y", (166.0, 196.0), (0.0, DOOR_H), "door", "A"),
    ("closet_front", "y", (138.0, 199.0), (0.0, 81.5), "door_sliding", "A"),
]

# Floors: (x0, x1, y0, y1, finish). Wood-look vinyl in the living/dining/kitchen and
# bath (as in the plan illustration), carpet in the bedroom side.
FLOORS = [
    (0.0, 134.0, 0.0, 289.9, "floor_vinyl"),            # living, dining, kitchen
    (138.75, 282.75, 0.0, 201.65, "floor_carpet"),      # bedroom, hall, closets
    (138.75, 282.75, 201.65, 289.9, "floor_vinyl"),     # bath and kitchen closet A
]

# Where things stand: name -> (x, y of the footprint centre, rotation about Z in degrees
# from the object's front = -Y). The shell exports a place_<name> marker for each, and
# Unity drops the <name> prefab on it.
PLACES = {
    # Bedroom side of the center wall, south of the bedroom door, drawers facing east.
    "filing_cabinet_set": (138.75 + 13.25 + 0.5, 95.0, 90.0),   # A: from photos
    # Laundry closet: against its west wall, facing the door in the hall wall (east).
    "washer_dryer": (177.75 + 13.75 + 0.5, (164.25 + 201.65) / 2, 90.0),   # A
    # Kitchen (from the plan illustration and the photo through the bedroom door; A).
    "kitchen_cabinets": (67.0, 239.95, 0.0),    # origin at the kitchen box centre; run built in room layout
    "range": (71.0, 275.4, 0.0),
    "fridge": (117.125, 273.4, 0.0),
    # Doors: hinged ones on the hinge-side edge of the opening at the wall centreline;
    # sliding, pocket and patio at the opening centre.
    "door_bedroom": (136.375, 156.0, 90.0),        # hinged north (from photo), open 90 deg into the bedroom
    "door_laundry": (207.375, 196.0, 90.0),        # hinged north (from photo), swings into the hall
    "door_entry": (-3.0, 181.0, 90.0),             # hinge side A
    "door_bath_pocket": (235.875, 204.025, 0.0),   # pocket side A
    "door_closet_sliding": (257.925, 168.5, -90.0),
    "door_patio": (238.75, -3.0, 180.0),           # which panel slides: A
    # Bathroom, layout B from the plan illustration: tub along the east wall, faucet at
    # the north wall, the 33 in stub wall at its south foot (A until a bathroom capture).
    "bathtub": (267.75, 259.9, 270.0),
    "toilet": (191.75, 270.0, 90.0),
    "vanity": (188.5, 228.0, 90.0),
    # Built in the building's own coordinates.
    "window_units": (0.0, 0.0, 0.0),
    "exterior_view": (0.0, 0.0, 0.0),
}
