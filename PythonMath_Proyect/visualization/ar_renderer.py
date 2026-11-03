
import cv2
import numpy as np


class ARSurfaceRenderer:

    def __init__(
        self,
        escala_z=0.45,
        resolucion=35,
        escala_visual=0.36,
        posicion_x=0.76,
        posicion_y=0.72
    ):
        self.escala_z = escala_z
        self.resolucion = resolucion

        # Tamaño y posición del modelo en pantalla
        self.escala_visual = escala_visual
        self.posicion_x = posicion_x
        self.posicion_y = posicion_y

    def render(self, frame, datos, rotacion_x=0, rotacion_y=0):

        X = np.asarray(datos["X"], dtype=float)
        Y = np.asarray(datos["Y"], dtype=float)
        Z = np.asarray(datos["Z"], dtype=float)

        if X.shape != Y.shape or X.shape != Z.shape:
            return frame

        if X.ndim != 2 or min(X.shape) < 2:
            return frame

        height, width = frame.shape[:2]

        # Reducir puntos para mejorar rendimiento
        step = max(1, int(max(X.shape) / self.resolucion))

        X = X[::step, ::step]
        Y = Y[::step, ::step]
        Z = Z[::step, ::step]

        valid = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z)

        if not np.any(valid):
            return frame

        # Centro geométrico
        cx = (np.nanmin(X) + np.nanmax(X)) / 2
        cy = (np.nanmin(Y) + np.nanmax(Y)) / 2
        cz = (np.nanmin(Z) + np.nanmax(Z)) / 2

        scale = max(
            np.nanmax(X) - np.nanmin(X),
            np.nanmax(Y) - np.nanmin(Y),
            1e-6
        )

        x = (X - cx) / scale
        y = (Y - cy) / scale
        z = (Z - cz) / scale

        z *= self.escala_z

        # Rotación controlada por la mano
        rx = np.radians(rotacion_x)
        ry = np.radians(rotacion_y)

        # Rotación sobre X
        y1 = y * np.cos(rx) - z * np.sin(rx)
        z1 = y * np.sin(rx) + z * np.cos(rx)

        # Rotación sobre Y
        x2 = x * np.cos(ry) + z1 * np.sin(ry)
        z2 = -x * np.sin(ry) + z1 * np.cos(ry)

        # Perspectiva isométrica base
        angle_y = np.radians(35)
        angle_x = np.radians(25)

        x3 = x2 * np.cos(angle_y) + z2 * np.sin(angle_y)
        z3 = -x2 * np.sin(angle_y) + z2 * np.cos(angle_y)

        y3 = y1 * np.cos(angle_x) - z3 * np.sin(angle_x)
        depth = y1 * np.sin(angle_x) + z3 * np.cos(angle_x)

        # Tamaño y ubicación en la cámara
        visual_scale = min(width, height) * self.escala_visual

        center_x = int(width * self.posicion_x)
        center_y = int(height * self.posicion_y)

        screen_x = center_x + x3 * visual_scale
        screen_y = center_y - y3 * visual_scale

        points = np.stack((screen_x, screen_y), axis=-1)

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

        # Construir caras
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

                polygon_float = np.array(
                    [points[r, c] for r, c in corners],
                    dtype=float
                )

                if not np.all(np.isfinite(polygon_float)):
                    continue

                polygon = np.round(polygon_float).astype(np.int32)

                # Evitar polígonos excesivamente grandes
                if (
                    np.any(polygon[:, 0] < -width) or
                    np.any(polygon[:, 0] > width * 2) or
                    np.any(polygon[:, 1] < -height) or
                    np.any(polygon[:, 1] > height * 2)
                ):
                    continue

                face_depth = np.mean([
                    depth[r, c] for r, c in corners
                ])

                color = np.mean([
                    colors[r, c, :].astype(float)
                    for r, c in corners
                ], axis=0)

                color = tuple(int(v) for v in color)

                faces.append((face_depth, polygon, color))

        # Dibujar primero las caras más alejadas
        faces.sort(key=lambda item: item[0])

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
