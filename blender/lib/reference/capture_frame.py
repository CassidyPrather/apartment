import numpy as np
d = np.load("cloud.npz"); P, C = d["p"].astype(np.float64), d["c"].astype(np.float64)
f = np.load("frame.npz"); nf, df, e1, e2, ang, top = f["nf"], f["df"], f["e1"], f["e2"], float(f["ang"]), float(f["top"])
a = np.radians(ang); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
h = P @ nf + df
uv = np.stack([P @ e1, P @ e2], 1) @ R
topm = np.abs(h - top) < 0.004
t = uv[topm]; med = np.median(t, 0); t = t[np.linalg.norm(t - med, axis=1) < 0.6]
lo, hi = np.percentile(t, 0.5, 0), np.percentile(t, 99.5, 0)
cen = (lo + hi) / 2
uv -= cen
L = hi - lo; long_ax = int(np.argmax(L)); s_ax = 1 - long_ax
# local coords: x = width axis, y = depth axis (+y toward the back), z = height
x = uv[:, s_ax].copy(); y = uv[:, long_ax].copy()
blue = (C[:,2] > 150) & (C[:,2] - C[:,0] > 60) & (h > 0.1) & (h < top) & (np.abs(x) < 0.25) & (np.abs(y) < 0.45)
if np.median(y[blue]) > 0: y = -y; uvsign = -1
else: uvsign = 1
# keep x right-handed looking at the front (front at -y): if x flips handedness, mirror
np.savez("cabframe.npz", R=R, cen=cen, long_ax=long_ax, s_ax=s_ax, uvsign=uvsign, e1=e1, e2=e2, nf=nf, df=df, top=top)
inside = (np.abs(x) < 0.35) & (np.abs(y) < 0.45)
# width: side panels at mid height, middle of the depth
band = inside & (h > 0.15) & (h < 0.55) & (np.abs(y) < 0.2)
xl, xr = x[band & (x < 0)], x[band & (x > 0)]
def outer(v, sgn):  # outer surface: robust extreme of the dense wall cluster
    return np.percentile(v, 1 if sgn < 0 else 99)
W = outer(xr, 1) - outer(xl, -1)
# depth: top surface along the centreline
cl = topm & inside & (np.abs(x) < 0.08)
D = np.percentile(y[cl], 99.7) - np.percentile(y[cl], 0.3)
# front face position at mid height vs top front edge
ff = inside & (h > 0.15) & (h < 0.55) & (np.abs(x) < 0.1) & (y < 0)
print("width  %.1f mm (%.2f in)" % (W*1000, W/0.0254))
print("depth  %.1f mm (%.2f in) top surface centreline" % (D*1000, D/0.0254))
print("top edge front y %.1f mm, drawer face y (1pct) %.1f mm" % (np.percentile(y[cl],0.3)*1000, np.percentile(y[ff],1)*1000))
print("height %.1f mm (%.2f in)" % (top*1000, top/0.0254))
print("side wall x: left %.1f right %.1f mm" % (outer(xl,-1)*1000, outer(xr,1)*1000))

def peak(v, lo, hi, bw=0.001):
    hgram, e = np.histogram(v, bins=np.arange(lo, hi, bw))
    k = np.argmax(hgram); return (e[k] + e[k+1]) / 2, hgram[k]
pl = peak(x[band], -0.26, -0.15); pr = peak(x[band], 0.15, 0.26)
print("wall peaks: left %.1f mm (n=%d)  right %.1f mm (n=%d)  -> width %.1f mm (%.2f in)" % (pl[0]*1000, pl[1], pr[0]*1000, pr[1], (pr[0]-pl[0])*1000, (pr[0]-pl[0])/0.0254))
# front plane: drawer faces at mid height, avoid handles/labels -> use the side strips of the faces
fs = inside & (h > 0.1) & (h < 0.62) & (np.abs(x) > 0.1) & (np.abs(x) < 0.17) & (y < -0.25)
pf = peak(y[fs], -0.40, -0.28)
bs = inside & (h > 0.1) & (h < 0.62) & (np.abs(x) < 0.15) & (y > 0.25)
pb = peak(y[bs], 0.28, 0.40)
print("front face y %.1f mm (n=%d), back y %.1f mm (n=%d) -> depth %.1f mm (%.2f in)" % (pf[0]*1000, pf[1], pb[0]*1000, pb[1], (pb[0]-pf[0])*1000, (pb[0]-pf[0])/0.0254))
# top rect via top-surface edge density on centre strips
for name, v, lo_, hi_ in (("top x", x[topm & inside & (np.abs(y) < 0.2)], -0.25, 0.25), ("top y", y[topm & inside & (np.abs(x) < 0.12)], -0.4, 0.4)):
    hg, e = np.histogram(v, bins=np.arange(lo_, hi_, 0.002)); m = hg > 0.25 * np.median(hg[hg > 0])
    idx = np.where(m)[0]; print(name, "occupied %.1f .. %.1f mm" % (e[idx[0]]*1000, e[idx[-1]+1]*1000))
