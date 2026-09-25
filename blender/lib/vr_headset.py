"""PC VR headset: compact purple-shelled visor on a rigid halo strap with off-ear
speakers, resting upright on the cabinet top.

Source of truth: scripted (the halo, arms and cable are sweeps, so proportions can be
tuned from the dimensions file). Dimensions: dimensions.HEADSET (loop size and tilt
from the splat, visor details estimated). Object origin: on the resting surface under
the loop's centre. Local frame: the visor faces +X, up is +Z. Parody brand: squintscreen.

The visor is two layers: a translucent purple shell (its own material, alpha-blended
in Unity) around opaque internals, so the frame, lenses and blue status LED show
through the plastic like the real one.
"""

import importlib
import math

from mathutils import Matrix, Vector

import common
import dimensions

importlib.reload(dimensions)

HS = dimensions.HEADSET
REGIONS = ["visor_front", "visor_top", "visor_inner", "strap", "foam", "badge", "cable", "dial"]
SHELL_REGIONS = ("visor_front", "visor_top")

# Layout (meters, headset-local).
VISOR_FRONT_X = 0.135     # the loop's front meets the visor's back
VISOR_Z = (0.004, 0.004 + HS["visor_h"])
HALO_CENTER = Vector((0.0, 0.0, 0.075))
HALO_TILT = HS["halo_tilt"]   # degrees; the back of the loop rides up
BAND_H = HS["halo_band"]      # halo band height
BAND_T = 0.0055               # halo band thickness
SHELL_ALPHA = 0.5


def visor_arc(x_front, width, depth_curve=0.9, n=12):
    """Points along a visor front edge seen from above, curving back at the sides."""
    pts = []
    for i in range(n + 1):
        y = -width / 2 + width * i / n
        pts.append((x_front - depth_curve * y * y, y))
    return pts


def curved_slab(b, region, x_front, depth, width, z0, z1, cap_region, bottom_region):
    front = visor_arc(x_front, width)
    back = [(x - depth, y) for x, y in reversed(front)]
    return b.prism(region, front + back, z0, z1, cap_region=cap_region, bottom_region=bottom_region)


def halo_point(theta):
    a, bb = HS["halo_len"] / 2, HS["halo_w"] / 2
    p = Vector((a * math.cos(theta), bb * math.sin(theta), 0.0))
    return HALO_CENTER + Matrix.Rotation(math.radians(HALO_TILT), 3, "Y") @ p


def halo_normal():
    return Matrix.Rotation(math.radians(HALO_TILT), 3, "Y") @ Vector((0, 0, 1))


def edge_drop():
    """Tether points hanging over the cabinet's left edge, in headset-local coords."""
    px, py, rot = dimensions.PLACEMENT["vr_headset"]
    left = -dimensions.CABINET["width"] / 2
    a = -math.radians(rot)
    ye = py - 0.06
    out = []
    for x, y, z in ((left + 0.03, ye, 0.0022), (left - 0.002, ye - 0.002, -0.004), (left - 0.006, ye - 0.005, -0.11)):
        dx, dy = x - px, y - py
        out.append((dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a), z))
    return out


