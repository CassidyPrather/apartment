"""Cable stubs: the plugs and short cable runs at the router and modem, ending just
over the cabinet's left edge. Long runs to the outlet wait for the walls.

Source of truth: scripted. Built in cabinet space (origin = cabinet origin) because the
cables connect items placed on the cabinet; paths follow dimensions.PLACEMENT.
"""

import importlib

import common
import dimensions

importlib.reload(dimensions)

C = dimensions.CABINET
REGIONS = ["plug_white", "cable_black"]
H = C["height"]
LEFT = -C["width"] / 2
DROP = 0.12        # how far the stubs hang down the side before ending


def runs():
    """(region, cable radius, [points]) in cabinet space."""
    t = H + 0.004
    return [
        # modem <-> router ethernet (white)
        ("plug_white", 0.0028, [(-0.037, 0.246, H + 0.07), (-0.07, 0.262, H + 0.05),
                                (-0.14, 0.24, t + 0.01), (-0.165, 0.15, t), (-0.16, 0.09, t + 0.004),
                                (-0.148, 0.068, H + 0.014)]),
        # router LAN out, off the left edge
        ("cable_black", 0.0026, [(-0.148, 0.03, H + 0.014), (-0.172, 0.015, t),
                                 (LEFT - 0.002, -0.01, H - 0.004), (LEFT - 0.006, -0.02, H - DROP)]),
        # router power
        ("cable_black", 0.0022, [(-0.148, -0.03, H + 0.012), (-0.175, -0.05, t),
                                 (LEFT - 0.002, -0.06, H - 0.004), (LEFT - 0.006, -0.07, H - DROP)]),
        # modem power
        ("cable_black", 0.0022, [(-0.037, 0.232, H + 0.035), (-0.09, 0.27, t + 0.004),
                                 (LEFT - 0.002, 0.285, H - 0.004), (LEFT - 0.006, 0.29, H - DROP)]),
        # modem coax
        ("cable_black", 0.0032, [(-0.037, 0.244, H + 0.105), (-0.1, 0.29, H + 0.05),
                                 (-0.16, 0.302, t + 0.004), (LEFT - 0.003, 0.305, H - 0.006),
                                 (LEFT - 0.007, 0.305, H - DROP)]),
    ]


def build(coll):
    b = common.Builder(REGIONS)
    for region, r, pts in runs():
        b.sweep("cable_black" if region == "cable_black" else "plug_white",
                common.smooth_path(pts, 6), common.circle_profile(r, 8), up=(0, 0, 1))
        # plug body at the device end
        x, y, z = pts[-1] if region == "plug_white" else pts[0]
        b.box("plug_white" if region == "plug_white" else "cable_black",
              (x - 0.008, y - 0.007, z - 0.006), (x + 0.008, y + 0.007, z + 0.006), bevel=0.0015)
    ob = b.to_object("cable_stubs", coll)
    return [ob]


def texture(obs):
    ob = obs[0]
    mat = common.atlas_material("router", "router")
    common.atlas_uvs(ob, "router")
    common.collapse_materials(ob, {r: mat for r in REGIONS})
