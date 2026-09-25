"""Build the filing-cabinet set's texture atlases in GIMP 3.

Runs inside GIMP's Python (through the GIMP MCP's pyGObject console, or the Python-Fu
console):

    exec(open(r"<repo>/blender/lib/textures/gimp_textures.py").read(), {"ROOT": r"<repo>", "RUN": True})

or headless, one builder or several at a time:

    python blender/lib/textures/gimp_headless.py router modem

Every pixel operation happens in GIMP: photo regions are perspective-corrected with
the transform tool, shading is flattened with a divide-by-blur layer, tiles are made
seamless with gegl:tile-seamless, and the parody logos (logos/*.svg) are loaded and
composited as layers. Photo-derived regions read the local-only Reference/ photos.

Output in Assets/Apartment/Textures/: <atlas>_albedo.png, <atlas>_mask.png (metallic in
R, smoothness in A, as VRChat's Standard Lite expects) and <atlas>_emission.png where
something glows. Each image stays open in GIMP so it can be inspected.
"""

import math
import os
import random
import sys

from gi.repository import Gegl, Gimp, Gio

ROOT = globals().get("ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
LIB = os.path.join(ROOT, "blender", "lib")
if LIB not in sys.path:
    sys.path.insert(0, LIB)
import importlib  # noqa: E402

import atlas_layout  # noqa: E402

importlib.reload(atlas_layout)
ATLAS_SIZE, LAYOUT = atlas_layout.ATLAS_SIZE, atlas_layout.LAYOUT

REF = os.path.join(ROOT, "Reference")
LOGOS = os.path.join(LIB, "textures", "logos")
OUT = os.path.join(ROOT, "Assets", "Apartment", "Textures")
SHOW = globals().get("SHOW", True)
random.seed(1492)

NONINT = Gimp.RunMode.NONINTERACTIVE


# --- GIMP helpers ----------------------------------------------------------------

def color(spec):
    """(r, g, b) or (r, g, b, alpha) with 0-255 sRGB channels and 0-1 alpha.

    GEGL's rgb()/rgba() strings take 0-1 floats, so 0-255 values would clamp to white;
    hex strings are unambiguous.
    """
    if isinstance(spec, tuple):
        a = round(spec[3] * 255) if len(spec) == 4 else 255
        spec = "#%02x%02x%02x%02x" % (spec[0], spec[1], spec[2], a)
    return Gegl.Color.new(spec)


def load(path):
    return Gimp.file_load(NONINT, Gio.File.new_for_path(path))


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    flat = img.duplicate()
    flat.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    Gimp.file_save(NONINT, flat, Gio.File.new_for_path(path), None)
    flat.delete()
    print("wrote", os.path.relpath(path, ROOT))


def new_image(w, h, name, alpha=False):
    img = Gimp.Image.new(w, h, Gimp.ImageBaseType.RGB)
    kind = Gimp.ImageType.RGBA_IMAGE if alpha else Gimp.ImageType.RGB_IMAGE
    lay = Gimp.Layer.new(img, name, w, h, kind, 100, Gimp.LayerMode.NORMAL)
    img.insert_layer(lay, None, 0)
    if alpha:
        lay.fill(Gimp.FillType.TRANSPARENT)
    else:
        Gimp.context_set_background(color((0, 0, 0)))
        lay.fill(Gimp.FillType.BACKGROUND)
    if SHOW:
        Gimp.Display.new(img)
    return img, lay


def gegl(drawable, op, **props):
    f = Gimp.DrawableFilter.new(drawable, op, "")
    cfg = f.get_config()
    for k, v in props.items():
        cfg.set_property(k.replace("_", "-"), v)
    drawable.merge_filter(f)


def fill_rect(img, drawable, rect, rgb):
    """Fill a rect; a 4th component (0-1) becomes the fill opacity, which on a
    transparent layer is the resulting alpha (GIMP ignores alpha in the fill color)."""
    x, y, w, h = rect
    img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    _fill(drawable, rgb)
    Gimp.Selection.none(img)


def _fill(drawable, rgb):
    Gimp.context_set_foreground(color(tuple(rgb[:3])))
    Gimp.context_set_opacity(100.0 * (rgb[3] if len(rgb) == 4 else 1.0))
    drawable.edit_fill(Gimp.FillType.FOREGROUND)
    Gimp.context_set_opacity(100.0)


def fill_ellipse(img, drawable, box, rgb):
    x0, y0, x1, y1 = box
    img.select_ellipse(Gimp.ChannelOps.REPLACE, x0, y0, x1 - x0, y1 - y0)
    # An ellipse entirely off-canvas leaves an empty selection, and filling with an
    # empty selection fills the whole layer; skip it.
    if not Gimp.Selection.is_empty(img):
        _fill(drawable, rgb)
    Gimp.Selection.none(img)


def fill_round_rect(img, drawable, box, radius, rgb):
    x0, y0, x1, y1 = box
    img.select_round_rectangle(Gimp.ChannelOps.REPLACE, x0, y0, x1 - x0, y1 - y0, radius, radius)
    _fill(drawable, rgb)
    Gimp.Selection.none(img)


def grain(img, drawable, rect, amount, size=1.0):
    """Monochrome noise inside rect, softened to `size` px."""
    x, y, w, h = rect
    img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(drawable, "gegl:noise-rgb", correlated=False, independent=False,
         red=amount, green=amount, blue=amount, gaussian=True, seed=random.randint(0, 99999))
    if size > 0:
        gegl(drawable, "gegl:gaussian-blur", std_dev_x=size, std_dev_y=size)
    Gimp.Selection.none(img)


def add_layer_from(img, src_img, name, x, y, scale_w=None):
    """Copy src_img (flattened) into img as a new layer at (x, y)."""
    src = src_img.duplicate()
    src.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    lay = Gimp.Layer.new_from_drawable(src.get_layers()[0], img)
    lay.set_name(name)
    img.insert_layer(lay, None, 0)
    if scale_w:
        h = round(lay.get_height() * scale_w / lay.get_width())
        lay.scale(scale_w, h, False)
    lay.set_offsets(x, y)
    src.delete()
    return lay


def logo(name, width):
    img = load(os.path.join(LOGOS, name + ".svg"))
    h = round(img.get_height() * width / img.get_width())
    img.scale(width, h)
    return img


def flatten(img):
    img.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    return img.get_layers()[0]


def solve8(a, b):
    """Gaussian elimination for the 8x8 homography system (no numpy in GIMP)."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def homography(src, dst):
    a, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    h = solve8(a, b) + [1.0]
    return lambda x, y: ((h[0] * x + h[1] * y + h[2]) / (h[6] * x + h[7] * y + 1),
                         (h[3] * x + h[4] * y + h[5]) / (h[6] * x + h[7] * y + 1))


def rectify(path, quad, w, h):
    """Open a photo and warp quad (TL, TR, BR, BL) onto a w x h image."""
    img = load(path)
    # Crop to the quad first: warping the full photo is slow enough to time out the MCP.
    x0 = max(0, int(min(p[0] for p in quad)) - 8)
    y0 = max(0, int(min(p[1] for p in quad)) - 8)
    x1 = min(img.get_width(), int(max(p[0] for p in quad)) + 8)
    y1 = min(img.get_height(), int(max(p[1] for p in quad)) + 8)
    img.crop(x1 - x0, y1 - y0, x0, y0)
    quad = [(px - x0, py - y0) for px, py in quad]
    lay = img.get_layers()[0]
    H = homography(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    W0, H0 = img.get_width(), img.get_height()
    ul, ur, ll, lr = H(0, 0), H(W0, 0), H(0, H0), H(W0, H0)
    Gimp.context_set_interpolation(Gimp.InterpolationType.NOHALO)
    Gimp.context_set_transform_resize(Gimp.TransformResize.ADJUST)
    lay = lay.transform_perspective(ul[0], ul[1], ur[0], ur[1], ll[0], ll[1], lr[0], lr[1])
    img.resize(w, h, 0, 0)
    lay = flatten(img)
    img.crop(w, h, 0, 0)
    return img


def flatten_lighting(img, sigma, target_rgb, detail=100.0):
    """orig / blur(orig) * target: removes shading, keeps fine surface detail."""
    base = img.get_layers()[0]
    blur = base.copy()
    img.insert_layer(blur, None, 0)
    gegl(blur, "gegl:gaussian-blur", std_dev_x=sigma, std_dev_y=sigma)
    blur.set_mode(Gimp.LayerMode.DIVIDE)
    blur.set_opacity(detail)
    lay = flatten(img)
    desat = lay.copy()
    img.insert_layer(desat, None, 0)
    desat.desaturate(Gimp.DesaturateMode.LUMINANCE)
    lay = flatten(img)
    tint = Gimp.Layer.new(img, "tint", img.get_width(), img.get_height(),
                          Gimp.ImageType.RGB_IMAGE, 100, Gimp.LayerMode.MULTIPLY)
    img.insert_layer(tint, None, 0)
    Gimp.context_set_foreground(color(target_rgb))
    tint.fill(Gimp.FillType.FOREGROUND)
    return flatten(img)


class Atlas:
    """Three GIMP images per atlas: albedo, mask (R metallic, A smoothness), emission."""

    def __init__(self, atlas):
        # atlas: a name registered in atlas_layout, or an object package's atlas dict.
        self.name, n, self.regions = atlas_layout.resolve(atlas)
        self.size = n
        self.img, self.lay = new_image(n, n, self.name + "_albedo")
        self.mimg, self.mlay = new_image(n, n, self.name + "_mask", alpha=True)
        self.eimg, self.elay = None, None

    def rect(self, region):
        return self.regions[region]

    def fill(self, region, rgb, metallic, smoothness, noise=0.0, blur=1.0):
        r = self.rect(region)
        fill_rect(self.img, self.lay, r, rgb)
        if noise:
            grain(self.img, self.lay, r, noise, blur)
        self.material(region, metallic, smoothness)

    def material(self, region, metallic, smoothness):
        fill_rect(self.mimg, self.mlay, self.rect(region),
                  (round(metallic * 255), 0, 0, max(smoothness, 1 / 255)))

    def glow_layer(self):
        if self.eimg is None:
            n = self.size
            self.eimg, self.elay = new_image(n, n, self.name + "_emission")
        return self.eimg, self.elay

    def save(self):
        save(self.img, os.path.join(OUT, self.name + "_albedo.png"))
        save(self.mimg, os.path.join(OUT, self.name + "_mask.png"))
        if self.eimg is not None:
            save(self.eimg, os.path.join(OUT, self.name + "_emission.png"))


# --- cabinet ---------------------------------------------------------------------

PUTTY = (196, 190, 167)


def cabinet_paint():
    """Tileable putty paint from a clean stretch of the cabinet's right side panel."""
    img = load(os.path.join(REF, "IMG_1493.jpg"))
    img.crop(480, 480, 980, 1280)
    lay = img.get_layers()[0]
    gegl(lay, "gegl:gaussian-blur", std_dev_x=1.2, std_dev_y=1.2)   # JPEG blocking
    lay = flatten_lighting(img, 40, PUTTY, detail=100.0)
    img.scale(1024, 1024)
    lay = img.get_layers()[0]
    gegl(lay, "gegl:tile-seamless")
    if SHOW:
        Gimp.Display.new(img)
    save(img, os.path.join(OUT, "cabinet_paint_albedo.png"))
    mimg, mlay = new_image(1024, 1024, "cabinet_paint_mask", alpha=True)
    fill_rect(mimg, mlay, (0, 0, 1024, 1024), (0, 0, 0, 0.38))
    save(mimg, os.path.join(OUT, "cabinet_paint_mask.png"))


def cabinet_hardware():
    a = Atlas("cabinet_hardware")
    x, y, w, h = a.rect("nickel")
    a.fill("nickel", (168, 166, 160), 1.0, 0.55, noise=0.08, blur=0)
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:motion-blur", length=40.0, angle=0.0)          # brushed streaks
    Gimp.Selection.none(a.img)
    a.fill("blue_anodized", (38, 146, 204), 0.85, 0.72, noise=0.03)
    x, y, w, h = a.rect("lock_face")
    a.fill("lock_face", (200, 200, 198), 1.0, 0.8, noise=0.02)
    fill_ellipse(a.img, a.lay, (x + 24, y + 24, x + 232, y + 232), (120, 120, 118))
    fill_ellipse(a.img, a.lay, (x + 34, y + 34, x + 222, y + 222), (200, 200, 198))
    fill_ellipse(a.img, a.lay, (x + 58, y + 58, x + 198, y + 198), (176, 172, 162))
    fill_rect(a.img, a.lay, (x + 118, y + 70, 20, 116), (25, 25, 25))
    a.fill("guard_plastic", (228, 229, 224), 0.0, 0.35, noise=0.02)
    a.fill("slide_steel", (140, 142, 145), 0.8, 0.45, noise=0.05)
    a.save()


# --- router ----------------------------------------------------------------------

def router():
    a = Atlas("router")
    x, y, w, h = a.rect("top")
    # Router lid from the top-down photo. Corners in full-resolution pixels; the atlas
    # left edge is the router's left end and the top row is the antenna edge.
    k = 1.44
    ox, oy = 450 * k, 420 * k
    tl, tr, br, bl = (240, 440), (590, 490), (440, 1025), (98, 925)
    quad = [(ox + bl[0], oy + bl[1]), (ox + tl[0], oy + tl[1]),
            (ox + tr[0], oy + tr[1]), (ox + br[0], oy + br[1])]
    top = rectify(os.path.join(REF, "IMG_1497.jpg"), quad, w, h)
    lay = top.get_layers()[0]
    # The photo's grooves land at 37.7% and 71% of the lid width; the real slats are
    # equal, so rescale each slat band to a third (matches the mesh).
    bands = [(0, 0.377), (0.377, 0.71), (0.71, 1.0)]
    for i, (b0, b1) in enumerate(bands):
        band = lay.copy()
        top.insert_layer(band, None, 0)
        y0, y1 = round(b0 * h), round(b1 * h)
        band.resize(w, y1 - y0, 0, -y0)
        band.scale(w, round(h / 3), False)
        band.set_offsets(0, round(i * h / 3))
    lay.set_visible(False)
    top.remove_layer(lay)
    lay = flatten(top)
    gegl(lay, "gegl:gaussian-blur", std_dev_x=1.5, std_dev_y=1.5)
    # Even out the lid's shading first, so the patch below matches its surroundings.
    lay = flatten_lighting(top, 25, (46, 46, 48), detail=100.0)
    # Cover the real wordmark (mid-length on the center slat) with a patch of the same
    # slat taken from further along, blended through a feathered selection.
    patch = lay.copy()
    top.insert_layer(patch, None, 0)
    patch.set_offsets(-round(w * 0.22), 0)
    top.select_rectangle(Gimp.ChannelOps.REPLACE, round(w * 0.38), round(h * 0.36),
                         round(w * 0.24), round(h * 0.28))
    Gimp.Selection.feather(top, 30)
    Gimp.Selection.invert(top)
    patch.edit_clear()
    Gimp.Selection.none(top)
    lay = flatten(top)
    lg = logo("tadpole_link", 200)
    tl_ = add_layer_from(top, lg, "logo", (w - 200) // 2, (h - lg.get_height()) // 2 + 20)
    lg.delete()
    lay = flatten(top)
    add_layer_from(a.img, top, "router_top", x, y)
    top.delete()
    a.lay = flatten(a.img)
    a.material("top", 0.0, 0.5)

    # Front: five status LEDs toward the left third; they glow.
    x, y, w, h = a.rect("front")
    a.fill("front", (22, 22, 23), 0.0, 0.5, noise=0.02)
    eimg, elay = a.glow_layer()
    for i in range(5):
        cx, cy = x + 300 + i * 52, y + h // 2
        fill_ellipse(a.img, a.lay, (cx - 9, cy - 9, cx + 9, cy + 9), (90, 230, 90))
        fill_ellipse(eimg, elay, (cx - 9, cy - 9, cx + 9, cy + 9), (60, 255, 60))

    # Back: power jack, button, WAN (blue), four LAN (yellow), USB.
    x, y, w, h = a.rect("back")
    a.fill("back", (22, 22, 23), 0.0, 0.4, noise=0.02)
    fill_ellipse(a.img, a.lay, (x + 90, y + 30, x + 130, y + 70), (8, 8, 8))
    fill_rect(a.img, a.lay, (x + 170, y + 36, 30, 28), (40, 40, 40))
    fill_rect(a.img, a.lay, (x + 250, y + 22, 80, 60), (30, 90, 190))
    for i in range(4):
        fill_rect(a.img, a.lay, (x + 370 + i * 100, y + 22, 80, 60), (220, 160, 30))
    fill_rect(a.img, a.lay, (x + 820, y + 36, 60, 26), (10, 10, 10))

    a.fill("body", (24, 24, 25), 0.0, 0.35, noise=0.02)
    a.fill("antenna", (17, 17, 18), 0.0, 0.3, noise=0.015)
    a.fill("plug_white", (226, 228, 224), 0.0, 0.45, noise=0.02)
    a.fill("cable_black", (20, 20, 21), 0.0, 0.4, noise=0.01)
    a.save()


# --- modem -----------------------------------------------------------------------

MODEM_GRAY = (58, 60, 64)


def perforate(img, lay, rect, pitch, radius, border):
    """Hex grid of round holes, selected together and filled once."""
    x, y, w, h = rect
    Gimp.Selection.none(img)
    row, yy = 0, y + border
    while yy < y + h - border:
        xx = x + border + (pitch / 2 if row % 2 else 0)
        while xx < x + w - border:
            img.select_ellipse(Gimp.ChannelOps.ADD, xx - radius, yy - radius, 2 * radius, 2 * radius)
            xx += pitch
        yy += pitch * 0.866
        row += 1
    Gimp.context_set_foreground(color((14, 14, 16)))
    lay.edit_fill(Gimp.FillType.FOREGROUND)
    Gimp.Selection.none(img)


def modem():
    a = Atlas("modem")
    for region in ("side", "side_b"):
        a.fill(region, MODEM_GRAY, 0.0, 0.3, noise=0.015)
        perforate(a.img, a.lay, a.rect(region), 11, 3.2, 26)

    # Top vent: a stadium ring of slots around a solid center strip.
    x, y, w, h = a.rect("top_vent")
    a.fill("top_vent", (40, 41, 44), 0.0, 0.3)
    fill_round_rect(a.img, a.lay, (x + 10, y + 10, x + w - 10, y + h - 10), h // 2 - 10, (22, 22, 24))
    fill_round_rect(a.img, a.lay, (x + 70, y + 70, x + w - 70, y + h - 70), h // 2 - 70, (46, 47, 50))
    r_in, r_out = 40, 88
    cx0, cx1, cy = x + h // 2, x + w - h // 2, y + h / 2
    Gimp.Selection.none(a.img)
    for i in range(34):
        px = cx0 + (cx1 - cx0) * i / 33
        for s in (-1, 1):
            y0 = cy + s * r_in if s > 0 else cy - r_out
            a.img.select_rectangle(Gimp.ChannelOps.ADD, px - 3, y0, 6, r_out - r_in)
    Gimp.context_set_foreground(color((6, 6, 7)))
    a.lay.edit_fill(Gimp.FillType.FOREGROUND)
    Gimp.Selection.none(a.img)
    Gimp.context_set_brush_size(6)
    for j in range(9):
        ang = -math.pi / 2 + math.pi * j / 8
        for cx, sgn in ((cx0, -1), (cx1, 1)):
            ex, ey = math.cos(ang) * sgn, math.sin(ang)
            Gimp.pencil(a.lay, [cx + ex * r_in, cy + ey * r_in, cx + ex * r_out, cy + ey * r_out])

    # LED end: glossy strip, parody logo near the top, five status LEDs.
    x, y, w, h = a.rect("led_panel")
    a.fill("led_panel", MODEM_GRAY, 0.0, 0.35, noise=0.015)
    fill_round_rect(a.img, a.lay, (x + 34, y + 40, x + w - 34, y + h - 30), 46, (14, 14, 16))
    fill_round_rect(a.mimg, a.mlay, (x + 34, y + 40, x + w - 34, y + h - 30), 46, (0, 0, 0, 0.8))
    eimg, elay = a.glow_layer()
    leds = [(70, 230, 90), (70, 140, 255), (70, 140, 255), (70, 140, 255), (70, 230, 90)]
    for i, c in enumerate(leds):
        cy = y + 250 + i * 34
        box = (x + w // 2 - 8, cy - 8, x + w // 2 + 8, cy + 8)
        fill_ellipse(a.img, a.lay, box, c)
        fill_ellipse(eimg, elay, box, c)
    lg = logo("motorboat", 56)
    add_layer_from(a.img, lg, "logo", x + (w - 56) // 2, y + 70)
    lg.delete()
    a.lay = flatten(a.img)

    x, y, w, h = a.rect("port_panel")
    a.fill("port_panel", (40, 41, 44), 0.0, 0.3, noise=0.015)
    fill_ellipse(a.img, a.lay, (x + w // 2 - 22, y + 300, x + w // 2 + 22, y + 344), (190, 170, 110))
    fill_ellipse(a.img, a.lay, (x + w // 2 - 9, y + 313, x + w // 2 + 9, y + 331), (20, 20, 20))
    fill_rect(a.img, a.lay, (x + w // 2 - 24, y + 380, 48, 40), (12, 12, 12))
    fill_ellipse(a.img, a.lay, (x + w // 2 - 14, y + 450, x + w // 2 + 14, y + 478), (8, 8, 8))
    a.fill("body", MODEM_GRAY, 0.0, 0.3, noise=0.015)
    a.fill("foot", (44, 45, 48), 0.0, 0.35, noise=0.015)
    a.save()


# --- VR headset ------------------------------------------------------------------

VISOR_PURPLE = (92, 22, 118)       # deep purple, matched to the capture photos; drawn translucent


def headset():
    a = Atlas("vr_headset")
    # Visor shell: clean tinted plastic. The internals behind it are real geometry
    # (visor_inner) seen through the translucent shell material.
    x, y, w, h = a.rect("visor_front")
    a.fill("visor_front", VISOR_PURPLE, 0.0, 0.9, noise=0.015, blur=6)
    for i in range(2):                            # faint moulding seams across the shell
        fill_rect(a.img, a.lay, (x, y + 60 + i * 230, w, 3), (78, 18, 100))
    # top edge catches more light
    shade = Gimp.Layer.new(a.img, "shade", w, h, Gimp.ImageType.RGBA_IMAGE, 25, Gimp.LayerMode.OVERLAY)
    a.img.insert_layer(shade, None, 0)
    shade.set_offsets(x, y)
    Gimp.context_set_foreground(color((255, 255, 255)))
    Gimp.context_set_background(color((0, 0, 0)))
    Gimp.context_set_gradient_fg_bg_rgb()
    shade.edit_gradient_fill(Gimp.GradientType.LINEAR, 0, False, 1, 0, True, 0, 0, 0, h)
    a.lay = flatten(a.img)

    # Shell top: plain tinted plastic, a little darker where the internals sit under it,
    # with one row of small vents along the back edge.
    x, y, w, h = a.rect("visor_top")
    a.fill("visor_top", VISOR_PURPLE, 0.0, 0.85, noise=0.015, blur=6)
    fill_rect(a.img, a.lay, (x, y + 70, w, 90), (76, 18, 98))
    for i in range(10):
        px = x + 70 + i * 92
        fill_round_rect(a.img, a.lay, (px, y + 20, px + 36, y + 42), 6, (40, 10, 52))
    a.img.select_rectangle(Gimp.ChannelOps.REPLACE, x, y, w, h)
    gegl(a.lay, "gegl:gaussian-blur", std_dev_x=2.0, std_dev_y=2.0)
    Gimp.Selection.none(a.img)

    # Internals behind the shell: dark frame, two lens housings, ribs, and the blue
    # status LED that glows through the purple (right end, as in the capture).
    x, y, w, h = a.rect("visor_inner")
    a.fill("visor_inner", (26, 24, 30), 0.0, 0.45, noise=0.02)
    for i in range(12):
        fill_rect(a.img, a.lay, (x + 14 + i * 41, y + 10, 18, 26), (44, 42, 50))
    for cx in (x + w // 4, x + 3 * w // 4):
        fill_round_rect(a.img, a.lay, (cx - 92, y + 52, cx + 92, y + 178), 44, (58, 56, 64))
        fill_round_rect(a.img, a.lay, (cx - 80, y + 62, cx + 80, y + 168), 38, (12, 12, 15))
    fill_rect(a.img, a.lay, (x + w // 2 - 22, y + 50, 44, 130), (34, 46, 38))   # centre board
    eimg, elay = a.glow_layer()
    led = (x + w - 58, y + 26, x + w - 30, y + 46)
    fill_ellipse(a.img, a.lay, led, (90, 140, 255))
    fill_ellipse(eimg, elay, led, (40, 90, 255))

    x, y, w, h = a.rect("strap")
    a.fill("strap", (20, 20, 22), 0.0, 0.35, noise=0.02)
    for _ in range(60):                           # light scuffs on the rigid plastic
        sx, sy = x + random.randint(0, w - 40), y + random.randint(0, h - 4)
        fill_rect(a.img, a.lay, (sx, sy, random.randint(6, 40), 2), (38, 38, 40))
    a.fill("foam", (26, 26, 28), 0.0, 0.1, noise=0.08, blur=0.5)
    x, y, w, h = a.rect("badge")
    a.fill("badge", (20, 20, 22), 0.0, 0.4)
    lg = logo("squintscreen", 256)
    add_layer_from(a.img, lg, "badge_logo", x, y)
    lg.delete()
    a.lay = flatten(a.img)
    a.fill("cable", (18, 18, 19), 0.0, 0.35, noise=0.01)
    x, y, w, h = a.rect("dial")
    a.fill("dial", (22, 22, 24), 0.0, 0.4, noise=0.01)
    Gimp.context_set_foreground(color((200, 200, 200)))
    Gimp.context_set_brush_size(5)
    cx, cy = x + w // 2, y + h // 2
    for i in range(24):
        ang = 2 * math.pi * i / 24
        Gimp.pencil(a.lay, [cx + math.cos(ang) * 70, cy + math.sin(ang) * 70,
                            cx + math.cos(ang) * 95, cy + math.sin(ang) * 95])
    a.save()


# --- apartment shell (tiling materials, 1024 px per tile) ---------------------------

def _tile_save(img, name, smoothness, metallic=0.0):
    save(img, os.path.join(OUT, name + "_albedo.png"))
    mimg, mlay = new_image(img.get_width(), img.get_height(), name + "_mask", alpha=True)
    fill_rect(mimg, mlay, (0, 0, img.get_width(), img.get_height()), (round(metallic * 255), 0, 0, smoothness))
    save(mimg, os.path.join(OUT, name + "_mask.png"))


def shell_carpet():
    """Bedroom carpet, photo-derived from a clean patch beside the filing cabinet
    (about 30 cm across), shading flattened, made seamless. Tiles every 0.5 m."""
    img = load(os.path.join(REF, "IMG_1493.jpg"))
    img.crop(600, 440, 980, 2420)
    flatten_lighting(img, 30, (132, 124, 117), detail=100.0)
    img.scale(1024, 1024)                 # the pile has no direction, so a mild stretch is invisible
    lay = img.get_layers()[0]
    gegl(lay, "gegl:tile-seamless")
    if SHOW:
        Gimp.Display.new(img)
    _tile_save(img, "shell_carpet", 0.08)


def _plaster(name, base, amount, blur, smoothness):
    """Orange-peel textured paint: fine bumps, faintly shaded, in the sampled colour."""
    img, lay = new_image(1024, 1024, name)
    fill_rect(img, lay, (0, 0, 1024, 1024), base)
    gegl(lay, "gegl:noise-rgb", correlated=False, independent=False, red=amount, green=amount,
         blue=amount, gaussian=True, seed=random.randint(0, 99999))
    gegl(lay, "gegl:gaussian-blur", std_dev_x=blur, std_dev_y=blur)
    gegl(lay, "gegl:tile-seamless")
    _tile_save(img, name, smoothness)


def shell_walls():
    _plaster("shell_wall", (206, 200, 191), 0.10, 1.6, 0.18)      # warm off-white, eggshell


def shell_ceiling():
    _plaster("shell_ceiling", (214, 211, 204), 0.12, 2.2, 0.08)   # flat ceiling white


def shell_trim():
    img, lay = new_image(256, 256, "shell_trim")
    fill_rect(img, lay, (0, 0, 256, 256), (232, 231, 226))           # semi-gloss white
    _tile_save(img, "shell_trim", 0.55)


def shell_vinyl():
    """Wood-look vinyl planks: 7 planks across a 1.22 m tile, joints staggered, in the
    grey-brown sampled from the kitchen floor, with long soft grain streaks."""
    img, lay = new_image(1024, 1024, "shell_vinyl")
    n = 7
    pw = 1024 / n
    for i in range(n):
        tone = random.randint(-10, 10)
        base = (116 + tone, 104 + tone, 94 + tone)
        fill_rect(img, lay, (round(i * pw), 0, round(pw) + 1, 1024), base)
    # grain: stretched noise, only along the plank length
    grain = Gimp.Layer.new(img, "grain", 1024, 1024, Gimp.ImageType.RGB_IMAGE, 35, Gimp.LayerMode.OVERLAY)
    img.insert_layer(grain, None, 0)
    fill_rect(img, grain, (0, 0, 1024, 1024), (128, 128, 128))
    gegl(grain, "gegl:noise-rgb", correlated=False, independent=False, red=0.35, green=0.35, blue=0.35,
         gaussian=True, seed=7)
    gegl(grain, "gegl:motion-blur", length=180.0, angle=90.0)
    lay = flatten(img)
    # plank seams and staggered end joints
    for i in range(n):
        x = round(i * pw)
        fill_rect(img, lay, (x, 0, 2, 1024), (64, 56, 50))
        j = random.randint(100, 900)
        fill_rect(img, lay, (x, j, round(pw), 2), (64, 56, 50))
    # No tile-seamless here: the planks already meet the tile edges, and blending
    # offset copies would ghost extra seams.
    _tile_save(img, "shell_vinyl", 0.42)


def shell():
    for f in (shell_carpet, shell_walls, shell_ceiling, shell_trim, shell_vinyl):
        f()


def build(which=("cabinet_paint", "cabinet_hardware", "router", "modem", "headset")):
    for name in which:
        globals()[name]()
    Gimp.displays_flush()


if globals().get("RUN", False) or __name__ == "__main__":
    build()
