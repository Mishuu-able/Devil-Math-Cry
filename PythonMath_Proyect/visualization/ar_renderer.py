
import cv2
import numpy as np


class ARSurfaceRenderer:

    def __init__(self, escala_z=0.45, resolucion=35):

        self.escala_z = escala_z
        self.resolucion = resolucion

    def render(self, frame, datos):

        X = np.asarray(datos["X"], dtype=float)
        Y = np.asarray(datos["Y"], dtype=float)
        Z = np.asarray(datos["Z"], dtype=float)

        if X.shape != Y.shape or X.shape != Z.shape:
            return frame

        if X.ndim != 2 or min(X.shape) < 2:
            return frame

        height, width = frame.shape[:2]

        # Reducir la cantidad de puntos para mejorar rendimiento
        step = max(
            1,
            int(max(X.shape) / self.resolucion)
        )

        X = X[::step, ::step]
        Y = Y[::step, ::step]
        Z = Z[::step, ::step]

        valid = valid[::step, ::step]

        # Centro geométrico
        valid = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z)

        if not np.any(valid):
            return frame

        cx = (np.nanmin(X) + np.nanmax(X)) / 2
        cy = (np.nanmin(Y) + np.nanmax(Y)) / 2
        cz = (np.nanmin(Z) + np.nanmax(Z)) / 2

        # Normalización de coordenadas
        scale = max(
            np.nanmax(X) - np.nanmin(X),
            np.nanmax(Y) - np.nanmin(Y),
            1e-6
        )

        x = (X - cx) / scale
        y = (Y - cy) / scale
        z = (Z - cz) / scale

        z *= self.escala_z

        # Proyección isométrica sencilla
        angle_y = np.radians(35)
        angle_x = np.radians(25)

        x1 = x * np.cos(angle_y) + z * np.sin(angle_y)
        z1 = -x * np.sin(angle_y) + z * np.cos(angle_y)

        y1 = y * np.cos(angle_x) - z1 * np.sin(angle_x)
        z2 = y * np.sin(angle_x) + z1 * np.cos(angle_x)

        # Escala para adaptar el modelo al video
        visual_scale = min(width, height) * 0.85

        screen_x = (
            width / 2 + x1 * visual_scale
        )

        screen_y = (
            height / 2 - y1 * visual_scale
        )

        points = np.stack(
            (screen_x, screen_y),
            axis=-1
        )

        # Colores según altura
        z_min = np.nanmin(Z)
        z_max = np.nanmax(Z)

        if z_max - z_min < 1e-8:
            normalized_z = np.zeros_like(Z)
        else:
            normalized_z = (Z - z_min) / (z_max - z_min)

        colors = cv2.applyColorMap(
            np.uint8(np.clip(normalized_z * 255, 0, 255)),
            cv2.COLORMAP_PLASMA
        )

        # Dibujar caras desde atrás hacia delante
        faces = []

        rows, cols = X.shape

        for i in range(rows - 1):
            for j in range(cols - 1):

                corners = [
                    (i, j),
                    (i, j + 1),
                    (i + 1, j + 1),
                    (i + 1, j)
                ]

                if not all(valid[r, c] for r, c in corners):
                    continue

                polygon = np.array([
                    points[r, c] for r, c in corners
                ], dtype=np.float32)

                if not np.all(np.isfinite(polygon)):
                    continue

                polygon = np.round(polygon).astype(np.int32)

                depth = np.mean([
                    z2[r, c] for r, c in corners
                ])

                color = np.mean([
                    colors[r, c, :].astype(float)
                    for r, c in corners
                ], axis=0)

                color = tuple(
                    int(v) for v in color
                )

                faces.append(
                    (depth, polygon, color)
                )

        faces.sort(
            key=lambda item: item[0]
        )

        for _, polygon, color in faces:

            cv2.fillConvexPoly(
                frame,
                polygon,
                color,
                lineType=cv2.LINE_AA
            )

            cv2.polylines(
                frame,
                [polygon],
                True,
                (220, 220, 220),
                1,
                cv2.LINE_AA
            )

        # Nombre de la expresión
        cv2.putText(
            frame,
            str(datos.get("expression", "Superficie 3D")),
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        return frame
