
import customtkinter as ctk
import cv2
import time

from PIL import Image

from tracking.hand_tracker import HandTracker
from visualization.ar_renderer import ARSurfaceRenderer


class CameraView:

    def __init__(self, parent, datos):

        self.parent = parent
        self.datos = datos

        self.running = False
        self.after_id = None

        # Rotación actual y objetivo
        self.rotacion_x = 0.0
        self.rotacion_y = 0.0

        self.objetivo_x = 0.0
        self.objetivo_y = 0.0

        # Suavizado: cuanto menor, más suave
        self.suavizado = 0.15

        self.tracker = HandTracker(
            model_path="hand_landmarker.task",
            camera_index=0,
            show_preview=False
        )

        self.renderer = ARSurfaceRenderer(
            escala_z=0.45,
            resolucion=35,
            escala_visual=0.36,
            posicion_x=0.76,
            posicion_y=0.72
        )

        self.crear_interfaz()

    # ======================================
    # INTERFAZ
    # ======================================

    def crear_interfaz(self):

        self.contenedor = ctk.CTkFrame(
            self.parent,
            fg_color="#0B1120",
            corner_radius=0
        )

        self.contenedor.pack(fill="both", expand=True)

        encabezado = ctk.CTkFrame(
            self.contenedor,
            fg_color="transparent"
        )

        encabezado.pack(
            fill="x",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            encabezado,
            text="REALIDAD AUMENTADA",
            font=("Poppins", 22, "bold"),
            text_color="white"
        ).pack(side="left")

        self.estado = ctk.CTkLabel(
            encabezado,
            text="Iniciando cámara...",
            font=("Poppins", 12),
            text_color="#F59E0B"
        )

        self.estado.pack(side="right")

        self.video_label = ctk.CTkLabel(
            self.contenedor,
            text="",
            fg_color="#111827"
        )

        self.video_label.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            self.contenedor,
            text="Mueve tu mano horizontal y verticalmente para rotar la superficie.",
            font=("Poppins", 12),
            text_color="#94A3B8"
        ).pack(pady=(0, 15))

        self.parent.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar
        )

    # ======================================
    # INICIAR
    # ======================================

    def iniciar(self):

        if self.running:
            return

        self.running = True

        self.tracker.start()

        self.actualizar_video()

    # ======================================
    # CONTROL DE ROTACIÓN
    # ======================================

    def actualizar_rotacion(self, data):

        if data["detected"]:

            # Coordenadas normalizadas de la palma
            x = float(data["x"])
            y = float(data["y"])

            # Limitar valores
            x = max(0.0, min(1.0, x))
            y = max(0.0, min(1.0, y))

            # Convertir posición de la mano en ángulos
            self.objetivo_y = (x - 0.5) * 120
            self.objetivo_x = (0.5 - y) * 90

        # Interpolación para evitar movimientos bruscos
        self.rotacion_x += (
            self.objetivo_x - self.rotacion_x
        ) * self.suavizado

        self.rotacion_y += (
            self.objetivo_y - self.rotacion_y
        ) * self.suavizado

    # ======================================
    # ACTUALIZAR VIDEO
    # ======================================

    def actualizar_video(self):

        if not self.running:
            return

        data = self.tracker.get_data()
        frame = data["frame"]

        if frame is not None:

            if data["detected"]:

                self.estado.configure(
                    text="MANO DETECTADA",
                    text_color="#22C55E"
                )

            else:

                self.estado.configure(
                    text="BUSCANDO MANO...",
                    text_color="#F59E0B"
                )

            # Actualizar rotación según la palma
            self.actualizar_rotacion(data)

            # Renderizar superficie
            frame = self.renderer.render(
                frame.copy(),
                self.datos,
                rotacion_x=self.rotacion_x,
                rotacion_y=self.rotacion_y
            )

            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            imagen = Image.fromarray(frame_rgb)

            ancho = max(1, self.video_label.winfo_width())
            alto = max(1, self.video_label.winfo_height())

            imagen.thumbnail((ancho, alto))

            imagen_ctk = ctk.CTkImage(
                light_image=imagen,
                dark_image=imagen,
                size=imagen.size
            )

            self.video_label.configure(image=imagen_ctk)
            self.video_label.image = imagen_ctk

        else:

            self.estado.configure(
                text="ESPERANDO CÁMARA...",
                text_color="#F59E0B"
            )

        self.after_id = self.parent.after(
            15,
            self.actualizar_video
        )

    # ======================================
    # CERRAR
    # ======================================

    def cerrar(self):

        self.running = False

        if self.after_id is not None:

            try:
                self.parent.after_cancel(self.after_id)
            except Exception:
                pass

            self.after_id = None

        self.tracker.stop()
        self.parent.destroy()
