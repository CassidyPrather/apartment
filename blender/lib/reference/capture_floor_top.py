import numpy as np
d = np.load("cloud.npz"); P, C = d["p"].astype(np.float64), d["c"]
rng = np.random.default_rng(0)
def plane_ransac(Q, iters=400, tol=0.006):
    best = None
    for _ in range(iters):
        s = Q[rng.choice(len(Q), 3, replace=False)]
        n = np.cross(s[1]-s[0], s[2]-s[0]); nn = np.linalg.norm(n)
        if nn < 1e-9: continue
        n /= nn; dd = -n @ s[0]
        inl = np.abs(Q @ n + dd) < tol
        if best is None or inl.sum() > best[2].sum(): best = (n, dd, inl)
    n, dd, inl = best
    # refine with least squares
    q = Q[inl]; c = q.mean(0); w, V = np.linalg.eigh(np.cov((q - c).T)); n = V[:, 0]
    if n[1] < 0: n = -n
    return n, -n @ c, inl
# floor: lowest 15 cm
low = P[P[:,1] < P[:,1].min() + 0.15]
nf, df, _ = plane_ransac(low[rng.choice(len(low), min(200000,len(low)), replace=False)])
print("floor normal", nf.round(4), "tilt deg", np.degrees(np.arccos(abs(nf[1]))).round(2))
h = P @ nf + df                              # height above floor
# horizontal points (normals unknown) -> histogram of heights to find the cabinet top
hist, edges = np.histogram(h[(h > 0.4) & (h < 1.0)], bins=600)
top_bin = edges[np.argmax(hist)]
print("dominant horizontal level above 0.4 m:", round(top_bin, 4))
top = P[np.abs(h - top_bin) < 0.004]
# project to floor plane basis
e1 = np.cross(nf, [0, 0, 1]); e1 /= np.linalg.norm(e1); e2 = np.cross(nf, e1)
xy = np.stack([top @ e1, top @ e2], 1)
# cabinet top only: cluster near the densest region
cen = np.median(xy, 0); xy = xy[np.linalg.norm(xy - cen, axis=1) < 0.6]
best = None
for a in np.radians(np.arange(0, 90, 0.25)):
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    r = xy @ R
    lo, hi = np.percentile(r, 0.5, 0), np.percentile(r, 99.5, 0)
    area = np.prod(hi - lo)
    if best is None or area < best[0]: best = (area, np.degrees(a), hi - lo)
print("top rectangle (0.5-99.5 pct):", (best[2]*1000).round(1), "mm at", best[1], "deg")
print("top height above floor:", round(top_bin*1000,1), "mm =", round(top_bin/0.0254,2), "in")
print("rect in inches:", (best[2]/0.0254).round(2))
np.savez("frame.npz", nf=nf, df=df, e1=e1, e2=e2, ang=best[1], top=top_bin)
