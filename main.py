"""
main.py – Entry point: GLFW window, OpenGL setup, and the main render loop.

Run with:  python main.py
"""
import math
import time

import glfw
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

import state
import planet_data as data
import utils
import lighting
import draw_planets
import draw_city
import hud
import input as inp   # 'input' is a built-in name; alias avoids shadowing it

# ── GLFW / OpenGL initialisation ──────────────────────────────────────────────

if not glfw.init():
    print("GLFW initialization failed!")
    raise SystemExit

window = glfw.create_window(1200, 1200, "Mini Solar System and City View", None, None)
if not window:
    print("Window creation failed!")
    glfw.terminate()
    raise SystemExit

glfw.make_context_current(window)
glutInit()   # initialise GLUT for bitmap text

glfw.set_key_callback(window,          inp.key_callback)
glfw.set_cursor_pos_callback(window,   inp.mouse_callback)
glfw.set_mouse_button_callback(window, inp.mouse_button_callback)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glEnable(GL_NORMALIZE)

state.quadric = gluNewQuadric()

# Projection
glViewport(0, 0, 1200, 1200)
glMatrixMode(GL_PROJECTION)
gluPerspective(45.0, 1200 / 1200, 0.01, 500.0)
glMatrixMode(GL_MODELVIEW)

# Compile city geometry into a GL display list
draw_city.init_city_list()

# ── Main loop ─────────────────────────────────────────────────────────────────

