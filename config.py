"""
config.py – Centralized configuration for the solar system simulation.

All constants, parameters, and tunable values that affect gameplay,
appearance, and performance live here for easy modification.
"""

# ── WINDOW SETTINGS ────────────────────────────────────────────────────────
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1200
WINDOW_TITLE = "Mini Solar System and City View"

# ── OPENGL RENDERING ──────────────────────────────────────────────────────
GL_NEAR_CLIP = 0.01
GL_FAR_CLIP = 500.0
CAMERA_FOV = 45.0

# City view only (different aspect ratio)
CITY_VIEW_NEAR = 0.1
CITY_VIEW_FAR = 2000.0
CITY_VIEW_WIDTH = 800.0
CITY_VIEW_HEIGHT = 900.0

# ── CAMERA ─────────────────────────────────────────────────────────────────
DEFAULT_CAMERA_ZOOM = -25.0
DEFAULT_CAMERA_ROT_Y = 0
DEFAULT_CAMERA_PAN_X = 0.0
DEFAULT_CAMERA_PAN_Z = 0.0

ZOOM_SPEED = 0.06        # lerp factor per frame
CAM_PAN_SPEED = 0.05     # lerp factor for panning to selected planet
ZOOM_INCREMENT = 1.0     # per arrow key press
CAMERA_ROT_INCREMENT = 5  # degrees per arrow key press

# Smooth speed multipliers
CAMERA_ZOOM_DAMPING = 0.85
MOUSE_SENSITIVITY = 0.3
MOUSE_ROT_SCALE = 0.5
MOUSE_HEIGHT_SCALE = 0.3
MOUSE_DISTANCE_SCALE = 0.2

# ── CAMERA VIEW MODES ──────────────────────────────────────────────────────
CAMERA_MODES = ["normal", "top-down", "side", "cinematic"]
DEFAULT_CAMERA_MODE = "normal"

CAMERA_ROT_NORMAL = 45.0
CAMERA_ROT_TOP_DOWN = 0.0
CAMERA_ROT_SIDE = -20.0
CAMERA_ROT_CINEMATIC = 25.0

CAMERA_HEIGHT_TOP_DOWN = 5.0
CAMERA_HEIGHT_SIDE = 2.0
CAMERA_HEIGHT_CINEMATIC = 0.0

CAMERA_DIST_CINEMATIC = -3.0

# ── ANIMATION & TRANSITIONS ───────────────────────────────────────────────
TRANSITION_SPEED = 0.008  # progress per frame going to/from city
TRANSITION_ROTATION = 15.0

EARTH_TRANSITION_THRESHOLD_LOW = 0.05
EARTH_TRANSITION_THRESHOLD_MID = 0.5
EARTH_TRANSITION_THRESHOLD_HIGH = 1.0

# ── SIMULATION MODES ───────────────────────────────────────────────────────
SIMULATION_MODES = {
    "S": "Standard",
    "C": "Cinematic",
    "I": "Educational",
    "G": "God"
}
DEFAULT_SIMULATION_MODE = "S"

# Auto-rotation speeds in different modes
CINEMATIC_AUTO_ROT_SPEED = 0.1   # degrees/frame
GOD_MODE_ROT_SPEED = 0.5         # degrees/frame

# ── SPEED CONTROL ──────────────────────────────────────────────────────────
DEFAULT_SPEED_MULTIPLIER = 1.0
MIN_SPEED_MULTIPLIER = 0.05
MAX_SPEED_MULTIPLIER = 20.0
SPEED_PRESET_1X = 1.0
SPEED_PRESET_5X = 5.0
SPEED_PRESET_10X = 10.0
SPEED_MULTIPLIER_INCREMENT = 1.2  # for smooth +/- scaling

# ── LIGHTING ───────────────────────────────────────────────────────────────
# Standard (day) mode
LIGHT_POSITION_STANDARD = [0.0, 0.0, 0.0, 1.0]
LIGHT_DIFFUSE_STANDARD = [1.0, 1.0, 0.95, 1.0]
LIGHT_AMBIENT_BASE = 0.05            # lower base ambient for better contrast
LIGHT_AMBIENT_TRANSITION = 0.15      # extra ambient during transition

# Night mode
LIGHT_POSITION_NIGHT = [8, 2, 0, 1]
LIGHT_DIFFUSE_NIGHT = [0.7, 0.7, 1.0, 1.0]
LIGHT_AMBIENT_NIGHT = [0.01, 0.01, 0.03, 1.0]

# City view - day
CITY_LIGHT_POSITION_DAY = [200.0, 300.0, 200.0, 1.0]
CITY_LIGHT_DIFFUSE_DAY = [1.0, 1.0, 1.0, 1.0]
CITY_LIGHT_AMBIENT_DAY = [0.5, 0.5, 0.5, 1.0]

