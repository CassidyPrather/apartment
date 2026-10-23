"""kitchen_upper_contents atlas (1024): a palette of flat swatches plus packaging prints
painted as flat colour blocks in each product's real colour scheme (no text, logos,
faces or barcodes). Layout and colours live in kuc_layout.py (shared with object.py)."""

import importlib
import os
import sys

_PKG = os.path.join(ROOT, "blender", "lib", "objects", "kitchen_upper_contents")
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)
import kuc_layout  # noqa: E402

importlib.reload(kuc_layout)
ATLAS = kuc_layout.ATLAS


def build():
    a = Atlas(ATLAS)
    x0, y0, _, _ = a.rect("palette")
    for i, (name, (rgb, met, sm)) in enumerate(kuc_layout.PALETTE.items()):
        r = (x0 + 32 * (i % 8), y0 + 32 * (i // 8), 32, 32)
        fill_rect(a.img, a.lay, r, rgb)
        fill_rect(a.mimg, a.mlay, r, (round(met * 255), 0, 0, max(sm, 1 / 255)))
    for name, (base, sm, ops) in kuc_layout.LABELS.items():
        x, y, w, h = a.rect(name)
        a.fill(name, base, 0.0, sm)
        for kind, fx0, fy0, fx1, fy1, rgb in ops:
            bx0, by0 = x + round(fx0 * w), y + round(fy0 * h)
            bx1, by1 = x + round(fx1 * w), y + round(fy1 * h)
            if kind == "r":
                fill_rect(a.img, a.lay, (bx0, by0, max(bx1 - bx0, 1), max(by1 - by0, 1)), rgb)
            else:
                fill_ellipse(a.img, a.lay, (bx0, by0, bx1, by1), rgb)
        grain(a.img, a.lay, (x, y, w, h), 0.02, 1.0)
    a.save()
