"""Filing cabinet: 2-drawer vertical letter file, putty paint (bedroom).

Source of truth: scripted. Dimensions come from dimensions.CABINET (estimates until
measured). Object origin is the floor at the center of the footprint; front faces -Y.

Objects:
  filing_cabinet_body      static shell: sides, back, top cap, base, frame, slides
  filing_cabinet_drawer_1  top drawer (moves); origin on its face, slides along -Y
  filing_cabinet_drawer_2  bottom drawer (moves)
  corner_guard_fl / _fr    white L-shaped corner protectors on the front top corners
"""

import importlib

import common
import dimensions

importlib.reload(common)
importlib.reload(dimensions)

C = dimensions.CABINET
REGIONS_BODY = ["paint", "slide_steel", "interior"]
REGIONS_DRAWER = ["paint", "nickel", "blue_anodized", "lock_face", "slide_steel"]
REGIONS_GUARD = ["guard_plastic"]


def drawer_faces():
    """(z_bottom, z_top) of each drawer face, top drawer first."""
    H, gap = C["height"], C["gap"]
    top = H - C["top_rail"]
    avail = top - C["base"] - gap          # one gap between the two faces
    fh = avail / 2
    d1 = (top - fh, top)
    d2 = (d1[0] - gap - fh, d1[0] - gap)
    return [d1, d2]


def build_body(coll):
    W, D, H = C["width"], C["depth"], C["height"]
    wrap = C["top_wrap"]
    b = common.Builder(REGIONS_BODY)
    y0, y1 = -D / 2, D / 2
    # Side panels and back (outer skins), stopping under the top cap's wrap.
    b.box("paint", (-W / 2, y0, 0), (-W / 2 + 0.012, y1, H - wrap), bevel=0.001)
    b.box("paint", (W / 2 - 0.012, y0, 0), (W / 2, y1, H - wrap), bevel=0.001)
    b.box("paint", (-W / 2 + 0.012, y1 - 0.012, 0), (W / 2 - 0.012, y1, H - wrap))
    # Top cap: the lid plus a skirt that wraps down the sides and back, a hair proud
    # of the panels so its lower edge reads as the seam in the photos.
    p = 0.0012
    b.box("paint", (-W / 2 - p, y0 - p, H - 0.012), (W / 2 + p, y1 + p, H), bevel=0.0025)
    b.box("paint", (-W / 2 - p, y0 - p, H - wrap), (-W / 2 + 0.004, y1 + p, H - 0.006), bevel=0.001)
    b.box("paint", (W / 2 - 0.004, y0 - p, H - wrap), (W / 2 + p, y1 + p, H - 0.006), bevel=0.001)
    b.box("paint", (-W / 2 - p, y1 - 0.004, H - wrap), (W / 2 + p, y1 + p, H - 0.006), bevel=0.001)
    # Front frame: top rail, stiles, base kick, and the rail behind the drawer gap.
    st, fr = C["stile"], 0.02
    b.box("paint", (-W / 2, y0, H - C["top_rail"] - 0.004), (W / 2, y0 + fr, H - 0.006))
    b.box("paint", (-W / 2, y0, 0), (-W / 2 + st, y0 + fr, H - 0.006), bevel=0.0015)
    b.box("paint", (W / 2 - st, y0, 0), (W / 2, y0 + fr, H - 0.006), bevel=0.0015)
    b.box("paint", (-W / 2, y0, 0), (W / 2, y0 + fr, C["base"]), bevel=0.0015)
    (d1b, _), (_, d2t) = drawer_faces()
    b.box("interior", (-W / 2 + st, y0 + 0.006, d2t), (W / 2 - st, y0 + fr, d1b))
    # Floor pan inside, and dark interior walls so an open drawer shows depth.
    b.box("interior", (-W / 2 + 0.012, y0 + fr, 0.01), (W / 2 - 0.012, y1 - 0.012, 0.02))
    b.box("interior", (-W / 2 + 0.012, y0 + fr, H - 0.014), (W / 2 - 0.012, y1 - 0.012, H - 0.012))
    # Slide rails on the inner walls for each drawer.
    for zb, zt in drawer_faces():
        z = zb + 0.03
        for sx in (-1, 1):
            x_in = sx * (W / 2 - 0.012)
            xa, xb = sorted((x_in, x_in - sx * 0.012))
            b.box("slide_steel", (xa, y0 + fr, z), (xb, y1 - 0.02, z + 0.03))
    return b.to_object("filing_cabinet_body", coll)


