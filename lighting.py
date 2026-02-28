"""
lighting.py – OpenGL lighting initialisation and per-planet material setup.
"""
from OpenGL.GL import *


def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)                          # the sun
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 0.95, 1.0])  # warm sunlight
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.1, 0.1, 0.1,  1.0])  # faint space fill

    glMaterialfv(GL_FRONT, GL_AMBIENT,  [0.2, 0.2, 0.2, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE,  [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, 50.0)


def set_planet_material(color, shininess=50.0, specular_intensity=1.0):
    """Set realistic material properties for a planet sphere."""
    r, g, b = color
    glMaterialfv(GL_FRONT, GL_AMBIENT,  [r * 0.1, g * 0.1, b * 0.1, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE,  [r, g, b, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR,
                 [specular_intensity, specular_intensity, specular_intensity, 1.0])
    glMaterialf (GL_FRONT, GL_SHININESS, min(shininess, 128.0))
    # GL_COLOR_MATERIAL is active (AMBIENT_AND_DIFFUSE), so glColor overrides
    # glMaterialfv for ambient+diffuse.  Reset it here so no leftover colour
    # from ring/overlay drawing bleeds into the next planet.
    glColor3f(r, g, b)
