
import pyvista as pv
import numpy as np
import time
import cv2

from tracking.hand_tracker import HandTracker
from tracking.camera_controller import CameraController


class Graph3D:

    def __init__(self, usar_gestos=False, modo_debug=False):

        self.usar_gestos = usar_gestos
        self.modo_debug = modo_debug

        # ======================================
        # CONTROLADOR DE CÁMARA
        # ======================================

        self.ultimo_tiempo = time.monotonic()
        self.mano_detectada = False

        self.camera_controller = None
        self.hand_tracker = None

        if self.usar_gestos or self.modo_debug:

            self.camera_controller = CameraController(
                dead_zone=0.06,
                max_offset=0.30,
                max_speed=120.0,
                smoothing=0.12
            )

        if self.usar_gestos and not self.modo_debug:

            self.hand_tracker = HandTracker(
                model_path="hand_landmarker.task",
                camera_index=0,
                show_preview=True
            )

        # Posición simulada de la palma
        self.debug_x = 0.5
        self.debug_y = 0.5

        self.debug_speed = 0.65

        self.plotter = pv.Plotter(
            window_size=(1200, 850)
        )

        # ======================================
        # CONFIGURACIÓN
        # ======================================

        self.escala_z = 0.25

        self.velocidad_rotacion = 1.5
        self.velocidad_zoom = 1.015

        self.teclas_activas = set()

        self.centro = np.array([0.0, 0.0, 0.0])
        self.distancia = 30

        self.bounds = None

        self.configurar_escena()
        self.configurar_controles()

    # Conserva aquí tu diccionario self.vistas original.
        self.vistas = {

            "x+": {
                "position": (30.0, -0.27010936166595556, 5.374197515613086),
                "focal_point":  (0.0, -0.27010936166595556, 5.374197515613086),
                "zoom": 7.781227380300003,
                "up": (0, 0, 1)
            },

            "x-": {
                "position": (-30.0, -0.27010936166595556, 5.374197515613086),
                "focal_point":  (0.0, -0.27010936166595556, 5.374197515613086),
                "zoom": 7.781227380300003,
                "up": (0, 0, 1)
            },

            "y+": {
                "position": (0.0, 30.0, 5.988653732379733),
                "focal_point": (0.0, 0.0, 5.988653732379733),
                "up": (0.0, 0.0, 1.0),
                "zoom": 7.781227380300003
            },

            "y-": {
                "position": (0.0, -30.0, 5.988653732379733),
                "focal_point": (0.0, 0.0, 5.988653732379733),
                "zoom": 7.781227380300003,
                "up": (0.0, 0.0, 1.0)
            },

            "z+": {
                "position": (0, 0, 30),
                "focal_point": (0, 0, 0),
                "zoom": 3.0,
                "up": (0, 1, 0)
            },

            "z-": {
                "position": (0, 0, -30),
                "focal_point": (0, 0, 0),
                "zoom": 3.0,
                "up": (0, 1, 0)
            }

        }

    # ==========================================
    # ESCENA
    # ==========================================
    def mostrar_posicion_camara(self):

        camara = self.plotter.camera

        print("\n========== CÁMARA ==========")

        print("position:", camara.position)
        print("focal_point:", camara.focal_point)
        print("up:", camara.up)
        print("zoom:", camara.parallel_scale)

        print("============================\n")

    def configurar_escena(self):

        self.plotter.set_background("#0B1120")

        self.plotter.add_axes(
            line_width=3,
            color="white"
        )

        self.plotter.show_grid(
            color="#64748B",
            xtitle="X",
            ytitle="Y",
            ztitle="Z"
        )

    # ==========================================
    # CONTROLES
    # ==========================================

    def configurar_controles(self):

        # Vistas ortogonales

        self.plotter.add_key_event(
            "1", lambda: self.vista_eje("x", 1)
        )

        self.plotter.add_key_event(
            "2", lambda: self.vista_eje("x", -1)
        )

        self.plotter.add_key_event(
            "3", lambda: self.vista_eje("y", 1)
        )

        self.plotter.add_key_event(
            "4", lambda: self.vista_eje("y", -1)
        )

        self.plotter.add_key_event(
            "5", lambda: self.vista_eje("z", 1)
        )

        self.plotter.add_key_event(
            "6", lambda: self.vista_eje("z", -1)
        )

        self.plotter.add_key_event(
            "0", self.vista_isometrica
        )

        self.plotter.add_key_event(
            "r", self.restablecer_camara
        )

        self.plotter.add_key_event(
            "p",
            self.mostrar_posicion_camara
        )

        # Eventos de movimiento continuo

        interactor = self.plotter.iren

        interactor.add_observer(
            "KeyPressEvent",
            self.tecla_presionada
        )

        interactor.add_observer(
            "KeyReleaseEvent",
            self.tecla_liberada
        )

    # ==========================================
    # MOVIMIENTO CONTINUO
    # ==========================================

    def tecla_presionada(self, obj, event):

        tecla = obj.GetKeySym().lower()

        print(f"[DEBUG] TECLA: {tecla}")

        # ======================================
        # SIMULADOR DE PALMA
        # ======================================

        if self.modo_debug:

            movimientos = {
                "left": (-8, 0),
                "right": (8, 0),
                "up": (0, 8),
                "down": (0, -8)
            }

            if tecla in movimientos:

                horizontal, vertical = movimientos[tecla]

                self.aplicar_rotacion(
                    horizontal,
                    vertical
                )

                return

        # ======================================
        # ROTACIÓN TRADICIONAL
        # ======================================

        movimientos = {
            "a": (-5, 0),
            "d": (5, 0),
            "w": (0, 5),
            "s": (0, -5)
        }

        if tecla in movimientos:

            horizontal, vertical = movimientos[tecla]

            self.aplicar_rotacion(
                horizontal,
                vertical
            )

            return

        # ======================================
        # ZOOM
        # ======================================

        if tecla == "i":

            self.plotter.camera.Zoom(
                self.velocidad_zoom
            )

            self.plotter.render()

        elif tecla == "k":

            self.plotter.camera.Zoom(
                1 / self.velocidad_zoom
            )

            self.plotter.render()


    def tecla_liberada(self, obj, event):

        tecla = obj.GetKeySym().lower()

        print(f"[DEBUG] TECLA LIBERADA: {tecla}")

        self.teclas_activas.discard(tecla)

    def aplicar_rotacion(self, horizontal, vertical):

        camara = self.plotter.camera

        camara.Azimuth(horizontal)
        camara.Elevation(vertical)

        camara.OrthogonalizeViewUp()

        self.plotter.render()

    
    def actualizar_camara(self, step):

        if step % 60 == 0:
            print(f"[DEBUG] TIMER ACTIVO - STEP: {step}")

        ahora = time.monotonic()

        dt = ahora - self.ultimo_tiempo
        self.ultimo_tiempo = ahora

        dt = max(0.0, min(dt, 0.05))

        camara = self.plotter.camera

        horizontal = 0.0
        vertical = 0.0

        # ======================================
        # CONTROL CON TECLADO WASD
        # ======================================

        if "a" in self.teclas_activas:
            horizontal -= self.velocidad_rotacion

        if "d" in self.teclas_activas:
            horizontal += self.velocidad_rotacion

        if "w" in self.teclas_activas:
            vertical += self.velocidad_rotacion

        if "s" in self.teclas_activas:
            vertical -= self.velocidad_rotacion

        # ======================================
        # SIMULADOR DE HAND TRACKING
        # ======================================

        if self.modo_debug:

            if "left" in self.teclas_activas:
                self.debug_x -= self.debug_speed * dt

            if "right" in self.teclas_activas:
                self.debug_x += self.debug_speed * dt

            if "up" in self.teclas_activas:
                self.debug_y -= self.debug_speed * dt

            if "down" in self.teclas_activas:
                self.debug_y += self.debug_speed * dt

            self.debug_x = np.clip(self.debug_x, 0.0, 1.0)
            self.debug_y = np.clip(self.debug_y, 0.0, 1.0)

            yaw, pitch = self.camera_controller.update(
                self.debug_x,
                self.debug_y,
                dt
            )

            horizontal += yaw * dt
            vertical += pitch * dt

        # ======================================
        # CONTROL REAL CON MEDIAPIPE
        # ======================================

        elif self.usar_gestos:

            data = self.hand_tracker.get_data()

            if data["detected"]:

                yaw, pitch = self.camera_controller.update(
                    data["x"],
                    data["y"],
                    dt
                )

                self.mano_detectada = True

                horizontal += yaw * dt
                vertical += pitch * dt

            else:

                if self.mano_detectada:

                    self.camera_controller.reset()
                    self.mano_detectada = False

        # ======================================
        # APLICAR ROTACIÓN
        # ======================================

        if horizontal != 0 or vertical != 0:

            camara.Azimuth(horizontal)
            camara.Elevation(vertical)

            camara.OrthogonalizeViewUp()

            self.plotter.render()

        # ======================================
        # ZOOM POR TECLADO
        # ======================================

        if "i" in self.teclas_activas:

            camara.Zoom(self.velocidad_zoom)
            self.plotter.render()

        if "k" in self.teclas_activas:

            camara.Zoom(1 / self.velocidad_zoom)
            self.plotter.render()


    # ==========================================
    # VISTAS ORTOGONALES
    # ==========================================

    def vista_eje(self, eje, direccion=1):

        camara = self.plotter.camera

        nombre = eje + ("+" if direccion > 0 else "-")

        config = self.vistas[nombre]

        camara.parallel_projection = True

        camara.position = config["position"]
        camara.focal_point = config["focal_point"]
        camara.up = config["up"]

        camara.parallel_scale = config["zoom"]

        camara.SetWindowCenter(0.0, 0.0)

        self.plotter.renderer.reset_camera_clipping_range()
        self.plotter.render()

    # ==========================================
    # VISTA ISOMÉTRICA
    # ==========================================

    def vista_isometrica(self):

        camara = self.plotter.camera

        camara.parallel_projection = False

        self.plotter.view_isometric()

        camara.focal_point = self.centro

        # Restablecer el encuadre
        self.plotter.reset_camera(
            bounds=self.bounds
        )

        camara.focal_point = self.centro

        # Zoom inicial
        camara.Zoom(1.5)

        self.plotter.renderer.reset_camera_clipping_range()

        self.plotter.render()

    # ==========================================
    # RESTABLECER
    # ==========================================

    def restablecer_camara(self):

        self.teclas_activas.clear()

        self.vista_isometrica()

    # ==========================================
    # MOSTRAR SUPERFICIE
    # ==========================================

    def mostrar_superficie(self, datos):

        self.plotter.clear()

        self.configurar_escena()

        X = np.asarray(datos["X"])
        Y = np.asarray(datos["Y"])
        Z = np.asarray(datos["Z"])

        # Crear superficie
        superficie = pv.StructuredGrid(
            X,
            Y,
            Z
        )

        superficie.point_data["Z"] = Z.ravel(
            order="F"
        )

        # Escala visual
        self.plotter.set_scale(
            xscale=1,
            yscale=1,
            zscale=self.escala_z
        )

        # Agregar superficie
        self.plotter.add_mesh(
            superficie,
            scalars="Z",
            cmap="plasma",
            show_edges=False,
            smooth_shading=True,
            lighting=True,
            show_scalar_bar=False
        )

        # Texto de expresión
        self.plotter.add_text(
            datos["expression"],
            position="upper_left",
            font_size=16,
            color="white"
        )

        # Ayuda de controles
        ayuda = (
            "WASD: Rotacion continua\n"
            "I / K: Zoom\n"
            "1-6: Vistas ortogonales\n"
            "0: Isometrica\n"
            "R: Restablecer\n"
        )

        if self.modo_debug:
            ayuda += (
                "\nDEBUG - SIMULADOR DE MANO\n"
                "Flechas: Mover palma virtual\n"
                "Centro: Posicion neutral"
            )
        else:
            ayuda += "Mouse: Navegacion"

        self.plotter.add_text(
            ayuda,
            position="lower_left",
            font_size=10,
            color="white"
        )
        # ======================================
        # CENTRO GEOMÉTRICO
        # ======================================

        xmin = np.nanmin(X)
        xmax = np.nanmax(X)

        ymin = np.nanmin(Y)
        ymax = np.nanmax(Y)

        zmin = np.nanmin(Z)
        zmax = np.nanmax(Z)

        self.centro = np.array([
            (xmin + xmax) / 2,
            (ymin + ymax) / 2,
            (zmin + zmax) / 2
        ])

        # ======================================
        # DIMENSIONES VISUALES
        # ======================================

        self.bounds = (
            xmin,
            xmax,
            ymin,
            ymax,
            zmin,
            zmax
        )

        self.distancia = max(
            xmax - xmin,
            ymax - ymin,
            (zmax - zmin) * self.escala_z,
            1
        )

        # ======================================
        # ENCUADRE INICIAL
        # ======================================

        self.plotter.reset_camera(
            bounds=self.bounds
        )

        self.vista_isometrica()

        # ======================================
        # INICIAR TRACKER
        # ======================================

        if self.usar_gestos:
            self.hand_tracker.start()

        try:
            self.plotter.show()

        finally:

            if self.usar_gestos:
                self.hand_tracker.stop()

def detectar_camara():
    cap = cv2.VideoCapture(0)
    disponible = cap.isOpened()

    if disponible:
        disponible = cap.read()[0]

    cap.release()
    return disponible