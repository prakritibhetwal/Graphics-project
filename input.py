"""
input.py – Organized GLFW keyboard and mouse callback functions.

All callbacks dispatch to command functions which encapsulate the logic.
This maintains separation between callbacks and the actual commands.
"""
import math
from typing import Optional

import glfw
from OpenGL.GLU import gluProject

import state
import planet_data as data
import config
from error_handler import log_error, safe_call


# ═════════════════════════════════════════════════════════════════════════════
# ── CAMERA COMMANDS (SOLAR SYSTEM VIEW)
# ═════════════════════════════════════════════════════════════════════════════

def cmd_rotate_camera_left() -> None:
    """Rotate camera left (counterclockwise) when in solar system view."""
    if state.earth_transition < config.EARTH_TRANSITION_THRESHOLD_MID:
        state.cam_rot_y -= config.CAMERA_ROT_INCREMENT


def cmd_rotate_camera_right() -> None:
    """Rotate camera right (clockwise) when in solar system view."""
    if state.earth_transition < config.EARTH_TRANSITION_THRESHOLD_MID:
        state.cam_rot_y += config.CAMERA_ROT_INCREMENT


def cmd_zoom_in() -> None:
    """Zoom the camera in (increase distance) in solar system view."""
    if state.earth_transition < config.EARTH_TRANSITION_THRESHOLD_MID:
        state.cam_zoom += config.ZOOM_INCREMENT


def cmd_zoom_out() -> None:
    """Zoom the camera out (decrease distance) in solar system view."""
    if state.earth_transition < config.EARTH_TRANSITION_THRESHOLD_MID:
        state.cam_zoom -= config.ZOOM_INCREMENT


def cmd_deselect_planet() -> None:
    """Deselect the currently selected planet and reset camera."""
    state.selected_planet = None
    state.zoom_target = config.DEFAULT_CAMERA_ZOOM
    state.cam_pan_x = config.DEFAULT_CAMERA_PAN_X
    state.cam_pan_z = config.DEFAULT_CAMERA_PAN_Z


def cmd_toggle_pause() -> None:
    """Toggle animation pause/resume."""
    state.paused = not state.paused


def cmd_toggle_night_mode() -> None:
    """Toggle dramatic night-mode lighting in solar system view."""
    state.night_mode = not state.night_mode


def cmd_toggle_help() -> None:
    """Toggle the help overlay display."""
    state.show_help = not state.show_help


def cmd_toggle_elliptical_orbits() -> None:
    """Toggle visualization of elliptical orbit paths."""
    state.show_elliptical_orbits = not state.show_elliptical_orbits


def cmd_toggle_planet_labels() -> None:
    """Toggle planet name labels on hover."""
    state.show_planet_labels = not state.show_planet_labels


def cmd_cycle_camera_view_mode() -> None:
    """Cycle through camera view modes (normal → top-down → side → cinematic)."""
    try:
        modes = config.CAMERA_MODES
        current_idx = modes.index(state.camera_view_mode)
        state.camera_view_mode = modes[(current_idx + 1) % len(modes)]
    except (ValueError, IndexError) as e:
        log_error(f"Failed to cycle camera modes: {e}", error_type="INPUT_ERROR")
        state.camera_view_mode = config.DEFAULT_CAMERA_MODE


# ═════════════════════════════════════════════════════════════════════════════
# ── SIMULATION MODE COMMANDS
# ═════════════════════════════════════════════════════════════════════════════

def cmd_set_simulation_mode_standard() -> None:
    """Switch to Standard simulation mode (manual control)."""
    state.simulation_mode = "S"


def cmd_set_simulation_mode_cinematic() -> None:
    """Switch to Cinematic mode (auto-orbiting camera)."""
    state.simulation_mode = "C"


def cmd_set_simulation_mode_educational() -> None:
    """Switch to Educational mode (always show planet info)."""
    state.simulation_mode = "I"


