# Mini Solar System & Earth City Simulation

An interactive 3-D simulation built with **Python**, **PyOpenGL**, **GLFW**, and **GLU**.
It features all 9 planets orbiting the sun with real axial tilts, elliptical orbits, and
rotation speeds, plus an Earth city model you can fly into and explore.

---

## Requirements

```
pip install PyOpenGL PyOpenGL_accelerate glfw pywavefront
```

---

## How to Run

```
python main.py
```

A help screen appears automatically on launch. Press **H** to close it and start.

---

## Features

| Feature | Description |
|---|---|
| 9 planets | Mercury → Pluto, scaled proportionally |
| Axial tilts | Real values (Earth 23.5°, Uranus 98°, etc.) |
| Elliptical orbits | Real eccentricities for each planet |
| Rotation speeds | Proportional to real sidereal days; retrograde for Venus, Uranus, Pluto |
| Orbit trails | Fading coloured trail behind each planet |
| Moons | Earth's moon, Jupiter's Io & Europa |
| Saturn's rings | Rendered with `gluDisk` |
| Comets | Two comets with tails crossing the system |
| Planet picking | Click any planet to zoom to it and read real stats |
| Day/Night mode | Shift light source for dramatic night-side shading |
| Simulation modes | Standard / Cinematic / Educational / God |
| Speed control | Scale all speeds from ×0.05 to ×20 |
| **Earth city view** | **Animated 3-D city model with interactive features:** |
| **Day/night toggle** | **Press D to switch between daytime and nighttime (street lights appear)** |
| **Moving vehicles** | **3 animated vehicles patrol city streets smoothly** |
| **Drone camera** | **Press X for free-look drone mode to explore the city freely** |
| **Street lighting** | **Realistic glowing street lamps visible only at night** |

---

## Controls

### Solar System View

| Key / Input | Action |
|---|---|
| `← →` arrow keys | Rotate camera left / right |
| `↑ ↓` arrow keys | Zoom in / out |
| `Left click` planet | Select → zoom in + info panel |
| `Left click` again | Deselect |
| `ESC` | Deselect and zoom back out |
| `SPACE` | Pause / resume animation |
| `N` | Toggle night-mode lighting |
| `E` | Fly into Earth city view |
| `=` / `+` | Speed up ×1.2 per press (max ×20) |
| `-` | Slow down ×0.8 per press (min ×0.05) |
| `H` | Toggle this help screen |

### Simulation Modes

| Key | Mode | Effect |
|---|---|---|
| `S` | Standard | Normal manual control |
| `C` | Cinematic | Camera slowly auto-orbits |
| `I` | Educational | Info panel always on (shows Earth by default) |
| `G` | God | Camera spins fast |

### City View  *(after pressing E)*

| Key / Input | Action |
|---|---|
| `← →` arrow keys | Rotate camera around the city |
| `↑ ↓` arrow keys | Zoom in-out / adjust height |
| `Mouse drag` (hold LMB) | Free camera rotation |
| `D` | Toggle day/night mode (reveals street lights at night) |
| `X` | Toggle drone free-look camera (fully free rotation) |
| `R` | Reset camera to default position |
| `E` | Return to solar system |

---

## File Structure

```
GraphicsProject/
├── main.py          ← Entry point — GLFW window + main render loop
├── state.py         ← All shared globals (camera, mode, selection, etc.)
├── planet_data.py   ← Planet geometry, speeds, tilts, trails, PLANET_INFO
├── utils.py         ← ease_in_out_cubic easing function
├── lighting.py      ← setup_lighting(), set_planet_material()
├── draw_planets.py  ← Sun, orbit guides, planet spheres, trails, selection ring
├── draw_city.py     ← OBJ/MTL city loading and rendering
├── hud.py           ← All 2-D overlays: city UI, planet info, help screen
├── input.py         ← Keyboard and mouse callbacks
├── final- Copy.obj  ← 3-D city model (Wavefront OBJ)
└── final- Copy.mtl  ← City material colours
```

---

## Things to Try

- Press **I** (Educational mode) then click each planet to compare their stats
- Press **N** to switch to night mode — watch the dark sides of planets
- Press **=** several times then **C** to watch a fast cinematic orbit
- Press **E** to enter the city view, then:
  - Press **D** to toggle between day and night modes
  - Watch the street lights automatically appear when night falls
  - Press **X** to switch to drone camera mode for free exploration
  - Use mouse drag or arrow keys to move the drone camera around
  - Press **R** to reset to the default city view
- Slow time down with **-** and watch Uranus's extreme 98° axial tilt clearly
- Watch the moving vehicles smoothly patrol the streets on different routes
