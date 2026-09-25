"""Write COLMAP-refined poses back into a Polycam export as corrected_cameras/,
scaled and oriented to match the original ARKit (metric, y-up) world.

Usage: python colmap_to_polycam.py <polycam_dir> <colmap_text_model_dir>

The text model comes from `colmap model_converter --output_type TXT`. Frames that
COLMAP didn't register are left out, so the converter trains on registered ones only.
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np

polycam = Path(sys.argv[1]) / "keyframes"
model = Path(sys.argv[2])


def quat_to_rot(w, x, y, z):
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])


# images.txt: two lines per image, the first is
# IMAGE_ID QW QX QY QZ TX TY TZ CAMERA_ID NAME (world-to-camera, OpenCV axes)
poses = {}
lines = [l for l in (model / "images.txt").read_text().splitlines() if not l.startswith("#")]
for line in lines[::2]:
    p = line.split()
    R = quat_to_rot(*map(float, p[1:5]))
    t = np.array(list(map(float, p[5:8])))
    c2w = np.eye(4)
    c2w[:3, :3] = R.T
    c2w[:3, 3] = -R.T @ t
    c2w = c2w @ np.diag([1, -1, -1, 1])  # OpenCV -> OpenGL camera axes, as ARKit uses
    poses[Path(p[9]).stem] = c2w

arkit = {s: json.loads((polycam / "cameras" / f"{s}.json").read_text()) for s in poses}
stems = sorted(poses)
src = np.array([poses[s][:3, 3] for s in stems])
dst = np.array([[arkit[s][f"t_{r}3"] for r in range(3)] for s in stems])


def umeyama(a, b):
    """Similarity (s, R, t) minimizing |s R a + t - b|."""
    ma, mb = a.mean(0), b.mean(0)
    A, B = a - ma, b - mb
    U, S, Vt = np.linalg.svd(B.T @ A / len(a))
    D = np.eye(3)
    D[2, 2] = np.sign(np.linalg.det(U @ Vt))
    R = U @ D @ Vt
    s = np.trace(np.diag(S) @ D) / A.var(0).sum()
    return s, R, mb - s * R @ ma


# COLMAP can fling a few mis-registered frames thousands of units away, and
# ARKit drifts, so fit with RANSAC and drop frames that still disagree after.
MAX_DRIFT = 0.30  # meters
rng = np.random.default_rng(0)
best = None
for _ in range(2000):
    idx = rng.choice(len(src), 4, replace=False)
    s, R, t = umeyama(src[idx], dst[idx])
    n = (np.linalg.norm((s * (R @ src.T)).T + t - dst, axis=1) < MAX_DRIFT).sum()
    if best is None or n > best[0]:
        best = (n, s, R, t)
_, s, R, t = best
for _ in range(3):
    keep = np.linalg.norm((s * (R @ src.T)).T + t - dst, axis=1) < MAX_DRIFT
    s, R, t = umeyama(src[keep], dst[keep])
res = np.linalg.norm((s * (R @ src.T)).T + t - dst, axis=1)
keep = res < MAX_DRIFT
print(f"{len(stems)} registered frames; ARKit drift vs COLMAP (kept frames): "
      f"median {np.median(res[keep])*100:.1f} cm, 95th pct {np.percentile(res[keep], 95)*100:.1f} cm; "
      f"dropped {(~keep).sum()} frames off by more than {MAX_DRIFT*100:.0f} cm")
stems = [st for st, k in zip(stems, keep) if k]

out_cams = polycam / "corrected_cameras"
out_imgs = polycam / "corrected_images"
for d in (out_cams, out_imgs):
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir()
for stem in stems:
    c2w = poses[stem]
    M = np.eye(4)
    M[:3, :3] = R @ c2w[:3, :3]
    M[:3, 3] = s * R @ c2w[:3, 3] + t
    cam = dict(arkit[stem])
    cam.update({f"t_{r}{k}": float(M[r, k]) for r in range(3) for k in range(4)})
    (out_cams / f"{stem}.json").write_text(json.dumps(cam))
    shutil.copy(polycam / "images" / f"{stem}.jpg", out_imgs / f"{stem}.jpg")
print(f"wrote {out_cams}")
