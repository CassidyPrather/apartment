"""Convert a Polycam raw-data export (keyframes/) into a nerfstudio-style
transforms.json plus an initial point cloud back-projected from LiDAR depth.

Usage: python polycam_to_nerfstudio.py <polycam_dir> <out_dir>
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

src = Path(sys.argv[1]) / "keyframes"
out = Path(sys.argv[2])
(out / "images").mkdir(parents=True, exist_ok=True)

# Prefer Polycam's bundle-adjusted cameras/images when present.
cam_dir = src / "corrected_cameras" if (src / "corrected_cameras").exists() else src / "cameras"
img_dir = src / "corrected_images" if (src / "corrected_images").exists() else src / "images"

# Seed about 450k points in total, however many frames there are (at most 3000 per frame).
per_frame = min(3000, 450_000 // max(1, len(list(cam_dir.glob("*.json")))))

frames, pts, cols = [], [], []
rng = np.random.default_rng(0)
for cam_path in sorted(cam_dir.glob("*.json")):
    stem = cam_path.stem
    c = json.loads(cam_path.read_text())
    # ARKit camera-to-world, already in OpenGL convention (x right, y up, -z forward).
    T = np.array([[c[f"t_{r}{k}"] for k in range(4)] for r in range(3)] + [[0, 0, 0, 1]])
    shutil.copy(img_dir / f"{stem}.jpg", out / "images" / f"{stem}.jpg")
    frames.append({
        "file_path": f"images/{stem}.jpg",
        "fl_x": c["fx"], "fl_y": c["fy"], "cx": c["cx"], "cy": c["cy"],
        "w": c["width"], "h": c["height"],
        "transform_matrix": T.tolist(),
    })

    # Back-project high-confidence depth (mm) into world space for splat init.
    depth = np.asarray(Image.open(src / "depth" / f"{stem}.png"), dtype=np.float32) / 1000.0
    conf = np.asarray(Image.open(src / "confidence" / f"{stem}.png"))
    dh, dw = depth.shape
    s = dw / c["width"]
    v, u = np.nonzero((conf == 255) & (depth > 0))
    keep = rng.choice(len(u), size=min(len(u), per_frame), replace=False)
    u, v = u[keep], v[keep]
    d = depth[v, u]
    x = (u + 0.5 - c["cx"] * s) / (c["fx"] * s) * d
    y = -(v + 0.5 - c["cy"] * s) / (c["fy"] * s) * d
    pc = np.stack([x, y, -d, np.ones_like(d)], axis=1)
    pts.append((T @ pc.T).T[:, :3])
    rgb = np.asarray(Image.open(img_dir / f"{stem}.jpg").resize((dw, dh)))
    cols.append(rgb[v, u])

pts = np.concatenate(pts).astype(np.float32)
cols = np.concatenate(cols).astype(np.uint8)
with open(out / "points3d.ply", "wb") as f:
    f.write((
        "ply\nformat binary_little_endian 1.0\n"
        f"element vertex {len(pts)}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n"
    ).encode())
    rec = np.zeros(len(pts), dtype=[("p", "<f4", 3), ("c", "u1", 3)])
    rec["p"], rec["c"] = pts, cols
    f.write(rec.tobytes())

# Alignment check: reproject the cloud into a few frames and compare its colors
# with the photo, against a shuffled-color baseline. Aligned poses land near half
# the baseline (cabinet test: ~28 vs ~57); a wrong convention lands near 1.0x.
shuffled = cols[rng.permutation(len(cols))].astype(int)
ratios = []
for fr in frames[:: max(1, len(frames) // 5)]:
    W = np.linalg.inv(np.array(fr["transform_matrix"]))
    pc = pts @ W[:3, :3].T + W[:3, 3]
    z = -pc[:, 2]
    m = z > 0.1
    u = fr["fl_x"] * pc[m, 0] / z[m] + fr["cx"]
    v = -fr["fl_y"] * pc[m, 1] / z[m] + fr["cy"]
    ok = (u >= 0) & (u < fr["w"]) & (v >= 0) & (v < fr["h"])
    zz = z[m][ok]
    key = (v[ok] // 8).astype(int) * (fr["w"] // 8 + 1) + (u[ok] // 8).astype(int)
    zmin = np.full(key.max() + 1, np.inf)
    np.minimum.at(zmin, key, zz)
    vis = zz < zmin[key] + 0.05  # drop occluded points
    img = np.asarray(Image.open(out / fr["file_path"])).astype(int)
    samp = img[v[ok].astype(int), u[ok].astype(int)][vis]
    err = np.abs(samp - cols[m][ok][vis].astype(int)).mean()
    base = np.abs(samp - shuffled[m][ok][vis]).mean()
    ratios.append(err / base)
ratio = float(np.mean(ratios))
print(f"alignment ratio {ratio:.2f} (good < 0.65, broken ~1.0)")

f0 = frames[0]
(out / "transforms.json").write_text(json.dumps({
    "camera_model": "OPENCV",
    "fl_x": f0["fl_x"], "fl_y": f0["fl_y"], "cx": f0["cx"], "cy": f0["cy"],
    "w": f0["w"], "h": f0["h"],
    "ply_file_path": "points3d.ply",
    "frames": frames,
}, indent=1))
print(f"{len(frames)} frames, {len(pts)} init points -> {out}")
