"""The shared `bathroom` atlas (bathtub, toilet, vanity). Runs inside GIMP with the
gimp_textures helpers in scope:

    python blender/lib/textures/gimp_headless.py --object bathtub

Flat fills for porcelain, acrylic, chrome, nickel, marble, mirror and wall paint, in the
albedo colours sampled by the bathroom survey (Reference/bathroom_survey/).

Photo-derived:
- oak grain: a plain stretch of the kitchen's oak cabinet door (same honey-oak species as
  the vanity), rectified, lighting-flattened and tinted to the vanity's surveyed colour.
- curtain: the pink-and-white floral print, from the bathroom capture's frame 010059
  (the curtain hanging flat over the apron), rectified upright, shading divided out by
  a blurred luminance copy (keeps the colours), made seamless as one tile. No text.

Wear, painted from what the capture shows (soft, low-contrast):
- vanity fronts: finger grime by the door pull, paler scuffed bottom edges; side panel
  scuffed and water-marked near the floor (frames 005846, 005934).
- basin (tub from above): yellowed floor edge and corners, rust flecks round the drain
  and under the spout (010120, 010259, 010303).
- unit walls (unrolled): grime along the rim joint, darker in the inside corners,
  mildew line up the corners, rust at the escutcheon and spout (010208, 010216, 010303).
- sink bowl: grimy ring and brassy stain round the drain, water spots, overflow holes.
- toilet deck: brown drips round the seat hinges on the rear rim (005949, 005952).
"""

import importlib
import os
import sys

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "bathtub")
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)
import bathroom_shared as S  # noqa: E402

importlib.reload(S)
ATLAS = S.ATLAS

OAK = (178, 104, 32)           # tint; lands at the survey albedo #9a5a1c after flattening
OAK_QUAD = [(2198, 300), (2288, 300), (2288, 460), (2198, 460)]   # plain door panel
CAPTURE = os.path.join(REF, "bathroom-splat", "LidarSeries_20260925_005649_127",
                       "COLMAP_Text_Model", "images")
# Frame 010059 is stored rotated a quarter turn; the quad is TL, TR, BR, BL of the upright
# curtain patch (left fold to just inside the right hem, about 20 x 34 in of fabric).
CURTAIN_QUAD = [(0, 1099), (0, 409), (1248, 409), (1248, 1099)]
ACRYLIC = (233, 230, 225)      # survey #e9e6e1
GRIME = (196, 172, 120)        # yellowed soap scum / caulk
RUST = (160, 92, 40)
MILDEW = (92, 84, 70)


def oak_grain(w, h):
    img = rectify(os.path.join(REF, "IMG_1498.jpg"), OAK_QUAD, w, h)
    flatten_lighting(img, 60, OAK, detail=70.0)
    return img


def curtain_print(w, h):
    img = rectify(os.path.join(CAPTURE, "wide_20260925_010059_137.jpg"), CURTAIN_QUAD, w, h)
    base = img.get_layers()[0]
    # Divide by a blurred, desaturated copy: removes the folds' shading, keeps the print.
    blur = base.copy()
    img.insert_layer(blur, None, 0)
    gegl(blur, "gegl:gaussian-blur", std_dev_x=40.0, std_dev_y=30.0)
    blur.desaturate(Gimp.DesaturateMode.LUMINANCE)
    blur.set_mode(Gimp.LayerMode.DIVIDE)
    blur.set_opacity(60.0)
    lay = flatten(img)
    gegl(lay, "gegl:saturation", scale=1.6)
    gegl(lay, "gegl:brightness-contrast", contrast=1.15, brightness=0.02)
    tint = Gimp.Layer.new(img, "tint", w, h, Gimp.ImageType.RGB_IMAGE, 100,
                          Gimp.LayerMode.MULTIPLY)
    img.insert_layer(tint, None, 0)
    Gimp.context_set_foreground(color((236, 232, 226)))
    tint.fill(Gimp.FillType.FOREGROUND)
    lay = flatten(img)
    gegl(lay, "gegl:tile-seamless")
    return img


