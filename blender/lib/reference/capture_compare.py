"""Photo | render | overlay triptychs, cropped around a cabinet-local point."""
import json, sys, os
import numpy as np
from PIL import Image
S, cap = sys.argv[1], sys.argv[2]
tx, ty, tz, rad = map(float, sys.argv[3:7]); tag = sys.argv[7]
cams = json.load(open(os.path.join(S, "hs_cams.json")))
rows = []
for c in cams:
    photo = Image.open(os.path.join(cap, "keyframes", "corrected_images", c["stem"] + ".jpg")).convert("RGBA")
    rend = Image.open(os.path.join(S, "render_" + c["stem"] + ".png")).convert("RGBA")
    M = np.array(c["matrix"]); Mi = np.linalg.inv(M)
    pc = Mi @ np.array([tx, ty, tz, 1.0]); d = -pc[2]
    px = c["fx"] * pc[0] / d + c["cx"]; py = c["cy"] - c["fy"] * pc[1] / d; r = c["fx"] * rad / d
    box = tuple(int(v) for v in (px - r, py - r, px + r, py + r))
    ov = photo.copy(); rr = rend.copy(); a = np.array(rr); a[..., 3] = (a[..., 3] * 0.55).astype(np.uint8)
    ov.alpha_composite(Image.fromarray(a))
    bg = Image.new("RGBA", rend.size, (255, 255, 255, 255)); bg.alpha_composite(rend)
    tiles = [im.crop(box).resize((420, 420), Image.LANCZOS).convert("RGB") for im in (photo, bg, ov)]
    row = Image.new("RGB", (1260, 420)); [row.paste(t, (i * 420, 0)) for i, t in enumerate(tiles)]
    rows.append(row)
sheet = Image.new("RGB", (1260, 420 * len(rows)))
for i, r in enumerate(rows): sheet.paste(r, (0, i * 420))
sheet.save(os.path.join(S, f"cmp_{tag}.png")); print("ok", len(rows))
