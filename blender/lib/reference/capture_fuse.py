"""Fuse a phone LiDAR capture (keyframes/{depth,confidence,images,corrected_cameras}) into a colored point cloud."""
import json, os, sys
import numpy as np
from PIL import Image

KF = sys.argv[1]
OUT = sys.argv[2]
CAMS = os.path.join(KF, "corrected_cameras")
pts, cols = [], []
for f in sorted(os.listdir(CAMS)):
    stem = f[:-5]
    cam = json.load(open(os.path.join(CAMS, f)))
    T = np.array([[cam[f"t_{r}{c}"] for c in range(4)] for r in range(3)] + [[0, 0, 0, 1]])
    d = np.array(Image.open(os.path.join(KF, "depth", stem + ".png")), np.float32) / 1000.0
    conf = np.array(Image.open(os.path.join(KF, "confidence", stem + ".png")))
    h, w = d.shape
    s = w / cam["width"]
    fx, fy, cx, cy = cam["fx"] * s, cam["fy"] * s, cam["cx"] * s, cam["cy"] * s
    img = np.array(Image.open(os.path.join(KF, "images", stem + ".jpg")).convert("RGB").resize((w, h), Image.BILINEAR))
    v, u = np.mgrid[0:h, 0:w]
    m = (conf == 255) & (d > 0.1) & (d < 3.0)
    z = d[m]
    x = (u[m] + 0.5 - cx) / fx * z
    y = (v[m] + 0.5 - cy) / fy * z
    pc = np.stack([x, -y, -z, np.ones_like(z)], 1)      # ARKit camera: +y up, looks down -z
    pw = (T @ pc.T).T[:, :3]
    pts.append(pw); cols.append(img[m])
P = np.concatenate(pts); Cc = np.concatenate(cols)
np.savez_compressed(OUT, p=P.astype(np.float32), c=Cc.astype(np.uint8))
print(len(P), "points; bounds", P.min(0).round(3), P.max(0).round(3))
