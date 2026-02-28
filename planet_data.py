"""
planet_data.py – All static planet / solar-system data.
Imported by main.py, input.py, hud.py, and the draw modules as needed.
"""
from collections import deque

# ── Axial tilts (degrees) ──────────────────────────────────────────────────────
EARTH_TILT   = 23.5
MARS_TILT    = 25.2
SATURN_TILT  = 27.0
URANUS_TILT  = 98.0
NEPTUNE_TILT = 30.0

# ── Static info shown in the HUD when a planet is selected ────────────────────
PLANET_INFO = [
    {"name": "Mercury", "radius_km":  2439, "day_h":  1407.6, "year_d":    88, "moons": 0,   "note": "Retrograde: No"},
    {"name": "Venus",   "radius_km":  6051, "day_h":  5832.5, "year_d":   225, "moons": 0,   "note": "Retrograde: Yes"},
    {"name": "Earth",   "radius_km":  6371, "day_h":    23.9,  "year_d":   365, "moons": 1,   "note": "Only known life"},
    {"name": "Mars",    "radius_km":  3389, "day_h":    24.6,  "year_d":   687, "moons": 2,   "note": "Iron oxide dust"},
    {"name": "Jupiter", "radius_km": 69911, "day_h":     9.9,  "year_d":  4333, "moons": 95,  "note": "Largest planet"},
    {"name": "Saturn",  "radius_km": 58232, "day_h":    10.7,  "year_d": 10756, "moons": 146, "note": "Least dense planet"},
    {"name": "Uranus",  "radius_km": 25362, "day_h":    17.2,  "year_d": 30687, "moons": 27,  "note": "Retrograde: Yes"},
    {"name": "Neptune", "radius_km": 24622, "day_h":    16.1,  "year_d": 60190, "moons": 16,  "note": "Strongest winds"},
    {"name": "Pluto",   "radius_km":  1188, "day_h":   153.3,  "year_d": 90520, "moons": 5,   "note": "Retrograde: Yes"},
]

# ── Planet geometry (distance from sun, sphere radius, base colour) ────────────
planets = [
    {"distance": 1.5,  "radius": 0.15, "color": (0.5, 0.5, 0.5)},  # Mercury
    {"distance": 2.5,  "radius": 0.2,  "color": (1.0, 1.0, 0.3)},  # Venus
    {"distance": 3.5,  "radius": 0.25, "color": (0.2, 0.5, 1.0)},  # Earth
    {"distance": 4.5,  "radius": 0.2,  "color": (1.0, 0.3, 0.3)},  # Mars
    {"distance": 6.0,  "radius": 0.6,  "color": (1.0, 0.6, 0.2)},  # Jupiter
    {"distance": 7.5,  "radius": 0.5,  "color": (1.0, 1.0, 0.5)},  # Saturn
    {"distance": 9.0,  "radius": 0.35, "color": (0.3, 1.0, 1.0)},  # Uranus
    {"distance": 10.0, "radius": 0.35, "color": (0.2, 0.3, 1.0)},  # Neptune
    {"distance": 11.5, "radius": 0.15, "color": (0.7, 0.7, 0.7)},  # Pluto
]

# ── Per-frame mutable animation state ─────────────────────────────────────────
planet_angle    = [0.0] * 9   # orbital angle around the sun
planet_rotation = [0.0] * 9   # axial rotation angle

# Axial rotation speeds (degrees/frame), Earth = 1.0.  Negative = retrograde.
#                Mercury  Venus    Earth   Mars    Jupiter  Saturn  Uranus   Neptune  Pluto
rotation_speed = [0.017, -0.004,   1.0,   0.972,  2.411,   2.246, -1.388,  1.486,  -0.156]

# Orbital speeds (radians/frame)
planet_speeds  = [0.004, 0.003, 0.002, 0.0016, 0.001, 0.0008, 0.0006, 0.0004, 0.0002]

# Elliptical orbit eccentricity (0 = circle)
eccentricity   = [0.2, 0.0, 0.0167, 0.09, 0.05, 0.06, 0.05, 0.01, 0.25]

# ── Jupiter moons ──────────────────────────────────────────────────────────────
jupiter_moon_angle  = [0.0, 0.0]    # Io and Europa
jupiter_moon_speeds = [0.08, 0.04]

# ── Comets ─────────────────────────────────────────────────────────────────────
comets = [
    {"speed": 0.001,  "distance_range": (5, 12), "color": (1.0, 1.0, 0.8)},
    {"speed": 0.0015, "distance_range": (4, 11), "color": (0.9, 1.0, 0.7)},
]
comet_angle = [0.0, 2.0]

# ── Orbit trails (rolling buffer of recent world positions, one per planet) ────
TRAIL_LENGTH  = 150   # number of positions kept per planet
planet_trails = [deque(maxlen=TRAIL_LENGTH) for _ in range(9)]