def build(coll):
    b = common.Builder(REGIONS)
    vw, vd = HS["visor_w"], HS["visor_d"]
    z0, z1 = VISOR_Z
    # Visor: translucent shell, opaque internals inside it, black face gasket behind.
    curved_slab(b, "visor_front", VISOR_FRONT_X, vd, vw, z0, z1, "visor_top", "visor_front")
    curved_slab(b, "visor_inner", VISOR_FRONT_X - 0.005, vd - 0.010, vw - 0.014,
                z0 + 0.004, z1 - 0.004, "visor_inner", "visor_inner")
    curved_slab(b, "strap", VISOR_FRONT_X - vd + 0.001, HS["gasket_d"], vw - 0.008,
                z0 + 0.003, z1 - 0.002, "strap", "strap")

    # Halo loop around the head.
    n = 48
    ring = [halo_point(2 * math.pi * i / n) for i in range(n)]
    b.sweep("strap", ring, common.rect_profile(BAND_T, BAND_H), closed=True,
            ups=[halo_normal()] * n)
    # Side arms from the gasket to the halo's sides.
    gx = VISOR_FRONT_X - vd - HS["gasket_d"] * 0.5
    for s in (-1, 1):
        side = halo_point(s * math.pi / 2)
        pts = [(gx + 0.01, s * (vw / 2 - 0.004), z0 + 0.024), (gx - 0.03, s * (vw / 2 + 0.008), 0.05),
               (side.x + 0.02, s * (abs(side.y) + 0.004), side.z - 0.01), tuple(side)]
        b.sweep("strap", common.smooth_path(pts, 5), common.rect_profile(0.005, 0.02), up=(0, 0, 1))
        # Off-ear speaker hanging outboard of the loop on a short stalk.
        sp = Vector((0.03, s * (HS["halo_w"] / 2 + 0.014), 0.03))
        b.cylinder("strap", tuple(sp), HS["speaker_d"] / 2, 0.012, axis="Y", segments=20,
                   cap_region="foam", bevel=0.002)
        b.sweep("strap", [(sp.x, sp.y, sp.z + 0.018), (sp.x + 0.005, sp.y, 0.048)],
                common.rect_profile(0.006, 0.004), up=(0, 1, 0))
    # Rear cradle: a wide curved band around the back of the loop, padded inside,
    # reaching down below the loop the way it cups the back of the head.
    arc = [halo_point(math.radians(a)) for a in range(135, 226, 5)]
    lower = Vector((0, 0, -0.018))
    b.sweep("strap", [tuple(p + lower) for p in arc], common.rect_profile(BAND_T + 0.002, 0.048),
            ups=[halo_normal()] * len(arc))
    inward = [tuple(p + lower + (HALO_CENTER - p).normalized() * 0.006) for p in arc]
    b.sweep("foam", inward, common.rect_profile(0.004, 0.040), ups=[halo_normal()] * len(arc))
    back = halo_point(math.pi)
    # Adjustment dial at the back, badge knob on the left rear of the halo.
    b.cylinder("strap", tuple(back + Vector((-0.012, 0, 0))), 0.017, 0.016, axis="X", segments=24,
               cap_region="dial")
    knob = halo_point(math.radians(140))
    b.cylinder("strap", tuple(knob + Vector((0, 0.008, 0))), 0.013, 0.01, axis="Y", segments=20,
               cap_region="badge")
    # Tether: short stub from the visor, along the right arm, across the cabinet top
    # and down its left side. The end is placed in cabinet space and brought back
    # through the headset's placement, so it always drops off the real edge.
    cpts = [(gx - 0.005, -0.02, z1 - 0.002), (gx - 0.03, -0.06, 0.055), (-0.05, -0.1, 0.06),
            (-0.11, -0.115, 0.03), (-0.15, -0.12, 0.004)] + edge_drop()
    b.sweep("cable", common.smooth_path(cpts, 6), common.circle_profile(0.0022, 8), up=(0, 0, 1))
    ob = b.to_object("vr_headset", coll)
    return [ob]


def texture(obs):
    ob = obs[0]
    vw = HS["visor_w"]
    z0, z1 = VISOR_Z
    iw = vw - 0.014
    mat = common.atlas_material("vr_headset", "vr_headset")
    shell = common.atlas_material("vr_headset_shell", "vr_headset")
    bsdf = next(n for n in shell.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Alpha"].default_value = SHELL_ALPHA
    shell.surface_render_method = "BLENDED"
    common.atlas_uvs(ob, "vr_headset", planar={
        "visor_front": ("+X", (-vw / 2, vw / 2), (z0, z1)),
        "visor_top": ("+Z_rot", (-vw / 2, vw / 2), (-VISOR_FRONT_X, -(VISOR_FRONT_X - HS["visor_d"]))),
        "visor_inner": ("+X", (-iw / 2, iw / 2), (z0 + 0.004, z1 - 0.004)),
    })
    common.collapse_materials(ob, {r: (shell if r in SHELL_REGIONS else mat) for r in REGIONS})