# City view - night
CITY_LIGHT_POSITION_NIGHT = [100.0, 150.0, 100.0, 1.0]
CITY_LIGHT_DIFFUSE_NIGHT = [0.3, 0.3, 0.4, 1.0]
CITY_LIGHT_AMBIENT_NIGHT = [0.1, 0.1, 0.15, 1.0]

# Material properties
MATERIAL_AMBIENT = [0.2, 0.2, 0.2, 1.0]
MATERIAL_DIFFUSE = [0.8, 0.8, 0.8, 1.0]
MATERIAL_SPECULAR = [1.0, 1.0, 1.0, 1.0]
MATERIAL_SHININESS = 50.0

# ── COLORS ────────────────────────────────────────────────────────────────
COLOR_SPACE_BG = (0, 0, 0)
COLOR_CITY_BG_DAY = (0.6, 0.8, 1.0)
COLOR_CITY_BG_NIGHT = (0.05, 0.05, 0.1)

COLOR_GRASS_DAY = (0.1, 0.4, 0.1)
COLOR_GRASS_NIGHT = (0.05, 0.1, 0.05)

COLOR_STAR = (1.0, 1.0, 1.0)

# HUD colors
COLOR_HUD_TEXT_PRIMARY = (0.0, 1.0, 0.0)
COLOR_HUD_TEXT_BRIGHT = (1.0, 1.0, 0.0)
COLOR_HUD_PANEL_BG = (0.0, 0.0, 0.0, 0.5)
COLOR_HUD_BORDER = (0.6, 0.8, 1.0)

# Planet UI
COLOR_PLANET_LABEL = (1.0, 1.0, 0.8)
COLOR_PLANET_INFO_LABEL = (1.0, 0.9, 0.3)
COLOR_PLANET_INFO_VALUE = (1.0, 1.0, 1.0)
COLOR_PLANET_INFO_BG = (0.0, 0.0, 0.1, 0.75)

COLOR_SELECTION_RING = (1.0, 0.9, 0.2)
COLOR_SELECTION_GLOW = (1.0, 0.9, 0.2)

# ── STARFIELD ──────────────────────────────────────────────────────────────
STARFIELD_COUNT = 1000
STARFIELD_EXTENT = 200

# ── ORBIT TRAILS ───────────────────────────────────────────────────────────
TRAIL_LENGTH = 150           # number of positions kept per planet
TRAIL_MAX_ALPHA = 0.55
TRAIL_LINE_WIDTH = 1.2

# ── PLANET SELECTION & HOVERING ────────────────────────────────────────────
HOVER_LABEL_OFFSET_X = 10
HOVER_LABEL_OFFSET_Y = -10
HOVER_PIXEL_THRESHOLD = 25.0
HOVER_PIXEL_SCALE_FACTOR = 60.0

SELECTION_RING_SCALE = 1.7
SELECTION_RING_PULSE_SPEED = 5.0  # Hz

SELECTION_GLOW_SCALE_1 = 1.25
SELECTION_GLOW_SCALE_2 = 1.12
SELECTION_GLOW_PULSE_SPEED = 3.0

# ── PLANET SHADOWS ─────────────────────────────────────────────────────────
SHADOW_RADIUS_X_SCALE = 1.5
SHADOW_RADIUS_Z_SCALE = 2.0
SHADOW_Y_SCALE = 0.08
SHADOW_ALPHA = 0.32
SHADOW_RINGS = 6
SHADOW_SEGMENTS = 56

# ── SUN & GLOW ─────────────────────────────────────────────────────────────
SUN_CORE_RADIUS = 1.0
SUN_GLOW_LAYERS = [
    {"radius": 1.15, "color": (1.0, 0.9, 0.0, 0.6)},
    {"radius": 1.3,  "color": (1.0, 0.7, 0.0, 0.4)},
    {"radius": 1.6,  "color": (1.0, 0.5, 0.0, 0.15)},
    {"radius": 2.0,  "color": (1.0, 0.3, 0.0, 0.08)},
]

# ── COMETS ─────────────────────────────────────────────────────────────────
COMET_SPHERE_RADIUS = 0.12
COMET_SPHERE_SLICES = 15
COMET_SPHERE_STACKS = 15
COMET_TAIL_SEGMENTS = 8
COMET_TAIL_STEP = 0.3
COMET_TAIL_ALPHA = 0.3

# ── MOONS ──────────────────────────────────────────────────────────────────
EARTH_MOON_RADIUS = 0.07
EARTH_MOON_DISTANCE = 0.5
EARTH_MOON_ORBIT_SPEED = 0.05

JUPITER_IO_DISTANCE = 0.6
JUPITER_IO_RADIUS = 0.05
JUPITER_EUROPA_DISTANCE = 0.9
JUPITER_EUROPA_RADIUS = 0.04

