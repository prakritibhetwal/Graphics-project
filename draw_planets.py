"""
draw_planets.py – Drawing functions for the sun, planetary bodies, and orbits.
All functions use the shared `quadric` object stored in state.py.
"""
import math
import time

from OpenGL.GL  import *
from OpenGL.GLU import *

import state
from lighting import set_planet_material


# ── Sun ────────────────────────────────────────────────────────────────────────

def draw_sun_with_glow():
    """Solid sun sphere with dramatic glow and light rays for maximum visual impact."""
    glDisable(GL_LIGHTING)

    # Bright core
    glColor3f(1.0, 1.0, 0.0)
    gluSphere(state.quadric, 1.0, 60, 60)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive blending for realistic glow

    # Inner bright glow
    glColor4f(1.0, 0.9, 0.0, 0.6)
    gluSphere(state.quadric, 1.15, 40, 40)
    
    # Mid glow
    glColor4f(1.0, 0.7, 0.0, 0.4)
    gluSphere(state.quadric, 1.3, 35, 35)

    # Outer glow (large and fading)
    glColor4f(1.0, 0.5, 0.0, 0.15)
    gluSphere(state.quadric, 1.6, 30, 30)
    
    # Dramatic outer corona
    glColor4f(1.0, 0.3, 0.0, 0.08)
    gluSphere(state.quadric, 2.0, 25, 25)

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


# ── Orbits ─────────────────────────────────────────────────────────────────────

def draw_orbit(distance):
    """Draw a circular orbit guide in the XZ plane."""
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.3)
    glLineWidth(0.1)
    glBegin(GL_LINE_LOOP)
    for i in range(100):
        angle = 2 * math.pi * i / 100
        glVertex3f(distance * math.cos(angle), 0, distance * math.sin(angle))
    glEnd()
    glPopMatrix()
    glEnable(GL_LIGHTING)


def draw_elliptical_orbit(semi_major, semi_minor):
    """Draw an elliptical orbit path (more realistic than circles)."""
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glColor3f(0.25, 0.35, 0.25)  # subtle green for ellipse
    glLineWidth(0.15)
    glBegin(GL_LINE_LOOP)
    for i in range(120):
        angle = 2 * math.pi * i / 120
        x = semi_major * math.cos(angle)
        z = semi_minor * math.sin(angle)
        glVertex3f(x, 0.01, z)  # slightly above XZ plane
    glEnd()
    
    # Sun position marker at focus (foci - not exactly at origin for ellipse)
    glColor3f(1.0, 0.8, 0.0)
    glPointSize(4.0)
    glBegin(GL_POINTS)
    glVertex3f(0, 0.02, 0)  # sun at center (approximate)
    glEnd()
    glPointSize(1.0)
    
    glPopMatrix()
    glEnable(GL_LIGHTING)


# ── Planets ────────────────────────────────────────────────────────────────────

