import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pywavefront
import math
import random
import time
import os

# ===== AXIAL TILTS (degrees) =====
EARTH_TILT = 23.5
MARS_TILT = 25.2
SATURN_TILT = 27.0
URANUS_TILT = 98.0
NEPTUNE_TILT = 30.0
# =================================

# =========================
# Global Variables
# =========================
quadric = None
cam_rot_y = 0
cam_zoom = -25.0        # Camera distance
city_rotation_angle = 0.0
city_rotation_speed = 0.2
moon_angle = 0.0        # Earth moon orbit
focus_on_earth = False
target_zoom = -25.0
paused = False
city_list = None
# For city transition effect
earth_transition = 0.0  # 0.0 = solar system, 1.0 = city view
transition_direction = 0  # -1 = going back to solar system, 0 = stopped, 1 = going to city
transition_speed = 0.008  # How fast the transition happens per frame (slower = longer animation)
city_cam_rot = 0.0  # Camera rotation angle around the city
city_cam_distance = 120  # Camera distance from city
city_cam_height = 250  # Camera height (increased for better overview)
transition_rotation = 0.0  # Rotation angle during transition for cinematic effect

# Easing function for smoother transitions
def ease_in_out_cubic(t):
    """Smooth easing function for natural acceleration/deceleration."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2

# For FPS Counter
last_time = time.time()
frames = 0
# =========================
# Generate 500 random points once
stars = [(random.uniform(-200, 200), random.uniform(-200, 200), random.uniform(-200, 200)) for _ in range(1000)]
# =========================
# =========================
# Keyboard Callback
# =========================
def key_callback(window, key, scancode, action, mods):
    global cam_rot_y, cam_zoom, focus_on_earth, paused, city_cam_rot, city_cam_distance, city_cam_height, earth_transition, transition_direction, transition_rotation
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_LEFT:
            if earth_transition >= 1.0:  # In city view
                city_cam_rot -= 5
            else:  # In solar system view
                cam_rot_y -= 5
        elif key == glfw.KEY_RIGHT:
            if earth_transition >= 1.0:  # In city view
                city_cam_rot += 5
            else:  # In solar system view
                cam_rot_y += 5
        elif key == glfw.KEY_UP:
            if earth_transition >= 1.0:  # In city view
                city_cam_distance -= 8  # Move camera closer
                city_cam_height += 3  # Move camera higher
            else:  # In solar system view
                cam_zoom += 1   # zoom in
        elif key == glfw.KEY_DOWN:
            if earth_transition >= 1.0:  # In city view
                city_cam_distance += 8  # Move camera farther
                city_cam_height -= 3  # Move camera lower
            else:  # In solar system view
                cam_zoom -= 1   # zoom out
        elif key == glfw.KEY_E and action == glfw.PRESS:
            # Start smooth transition animation
            if earth_transition < 0.5:
                # Currently in solar system, transition to city
                transition_direction = 1
                transition_rotation = 0.0  # Reset rotation for this transition
            else:
                # Currently in city, transition back to solar system
                transition_direction = -1
                transition_rotation = 0.0
        elif key == glfw.KEY_R and action == glfw.PRESS:
            # Reset camera to default city view
            if earth_transition >= 1.0:  # Only in city view
                city_cam_rot = 0.0
                city_cam_distance = 120
                city_cam_height = 250
        elif key == glfw.KEY_SPACE and action == glfw.PRESS:
            paused = not paused

# Mouse tracking for camera control
last_mouse_x = 400
last_mouse_y = 450
mouse_button_pressed = False  # Only update camera when mouse button is held
mouse_sensitivity = 0.3  # Multiplier for mouse movement sensitivity
camera_velocity = {"rot": 0.0, "dist": 0.0, "height": 0.0}  # Smooth camera velocity
camera_damping = 0.85  # Velocity damping for smooth movement

def mouse_callback(window, xpos, ypos):
    global city_cam_rot, city_cam_distance, city_cam_height, last_mouse_x, last_mouse_y, earth_transition, mouse_button_pressed, camera_velocity, mouse_sensitivity
    
    if earth_transition >= 1.0 and mouse_button_pressed:  # Only in city view AND when button pressed
        # Calculate mouse movement
        dx = (xpos - last_mouse_x) * mouse_sensitivity
        dy = (ypos - last_mouse_y) * mouse_sensitivity
        
        # Apply smoothing with velocity damping
        # Horizontal movement (mouse left/right) = rotate around city
        camera_velocity["rot"] = dx * 0.5
        city_cam_rot += camera_velocity["rot"]
        
        # Vertical movement (mouse up/down) = change height and distance
        camera_velocity["height"] = dy * 0.3
        camera_velocity["dist"] = -dy * 0.2
        
        city_cam_height += camera_velocity["height"]
        city_cam_distance += camera_velocity["dist"]
        
        # Clamp values to prevent extreme camera positions
        city_cam_height = max(20.0, min(450.0, city_cam_height))
        city_cam_distance = max(30.0, min(350.0, city_cam_distance))
    
    last_mouse_x = xpos
    last_mouse_y = ypos

def mouse_button_callback(window, button, action, mods):
    global mouse_button_pressed
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            mouse_button_pressed = True
        elif action == glfw.RELEASE:
            mouse_button_pressed = False

# =========================
# Draw Functions
# =========================
def Draw_Sun():
    glDisable(GL_LIGHTING) # sun glows, it doesnot receives light
    glPushMatrix()
    glColor3f(1.0, 1.0, 0.0)
    gluSphere(quadric, 1.0, 50, 50)
    glPopMatrix()
    glEnable(GL_LIGHTING) # Re-enable for planets
# =========================
# to draw orbits
def  Draw_Orbit(distance):
    glDisable(GL_LIGHTING) # Orbits should not show shadows
    # glDisable(GL_DEPTH_TEST)
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3) # subtle grey color
    glLineWidth(0.1)

    glBegin(GL_LINE_LOOP)
    for i in range(100):
        angle = 2 * math.pi *i / 100
        x = distance * math.cos(angle)
        z = distance * math.sin(angle)
        glVertex3f(x, 0, z)
    glEnd()

    glPopMatrix()
    # glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    obj_path = os.path.join(script_dir, 'final- Copy.obj')
    city = pywavefront.Wavefront(obj_path, collect_faces=True)
except:
    print("Could not find the .obj file!")
    city = None

# Parse MTL file directly for accurate material colors
mtl_materials = {}
available_colors = []  # List of all available colors from MTL
mtl_materials_lower = {}  # Lowercase version for case-insensitive matching

def load_mtl_file():
    global mtl_materials, available_colors, mtl_materials_lower
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mtl_path = os.path.join(script_dir, 'final- Copy.mtl')
        with open(mtl_path, 'r') as f:
            current_material = None
            for line in f:
                line = line.strip()
                if line.startswith('newmtl '):
                    current_material = line.split('newmtl ')[1]
                    mtl_materials[current_material] = {}
                    mtl_materials_lower[current_material.lower()] = mtl_materials[current_material]
                elif line.startswith('Kd ') and current_material:
                    # Diffuse color
                    rgb = list(map(float, line.split()[1:4]))
                    mtl_materials[current_material]['diffuse'] = rgb
                    available_colors.append(rgb)
                elif line.startswith('Ka ') and current_material:
                    # Ambient color
                    rgb = list(map(float, line.split()[1:4]))
                    mtl_materials[current_material]['ambient'] = rgb
                elif line.startswith('Ks ') and current_material:
                    # Specular color
                    rgb = list(map(float, line.split()[1:4]))
                    mtl_materials[current_material]['specular'] = rgb
                elif line.startswith('Ns ') and current_material:
                    # Shininess
                    mtl_materials[current_material]['shininess'] = float(line.split()[1])
                elif line.startswith('Ke ') and current_material:
                    # Emission
                    rgb = list(map(float, line.split()[1:4]))
                    mtl_materials[current_material]['emission'] = rgb
        print(f"Loaded {len(mtl_materials)} materials from MTL file with {len(available_colors)} colors")
    except Exception as e:
        print(f"Could not load MTL file: {e}")

load_mtl_file()

def Draw_City():
    if not city: return
    
    glPushAttrib(GL_LIGHTING_BIT | GL_COLOR_BUFFER_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)  # Disable lighting to show colors directly

    matches = 0
    fallbacks = 0
    
    # Debug: Print materials loaded (only once)
    if len(mtl_materials) > 0 and not hasattr(Draw_City, 'debug_printed'):
        print(f"\nDEBUG: MTL Materials loaded: {len(mtl_materials)}")
        print(f"DEBUG: Available colors count: {len(available_colors)}")
        print(f"DEBUG: Sample materials: {list(mtl_materials.keys())[:5]}")
        print(f"DEBUG: Trypywavefront mesh access...")
        if city.meshes:
            first_mesh_name = list(city.meshes.keys())[0]
            first_mesh = city.meshes[first_mesh_name]
            print(f"DEBUG: First mesh name: {first_mesh_name}")
            print(f"DEBUG: First mesh face count: {len(first_mesh.faces)}")
            print(f"DEBUG: First mesh materials: {first_mesh.materials}")
            # Check if faces have material info
            if hasattr(first_mesh, 'mesh_materials'):
                print(f"DEBUG: mesh_materials: {first_mesh.mesh_materials}")
        Draw_City.debug_printed = True
    
    # Parse OBJ directly to get per-face materials
    obj_path = os.path.join(os.path.dirname(__file__), 'final- Copy.obj')
    face_materials = {}  # Map face index to material name
    current_material = None
    face_index = 0
    
    try:
        with open(obj_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('usemtl '):
                    current_material = line.split('usemtl ')[1]
                elif line.startswith('f '):
                    face_materials[face_index] = current_material
                    face_index += 1
    except Exception as e:
        print(f"Error parsing OBJ for materials: {e}")
    
    # Now render with proper per-face materials
    for mesh_name, mesh in city.meshes.items():
        face_idx = 0
        for face in mesh.faces:
            # Get material for this face
            mat_name = face_materials.get(face_idx, "NONE")
            color = [0.5, 0.5, 0.5]  # Default gray
            
            # Try to match material
            if mat_name and mat_name != "NONE":
                if mat_name in mtl_materials:
                    mat = mtl_materials[mat_name]
                    if 'diffuse' in mat:
                        color = mat['diffuse']
                        matches += 1
                elif mat_name.lower() in mtl_materials_lower:
                    mat = mtl_materials_lower[mat_name.lower()]
                    if 'diffuse' in mat:
                        color = mat['diffuse']
                        matches += 1
                else:
                    # Fallback color from available colors
                    if available_colors:
                        color_idx = hash(mat_name) % len(available_colors)
                        color = available_colors[color_idx]
                        fallbacks += 1
            else:
                # No material found, use fallback
                if available_colors:
                    color_idx = hash(f"{face_idx}") % len(available_colors)
                    color = available_colors[color_idx]
                    fallbacks += 1
            
            # Set color for rendering
            glColor3f(float(color[0]), float(color[1]), float(color[2]))

            # Render this face
            glBegin(GL_TRIANGLES)
            for vertex_i in face:
                vertex = city.vertices[vertex_i]
                glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()
            
            face_idx += 1
    
    if matches > 0 or fallbacks > 0:
        print(f"City: {matches} materials matched, {fallbacks} fallback colors - Total faces: {face_idx if 'face_idx' in locals() else 'unknown'}")

    glPopAttrib()

def init_city_list():
    global city_list
    if not city:
        return
    city_list = glGenLists(1)
    glNewList(city_list, GL_COMPILE)
    Draw_City()
    glEndList()


# =========================
# Text Rendering for UI
# =========================
def render_text_2d(x, y, text, font=None):
    """Render 2D text on screen at (x, y) in screen coordinates."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 900, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glColor3f(0.0, 1.0, 0.0)  # Green text
    
    glRasterPos2f(x, y)
    if font is None:
        font = GLUT_BITMAP_HELVETICA_18
    
    for char in text:
        glutBitmapCharacter(font, ord(char))
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_city_ui():
    """Draw UI overlay for city visualization."""
    global city_cam_rot, city_cam_distance, city_cam_height, earth_transition
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 900, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)
    
    # Draw semi-transparent background for text
    glColor4f(0.0, 0.0, 0.0, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(10, 10)
    glVertex2f(350, 10)
    glVertex2f(350, 180)
    glVertex2f(10, 180)
    glEnd()
    
    # Draw text
    glColor3f(0.0, 1.0, 0.0)  # Green text
    glRasterPos2f(20, 40)
    text = "CITY VIEW - Controls:"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glRasterPos2f(20, 65)
    text = "LEFT/RIGHT: Rotate"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glRasterPos2f(20, 85)
    text = "UP/DOWN: Zoom/Height"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glRasterPos2f(20, 105)
    text = "Mouse: Drag to control"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glRasterPos2f(20, 125)
    text = f"Rotation: {city_cam_rot:.1f}\xb0"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glRasterPos2f(20, 145)
    text = f"Height: {city_cam_height:.1f}"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glRasterPos2f(20, 165)
    text = f"Distance: {city_cam_distance:.1f}"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Draw "Press E to return" hint at bottom
    glColor3f(1.0, 1.0, 0.0)  # Yellow text
    glRasterPos2f(250, 880)
    text = "Press E to return to Solar System | R to reset view"
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0) # the sun
    glEnable(GL_COLOR_MATERIAL) # allows glcolor3f to work
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Light position
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.95, 1.0]) # Sunlight color
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0]) # Faint space light
    
    # Material properties - better for Blender models
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

