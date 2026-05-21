import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class SimCanvas(QWidget):
    def __init__(self, simulation, steps_per_frame=5, dt=3600*24, parent=None):
        super().__init__(parent)
        self.sim = simulation
        self.steps_per_frame = steps_per_frame  # physics steps per render
        self.dt = dt                             # timestep in seconds (default 1 day)
        self.running = False
        self.scale = 1e-9                        # meters to pixels
        self.offset = np.array([0.0, 0.0])      # pan offset in pixels
        self.setMinimumSize(600, 600)
        self.setStyleSheet("background-color: #0a0a1a;")

        self._drag_start = None
        self._offset_start = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.setInterval(16)               # ~60fps

    def start(self):
        self.running = True
        self.timer.start()

    def stop(self):
        self.running = False
        self.timer.stop()

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def _tick(self):
        for _ in range(self.steps_per_frame):
            self.sim.step(self.dt)
        self.update()

    def _world_to_screen(self, pos):
        cx, cy = self.width() / 2, self.height() / 2
        sx = pos[0] * self.scale + cx + self.offset[0]
        sy = -pos[1] * self.scale + cy + self.offset[1]  # flip y axis
        return int(sx), int(sy)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for body in self.sim.bodies:
            color = QColor(body.color)

            # Draw trail
            if len(body.trail) > 1:
                for i in range(1, len(body.trail)):
                    alpha = int(255 * i / len(body.trail))
                    trail_color = QColor(color)
                    trail_color.setAlpha(alpha)
                    pen = QPen(trail_color, 1)
                    painter.setPen(pen)
                    x1, y1 = self._world_to_screen(body.trail[i - 1])
                    x2, y2 = self._world_to_screen(body.trail[i])
                    painter.drawLine(x1, y1, x2, y2)

            # Draw body
            x, y = self._world_to_screen(body.pos)
            radius = max(4, int(np.log10(body.mass) - 20))  # scale size loosely with mass
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

            # Draw label
            painter.setPen(QPen(QColor("#aaaaaa")))
            painter.drawText(x + radius + 3, y + 4, body.name)

        painter.end()

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale *= factor
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.position()
            self._offset_start = self.offset.copy()

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            delta = event.position() - self._drag_start
            self.offset = self._offset_start + np.array([delta.x(), delta.y()])
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None