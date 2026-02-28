"""
state.py – All shared mutable globals for the solar system simulation.
Every other module imports this module and accesses globals as state.<name>.
"""
import time
import random

# ── Quadric object (set to gluNewQuadric() in main.py after GL init) ──────────
quadric = None

# ── Camera – solar system view ─────────────────────────────────────────────────
cam_rot_y  = 0
cam_zoom   = -25.0      # camera distance (negative = behind origin)

# ── Earth / city transition ────────────────────────────────────────────────────
earth_transition    = 0.0    # 0.0 = solar system, 1.0 = city view
transition_direction = 0     # -1 going to solar system, 0 stopped, 1 going to city
transition_speed    = 0.008  # progress added per frame
transition_rotation = 0.0    # cinematic rotation during approach

# ── City camera ────────────────────────────────────────────────────────────────
city_cam_rot      = 0.0
city_cam_distance = 120
city_cam_height   = 250

# ── City display list ──────────────────────────────────────────────────────────
city_list = None

# ── Misc ───────────────────────────────────────────────────────────────────────
city_rotation_angle = 0.0
city_rotation_speed = 0.2
moon_angle          = 0.0    # Earth moon orbit angle
focus_on_earth      = False
target_zoom         = -25.0
paused              = False
night_mode          = False  # N key: shift light to dramatic side-angle

# ── Simulation modes ────────────────────────────────────────────────────────────
# S=Standard  C=Cinematic (auto-orbit)  I=Educational (always-on info)  G=God (fast spin)
simulation_mode  = "S"
speed_multiplier = 1.0      # +/- keys scale all orbital and rotation speeds

# ── Visual toggles ────────────────────────────────────────────────────────────
show_elliptical_orbits = False  # T key: toggle elliptical orbit paths
show_planet_labels = False      # L key: toggle planet name labels

# ── Help overlay ───────────────────────────────────────────────────────────────
show_help = True   # shown on startup; H key toggles it

# ── Camera view mode ───────────────────────────────────────────────────────────
camera_view_mode = "normal"  # normal, top-down, side, cinematic

# ── Planet selection & smooth zoom/pan ────────────────────────────────────────
selected_planet = None   # index of currently selected planet, None = none
zoom_target     = None   # cam_zoom value to lerp toward
zoom_speed      = 0.06   # lerp factor per frame
cam_pan_x       = 0.0    # world-space X pan to centre selected planet
cam_pan_z       = 0.0    # world-space Z pan

# ── MVP matrices for gluProject-based picking (updated each frame) ─────────────
_pick_modelview  = None
_pick_projection = None
_pick_viewport   = None

# ── Mouse state ────────────────────────────────────────────────────────────────
last_mouse_x          = 400
last_mouse_y          = 450
mouse_button_pressed  = False
mouse_sensitivity     = 0.3
camera_velocity       = {"rot": 0.0, "dist": 0.0, "height": 0.0}
camera_damping        = 0.85

# ── FPS counter ────────────────────────────────────────────────────────────────
last_time = time.time()
frames    = 0

# ── Starfield (generated once at import time) ──────────────────────────────────
stars = [
    (random.uniform(-200, 200), random.uniform(-200, 200), random.uniform(-200, 200))
    for _ in range(1000)
]

# ── City-specific state (interactive city features) ────────────────────────────
city_day_mode = True            # True = day, False = night
city_drone_mode = False         # Free-look drone camera
city_vehicle_positions = {}     # vehicle_id → current (x, z) position
city_vehicle_speed = 0.5        # units per frame
city_time = 0.0                 # accumulated time for vehicle animations
