"""Contact sheet of capture frames looking at a point on the cabinet (cabinet-local coords, metres)."""
import json, os, sys, math
import numpy as np
from PIL import Image, ImageDraw
cap, out = sys.argv[1], sys.argv[2]
tx, ty, tz, radius = map(float, sys.argv[3:7])     # tz: height above floor
f = np.load(os.path.join(cap, "cabframe.npz"))
e1, e2, nf, df, R, cen = f["e1"], f["e2"], f["nf"], float(f["df"]), f["R"], f["cen"]
sa, la, sg = int(f["s_ax"]), int(f["long_ax"]), int(f["uvsign"])
def l2w(x, y, h):
    u = np.zeros(2); u[sa] = -x; u[la] = y * sg; ab = (u + cen) @ R.T
    return ab[0] * e1 + ab[1] * e2 + (h - df) * nf
Pt = l2w(tx, ty, tz)
kf = os.path.join(cap, "keyframes"); cands = []
for fn in sorted(os.listdir(os.path.join(kf, "corrected_cameras"))):
    cam = json.load(open(os.path.join(kf, "corrected_cameras", fn)))
    T = np.array([[cam[f"t_{r}{c}"] for c in range(4)] for r in range(3)] + [[0, 0, 0, 1]])
    Ti = np.linalg.inv(T); pc = Ti[:3, :3] @ Pt + Ti[:3, 3]; d = -pc[2]
    if d < 0.1: continue
    px = cam["fx"] * pc[0] / d + cam["cx"]; py = cam["cy"] - cam["fy"] * pc[1] / d
    rpx = cam["fx"] * radius / d
    if not (rpx * 0.6 < px < cam["width"] - rpx * 0.6 and rpx * 0.6 < py < cam["height"] - rpx * 0.6): continue
    # viewing direction in cabinet-local terms (azimuth around z, elevation)
    campos = T[:3, 3]; v = campos - Pt
    vl = np.array([-(v @ (R[:, sa] @ np.stack([e1, e2]))), sg * (v @ (R[:, la] @ np.stack([e1, e2]))), v @ nf])
    az = math.degrees(math.atan2(vl[0], -vl[1])); el = math.degrees(math.atan2(vl[2], math.hypot(vl[0], vl[1])))
    cands.append((cam.get("blur_score", 0), az, el, fn[:-5], px, py, rpx))
# pick diverse azimuth/elevation bins, sharpest in each
bins = {}
for c in cands:
    k = (int((c[1] + 180) // 30), int(c[2] // 25))
    if k not in bins or c[0] > bins[k][0]: bins[k] = c
sel = sorted(bins.values(), key=lambda c: (c[1], c[2]))[:16]
tiles = []
for blur, az, el, stem, px, py, rpx in sel:
    im = Image.open(os.path.join(kf, "corrected_images", stem + ".jpg")).convert("RGB")
    r = int(rpx * 1.25); box = (int(px - r), int(py - r), int(px + r), int(py + r))
    t = im.crop(box).resize((320, 320), Image.LANCZOS); dr = ImageDraw.Draw(t)
    dr.rectangle((0, 0, 170, 16), fill=(0, 0, 0)); dr.text((3, 2), "az %+4.0f el %+3.0f %s" % (az, el, stem[-5:]), fill=(255, 255, 255))
    tiles.append(t)
cols = 4; rows = math.ceil(len(tiles) / cols)
sheet = Image.new("RGB", (cols * 320, rows * 320), (30, 30, 30))
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * 320, (i // cols) * 320))
sheet.save(out); print(out, len(cands), "candidate frames,", len(tiles), "tiles")