def draw_planet_with_atmosphere(radius, color, shininess=50, specular=0.5):
    """
    Draw a planet sphere with:
      - proper material colours
      - a sparse wireframe lat/lon overlay (makes axial rotation visible)
      - two translucent atmosphere halos
      - realistic lighting showing day/night terminator
    """
    set_planet_material(color, shininess, specular)
    gluSphere(state.quadric, radius, 40, 40)
    
    # Night-side darkening for realism (back side faces away from sun at origin)
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Semitransparent dark layer on night side
    r, g, b = color
    glColor4f(r * 0.15, g * 0.15, b * 0.15, 0.35)
    gluQuadricDrawStyle(state.quadric, GLU_FILL)
    
    # Draw a "dark side" by translating and drawing another sphere
    # This creates the effect of the sun lighting only the front
    glPushMatrix()
    glTranslatef(0, 0, -radius * 1.8)  # offset behind planet
    gluSphere(state.quadric, radius * 1.1, 30, 30)
    glPopMatrix()
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

    # Wireframe overlay – makes spin clearly visible
    glDisable(GL_LIGHTING)
    r, g, b = color
    glColor3f(r * 0.5, g * 0.5, b * 0.5)
    gluQuadricDrawStyle(state.quadric, GLU_LINE)
    gluSphere(state.quadric, radius * 1.002, 10, 6)   # 10 meridians, 6 parallels
    gluQuadricDrawStyle(state.quadric, GLU_FILL)       # restore for all later draws
    glEnable(GL_LIGHTING)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    glColor4f(color[0], color[1], color[2], 0.15)
    gluSphere(state.quadric, radius * 1.08, 30, 30)

    glColor4f(color[0], color[1], color[2], 0.08)
    gluSphere(state.quadric, radius * 1.15, 20, 20)

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def draw_planet_texture_detail(radius, planet_index):
    """
    Add procedural texture details to planets:
    - Gas giants: atmospheric bands and swirls
    - Earth: continents and oceans
    - Mars: canyons and polar caps
    - Others: subtle surface features
    """
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Planet-specific texture patterns
    if planet_index == 1:  # Venus - cloudy with swirls
        glColor4f(0.8, 0.6, 0.1, 0.15)
        for i in range(3):
            glRotatef(45, 1, 0, 0)
            glBegin(GL_LINE_LOOP)
            for j in range(32):
                angle = 2 * math.pi * j / 32
                y = radius * 0.9 * math.sin(angle + i * 0.5)
                x = radius * 0.95 * math.cos(angle)
                glVertex3f(x, y, 0)
            glEnd()
    
    elif planet_index == 2:  # Earth - continents and water
        glColor4f(0.0, 0.3, 0.1, 0.2)  # dark green continents
        # Northern continents
        glBegin(GL_TRIANGLES)
        glVertex3f(radius * 0.4, radius * 0.3, 0)
        glVertex3f(radius * 0.6, radius * 0.2, 0)
        glVertex3f(radius * 0.5, radius * 0.5, 0)
        glEnd()
        # Southern continents
        glColor4f(0.1, 0.2, 0.05, 0.15)
        glBegin(GL_TRIANGLES)
        glVertex3f(-radius * 0.3, -radius * 0.4, 0)
        glVertex3f(-radius * 0.5, -radius * 0.2, 0)
        glVertex3f(-radius * 0.4, -radius * 0.5, 0)
        glEnd()
    
    elif planet_index == 3:  # Mars - rust and canyons
        glColor4f(0.6, 0.2, 0.1, 0.18)  # dark canyons
        # Valles Marineris-like feature
        glBegin(GL_LINES)
        for i in range(6):
            angle = i * math.pi / 5
            glVertex3f(radius * 0.7 * math.cos(angle), -radius * 0.4, radius * 0.5 * math.sin(angle))
            glVertex3f(radius * 0.8 * math.cos(angle), -radius * 0.2, radius * 0.6 * math.sin(angle))
        glEnd()
        # Polar ice caps
        glColor4f(0.9, 0.9, 0.95, 0.2)
        glBegin(GL_QUADS)
        glVertex3f(-radius * 0.5, radius * 0.6, -radius * 0.2)
        glVertex3f(radius * 0.5, radius * 0.6, -radius * 0.2)
        glVertex3f(radius * 0.5, radius * 0.8, -radius * 0.1)
        glVertex3f(-radius * 0.5, radius * 0.8, -radius * 0.1)
        glEnd()
    
    elif planet_index == 4:  # Jupiter - thick bands
        glColor4f(0.6, 0.4, 0.1, 0.25)
        for band in range(6):
            y = radius * (0.6 - band * 0.2)
            glBegin(GL_LINE_LOOP)
            for i in range(64):
                angle = 2 * math.pi * i / 64
                x = radius * 1.05 * math.cos(angle)
                z = radius * 0.3 * math.sin(angle)
                glVertex3f(x, y, z)
            glEnd()
        # Great Red Spot
        glColor4f(1.0, 0.4, 0.1, 0.3)
        glBegin(GL_TRIANGLE_FAN)
        for i in range(32):
            angle = 2 * math.pi * i / 32
            x = radius * 0.3 * math.cos(angle)
            z = radius * 0.2 * math.sin(angle)
            glVertex3f(x, -radius * 0.3, z)
        glEnd()
    
    elif planet_index == 5:  # Saturn - subtle bands
        glColor4f(0.85, 0.75, 0.5, 0.2)
        for band in range(4):
            y = radius * (0.4 - band * 0.2)
            glBegin(GL_LINE_LOOP)
            for i in range(48):
                angle = 2 * math.pi * i / 48
                x = radius * 1.08 * math.cos(angle)
                z = radius * 0.2 * math.sin(angle)
                glVertex3f(x, y, z)
            glEnd()
    
    elif planet_index == 6:  # Uranus - faint methane clouds
        glColor4f(0.3, 0.7, 0.85, 0.15)
        glBegin(GL_LINE_LOOP)
        for i in range(48):
            angle = 2 * math.pi * i / 48
            x = radius * 1.08 * math.cos(angle)
            y = radius * 0.4 * math.sin(angle * 0.5)
            z = radius * 0.2 * math.sin(angle)
            glVertex3f(x, y, z)
        glEnd()
    
    elif planet_index == 7:  # Neptune - storm features
        glColor4f(0.2, 0.3, 0.8, 0.2)
        # Great Dark Spot equivalent
        glBegin(GL_TRIANGLE_FAN)
        for i in range(32):
            angle = 2 * math.pi * i / 32
            x = radius * 0.25 * math.cos(angle)
            z = radius * 0.15 * math.sin(angle)
            glVertex3f(x, -radius * 0.4, z)
        glEnd()
        # Scooter clouds
        glColor4f(0.6, 0.7, 1.0, 0.15)
        glBegin(GL_LINE_STRIP)
        for i in range(24):
            angle = i * math.pi / 12
            x = radius * 0.8 * math.cos(angle)
            y = radius * 0.3 * math.sin(angle * 2)
            z = radius * 0.4 * math.sin(angle)
            glVertex3f(x, y, z)
        glEnd()
    
    glEnable(GL_LIGHTING)
    glDisable(GL_BLEND)
    glPopMatrix()


