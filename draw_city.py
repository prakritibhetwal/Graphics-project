"""
draw_city.py – City OBJ model loading and rendering.

The OBJ and MTL files are expected to sit in the same directory as this script.
The OBJ is loaded once at import time; `init_city_list()` must be called after
OpenGL is initialised to compile the geometry into a display list.
"""
import os
import math
import time

import pywavefront
from OpenGL.GL import *
from OpenGL.GLU import gluSphere

import state

# ── File paths ─────────────────────────────────────────────────────────────────
_script_dir = os.path.dirname(os.path.abspath(__file__))
_obj_path   = os.path.join(_script_dir, "final- Copy.obj")
_mtl_path   = os.path.join(_script_dir, "final- Copy.mtl")

# ── Load OBJ ───────────────────────────────────────────────────────────────────
try:
    city = pywavefront.Wavefront(_obj_path, collect_faces=True)
except Exception:
    print("Could not find the .obj file!")
    city = None

# ── Parse MTL for accurate material colours ────────────────────────────────────
mtl_materials       = {}   # material name  → {diffuse, ambient, specular, …}
mtl_materials_lower = {}   # lowercase name → same dict (for case-insensitive match)
available_colors    = []   # flat list of all diffuse RGB values

def load_mtl_file():
    global mtl_materials, mtl_materials_lower, available_colors
    try:
        with open(_mtl_path, "r") as f:
            current = None
            for line in f:
                line = line.strip()
                if line.startswith("newmtl "):
                    current = line.split("newmtl ")[1]
                    mtl_materials[current] = {}
                    mtl_materials_lower[current.lower()] = mtl_materials[current]
                elif line.startswith("Kd ") and current:
                    rgb = list(map(float, line.split()[1:4]))
                    mtl_materials[current]["diffuse"] = rgb
                    available_colors.append(rgb)
                elif line.startswith("Ka ") and current:
                    mtl_materials[current]["ambient"] = list(map(float, line.split()[1:4]))
                elif line.startswith("Ks ") and current:
                    mtl_materials[current]["specular"] = list(map(float, line.split()[1:4]))
                elif line.startswith("Ns ") and current:
                    mtl_materials[current]["shininess"] = float(line.split()[1])
                elif line.startswith("Ke ") and current:
                    mtl_materials[current]["emission"] = list(map(float, line.split()[1:4]))
        print(f"Loaded {len(mtl_materials)} materials from MTL file "
              f"with {len(available_colors)} colours")
    except Exception as e:
        print(f"Could not load MTL file: {e}")

load_mtl_file()


