"""Dresser: a solid honey-oak five-drawer chest against the east wall at the SE corner of
the bedroom. Slab drawer fronts set back between the side panels; there are no knobs:
each front has a chamfered (sloped) top edge and a bevelled underside that together read
as the dark finger-pull gap between drawers. Flush top, bottom drawer almost on the floor
over a shallow shadow recess.

The carcass is hollow (dark plain-wood interior, open between drawers as in the photos)
and every drawer is its own moving object: a real open-top box (light unfinished birch
sub-front, sides, back and bottom) behind the oak front, riding on white plastic
bottom-mount glides (photo 25 shows the white runner along the drawer side).

Source of truth: scripted from the LiDAR survey and the survey crops, refined from the
sharp capture frames wide_..011937 (front) and wide_..012006 (left side) copied to
Reference/dresser_work/src_front.jpg and src_side.jpg; drawer boxes from the open-drawer
photos Reference/cupboards_drawers (sorted index 21-25 = drawers 1-5). Origin on the floor
at the footprint centre; front faces -Y. Place at plan (264.75, 18), rotation -90 (front
faces west; local +X is south).

Moving parts (the coordinator's Unity setup relies on these names):
  dresser                    static carcass (root)
  dresser_drawer_1 .. _5     drawers, 1 = top .. 5 = bottom; origin at the box centre
  dresser_drawer_<n>_grab    empty at the sloped top edge of each front (finger pull);
                             the drawer slides along local -Y toward it
Contents are the separate `dresser_contents` package (dresser_drawer_<n>_contents).

Dimensions (inches):
  width 34, depth 19.5, height 58.5     SCAN (survey box 254-274.5 x 0.5-36, top 58-59.7)
  side/top panel thickness 0.75          EST (photo: edge ~ 1/45 of the width)
  base recess 0.75 tall, 0.4 deep        EST from photo (bottom drawer nearly on the floor)
  5 equal drawers, 0.25 gaps             EST from photo (equal heights)
  drawer fronts 0.8 thick, set back 0.35 EST from photo (shadow line inside the sides)
  top chamfer 0.25, underside bevel 0.55 EST from photo (light line over a dark gap)
  drawer box 31.5 W x 17 D, sides 0.5    EST from photos 21-25 (box nearly fills the
                                         carcass; ~0.5 each side for the glides)
  box sides 1.0 below the front top and  EST from photos 21-22 (side top a little under
    1.0 above the front bottom                 the sloped front edge)
  box bottom 0.25, sub-front 0.5         EST
  glides: drawer member 0.45 x 0.9,      EST from photo 25 (white runner low on the side)
    carcass rail 0.5 x 0.6 under it
"""

import common

IN = 0.0254


def m(v):
    return v * IN


NAME = "dresser"
W, D, H = 34.0, 19.5, 58.5
T = 0.75
KICK, KICK_IN = 0.75, 0.4
N_DRAWERS = 5
GAP = 0.25
FRONT_T, FRONT_SET = 0.8, 0.35
CHAMFER, UNDERCUT = 0.25, 0.55
BACK_T = 0.3
BOX_SIDE = 0.5          # drawer box side/back thickness
BOX_BOT = 0.25          # drawer box bottom
SUB_FRONT = 0.5         # birch sub-front behind the oak front
BOX_D = 17.0            # drawer box depth behind the oak front
BOX_TOP_DROP = 1.0      # box sides stop this far under the front's top edge
BOX_BOT_RISE = 1.0      # box bottom this far over the front's bottom edge
GLIDE_W, GLIDE_H = 0.45, 0.9
RAIL_W, RAIL_H = 0.5, 0.6

