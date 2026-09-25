"""Orthophoto of a plane in the cabinet-local frame, from the capture's posed photos.

Usage: orthophoto.py <capture_dir> <out.png> <plane> <u_min> <u_max> <v_min> <v_max> [res_m] [offset]
plane: 'front' (x right, z up, at y=offset), 'right' (-y..+y, z at x=offset), 'top' (x, y at z=offset above floor)
"""
import json, os, sys
import numpy as np
from PIL import Image

cap, out, plane = sys.argv[1], sys.argv[2], sys.argv[3]
u0, u1, v0, v1 = map(float, sys.argv[4:8])
res = float(sys.argv[8]) if len(sys.argv) > 8 else 0.001
off = float(sys.argv[9]) if len(sys.argv) > 9 else 0.0
f = np.load(os.path.join(cap, "cabframe.npz"))
e1, e2, nf, df, R, cen = f["e1"], f["e2"], f["nf"], float(f["df"]), f["R"], f["cen"]
sa, la, sg = int(f["s_ax"]), int(f["long_ax"]), int(f["uvsign"])

def local_to_world(x, y, h):
    u = np.zeros((len(x), 2)); u[:, sa] = -x; u[:, la] = y * sg      # frame is mirrored: x = -u[sa]
    ab = (u + cen) @ R.T
    return ab[:, :1] * e1 + ab[:, 1:] * e2 + (h - df)[:, None] * nf

W = int((u1 - u0) / res); H = int((v1 - v0) / res)
uu, vv = np.meshgrid(u0 + (np.arange(W) + 0.5) * res, v1 - (np.arange(H) + 0.5) * res)
uu, vv = uu.ravel(), vv.ravel()
if plane == "front":
    x, y, h = uu, np.full_like(uu, off), vv; normal_local = (0, -1, 0)
elif plane == "right":
    x, y, h = np.full_like(uu, off), -uu, vv; normal_local = (1, 0, 0)     # u runs front->back as seen from +x
elif plane == "top":
    x, y, h = uu, vv, np.full_like(uu, off); normal_local = (0, 0, 1)
Pw = local_to_world(x, y, h)
nW = local_to_world(np.array([normal_local[0]]), np.array([normal_local[1]]), np.array([normal_local[2]]) + df * 0) \
     - local_to_world(np.zeros(1), np.zeros(1), np.zeros(1))
nW = nW[0] / np.linalg.norm(nW[0])

kf = os.path.join(cap, "keyframes")
samples, weights = [], []
for fn in sorted(os.listdir(os.path.join(kf, "corrected_cameras"))):
    cam = json.load(open(os.path.join(kf, "corrected_cameras", fn)))
    T = np.array([[cam[f"t_{r}{c}"] for c in range(4)] for r in range(3)] + [[0, 0, 0, 1]])
    campos = T[:3, 3]
    view = Pw.mean(0) - campos; view /= np.linalg.norm(view)
    facing = -view @ nW
    if facing < 0.5:                      # only frames looking at the plane fairly square-on
        continue
    Ti = np.linalg.inv(T)
    pc = (Ti[:3, :3] @ Pw.T + Ti[:3, 3:4]).T
    d = -pc[:, 2]
    ok = d > 0.05
    px = cam["fx"] * pc[:, 0] / np.where(ok, d, 1) + cam["cx"]
    py = cam["cy"] - cam["fy"] * pc[:, 1] / np.where(ok, d, 1)
    ok &= (px >= 0) & (px < cam["width"] - 1) & (py >= 0) & (py < cam["height"] - 1)
    # occlusion test against the frame's depth map
    dm = np.array(Image.open(os.path.join(kf, "depth", fn[:-5] + ".png")), np.float32) / 1000.0
    s = dm.shape[1] / cam["width"]
    dd = dm[np.clip((py * s).astype(int), 0, dm.shape[0] - 1), np.clip((px * s).astype(int), 0, dm.shape[1] - 1)]
    ok &= np.abs(dd - d) < 0.03
    img = np.asarray(Image.open(os.path.join(kf, "corrected_images", fn[:-5] + ".jpg")).convert("RGB"), np.float32)
    col = np.full((len(Pw), 3), np.nan, np.float32)
    ix, iy = px[ok], py[ok]
    x0, y0 = np.floor(ix).astype(int), np.floor(iy).astype(int); fx_, fy_ = (ix - x0)[:, None], (iy - y0)[:, None]
    col[ok] = (img[y0, x0] * (1 - fx_) * (1 - fy_) + img[y0, x0 + 1] * fx_ * (1 - fy_)
               + img[y0 + 1, x0] * (1 - fx_) * fy_ + img[y0 + 1, x0 + 1] * fx_ * fy_)
    samples.append(col); weights.append(facing * cam.get("blur_score", 50) / (d.mean() + 1e-3))
S = np.stack(samples)                      # frames x pixels x 3
print("frames used", len(samples))
med = np.nanmedian(S, axis=0)
med = np.nan_to_num(med, nan=0).reshape(H, W, 3)
Image.fromarray(np.clip(med, 0, 255).astype(np.uint8)).save(out)
print("wrote", out, W, H)
