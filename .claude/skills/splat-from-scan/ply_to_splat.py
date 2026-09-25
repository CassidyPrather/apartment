"""Convert a Brush/3DGS .ply into the compact .splat web format (32 bytes per splat:
xyz f32, scale f32 x3, rgba u8, quaternion u8 x4, SH dropped), sorted most-important
first, for browser viewers. Also prints a JSON line with the scene's center and extent.

Usage: python ply_to_splat.py <in.ply> <out.splat> [max_splats]
"""
import json
import sys

import numpy as np

src, dst = sys.argv[1], sys.argv[2]
cap = int(sys.argv[3]) if len(sys.argv) > 3 else None

with open(src, "rb") as f:
    props, n = [], 0
    while (line := f.readline().decode().strip()) != "end_header":
        p = line.split()
        if p[:2] == ["element", "vertex"]:
            n = int(p[2])
        elif p[0] == "property":
            assert p[1] == "float", f"unsupported property type {p[1]}"
            props.append(p[2])
    v = np.fromfile(f, dtype=[(name, "<f4") for name in props], count=n)

xyz = np.stack([v["x"], v["y"], v["z"]], 1)
scale = np.exp(np.stack([v["scale_0"], v["scale_1"], v["scale_2"]], 1))
alpha = 1 / (1 + np.exp(-v["opacity"]))
rgb = 0.5 + 0.28209479177387814 * np.stack([v["f_dc_0"], v["f_dc_1"], v["f_dc_2"]], 1)
rot = np.stack([v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]], 1)  # w, x, y, z
rot /= np.linalg.norm(rot, axis=1, keepdims=True)

order = np.argsort(-(scale.prod(1) * alpha))  # big, opaque splats first
if cap:
    order = order[:cap]

out = np.zeros(len(order), dtype=[("p", "<f4", 3), ("s", "<f4", 3), ("c", "u1", 4), ("r", "u1", 4)])
out["p"] = xyz[order]
out["s"] = scale[order]
out["c"] = np.clip(np.concatenate([rgb[order], alpha[order, None]], 1) * 255, 0, 255).astype(np.uint8)
out["r"] = np.clip(rot[order] * 128 + 128, 0, 255).astype(np.uint8)
out.tofile(dst)

core = xyz[alpha > 0.5]
lo, hi = np.percentile(core, 2, 0), np.percentile(core, 98, 0)
print(json.dumps({"splats": len(order), "center": np.median(core, 0).round(3).tolist(),
                  "min": lo.round(3).tolist(), "max": hi.round(3).tolist()}))
