import numpy as np

class Simulation:
    def __init__(self, G=6.674e-11, softening=1e8, trail_length=300):
        self.G = G
        self.softening = softening              # prevents div by zero on close approach
        self.trail_length = trail_length
        self.bodies = []
        self.time = 0.0

    def add_body(self, body):
        self.bodies.append(body)

    def clear(self):
        self.bodies = []
        self.time = 0.0

    def _compute_accelerations(self):
        n = len(self.bodies)
        acc = np.zeros((n, 2))
        positions = np.array([b.pos for b in self.bodies])
        masses = np.array([b.mass for b in self.bodies])

        for i in range(n):
            diff = positions - positions[i]               # (n, 2)
            dist_sq = np.sum(diff**2, axis=1) + self.softening**2
            dist_sq[i] = 1.0                              # avoid self-interaction
            inv_dist3 = dist_sq**(-1.5)
            inv_dist3[i] = 0.0
            acc[i] = self.G * np.sum(masses[:, None] * diff * inv_dist3[:, None], axis=0)

        return acc

    def step(self, dt):
        if len(self.bodies) < 2:
            return

        # Leapfrog (Verlet) integration - more stable than Euler
        acc = self._compute_accelerations()

        for i, body in enumerate(self.bodies):
            body.vel += 0.5 * acc[i] * dt

        for body in self.bodies:
            body.pos += body.vel * dt

        acc = self._compute_accelerations()

        for i, body in enumerate(self.bodies):
            body.vel += 0.5 * acc[i] * dt
            body.trail.append(body.pos.copy())
            if len(body.trail) > self.trail_length:
                body.trail.pop(0)

        self.time += dt

class Body:
    def __init__(self, mass, pos, vel, color="#ffffff", name=""):
        self.mass = float(mass)
        self.pos = np.array(pos, dtype=float)   # [x, y]
        self.vel = np.array(vel, dtype=float)   # [vx, vy]
        self.color = color
        self.name = name
        self.trail = []  