def paste(a, src, region):
    x, y, w, h = a.rect(region)
    add_layer_from(a.img, src, region, x, y)
    a.lay = flatten(a.img)


def blot(a, region, shapes, rgb, blur, opacity, mode=None):
    """Soft stains inside a region: ellipses/rects ((kind, x0, y0, x1, y1) in region
    pixels) filled on their own layer, blurred, faded, clipped to the region, merged."""
    x, y, w, h = a.rect(region)
    lay = Gimp.Layer.new(a.img, "blot", a.size, a.size, Gimp.ImageType.RGBA_IMAGE,
                         100.0 * opacity, mode or Gimp.LayerMode.NORMAL)
    a.img.insert_layer(lay, None, 0)
    lay.fill(Gimp.FillType.TRANSPARENT)
    for kind, bx0, by0, bx1, by1 in shapes:
        box = (x + int(bx0), y + int(by0), x + int(max(bx1, bx0 + 1)), y + int(max(by1, by0 + 1)))
        if kind == "e":
            fill_ellipse(a.img, lay, box, rgb)
        else:
            fill_rect(a.img, lay, (box[0], box[1], box[2] - box[0], box[3] - box[1]), rgb)
    if blur:
        gegl(lay, "gegl:gaussian-blur", std_dev_x=blur, std_dev_y=blur)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    Gimp.Selection.invert(a.img)
    lay.edit_clear()
    Gimp.Selection.none(a.img)
    a.lay = flatten(a.img)


def flecks(rng, cx, cy, rx, ry, n, size):
    out = []
    for _ in range(n):
        px, py = cx + rng.uniform(-rx, rx), cy + rng.uniform(-ry, ry)
        s = rng.uniform(0.5, 1.0) * size
        out.append(("e", px - s, py - s * rng.uniform(0.6, 1.0), px + s, py + s))
    return out


# --- wear -----------------------------------------------------------------------------

def vanity_wear(a):
    """oak_doors: the whole front, u = local x (-25.05..25.05 in), v = z (0..30.4 in);
    oak: the side panels, u = local y (-11.35..11.35 in, front at u=0), v = z."""
    _, _, w, h = a.rect("oak_doors")
    sx, sz = w / 50.1, h / 30.4

    def P(xin, zin):          # front: local x, height -> region pixels
        return (xin + 25.05) * sx, (30.4 - zin) * sz

    # Finger grime round the door pull (door's inner edge, upper half) and the knobs.
    px, pz = P(-2.85, 18.5)
    blot(a, "oak_doors", [("e", px - 26, pz - 60, px + 14, pz + 60)], (70, 40, 14), 14, 0.35,
         Gimp.LayerMode.MULTIPLY)
    for kz in (9.35, 20.45):
        kx, kz2 = P(11.85, kz)
        blot(a, "oak_doors", [("e", kx - 22, kz2 - 16, kx + 22, kz2 + 16)], (80, 46, 16), 10,
             0.3, Gimp.LayerMode.MULTIPLY)
    # Paler, scuffed bottom edges of the door and lower drawer (feet, mop).
    x0, z0 = P(-24.2, 5.4)
    x1, _ = P(24.2, 5.4)
    blot(a, "oak_doors", [("r", x0, z0 - 2, x1, z0 + 14)], (226, 190, 140), 9, 0.18)
    blot(a, "oak_doors", flecks(random.Random(3), (x0 + x1) / 2, z0 + 6,
                                (x1 - x0) / 2, 7, 25, 2.0), (230, 200, 150), 1.5, 0.25)
    # Side panel: water marks and scuffs in the bottom few inches, worst at the front.
    _, _, w2, h2 = a.rect("oak")
    zfl = h2 * (1 - 6.0 / 30.4)
    blot(a, "oak", [("r", 0, zfl, w2 * 0.45, h2), ("e", -10, zfl - 20, w2 * 0.25, h2 - 10)],
         (206, 176, 136), 22, 0.2)
    rng = random.Random(5)
    blot(a, "oak", flecks(rng, w2 * 0.2, zfl + 30, w2 * 0.2, 30, 60, 2.0), (236, 222, 200),
         0.8, 0.3)


