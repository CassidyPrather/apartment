"""Measurements for scripted objects, in inches as taken, converted to meters once here.

Every value carries its provenance:
  TAPE  - tape-measured by Cassidy
  SPEC  - manufacturer's published dimensions for the exact model
  EST   - estimated from reference photos against a standard size; replace when measured
"""

IN = 0.0254


def m(inches):
    return inches * IN


# --- Filing cabinet: 2-drawer vertical letter file, putty finish (bedroom) ----------
CABINET = {
    "width": m(15.0),            # EST standard letter-width vertical file
    "depth": m(25.0),            # EST top-view proportions ~1.67:1
    "height": m(28.375),         # EST standard 2-drawer height
    "top_wrap": m(1.0),          # EST top cap wraps down the sides/back (visible seam)
    "stile": m(0.625),           # EST side frame visible beside the drawer faces
    "top_rail": m(0.375),        # EST gap from cabinet top to the top drawer face
    "base": m(1.5),              # EST kick below the bottom drawer face
    "gap": m(0.125),             # EST reveal between drawer faces
    "face_proud": m(0.05),       # EST drawer faces sit just proud of the frame
    "sheet": m(0.05),            # EST steel sheet thickness (drawn thicker than real)
    "drawer_box_width": m(12.75),   # EST letter-size file drawer
    "drawer_box_depth": m(23.0),    # EST
    "drawer_box_height": m(10.5),   # EST
    "drawer_travel": m(21.0),       # EST full-suspension slide extension
    # Hardware, positions measured from the top of each drawer face, centered in x.
    "label_w": m(3.5), "label_h": m(1.625), "label_frame": m(0.25),   # EST
    "label_center_from_top": m(3.0),                                  # EST
    "handle_w": m(5.5), "handle_bar": m(0.375), "handle_standoff": m(1.0),  # EST
    "handle_center_from_top": m(6.25),                                # EST
    "latch_w": m(0.6), "latch_h": m(0.45), "latch_d": m(0.35),        # EST
    "lock_d": m(0.75), "lock_proud": m(0.18),                         # EST
    "lock_from_right": m(0.9), "lock_from_top": m(0.8),               # EST
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
    "height": m(6.9),            # EST from photos against the router's SPEC length
    "length": m(5.6),            # EST
    "thick": m(2.25),            # EST
    "corner_r": m(0.55),         # EST
    "foot_len": m(4.9), "foot_thick": m(2.6), "foot_h": m(0.45),  # EST
}

# --- PC VR headset with a halo strap and off-ear speakers ---------------------------
HEADSET = {
    "visor_w": m(5.75),          # EST
    "visor_h": m(1.9),           # EST
    "visor_d": m(1.5),           # EST
    "gasket_d": m(0.9),          # EST
    "arm_len": m(5.5),           # EST
    "halo_len": m(7.6),          # EST outer length of the rear loop
    "halo_w": m(6.6),            # EST
    "speaker_d": m(1.6),         # EST
}

# --- Placement on the cabinet top (cabinet local: +X right, -Y front, Z up) ---------
PLACEMENT = {
    # (x, y, rotation about Z in degrees). Objects sit on the cabinet top.
    "router": (m(-2.4), m(2.8), 92.0),     # EST from the top-down photo
    "modem": (m(1.4), m(9.6), 0.0),        # EST
    "vr_headset": (m(0.4), m(-6.8), 0.0),  # EST visor faces +X
}
