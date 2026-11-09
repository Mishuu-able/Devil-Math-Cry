
import customtkinter as ctk
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np

from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from mathematics.graphics.graph_engine import generar_datos_2d
from mathematics.calculus.limits import analizar_comportamiento_limite


# ============================================================
# CONFIGURACIÓN VISUAL
# ============================================================

FONDO = "#0B1120"
TARJETA = "#111C30"
TEXTO = "#F1F5F9"
TEXTO_SECUNDARIO = "#94A3B8"

AZUL = "#3B82F6"
VERDE = "#34D399"
ROJO = "#F87171"
AMARILLO = "#FBBF24"

COLORES_FUNCIONES = [
    "#3B82F6",
    "#34D399",
    "#F59E0B",
    "#A78BFA",
    "#F87171",
    "#22D3EE",
]


class GraphView:

    def __init__(
        self,
        parent,
        expresiones,
        titulo="Gráfica matemática",
        analisis_limite=None
    ):

        self.parent = parent
        self.expresiones = expresiones
        self.analisis_limite = analisis_limite

        # Estado de navegación
        self.vista_original = None
        self.arrastrando = False
        self.posicion_anterior = None
        self.limites_arrastre = None

        # Elementos gráficos controlables
        self.function_artists = {}
        self.axis_artists = []
        self.reference_artists = []
        self.asymptote_artists = []
        self.marker_artists = []

        self.legend_artist = None

        self.variables_elementos = {}
        self.menu_visible = False

        # Evitar referencias duplicadas
        self.referencias_dibujadas = set()
        self.asintotas_dibujadas = set()

        self.ventana = ctk.CTkToplevel(parent)

        self.ventana.title(titulo)
        self.ventana.geometry("1000x750")
        self.ventana.minsize(700, 500)
        self.ventana.configure(fg_color=FONDO)

        self.ventana.transient(parent.winfo_toplevel())
        self.ventana.attributes("-topmost", True)
        self.ventana.lift()
        self.ventana.focus_force()

        self.crear_interfaz()

    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        encabezado = ctk.CTkFrame(
            self.ventana,
            fg_color="transparent"
        )

        encabezado.pack(
            fill="x",
            padx=22,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            encabezado,
            text="Visualización gráfica",
            font=("Poppins", 22, "bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        # ====================================================
        # FIGURA
        # ====================================================

        self.figura, self.ax = plt.subplots(
            figsize=(8, 5),
            dpi=100
        )

        self.configurar_ejes()

        # ====================================================
        # DIBUJAR FUNCIONES
        # ====================================================

        for nombre, expresion in self.expresiones:

            self.dibujar_funcion(
                nombre,
                expresion
            )

        # Análisis específico de límites
        if self.analisis_limite is not None:

            self.dibujar_analisis_limite()

        # Eliminar etiquetas duplicadas
        self.actualizar_leyenda()

        self.figura.tight_layout()

        # Guardar límites originales
        self.guardar_vista_original()

        # Crear panel de configuración
        self.crear_menu_elementos()

        # ====================================================
        # CONTROLES PERSONALIZADOS
        # ====================================================

        self.crear_controles()

        # ====================================================
        # CANVAS
        # ====================================================

        self.canvas = FigureCanvasTkAgg(
            self.figura,
            master=self.ventana
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(0, 8)
        )

        # ====================================================
        # INFORMACIÓN INFERIOR
        # ====================================================

        self.info_frame = ctk.CTkFrame(
            self.ventana,
            fg_color="transparent"
        )

        self.info_frame.pack(
            fill="x",
            padx=22,
            pady=(0, 10)
        )

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="ZOOM: 100%  •  ARRASTRA PARA DESPLAZAR",
            font=("Consolas", 10),
            text_color=TEXTO_SECUNDARIO
        )

        self.info_label.pack(side="left")

        # Coordenadas del cursor
        self.coordenadas_label = ctk.CTkLabel(
            self.info_frame,
            text="X: -- | Y: --",
            font=("Consolas", 10),
            text_color=VERDE
        )

        self.coordenadas_label.pack(side="right")

        # Eventos del ratón
        self.conectar_eventos()

        # Cierre
        self.ventana.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar
        )

    # ========================================================
    # CONTROLES PERSONALIZADOS
    # ========================================================

    def crear_controles(self):

        self.controles = ctk.CTkFrame(
            self.ventana,
            fg_color="transparent"
        )

        self.controles.pack(
            fill="x",
            padx=18,
            pady=(5, 8)
        )

        self.modo_movimiento = False

        botones = [
            ("−  Alejar", self.zoom_out),
            ("+  Acercar", self.zoom_in),
            ("✥  Mover", self.activar_movimiento),
            ("⌂  Inicio", self.restablecer_vista),
            ("⤢  Ajustar", self.autoajustar_ejes),
            ("☷  Elementos", self.alternar_menu_elementos),
            ("↓  Exportar", self.exportar_grafica)
        ]

        self.botones = {}

        for texto, comando in botones:

            nombre = texto.split("  ")[-1]

            boton = ctk.CTkButton(
                self.controles,
                text=texto,
                width=125 if nombre == "Elementos" else 105,
                height=36,
                corner_radius=8,
                fg_color=TARJETA,
                hover_color="#263650",
                text_color=TEXTO,
                font=("Segoe UI", 12, "bold"),
                command=comando
            )

            boton.pack(
                side="left",
                padx=4
            )

            self.botones[nombre] = boton


    
    def crear_menu_elementos(self):

        self.menu_elementos = ctk.CTkFrame(
            self.ventana,
            fg_color=TARJETA,
            corner_radius=10,
            border_width=1,
            border_color="#263650"
        )

        # Encabezado
        encabezado = ctk.CTkFrame(
            self.menu_elementos,
            fg_color="transparent"
        )

        encabezado.pack(
            fill="x",
            padx=12,
            pady=(10, 5)
        )

        ctk.CTkLabel(
            encabezado,
            text="ELEMENTOS DE VISUALIZACIÓN",
            font=("Segoe UI", 12, "bold"),
            text_color=TEXTO
        ).pack(side="left")

        ctk.CTkButton(
            encabezado,
            text="×",
            width=28,
            height=26,
            fg_color="transparent",
            hover_color="#263650",
            text_color=TEXTO,
            command=self.alternar_menu_elementos
        ).pack(side="right")

        contenido = ctk.CTkFrame(
            self.menu_elementos,
            fg_color="transparent"
        )

        contenido.pack(
            fill="x",
            padx=12,
            pady=(0, 12)
        )

        # Columnas
        generales = ctk.CTkFrame(
            contenido,
            fg_color="transparent"
        )

        generales.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        funciones = ctk.CTkFrame(
            contenido,
            fg_color="transparent"
        )

        funciones.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ----------------------------------------
        # OPCIONES GENERALES
        # ----------------------------------------

        ctk.CTkLabel(
            generales,
            text="GENERAL",
            font=("Segoe UI", 11, "bold"),
            text_color=AZUL
        ).pack(anchor="w", pady=(0, 5))

        opciones = [
            ("Ejes X / Y", "axes", True),
            ("Cuadrícula", "grid", True),
            ("Leyenda", "legend", True),
            ("Líneas de referencia", "references", True),
            ("Asíntotas", "asymptotes", True),
            ("Puntos especiales", "markers", True)
        ]

        for texto, clave, estado in opciones:

            variable = ctk.BooleanVar(value=estado)

            self.variables_elementos[clave] = variable

            ctk.CTkCheckBox(
                generales,
                text=texto,
                variable=variable,
                font=("Segoe UI", 11),
                text_color=TEXTO,
                fg_color=AZUL,
                hover_color="#2563EB",
                command=lambda k=clave: self.actualizar_elementos(k)
            ).pack(
                anchor="w",
                pady=4
            )

        # ----------------------------------------
        # FUNCIONES INDIVIDUALES
        # ----------------------------------------

        ctk.CTkLabel(
            funciones,
            text="FUNCIONES",
            font=("Segoe UI", 11, "bold"),
            text_color=AZUL
        ).pack(anchor="w", pady=(0, 5))

        for nombre in self.function_artists:

            variable = ctk.BooleanVar(value=True)

            self.variables_elementos[
                f"function:{nombre}"
            ] = variable

            ctk.CTkCheckBox(
                funciones,
                text=nombre,
                variable=variable,
                font=("Segoe UI", 11),
                text_color=TEXTO,
                fg_color=AZUL,
                hover_color="#2563EB",
                command=lambda n=nombre: self.actualizar_elementos(
                    f"function:{n}"
                )
            ).pack(
                anchor="w",
                pady=4
            )


    def alternar_menu_elementos(self):

        if self.menu_visible:

            self.menu_elementos.pack_forget()
            self.menu_visible = False

        else:

            self.menu_elementos.pack(
                fill="x",
                padx=18,
                pady=(0, 8),
                before=self.canvas.get_tk_widget()
            )

            self.menu_visible = True


    def actualizar_elementos(self, clave):
    
        visible = self.variables_elementos[clave].get()

        if clave == "axes":

            for artista in self.axis_artists:
                artista.set_visible(visible)

        elif clave == "grid":

            self.ax.grid(visible)

        elif clave == "legend":

            if self.legend_artist is not None:
                self.legend_artist.set_visible(visible)

        elif clave == "references":

            for artista in self.reference_artists:
                artista.set_visible(visible)

        elif clave == "asymptotes":

            for artista in self.asymptote_artists:
                artista.set_visible(visible)

        elif clave == "markers":

            for artista in self.marker_artists:
                artista.set_visible(visible)

        elif clave.startswith("function:"):

            nombre = clave.split(":", 1)[1]

            for artista in self.function_artists.get(nombre, []):
                artista.set_visible(visible)

        self.canvas.draw_idle()

    # ========================================================
    # CONFIGURACIÓN DE EJES
    # ========================================================

    def configurar_ejes(self):

        self.figura.patch.set_facecolor(TARJETA)
        self.ax.set_facecolor(TARJETA)

        self.axis_artists.append(
            self.ax.axhline(
                0,
                linewidth=0.8,
                color="gray",
                alpha=0.7
            )
        )

        self.axis_artists.append(
            self.ax.axvline(
                0,
                linewidth=0.8,
                color="gray",
                alpha=0.7
            )
        )

        self.ax.grid(
            True,
            linestyle="--",
            alpha=0.2
        )

        self.ax.set_xlabel(
            "X",
            color=TEXTO
        )

        self.ax.set_ylabel(
            "Y",
            color=TEXTO
        )

        self.ax.tick_params(
            colors=TEXTO
        )

        for borde in self.ax.spines.values():
            borde.set_color("#64748B")

    # ========================================================
    # DIBUJAR FUNCIONES
    # ========================================================

    
    def dibujar_funcion(self, nombre, expresion):

        datos = generar_datos_2d(expresion)

        # ====================================================
        # PREPARAR DATOS PARA EVITAR PICOS NUMÉRICOS
        # ====================================================

        valores_x = np.asarray(datos["x"], dtype=float)

        valores_y = np.asarray(
            datos["y"],
            dtype=float
        )

        # Garantizar que X e Y tengan las mismas dimensiones.
        valores_y = np.broadcast_to(
            valores_y,
            valores_x.shape
        ).copy()

        # ====================================================
        # DISCONTINUIDAD DE sign(x) EN UNA DERIVADA
        # ====================================================

        puntos_abiertos_signo = []

        if "derivada" in nombre.lower() and expresion.has(sp.sign):

            variable = next(
                iter(expresion.free_symbols),
                sp.Symbol("x", real=True)
            )

            if valores_x[0] <= 0 <= valores_x[-1]:

                limite_izquierdo = sp.limit(
                    expresion, variable, 0, dir="-"
                )

                limite_derecho = sp.limit(
                    expresion, variable, 0, dir="+"
                )

                puntos_abiertos_signo = [
                    limite_izquierdo,
                    limite_derecho
                ]

                # Insertar x=0 con un valor NaN para cortar la curva.
                indice = np.searchsorted(valores_x, 0)

                if (
                    indice < len(valores_x)
                    and np.isclose(valores_x[indice], 0)
                ):
                    valores_y[indice] = np.nan

                else:
                    valores_x = np.insert(valores_x, indice, 0)
                    valores_y = np.insert(valores_y, indice, np.nan)

        singularidades = datos["singularities"]

        if len(valores_x) > 1 and singularidades:

            paso_muestreo = np.median(np.diff(valores_x))
            margen = paso_muestreo * 3.0

            for punto in singularidades:

                mascara = np.abs(valores_x - punto) <= margen
                valores_y[mascara] = np.nan

        # ====================================================
        # DIBUJAR FUNCIÓN
        # ====================================================

        indice_color = len(self.ax.lines) % len(
            COLORES_FUNCIONES
        )

        color = COLORES_FUNCIONES[indice_color]
        # Dibujar asíntotas horizontales, oblicuas y polinómicas
        self.dibujar_asintotas_racionales(
            datos.get("asymptotes", {}),
            color
        )

        line, = self.ax.plot(
            valores_x,
            valores_y,
            label=nombre,
            linewidth=2.2,
            color=color
        )

        self.function_artists.setdefault(
            nombre, []
        ).append(line)

        # Mostrar los límites laterales de la derivada.
        for limite in puntos_abiertos_signo:

            self.dibujar_punto_abierto(
                0,
                limite,
                "Derivada no definida"
            )

        # ====================================================
        # ANALIZAR PUNTOS ESPECIALES
        # ====================================================

        if self.analisis_limite is None:

            variable = next(
                (
                    simbolo
                    for simbolo in expresion.free_symbols
                    if simbolo.name == "x"
                ),
                sp.Symbol("x")
            )

            puntos_especiales = sorted(
                set(
                    datos["singularities"]
                    + datos["discontinuities"]
                )
            )

            for punto in puntos_especiales:

                try:

                    # Recuperar precisión simbólica.
                    # Ejemplo: 1.570796... -> pi/2
                    punto_exacto = sp.nsimplify(
                        punto,
                        [sp.pi]
                    )

                    analisis = analizar_comportamiento_limite(
                        expresion,
                        punto_exacto,
                        variable
                    )

                    # El analizador determina si es:
                    # - Asíntota vertical.
                    # - Hueco.
                    # - Discontinuidad de salto.

                    self.dibujar_analisis_punto(
                        analisis
                    )

                except (
                    ValueError,
                    TypeError,
                    NotImplementedError
                ) as error:

                    print(
                        f"No se pudo analizar x={punto}: {error}"
                    )

        # ====================================================
        # EXTREMOS DEL DOMINIO
        # ====================================================

        variable = next(
            (
                simbolo
                for simbolo in expresion.free_symbols
                if simbolo.name == "x"
            ),
            sp.Symbol("x", real=True)
        )

        self.dibujar_extremos_dominio(
            datos.get("domain_extremes", []),
            expresion,
            variable,
            singularidades + datos["discontinuities"]
        )


    # ========================================================
    # EXTREMOS DEL DOMINIO
    # ========================================================

    def dibujar_extremos_dominio(
        self,
        extremos,
        expresion,
        variable,
        puntos_analizados
    ):

        for extremo in extremos:

            punto = extremo["x"]
            lado = extremo["lado"]
            incluido = extremo["incluido"]

            # Evitar duplicar puntos ya analizados.
            if any(
                np.isclose(punto, especial)
                for especial in puntos_analizados
            ):
                continue

            try:

                punto_exacto = sp.nsimplify(
                    punto,
                    [sp.pi]
                )

                # Evaluar el valor real si el extremo está incluido.
                if incluido:

                    valor = expresion.subs(
                        variable,
                        punto_exacto
                    )

                else:

                    # Obtener el límite desde el lado del dominio.
                    direccion = (
                        "+"
                        if lado == "derecho"
                        else "-"
                    )

                    valor = sp.limit(
                        expresion,
                        variable,
                        punto_exacto,
                        dir=direccion
                    )

                # No dibujar puntos con valores infinitos.
                if not self.es_valor_finito(valor):
                    continue

                valor = float(sp.N(valor))

                if incluido:

                    # Extremo cerrado.
                    artista = self.ax.scatter(
                        [punto],
                        [valor],
                        color=VERDE,
                        edgecolors=VERDE,
                        s=85,
                        zorder=9,
                        label="Extremo incluido"
                    )

                    self.marker_artists.append(artista)

                else:

                    # Extremo abierto.
                    self.dibujar_punto_abierto(
                        punto,
                        valor,
                        "Extremo no incluido"
                    )

            except (
                TypeError,
                ValueError,
                NotImplementedError,
                OverflowError
            ) as error:

                print(
                    f"No se pudo dibujar el extremo "
                    f"x={punto}: {error}"
                )


    # ========================================================
    # ASÍNTOTAS DE FUNCIONES RACIONALES
    # ========================================================

    def dibujar_asintotas_racionales(self, asintotas, color):

        if not asintotas:
            return

        x_min, x_max = self.ax.get_xlim()

        valores_x = np.linspace(x_min, x_max, 500)

        estilos = {
            "horizontal": "--",
            "oblicua": "-.",
            "polinomica": ":"
        }

        etiquetas = {
            "horizontal": "Asíntota horizontal",
            "oblicua": "Asíntota oblicua",
            "polinomica": "Asíntota polinómica"
        }

        for tipo, expresion in asintotas.items():

            if expresion is None:
                continue

            try:

                variable = next(
                    iter(expresion.free_symbols),
                    sp.Symbol("x")
                )

                funcion = sp.lambdify(
                    variable,
                    expresion,
                    modules=["numpy"]
                )

                valores_y = np.asarray(
                    funcion(valores_x),
                    dtype=float
                )

                # Garantizar que Y tenga la misma cantidad de elementos que X.
                valores_y = np.broadcast_to(
                    valores_y,
                    valores_x.shape
                ).copy()

                valores_y = np.where(
                    np.isfinite(valores_y),
                    valores_y,
                    np.nan
                )

                artista, = self.ax.plot(
                    valores_x,
                    valores_y,
                    color=color,
                    linestyle=estilos[tipo],
                    linewidth=1.7,
                    alpha=0.85,
                    label=etiquetas[tipo]
                )

                self.asymptote_artists.append(artista)

            except (
                TypeError,
                ValueError,
                NotImplementedError
            ) as error:

                print(
                    f"No se pudo dibujar la asíntota {tipo}: {error}"
                )

    # ========================================================
    # ANÁLISIS DE LÍMITES
    # ========================================================

    def dibujar_analisis_limite(self):

        self.dibujar_analisis_punto(
            self.analisis_limite
        )

    def dibujar_analisis_punto(self, datos):

        if datos is None:
            return

        punto = datos["punto"]

        limite_izquierdo = datos["limite_izquierdo"]
        limite_derecho = datos["limite_derecho"]
        valor_funcion = datos["valor_funcion"]

        try:

            x = float(sp.N(punto))

        except (
            TypeError,
            ValueError,
            OverflowError
        ):
            return

        # ====================================================
        # REFERENCIA VERTICAL
        # ====================================================

        if x not in self.referencias_dibujadas:

            artista = self.ax.axvline(
                x,
                color=AMARILLO,
                linestyle=":",
                linewidth=1.5,
                alpha=0.85,
                label="Punto de referencia"
            )

            self.reference_artists.append(artista)

            self.referencias_dibujadas.add(x)

        # ====================================================
        # VALIDACIÓN DE VALORES
        # ====================================================

        izquierda_valida = self.es_valor_finito(
            limite_izquierdo
        )

        derecha_valida = self.es_valor_finito(
            limite_derecho
        )

        valor_valido = self.es_valor_finito(
            valor_funcion
        )

        izquierda = (
            float(sp.N(limite_izquierdo))
            if izquierda_valida else None
        )

        derecha = (
            float(sp.N(limite_derecho))
            if derecha_valida else None
        )

        valor = (
            float(sp.N(valor_funcion))
            if valor_valido else None
        )

        # ====================================================
        # ASÍNTOTA VERTICAL
        # ====================================================

        if datos["asintota_vertical"]:

            if x not in self.asintotas_dibujadas:

                artista = self.ax.axvline(
                    x,
                    color=ROJO,
                    linestyle="--",
                    linewidth=2,
                    alpha=0.9,
                    label="Asíntota vertical"
                )

                self.asymptote_artists.append(artista)
                self.asintotas_dibujadas.add(x)

            self.dibujar_punto_abierto(
                x,
                limite_izquierdo,
                "Límite izquierdo"
            )

            self.dibujar_punto_abierto(
                x,
                limite_derecho,
                "Límite derecho"
            )

            return

        # ====================================================
        # COMPARAR LÍMITES
        # ====================================================

        limites_iguales = (
            izquierda_valida
            and derecha_valida
            and sp.simplify(
                limite_izquierdo - limite_derecho
            ) == 0
        )

        # ====================================================
        # DISCONTINUIDAD REMOVIBLE
        # ====================================================

        if limites_iguales:

            if (
                not valor_valido
                or sp.simplify(
                    limite_izquierdo - valor_funcion
                ) != 0
            ):

                self.dibujar_punto_abierto(
                    x,
                    limite_izquierdo,
                    "Hueco"
                )

        # ====================================================
        # DISCONTINUIDAD DE SALTO
        # ====================================================

        else:

            if (
                izquierda_valida
                and (
                    not valor_valido
                    or sp.simplify(
                        limite_izquierdo - valor_funcion
                    ) != 0
                )
            ):

                self.dibujar_punto_abierto(
                    x,
                    limite_izquierdo,
                    "Límite izquierdo"
                )

            if (
                derecha_valida
                and (
                    not valor_valido
                    or sp.simplify(
                        limite_derecho - valor_funcion
                    ) != 0
                )
            ):

                self.dibujar_punto_abierto(
                    x,
                    limite_derecho,
                    "Límite derecho"
                )

        # ====================================================
        # VALOR REAL DE LA FUNCIÓN
        # ====================================================

        if valor_valido:

            artista = self.ax.scatter(
                [x],
                [valor],
                color=VERDE,
                edgecolors=VERDE,
                s=75,
                zorder=8,
                label="Valor de f(x)"
            )

            self.marker_artists.append(artista)

    # ========================================================
    # PUNTOS ABIERTOS
    # ========================================================

    def dibujar_punto_abierto(self, x, y, etiqueta):

        if not self.es_valor_finito(y):
            return

        artista = self.ax.scatter(
            [x],
            [float(sp.N(y))],
            facecolors="none",
            edgecolors=AMARILLO,
            linewidths=2,
            s=100,
            zorder=7,
            label=etiqueta
        )

        self.marker_artists.append(artista)

    # ========================================================
    # ELIMINAR ETIQUETAS DUPLICADAS
    # ========================================================

    def actualizar_leyenda(self):

        handles, labels = self.ax.get_legend_handles_labels()

        etiquetas = {}

        for handle, label in zip(handles, labels):

            if label not in etiquetas:
                etiquetas[label] = handle

        if etiquetas:

            self.legend_artist = self.ax.legend(
                etiquetas.values(),
                etiquetas.keys(),
                facecolor=TARJETA,
                labelcolor=TEXTO,
                edgecolor="#263650"
            )

    # ========================================================
    # VALIDACIÓN
    # ========================================================

    @staticmethod
    def es_valor_finito(valor):

        try:

            valor = sp.sympify(valor)

            if valor.has(
                sp.zoo,
                sp.oo,
                -sp.oo,
                sp.nan
            ):
                return False

            return valor.is_finite is True

        except (TypeError, ValueError):
            return False

    # ========================================================
    # GUARDAR VISTA ORIGINAL
    # ========================================================

    def guardar_vista_original(self):

        self.vista_original = (
            self.ax.get_xlim(),
            self.ax.get_ylim()
        )

    # ========================================================
    # ZOOM
    # ========================================================

    def zoom(self, factor, centro=None):

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        if centro is None:

            centro_x = (xlim[0] + xlim[1]) / 2
            centro_y = (ylim[0] + ylim[1]) / 2

        else:

            centro_x, centro_y = centro

        ancho = (xlim[1] - xlim[0]) * factor
        alto = (ylim[1] - ylim[0]) * factor

        self.ax.set_xlim(
            centro_x - ancho / 2,
            centro_x + ancho / 2
        )

        self.ax.set_ylim(
            centro_y - alto / 2,
            centro_y + alto / 2
        )

        self.canvas.draw_idle()

    def zoom_in(self):

        self.zoom(0.8)

    def zoom_out(self):

        self.zoom(1.25)

    # ========================================================
    # RESTABLECER VISTA
    # ========================================================

    def restablecer_vista(self):

        if self.vista_original is None:
            return

        xlim, ylim = self.vista_original

        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        self.canvas.draw_idle()

    # ========================================================
    # AUTOAJUSTE DE EJES
    # ========================================================

    def autoajustar_ejes(self):

        valores_x = []
        valores_y = []

        # Obtener datos de las funciones visibles
        for artistas in self.function_artists.values():

            for artista in artistas:

                if not artista.get_visible():
                    continue

                x, y = artista.get_data()

                x = np.asarray(x, dtype=float)
                y = np.asarray(y, dtype=float)

                mascara = np.isfinite(x) & np.isfinite(y)

                valores_x.extend(x[mascara])
                valores_y.extend(y[mascara])

        if not valores_x or not valores_y:
            return

        x_min = min(valores_x)
        x_max = max(valores_x)

        y_min = min(valores_y)
        y_max = max(valores_y)

        # Evitar rangos demasiado pequeños
        rango_x = x_max - x_min
        rango_y = y_max - y_min

        if rango_x == 0:
            rango_x = 2

        if rango_y == 0:
            rango_y = 2

        # Añadir margen visual
        margen_x = rango_x * 0.05
        margen_y = rango_y * 0.10

        self.ax.set_xlim(
            x_min - margen_x,
            x_max + margen_x
        )

        self.ax.set_ylim(
            y_min - margen_y,
            y_max + margen_y
        )

        self.canvas.draw_idle()

    # ========================================================
    # MOVIMIENTO
    # ========================================================

    def activar_movimiento(self):

        self.modo_movimiento = not self.modo_movimiento

        boton = self.botones["Mover"]

        if self.modo_movimiento:

            boton.configure(
                fg_color=AZUL,
                hover_color="#2563EB",
                text="✥  Moviendo"
            )

            self.canvas.get_tk_widget().configure(
                cursor="fleur"
            )

            self.info_label.configure(
                text="MODO MOVER ACTIVO • ARRASTRA CON EL RATÓN"
            )

        else:

            boton.configure(
                fg_color=TARJETA,
                hover_color="#263650",
                text="✥  Mover"
            )

            self.canvas.get_tk_widget().configure(
                cursor=""
            )

            self.info_label.configure(
                text="MODO NORMAL • UTILIZA LOS CONTROLES PARA NAVEGAR"
            )

            self.arrastrando = False
            self.posicion_anterior = None
            self.limites_arrastre = None

    def conectar_eventos(self):

        self.canvas.mpl_connect(
            "button_press_event",
            self.al_iniciar_arrastre
        )

        self.canvas.mpl_connect(
            "motion_notify_event",
            self.al_mover_ratón
        )

        self.canvas.mpl_connect(
            "button_release_event",
            self.al_terminar_arrastre
        )

        self.canvas.mpl_connect(
            "scroll_event",
            self.al_hacer_zoom
        )

    def al_iniciar_arrastre(self, evento):

        if not self.modo_movimiento:
            return

        if evento.inaxes != self.ax:
            return

        if evento.button != 1:
            return

        self.arrastrando = True

        # Guardar posición inicial en píxeles
        self.posicion_anterior = (
            evento.x,
            evento.y
        )

        # Guardar límites originales del movimiento
        self.limites_arrastre = (
            self.ax.get_xlim(),
            self.ax.get_ylim()
        )


    def al_mover_ratón(self, evento):

          # Actualizar coordenadas del cursor
        if (
            evento.inaxes == self.ax
            and evento.xdata is not None
            and evento.ydata is not None
        ):

            self.coordenadas_label.configure(
                text=(
                    f"X: {evento.xdata:.4f} | "
                    f"Y: {evento.ydata:.4f}"
                )
            )

        else:

            self.coordenadas_label.configure(
                text="X: -- | Y: --"
            )

        # Mantener el comportamiento de desplazamiento
        if not self.arrastrando:
            return

        if self.posicion_anterior is None:
            return

        if self.limites_arrastre is None:
            return

        # Desplazamiento en píxeles
        inicio_x, inicio_y = self.posicion_anterior

        delta_x = evento.x - inicio_x
        delta_y = evento.y - inicio_y

        # Límites iniciales
        xlim, ylim = self.limites_arrastre

        ancho = self.ax.bbox.width
        alto = self.ax.bbox.height

        if ancho <= 0 or alto <= 0:
            return

        # Convertir desplazamiento de píxeles a unidades matemáticas
        escala_x = (xlim[1] - xlim[0]) / ancho
        escala_y = (ylim[1] - ylim[0]) / alto

        desplazamiento_x = -delta_x * escala_x
        desplazamiento_y = -delta_y * escala_y

        # Calcular siempre desde la posición inicial
        self.ax.set_xlim(
            xlim[0] + desplazamiento_x,
            xlim[1] + desplazamiento_x
        )

        self.ax.set_ylim(
            ylim[0] + desplazamiento_y,
            ylim[1] + desplazamiento_y
        )

        self.canvas.draw_idle()


    def al_terminar_arrastre(self, evento):

        self.arrastrando = False
        self.posicion_anterior = None
        self.limites_arrastre = None

    # ========================================================
    # ZOOM CON RUEDA DEL RATÓN
    # ========================================================

    def al_hacer_zoom(self, evento):

        if evento.inaxes != self.ax:
            return

        if evento.xdata is None or evento.ydata is None:
            return

        if evento.button == "up":
            factor = 0.8

        elif evento.button == "down":
            factor = 1.25

        else:
            return

        self.zoom(
            factor,
            centro=(evento.xdata, evento.ydata)
        )

    # ========================================================
    # EXPORTAR GRÁFICA
    # ========================================================

    def exportar_grafica(self):

        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("Imagen PNG", "*.png"),
                ("Imagen PDF", "*.pdf")
            ],
            title="Exportar gráfica"
        )

        if not ruta:
            return

        try:

            self.figura.savefig(
                ruta,
                dpi=200,
                bbox_inches="tight",
                facecolor=self.figura.get_facecolor()
            )

            self.info_label.configure(
                text="GRÁFICA EXPORTADA CORRECTAMENTE"
            )

        except Exception as error:

            print("Error al exportar:", error)

            self.info_label.configure(
                text="ERROR AL EXPORTAR LA GRÁFICA"
            )

    # ========================================================
    # CERRAR
    # ========================================================

    def cerrar(self):

        plt.close(self.figura)
        self.ventana.destroy()
