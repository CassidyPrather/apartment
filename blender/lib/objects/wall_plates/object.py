"""Wall plates: every outlet, light switch, thermostat, wall smoke alarm and the breaker
panel that the captures show, each at its surveyed spot on the modelled wall face.

  living   entry toggle (west wall, between window 2 and the entry door), line-voltage
           thermostat and a rectangular wall smoke alarm on the center wall's west face
           above/right of the wall heater, the TV outlet low on the center wall, a duplex
           on the south wall beside the media hutch
  kitchen  2-gang toggle + GFCI by the dishwasher, duplex at the west run's north end,
           duplex on the north backsplash (all sitting on the 4 in backsplash)
  bedroom  line-voltage thermostat + toggle by the bedroom door (center wall), 3-gang
           toggle plate and a duplex on the back wall, the breaker panel (flush, painted
           cover with an inner door and latch) on the back wall, a duplex on the east wall
  bath     2-gang toggle plate on the tub stub wall's south face (the linen niche mouth),
           a decora GFCI beside the vanity mirror
Not built here (already modelled, listed in positions.json): bedroom_cables' coax plate
and duplex on the center wall; bedroom_fixtures' ceiling smoke detector.
bedroom_fixtures also has a thermostat block at y 110-114 that this package replaces
(it sits where the real toggle is): hide or remove that one.

Source of truth: the living, bedroom and bathroom LiDAR captures (registered photos,
Reference/wall_plates_work/: wo.py orthophotos, sheet.py crops with a plan grid and a
ray/wall-plane locate), plus Reference/IMG_1498.jpg (bedroom thermostat + toggle) and the
rn_image_picker photo (bedroom back-wall 3-gang and outlet). Positions along the wall and
heights: SCAN (about +-1.5 in, the capture's registration); sizes: SPEC (standard
wall-plate sizes) or EST (proportioned from the photos).

FRAME: PLAN COORDINATES like bedroom_cables: object X = plan x (east), Y = plan y (north),
Z up, metres; the package goes on a marker at the plan origin with no rotation. Every
plate is snapped onto the shell's wall face (shell_layout.WALLS) and stands 0.25 in proud.
build() also writes objects/wall_plates/positions.json (one entry per item, plus "levers": the
pivots of the split-out interactive levers, see SPLIT_LEVERS).
"""

import json
import math
import os

from mathutils import Matrix, Vector

import common

NAME = "wall_plates"
IN = 0.0254
HERE = os.path.dirname(os.path.abspath(__file__))


def m(v):
    return v * IN


# --- sizes (inches) ----------------------------------------------------------------
PLATE_H = 4.5                                          # SPEC standard plate height
GANG_W = {1: 2.75, 2: 4.56, 3: 6.375}                  # SPEC standard plate widths
PLATE_T = 0.25                                         # SPEC (brief: 0.25 proud)
THERMO = (3.7, 4.8, 0.9)                               # EST w, h, depth (IMG_1498: 1.35x the
                                                       # toggle plate's width, a little taller)
SMOKE = (4.25, 5.75, 1.5)                              # EST (capture ortho 4.5 x 6)
PANEL = (15.25, 28.0, 0.12)                            # TAPE width 15.25 / SCAN height 26.5-54.5
PANEL_DOOR = (8.0, 20.5, 0.1)                          # SCAN inner door x 170.5-178.5, z 30-50.5
PANEL_LATCH = (-2.4, 1.0)                              # SCAN latch: 2.4 in left of the door
                                                       # centre, 1 in above the panel centre
TOGGLE = (0.3, 0.55, 0.28)                             # EST lever width, reach, thickness

# --- wall faces (shell_layout, inches): name -> (axis, coordinate, normal sign) --------
WALLS = {
    "east face of ext_west":           ("x", 0.0, +1),
    "west face of center":             ("x", 134.0, -1),
    "north face of ext_south":         ("y", 0.0, +1),
    "south face of ext_north":         ("y", 286.0, -1),
    "east face of center":             ("x", 138.75, +1),
    "south face of bedroom_back":      ("y", 158.4, -1),
    "west face of ext_east":           ("x", 274.6, -1),
    "east face of bath_west":          ("x", 171.3, +1),
    "south face of bath_stub_wall":    ("y", 222.55, -1),   # bathtub package stub (y 222.55..228.1)
}

