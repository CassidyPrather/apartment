"""Atlas layout and photo data for own_art (pure data, shared by object.py and textures.py).

Every picture region is 72 px per inch of the real piece, so all five read equally sharp.
Photo quads are (TL, TR, BR, BL) of the piece HUNG UPRIGHT, in full-resolution pixels of the
named photo; the order encodes the rotation (the cat and the isopod lay sideways on the bed,
the waterfall upside down in the overhead shot). Corners were snapped to the strongest edges
(Reference/own_art_work/refine.py) or read on 1:1 corner zooms (zoom.py), then checked on PIL
previews of the same homography (preview.py).
"""

PX_PER_IN = 72

ATLAS = {
    "name": "own_art",
    "size": 2048,
    "regions": {
        "cat": (0, 0, 1008, 1008),              # 14 x 14 canvas face
        "abstract": (1012, 0, 792, 1008),       # 11 x 14 canvas face
        "rabbit": (0, 1012, 694, 838),          # 9.64 x 11.64 frame inner (mat + print)
        "waterfall": (698, 1012, 569, 828),     # 7.9 x 11.5 frame inner (grey mat + paper)
        "isopod": (1271, 1012, 439, 270),       # 6.1 x 3.75 frame window (paper)
        "abstract_side": (1271, 1286, 600, 56),  # painted canvas edge, photographed
        "frame_black": (1808, 0, 64, 64),
        "mat_white": (1876, 0, 64, 64),
        "canvas_back": (1944, 0, 64, 64),
        "cat_side": (1808, 68, 64, 64),
    },
}

REF_P1 = "PXL_20260925_173348922.jpg"   # all five on the bed, hand for scale
REF_P2 = "PXL_20260925_173356899.jpg"   # overhead, all five (sizes; cat face)
REF_RABBIT = "PXL_20260925_173425104.jpg"
REF_ABSTRACT = "PXL_20260925_173428611.jpg"
REF_WATERFALL = "PXL_20260925_173432229.jpg"
REF_ISOPOD = "PXL_20260925_173435004.jpg"

# region: (photo, upright quad)
PHOTOS = {
    "cat": (REF_P2, [(2832, 1263), (2850, 2363), (1831, 2422), (1791, 1259)]),       # ears were east
    "abstract": (REF_ABSTRACT, [(220, 234), (2635, 260), (2649, 3446), (52, 3526)]),
    "rabbit": (REF_RABBIT, [(500, 434), (2713, 434), (2809, 3283), (275, 3174)]),
    "waterfall": (REF_WATERFALL, [(52, 188), (2236, 48), (2242, 3354), (28, 3220)]),
    "isopod": (REF_ISOPOD, [(435, 3155), (510, 795), (2087, 805), (1950, 3282)]),    # lay rotated
    # the teal-painted front edge of the abstract canvas as it lay on the bed (photo 1)
    "abstract_side": (REF_P1, [(2300, 1618), (3450, 1606), (3450, 1648), (2300, 1658)]),
}

# Per-photo colour gains (R, G, B), measured by Reference/own_art_work (see object.py):
# the rabbit's white mat is the white reference (-> 232, 228, 220, a warm off-white), and the
# blue blanket, which is in every photo, carries that correction to the photos without a mat
# (gain = rabbit gain * rabbit-photo blanket / this photo's blanket). The room light was warm;
# the blanket reads only faintly blue, so nothing here pushes toward blue.
GAINS = {
    REF_RABBIT: (1.125, 1.197, 1.233),
    REF_P2: (1.180, 1.297, 1.355),        # mean of its own mat and its blanket (they agree)
    REF_ABSTRACT: (1.043, 1.094, 1.135),
    REF_WATERFALL: (1.091, 1.124, 1.112),
    REF_ISOPOD: (1.315, 1.381, 1.424),
    REF_P1: (1.145, 1.199, 1.217),
}

# Blurs, (x, y, w, h) inside the region, in region pixels. Empty: Cassidy asked that the
# signatures (the isopod's pencil signature and edition number, the cat's signature mark)
# not be blurred.
BLURS = {}

# solid colours (sampled): frame black, mat white, raw canvas back, cat canvas edge
SOLIDS = {
    "frame_black": ((18, 17, 18), 0.25),
    "mat_white": ((232, 228, 220), 0.1),
    "canvas_back": ((214, 204, 184), 0.05),
    "cat_side": ((36, 28, 31), 0.15),     # photo 1 edge, (31, 25, 26) raw, gained
}
