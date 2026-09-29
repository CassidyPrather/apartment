"""Desk: dark cherry/mahogany office desk with a three-drawer pedestal (two box drawers
over a file drawer) at one end, a recessed modesty panel and a flat end panel leg at
the other end. Glossy finish, brushed-nickel tapered cup pulls on the top rail of each drawer.

Source of truth: scripted from the bedroom survey (LiDAR + splat, registered in plan
inches) and the survey crops. Origin on the floor at the footprint centre; the front
(where you sit) faces -Y. In the room it stands against the south wall facing north, so
it is placed with rotation 180: local +X (the pedestal end) is world west.

Placement: plan (175.4, 14.5), rotation 180.
"""

import common

IN = 0.0254


def m(v):
    return v * IN


W = 71.0            # SCAN top x 139.4..210.8
D = 28.5            # SCAN top y 0.4..27.3 (+ edge), brief 28.5
H = 29.5            # SCAN top surface peak z 28-29.5 (brief said 30)
TOP_T = 1.4         # EST photo: thick bullnosed top
PED_W = 19.0        # SCAN knee space starts ~world x 159 (pedestal x 140..159)
PED_SET = 1.0       # EST photo: top overhangs the drawer faces ~1 in
PLINTH = 2.5        # EST photo: low recessed plinth under the file drawer
DRAWERS = (6.6, 7.0, 11.4)   # EST photo ratios 85:90:140 of the drawer zone, top first
GAP = 0.18          # EST drawer reveal
FRONT_T = 0.75      # EST drawer front thickness
END_T = 1.2         # EST end panel thickness
END_IN = 2.2        # SCAN end panel at world x ~208 vs top end 210.8
MODESTY_Y = 5.7     # SCAN modesty panel plane at world y ~8.8 (local +5.7 from centre)
MODESTY_Z = (3.0, H - TOP_T)  # EST photo: reaches nearly to the floor
PULL = (5.2, 3.9, 1.15, 0.6)   # EST photo: tapered cup pull, top w, bottom w, h, projection
PULL_DOWN = 1.15             # EST photo: pull centre below the drawer top (on the top rail)
PANEL_IN = (1.3, 2.3)        # EST photo: raised panel inset (sides/bottom, top rail)

NAME = "desk"
ATLAS = {
    "name": "desk",
    "size": 1024,
    "regions": {
        "wood_top": (0, 0, 1024, 384),
        "wood_v": (0, 384, 512, 640),
        "wood_drawer": (512, 384, 512, 384),
        "pull": (512, 768, 128, 128),
        "shadow": (640, 768, 128, 128),
        "raised": (768, 768, 256, 256),
    },
}
REGIONS = list(ATLAS["regions"])
MATERIALS = {"desk": {"atlas": "desk", "mode": "opaque", "tiled": False}}
COLLIDER = "box"
STATIC = True
VIEWS = [("photo_front_r", 20, 30, 0.75), ("photo_front_l", 335, 35, 0.8)]