# --- the items -----------------------------------------------------------------------
# u = position along the wall (plan y for x-walls, plan x for y-walls), z = plate centre.
# style: duplex | toggle | combo | gfci | thermostat | smoke | panel
ITEMS = [
    dict(id="entry_switch", kind="light_switch", room="living (entry)", wall="east face of ext_west",
         u=139.0, z=46.0, gangs=1, style="toggle", toggles=["up"],
         controls="unknown; the only switch at the entry, most likely the entry/dining ceiling dome "
                  "(ceiling_dome_light__dining, plan 67,152)",
         notes="traditional single toggle plate between window 2's recess and the entry door "
               "casing (latch side); capture puts it at y 137.2-137.6, snapped to 139.0 to sit "
               "centred in the modelled 136.5-141.5 gap",
         frames=["living wide_20260925_003702_768", "living wide_20260925_003336_768",
                 "living wide_20260925_003413_768"]),
    dict(id="living_thermostat", kind="thermostat", room="living", wall="west face of center",
         u=108.2, z=46.2, gangs=1, style="thermostat",
         controls="the living-room wall heater (wall_heater, plan y 97.5)",
         notes="white line-voltage thermostat, dark window with a slider on its right half; "
               "below the map poster",
         frames=["living wide_20260925_003549_773", "living wide_20260925_004349_769",
                 "living wide_20260925_003553_772"]),
    dict(id="living_smoke_alarm", kind="smoke_detector", room="living", wall="west face of center",
         u=92.1, z=81.6, gangs=0, style="smoke",
         notes="rectangular wall-mount smoke alarm (vented face), high on the wall above the heater",
         frames=["living wide_20260925_003553_772", "living wide_20260925_004209_769",
                 "living wide_20260925_004207_768"]),
    dict(id="living_outlet_tv", kind="outlet", room="living", wall="west face of center",
         u=76.2, z=19.2, gangs=1, style="duplex",
         notes="duplex just below the TV, both receptacles in use (two black plugs, not modelled); "
               "the plate reads a little large (3.5 x 4.3) in the capture, built standard",
         frames=["living wide_20260925_003606_772", "living wide_20260925_003547_768",
                 "living wide_20260925_004348_769"]),
    dict(id="living_outlet_south", kind="outlet", room="living", wall="north face of ext_south",
         u=114.2, z=17.5, gangs=1, style="duplex",
         notes="duplex just west of the media hutch, a plug in the upper receptacle (not modelled)",
         frames=["living wide_20260925_003448_768", "living wide_20260925_003528_768",
                 "living wide_20260925_003530_768"]),
    dict(id="kitchen_switch_gfci", kind="switch+gfci", room="kitchen", wall="east face of ext_west",
         u=203.8, z=42.4, gangs=2, style="combo", toggles=["down"],
         controls="toggle: unknown, probably the garbage disposal (next to the sink) or the "
                  "kitchen light bar",
         notes="2-gang plate: toggle (south) + decora GFCI with red TEST / black RESET (north), "
               "on the backsplash between the dishwasher and the sink",
         frames=["living wide_20260925_004026_769", "living wide_20260925_004058_769",
                 "living wide_20260925_003856_767"]),
    dict(id="kitchen_outlet_west", kind="outlet", room="kitchen", wall="east face of ext_west",
         u=254.6, z=42.4, gangs=1, style="duplex",
         notes="traditional duplex on the backsplash north of the sink",
         frames=["living wide_20260925_003900_768", "living wide_20260925_004028_769",
                 "living wide_20260925_003859_770"]),
    dict(id="kitchen_outlet_north", kind="outlet", room="kitchen", wall="south face of ext_north",
         u=37.1, z=42.4, gangs=1, style="duplex",
         notes="duplex on the north backsplash over the drawer bank; rice cooker plugged into "
               "the lower receptacle (not modelled)",
         frames=["living wide_20260925_004033_769", "living wide_20260925_003905_769",
                 "living wide_20260925_004102_768"]),
    dict(id="bedroom_thermostat", kind="thermostat", room="bedroom", wall="east face of center",
         u=110.4, z=45.4, gangs=1, style="thermostat",
         controls="the bedroom wall heater (wall_heater__bedroom, plan y 104)",
         notes="same line-voltage thermostat as the living room; replaces bedroom_fixtures' "
               "thermostat block (y 110-114, z 45.5-50.5), which overlaps the toggle",
         frames=["bedroom wide_20260925_011435_923", "bedroom wide_20260925_011448_922", "IMG_1498.jpg"]),
    dict(id="bedroom_door_switch", kind="light_switch", room="bedroom", wall="east face of center",
         u=113.8, z=45.5, gangs=1, style="toggle", toggles=["up"],
         controls="unknown: the bedroom has no ceiling fixture, so most likely a switched "
                  "receptacle (none identified)",
         notes="traditional single toggle right beside the thermostat, ~1.3 in short of the "
               "bedroom door casing",
         frames=["bedroom wide_20260925_011435_923", "bedroom wide_20260925_011449_923", "IMG_1498.jpg"]),
    dict(id="bedroom_back_3gang", kind="light_switch", room="bedroom", wall="south face of bedroom_back",
         u=187.9, z=45.0, gangs=3, style="toggle", toggles=["down", "down", "down"],
         controls="unknown per toggle; the nearest fixture is the hall ceiling dome "
                  "(ceiling_dome_light__hall, 229,183.5), so one toggle is very likely the hall "
                  "light; the others possibly switched receptacles",
         notes="3-gang traditional toggle plate, all three down in the capture; just east of the "
               "breaker panel, under the six-panel flower print",
         frames=["bedroom wide_20260925_012650_930", "bedroom wide_20260925_012652_930",
                 "bedroom wide_20260925_012710_930", "rn_image_picker_lib_temp_c06cbadc-a28a-409c-a06a-495334ccfb5e.jpg"]),
    dict(id="bedroom_back_outlet", kind="outlet", room="bedroom", wall="south face of bedroom_back",
         u=185.9, z=16.1, gangs=1, style="duplex",
         notes="duplex below the 3-gang switch",
         frames=["bedroom wide_20260925_012658_930", "bedroom wide_20260925_012652_930",
                 "rn_image_picker_lib_temp_c06cbadc-a28a-409c-a06a-495334ccfb5e.jpg"]),
    dict(id="breaker_panel", kind="breaker_panel", room="bedroom", wall="south face of bedroom_back",
         u=174.4, z=40.5, gangs=0, style="panel",
         notes="flush load-centre cover painted the wall colour, 15.25 x 28 (x 166.8-182.05, "
               "z 26.5-54.5) with four corner screws, an 8 x 20.5 inner door and a small square "
               "latch on its left (west) side; capture x 166.5-182.5 matches the tape width",
         frames=["bedroom wide_20260925_012653_930", "bedroom wide_20260925_012649_929",
                 "bedroom wide_20260925_012654_930", "bedroom wide_20260925_012710_930"]),
    dict(id="bedroom_east_outlet", kind="outlet", room="bedroom", wall="west face of ext_east",
         u=49.2, z=16.6, gangs=1, style="duplex",
         notes="duplex behind the floor lamp / plastic drawers, a black plug in the lower "
               "receptacle (not modelled)",
         frames=["bedroom wide_20260925_011817_924", "bedroom wide_20260925_011942_926",
                 "bedroom wide_20260925_011940_926"]),
    dict(id="bath_switches", kind="light_switch", room="bath", wall="south face of bath_stub_wall",
         u=254.8, z=45.8, gangs=3, style="toggle", toggles=["up", "down", "up"],
         controls="three toggles for the vanity light bar and the ceiling fan/light unit (light, "
                  "fan); which toggle is which is unknown",
         notes="3-gang toggle plate (six screws) on the stub wall at the tub's foot, facing south "
               "inside the linen niche's mouth, between the stub's west end (x 249.55) and the "
               "shelves (x 260.95); the capture sees it only obliquely, so x is +-2",
         frames=["bath wide_20260925_005712_134", "bath wide_20260925_005714_134",
                 "Reference/bathroom_survey/v_closet.jpg (tile 24)"]),
    dict(id="bath_gfci", kind="gfci_outlet", room="bath", wall="east face of bath_west",
         u=242.0, z=42.0, gangs=1, style="gfci",
         notes="decora GFCI beside the vanity mirror (north of it), both receptacles in use "
               "(white + black plugs, not modelled; they hide the TEST/RESET buttons)",
         frames=["bath wide_20260925_005915_135", "bath wide_20260925_005917_136",
                 "bath wide_20260925_005902_136"]),
]