def build_drawer(coll, index, zb, zt, with_lock):
    W, D = C["width"], C["depth"]
    st, gap = C["stile"], C["gap"]
    fw = W - 2 * st - 2 * gap
    fh = zt - zb
    y_face = -D / 2 - C["face_proud"]
    zc = (zb + zt) / 2
    b = common.Builder(REGIONS_DRAWER)
    # Face: a shallow pan with rounded edges.
    b.box("paint", (-fw / 2, y_face, zb), (fw / 2, y_face + 0.02, zt), bevel=0.003, segments=3)
    # Box behind the face: sides, bottom, back; open at the top for files.
    bw, bd, bh = C["drawer_box_width"], C["drawer_box_depth"], C["drawer_box_height"]
    by0, by1 = y_face + 0.02, y_face + 0.02 + bd
    bz0 = zb + 0.015
    s = 0.0015
    b.box("paint", (-bw / 2, by0, bz0), (-bw / 2 + s, by1, bz0 + bh))
    b.box("paint", (bw / 2 - s, by0, bz0), (bw / 2, by1, bz0 + bh))
    b.box("paint", (-bw / 2, by0, bz0), (bw / 2, by1, bz0 + s))
    b.box("paint", (-bw / 2, by1 - s, bz0), (bw / 2, by1, bz0 + bh))
    # Hanging-file rails along the top of the sides.
    for sx in (-1, 1):
        x = sx * (bw / 2 - 0.004)
        b.box("paint", (x - 0.004, by0, bz0 + bh - 0.004), (x + 0.004, by1, bz0 + bh))
    # Drawer-side slide members (mate with the body's rails).
    for sx in (-1, 1):
        xa, xb = sorted((sx * bw / 2, sx * (bw / 2 + 0.012)))
        b.box("slide_steel", (xa, by0 + 0.01, zb + 0.032), (xb, by1, zb + 0.056))

    yf = y_face  # front plane of the face
    # Label holder: blue anodized frame, open in the middle.
    lw, lh, lf = C["label_w"], C["label_h"], C["label_frame"]
    lz = zt - C["label_center_from_top"]
    t = 0.0022
    for lo, hi in (((-lw / 2, lz + lh / 2 - lf), (lw / 2, lz + lh / 2)),
                   ((-lw / 2, lz - lh / 2), (lw / 2, lz - lh / 2 + lf)),
                   ((-lw / 2, lz - lh / 2), (-lw / 2 + lf, lz + lh / 2)),
                   ((lw / 2 - lf, lz - lh / 2), (lw / 2, lz + lh / 2))):
        b.box("blue_anodized", (lo[0], yf - t, lo[1]), (hi[0], yf, hi[1]), bevel=0.0008)
    # Pull: U-shaped bar with rounded corners, posts into the face.
    hw, bar, so = C["handle_w"], C["handle_bar"], C["handle_standoff"]
    hz = zt - C["handle_center_from_top"]
    r = 0.009
    pts = [(-hw / 2, yf + 0.002, hz), (-hw / 2, yf - so + r, hz), (-hw / 2 + r * 0.3, yf - so + r * 0.3, hz),
           (-hw / 2 + r, yf - so, hz), (hw / 2 - r, yf - so, hz), (hw / 2 - r * 0.3, yf - so + r * 0.3, hz),
           (hw / 2, yf - so + r, hz), (hw / 2, yf + 0.002, hz)]
    prof = [(x * 0.8, y * 1.35) for x, y in common.circle_profile(bar / 2, 10)]   # flat oval bar
    b.sweep("nickel", common.smooth_path(pts, 4), prof, up=(0, 0, 1))
    for sx in (-1, 1):   # mounting bosses
        b.cylinder("nickel", (sx * hw / 2, yf - 0.002, hz), bar * 0.75, 0.004, axis="Y", segments=12)
    # Thumb latch: small block left of the pull.
    lw_, lh_, ld_ = C["latch_w"], C["latch_h"], C["latch_d"]
    lx = -hw / 2 - 0.012 - lw_ / 2
    b.box("nickel", (lx - lw_ / 2, yf - ld_, hz - lh_ / 2), (lx + lw_ / 2, yf, hz + lh_ / 2), bevel=0.0015)
    if with_lock:
        lx = fw / 2 - C["lock_from_right"]
        lzz = zt - C["lock_from_top"]
        b.cylinder("nickel", (lx, yf - C["lock_proud"] / 2, lzz), C["lock_d"] / 2, C["lock_proud"],
                   axis="Y", segments=20, cap_region="lock_face", bevel=0.0008)
    ob = b.to_object(f"filing_cabinet_drawer_{index}", coll, origin=(0, y_face, zc))
    # Marker at the pull's grip: Unity turns it into the drawer's invisible grab handle.
    marker(coll, f"filing_cabinet_drawer_{index}_grab", (0, yf - so + bar / 2, hz))
    return ob


