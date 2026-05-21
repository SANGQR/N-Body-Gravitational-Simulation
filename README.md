# N-Body Gravitational Simulation

A real-time 2D gravitational N-body simulator built in Python. Bodies attract each other via Newtonian gravity, integrated with a **Leapfrog (Verlet) scheme** for long-term orbital stability. The GUI is built with **PySide6/Qt** and renders at ~60 fps with pan, zoom, and trail history.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-green)
![NumPy](https://img.shields.io/badge/NumPy-vectorized-orange)

---

## Features

- Real-time physics at ~60 fps via a Qt timer loop
- Leapfrog integration — energy-conserving and stable over long timescales
- Softening length to prevent singularities on close approach
- Fading trail history for each body
- Three built-in scenarios:
  - **Solar System** — Sun + 5 planets with NASA orbital velocities
  - **Figure-Eight** — Chenciner–Montgomery (2000) periodic three-body choreography
  - **Binary + Planet** — two equal-mass stars with an orbiting planet
- Adjustable simulation speed (steps per frame)
- Mouse pan (click-drag) and scroll-to-zoom

---

## Requirements

- Python 3.10+
- PySide6
- NumPy

Install dependencies:

```bash
pip install PySide6 numpy
```

---

## Usage

```bash
python main.py
```

| Control | Action |
|---|---|
| Scroll wheel | Zoom in / out |
| Click + drag | Pan the view |
| Play / Pause | Start or freeze the simulation |
| Reset | Restart current scenario from initial conditions |
| Scenario dropdown | Switch between presets |
| Speed slider | Change steps per frame (1–30) |

---

## Project Structure

```
NBodySim/
├── main.py            # Entry point — creates window and wires components
├── nbody_physics.py   # Simulation and Body classes, Leapfrog integrator
├── canvas.py          # Qt widget — rendering, pan, zoom
└── control.py         # Qt widget — control panel, scenario presets
```

---

## Physics

Gravitational acceleration on body *i*:

$$a_i = G \sum_{j \neq i} \frac{m_j (\mathbf{r}_j - \mathbf{r}_i)}{(|\mathbf{r}_j - \mathbf{r}_i|^2 + \epsilon^2)^{3/2}}$$

where $\epsilon$ is the softening length (default `1e9 m`) that prevents the force from diverging as two bodies approach each other.

Integration uses the **Leapfrog (kick-drift-kick) scheme**:

1. Half-kick: $v \mathrel{+}= \tfrac{1}{2} a \, \Delta t$
2. Drift: $r \mathrel{+}= v \, \Delta t$
3. Recompute accelerations
4. Half-kick: $v \mathrel{+}= \tfrac{1}{2} a \, \Delta t$

This is symplectic (time-reversible), keeping total energy nearly constant over thousands of orbits — a significant improvement over simple Euler integration.

---

## License

MIT
