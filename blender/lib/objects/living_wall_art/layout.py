"""Atlas layout for living_wall_art (pure data, shared by object.py and textures.py)."""

PHOTOS = ["canvas", "pic_west"]

ATLAS = {
    "name": "living_wall_art",
    "size": 1024,
    "regions": {
        "canvas": (0, 0, 589, 261),
        "pic_west": (0, 265, 389, 228),
        "map_standin": (393, 265, 400, 260),
        "canvas_side": (593, 0, 64, 64),
        "frame_black": (661, 0, 64, 64),
        "frame_cherry": (729, 0, 64, 64),
        "mat_black": (797, 0, 64, 64),
        "diploma_sheet": (865, 0, 128, 128),
        "tassel": (593, 68, 64, 64),
        "paper": (661, 68, 64, 64),
    },
}
