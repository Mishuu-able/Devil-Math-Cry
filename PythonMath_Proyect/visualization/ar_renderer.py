import cv2
import numpy as np


class ARSurfaceRenderer:
    """
    Renderizador ligero de superficies 3D sobre un fotograma de cámara.

    La geometría y los colores se preparan una sola vez por cada conjunto
    de datos. En cada fotograma únicamente se recalculan la rotación,
    la proyección y el orden de profundidad.
    """

    def __init__(
        self,
        escala_z=0.45,
        resolucion=35,
        escala_visual=0.36,
        posicion_x=0.76,
        posicion_y=0.72,
        mostrar_bordes=False
    ):
        self.escala_z = escala_z
        self.resolucion = max(2, int(resolucion))

        self.escala_visual = escala_visual
        self.posicion_x = posicion_x
        self.posicion_y = posicion_y
        self.mostrar_bordes = mostrar_bordes

        # Caché: evita volver a muestrear y colorear la misma superficie
        # en cada actualización de la cámara.
        self._datos_cache = None
        self._geometria = None

    def _preparar_superficie(self, datos):
        """Muestrea la superficie y prepara sus caras y colores."""
        X_original = np.asarray(datos["X"], dtype=np.float32)
        Y_original = np.asarray(datos["Y"], dtype=np.float32)
        Z_original = np.asarray(datos["Z"], dtype=np.float32)

        if (
            X_original.shape != Y_original.shape
            or X_original.shape != Z_original.shape
            or X_original.ndim != 2
            or min(X_original.shape) < 2
        ):
            return None

        filas, columnas = X_original.shape

        # Seleccionar como máximo 'resolucion' muestras por dimensión.
        indices_fila = np.linspace(
            0, filas - 1, min(filas, self.resolucion)
        ).round().astype(np.int32)

        indices_columna = np.linspace(
            0, columnas - 1, min(columnas, self.resolucion)
        ).round().astype(np.int32)

        X = X_original[np.ix_(indices_fila, indices_columna)]
        Y = Y_original[np.ix_(indices_fila, indices_columna)]
        Z = Z_original[np.ix_(indices_fila, indices_columna)]

        validos = np.isfinite(X) & np.isfinite(Y) & np.isfinite(Z)

        if not np.any(validos):
            return None

        # Centro y escala calculados una sola vez.
        cx = (float(np.nanmin(X)) + float(np.nanmax(X))) / 2
        cy = (float(np.nanmin(Y)) + float(np.nanmax(Y))) / 2
        cz = (float(np.nanmin(Z)) + float(np.nanmax(Z))) / 2

        escala = max(
            float(np.nanmax(X) - np.nanmin(X)),
            float(np.nanmax(Y) - np.nanmin(Y)),
            1e-6
        )

        x_base = (X - cx) / escala
        y_base = (Y - cy) / escala
        z_base = ((Z - cz) / escala) * self.escala_z

        # Colores estáticos: no hace falta recalcularlos al rotar.
        z_min = float(np.nanmin(Z))
        z_max = float(np.nanmax(Z))

        if z_max - z_min < 1e-8:
            normalizado = np.zeros_like(Z, dtype=np.float32)
        else:
            normalizado = (Z - z_min) / (z_max - z_min)

        mapa_colores = cv2.applyColorMap(
            np.uint8(np.clip(normalizado * 255, 0, 255)),
            cv2.COLORMAP_PLASMA
        )

        # Construir los índices de los cuadriláteros de forma vectorizada.
        n_filas, n_columnas = X.shape
        rr, cc = np.indices((n_filas - 1, n_columnas - 1))

        esquinas = np.stack(
            (
                rr * n_columnas + cc,
                rr * n_columnas + cc + 1,
                (rr + 1) * n_columnas + cc + 1,
                (rr + 1) * n_columnas + cc
            ),
            axis=-1
        ).reshape(-1, 4)

        validos_plano = validos.ravel()
        caras_validas = np.all(validos_plano[esquinas], axis=1)
        indices_caras = esquinas[caras_validas]

        if len(indices_caras) == 0:
            return None

        # Un color medio por cara, calculado una sola vez.
        colores_plano = mapa_colores.reshape(-1, 3).astype(np.float32)
        colores_caras = np.mean(
            colores_plano[indices_caras],
            axis=1
        ).astype(np.uint8)

        return {
            "x": x_base.astype(np.float32).ravel(),
            "y": y_base.astype(np.float32).ravel(),
            "z": z_base.astype(np.float32).ravel(),
            "validos": validos_plano,
            "indices_caras": indices_caras,
            "colores_caras": colores_caras,
            "expression": str(datos.get("expression", "Superficie 3D"))
        }

    def _obtener_geometria(self, datos):
        # CameraView conserva el mismo diccionario durante toda la sesión.
        if datos is not self._datos_cache:
            self._geometria = self._preparar_superficie(datos)
            self._datos_cache = datos

        return self._geometria

    def render(self, frame, datos, rotacion_x=0, rotacion_y=0):
        geometria = self._obtener_geometria(datos)

        if geometria is None:
            return frame

        height, width = frame.shape[:2]

        x = geometria["x"]
        y = geometria["y"]
        z = geometria["z"]

        # Rotación sobre X.
        rx = np.radians(rotacion_x)
        cos_rx, sin_rx = np.cos(rx), np.sin(rx)

        y1 = y * cos_rx - z * sin_rx
        z1 = y * sin_rx + z * cos_rx

        # Rotación sobre Y.
        ry = np.radians(rotacion_y)
        cos_ry, sin_ry = np.cos(ry), np.sin(ry)

        x2 = x * cos_ry + z1 * sin_ry
        z2 = -x * sin_ry + z1 * cos_ry

        # Proyección isométrica.
        angle_y = np.radians(35)
        angle_x = np.radians(25)

        cos_y, sin_y = np.cos(angle_y), np.sin(angle_y)
        cos_x, sin_x = np.cos(angle_x), np.sin(angle_x)

        x3 = x2 * cos_y + z2 * sin_y
        z3 = -x2 * sin_y + z2 * cos_y

        y3 = y1 * cos_x - z3 * sin_x
        depth = y1 * sin_x + z3 * cos_x

        visual_scale = min(width, height) * self.escala_visual
        center_x = width * self.posicion_x
        center_y = height * self.posicion_y

        screen_points = np.column_stack(
            (
                center_x + x3 * visual_scale,
                center_y - y3 * visual_scale
            )
        )

        indices_caras = geometria["indices_caras"]
        polygons = np.rint(screen_points[indices_caras]).astype(np.int32)

        # Profundidad media por cara; el orden se calcula sobre arrays.
        depth_faces = np.mean(depth[indices_caras], axis=1)
        orden = np.argsort(depth_faces)

        # Descartar caras muy alejadas del fotograma antes de dibujarlas.
        margen_x = width
        margen_y = height

        min_x = np.min(polygons[:, :, 0], axis=1)
        max_x = np.max(polygons[:, :, 0], axis=1)
        min_y = np.min(polygons[:, :, 1], axis=1)
        max_y = np.max(polygons[:, :, 1], axis=1)

        visibles = (
            (max_x >= -margen_x)
            & (min_x <= width + margen_x)
            & (max_y >= -margen_y)
            & (min_y <= height + margen_y)
        )

        colores = geometria["colores_caras"]

        # Dibujar primero las caras más alejadas, como en la versión original.
        for indice in orden:
            if not visibles[indice]:
                continue

            polygon = polygons[indice]
            color = tuple(int(v) for v in colores[indice])

            cv2.fillConvexPoly(
                frame,
                polygon,
                color,
                lineType=cv2.LINE_8
            )

            # Los bordes son opcionales: dibujarlos todos encarece el render.
            if self.mostrar_bordes:
                cv2.polylines(
                    frame,
                    [polygon],
                    True,
                    (220, 220, 220),
                    1,
                    cv2.LINE_8
                )

        cv2.putText(
            frame,
            geometria["expression"],
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        return frame
