#!/usr/bin/env python3
"""
Solar System with AUTO-ROTATING CAMERA
- No keyboard input needed
- Camera automatically orbits to show the system
"""

import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

class CelestialBody:
    """Represents a celestial body with hierarchical transformations"""
    
    def __init__(self, name, radius=0.1, color=(1, 1, 1)):
        self.name = name
        self.radius = radius
        self.color = color
        self.orbital_distance = 0.0
        self.orbital_angle = 0.0
        self.orbital_speed = 0.0
        self.axial_tilt = 0.0
        self.tilt_axis = (0, 0, 1)
        self.rotation_angle = 0.0
        self.rotation_speed = 0.0
        self.shininess = 50
        self.specular = 0.5
        self.children = []
    
    def add_child(self, body):
        self.children.append(body)
        return body
    
    def update(self, dt=0.016):
        self.orbital_angle += self.orbital_speed
        self.rotation_angle += self.rotation_speed
        self.orbital_angle = self.orbital_angle % (2 * math.pi)
        self.rotation_angle = self.rotation_angle % 360.0
        for child in self.children:
            child.update(dt)
    
    def draw(self, quadric):
        glPushMatrix()
        
        # ORBITAL REVOLUTION
        if self.orbital_distance > 0:
            x = self.orbital_distance * math.cos(self.orbital_angle)
            z = self.orbital_distance * math.sin(self.orbital_angle)
            glTranslatef(x, 0, z)
        
        # AXIAL TILT
        if self.axial_tilt != 0:
            glRotatef(self.axial_tilt, self.tilt_axis[0], 
                     self.tilt_axis[1], self.tilt_axis[2])
        
        # SELF-ROTATION
        if self.rotation_speed != 0 or self.rotation_angle != 0:
            glRotatef(self.rotation_angle, 0, 1, 0)
        
        # DRAW
        self._draw_sphere(quadric)
        
        # CHILDREN
        for child in self.children:
            child.draw(quadric)
        
        glPopMatrix()
    
    def _draw_sphere(self, quadric):
        glColor3f(*self.color)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, 
                    tuple(c * 0.1 for c in self.color) + (1,))
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.color + (1,))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)
        gluSphere(quadric, self.radius, 32, 32)


def setup_solar_system():
    """Create the solar system with proper hierarchy"""
    
    # SUN (root - at origin)
    sun = CelestialBody("Sun", radius=0.5, color=(1.0, 1.0, 0.0))
    sun.rotation_speed = 2.0
    
    # MERCURY
    mercury = CelestialBody("Mercury", radius=0.08, color=(0.8, 0.6, 0.4))
    mercury.orbital_distance = 2.0
    mercury.orbital_speed = 0.04
    mercury.rotation_speed = 2.0
    sun.add_child(mercury)
    
    # VENUS
    venus = CelestialBody("Venus", radius=0.15, color=(1.0, 0.8, 0.5))
    venus.orbital_distance = 2.8
    venus.orbital_speed = 0.015
    venus.rotation_speed = 0.5
    venus.axial_tilt = 177.0
    sun.add_child(venus)
    
    # EARTH
    earth = CelestialBody("Earth", radius=0.25, color=(0.2, 0.6, 1.0))
    earth.orbital_distance = 3.5
    earth.orbital_speed = 0.01
    earth.axial_tilt = 23.5
    earth.rotation_speed = 3.6
    sun.add_child(earth)
    
    # MOON (orbits Earth, not sun!)
    moon = CelestialBody("Moon", radius=0.07, color=(0.8, 0.8, 0.8))
    moon.orbital_distance = 0.5
    moon.orbital_speed = 0.05
    moon.rotation_speed = 0.05
    earth.add_child(moon)
    
    # ISS SATELLITE
    iss = CelestialBody("ISS", radius=0.02, color=(1.0, 1.0, 0.5))
    iss.orbital_distance = 0.38
    iss.orbital_speed = 0.15
    iss.axial_tilt = 45
    iss.tilt_axis = (0.5, 0.5, 1)
    earth.add_child(iss)
    
    # MARS
    mars = CelestialBody("Mars", radius=0.2, color=(1.0, 0.4, 0.2))
    mars.orbital_distance = 4.5
    mars.orbital_speed = 0.0011
    mars.axial_tilt = 25.2
    mars.rotation_speed = 3.8
    sun.add_child(mars)
    
    # JUPITER
    jupiter = CelestialBody("Jupiter", radius=0.5, color=(1.0, 0.8, 0.4))
    jupiter.orbital_distance = 6.0
    jupiter.orbital_speed = 0.0004
    jupiter.rotation_speed = 5.5
    sun.add_child(jupiter)
    
    # SATURN
    saturn = CelestialBody("Saturn", radius=0.44, color=(1.0, 1.0, 0.7))
    saturn.orbital_distance = 7.5
    saturn.orbital_speed = 0.00025
    saturn.axial_tilt = 27.0
    saturn.rotation_speed = 4.8
    sun.add_child(saturn)
    
    # URANUS
    uranus = CelestialBody("Uranus", radius=0.3, color=(0.4, 0.9, 1.0))
    uranus.orbital_distance = 9.0
    uranus.orbital_speed = 0.0001
    uranus.axial_tilt = 98.0
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


def main():
    if not glfw.init():
        print("GLFW failed")
        return
    
    window = glfw.create_window(1200, 800, "Solar System - AUTO", None, None)
    if not window:
        print("Window failed")
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    
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
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 1200 / 800, 0.1, 500)
    glMatrixMode(GL_MODELVIEW)
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    
    sun, earth = setup_solar_system()
    
    camera_angle = 0.0  # For auto-rotation
    
    print("=== SOLAR SYSTEM - AUTO CAMERA ===")
    print("Camera automatically rotates around the solar system")
    print("Press ESC to exit")
    print("")
    print("You should see:")
    print("  ☀️  Yellow Sun (center)")
    print("  🔵 Blue Earth (tilted 23.5°)")
    print("  ⚪ Gray Moon (orbiting Earth)")
    print("  🟡 Yellow ISS (different orbit)")
    print("  Other planets at various distances")
    
    frame_count = 0
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        
        # Check ESC to quit
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)
        
        # Update
        sun.update()
        
        # AUTO-ROTATING CAMERA
        camera_angle += 0.005
        camera_distance = 15.0
        camera_x = camera_distance * math.cos(camera_angle)
        camera_z = camera_distance * math.sin(camera_angle)
        camera_y = camera_distance * 0.4 * math.sin(camera_angle * 0.5)
        
        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        gluLookAt(
            camera_x, camera_y, camera_z,  # eye
            0, 0, 0,                         # center
            0, 1, 0                          # up
        )
        
        # Draw solar system
        sun.draw(quadric)
        
        glfw.swap_buffers(window)
        
        frame_count += 1
        if frame_count % 120 == 0:
            print(f"Frame {frame_count}: rendering...")
    
    glfw.terminate()
    print("Done!")


if __name__ == "__main__":
    main()
