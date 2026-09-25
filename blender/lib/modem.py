"""Cable modem: tower with rounded-rectangle section on an oval foot.

Source of truth: scripted. Dimensions: dimensions.MODEM (estimates).
Object origin: bottom center. Local frame: long side along X, the perforated wide
faces face -Y/+Y, status-LED end at +X, port end at -X. Parody brand: Motorboat.
"""

import importlib
import math

import common
import dimensions

importlib.reload(dimensions)

M = dimensions.MODEM
REGIONS = ["side", "side_b", "top_vent", "led_panel", "port_panel", "body", "foot"]


def ellipse(cx, cy, a, b, n=28):
    return [(cx + a * math.cos(2 * math.pi * i / n), cy + b * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def build(coll):
    L, T, H = M["length"], M["thick"], M["height"]
    fh = M["foot_h"]
    b = common.Builder(REGIONS)
    b.prism("foot", ellipse(0, 0, M["foot_len"] / 2, M["foot_thick"] / 2), 0.0, fh)
    # Shell: rounded-rectangle section, a little inset lip at the top for the vent cap.
    outline = common.rounded_rect(0, 0, L, T, M["corner_r"], seg=6)
    faces = b.prism("body", outline, fh, H - 0.004, cap_region="body", bottom_region="foot")
    inner = common.rounded_rect(0, 0, L - 0.004, T - 0.004, M["corner_r"] - 0.002, seg=6)
    b.prism("body", inner, H - 0.0045, H, cap_region="top_vent")
    # Tag shell sides by facing: wide faces get the perforation, ends get panels.
    b.bm.normal_update()
    for f in faces:
        n = f.normal
        if abs(n.z) > 0.5:
            continue
        if n.y < -0.7:
            f.material_index = b.idx("side")
        elif n.y > 0.7:
            f.material_index = b.idx("side")     # both wide faces share the perforation
        elif n.x > 0.3:
            f.material_index = b.idx("led_panel")
        elif n.x < -0.3:
            f.material_index = b.idx("port_panel")
    ob = b.to_object("modem", coll)
    return [ob]


def texture(obs):
    ob = obs[0]
    L, T, H = M["length"], M["thick"], M["height"]
    fh = M["foot_h"]
    mat = common.atlas_material("modem", "modem")
    common.atlas_uvs(ob, "modem", planar={
        "side": ("-Y", (-L / 2, L / 2), (fh, H)),
        "led_panel": ("+X", (-T / 2, T / 2), (fh, H)),
        "port_panel": ("-X", (-T / 2, T / 2), (fh, H)),
        "top_vent": ("+Z", (-L / 2, L / 2), (-T / 2, T / 2)),
    })
    common.collapse_materials(ob, {r: mat for r in REGIONS})
