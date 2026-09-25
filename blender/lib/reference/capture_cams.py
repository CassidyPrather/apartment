"""Export capture cameras (pose + intrinsics) in the cabinet-local frame (= Blender frame)."""
import json, os, sys
import numpy as np
cap = sys.argv[1]; out = sys.argv[2]; stems_suffix = sys.argv[3:]
f = np.load(os.path.join(cap, "cabframe.npz"))
e1, e2, nf, df, R, cen = f["e1"], f["e2"], f["nf"], float(f["df"]), f["R"], f["cen"]
sa, la, sg = int(f["s_ax"]), int(f["long_ax"]), int(f["uvsign"])
A = np.stack([e1, e2])                  # 2x3
Mu = R.T @ A                            # uv = Mu @ P - cen
L = np.zeros((4, 4)); L[3, 3] = 1
L[0, :3] = -Mu[sa]; L[0, 3] = cen[sa]           # x = -(uv[sa])
L[1, :3] = sg * Mu[la]; L[1, 3] = -sg * cen[la]  # y = sg * uv[la]
L[2, :3] = nf; L[2, 3] = df                      # z = height above floor
print("det(L rot) =", round(np.linalg.det(L[:3, :3]), 4))
kf = os.path.join(cap, "keyframes", "corrected_cameras")
res = []
for fn in sorted(os.listdir(kf)):
    stem = fn[:-5]
    if stems_suffix and not any(stem.endswith(s) for s in stems_suffix): continue
    c = json.load(open(os.path.join(kf, fn)))
    T = np.array([[c[f"t_{r}{k}"] for k in range(4)] for r in range(3)] + [[0, 0, 0, 1]])
    res.append({"stem": stem, "matrix": (L @ T).tolist(), "fx": c["fx"], "fy": c["fy"], "cx": c["cx"], "cy": c["cy"],
                "w": c["width"], "h": c["height"]})
json.dump(res, open(out, "w"), indent=1); print(len(res), "cameras ->", out)
