"""Atlas layout for bedroom_fixtures (pure data, shared by object.py and textures.py).
Photo regions are sized to the rectified photos in Reference/bedroom_fixtures_work/final/."""

PHOTOS = ['art_moon', 'art_space', 'art_tree', 'art_center', 'art_purple', 'art_south', 'mid_poster', 'charms', 'corner_poster', 'drawing_bw', 'card_a', 'card_b', 'card_d', 'card_s', 'card_c']

ATLAS = {
    "name": "bedroom_fixtures",
    "size": 2048,
    "regions": {
        'art_space': (0, 0, 546, 728),
        'art_tree': (550, 0, 496, 611),
        'art_center': (1050, 0, 434, 559),
        'art_moon': (0, 732, 758, 453),
        'charms': (762, 732, 300, 390),
        'art_purple': (1066, 732, 495, 369),
        'art_south': (1565, 732, 224, 368),
        'mid_poster': (0, 1189, 260, 335),
        'corner_poster': (264, 1189, 202, 308),
        'drawing_bw': (470, 1189, 248, 278),
        'card_s': (722, 1189, 133, 195),
        'card_a': (859, 1189, 130, 192),
        'card_d': (993, 1189, 115, 190),
        'card_b': (1112, 1189, 126, 173),
        'art_strip': (1242, 1189, 340, 130),
        'card_c': (1586, 1189, 61, 124),
        'vane': (1651, 1189, 128, 512),
        'rail': (1783, 1189, 128, 128),
        'bs_face': (1915, 1189, 128, 128),
        'smoke': (0, 1705, 128, 128),
        'thermo_face': (132, 1705, 128, 128),
        'carrier': (264, 1705, 64, 64),
        'wand': (332, 1705, 64, 64),
        'frame_black': (400, 1705, 64, 64),
        'mat_white': (468, 1705, 64, 64),
        'paper': (536, 1705, 64, 64),
        'frame_white': (604, 1705, 64, 64),
        'bs_body': (672, 1705, 64, 64),
        'bracket': (740, 1705, 64, 64),
        'cable': (808, 1705, 64, 64),
        'thermo': (876, 1705, 64, 64),
    },
}
