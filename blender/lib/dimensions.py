"""Measurements for scripted objects, in inches as taken, converted to meters once here.

Every value carries its provenance:
  TAPE  - tape-measured by Cassidy
  SCAN  - measured from Cassidy's phone LiDAR capture (Reference/cabinet_capture, 2026-09-24):
          fused depth for sizes, posed-photo orthophotos for layouts; checked against the
          router's SPEC width to within 1.3%. Heights are from the carpet surface.
  SPEC  - manufacturer's published dimensions for the exact model
  EST   - estimated from reference photos against a standard size; replace when measured
"""

IN = 0.0254


def m(inches):
    return inches * IN


# --- Filing cabinet: 2-drawer vertical letter file, putty finish (bedroom) ----------
CABINET = {
    "width": m(15.0),            # SCAN 375-384 mm across the top (standard 15 in letter file)
    "depth": m(26.5),            # SCAN ~670-680 mm front to back along the top
    "height": 0.710,             # SCAN 710 mm, carpet surface to top
    "top_wrap": m(0.8),          # SCAN top cap wraps ~20 mm down the sides/back (visible seam)
    "stile": m(0.9),             # SCAN ~23 mm of frame beside the drawer faces
    "top_rail": 0.0305,          # SCAN top drawer face ends 30.5 mm below the top; holds the lock
    "base": 0.118,               # SCAN plinth under the bottom drawer face
    "gap": 0.003,                # SCAN reveal between the drawer faces
    "top_face_h": 0.283,         # SCAN top drawer face; the bottom one takes the rest (~275 mm)
    "face_proud": m(0.05),       # EST drawer faces sit just proud of the frame
    "sheet": m(0.05),            # EST steel sheet thickness (drawn thicker than real)
    "drawer_box_width": m(12.75),   # EST letter-size file drawer
    "drawer_box_depth": m(24.5),    # EST from the SCAN depth
    "drawer_box_height": m(10.0),   # EST, clears the shorter bottom face
    "drawer_travel": m(22.0),       # EST full-suspension slide extension
    # Hardware, positions measured from the top of each drawer face, centered in x.
    "label_w": 0.087, "label_h": 0.047, "label_frame": m(0.25),       # SCAN size, EST frame width
    "label_center_from_top": 0.072,                                   # SCAN
    "handle_w": 0.107, "handle_bar": m(0.375), "handle_standoff": m(1.0),  # SCAN width, EST bar/standoff
    "handle_center_from_top": 0.182,                                  # SCAN (pull and latch line)
    "latch_w": m(0.6), "latch_h": m(0.45), "latch_d": m(0.35),        # EST
    # The lock sits in the top rail, above the top drawer, not on the drawer face.
    "lock_d": 0.020, "lock_proud": m(0.18),                           # SCAN diameter, EST proud
    "lock_from_right": 0.032, "lock_from_top": 0.015,                 # SCAN, from the right edge and top
    "guard_leg": m(2.25), "guard_wrap": m(0.9), "guard_thick": m(0.2),  # EST
}

# --- Router: dual-band AC1750-class router ------------------------------------------
ROUTER = {
    "length": m(243 / 25.4),     # SPEC 243 mm (front edge)
    "width": m(160.6 / 25.4),    # SPEC 160.6 mm
    "height": m(32.5 / 25.4),    # SPEC 32.5 mm
    "slat_groove": m(0.14),      # EST
    "antenna_len": m(6.6),       # EST
    "antenna_w": m(0.62),        # EST
    "antenna_t": m(0.3),         # EST
}

# --- Cable modem: tower style on an oval foot ---------------------------------------
MODEM = {
    "height": 0.209,             # SCAN overall, foot included
    "length": 0.167,             # SCAN
    "thick": 0.065,              # SCAN
    "corner_r": m(0.55),         # EST
    "foot_len": m(6.0), "foot_thick": m(3.0), "foot_h": m(0.45),  # EST, scaled with the body
}

# --- PC VR headset with a halo strap and off-ear speakers ---------------------------
HEADSET = {
    "visor_w": m(5.75),          # EST (the scan sees ~150 mm of purple across)
    "visor_h": m(1.9),           # EST
    "visor_d": m(1.5),           # EST
    "gasket_d": m(0.9),          # EST
    "arm_len": m(5.5),           # EST
    "halo_len": 0.205,           # SCAN splat: the head loop is ~22 cm across, visor included
    "halo_w": 0.205,             # SCAN
    "halo_tilt": 22.0,           # SCAN back of the loop rides ~12-13 cm up, the front ~3 cm
    "halo_band": 0.030,          # EST rear cradle band height
    "speaker_d": m(1.6),         # EST
}

# --- Placement on the cabinet top (cabinet local: +X right, -Y front, Z up) ---------
PLACEMENT = {
    # (x, y, rotation about Z in degrees). Objects sit on the cabinet top.
    "router": (-0.069, 0.084, 73.5),       # SCAN lid centre and long-axis heading
    "modem": (-0.002, 0.220, -26.5),       # SCAN; the LED end points front-right
    "vr_headset": (0.005, -0.190, -16.0),  # SCAN splat: loop centre, visor front near x=+0.14; it moves around
}
