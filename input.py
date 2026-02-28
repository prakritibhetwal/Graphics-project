"""
input.py – GLFW keyboard and mouse callback functions.

All callbacks read/write globals through the `state` and `planet_data` modules
so that every other module sees the updated values instantly.
"""
import math

import glfw
from OpenGL.GLU import gluProject

import state
import planet_data as data


# ── Keyboard ───────────────────────────────────────────────────────────────────

def key_callback(window, key, scancode, action, mods):
    if action not in (glfw.PRESS, glfw.REPEAT):
        return

    # ── Arrow keys ─────────────────────────────────────────────────────────────
    if key == glfw.KEY_LEFT:
        if state.earth_transition >= 1.0:
            state.city_cam_rot -= 5
        else:
            state.cam_rot_y -= 5

    elif key == glfw.KEY_RIGHT:
        if state.earth_transition >= 1.0:
            state.city_cam_rot += 5
        else:
            state.cam_rot_y += 5

    elif key == glfw.KEY_UP:
        if state.earth_transition >= 1.0:
            state.city_cam_distance -= 8
            state.city_cam_height   += 3
        else:
            state.cam_zoom += 1

    elif key == glfw.KEY_DOWN:
        if state.earth_transition >= 1.0:
            state.city_cam_distance += 8
            state.city_cam_height   -= 3
        else:
            state.cam_zoom -= 1

    # ── E: toggle Earth city view ──────────────────────────────────────────────
    elif key == glfw.KEY_E and action == glfw.PRESS:
        if state.earth_transition < 0.5:
            state.transition_direction = 1
            state.transition_rotation  = 0.0
        else:
            state.transition_direction = -1
            state.transition_rotation  = 0.0

    # ── R: reset city camera ───────────────────────────────────────────────────
    elif key == glfw.KEY_R and action == glfw.PRESS:
        if state.earth_transition >= 1.0:
            state.city_cam_rot      = 0.0
            state.city_cam_distance = 120
            state.city_cam_height   = 250

    # ── Space: pause / unpause ─────────────────────────────────────────────────
    elif key == glfw.KEY_SPACE and action == glfw.PRESS:
        state.paused = not state.paused

    # ── N: toggle day / night lighting ────────────────────────────────────────
    elif key == glfw.KEY_N and action == glfw.PRESS:
        state.night_mode = not state.night_mode

    # ── H: toggle help / welcome screen ───────────────────────────────────────
    elif key == glfw.KEY_H and action == glfw.PRESS:
        state.show_help = not state.show_help

    # ── T: toggle elliptical orbit visualization ─────────────────────────────
    elif key == glfw.KEY_T and action == glfw.PRESS:
        state.show_elliptical_orbits = not state.show_elliptical_orbits

    # ── L: toggle planet name labels ────────────────────────────────────────
    elif key == glfw.KEY_L and action == glfw.PRESS:
        state.show_planet_labels = not state.show_planet_labels

    # ── V: cycle camera view modes ──────────────────────────────────────────
    elif key == glfw.KEY_V and action == glfw.PRESS:
        modes = ["normal", "top-down", "side", "cinematic"]
        current_idx = modes.index(state.camera_view_mode)
        state.camera_view_mode = modes[(current_idx + 1) % len(modes)]

    # ── Simulation modes ───────────────────────────────────────────────────────
    elif key == glfw.KEY_S and action == glfw.PRESS:
        state.simulation_mode = "S"   # Standard
    elif key == glfw.KEY_C and action == glfw.PRESS:
        state.simulation_mode = "C"   # Cinematic – camera auto-orbits
    elif key == glfw.KEY_I and action == glfw.PRESS:
        state.simulation_mode = "I"   # Educational – info overlay always on
    elif key == glfw.KEY_G and action == glfw.PRESS:
        state.simulation_mode = "G"   # God – high-speed auto-spin

    # ── Speed presets: 1X, 5X, 10X ────────────────────────────────────────────
    elif key == glfw.KEY_1 and action == glfw.PRESS:
        state.speed_multiplier = 1.0   # Normal speed
    elif key == glfw.KEY_5 and action == glfw.PRESS:
        state.speed_multiplier = 5.0   # 5x speed
    elif key == glfw.KEY_0 and action == glfw.PRESS:
        state.speed_multiplier = 10.0  # 10x speed

    # ── Speed controls (fine-tuning) ────────────────────────────────────────────
    elif key == glfw.KEY_EQUAL:        # = / + key: increase smoothly
        state.speed_multiplier = min(state.speed_multiplier * 1.2, 20.0)
    elif key == glfw.KEY_MINUS:        # - key: decrease smoothly
        state.speed_multiplier = max(state.speed_multiplier * 0.8, 0.05)

    # ── Escape: deselect planet and zoom back out ──────────────────────────────
    elif key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        state.selected_planet = None
        state.zoom_target     = -25.0
        state.cam_pan_x       = 0.0
        state.cam_pan_z       = 0.0

    # ── City view controls (active when in city view, earth_transition >= 1.0) ──
    if state.earth_transition >= 1.0 and action == glfw.PRESS:
        # D: toggle day/night in city
        if key == glfw.KEY_D:
            state.city_day_mode = not state.city_day_mode
        
        # X: toggle drone mode (free-look camera)
        elif key == glfw.KEY_X:
            state.city_drone_mode = not state.city_drone_mode