def build(coll):
    b = common.Builder(REGIONS)
    bx = lambda r, a, c, bev=0.0, seg=1: b.box(r, tuple(map(m, a)), tuple(map(m, c)),
                                               bevel=m(bev), segments=seg)
    x0, x1 = -W / 2, W / 2
    y0, y1 = -D / 2, D / 2
    zt = H - TOP_T
    # top, bullnosed
    bx("wood_top", (x0, y0, zt), (x1, y1, H), 0.45, 2)
    # pedestal carcass at +X (world west)
    px0, px1 = x1 - PED_W, x1 - 0.3
    pf = y0 + PED_SET + FRONT_T                 # carcass front plane
    bx("wood_v", (px0, pf, 0.0), (px0 + 0.9, y1 - 0.5, zt), 0.1)       # inner side
    bx("wood_v", (px1 - 0.9, pf, 0.0), (px1, y1 - 0.5, zt), 0.1)       # outer side
    bx("wood_v", (px0 + 0.9, y1 - 1.2, 0.0), (px1 - 0.9, y1 - 0.5, zt))  # back
    bx("shadow", (px0 + 0.9, pf + 0.6, 0.0), (px1 - 0.9, pf + 1.2, PLINTH))  # plinth (recessed)
    bx("shadow", (px0 + 0.9, pf, PLINTH), (px1 - 0.9, pf + 0.3, zt))       # face frame behind the fronts
    # drawer fronts, top down, each with a raised centre panel and a pull
    z = zt - GAP
    for hgt in DRAWERS:
        za, zb = z - hgt, z
        fx0, fx1 = px0 + 0.1, px1 - 0.1
        bx("wood_drawer", (fx0, pf - FRONT_T, za), (fx1, pf, zb), 0.12)
        ins, ins_top = PANEL_IN
        bx("raised", (fx0 + ins, pf - FRONT_T - 0.18, za + ins), (fx1 - ins, pf - FRONT_T + 0.05, zb - ins_top), 0.25, 1)
        cup_pull(b, (fx0 + fx1) / 2, pf - FRONT_T, zb - PULL_DOWN)
        z = za - GAP
    # end panel leg at -X (world east)
    ex = x0 + END_IN
    bx("wood_v", (ex, y0 + 0.9, 0.0), (ex + END_T, y1 - 0.5, zt), 0.2)
    # modesty panel spanning the knee space
    my = MODESTY_Y
    bx("wood_v", (ex + END_T, my, MODESTY_Z[0]), (px0, my + 0.75, MODESTY_Z[1]))
    # front apron under the top edge across the knee space (photo: thick edge band)
    bx("wood_top", (ex + END_T, y0 + 0.6, zt - 1.6), (px0, y0 + 1.4, zt))
    return [b.to_object(NAME, coll)]


def cup_pull(b, cx, yf, pz):
    """Brushed-nickel cup (bin) pull, photo: a trapezoid face (long straight top edge,
    chamfered ends) that leans out toward the bottom, open underneath (dark cup)."""
    tw, bw, h, proj = PULL
    top, bot = pz + h / 2, pz - h / 2
    back = [(-tw / 2, top), (tw / 2, top), (bw / 2, bot), (-bw / 2, bot)]
    # face: top edge 0.18 proud, bottom edge `proj` proud, a mid row for a gentle curve
    mid_z = pz - h * 0.1
    rows = [(top, 0.18, tw), (mid_z, proj * 0.8, (tw + bw) / 2 + 0.1), (bot, proj, bw)]
    bm = b.bm
    V = lambda x, y, z: bm.verts.new((m(x), m(y), m(z)))
    front = [(V(cx - w / 2, yf - d, z), V(cx + w / 2, yf - d, z)) for z, d, w in rows]
    rear = [(V(cx - w / 2, yf, z), V(cx + w / 2, yf, z)) for z, d, w in rows]
    f = []
    nf = bm.faces.new
    for i in range(len(rows) - 1):
        (a, c), (a2, c2) = front[i], front[i + 1]
        f.append(nf((a, c, c2, a2)))                       # hood face
        (ra, rc), (ra2, rc2) = rear[i], rear[i + 1]
        f.append(nf((ra, a, a2, ra2)))                      # left end
        f.append(nf((c, rc, rc2, c2)))                      # right end
        f.append(nf((ra2, rc2, rc, ra)))                    # back plate (closes the shell)
    f.append(nf((rear[0][0], rear[0][1], front[0][1], front[0][0])))   # top
    b._tag(f, "pull")
    cup = nf((front[-1][0], front[-1][1], rear[-1][1], rear[-1][0]))   # the open cup, dark
    b._tag([cup], "shadow")


def texture(objs):
    ob = objs[0]
    mat = common.atlas_material(NAME, ATLAS)
    common.atlas_uvs(ob, ATLAS)
    common.collapse_materials(ob, {r: mat for r in REGIONS})