def marker(coll, name, loc):
    import bpy
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.03
    ob.location = loc
    coll.objects.link(ob)
    return ob


def build_guard(coll, side):
    """Rounded L corner cap over a top front corner; side = -1 (left) or +1 (right)."""
    W, D, H = C["width"], C["depth"], C["height"]
    leg, wrap, gt = C["guard_leg"], C["guard_wrap"], C["guard_thick"]
    x_edge, y_edge = side * W / 2, -D / 2
    b = common.Builder(REGIONS_GUARD)
    xo = x_edge + side * gt      # outer face beyond the side panel
    yo = y_edge - gt             # outer face in front of the front panel
    xl = x_edge - side * leg     # end of the leg running along the front edge
    ye = y_edge + leg            # end of the leg running back along the side
    bev = gt * 0.45
    # top plates (L), front skirt, side skirt
    b.box("guard_plastic", (min(xo, xl), yo, H), (max(xo, xl), y_edge + wrap, H + gt), bevel=bev)
    b.box("guard_plastic", (min(xo, x_edge - side * wrap), yo, H), (max(xo, x_edge - side * wrap), ye, H + gt), bevel=bev)
    b.box("guard_plastic", (min(xo, xl), yo, H - wrap), (max(xo, xl), y_edge, H + gt), bevel=bev)
    b.box("guard_plastic", (min(xo, x_edge), yo, H - wrap), (max(xo, x_edge), ye, H + gt), bevel=bev)
    name = "corner_guard_fl" if side < 0 else "corner_guard_fr"
    return b.to_object(name, coll, origin=(x_edge, y_edge, H))


def build(coll):
    body = build_body(coll)
    faces = drawer_faces()
    drawers = [build_drawer(coll, i + 1, zb, zt, with_lock=(i == 0)) for i, (zb, zt) in enumerate(faces)]
    guards = [build_guard(coll, -1), build_guard(coll, 1)]
    # Where each item sits on the top (Unity parents the item prefabs here).
    import math
    for key, (x, y, rot) in dimensions.PLACEMENT.items():
        m = marker(coll, f"place_{key}", (x, y, C["height"]))
        m.rotation_euler = (0, 0, math.radians(rot))
    return body, drawers, guards


def texture(body, drawers, guards):
    paint = common.atlas_material("cabinet_paint", "cabinet_paint", tiled=True)
    hw = common.atlas_material("cabinet_hardware", "cabinet_hardware")
    interior = bpy_interior_material()
    tile = 0.5   # meters per paint tile
    common.atlas_uvs(body, "cabinet_hardware", tiled={"paint": tile, "interior": tile})
    common.collapse_materials(body, {"paint": paint, "interior": interior, "slide_steel": hw})
    for d in drawers:
        common.atlas_uvs(d, "cabinet_hardware", tiled={"paint": tile},
                         planar={"lock_face": ("-Y", (d_lock_x(d) - C["lock_d"] / 2, d_lock_x(d) + C["lock_d"] / 2),
                                               (d_lock_z(d) - C["lock_d"] / 2, d_lock_z(d) + C["lock_d"] / 2))})
        common.collapse_materials(d, {"paint": paint, "nickel": hw, "blue_anodized": hw,
                                      "lock_face": hw, "slide_steel": hw})
    for g in guards:
        common.atlas_uvs(g, "cabinet_hardware")
        common.collapse_materials(g, {"guard_plastic": hw})


def d_lock_x(drawer):
    W = C["width"]
    fw = W - 2 * C["stile"] - 2 * C["gap"]
    return fw / 2 - C["lock_from_right"]


def d_lock_z(drawer):
    zb, zt = drawer_faces()[0]
    return zt - C["lock_from_top"] - (zb + zt) / 2   # drawer-local (origin at face center)


def bpy_interior_material():
    """The cabinet's inside reads as the same paint in shadow; reuse the paint texture
    darkened, rather than another atlas."""
    import bpy
    mat = common.atlas_material("cabinet_interior", "cabinet_paint", tiled=True)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    alb = next(n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")
    mix = mat.node_tree.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    mix.inputs["B"].default_value = (0.55, 0.55, 0.55, 1)
    mat.node_tree.links.new(alb.outputs["Color"], mix.inputs["A"])
    mat.node_tree.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    return mat