def cmd_set_simulation_mode_god() -> None:
    """Switch to God mode (fast camera spin)."""
    state.simulation_mode = "G"


# ═════════════════════════════════════════════════════════════════════════════
# ── SPEED CONTROL COMMANDS
# ═════════════════════════════════════════════════════════════════════════════

def cmd_set_speed_1x() -> None:
    """Set simulation speed to 1X (normal)."""
    state.speed_multiplier = config.SPEED_PRESET_1X


def cmd_set_speed_5x() -> None:
    """Set simulation speed to 5X."""
    state.speed_multiplier = config.SPEED_PRESET_5X


def cmd_set_speed_10x() -> None:
    """Set simulation speed to 10X."""
    state.speed_multiplier = config.SPEED_PRESET_10X


def cmd_increase_speed() -> None:
    """Increase speed by 20% (smooth fine-tuning)."""
    state.speed_multiplier = min(
        state.speed_multiplier * config.SPEED_MULTIPLIER_INCREMENT,
        config.MAX_SPEED_MULTIPLIER
    )


def cmd_decrease_speed() -> None:
    """Decrease speed by 20% (smooth fine-tuning)."""
    state.speed_multiplier = max(
        state.speed_multiplier / config.SPEED_MULTIPLIER_INCREMENT,
        config.MIN_SPEED_MULTIPLIER
    )


# ═════════════════════════════════════════════════════════════════════════════
# ── EARTH TRANSITION COMMANDS
# ═════════════════════════════════════════════════════════════════════════════

def cmd_toggle_earth_city_view() -> None:
    """Toggle between solar system and Earth city views.
    
    When going to Earth city, first selects Earth directly so camera zooms to it.
    """
    if state.earth_transition < config.EARTH_TRANSITION_THRESHOLD_MID:
        # Going TO city view - select Earth first so camera zooms to it
        cmd_select_planet(2)  # Earth is index 2
        state.transition_direction = 1
        state.transition_rotation = 0.0
    else:
        # Going back to solar system
        state.transition_direction = -1
        state.transition_rotation = 0.0


# ═════════════════════════════════════════════════════════════════════════════
# ── CITY VIEW COMMANDS
# ═════════════════════════════════════════════════════════════════════════════

def cmd_city_rotate_left() -> None:
    """Rotate city camera left."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_cam_rot -= config.CITY_ARROW_KEY_ROT


def cmd_city_rotate_right() -> None:
    """Rotate city camera right."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_cam_rot += config.CITY_ARROW_KEY_ROT


def cmd_city_zoom_in() -> None:
    """Move city camera closer and higher."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_cam_distance -= config.CITY_ARROW_KEY_DISTANCE
        state.city_cam_height += config.CITY_ARROW_KEY_HEIGHT


def cmd_city_zoom_out() -> None:
    """Move city camera farther and lower."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_cam_distance += config.CITY_ARROW_KEY_DISTANCE
        state.city_cam_height -= config.CITY_ARROW_KEY_HEIGHT


def cmd_city_reset_camera() -> None:
    """Reset city camera to default position."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_cam_rot = config.CITY_CAM_DEFAULT_ROT
        state.city_cam_distance = config.CITY_CAM_DEFAULT_DISTANCE
        state.city_cam_height = config.CITY_CAM_DEFAULT_HEIGHT


def cmd_city_toggle_day_night() -> None:
    """Toggle day/night mode in city view."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_day_mode = not state.city_day_mode


def cmd_city_toggle_drone_mode() -> None:
    """Toggle free-look drone camera mode in city view."""
    if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
        state.city_drone_mode = not state.city_drone_mode


# ═════════════════════════════════════════════════════════════════════════════
# ── PLANET PICKING / SELECTION
# ═════════════════════════════════════════════════════════════════════════════

