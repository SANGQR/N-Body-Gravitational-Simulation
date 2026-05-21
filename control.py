from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QSlider, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from nbody_physics import Simulation, Body
import numpy as np


def _solar_system(sim):
    sim.clear()
    sim.add_body(Body(1.989e30, [0, 0],           [0, 0],         "#FFD700", "Sun"))
    sim.add_body(Body(3.30e23,  [5.79e10, 0],     [0,  47360],    "#aaaaaa", "Mercury"))
    sim.add_body(Body(4.87e24,  [1.08e11, 0],     [0,  35020],    "#e8cda0", "Venus"))
    sim.add_body(Body(5.97e24,  [1.50e11, 0],     [0,  29783],    "#4fa3e0", "Earth"))
    sim.add_body(Body(6.42e23,  [2.28e11, 0],     [0,  24077],    "#c1440e", "Mars"))
    sim.add_body(Body(1.90e27,  [7.78e11, 0],     [0,  13070],    "#c88b3a", "Jupiter"))
    # Velocities derived from Nasa fact sheet:

def _figure_eight(sim):
    sim.clear()
    # Choreography figure-8 solution (Chenciner & Montgomery 2000) — scaled to AU
    AU = 1.5e11
    v0 = 1e4
    r = 0.97000436 * AU
    vx = 0.93240737 * v0
    vy = 0.86473146 * v0
    m = 1e30
    sim.add_body(Body(m, [ r,        0.24308753 * AU], [ vx / 2,  vy / 2], "#ff6666", "A"))
    sim.add_body(Body(m, [-r,       -0.24308753 * AU], [ vx / 2,  vy / 2], "#66ff66", "B"))
    sim.add_body(Body(m, [0,         0],               [-vx,      -vy],     "#6688ff", "C"))


def _binary_star(sim):
    sim.clear()
    sep = 2e11
    m = 1.5e30
    v = np.sqrt(6.674e-11 * m / (2 * sep)) * 0.9
    sim.add_body(Body(m, [-sep / 2, 0], [0, -v], "#ffaa44", "Star A"))
    sim.add_body(Body(m, [ sep / 2, 0], [0,  v], "#44aaff", "Star B"))
    sim.add_body(Body(5e24, [sep, 0],   [0,  v * 1.8], "#88ff88", "Planet"))


SCENARIOS = {
    "Solar System": _solar_system,
    "Figure-Eight": _figure_eight,
    "Binary + Planet": _binary_star,
}


class ControlPanel(QWidget):
    def __init__(self, sim: Simulation, canvas, parent=None):
        super().__init__(parent)
        self.sim = sim
        self.canvas = canvas
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #111122; color: #dddddd;")

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignTop)
        root.setSpacing(12)
        root.setContentsMargins(12, 12, 12, 12)

        # --- Playback ---
        pb_group = QGroupBox("Playback")
        pb_group.setStyleSheet("QGroupBox { color: #aaaaaa; border: 1px solid #333355; margin-top: 6px; }"
                               "QGroupBox::title { subcontrol-origin: margin; left: 8px; }")
        pb_layout = QHBoxLayout(pb_group)

        self.play_btn = QPushButton("Play")
        self.play_btn.setCheckable(True)
        self.play_btn.clicked.connect(self._toggle_play)
        pb_layout.addWidget(self.play_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset)
        pb_layout.addWidget(reset_btn)

        root.addWidget(pb_group)

        # --- Scenario ---
        sc_group = QGroupBox("Scenario")
        sc_group.setStyleSheet(pb_group.styleSheet())
        sc_layout = QVBoxLayout(sc_group)

        self.scenario_box = QComboBox()
        self.scenario_box.addItems(list(SCENARIOS.keys()))
        self.scenario_box.currentTextChanged.connect(self._load_scenario)
        sc_layout.addWidget(self.scenario_box)

        root.addWidget(sc_group)

        # --- Speed ---
        sp_group = QGroupBox("Speed")
        sp_group.setStyleSheet(pb_group.styleSheet())
        sp_layout = QVBoxLayout(sp_group)

        self.speed_label = QLabel(f"Steps/frame: {canvas.steps_per_frame}")
        sp_layout.addWidget(self.speed_label)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 30)
        self.speed_slider.setValue(canvas.steps_per_frame)
        self.speed_slider.valueChanged.connect(self._set_speed)
        sp_layout.addWidget(self.speed_slider)

        root.addWidget(sp_group)

        # --- Info ---
        self.time_label = QLabel("Time: 0.00 days")
        self.time_label.setStyleSheet("color: #888888; font-size: 11px;")
        root.addWidget(self.time_label)

        self.body_label = QLabel("Bodies: 0")
        self.body_label.setStyleSheet("color: #888888; font-size: 11px;")
        root.addWidget(self.body_label)

        # Refresh info labels at ~10 Hz
        self._info_timer = QTimer(self)
        self._info_timer.timeout.connect(self._update_info)
        self._info_timer.start(100)

        # Load default scenario
        self._load_scenario(self.scenario_box.currentText())

    def _toggle_play(self, checked: bool):
        self.play_btn.setText("Pause" if checked else "Play")
        self.canvas.toggle()

    def _reset(self):
        was_running = self.canvas.running
        self.canvas.stop()
        self.play_btn.setChecked(False)
        self.play_btn.setText("Play")
        self._load_scenario(self.scenario_box.currentText())
        if was_running:
            self.canvas.start()
            self.play_btn.setChecked(True)
            self.play_btn.setText("Pause")

    def _load_scenario(self, name: str):
        SCENARIOS[name](self.sim)
        self.sim.time = 0.0

    def _set_speed(self, value: int):
        self.canvas.steps_per_frame = value
        self.speed_label.setText(f"Steps/frame: {value}")

    def _update_info(self):
        days = self.sim.time / (3600 * 24)
        if days >= 365:
            self.time_label.setText(f"Time: {days / 365:.2f} yr")
        else:
            self.time_label.setText(f"Time: {days:.1f} days")
        self.body_label.setText(f"Bodies: {len(self.sim.bodies)}")
        self.canvas.update()
