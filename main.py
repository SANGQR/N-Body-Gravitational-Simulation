from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from nbody_physics import Simulation
from canvas import SimCanvas
from control import ControlPanel
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("N-Body Gravitational Simulator")
        self.setMinimumSize(900, 650)

        sim = Simulation(G=6.674e-11, softening=1e9, trail_length=400)
        canvas = SimCanvas(sim, steps_per_frame=5, dt=3600*24)
        controls = ControlPanel(sim, canvas)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(canvas, stretch=1)
        layout.addWidget(controls)
        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())