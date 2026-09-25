import sys, math, numpy as np
from PIL import Image
sys.path.insert(0, r"C:/Source/apartment/blender/lib"); import dimensions as D
px, py, rot = D.PLACEMENT["vr_headset"]; H = D.CABINET["height"]
d = np.load(r"C:/Source/apartment/Reference/cabinet-splat/splat_local.npz")
x, y, z, c, o = d["x"], d["y"], d["z"] - H, d["c"], d["o"]
a = -math.radians(rot); dx, dy = x - px, y - py
hx, hy = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
m = (hx > -0.17) & (hx < 0.21) & (np.abs(hy) < 0.17) & (z > 0.002) & (z < 0.20) & (o > 0.35)
dark = c[:, :3].mean(1) < 110          # the headset is black/purple; drop the beige top
m &= dark | ((c[:, 0] > 60) & (c[:, 2] > 70) & (c[:, 1] < 0.7 * np.minimum(c[:, 0], c[:, 2])))
print("headset splat points", m.sum())
views = {"top": (hx, hy, z, (-0.16, 0.20), (-0.16, 0.16)),
         "side": (hx, z, -hy, (-0.16, 0.20), (-0.01, 0.19)),     # seen from +y... nearest = largest y -> depth -hy ascending
         "front": (hy, z, hx, (-0.16, 0.16), (-0.01, 0.19))}
for name, (u, v, dep, ur, vr) in views.items():
    W, Hh = int(round((ur[1]-ur[0]) * 1000)), int(round((vr[1]-vr[0]) * 1000))
    img = np.full((Hh, W, 3), 245, np.uint8)
    iu = ((u[m] - ur[0]) * 1000).astype(int); iv = Hh - 1 - ((v[m] - vr[0]) * 1000).astype(int)
    ok = (iu >= 0) & (iu < W) & (iv >= 0) & (iv < Hh)
    order = np.argsort(dep[m][ok])
    for du in (0, 1):
        for dv in (0, 1):
            img[np.clip(iv[ok][order] + dv, 0, Hh-1), np.clip(iu[ok][order] + du, 0, W-1)] = c[m][ok][order][:, :3]
    Image.fromarray(img).save(f"{sys.argv[1]}/splat_hs_{name}.png"); print(name, W, Hh)