def _pick_planet_at_cursor(window) -> Optional[int]:
    """
    Determine which planet (if any) is under the cursor.
    
    Uses gluProject to convert world coordinates to screen coordinates
    and checks distance to cursor position.
    
    Args:
        window: GLFW window to get cursor position from
        
    Returns:
        Planet index if one is under cursor, None otherwise
    """
    try:
        if state._pick_modelview is None:
            return None
        
        mx, my = glfw.get_cursor_pos(window)
        _, win_h = glfw.get_framebuffer_size(window)
        
        best_i = None
        best_dist = float("inf")
        
        for i, p in enumerate(data.planets):
            if "world_pos" not in p:
                continue
            
            wx, wy, wz = p["world_pos"]
            try:
                sx, sy, _ = gluProject(
                    wx, wy, wz,
                    state._pick_modelview,
                    state._pick_projection,
                    state._pick_viewport
                )
                sy = win_h - sy  # flip: GL=bottom-origin, GLFW=top-origin
                pix_dist = math.sqrt((mx - sx) ** 2 + (my - sy) ** 2)
                
                threshold = max(
                    config.PICKING_THRESHOLD_BASE,
                    p["radius"] * config.PICKING_THRESHOLD_SCALE
                )
                
                if pix_dist < threshold and pix_dist < best_dist:
                    best_dist = pix_dist
                    best_i = i
            except Exception as e:
                log_error(f"gluProject failed for planet {i}: {e}", error_type="PICKING_ERROR")
                continue
        
        return best_i
    except Exception as e:
        log_error(f"Planet picking failed: {e}", error_type="PICKING_ERROR", print_traceback=True)
        return None


def cmd_select_planet(planet_index: int) -> None:
    """
    Select a planet and zoom to it with a dramatic close-up view.
    
    Args:
        planet_index: Index of the planet to select
    """
    try:
        if 0 <= planet_index < len(data.planets):
            state.selected_planet = planet_index
            p = data.planets[planet_index]
            # Calculate zoom to show planet large and impressive
            # Uses planet radius (visual size) as primary factor for dramatic zoom
            radius = p["radius"]
            distance = p["distance"]
            state.zoom_target = -(radius * 10 + distance * 0.2)
    except IndexError as e:
        log_error(f"Invalid planet index {planet_index}: {e}", error_type="INPUT_ERROR")


# ═════════════════════════════════════════════════════════════════════════════
# ── GLFW CALLBACKS
# ═════════════════════════════════════════════════════════════════════════════

def key_callback(window, key, scancode, action, mods) -> None:
    """GLFW key callback: dispatch key events to command functions."""
    if action not in (glfw.PRESS, glfw.REPEAT):
        return

    # Only PRESS events for single-action toggles
    press_only = action == glfw.PRESS
    
    # Arrow keys (handle both solar system and city views)
    try:
        if key == glfw.KEY_LEFT:
            if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
                cmd_city_rotate_left()
            else:
                cmd_rotate_camera_left()
        elif key == glfw.KEY_RIGHT:
            if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
                cmd_city_rotate_right()
            else:
                cmd_rotate_camera_right()
        elif key == glfw.KEY_UP:
            if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
                cmd_city_zoom_in()
            else:
                cmd_zoom_in()
        elif key == glfw.KEY_DOWN:
            if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH:
                cmd_city_zoom_out()
            else:
                cmd_zoom_out()
        
        # Mode and view toggles (PRESS only)
        elif press_only:
            if key == glfw.KEY_E:
                cmd_toggle_earth_city_view()
            elif key == glfw.KEY_R:
                cmd_city_reset_camera()
            elif key == glfw.KEY_SPACE:
                cmd_toggle_pause()
            elif key == glfw.KEY_N:
                cmd_toggle_night_mode()
            elif key == glfw.KEY_H:
                cmd_toggle_help()
            elif key == glfw.KEY_T:
                cmd_toggle_elliptical_orbits()
            elif key == glfw.KEY_L:
                cmd_toggle_planet_labels()
            elif key == glfw.KEY_V:
                cmd_cycle_camera_view_mode()
            elif key == glfw.KEY_S:
                cmd_set_simulation_mode_standard()
            elif key == glfw.KEY_C:
                cmd_set_simulation_mode_cinematic()
            elif key == glfw.KEY_I:
                cmd_set_simulation_mode_educational()
            elif key == glfw.KEY_G:
                cmd_set_simulation_mode_god()
            elif key == glfw.KEY_1:
                cmd_set_speed_1x()
            elif key == glfw.KEY_5:
                cmd_set_speed_5x()
            elif key == glfw.KEY_0:
                cmd_set_speed_10x()
            elif key == glfw.KEY_EQUAL:
                cmd_increase_speed()
            elif key == glfw.KEY_MINUS:
                cmd_decrease_speed()
            elif key == glfw.KEY_ESCAPE:
                cmd_deselect_planet()
            elif key == glfw.KEY_D:
                cmd_city_toggle_day_night()
            elif key == glfw.KEY_X:
                cmd_city_toggle_drone_mode()
    except Exception as e:
        log_error(f"Key callback error: {e}", error_type="CALLBACK_ERROR", print_traceback=True)