def draw_trail(trail, color):
    """Draw a fading orbit trail as a GL_LINE_STRIP.

    *trail* is a deque of (x, y, z) world positions (oldest first).
    The line fades from fully transparent at the tail to half-opaque at the head.
    """
    if len(trail) < 2:
        return

    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glLineWidth(1.2)

    r, g, b   = color
    n         = len(trail)
    positions = list(trail)   # oldest → newest

    glBegin(GL_LINE_STRIP)
    for k, pos in enumerate(positions):
        alpha = (k / (n - 1)) * 0.55   # 0.0 at oldest, 0.55 at newest
        glColor4f(r, g, b, alpha)
        glVertex3f(*pos)
    glEnd()

    glLineWidth(1.0)
    glDisable(GL_LINE_SMOOTH)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def draw_selection_ring(radius):
    """Pulsing gold ring drawn in the XZ plane around a selected planet."""
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    pulse   = 0.55 + 0.45 * math.sin(time.time() * 5.0)
    glColor4f(1.0, 0.9, 0.2, pulse)
    glLineWidth(2.0)

    ring_r = radius * 1.7
    glBegin(GL_LINE_LOOP)
    for k in range(72):
        a = 2.0 * math.pi * k / 72
        glVertex3f(ring_r * math.cos(a), 0.0, ring_r * math.sin(a))
    glEnd()

    glLineWidth(1.0)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()


def draw_selection_glow(radius):
    """Subtle glow effect around a selected planet for enhanced visibility."""
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive blend for glow
    
    # Multi-layer glow effect
    pulse = 0.3 + 0.2 * math.sin(time.time() * 3.0)
    
    # Outer glow layer
    glColor4f(1.0, 0.9, 0.2, pulse * 0.3)
    gluSphere(state.quadric, radius * 1.25, 30, 30)
    
    # Inner glow layer (stronger)
    glColor4f(1.0, 0.95, 0.3, pulse * 0.5)
    gluSphere(state.quadric, radius * 1.12, 25, 25)
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()

def draw_planet_shadow(radius):
    """
    Draw a realistic shadow on the ground beneath a planet.
    
    Uses the sun position to cast a shadow - darker and more dramatic
    when sun is low, lighter when directly overhead.
    """
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Shadow dimensions - elliptical shape
    shadow_radius_x = radius * 1.5
    shadow_radius_z = radius * 2.0
    shadow_y = -radius * 0.08
    shadow_alpha = 0.32
    
    # Gradient shadow with concentric ellipses for natural look
    num_rings = 6
    for ring in range(num_rings):
        ring_pos = ring / (num_rings - 1) if num_rings > 1 else 1.0
        ring_alpha = shadow_alpha * max(0.0, (1.0 - ring_pos) ** 1.8)
        curr_r_x = shadow_radius_x * ring_pos
        curr_r_z = shadow_radius_z * ring_pos
        
        glColor4f(0.0, 0.0, 0.0, ring_alpha)
        glBegin(GL_LINE_LOOP)
        for segment in range(56):
            angle = 2.0 * math.pi * segment / 56
            x = curr_r_x * math.cos(angle)
            z = curr_r_z * math.sin(angle)
            glVertex3f(x, shadow_y, z)
        glEnd()
    
    # Dark gradient core
    glBegin(GL_TRIANGLE_FAN)
    glColor4f(0.0, 0.0, 0.0, shadow_alpha * 0.85)
    glVertex3f(0, shadow_y, 0)
    for segment in range(57):
        angle = 2.0 * math.pi * segment / 56
        x = shadow_radius_x * 0.35 * math.cos(angle)
        z = shadow_radius_z * 0.35 * math.sin(angle)
        glColor4f(0.0, 0.0, 0.0, shadow_alpha * 0.5)
        glVertex3f(x, shadow_y, z)
    glEnd()
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)
    glPopMatrix()