ATLAS = {
    "name": "dresser",
    "size": 1024,
    "regions": {
        "front": (0, 0, 512, 1024),      # photo drawer fronts, planar over the whole front
        "top": (512, 0, 512, 320),       # photo grain along X
        "side": (512, 320, 256, 704),    # photo side panel, vertical grain
        "dark": (768, 320, 128, 128),    # gaps, back, base recess
        "edge": (896, 320, 128, 128),    # panel front edges (worn, lighter)
        "birch": (768, 448, 256, 384),   # drawer boxes: light unfinished birch
        "glide": (768, 832, 128, 128),   # white plastic glides
        "interior": (896, 832, 128, 128),  # carcass inside: plain darker wood
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"dresser": {"atlas": "dresser", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True           # the carcass; the dresser_drawer_<n> objects move
VIEWS = [("photo_front", 340, 15, 1.0), ("photo_left", 300, 15, 1.0),
         ("photo_high", 330, 30, 0.75)]

X0, X1, Y0, Y1 = -W / 2, W / 2, -D / 2, D / 2
FY0 = Y0 + FRONT_SET            # front face of the drawer fronts
FY1 = FY0 + FRONT_T             # back of the oak fronts
BX0, BX1 = -(W / 2 - T - RAIL_W), W / 2 - T - RAIL_W   # drawer box outer x


def drawer_rows():
    """(z_bottom, z_top) of each front, bottom drawer first (drawer 5 .. 1)."""
    ih = (H - T - KICK - GAP * N_DRAWERS) / N_DRAWERS
    return [(KICK + GAP / 2 + i * (ih + GAP), KICK + GAP / 2 + i * (ih + GAP) + ih)
            for i in range(N_DRAWERS)]


def drawer_front(n):
    """(z_bottom, z_top) of drawer n (1 = top)."""
    return drawer_rows()[N_DRAWERS - n]


def drawer_box(n):
    """Drawer n's box in dresser-local inches: (x0, x1, y0, y1, z0, z1) outer bounds
    (y0 = back of the oak front)."""
    z0, z1 = drawer_front(n)
    return (BX0, BX1, FY1, FY1 + BOX_D, z0 + BOX_BOT_RISE, z1 - BOX_TOP_DROP)


def drawer_interior(n):
    """Inside of drawer n's box (x0, x1, y0, y1, z_floor, z_top_edge), dresser-local inches.
    The contents package fills this."""
    x0, x1, y0, y1, z0, z1 = drawer_box(n)
    return (x0 + BOX_SIDE, x1 - BOX_SIDE, y0 + SUB_FRONT, y1 - BOX_SIDE, z0 + BOX_BOT, z1)


def drawer_origin(n):
    """Drawer n's object origin (inches): centre of its box footprint at mid front height."""
    x0, x1, y0, y1, _, _ = drawer_box(n)
    z0, z1 = drawer_front(n)
    return ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def _retag_inward(b, faces, region, normal):
    """Re-tag the faces of a closed panel whose normal matches `normal` (the side facing
    into the carcass) with `region`."""
    b.bm.normal_update()
    for f in faces:
        if f.is_valid and f.normal.dot(normal) > 0.9:
            f.material_index = b.idx(region)


def build_carcass(coll):
    from mathutils import Vector
    b = common.Builder(REGIONS)
    bx = lambda r, lo, hi, bev=0.0, seg=2: b.box(r, tuple(map(m, lo)), tuple(map(m, hi)),
                                                 bevel=m(bev), segments=seg)
    # sides (slightly eased front edges), their inner faces plain dark wood
    fl = bx("side", (X0, Y0, 0), (X0 + T, Y1, H - T), 0.06, 1)
    fr = bx("side", (X1 - T, Y0, 0), (X1, Y1, H - T), 0.06, 1)
    _retag_inward(b, fl, "interior", Vector((1, 0, 0)))
    _retag_inward(b, fr, "interior", Vector((-1, 0, 0)))
    ft = bx("top", (X0, Y0, H - T), (X1, Y1, H), 0.12)
    _retag_inward(b, ft, "interior", Vector((0, 0, -1)))
    # back panel and bottom panel (inside: plain wood)
    fb = bx("dark", (X0 + T, Y1 - BACK_T, 0), (X1 - T, Y1, H - T))
    _retag_inward(b, fb, "interior", Vector((0, -1, 0)))
    bx("dark", (X0 + T, FY0 + KICK_IN, 0), (X1 - T, FY0 + KICK_IN + 0.5, KICK))   # base recess
    bx("interior", (X0 + T, FY0 + KICK_IN + 0.5, KICK - 0.5), (X1 - T, Y1 - BACK_T, KICK))
    # thin rail under the top, set back like the fronts
    bx("edge", (X0 + T, FY0 - 0.05, H - T - 0.1), (X1 - T, FY1, H - T))
    # white glide rails on the inner side walls, under each drawer's glide
    for n in range(1, N_DRAWERS + 1):
        _, _, _, _, z0, _ = drawer_box(n)
        for xa, xb in ((X0 + T, X0 + T + RAIL_W), (X1 - T - RAIL_W, X1 - T)):
            bx("glide", (xa, FY1 + 0.3, z0 - RAIL_H), (xb, Y1 - BACK_T, z0), 0.05, 1)
    return b.to_object(NAME, coll)


def build_drawer(coll, n):
    b = common.Builder(REGIONS)
    bx = lambda r, lo, hi, bev=0.0, seg=2: b.box(r, tuple(map(m, lo)), tuple(map(m, hi)),
                                                 bevel=m(bev), segments=seg)
    z0, z1 = drawer_front(n)
    h = z1 - z0
    # oak front: a slab profile swept along X, sloped top edge, bevelled underside
    fx0, fx1 = X0 + T + GAP / 2, X1 - T - GAP / 2
    prof = [(0.0, 0.0), (FRONT_T - UNDERCUT, 0.0), (FRONT_T, UNDERCUT * 0.8),
            (FRONT_T, h - CHAMFER), (FRONT_T - CHAMFER, h), (0.0, h)]
    b.sweep("front", [(m(fx0), m(FY1), m(z0)), (m(fx1), m(FY1), m(z0))],
            [(m(s), m(u)) for s, u in prof])
    # open-top birch box: sub-front, sides, back, bottom (each a closed panel)
    x0, x1, y0, y1, bz0, bz1 = drawer_box(n)
    s, bt = BOX_SIDE, BOX_BOT
    bx("birch", (x0, y0, bz0), (x1, y0 + SUB_FRONT, bz1), 0.04, 1)
    bx("birch", (x0, y0, bz0), (x0 + s, y1, bz1), 0.04, 1)
    bx("birch", (x1 - s, y0, bz0), (x1, y1, bz1), 0.04, 1)
    bx("birch", (x0 + s, y1 - s, bz0), (x1 - s, y1, bz1), 0.04, 1)
    bx("birch", (x0 + s, y0 + SUB_FRONT, bz0), (x1 - s, y1 - s, bz0 + bt))
    # white glide members low on each side, riding on the carcass rails
    for xa, xb in ((x0 - GLIDE_W, x0), (x1, x1 + GLIDE_W)):
        bx("glide", (xa, y0 + 0.4, bz0), (xb, y1 - 0.2, bz0 + GLIDE_H), 0.05, 1)
    org = drawer_origin(n)
    ob = b.to_object(f"{NAME}_drawer_{n}", coll, origin=tuple(map(m, org)))
    # grab marker on the sloped top edge of the front (the finger pull)
    marker(coll, f"{NAME}_drawer_{n}_grab",
           (0.0, m(FY0 + CHAMFER * 0.5), m(z1 - CHAMFER * 0.5)))
    return ob


def marker(coll, name, loc):
    import bpy
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.03
    ob.location = loc
    coll.objects.link(ob)
    return ob


def build(coll):
    import bpy
    body = build_carcass(coll)
    drawers = [build_drawer(coll, n) for n in range(1, N_DRAWERS + 1)]
    grabs = [bpy.data.objects[f"{NAME}_drawer_{n}_grab"] for n in range(1, N_DRAWERS + 1)]
    return [body] + drawers + grabs


def texture(objs):
    mat = common.atlas_material(NAME, ATLAS)
    for ob in objs:
        if ob.type != "MESH":
            continue
        # the front photo is mapped planar over the whole dresser front, in object space
        ox, _, oz = ob.location
        planar = {"front": ("-Y", (m(X0) - ox, m(X1) - ox), (-oz, m(H) - oz))}
        common.atlas_uvs(ob, ATLAS, planar=planar)
        common.collapse_materials(ob, {r: mat for r in REGIONS})
