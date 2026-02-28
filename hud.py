"""
hud.py – 2-D HUD / overlay rendering functions.

All functions temporarily switch to an orthographic projection, draw the UI,
then restore the previous projection matrix.
"""
from OpenGL.GL   import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluProject
import math

import glfw

import state
import planet_data as data


def _begin_2d():
    """Switch to a 2-D ortho projection (800×900, top-left origin)."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 900, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def _end_2d():
    """Restore the 3-D projection matrices."""
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# ── Generic text helper ────────────────────────────────────────────────────────

def render_text_2d(x, y, text, font=None):
    """Render ASCII *text* at screen position (x, y) in green."""
    _begin_2d()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.0, 1.0, 0.0)
    glRasterPos2f(x, y)
    if font is None:
        font = GLUT_BITMAP_HELVETICA_18
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    _end_2d()


# ── City-view control panel ────────────────────────────────────────────────────

def draw_city_ui():
    """Overlay shown while in city view: controls and camera state."""
    _begin_2d()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)

    # Semi-transparent background panel
    glColor4f(0.0, 0.0, 0.0, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(10, 10);  glVertex2f(350, 10)
    glVertex2f(350, 220); glVertex2f(10, 220)
    glEnd()

    def _line(x, y, text, color=(0.0, 1.0, 0.0)):
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    _line(20, 40,  "CITY VIEW - Controls:")
    _line(20, 65,  "LEFT/RIGHT: Rotate")
    _line(20, 85,  "UP/DOWN: Zoom/Height")
    _line(20, 105, "Mouse: Drag to control")
    _line(20, 125, "D: Toggle Day/Night")
    _line(20, 145, "X: Drone Free-Look Mode")
    _line(20, 165, f"Rotation: {state.city_cam_rot:.1f}\xb0")
    _line(20, 185, f"Height: {state.city_cam_height:.1f}")
    _line(20, 205, f"Distance: {state.city_cam_distance:.1f}")

    _line(250, 880,
          "Press E to return to Solar System | R to reset view",
          color=(1.0, 1.0, 0.0))

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    _end_2d()


# ── Selected-planet info panel ────────────────────────────────────────────────

def draw_planet_hover_label():
    """Show planet name when mouse hovers near a planet."""
    if state.earth_transition >= 0.5:
        return  # Only show in solar system view
    
    # Get the primary window (created in main.py)
    windows = glfw.get_windows()
    if not windows:
        return
    
    window = windows[0]
    mx, my = glfw.get_cursor_pos(window)
    _, win_h = glfw.get_framebuffer_size(window)
    
    hovered_planet = None
    best_dist = 25.0  # pixels
    
    for i, p in enumerate(data.planets):
        if "world_pos" not in p:
            continue
        wx, wy, wz = p["world_pos"]
        try:
            sx, sy, _ = gluProject(wx, wy, wz,
                                  state._pick_modelview,
                                  state._pick_projection,
                                  state._pick_viewport)
            sy = win_h - sy
            pix_dist = math.sqrt((mx - sx) ** 2 + (my - sy) ** 2)
            if pix_dist < best_dist:
                best_dist = pix_dist
                hovered_planet = i
        except Exception:
            pass
    
    if hovered_planet is not None:
        planet_name = data.PLANET_INFO[hovered_planet]["name"]
        _begin_2d()
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glColor3f(1.0, 1.0, 0.8)
        glRasterPos2f(mx + 10, my - 10)
        for ch in planet_name:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        _end_2d()


def draw_planet_info_overlay():
    """Fixed info panel in the top-right corner for the selected planet.

    In Educational mode (I) the panel is always shown, defaulting to Earth
    when no planet is explicitly selected.
    """
    # Determine which planet to display
    idx = state.selected_planet
    if idx is None:
        if state.simulation_mode == "I":
            idx = 2   # default to Earth in educational mode
        else:
            return

    info = data.PLANET_INFO[idx]
    p    = data.planets[idx]

    _begin_2d()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Background panel (taller to fit extra rows)
    px, py, pw, ph = 450, 15, 335, 230
    glColor4f(0.0, 0.0, 0.1, 0.75)
    glBegin(GL_QUADS)
    glVertex2f(px,      py);      glVertex2f(px + pw, py)
    glVertex2f(px + pw, py + ph); glVertex2f(px,      py + ph)
    glEnd()

    # Thin border
    glColor4f(0.6, 0.8, 1.0, 0.9)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(px,      py);      glVertex2f(px + pw, py)
    glVertex2f(px + pw, py + ph); glVertex2f(px,      py + ph)
    glEnd()
    glLineWidth(1.0)

    def _hud(x, y, text, color=(1.0, 1.0, 1.0)):
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    # Mode labels
    MODE_LABELS = {"S": "Standard", "C": "Cinematic", "I": "Educational", "G": "God"}

    tx = px + 10
    _hud(tx, py + 22,  info["name"],                                  color=(1.0, 0.9, 0.3))
    _hud(tx, py + 42,  f"Radius   : {info['radius_km']:,} km")
    _hud(tx, py + 58,  f"Day      : {info['day_h']:.1f} hours")
    _hud(tx, py + 74,  f"Year     : {info['year_d']:,} Earth days")
    _hud(tx, py + 90,  f"Moons    : {info['moons']}")
    _hud(tx, py + 106, f"Note     : {info['note']}")
    _hud(tx, py + 126, f"Mode     : {MODE_LABELS.get(state.simulation_mode, state.simulation_mode)}",
         color=(0.4, 1.0, 0.4))
    
    # Speed control with preset buttons and current value
    speed_str = f"Speed:"
    preset_speed = None
    if abs(state.speed_multiplier - 1.0) < 0.01:
        preset_speed = "[1X]"
    elif abs(state.speed_multiplier - 5.0) < 0.01:
        preset_speed = "[5X]"
    elif abs(state.speed_multiplier - 10.0) < 0.01:
        preset_speed = "[10X]"
    
    if preset_speed:
        _hud(tx, py + 142, f"{speed_str}  {preset_speed}  (1/5/0 for preset, +/- fine-tune)",
             color=(1.0, 0.8, 0.2))
    else:
        _hud(tx, py + 142, f"{speed_str}  x{state.speed_multiplier:.2f}  (1/5/0 for preset, +/- fine-tune)",
             color=(1.0, 0.8, 0.2))
    
    _hud(tx, py + 162, f"Orbit Spd: {data.planet_speeds[idx]:.4f} rad/frame")
    _hud(tx, py + 185, "Click again or ESC to deselect",              color=(0.6, 0.6, 0.6))

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    _end_2d()


# ── Help / Welcome overlay ────────────────────────────────────────────────────

def draw_help_overlay():
    """Full-screen semi-transparent help panel shown on startup (H to toggle)."""
    if not state.show_help:
        return

    _begin_2d()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Dark full-screen backdrop
    glColor4f(0.0, 0.0, 0.05, 0.88)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(800, 0)
    glVertex2f(800, 900); glVertex2f(0, 900)
    glEnd()

    # Bright border around the whole panel
    glColor4f(0.4, 0.7, 1.0, 0.9)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(20, 20); glVertex2f(780, 20)
    glVertex2f(780, 880); glVertex2f(20, 880)
    glEnd()
    glLineWidth(1.0)

    def big(x, y, text, color=(1.0, 1.0, 1.0)):
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def small(x, y, text, color=(0.85, 0.85, 0.85)):
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

    # ── Title ─────────────────────────────────────────────────────────────────
    big(180, 60,  "Mini Solar System & Earth City Simulation",
        color=(1.0, 0.9, 0.2))
    big(260, 85,  "Built with Python, PyOpenGL, GLFW, GLU",
        color=(0.6, 0.8, 1.0))

    # ── About ─────────────────────────────────────────────────────────────────
    small(40, 125, "ABOUT THIS PROJECT", color=(0.4, 1.0, 0.4))
    small(40, 145, "An interactive 3-D simulation of the solar system featuring all 9 planets with realistic")
    small(40, 163, "axial tilts, elliptical orbits, fading orbit trails, moons, Saturn's rings, and comets.")
    small(40, 181, "Press E to fly into an Earth city model and explore it from above.")

    # ── Divider ───────────────────────────────────────────────────────────────
    glColor4f(0.4, 0.7, 1.0, 0.4)
    glBegin(GL_LINES)
    glVertex2f(40, 198); glVertex2f(760, 198)
    glEnd()

    # ── Controls – Left column (solar system) ─────────────────────────────────
    cx1 = 40
    small(cx1, 218, "SOLAR SYSTEM CONTROLS", color=(0.4, 1.0, 0.4))
    rows_left = [
        ("Arrow Keys",       "Rotate camera / Zoom in-out"),
        ("Left Click",       "Select a planet (zoom + info)"),
        ("Click again / ESC","Deselect planet"),
        ("SPACE",            "Pause / resume animation"),
        ("N",                "Toggle night-mode lighting"),
        ("T",                "Toggle elliptical orbits"),
        ("L",                "Toggle planet name labels (hover)"),
        ("V",                "Cycle view modes (normal/top/side)"),
        ("E",                "Fly to Earth city view"),
        ("1 / 5 / 0",        "Speed preset: 1X / 5X / 10X"),
        ("= / +",            "Fine-tune speed (smooth)"),
        ("  -",              "Fine-tune speed down"),
    ]
    y = 238
    for key_label, desc in rows_left:
        small(cx1,       y, f"{key_label:<18}", color=(1.0, 0.85, 0.3))
        small(cx1 + 150, y, desc)
        y += 18

    # ── Controls – Right column (city view) ───────────────────────────────────
    cx2 = 420
    small(cx2, 218, "CITY VIEW CONTROLS  (after pressing E)", color=(0.4, 1.0, 0.4))
    rows_right = [
        ("LEFT / RIGHT",  "Rotate camera around city"),
        ("UP / DOWN",     "Move closer / farther + height"),
        ("Mouse drag",    "Free camera rotation"),
        ("D",             "Toggle day/night mode"),
        ("X",             "Toggle drone free-look camera"),
        ("R",             "Reset camera to default"),
        ("E",             "Return to solar system"),
    ]
    y = 238
    for key_label, desc in rows_right:
        small(cx2,       y, f"{key_label:<15}", color=(1.0, 0.85, 0.3))
        small(cx2 + 120, y, desc)
        y += 18

    # ── Divider ───────────────────────────────────────────────────────────────
    glColor4f(0.4, 0.7, 1.0, 0.4)
    glBegin(GL_LINES)
    glVertex2f(40, 580); glVertex2f(760, 580)
    glEnd()

    # ── Simulation modes ──────────────────────────────────────────────────────
    small(40, 600, "SIMULATION MODES", color=(0.4, 1.0, 0.4))
    modes = [
        ("S  Standard",   "Normal manual control — default"),
        ("C  Cinematic",  "Camera slowly auto-orbits the solar system"),
        ("I  Educational","Planet info panel always visible (defaults to Earth)"),
        ("G  God",        "Camera spins fast, great for quick overview"),
    ]
    y = 620
    for label, desc in modes:
        small(40,  y, f"{label:<18}", color=(1.0, 0.85, 0.3))
        small(220, y, desc)
        y += 18

    # ── Divider ───────────────────────────────────────────────────────────────
    glColor4f(0.4, 0.7, 1.0, 0.4)
    glBegin(GL_LINES)
    glVertex2f(40, 690); glVertex2f(760, 690)
    glEnd()

    # ── What to look for ──────────────────────────────────────────────────────
    small(40, 710, "WHAT TO EXPLORE", color=(0.4, 1.0, 0.4))
    tips = [
        "✨ Enhanced lighting: Watch how the sun illuminates planet day/night sides realistically",
        "🎨 Procedural textures: Gas giants have atmospheric bands, Earth has continents & oceans",
        "🔥 Interactive orbits: Press T to see elliptical orbit paths, L to hover-label planets",
        "📊 Multiple views: Press V to switch between normal, top-down, and side viewing angles",
        "⏱️ Speed control: Use 1/5/0 for instant 1X/5X/10X presets, or +/- for fine-tuning",
        "🌍 Click planets to zoom, glow highlights selection, golden ring marks orbit",
    ]
    y = 730
    for tip in tips:
        small(50, y, f"{tip}")
        y += 18

    # ── Footer ────────────────────────────────────────────────────────────────
    big(265, 858, "Press  H  to close this screen and start exploring",
        color=(0.5, 1.0, 0.5))

    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    _end_2d()
