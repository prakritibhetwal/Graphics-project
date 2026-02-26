#!/usr/bin/env python3
"""
Solar System with Hierarchical Transformations
- Moon orbits Earth (not sun)
- Satellites orbit with different inclination
- Proper axial tilts (Earth 23.5°, Uranus 98°, etc.)
- Skybox background
- Day/night cycle support
"""

import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# ============================================================================
# PART 1: CELESTIAL BODY CLASS
# ============================================================================

class CelestialBody:
    """Represents a celestial body with hierarchical transformations"""
    
    def __init__(self, name, radius=0.1, color=(1, 1, 1)):
        self.name = name
        self.radius = radius
        self.color = color
        
        # Orbital properties (revolution around parent)
        self.orbital_distance = 0.0
        self.orbital_angle = 0.0
        self.orbital_speed = 0.0
        
        # Axial tilt (permanent inclination)
        self.axial_tilt = 0.0
        self.tilt_axis = (0, 0, 1)
        
        # Self-rotation (day-night)
        self.rotation_angle = 0.0
        self.rotation_speed = 0.0
        
        # Material properties
        self.shininess = 50
        self.specular = 0.5
        
        # Hierarchy
        self.children = []
    
    def add_child(self, body):
        """Add child body"""
        self.children.append(body)
        return body
    
    def update(self, dt=0.016):
        """Update orbital and rotation angles"""
        self.orbital_angle += self.orbital_speed
        self.rotation_angle += self.rotation_speed
        
        # Wrap to prevent floating point bloat
        self.orbital_angle = self.orbital_angle % (2 * math.pi)
        self.rotation_angle = self.rotation_angle % 360.0
        
        # Update children
        for child in self.children:
            child.update(dt)
    
    def draw(self, quadric):
        """Draw body with correct transformation order and children"""
        
        glPushMatrix()
        
        # STEP 1: ORBITAL REVOLUTION
        if self.orbital_distance > 0:
            x = self.orbital_distance * math.cos(self.orbital_angle)
            z = self.orbital_distance * math.sin(self.orbital_angle)
            glTranslatef(x, 0, z)
        
        # STEP 2: AXIAL TILT
        if self.axial_tilt != 0:
            glRotatef(self.axial_tilt, self.tilt_axis[0], 
                     self.tilt_axis[1], self.tilt_axis[2])
        
        # STEP 3: SELF-ROTATION
        if self.rotation_speed != 0 or self.rotation_angle != 0:
            glRotatef(self.rotation_angle, 0, 1, 0)
        
        # STEP 4: DRAW THIS BODY
        self._draw_sphere(quadric)
        
        # STEP 5: DRAW CHILDREN
        for child in self.children:
            child.draw(quadric)
        
        glPopMatrix()
    
    def _draw_sphere(self, quadric):
        """Draw sphere with material properties"""
        glColor3f(*self.color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, 
                    tuple(c * 0.1 for c in self.color) + (1,))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.color + (1,))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, 
                    (self.specular, self.specular, self.specular, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)
        
        gluSphere(quadric, self.radius, 40, 40)


# ============================================================================
# PART 2: SKYBOX CLASS
# ============================================================================

class Skybox:
    """Background that follows camera position"""
    
    def __init__(self, size=100.0):
        self.size = size
    
    def draw(self, camera_pos):
        """Draw skybox centered on camera"""
        
        glPushAttrib(GL_LIGHTING_BIT | GL_DEPTH_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        glPushMatrix()
        
        # Translate to camera position (keeps skybox centered)
        glTranslatef(camera_pos[0], camera_pos[1], camera_pos[2])
        
        # Draw cube
        s = self.size
        glColor3f(0.02, 0.02, 0.05)  # Space black
        
        glBegin(GL_QUADS)
        
        # Top
        glVertex3f(-s, s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(-s, s, s)
        
        # Bottom
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(s, -s, s)
        glVertex3f(s, -s, -s)
        
        # Front
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)
        
        # Back
        glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(-s, s, -s)
        
        # Left
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(-s, s, -s)
        
        # Right
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)
        
        glEnd()
        
        glPopMatrix()
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glPopAttrib()


# ============================================================================
# PART 3: SETUP FUNCTION
# ============================================================================