EXISTING = [
    dict(id="bedroom_coax", kind="cable_jack", room="bedroom", wall="east face of center",
         u=45.0, z=12.75, gangs=1, existing="bedroom_cables",
         notes="coax F-connector plate; the capture reads the centre nearer z 14-15",
         frames=["IMG_1516.jpg", "IMG_1498.jpg", "bedroom wide_20260925_011516_923"]),
    dict(id="bedroom_center_outlet", kind="outlet", room="bedroom", wall="east face of center",
         u=62.5, z=12.75, gangs=1, existing="bedroom_cables",
         notes="duplex with the power strip's plug; the capture reads the centre nearer z 14",
         frames=["IMG_1516.jpg", "IMG_1498.jpg", "bedroom wide_20260925_011516_923"]),
    dict(id="bedroom_smoke_detector", kind="smoke_detector", room="bedroom", wall="ceiling",
         u=None, z=108.0, gangs=0, existing="bedroom_fixtures", plan=(166.0, 142.0),
         notes="round ceiling smoke detector near the bedroom door",
         frames=["Reference/bedroom_survey/crops/smoke_detector_1.jpg"]),
]

# --- atlas ---------------------------------------------------------------------------
ATLAS = {
    "name": NAME,
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
REGIONS = list(ATLAS["regions"])
MATERIALS = {NAME: {"atlas": NAME, "mode": "opaque", "tiled": False}}
COLLIDER = "none"
STATIC = True
VIEWS = [("west_low", 270, 5, 0.35), ("east_low", 90, 5, 0.35), ("south_view", 180, 5, 0.35)]

FACE_OF = {"duplex": "face_duplex", "gfci": "face_gfci", "combo": "face_combo",
           "thermostat": "face_thermo", "smoke": "face_smoke", "panel": "face_panel"}


def face_region(it):
    if it["style"] == "toggle":
        return "face_toggle%d" % it["gangs"]
    return FACE_OF[it["style"]]


def item_size(it):
    s = it["style"]
    if s == "thermostat":
        return THERMO
    if s == "smoke":
        return SMOKE
    if s == "panel":
        return PANEL
    return (GANG_W[it["gangs"]], PLATE_H, PLATE_T)


def frame(it):
    """(centre on the wall face, right, out-normal) in plan inches (Vectors)."""
    axis, c, n = WALLS[it["wall"]]
    if axis == "x":
        nrm = Vector((n, 0.0, 0.0)); C = Vector((c, it["u"], it["z"]))
    else:
        nrm = Vector((0.0, n, 0.0)); C = Vector((it["u"], c, it["z"]))
    right = Vector((-nrm.y, nrm.x, 0.0))
    return C, right, nrm


def basis(it):
    """Local -> plan-metres matrix: local X = right, local -Y = out of the wall, Z = up."""
    C, r, n = frame(it)
    M = Matrix(((r.x, -n.x, 0, m(C.x)), (r.y, -n.y, 0, m(C.y)), (0, 0, 1, m(C.z)), (0, 0, 0, 1)))
    return M


# Interactive switches: these plates' levers are separate objects (west -> east).
SPLIT_LEVERS = {
    "entry_switch": ["wall_plates_lever_entry"],
    "bedroom_back_3gang": ["wall_plates_lever_bedback_1", "wall_plates_lever_bedback_2",
                           "wall_plates_lever_bedback_3"],
    "bath_switches": ["wall_plates_lever_bath_1", "wall_plates_lever_bath_2", "wall_plates_lever_bath_3"],
}
LEVER_THROW = 40.0           # EST degrees between up and down (+-20 from straight out)
LEVERS = []

FACES = []   # (region, item, w, h) for texture(): which instance each front face belongs to


def lbox(b, region, M, u0, u1, v0, v1, d0, d1, bevel=0.0, segments=1):
    """Box in the item's local inches: u right, v up, d out of the wall."""
    return b.box(region, (m(u0), m(-d1), m(v0)), (m(u1), m(-d0), m(v1)),
                 bevel=m(bevel) if bevel else 0.0, segments=segments, matrix=M)


def retag_front(b, src, dst, M, d_front):
    """Faces of `src` whose normal points out of the wall and lie on the front plane."""
    b.bm.normal_update()
    Mi = M.inverted()
    i, j = b.idx(src), b.idx(dst)
    R = M.to_3x3()
    out = R @ Vector((0, -1, 0))
    for f in b.bm.faces:
        if f.material_index != i or f.normal.dot(out) < 0.999:
            continue
        c = Mi @ f.calc_center_median()
        if abs(-c.y - m(d_front)) < m(0.02):
            f.material_index = j


def build_item(b, it):
    M = basis(it)
    w, h, t = item_size(it)
    fr = face_region(it)
    s = it["style"]
    if s == "panel":
        lbox(b, "wall_paint", M, -w / 2, w / 2, -h / 2, h / 2, 0.0, t, bevel=0.03)
        retag_front(b, "wall_paint", fr, M, t)
        dw, dh, dt = PANEL_DOOR
        lbox(b, "wall_paint", M, -dw / 2, dw / 2, -dh / 2, dh / 2, t, t + dt, bevel=0.03)
        retag_front(b, "wall_paint", fr, M, t + dt)
        lx, lz = PANEL_LATCH
        lbox(b, "metal", M, lx - 0.55, lx + 0.55, lz - 0.55, lz + 0.55, t + dt, t + dt + 0.18)
        FACES.append((fr, it, w, h))
        return
    body = "almond" if s == "smoke" else "plate_white"
    bev = {"thermostat": 0.18, "smoke": 0.4}.get(s, 0.06)
    lbox(b, body, M, -w / 2, w / 2, -h / 2, h / 2, 0.0, t, bevel=bev, segments=1 if s != "smoke" else 2)
    retag_front(b, body, fr, M, t)
    FACES.append((fr, it, w, h))
    if s == "thermostat":
        # slider knob in the dark window (window right of centre, see textures.py)
        lbox(b, "dark", M, 0.25, 0.65, -0.35, 0.05, t, t + 0.18, bevel=0.04)
    if s == "smoke":
        # the alarm sits on a slightly larger flat mounting plate
        lbox(b, "almond", M, -w / 2 - 0.3, w / 2 + 0.3, -h / 2 - 0.3, h / 2 + 0.3, 0.0, 0.12, bevel=0.04)
    if s in ("toggle", "combo"):
        pitch = 1.8125                                      # SPEC gang spacing
        n = len(it["toggles"])
        xs = [(k - (n - 1) / 2) * pitch for k in range(n)] if s == "toggle" else [-0.906]
        lw, ll, lr = TOGGLE
        split = SPLIT_LEVERS.get(it["id"])
        for k, (x, st) in enumerate(zip(xs, it["toggles"])):
            if split:
                # its own object: origin on the pivot (plate face, lever centre), local X =
                # the plate's horizontal (right) axis, local -Y = out of the wall; the mesh is
                # built in the UP (= on) pose; +LEVER_THROW about local X tips it down (off)
                name = split[k]
                lb = common.Builder(REGIONS)
                lb.box("lever", (m(-lw / 2), -m(ll), m(-lr / 2)), (m(lw / 2), 0.0, m(lr / 2)),
                       bevel=m(0.05), segments=1, matrix=Matrix.Rotation(math.radians(-LEVER_THROW / 2), 4, "X"))
                C, r, n = frame(it)
                pivot = C + r * x + n * t
                LEVERS.append(dict(object=name, plate=it["id"], index=k + 1, pivot=pivot, facing=n,
                                   right=r, observed=st, builder=lb, M=M @ Matrix.Translation((m(x), -m(t), 0.0))))
                continue
            ang = math.radians(-LEVER_THROW / 2 if st == "up" else LEVER_THROW / 2)   # tips toward its state
            L = M @ Matrix.Translation((m(x), -m(t), 0.0)) @ Matrix.Rotation(ang, 4, "X")
            b.box("lever", (m(-lw / 2), -m(ll), m(-lr / 2)), (m(lw / 2), 0.0, m(lr / 2)),
                  bevel=m(0.05), segments=1, matrix=L)
    if s in ("combo", "gfci"):
        # the GFCI's decora face stands slightly proud of the plate
        cx = 0.906 if s == "combo" else 0.0
        lbox(b, "plate_white", M, cx - 0.66, cx + 0.66, -1.31, 1.31, t, t + 0.08)
        retag_front(b, "plate_white", fr, M, t + 0.08)


def positions():
    out = []
    for it in ITEMS + EXISTING:
        e = {"id": it["id"], "kind": it["kind"], "room": it["room"]}
        if it["wall"] == "ceiling":
            e.update(plan_x=it["plan"][0], plan_y=it["plan"][1], z=it["z"], wall="ceiling",
                     facing=[0.0, 0.0, -1.0])
        else:
            C, r, n = frame(it)
            P = C + n * PLATE_T / 2 if "existing" not in it else C
            e.update(plan_x=round(P.x, 2), plan_y=round(P.y, 2), z=it["z"],
                     wall=it["wall"], facing=[n.x, n.y])
        e["gangs"] = it["gangs"]
        if "toggles" in it:
            e["toggles"] = it["toggles"]
        if "controls" in it:
            e["controls"] = it["controls"]
        if "style" in it:
            e["size_in"] = list(item_size(it))
        e["notes"] = it["notes"]
        e["frames"] = it["frames"]
        if "existing" in it:
            e["existing"] = it["existing"]
        out.append(e)
    return out


def lever_json():
    out = []
    for L in LEVERS:
        p = L["pivot"]
        out.append({"object": L["object"], "plate": L["plate"], "index_west_to_east": L["index"],
                    "pivot": [round(p.x, 3), round(p.y, 3), round(p.z, 3)],
                    "facing": [L["facing"].x, L["facing"].y], "axis_plan": [L["right"].x, L["right"].y, 0.0],
                    "observed_state": L["observed"]})
    return out


def build(coll):
    FACES.clear()
    LEVERS.clear()
    b = common.Builder(REGIONS)
    for it in ITEMS:
        build_item(b, it)
    levers = []
    for L in LEVERS:
        ob = L["builder"].to_object(L["object"], coll)
        ob.matrix_world = L["M"]
        levers.append(ob)
    with open(os.path.join(HERE, "positions.json"), "w", encoding="utf-8") as f:
        json.dump({"frame": "plan inches; z = plate centre above the floor; facing = unit normal "
                            "out of the wall (plan x, y); plan_x/plan_y = the plate centre, half its 0.25 in thickness off the wall face",
                   "captures": {"living": "Reference/lidarseries-splat/LidarSeries_20260925_003335_763",
                                "bedroom": "Reference/bedroom-lidar-splat/LidarSeries_20260925_011425_918",
                                "bath": "Reference/bathroom-splat/LidarSeries_20260925_005649_127"},
                   "items": positions(),
                   "levers_note": "separate lever objects for the interactive switches: origin at "
                                  "'pivot' (plan inches, on the plate face at the lever centre); the "
                                  "object's local X is the plate's horizontal axis ('axis_plan', "
                                  "pointing right as seen from the room), local -Y points out of "
                                  "the wall ('facing'); the mesh is in the UP = on pose, and "
                                  "+%g deg about local X tips it DOWN = off" % LEVER_THROW,
                   "levers": lever_json()}, f, indent=1)
    return [b.to_object(NAME, coll)] + levers


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    _face_uvs(ob)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
    for lv in objs[1:]:
        common.atlas_uvs(lv, ATLAS)
        common.collapse_materials(lv, {r: mat for r in REGIONS})


def _face_uvs(ob):
    """Map each front face into its region using its own item's frame."""
    import atlas_layout
    me = ob.data
    names = [mt.name.split(".")[0] for mt in me.materials]
    uvl = me.uv_layers["UVMap"]
    for p in me.polygons:
        reg = names[p.material_index]
        cands = [f for f in FACES if f[0] == reg]
        if not cands:
            continue
        c = p.center
        best = min(cands, key=lambda f: (basis(f[1]).translation - c).length)
        _, it, w, h = best
        Mi = basis(it).inverted()
        u0, v0, u1, v1 = atlas_layout.uv_rect(ATLAS, reg, inset=0)
        for li in p.loop_indices:
            lc = Mi @ me.vertices[me.loops[li].vertex_index].co
            fu = (lc.x / IN + w / 2) / w
            fv = (lc.z / IN + h / 2) / h
            uvl.data[li].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))
