
import cv2
import mediapipe as mp
import threading
import time

from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker:

    def __init__(
        self,
        model_path="hand_landmarker.task",
        camera_index=0,
        show_preview=False
    ):

        self.model_path = str(Path(model_path).resolve())
        self.camera_index = camera_index
        self.show_preview = show_preview

        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        self.hand_data = {
            "detected": False,
            "x": 0.5,
            "y": 0.5,
            "timestamp": 0.0,
            "frame": None
        }

    # ======================================
    # INICIAR TRACKER
    # ======================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._tracking_loop,
            daemon=True
        )

        self.thread.start()

    # ======================================
    # DETENER TRACKER
    # ======================================

    def stop(self):

        self.running = False

        if (
            self.thread is not None
            and threading.current_thread() is not self.thread
        ):
            self.thread.join(timeout=2)

        self.thread = None

    # ======================================
    # OBTENER DATOS
    # ======================================

    def get_data(self):

        with self.lock:
            return self.hand_data.copy()

    # ======================================
    # ACTUALIZAR DATOS
    # ======================================

    def _set_data(
        self,
        detected,
        x=0.5,
        y=0.5,
        frame=None
    ):

        with self.lock:

            self.hand_data = {
                "detected": detected,
                "x": x,
                "y": y,
                "timestamp": time.monotonic(),
                "frame": frame
            }

    # ======================================
    # LOOP PRINCIPAL
    # ======================================

    def _tracking_loop(self):

        cap = None

        try:

            # Configuración de MediaPipe
            options = vision.HandLandmarkerOptions(
                base_options=python.BaseOptions(
                    model_asset_path=self.model_path
                ),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )

            # Abrir cámara
            cap = cv2.VideoCapture(self.camera_index)

            if not cap.isOpened():

                print("ERROR: No se pudo abrir la cámara.")
                return

            print("CÁMARA ABIERTA CORRECTAMENTE")

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            with vision.HandLandmarker.create_from_options(
                options
            ) as detector:

                start_time = time.monotonic()
                last_timestamp = -1

                while self.running:

                    # Obtener fotograma
                    ret, frame = cap.read()

                    if not ret:

                        print(
                            "ERROR: No se pudo obtener el fotograma."
                        )

                        time.sleep(0.01)
                        continue

                    # Espejar cámara
                    frame = cv2.flip(frame, 1)

                    height, width = frame.shape[:2]

                    # Convertir a RGB
                    rgb = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB
                    )

                    image = mp.Image(
                        image_format=mp.ImageFormat.SRGB,
                        data=rgb
                    )

                    # Timestamp creciente para MediaPipe
                    timestamp_ms = int(
                        (time.monotonic() - start_time) * 1000
                    )

                    timestamp_ms = max(
                        timestamp_ms,
                        last_timestamp + 1
                    )

                    last_timestamp = timestamp_ms

                    # Detectar manos
                    result = detector.detect_for_video(
                        image,
                        timestamp_ms
                    )

                    if result.hand_landmarks:

                        hand = result.hand_landmarks[0]

                        # Puntos de referencia de la palma
                        indices = [0, 5, 9, 13, 17]

                        center_x = sum(
                            hand[i].x for i in indices
                        ) / len(indices)

                        center_y = sum(
                            hand[i].y for i in indices
                        ) / len(indices)

                        # Conexiones del esqueleto
                        connections = (
                            vision.HandLandmarksConnections.HAND_CONNECTIONS
                        )

                        for connection in connections:

                            start_point = hand[connection.start]
                            end_point = hand[connection.end]

                            p1 = (
                                int(start_point.x * width),
                                int(start_point.y * height)
                            )

                            p2 = (
                                int(end_point.x * width),
                                int(end_point.y * height)
                            )

                            cv2.line(
                                frame,
                                p1,
                                p2,
                                (0, 255, 0),
                                2,
                                cv2.LINE_AA
                            )

                        # Centro de la palma
                        cx = int(center_x * width)
                        cy = int(center_y * height)

                        cv2.circle(
                            frame,
                            (cx, cy),
                            10,
                            (255, 0, 255),
                            -1,
                            cv2.LINE_AA
                        )

                        # Actualizar coordenadas normalizadas
                        self._set_data(
                            detected=True,
                            x=center_x,
                            y=center_y,
                            frame=frame
                        )

                    else:

                        self._set_data(
                            detected=False,
                            frame=frame
                        )

                    # Vista de depuración opcional
                    if self.show_preview:

                        cv2.imshow(
                            "Devil Math Cry - Hand Tracking",
                            frame
                        )

                        if cv2.waitKey(1) & 0xFF == 27:

                            self.running = False
                            break

        except Exception as error:

            print("ERROR EN HAND TRACKER:", error)

        finally:

            self.running = False

            self._set_data(
                detected=False,
                frame=None
            )

            if cap is not None:
                cap.release()

            if self.show_preview:
                cv2.destroyAllWindows()

            print("HAND TRACKER DETENIDO")
