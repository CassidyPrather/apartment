"""Alignment check for a COLMAP text model with colored points (e.g. SplatKing's
COLMAP_Text_Model): reproject the points into ~10 frames and compare their colors
with the photo, against a shuffled-color baseline. Aligned poses score near 0.45
(SplatKing bedroom); drifted or broken ones approach 1.0.

Usage: python check_colmap.py <model_dir with sparse/0 and images/>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

root = Path(sys.argv[1])
sp = root / "sparse" / "0"


def q2r(w, x, y, z):
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


cams = {}
for line in (sp / "cameras.txt").read_text().splitlines():
    if line and not line.startswith("#"):
        p = line.split()
        assert p[1] == "PINHOLE", f"only PINHOLE supported, got {p[1]}"
        cams[p[0]] = tuple(map(float, p[2:8]))  # w h fx fy cx cy

ims = []
for line in (sp / "images.txt").read_text().splitlines():
    p = line.split()
    if line.startswith("#") or len(p) < 10 or not p[9].lower().endswith((".jpg", ".png")):
        continue
    ims.append((p[9], q2r(*map(float, p[1:5])), np.array(list(map(float, p[5:8]))), cams[p[8]]))
ims.sort(key=lambda x: x[0])
centers = np.array([-R.T @ t for _, R, t, _ in ims])
print(f"{len(ims)} posed images; walk {np.linalg.norm(np.diff(centers, axis=0), axis=1).sum():.1f} m; "
      f"camera extent {np.round(centers.max(0) - centers.min(0), 2)} m")

rows = [l.split() for l in open(sp / "points3D.txt") if not l.startswith("#")]
P = np.array([[float(r[1]), float(r[2]), float(r[3])] for r in rows])
C = np.array([[int(r[4]), int(r[5]), int(r[6])] for r in rows])
rng = np.random.default_rng(0)
sel = rng.choice(len(P), min(300_000, len(P)), replace=False)
P, C = P[sel], C[sel]
Cs = C[rng.permutation(len(C))]

ratios = []
for name, R, t, (w, h, fx, fy, cx, cy) in ims[:: max(1, len(ims) // 10)]:
    pc = P @ R.T + t
    z = pc[:, 2]
    zz = np.maximum(z, 1e-6)
    u = fx * pc[:, 0] / zz + cx
    v = fy * pc[:, 1] / zz + cy
    idx = np.nonzero((z > 0.1) & (u >= 0) & (u < w) & (v >= 0) & (v < h))[0]
    gw = int(w // 12) + 1
    key = (v[idx] // 12).astype(int) * gw + (u[idx] // 12).astype(int)
    zmin = np.full(key.max() + 1, np.inf)
    np.minimum.at(zmin, key, z[idx])
    idx = idx[z[idx] < zmin[key] + 0.03]  # drop occluded points
    img = np.asarray(Image.open(root / "images" / name).convert("RGB")).astype(int)
    s = img[v[idx].astype(int), u[idx].astype(int)]
    ratios.append(np.abs(s - C[idx]).mean() / np.abs(s - Cs[idx]).mean())
print(f"alignment ratio {np.mean(ratios):.2f} (good < 0.65, broken ~1.0); per frame {np.round(ratios, 2)}")
