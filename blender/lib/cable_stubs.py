"""Cable stubs: the plugs and short cable runs at the router and modem, ending just
over the cabinet's left edge. Long runs to the outlet wait for the walls.

Source of truth: scripted. Built in cabinet space (origin = cabinet origin) because the
cables connect items placed on the cabinet. Port positions are item-local (matching
the port artwork in the router and modem atlases) and follow dimensions.PLACEMENT, so
moving an item re-routes its cables.
"""

import importlib
import math

from mathutils import Vector

import common
import dimensions

importlib.reload(dimensions)

C, R, M = dimensions.CABINET, dimensions.ROUTER, dimensions.MODEM
REGIONS = ["plug_white", "cable_black"]
H = C["height"]
LEFT = -C["width"] / 2
DROP = 0.12        # how far the stubs hang down the side before ending


def to_cabinet(item, local):
    """Item-local point -> cabinet space, using the item's placement on the top."""
    px, py, rot = dimensions.PLACEMENT[item]
    a = math.radians(rot)
    x, y, z = local
    return Vector((px + x * math.cos(a) - y * math.sin(a), py + x * math.sin(a) + y * math.cos(a), H + z))


def router_port(x_local):
    """A port on the router's back edge (+Y local); returns (port, point 3 cm out)."""
    y = R["width"] / 2
    return to_cabinet("router", (x_local, y + 0.004, 0.016)), to_cabinet("router", (x_local, y + 0.035, 0.012))


def modem_port(z_frac):
    """A port on the modem's -X end, at a fraction of the shell height above the foot."""
    x = -M["length"] / 2
    z = M["foot_h"] + z_frac * (M["height"] - M["foot_h"])
    return to_cabinet("modem", (x - 0.004, 0.0, z)), to_cabinet("modem", (x - 0.035, 0.0, z - 0.01))


def over_left_edge(p, y_shift=0.0):
    """Lie across the top to the left edge, then hang down the side."""
    y = p.y + y_shift
    t = H + 0.004
    return [Vector((LEFT + 0.03, y, t)), Vector((LEFT - 0.002, y, H - 0.004)),
            Vector((LEFT - 0.006, y - 0.01, H - DROP))]


def runs():
    """(region, radius, [points]) in cabinet space; the first point is the plug end."""
    t = H + 0.004
    wan, wan_out = router_port(0.052)         # blue WAN port in the router atlas
    lan, lan_out = router_port(-0.002)
    pwr, pwr_out = router_port(0.095)
    m_eth, m_eth_out = modem_port(0.206)
    m_coax, m_coax_out = modem_port(0.36)
    m_pwr, m_pwr_out = modem_port(0.079)
    mid = (m_eth_out + wan_out) / 2
    return [
        # modem <-> router ethernet (white), sagging onto the top between them
        ("plug_white", 0.0028, [m_eth, m_eth_out, Vector((mid.x, mid.y, t + 0.006)), wan_out, wan]),
        # The LAN run is bedroom_cables' white ethernet now (it starts at router_port).
        ("cable_black", 0.0022, [pwr, pwr_out, Vector((pwr_out.x - 0.02, pwr_out.y, t))] + over_left_edge(pwr_out)),
        ("cable_black", 0.0022, [m_pwr, m_pwr_out, Vector((m_pwr_out.x - 0.02, m_pwr_out.y, t))]
         + over_left_edge(m_pwr_out, 0.01)),
        ("cable_black", 0.0032, [m_coax, m_coax_out, Vector((m_coax_out.x - 0.03, m_coax_out.y + 0.02, t + 0.01))]
         + over_left_edge(m_coax_out, 0.03)),
    ]


def build(coll):
    b = common.Builder(REGIONS)
    for region, r, pts in runs():
        b.sweep(region, common.smooth_path([tuple(p) for p in pts], 6), common.circle_profile(r, 8), up=(0, 0, 1))
        ends = [pts[0], pts[-1]] if region == "plug_white" else [pts[0]]
        for x, y, z in ends:          # plug bodies at the device ends
            b.box(region, (x - 0.008, y - 0.007, z - 0.006), (x + 0.008, y + 0.007, z + 0.006), bevel=0.0015)
    ob = b.to_object("cable_stubs", coll)
    return [ob]


def texture(obs):
    ob = obs[0]
    mat = common.atlas_material("router", "router")
    common.atlas_uvs(ob, "router")
    common.collapse_materials(ob, {r: mat for r in REGIONS})