# ── Mouse motion ───────────────────────────────────────────────────────────────

def mouse_callback(window, xpos, ypos):
    if state.earth_transition >= 1.0 and state.mouse_button_pressed:
        dx = (xpos - state.last_mouse_x) * state.mouse_sensitivity
        dy = (ypos - state.last_mouse_y) * state.mouse_sensitivity

        state.camera_velocity["rot"]    = dx * 0.5
        state.city_cam_rot             += state.camera_velocity["rot"]

        state.camera_velocity["height"] = dy * 0.3
        state.camera_velocity["dist"]   = -dy * 0.2

        state.city_cam_height   += state.camera_velocity["height"]
        state.city_cam_distance += state.camera_velocity["dist"]

        state.city_cam_height   = max(20.0,  min(450.0, state.city_cam_height))
        state.city_cam_distance = max(30.0,  min(350.0, state.city_cam_distance))

    state.last_mouse_x = xpos
    state.last_mouse_y = ypos


# ── Mouse button ───────────────────────────────────────────────────────────────

def mouse_button_callback(window, button, action, mods):
    if button != glfw.MOUSE_BUTTON_LEFT:
        return

    # Track drag state for city view
    if action == glfw.PRESS:
        state.mouse_button_pressed = True
    elif action == glfw.RELEASE:
        state.mouse_button_pressed = False

    # Planet picking (solar system view only)
    if (action == glfw.PRESS
            and state.earth_transition < 0.5
            and state._pick_modelview is not None):

        mx, my   = glfw.get_cursor_pos(window)
        _, win_h = glfw.get_framebuffer_size(window)

        best_i    = None
        best_dist = float("inf")

        for i, p in enumerate(data.planets):
            if "world_pos" not in p:
                continue
            wx, wy, wz = p["world_pos"]
            try:
                sx, sy, _ = gluProject(wx, wy, wz,
                                       state._pick_modelview,
                                       state._pick_projection,
                                       state._pick_viewport)
                sy       = win_h - sy          # flip: GL=bottom-origin, GLFW=top-origin
                pix_dist = math.sqrt((mx - sx) ** 2 + (my - sy) ** 2)
                threshold = max(18.0, p["radius"] * 60.0)
                if pix_dist < threshold and pix_dist < best_dist:
                    best_dist = pix_dist
                    best_i    = i
            except Exception:
                pass

        if best_i is not None:
            if state.selected_planet == best_i:
                # Re-click same planet → deselect
                state.selected_planet = None
                state.zoom_target     = -25.0
                state.cam_pan_x       = 0.0
                state.cam_pan_z       = 0.0
            else:
                state.selected_planet = best_i
                state.zoom_target     = -(data.planets[best_i]["distance"] * 1.1 + 1.5)
        else:
            # Clicked empty space → deselect
            state.selected_planet = None
            state.zoom_target     = -25.0
            state.cam_pan_x       = 0.0
            state.cam_pan_z       = 0.0