def basin_wear(a):
    (x0, x1, y0, y1), (cx, cy, bw, bh, br) = S.tub_basin()
    _, _, w, h = a.rect("basin")

    def P(x, y):
        return (x - x0) / (x1 - x0) * w, (1 - (y - y0) / (y1 - y0)) * h

    fx0, fy1 = P(cx - bw / 2, cy - bh / 2)
    fx1, fy0 = P(cx + bw / 2, cy + bh / 2)
    # Yellowed band where the floor turns up into the walls, heavier in the corners.
    band = [("r", fx0 - 6, fy0 - 6, fx1 + 6, fy0 + 4), ("r", fx0 - 6, fy1 - 4, fx1 + 6, fy1 + 6),
            ("r", fx0 - 6, fy0 - 6, fx0 + 4, fy1 + 6), ("r", fx1 - 4, fy0 - 6, fx1 + 6, fy1 + 6)]
    blot(a, "basin", band, GRIME, 4, 0.6)
    corners = [("e", px - 12, py - 10, px + 12, py + 10) for px in (fx0, fx1) for py in (fy0, fy1)]
    blot(a, "basin", corners, GRIME, 6, 0.65)
    # A faint yellow tide down the middle of the floor (010120) and rust round the drain.
    blot(a, "basin", [("e", fx0 + 30, (fy0 + fy1) / 2 - 10, fx1 - 20, (fy0 + fy1) / 2 + 12)],
         (210, 188, 138), 14, 0.5)
    ddx, ddy = P(cx + (bw / 2 - 3.5) * S.TUB_FAUCET_END, cy)
    rng = random.Random(11)
    blot(a, "basin", flecks(rng, ddx, ddy, 22, 16, 30, 1.6), RUST, 0.8, 0.5)
    blot(a, "basin", [("e", ddx - 9, ddy - 9, ddx + 9, ddy + 9)], (120, 100, 70), 2.5, 0.55)


def unit_wall_wear(a):
    W, L = S.TUB_W, S.TUB_L
    per = 2 * W + L
    _, _, w, h = a.rect("unit_wall")
    zr = 77.0 - S.TUB_H

    def P(s, z):
        return s / per * w, (1 - (z - S.TUB_H) / zr) * h

    # Grime along the rim joint, darker into the two inside corners.
    _, zb = P(0, S.TUB_H)
    blot(a, "unit_wall", [("r", 0, zb - 4, w, zb + 2)], GRIME, 2.0, 0.5)
    for s in (W, W + L):
        px, _ = P(s, 0)
        blot(a, "unit_wall", [("e", px - 10, zb - 12, px + 10, zb + 4)], GRIME, 3, 0.55)
        # mildew line up the corner caulk
        blot(a, "unit_wall", [("r", px - 1, P(0, 50)[1], px + 1, zb)], MILDEW, 1.0, 0.35)
    # Rust round the escutcheon rim and dribbling under the spout (faucet end wall).
    s_hw = W / 2 + 0.25
    ex, ez = P(s_hw, 34.0)
    r = 3.5 / per * w
    blot(a, "unit_wall", [("e", ex - r - 1, ez - r * 0.5, ex + r + 1, ez + r * 0.5 + 2)], RUST,
         1.2, 0.35)
    sx, sz = P(s_hw, 24.0)
    rng = random.Random(17)
    blot(a, "unit_wall", flecks(rng, sx, sz + 3, 4, 2, 10, 1.0) + [("r", sx - 1, sz, sx + 1, zb)],
         RUST, 0.7, 0.45)