def mouse_callback(window, xpos, ypos) -> None:
    """GLFW mouse motion callback: handle city view mouse-drag camera control."""
    try:
        if state.earth_transition >= config.EARTH_TRANSITION_THRESHOLD_HIGH and state.mouse_button_pressed:
            dx = (xpos - state.last_mouse_x) * state.mouse_sensitivity
            dy = (ypos - state.last_mouse_y) * state.mouse_sensitivity
            
            state.camera_velocity["rot"] = dx * config.MOUSE_ROT_SCALE
            state.city_cam_rot += state.camera_velocity["rot"]
            
            state.camera_velocity["height"] = dy * config.MOUSE_HEIGHT_SCALE
            state.camera_velocity["dist"] = -dy * config.MOUSE_DISTANCE_SCALE
            
            state.city_cam_height += state.camera_velocity["height"]
            state.city_cam_distance += state.camera_velocity["dist"]
            
            # Clamp to reasonable bounds
            state.city_cam_height = max(
                config.CITY_CAM_HEIGHT_MIN,
                min(config.CITY_CAM_HEIGHT_MAX, state.city_cam_height)
            )
            state.city_cam_distance = max(
                config.CITY_CAM_DISTANCE_MIN,
                min(config.CITY_CAM_DISTANCE_MAX, state.city_cam_distance)
            )
        
        state.last_mouse_x = xpos
        state.last_mouse_y = ypos
    except Exception as e:
        log_error(f"Mouse callback error: {e}", error_type="CALLBACK_ERROR")


def mouse_button_callback(window, button, action, mods) -> None:
    """GLFW mouse button callback: handle planet picking and city view dragging."""
    try:
        if button != glfw.MOUSE_BUTTON_LEFT:
            return
        
        # Track drag state for city view
        if action == glfw.PRESS:
            state.mouse_button_pressed = True
        elif action == glfw.RELEASE:
            state.mouse_button_pressed = False
        
        # Planet picking (solar system view only)
        if (action == glfw.PRESS and
                state.earth_transition < config.EARTH_TRANSITION_THRESHOLD_MID and
                state._pick_modelview is not None):
            
            picked_planet = _pick_planet_at_cursor(window)
            
            if picked_planet is not None:
                if state.selected_planet == picked_planet:
                    # Re-click same planet → deselect
                    cmd_deselect_planet()
                else:
                    # Click new planet → select it
                    cmd_select_planet(picked_planet)
            else:
                # Clicked empty space → deselect
                cmd_deselect_planet()
    except Exception as e:
        log_error(f"Mouse button callback error: {e}", error_type="CALLBACK_ERROR", print_traceback=True)