while not glfw.window_should_close(window):

    # ── 0. Advance transition animation ───────────────────────────────────────
    if state.transition_direction == 1:
        if state.earth_transition < 1.0:
            state.earth_transition += state.transition_speed
            if state.earth_transition >= 1.0:
                state.earth_transition    = 1.0
                state.transition_direction = 0
                state.transition_rotation  = 0.0
            else:
                state.transition_rotation = (
                    utils.ease_in_out_cubic(state.earth_transition) * 15.0
                )
    elif state.transition_direction == -1:
        if state.earth_transition > 0.0:
            state.earth_transition -= state.transition_speed
            if state.earth_transition <= 0.0:
                state.earth_transition    = 0.0
                state.transition_direction = 0
                state.transition_rotation  = 0.0
            else:
                state.transition_rotation = (
                    utils.ease_in_out_cubic(1.0 - state.earth_transition) * 15.0
                )

    # ── 1. Background colour (space ↔ sky) ────────────────────────────────────
    if state.earth_transition > 0.0:
        eased = utils.ease_in_out_cubic(state.earth_transition)
        glClearColor(eased * 0.6, 0.3 + eased * 0.5, 1.0, 1.0)
    else:
        glClearColor(0, 0, 0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # ── 2. Smooth zoom toward zoom_target (solar system view only) ─────────────
    if state.zoom_target is not None and state.earth_transition < 0.05:
        state.cam_zoom += (state.zoom_target - state.cam_zoom) * state.zoom_speed
        if abs(state.cam_zoom - state.zoom_target) < 0.05:
            state.cam_zoom   = state.zoom_target
            state.zoom_target = None

    # ── 3. Smooth pan to follow selected planet ────────────────────────────────
    if (state.selected_planet is not None
            and "world_pos" in data.planets[state.selected_planet]):
        tgt_x, _, tgt_z = data.planets[state.selected_planet]["world_pos"]
    else:
        tgt_x, tgt_z = 0.0, 0.0
    state.cam_pan_x += (tgt_x - state.cam_pan_x) * 0.05
    state.cam_pan_z += (tgt_z - state.cam_pan_z) * 0.05

    glLoadIdentity()

    # ── 4a. Solar system (or transition) view ─────────────────────────────────
    if state.earth_transition < 1.0:

        earth_dist = data.planets[2]["distance"]
        earth_x    = earth_dist * math.cos(data.planet_angle[2])
        earth_z    = earth_dist * math.sin(data.planet_angle[2])

        eased = utils.ease_in_out_cubic(state.earth_transition)

        cam_dist   = state.cam_zoom + (earth_dist + 5.0 - state.cam_zoom) * eased
        cam_height = 0.0  + (5.0  - 0.0)  * eased
        rot_x      = 45.0 + (0.0  - 45.0) * eased

        interp_x = earth_x * (1.0 - eased * 0.8)
        interp_z = earth_z * (1.0 - eased * 0.8)

        # Apply view mode camera adjustments
        if state.camera_view_mode == "top-down":
            rot_x = 0.0  # looking straight down
            cam_height += 5.0  # higher up
        elif state.camera_view_mode == "side":
            rot_x = -20.0  # side angle
            cam_height += 2.0
            state.cam_rot_y = state.cam_rot_y if state.earth_transition < 0.5 else state.cam_rot_y  # maintain rotation
        elif state.camera_view_mode == "cinematic":
            rot_x = 25.0  # cinematic angle
            cam_dist -= 3.0  # closer for dramatic effect

        glTranslatef(-interp_x, -cam_height, cam_dist)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(state.cam_rot_y + state.transition_rotation, 0, 1, 0)
        glTranslatef(-state.cam_pan_x, 0.0, -state.cam_pan_z)

        # Capture MVP for gluProject-based picking
        state._pick_modelview  = glGetDoublev(GL_MODELVIEW_MATRIX)
        state._pick_projection = glGetDoublev(GL_PROJECTION_MATRIX)
        state._pick_viewport   = glGetIntegerv(GL_VIEWPORT)

        # Lighting: day/night toggle + sun at origin for realistic lighting
        if state.night_mode:
            # Night: dramatic side-angle light, near-zero ambient (dramatic effect)
            glLightfv(GL_LIGHT0, GL_POSITION, [8, 2, 0, 1])
            glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.7, 0.7, 1.0, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.01, 0.01, 0.03, 1.0])
        else:
            # Standard mode: sun at origin with realistic lighting
            # Higher diffuse = brighter sun effect, lower ambient = more contrast
            glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])  # sun at center
            glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 0.95, 1.0])
            # Reduce ambient to show day/night sides clearly
            ambient = 0.05 + 0.15 * eased  # lower base ambient (0.05 instead of 0.1)
            glLightfv(GL_LIGHT0, GL_AMBIENT, [ambient, ambient, ambient, 1.0])

        # Starfield (fades out during transition)
        glDisable(GL_LIGHTING)
        glPointSize(1.0)
        glBegin(GL_POINTS)
        star_alpha = 1.0 - utils.ease_in_out_cubic(state.earth_transition)
        glColor3f(star_alpha, star_alpha, star_alpha)
        for s in state.stars:
            glVertex3f(*s)
        glEnd()
        glEnable(GL_LIGHTING)

        # Sun
        draw_planets.draw_sun_with_glow()

        # Comets
        for j, comet in enumerate(data.comets):
            dist_avg   = (comet["distance_range"][0] + comet["distance_range"][1]) / 2
            dist_range = comet["distance_range"][1] - comet["distance_range"][0]
            dist = dist_avg + dist_range * 0.5 * math.sin(data.comet_angle[j])
            cx   = dist * math.cos(data.comet_angle[j])
            cz   = dist * math.sin(data.comet_angle[j])
            glPushMatrix()
            glTranslatef(cx, math.sin(data.comet_angle[j] * 2) * 0.5, cz)
            glColor3f(*comet["color"])
            gluSphere(state.quadric, 0.12, 15, 15)
            glDisable(GL_LIGHTING)
            glColor4f(*comet["color"], 0.3)
            glBegin(GL_LINE_STRIP)
            for k in range(8):
                td   = dist - k * 0.3
                tx   = td * math.cos(data.comet_angle[j] - 0.5)
                tz   = td * math.sin(data.comet_angle[j] - 0.5)
                glVertex3f(tx - cx,
                           math.sin((data.comet_angle[j] - 0.5) * 2) * 0.5,
                           tz - cz)
            glEnd()
            glEnable(GL_LIGHTING)
            glPopMatrix()

        # Orbits and planets
        for i, p in enumerate(data.planets):
            # Draw orbit guide (circular)
            draw_planets.draw_orbit(p["distance"])
            
            # Optionally draw accurate elliptical orbit path
            if state.show_elliptical_orbits:
                e          = data.eccentricity[i]
                semi_major = p["distance"]
                semi_minor = semi_major * math.sqrt(1 - e * e)
                draw_planets.draw_elliptical_orbit(semi_major, semi_minor)

            # Compute world position outside the local matrix (trail + picking need world space)
            e          = data.eccentricity[i]
            semi_major = p["distance"]
            semi_minor = semi_major * math.sqrt(1 - e * e)
            px         = semi_major * math.cos(data.planet_angle[i])
            pz         = semi_minor * math.sin(data.planet_angle[i])
            p["world_pos"] = (px, 0.0, pz)

            # Append to trail buffer and draw fading trail
            data.planet_trails[i].append((px, 0.0, pz))
            draw_planets.draw_trail(data.planet_trails[i], p["color"])

            glPushMatrix()
            glTranslatef(px, 0, pz)

            # Selection ring (drawn before tilt so it stays horizontal)
            if i == state.selected_planet:
                draw_planets.draw_selection_ring(p["radius"])

            # Axial tilt
            if   i == 2: glRotatef(data.EARTH_TILT,   0, 0, 1)
            elif i == 3: glRotatef(data.MARS_TILT,    0, 0, 1)
            elif i == 5: glRotatef(data.SATURN_TILT,  0, 0, 1)
            elif i == 6: glRotatef(data.URANUS_TILT,  0, 0, 1)
            elif i == 7: glRotatef(data.NEPTUNE_TILT, 0, 0, 1)

            # Axial rotation
            glRotatef(data.planet_rotation[i], 0, 1, 0)

            # Planet sphere with material and atmosphere
            shininess_map = {0: 20, 1: 40, 2: 60, 3: 15, 4: 30, 5: 50}
            specular_map  = {0: 0.3, 1: 0.6, 2: 0.8, 3: 0.1, 4: 0.4, 5: 0.5}
            sh = shininess_map.get(i, 40)
            sp = specular_map.get(i, 0.4)
            draw_planets.draw_planet_with_atmosphere(p["radius"], p["color"], sh, sp)
            
            # Add procedural texture details (clouds, bands, continents, etc.)
            draw_planets.draw_planet_texture_detail(p["radius"], i)
            
            # Selection glow (only when selected – adds extra visual emphasis)
            if i == state.selected_planet:
                draw_planets.draw_selection_glow(p["radius"])
            
            # Draw shadow beneath the planet
            draw_planets.draw_planet_shadow(p["radius"])

            # Earth's moon
            if i == 2:
                glPushMatrix()
                glRotatef(math.degrees(state.moon_angle), 0, 1, 0)
                glTranslatef(0.5, 0, 0)
                lighting.set_planet_material((0.8, 0.8, 0.8), 20, 0.2)
                gluSphere(state.quadric, 0.07, 20, 20)
                glPopMatrix()

            # Jupiter's moons (Io + Europa)
            if i == 4:
                for j, dist in enumerate([0.6, 0.9]):
                    glPushMatrix()
                    glRotatef(math.degrees(data.jupiter_moon_angle[j]), 0, 1, 0)
                    glTranslatef(dist, 0, 0)
                    glColor3f(0.8, 0.7 + 0.1 * j, 0.6)
                    gluSphere(state.quadric, 0.05 - j * 0.01, 15, 15)
                    glPopMatrix()

            # Saturn's rings
            if i == 5:
                glPushMatrix()
                glRotatef(70, 1, 0.2, 0)
                glColor3f(0.8, 0.7, 0.2)
                gluDisk(state.quadric, 0.6, 1.1, 50, 1)
                glPopMatrix()

            glPopMatrix()

    # ── 4b. Full city view ─────────────────────────────────────────────────────
    else:
        # Animate city vehicles
        state.city_time += 1.0
        
        # Sky color: day = blue, night = dark
        if state.city_day_mode:
            glClearColor(0.6, 0.8, 1.0, 1.0)  # bright daytime sky
        else:
            glClearColor(0.05, 0.05, 0.1, 1.0)  # dark night sky
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45.0, 800.0 / 900.0, 0.1, 2000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Drone camera mode: free-look with mouse control
        if state.city_drone_mode:
            # Reset distance to reasonable value on first enter
            if state.city_cam_distance > 300:
                state.city_cam_distance = 100
            if state.city_cam_height > 300:
                state.city_cam_height = 100
            
            # Free-look camera pointing at city center
            cam_x = state.city_cam_distance * math.cos(math.radians(state.city_cam_rot))
            cam_z = state.city_cam_distance * math.sin(math.radians(state.city_cam_rot))
            cam_y = state.city_cam_height
            
            # Look at city center
            gluLookAt(cam_x, cam_y, cam_z,
                      0, 30, 0,
                      0, 1, 0)
        else:
            # Normal orbital camera
            cam_x = state.city_cam_distance * math.cos(math.radians(state.city_cam_rot + 45))
            cam_z = state.city_cam_distance * math.sin(math.radians(state.city_cam_rot + 45))
            gluLookAt(cam_x, state.city_cam_height, cam_z,
                      0, 30, 0,
                      0, 1, 0)

        # Day/Night lighting
        if state.city_day_mode:
            # Bright daytime lighting
            glLightfv(GL_LIGHT0, GL_POSITION, [200.0, 300.0, 200.0, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.5, 0.5, 0.5, 1.0])
        else:
            # Night lighting: dim with blue tint
            glLightfv(GL_LIGHT0, GL_POSITION, [100.0, 150.0, 100.0, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.3, 0.3, 0.4, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.1, 0.1, 0.15, 1.0])

        # Ground plane
        glDisable(GL_LIGHTING)
        if state.city_day_mode:
            glColor3f(0.1, 0.4, 0.1)  # Green grass
        else:
            glColor3f(0.05, 0.1, 0.05)  # Dark green grass at night
        
        glBegin(GL_QUADS)
        glVertex3f(-600, 0, -600); glVertex3f(600, 0, -600)
        glVertex3f( 600, 0,  600); glVertex3f(-600, 0,  600)
        glEnd()
        glEnable(GL_LIGHTING)

        glPushMatrix()
        glScalef(0.3, 0.3, 0.3)
        glColor3f(0.8, 0.8, 0.8)
        draw_city.Draw_City()
        glPopMatrix()

        # Draw moving vehicles
        draw_city.draw_moving_vehicles()
        
        # Draw street lights (only at night)
        if not state.city_day_mode:
            draw_city.draw_street_lights()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    # ── 5. Advance animation ───────────────────────────────────────────────────
    # Cinematic / God mode: auto-rotate camera (skip during city transition)
    if not state.paused and state.earth_transition < 0.5:
        if state.simulation_mode == "C":
            state.cam_rot_y += 0.1    # slow cinematic orbit
        elif state.simulation_mode == "G":
            state.cam_rot_y += 0.5    # fast god-mode spin

    if not state.paused:
        for i in range(len(data.planets)):
            data.planet_angle[i]    += data.planet_speeds[i]    * state.speed_multiplier
            data.planet_rotation[i] += data.rotation_speed[i]   * state.speed_multiplier
        state.moon_angle += 0.05 * state.speed_multiplier
        for j in range(len(data.jupiter_moon_angle)):
            data.jupiter_moon_angle[j] += data.jupiter_moon_speeds[j] * state.speed_multiplier
        for j in range(len(data.comets)):
            data.comet_angle[j] += data.comets[j]["speed"] * state.speed_multiplier

    # ── 6. HUD overlays ────────────────────────────────────────────────────────
    if state.earth_transition >= 1.0:
        hud.draw_city_ui()
    if state.earth_transition < 0.5:
        hud.draw_planet_info_overlay()
        # Show planet name on hover
        if state.show_planet_labels:
            hud.draw_planet_hover_label()

    # Help screen drawn last so it sits on top of everything
    hud.draw_help_overlay()

    # ── 7. FPS counter ─────────────────────────────────────────────────────────
    state.frames += 1
    if time.time() - state.last_time >= 1.0:
        glfw.set_window_title(window, f"Simulation - FPS: {state.frames}")
        state.frames    = 0
        state.last_time = time.time()

    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()