# ── SATURN RINGS ───────────────────────────────────────────────────────────
SATURN_RING_INNER_RADIUS = 0.6
SATURN_RING_OUTER_RADIUS = 1.1
SATURN_RING_SLICES = 50
SATURN_RING_ROTATION = [70, 1, 0.2, 0]  # [angle, x, y, z]

# ── ATMOSPHERE EFFECTS ─────────────────────────────────────────────────────
ATMOSPHERE_SCALE_1 = 1.08
ATMOSPHERE_SCALE_2 = 1.15
ATMOSPHERE_ALPHA_1 = 0.15
ATMOSPHERE_ALPHA_2 = 0.08

# ── PLANET TEXTURE DETAILS ─────────────────────────────────────────────────
PLANET_WIREFRAME_MERIDIANS = 10
PLANET_WIREFRAME_PARALLELS = 6
PLANET_WIREFRAME_SCALE = 1.002

# ── CITY VIEW ──────────────────────────────────────────────────────────────
CITY_SCALE = 0.3
CITY_SCALE_Y = 30  # Y-offset view position

CITY_CAM_DEFAULT_ROT = 0.0
CITY_CAM_DEFAULT_DISTANCE = 120
CITY_CAM_DEFAULT_HEIGHT = 250

CITY_CAM_DISTANCE_MIN = 30.0
CITY_CAM_DISTANCE_MAX = 350.0
CITY_CAM_HEIGHT_MIN = 20.0
CITY_CAM_HEIGHT_MAX = 450.0

CITY_CAM_DRONE_DISTANCE_MAX = 300

CITY_ARROW_KEY_ROT = 5      # degrees per key
CITY_ARROW_KEY_DISTANCE = 8
CITY_ARROW_KEY_HEIGHT = 3

# City camera look-at target
CITY_LOOKAT_Y = 30
CITY_LOOKAT_X = 0
CITY_LOOKAT_Z = 0

CITY_CAMERA_UP = [0, 1, 0]  # Y-up

# Ground plane
CITY_GROUND_SIZE = 600

# ── VEHICLES ───────────────────────────────────────────────────────────────
VEHICLE_CYCLE_FRAMES = 500.0  # slower for smoother movement

VEHICLE_1_WIDTH = 1.5
VEHICLE_1_LENGTH = 3.0
VEHICLE_1_Y = 0.1
VEHICLE_1_START_X = -40
VEHICLE_1_END_X = 40
VEHICLE_1_Z = 10
VEHICLE_1_COLOR = (1.0, 0.2, 0.2)  # red

VEHICLE_2_WIDTH = 1.5
VEHICLE_2_LENGTH = 3.0
VEHICLE_2_Y = 0.1
VEHICLE_2_START_Z = -30
VEHICLE_2_END_Z = 50
VEHICLE_2_X = -15
VEHICLE_2_COLOR = (0.2, 0.5, 1.0)  # blue

VEHICLE_3_RADIUS = 20
VEHICLE_3_WIDTH = 1.5
VEHICLE_3_LENGTH = 3.0
VEHICLE_3_Y = 0.1
VEHICLE_3_COLOR = (0.2, 1.0, 0.2)  # green

# ── STREET LIGHTS ──────────────────────────────────────────────────────────
STREET_LIGHT_HEIGHT = 4.0
STREET_LIGHT_RADIUS = 0.5
STREET_LIGHT_GLOW_ALPHA = 0.3
STREET_LIGHT_COLOR = (1.0, 0.9, 0.4)  # warm yellow
STREET_LIGHT_POLE_COLOR = (0.3, 0.3, 0.3)

# Light positions (x, y, z) for rendering
STREET_LIGHT_POSITIONS = [
    (-30, 0.1, 0), (-30, 0.1, 20), (-30, 0.1, 40),
    (0, 0.1, 0), (0, 0.1, 30),
    (30, 0.1, 20), (30, 0.1, 40),
    (-20, 0.1, -20), (20, 0.1, -20)
]

# ── FPS COUNTER ────────────────────────────────────────────────────────────
FPS_UPDATE_INTERVAL = 1.0  # seconds

# ── HELP SCREEN ────────────────────────────────────────────────────────────
HUD_ORTHO_WIDTH = 800
HUD_ORTHO_HEIGHT = 900

HELP_PANEL_WIDTH = 795    # 780 end - 5 start (minus borders)
HELP_PANEL_HEIGHT = 860   # 880 end - 20 start

# ── PICKING (PLANET SELECTION) ─────────────────────────────────────────────
PICKING_THRESHOLD_BASE = 18.0
PICKING_THRESHOLD_SCALE = 60.0

# ── ERROR HANDLING ─────────────────────────────────────────────────────────
LOG_ERRORS = True
CRASH_ON_CRITICAL = False  # if True, exit on critical OpenGL errors
