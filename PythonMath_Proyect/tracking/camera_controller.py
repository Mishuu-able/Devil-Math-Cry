
import math


class CameraController:

    def __init__(
        self,
        dead_zone=0.06,
        max_offset=0.30,
        max_speed=120.0,
        smoothing=0.12
    ):

        # Configuración del joystick
        self.dead_zone = dead_zone
        self.max_offset = max_offset
        self.max_speed = max_speed
        self.smoothing = smoothing

        # Posición neutral de la mano
        self.center_x = None
        self.center_y = None

        # Movimiento suavizado
        self.input_x = 0.0
        self.input_y = 0.0

    # ======================================
    # CALIBRACIÓN
    # ======================================

    def calibrate(self, x, y):

        self.center_x = x
        self.center_y = y

        self.input_x = 0.0
        self.input_y = 0.0

    def reset(self):

        self.center_x = None
        self.center_y = None

        self.input_x = 0.0
        self.input_y = 0.0

    # ======================================
    # NORMALIZACIÓN DEL JOYSTICK
    # ======================================

    def normalize_input(self, value):

        magnitude = abs(value)

        if magnitude <= self.dead_zone:
            return 0.0

        magnitude = min(
            (magnitude - self.dead_zone)
            / (self.max_offset - self.dead_zone),
            1.0
        )

        return math.copysign(magnitude, value)

    # ======================================
    # ACTUALIZACIÓN
    # ======================================

    def update(self, x, y, dt):

        if self.center_x is None:
            self.calibrate(x, y)
            return 0.0, 0.0

        dt = max(0.0, min(dt, 0.05))

        # Desplazamiento respecto al centro
        offset_x = x - self.center_x

        # Invertir Y porque en imagen crece hacia abajo
        offset_y = self.center_y - y

        # Normalizar
        target_x = self.normalize_input(offset_x)
        target_y = self.normalize_input(offset_y)

        # Suavizado independiente del framerate
        alpha = 1.0 - math.exp(
            -dt / self.smoothing
        )

        self.input_x += (
            target_x - self.input_x
        ) * alpha

        self.input_y += (
            target_y - self.input_y
        ) * alpha

        # Convertir a grados por segundo
        yaw = self.input_x * self.max_speed
        pitch = self.input_y * self.max_speed

        return yaw, pitch