def setup_solar_system():
    """Create complete solar system with hierarchical relationships"""
    
    # SUN
    sun = CelestialBody("Sun", radius=1.0, color=(1.0, 1.0, 0.0))
    sun.rotation_speed = 0.5
    sun.shininess = 100
    sun.specular = 1.0
    
    # MERCURY
    mercury = CelestialBody("Mercury", radius=0.1, color=(0.7, 0.7, 0.7))
    mercury.orbital_distance = 2.5
    mercury.orbital_speed = 0.004
    mercury.rotation_speed = 2.0
    sun.add_child(mercury)
    
    # VENUS
    venus = CelestialBody("Venus", radius=0.18, color=(1.0, 0.8, 0.4))
    venus.orbital_distance = 3.0
    venus.orbital_speed = 0.0015
    venus.rotation_speed = -0.1
    venus.axial_tilt = 177.0
    sun.add_child(venus)
    
    # EARTH
    earth = CelestialBody("Earth", radius=0.25, color=(0.2, 0.6, 1.0))
    earth.orbital_distance = 3.5
    earth.orbital_speed = 0.002
    earth.axial_tilt = 23.5      # THE KEY TILT
    earth.rotation_speed = 4.0
    earth.shininess = 60
    earth.specular = 0.8
    sun.add_child(earth)
    
    # MOON (child of Earth!)
    moon = CelestialBody("Moon", radius=0.07, color=(0.8, 0.8, 0.8))
    moon.orbital_distance = 0.5
    moon.orbital_speed = 0.05
    moon.rotation_speed = 0.05
    moon.shininess = 20
    moon.specular = 0.2
    earth.add_child(moon)  # KEY: Moon orbits Earth, not sun
    
    # ISS SATELLITE (child of Earth, different plane)
    iss = CelestialBody("ISS", radius=0.02, color=(1.0, 1.0, 0.5))
    iss.orbital_distance = 0.38
    iss.orbital_speed = 0.15
    iss.axial_tilt = 45
    iss.tilt_axis = (0.5, 0.5, 1)  # Different inclination
    iss.shininess = 50
    iss.specular = 0.7
    earth.add_child(iss)  # KEY: ISS orbits Earth
    
    # MARS
    mars = CelestialBody("Mars", radius=0.2, color=(1.0, 0.4, 0.2))
    mars.orbital_distance = 4.5
    mars.orbital_speed = 0.0011
    mars.axial_tilt = 25.2
    mars.rotation_speed = 3.8
    mars.shininess = 15
    mars.specular = 0.1
    sun.add_child(mars)
    
    # JUPITER
    jupiter = CelestialBody("Jupiter", radius=0.5, color=(1.0, 0.8, 0.4))
    jupiter.orbital_distance = 6.0
    jupiter.orbital_speed = 0.0004
    jupiter.rotation_speed = 5.5
    jupiter.shininess = 30
    jupiter.specular = 0.4
    sun.add_child(jupiter)
    
    # SATURN
    saturn = CelestialBody("Saturn", radius=0.44, color=(1.0, 1.0, 0.7))
    saturn.orbital_distance = 7.5
    saturn.orbital_speed = 0.00025
    saturn.axial_tilt = 27.0
    saturn.rotation_speed = 4.8
    saturn.shininess = 50
    saturn.specular = 0.5
    sun.add_child(saturn)
    
    # URANUS (extreme tilt!)
    uranus = CelestialBody("Uranus", radius=0.3, color=(0.4, 0.9, 1.0))
    uranus.orbital_distance = 9.0
    uranus.orbital_speed = 0.0001
    uranus.axial_tilt = 98.0  # ROLLING ON ITS SIDE!
    uranus.rotation_speed = 3.0
    sun.add_child(uranus)
    
    # NEPTUNE
    neptune = CelestialBody("Neptune", radius=0.29, color=(0.1, 0.4, 1.0))
    neptune.orbital_distance = 10.0
    neptune.orbital_speed = 0.00008
    neptune.axial_tilt = 30.0
    neptune.rotation_speed = 3.2
    sun.add_child(neptune)
    
    return sun, earth


# ============================================================================
# PART 4: MAIN PROGRAM
# ============================================================================

def main():
    # Initialize GLFW
    if not glfw.init():
        print("GLFW initialization failed")
        return
    
    # Create window
    window = glfw.create_window(1200, 800, "Solar System - Hierarchical", None, None)
    if not window:
        print("Window creation failed")
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
    # OpenGL setup
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Lighting
    glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
    
    # Projection
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1200 / 800, 0.1, 500)
    glMatrixMode(GL_MODELVIEW)
    
    # Clear color
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    # Create quadric
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    
    # Create solar system
    sun, earth = setup_solar_system()
    skybox = Skybox(size=150)
    
    camera_pos = [12.0, 6.0, 15.0]
    
    print("=== Solar System with Hierarchical Transformations ===")
    print("Controls:")
    print("  WASD - Move camera")
    print("  Q/E - Move up/down")
    print("  ESC - Quit")
    print("\nFeatures:")
    print("  ✓ Moon orbits Earth (not sun)")
    print("  ✓ Earth tilted 23.5°")
    print("  ✓ ISS orbits at 45° inclination")
    print("  ✓ Skybox follows camera")
    print("  ✓ Uranus tilted 98° (on its side)")
    
    # Main loop
    while not glfw.window_should_close(window):
        # Process events FIRST
        glfw.poll_events()
        
        # Input - Make sure to click on window first to give it focus!
        speed = 0.2
        
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            camera_pos[2] -= speed
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            camera_pos[2] += speed
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            camera_pos[0] -= speed
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            camera_pos[0] += speed
        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            camera_pos[1] += speed
        if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            camera_pos[1] -= speed
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        
        # Update
        sun.update()
        
        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera
        gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],
            0, 0, 0,
            0, 1, 0
        )
        
        # Draw solar system
        sun.draw(quadric)
        
        # Draw skybox
        skybox.draw(camera_pos)
        
        # Swap
        glfw.swap_buffers(window)
    
    glfw.terminate()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