def sink_wear(a):
    """sink_bowl: the vanity basin from above, 17 x 13 in oval centred in the region;
    u along the counter (+ = north), v across (+ = back, faucet side)."""
    x, y, w, h = a.rect("sink_bowl")
    cx, cy = w / 2, h / 2
    a.fill("sink_bowl", (234, 232, 226), 0.0, 0.8, noise=0.015, blur=1.2)
    # Water spots and a greyish film on the bowl floor.
    rng = random.Random(23)
    blot(a, "sink_bowl", [("e", cx - 30, cy - 22, cx + 30, cy + 26)], (200, 196, 184), 8, 0.35)
    blot(a, "sink_bowl", flecks(rng, cx, cy, 34, 26, 40, 1.2), (190, 180, 160), 0.6, 0.45)
    # Brassy grime ring round the drain (drain at the bowl's centre).
    blot(a, "sink_bowl", [("e", cx - 10, cy - 10, cx + 10, cy + 10)], (150, 118, 56), 1.5, 0.8)
    blot(a, "sink_bowl", [("e", cx - 16, cy - 16, cx + 16, cy + 16)], (170, 150, 110), 4, 0.35)
    # Overflow holes on the front wall just under the rim (front = -v = bottom rows).
    for dx in (-5, 0, 5):
        fill_ellipse(a.img, a.lay, (x + int(cx + dx - 2), y + h - 12, x + int(cx + dx + 2),
                                    y + h - 9), (60, 58, 54))


def toilet_wear(a):
    """toilet_deck: the bowl rim and rear deck from above; u = x (-7.3..7.3 in),
    v = y (front of the bowl -14.875 .. 9.4 in under the tank); toilet/object.py DECK_*."""
    x, y, w, h = a.rect("toilet_deck")
    a.fill("toilet_deck", (242, 237, 230), 0.0, 0.9, noise=0.006)

    def P(xin, yin):
        return (xin + 7.3) / 14.6 * w, (1 - (yin + 14.875) / 24.275) * h

    rng = random.Random(29)
    shapes = []
    for hx in (-2.8, 2.8):
        px, py = P(hx, 4.6)
        shapes += [("e", px - 6, py - 5, px + 6, py + 5)]
        shapes += flecks(rng, px, py + 6, 8, 6, 8, 1.4)
    blot(a, "toilet_deck", shapes, (150, 104, 50), 1.2, 0.55)
    px, py = P(0, 4.8)
    blot(a, "toilet_deck", [("r", px - 26, py - 3, px + 26, py + 3)], (180, 150, 110), 2.5, 0.3)


def build():
    a = Atlas(ATLAS)
    # Oak: photo grain for both oak regions.
    for region in ("oak", "oak_doors"):
        _, _, w, h = a.rect(region)
        g = oak_grain(w, h)
        paste(a, g, region)
        g.delete()
        a.material(region, 0.0, 0.45)       # satin lacquer
    vanity_wear(a)

    a.fill("marble", (226, 226, 221), 0.0, 0.8, noise=0.02, blur=4.0)   # survey #e2e2dd
    grain(a.img, a.lay, a.rect("marble"), 0.04, 0.6)                     # fine speckle
    a.fill("chrome", (214, 216, 220), 1.0, 0.92, noise=0.01)
    a.fill("nickel", (168, 166, 160), 1.0, 0.55, noise=0.03)            # survey #a8a6a0
    a.fill("porcelain", (242, 237, 230), 0.0, 0.9, noise=0.006)         # survey #f2ede6
    a.fill("acrylic", ACRYLIC, 0.0, 0.8, noise=0.006)
    a.fill("basin", ACRYLIC, 0.0, 0.75, noise=0.006)
    basin_wear(a)
    a.fill("unit_wall", ACRYLIC, 0.0, 0.8, noise=0.006)
    unit_wall_wear(a)
    _, _, w, h = a.rect("curtain")
    c = curtain_print(w, h)
    paste(a, c, "curtain")
    c.delete()
    a.material("curtain", 0.0, 0.2)
    a.fill("ring_red", (178, 30, 44), 0.0, 0.6, noise=0.01)
    a.fill("mirror", (188, 196, 200), 1.0, 0.97)
    a.fill("wall_paint", (207, 197, 180), 0.0, 0.18, noise=0.04, blur=1.6)  # survey #cfc5b4
    a.fill("dark", (34, 32, 30), 0.0, 0.2, noise=0.02)
    a.fill("seat", (240, 236, 229), 0.0, 0.7, noise=0.006)
    a.fill("paper", (244, 243, 238), 0.0, 0.05, noise=0.03)
    sink_wear(a)
    toilet_wear(a)
    a.save()