# ── Internal helper: build face→material mapping from the OBJ ─────────────────
def _build_face_materials():
    """Return a dict {face_index: material_name} by scanning the OBJ directly."""
    mapping = {}
    current = None
    idx     = 0
    try:
        with open(_obj_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("usemtl "):
                    current = line.split("usemtl ")[1]
                elif line.startswith("f "):
                    mapping[idx] = current
                    idx += 1
    except Exception as e:
        print(f"Error parsing OBJ for materials: {e}")
    return mapping


# ── Main draw function ─────────────────────────────────────────────────────────
def Draw_City():
    if not city:
        return

    glPushAttrib(GL_LIGHTING_BIT | GL_COLOR_BUFFER_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)  # show vertex colours directly

    # Debug printout (runs once)
    if mtl_materials and not getattr(Draw_City, "_debug_printed", False):
        print(f"\nDEBUG: MTL Materials loaded: {len(mtl_materials)}")
        print(f"DEBUG: Available colours count: {len(available_colors)}")
        print(f"DEBUG: Sample materials: {list(mtl_materials.keys())[:5]}")
        if city.meshes:
            name  = list(city.meshes.keys())[0]
            mesh  = city.meshes[name]
            print(f"DEBUG: First mesh name: {name}")
            print(f"DEBUG: First mesh face count: {len(mesh.faces)}")
            print(f"DEBUG: First mesh materials: {mesh.materials}")
        Draw_City._debug_printed = True

    face_materials = _build_face_materials()
    matches   = 0
    fallbacks = 0

    for _mesh_name, mesh in city.meshes.items():
        for face_idx, face in enumerate(mesh.faces):
            mat_name = face_materials.get(face_idx, "NONE")
            color    = [0.5, 0.5, 0.5]  # default grey

            if mat_name and mat_name != "NONE":
                if mat_name in mtl_materials and "diffuse" in mtl_materials[mat_name]:
                    color = mtl_materials[mat_name]["diffuse"]
                    matches += 1
                elif mat_name.lower() in mtl_materials_lower and "diffuse" in mtl_materials_lower[mat_name.lower()]:
                    color = mtl_materials_lower[mat_name.lower()]["diffuse"]
                    matches += 1
                elif available_colors:
                    color = available_colors[hash(mat_name) % len(available_colors)]
                    fallbacks += 1
            elif available_colors:
                color = available_colors[hash(str(face_idx)) % len(available_colors)]
                fallbacks += 1

            glColor3f(float(color[0]), float(color[1]), float(color[2]))
            glBegin(GL_TRIANGLES)
            for vi in face:
                v = city.vertices[vi]
                glVertex3f(v[0], v[1], v[2])
            glEnd()

    if matches > 0 or fallbacks > 0:
        print(f"City: {matches} materials matched, {fallbacks} fallback colours")

    glPopAttrib()


# ── Display-list compiler (call once after GL init) ────────────────────────────
def init_city_list():
    if not city:
        return
    state.city_list = glGenLists(1)
    glNewList(state.city_list, GL_COMPILE)
    Draw_City()
    glEndList()

# ── Vehicle rendering ──────────────────────────────────────────────────────────

def draw_vehicle(x, y, z, width=2.0, length=4.0, color=(1.0, 0.3, 0.2)):
    """Draw a simple rectangular vehicle (car)."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    
    # Simple box for car body
    glBegin(GL_QUADS)
    # Front/back
    glVertex3f(-width/2, 0, -length/2)
    glVertex3f(width/2, 0, -length/2)
    glVertex3f(width/2, 1.5, -length/2)
    glVertex3f(-width/2, 1.5, -length/2)
    
    glVertex3f(-width/2, 0, length/2)
    glVertex3f(width/2, 0, length/2)
    glVertex3f(width/2, 1.5, length/2)
    glVertex3f(-width/2, 1.5, length/2)
    
    # Sides
    glVertex3f(-width/2, 0, -length/2)
    glVertex3f(-width/2, 0, length/2)
    glVertex3f(-width/2, 1.5, length/2)
    glVertex3f(-width/2, 1.5, -length/2)
    
    glVertex3f(width/2, 0, -length/2)
    glVertex3f(width/2, 0, length/2)
    glVertex3f(width/2, 1.5, length/2)
    glVertex3f(width/2, 1.5, -length/2)
    
    # Top
    glVertex3f(-width/2, 1.5, -length/2)
    glVertex3f(width/2, 1.5, -length/2)
    glVertex3f(width/2, 1.5, length/2)
    glVertex3f(-width/2, 1.5, length/2)
    glEnd()
    
    glPopMatrix()


def draw_street_lights():
    """Draw animated street lights (brighter at night)."""
    if state.city_day_mode:
        return  # Don't draw lights during day
    
    # Light positions along streets
    light_positions = [
        (-30, 0.1, 0), (-30, 0.1, 20), (-30, 0.1, 40),
        (0, 0.1, 0), (0, 0.1, 30),
        (30, 0.1, 20), (30, 0.1, 40),
        (-20, 0.1, -20), (20, 0.1, -20)
    ]
    
    glPushMatrix()
    glDisable(GL_LIGHTING)
    
    # Warm yellow light color
    glow_color = (1.0, 0.9, 0.4)
    
    for pos in light_positions:
        glTranslatef(pos[0], pos[1], pos[2])
        
        # Pole
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 4.0, 0)
        glEnd()
        
        # Light bulb with glow
        glColor4f(*glow_color, 0.3)
        gluSphere(state.quadric if state.quadric else None, 0.5, 16, 16)
        
        glTranslatef(-pos[0], -pos[1], -pos[2])
    
    glEnable(GL_LIGHTING)
    glPopMatrix()


def draw_moving_vehicles():
    """Draw vehicles moving smoothly along predefined routes."""
    glPushMatrix()
    glDisable(GL_LIGHTING)
    
    # Slower animation: 500 frame cycle for smooth movement
    time_cycle = (state.city_time % 500.0) / 500.0  # 500 frames per cycle = much smoother
    
    # Vehicle 1: Smooth movement along street 1 (X axis)
    v1_x = -40 + time_cycle * 80  # -40 to +40
    v1_z = 10
    draw_vehicle(v1_x, 0.1, v1_z, width=1.5, length=3.0, color=(1.0, 0.2, 0.2))
    
    # Vehicle 2: Smooth movement along street 2 (Z axis)
    v2_x = -15
    v2_z = -30 + time_cycle * 80  # -30 to +50
    draw_vehicle(v2_x, 0.1, v2_z, width=1.5, length=3.0, color=(0.2, 0.5, 1.0))
    
    # Vehicle 3: Smooth circular patrol route
    v3_angle = time_cycle * 2 * math.pi
    v3_x = 20 * math.cos(v3_angle)
    v3_z = 20 * math.sin(v3_angle)
    draw_vehicle(v3_x, 0.1, v3_z, width=1.5, length=3.0, color=(0.2, 1.0, 0.2))
    
    glEnable(GL_LIGHTING)
    glPopMatrix()