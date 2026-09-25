"""Atlas layout for living_wall_art (pure data, shared by object.py and textures.py)."""

PHOTOS = ["canvas", "pic_west", "map"]

ATLAS = {
    "name": "living_wall_art",
    "size": 1024,
    "regions": {
        "canvas": (0, 0, 589, 261),
        "pic_west": (0, 265, 389, 228),
        "map": (0, 530, 620, 401),              # 17 x 11 in, 36.5 px/in
        "canvas_side": (593, 0, 64, 64),
        "frame_black": (661, 0, 64, 64),
        "frame_cherry": (729, 0, 64, 64),
        "mat_black": (797, 0, 64, 64),
        "paper": (865, 0, 64, 64),
        "tassel_side": (933, 0, 64, 64),
        "tassel": (597, 136, 48, 340),          # 1.7 x 12.1 in
        "diploma_sheet": (624, 530, 400, 338),  # 11.7 x 9.9 in, 34 px/in
        "dip_seal": (624, 872, 120, 120),       # 2.3 in medallion on the mat
        "dip_plate": (748, 872, 276, 40),       # 8.6 x 1.2 in gold lettering on the mat
    },
}