def set_planet_material(color, shininess=50.0, specular_intensity=1.0):
    """Set realistic material properties for planets"""
    r, g, b = color
    glMaterialfv(GL_FRONT, GL_AMBIENT, [r*0.1, g*0.1, b*0.1, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [r, g, b, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [specular_intensity, specular_intensity, specular_intensity, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, min(shininess, 128.0))

def draw_sun_with_glow():
    """Improved sun with emissive glow effect"""
    glDisable(GL_LIGHTING)
    
    glColor3f(1.0, 1.0, 0.0)
    gluSphere(quadric, 1.0, 50, 50)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    glColor4f(1.0, 0.8, 0.0, 0.3)
    gluSphere(quadric, 1.2, 30, 30)
    
    glColor4f(1.0, 0.6, 0.0, 0.15)
    gluSphere(quadric, 1.3, 20, 20)
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_planet_with_atmosphere(radius, color, shininess=50, specular=0.5):
    """Draw planet with atmospheric glow"""
    set_planet_material(color, shininess, specular)
    gluSphere(quadric, radius, 40, 40)
    
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    
    glColor4f(color[0], color[1], color[2], 0.15)
    gluSphere(quadric, radius * 1.08, 30, 30)
    
    glColor4f(color[0], color[1], color[2], 0.08)
    gluSphere(quadric, radius * 1.15, 20, 20)
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

# =========================
# Initialize GLFW
# =========================
if not glfw.init():
    print("GLFW initialization failed!!")
    exit()

window = glfw.create_window(800, 900, "Mini Solar System and City View", None, None)
if not window:
    print("Window Creation Failed")
    glfw.terminate()
    exit()

glfw.make_context_current(window)
glutInit()  # Initialize GLUT for text rendering
glfw.set_key_callback(window, key_callback)
glfw.set_cursor_pos_callback(window, mouse_callback)
glfw.set_mouse_button_callback(window, mouse_button_callback)
glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glEnable(GL_NORMALIZE)
quadric = gluNewQuadric()

# =========================
# Setup Projection
# =========================
glViewport(0, 0, 800, 900)
glMatrixMode(GL_PROJECTION)
gluPerspective(45.0, 800/900, 0.01, 500.0)
glMatrixMode(GL_MODELVIEW)



# =========================
# Planets Setup
# =========================
planets = [
    {"distance":1.5, "radius":0.15, "color":(0.5,0.5,0.5)}, # Mercury
    {"distance":2.5, "radius":0.2,  "color":(1.0,1.0,0.3)}, # Venus
    {"distance":3.5, "radius":0.25, "color":(0.2,0.5,1.0)}, # Earth
    {"distance":4.5, "radius":0.2,  "color":(1.0,0.3,0.3)}, # Mars
    {"distance":6.0, "radius":0.6,  "color":(1.0,0.6,0.2)}, # Jupiter
    {"distance":7.5, "radius":0.5,  "color":(1.0,1.0,0.5)}, # Saturn
    {"distance":9.0, "radius":0.35, "color":(0.3,1.0,1.0)}, # Uranus
    {"distance":10.0,"radius":0.35, "color":(0.2,0.3,1.0)}, # Neptune
    {"distance":11.5,"radius":0.15, "color":(0.7,0.7,0.7)}, # Pluto
]
planet_angle = [0.0]*9
planet_rotation = [0.0]*9
rotation_speed = [0.006,0.005,0.004,0.0036,0.002,0.0016,0.0012,0.001,0.0008]
planet_speeds = [0.004, 0.003, 0.002, 0.0016, 0.001, 0.0008, 0.0006, 0.0004, 0.0002]

# Elliptical orbit eccentricity (0 = circle, closer to 1 = more elliptical)
eccentricity = [0.2, 0.0, 0.0167, 0.09, 0.05, 0.06, 0.05, 0.01, 0.25]

# Jupiter moons tracking
jupiter_moon_angle = [0.0, 0.0]  # Io and Europa
jupiter_moon_speeds = [0.08, 0.04]  # Different orbital speeds

# Comets
comets = [
    {"speed": 0.001, "distance_range": (5, 12), "color": (1.0, 1.0, 0.8)},
    {"speed": 0.0015, "distance_range": (4, 11), "color": (0.9, 1.0, 0.7)},
]
comet_angle = [0.0, 2.0]  # Starting angles

init_city_list()
# =========================
# Main Loop
# =========================
while not glfw.window_should_close(window):
    # ---0. Handle Earth transition animation with easing
    if transition_direction == 1:
        # Transitioning to city
        if earth_transition < 1.0:
            earth_transition += transition_speed  # Smooth transition animation
            if earth_transition >= 1.0:
                earth_transition = 1.0
                transition_direction = 0  # Stop transitioning
                transition_rotation = 0.0
            else:
                # Cinematic rotation during approach
                transition_rotation = ease_in_out_cubic(earth_transition) * 15.0  # Rotate up to 15 degrees
    elif transition_direction == -1:
        # Transitioning back to solar system
        if earth_transition > 0.0:
            earth_transition -= transition_speed
            if earth_transition <= 0.0:
                earth_transition = 0.0
                transition_direction = 0  # Stop transitioning
                transition_rotation = 0.0
            else:
                # Cinematic rotation during departure
                transition_rotation = ease_in_out_cubic(1.0 - earth_transition) * 15.0
    
    # ---1. Handle camera and scene selection and rendering
    # Smooth color transition between space (dark) and city (bright)
    if earth_transition > 0.0:
        # Transitioning to Earth city view
        # Apply easing for smooth color transition
        eased_transition = ease_in_out_cubic(earth_transition)
        sky_color = 0.0 + (0.6 * eased_transition)
        glClearColor(sky_color, 0.3 + (0.5 * eased_transition), 1.0, 1.0)
    else:
        # Solar system view
        glClearColor(0, 0, 0, 1.0)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Calculate Earth position
    earth_dist = planets[2]["distance"]
    earth_x = earth_dist * math.cos(planet_angle[2])
    earth_z = earth_dist * math.sin(planet_angle[2])
    
    # Interpolate camera position based on transition
    if earth_transition < 1.0:
        # Solar system view to Earth transition - smoothly move toward Earth
        # Apply easing function for natural acceleration/deceleration
        eased = ease_in_out_cubic(earth_transition)
        
        # Start position: far back in solar system view
        start_cam_dist = -25.0
        start_cam_height = 0.0
        start_rot_x = 45.0
        
        # End position: positioned at Earth looking down
        end_cam_dist = earth_dist + 5.0  # Close to Earth
        end_cam_height = 5.0
        end_rot_x = 0.0
        
        # Interpolate camera position using eased value
        cam_dist = start_cam_dist + (end_cam_dist - start_cam_dist) * eased
        cam_height = start_cam_height + (end_cam_height - start_cam_height) * eased
        rot_x = start_rot_x + (end_rot_x - start_rot_x) * eased
        
        # Calculate interpolated Earth position with orbital sweep
        # Gradually center on Earth as we transition
        interp_factor = eased
        interp_earth_x = earth_x * (1.0 - interp_factor * 0.8)  # Slowly reduce X offset
        interp_earth_z = earth_z * (1.0 - interp_factor * 0.8)  # Slowly reduce Z offset
        
        # Position camera with cinematic approach
        glTranslatef(-interp_earth_x, -cam_height, cam_dist)
        glRotatef(rot_x, 1, 0, 0)  # Gradually flatten rotation
        glRotatef(cam_rot_y + transition_rotation, 0, 1, 0)  # Add cinematic rotation
        
        # Smooth lighting transition from sun to Earth location
        eased_light = ease_in_out_cubic(earth_transition)
        light_pos_x = earth_x * eased_light
        light_pos_z = earth_z * eased_light
        light_pos_y = 2.0 * eased_light  # Light rises above Earth
        
        glLightfv(GL_LIGHT0, GL_POSITION, [light_pos_x, light_pos_y, light_pos_z, 1])
        # Gradually brighten the ambient light as we approach Earth
        ambient_level = 0.1 + (0.3 * eased_light)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [ambient_level, ambient_level, ambient_level, 1.0])
        
        # Draw starfield with fade-out effect during transition
        glDisable(GL_LIGHTING)
        glPointSize(1.0)
        glBegin(GL_POINTS)
        # Stars fade out as we approach Earth
        star_alpha = 1.0 - ease_in_out_cubic(earth_transition)
        glColor3f(star_alpha, star_alpha, star_alpha)
        for s in stars:
            glVertex3f(*s)
        glEnd()
        glEnable(GL_LIGHTING)
        
        # DRAW SUN
        draw_sun_with_glow()
        
        # Draw comets
        for j, comet in enumerate(comets):
            # Comet position using parametric ellipse
            dist_avg = (comet["distance_range"][0] + comet["distance_range"][1]) / 2
            dist_range = comet["distance_range"][1] - comet["distance_range"][0]
            dist = dist_avg + (dist_range * 0.5 * math.sin(comet_angle[j]))
            cx = dist * math.cos(comet_angle[j])
            cz = dist * math.sin(comet_angle[j])
            glPushMatrix()
            glTranslatef(cx, math.sin(comet_angle[j]*2)*0.5, cz)
            glColor3f(*comet["color"])
            gluSphere(quadric, 0.12, 15, 15)
            # Comet tail
            glDisable(GL_LIGHTING)
            glColor4f(*comet["color"], 0.3)
            glBegin(GL_LINE_STRIP)
            for k in range(8):
                tail_dist = dist - k*0.3
                tail_x = tail_dist * math.cos(comet_angle[j] - 0.5)
                tail_z = tail_dist * math.sin(comet_angle[j] - 0.5)
                glVertex3f(tail_x - cx, math.sin((comet_angle[j]-0.5)*2)*0.5, tail_z - cz)
            glEnd()
            glEnable(GL_LIGHTING)
            glPopMatrix()
        
        # Draw Orbits and Planets
        for i, p in enumerate(planets):
            Draw_Orbit(p['distance'])
            glPushMatrix()
            # Elliptical orbit calculation
            e = eccentricity[i]
            semi_major = p["distance"]
            semi_minor = semi_major * math.sqrt(1 - e*e)
            tx = semi_major * math.cos(planet_angle[i])
            tz = semi_minor * math.sin(planet_angle[i])
            glTranslatef(tx, 0, tz)
            
            # Apply axial tilt before rotation
            if i == 2:  # Earth
                glRotatef(EARTH_TILT, 0, 0, 1)
            elif i == 3:  # Mars
                glRotatef(MARS_TILT, 0, 0, 1)
            elif i == 5:  # Saturn
                glRotatef(SATURN_TILT, 0, 0, 1)
            elif i == 6:  # Uranus
                glRotatef(URANUS_TILT, 0, 0, 1)
            elif i == 7:  # Neptune
                glRotatef(NEPTUNE_TILT, 0, 0, 1)
            
            # Rotate for day/night
            glRotatef(planet_rotation[i], 0, 1, 0)
            
            # Draw planet with materials and atmospheric glow
            if i == 0:  # Mercury - dull rock
                draw_planet_with_atmosphere(p["radius"], p["color"], 20, 0.3)
            elif i == 1:  # Venus - reflective clouds
                draw_planet_with_atmosphere(p["radius"], p["color"], 40, 0.6)
            elif i == 2:  # Earth - shiny oceans
                draw_planet_with_atmosphere(p["radius"], p["color"], 60, 0.8)
            elif i == 3:  # Mars - dull dust
                draw_planet_with_atmosphere(p["radius"], p["color"], 15, 0.1)
            elif i == 4:  # Jupiter
                draw_planet_with_atmosphere(p["radius"], p["color"], 30, 0.4)
            elif i == 5:  # Saturn
                draw_planet_with_atmosphere(p["radius"], p["color"], 50, 0.5)
            else:  # Others
                draw_planet_with_atmosphere(p["radius"], p["color"], 40, 0.4)
            
            # Earth's moon
            if i == 2:
                glPushMatrix()
                glRotatef(math.degrees(moon_angle), 0, 1, 0)
                glTranslatef(0.5, 0, 0)
                set_planet_material((0.8, 0.8, 0.8), 20, 0.2)
                gluSphere(quadric, 0.07, 20, 20)
                glPopMatrix()
            
            if i == 4:  # Jupiter - add moons
                for j, dist in enumerate([0.6, 0.9]):
                    glPushMatrix()
                    glRotatef(math.degrees(jupiter_moon_angle[j]), 0, 1, 0)
                    glTranslatef(dist, 0, 0)
                    glColor3f(0.8, 0.7 + 0.1*j, 0.6)
                    gluSphere(quadric, 0.05 - j*0.01, 15, 15)
                    glPopMatrix()
            
            if i == 5:  # Saturn
                glPushMatrix()
                glRotatef(70, 1, 0.2, 0)
                glColor3f(0.8, 0.7, 0.2)
                gluDisk(quadric, 0.6, 1.1, 50, 1)
                glPopMatrix()
            
            glPopMatrix()
    
    else:
        # Full city close-up view 
        glClearColor(0.6, 0.8, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Switch to perspective projection for city view
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluPerspective(45.0, 800.0/900.0, 0.1, 2000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Camera positioned for isometric/aerial view of city
        # Rotate around the city with LEFT/RIGHT arrows
        # Zoom with UP/DOWN arrows
        cam_distance_x = city_cam_distance * math.cos(math.radians(city_cam_rot + 45))
        cam_distance_z = city_cam_distance * math.sin(math.radians(city_cam_rot + 45))
        
        gluLookAt(cam_distance_x, city_cam_height, cam_distance_z,
                  0, 30, 0,
                  0, 1, 0)
        
        # Lighting - better for showing material colors
        glLightfv(GL_LIGHT0, GL_POSITION, [200.0, 300.0, 200.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])  # Increased ambient to show colors better
        
        # Draw ground plane
        glDisable(GL_LIGHTING)
        glColor3f(0.1, 0.4, 0.1)
        glBegin(GL_QUADS)
        glVertex3f(-600, 0, -600)
        glVertex3f(600, 0, -600)
        glVertex3f(600, 0, 600)
        glVertex3f(-600, 0, 600)
        glEnd()
        glEnable(GL_LIGHTING)
        
        # Draw city at original scale
        glPushMatrix()
        glScalef(0.3, 0.3, 0.3)  # Scale down the city to 30% of original size
        glColor3f(0.8, 0.8, 0.8)
        Draw_City()
        glPopMatrix()
        
        # Restore projection
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    # --- 2. UPDATE ANIMATION ---
    if not paused:
        for i in range(len(planets)):
            planet_angle[i] += planet_speeds[i]
            planet_rotation[i] += rotation_speed[i]
        moon_angle += 0.05
        # Update Jupiter moons
        for j in range(len(jupiter_moon_angle)):
            jupiter_moon_angle[j] += jupiter_moon_speeds[j]
        # Update comets
        for j in range(len(comets)):
            comet_angle[j] += comets[j]["speed"]

    # Draw UI overlay when in city view
    if earth_transition >= 1.0:
        draw_city_ui()

    # FPS Counter Update
    frames += 1
    if time.time() - last_time >= 1.0:
        glfw.set_window_title(window, f"Simulation - FPS: {frames}")
        frames, last_time = 0, time.time()

    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()
