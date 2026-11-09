
import customtkinter as ctk
import sympy as sp


from tkinter import messagebox

from mathematics.parser import convertir_expresion, X
from mathematics.functions.evaluator import evaluar_funcion
from mathematics.functions.analysis import (
    analizar_funcion,
    generar_explicaciones
)

from mathematics.functions.operations import (
    operar_funciones,
    generar_procedimiento
)

from mathematics.functions.classifier import (
    clasificar_funcion,
    generar_explicacion_clasificacion
)

from ui.graph_view import GraphView
from ui.components.graph_selector import GraphSelector
from ui.camera_view import CameraView
from mathematics.graphics.graph_engine import generar_datos_3d
from visualization.graph_3D import Graph3D, detectar_camara

from ui.theme import (
    FUNCTIONS_BG as FONDO,
    FUNCTIONS_CARD as TARJETA,
    FUNCTIONS_CARD_SECONDARY as TARJETA_SECUNDARIA,

    FUNCTIONS_PRIMARY as AZUL,
    FUNCTIONS_PRIMARY_HOVER as AZUL_HOVER,

    FUNCTIONS_TEXT as TEXTO,
    FUNCTIONS_TEXT_SECONDARY as TEXTO_SECUNDARIO,

    FUNCTIONS_BORDER as BORDE,
    FUNCTIONS_SUCCESS as VERDE,
    FUNCTIONS_ERROR as ROJO,

    FUNCTIONS_GRAPH_2D as GRAPH_2D_COLOR,
    FUNCTIONS_GRAPH_2D_HOVER as GRAPH_2D_HOVER,

    FUNCTIONS_GRAPH_3D as GRAPH_3D_COLOR,
    FUNCTIONS_GRAPH_3D_HOVER as GRAPH_3D_HOVER,

    FONT_FAMILY as FUENTE
)

from ui.components.math_chat import MathChat
from mathematics.renderer import expresion_a_imagen
from PIL import Image

class FunctionsView:

    def __init__(self, parent):

        self.parent = parent
        self.funcion = None

        # Contexto de Rebellion
        self.chat_rebellion = None
        self.ultimo_contexto = {}

        self.crear_interfaz()

    # ==========================================
    # INTERFAZ PRINCIPAL
    # ==========================================

    def crear_interfaz(self):

        self.contenedor = ctk.CTkFrame(
            self.parent,
            fg_color=FONDO,
            corner_radius=0
        )

        self.contenedor.pack(
            fill="both",
            expand=True
        )

        # ENCABEZADO

        encabezado = ctk.CTkFrame(
            self.contenedor,
            fg_color="transparent"
        )

        encabezado.pack(
            fill="x",
            padx=30,
            pady=(24, 15)
        )

        ctk.CTkLabel(
            encabezado,
            text="Análisis de funciones",
            font=(FUENTE, 27, "bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            encabezado,
            text="Evalúa y estudia el comportamiento de funciones matemáticas.",
            font=(FUENTE, 13),
            text_color=TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(5, 0))

        # PANEL DESPLAZABLE

        self.panel = ctk.CTkScrollableFrame(
            self.contenedor,
            fg_color=FONDO,
            corner_radius=0
        )

        self.panel.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        # TARJETA DE ENTRADA

        self.crear_entrada()

        # TARJETA DE RESULTADOS

        self.crear_resultados()
        self.crear_operaciones()
        self.crear_boton_graficar()

        # ==========================================
        # REBELLION - ASISTENTE MATEMÁTICO
        # ==========================================

        self.chat_rebellion = MathChat(
            self.panel,
            contexto={}
        )

        self.chat_rebellion.configure(height=500)
        self.chat_rebellion.pack_propagate(False)

        self.chat_rebellion.pack(
            fill="x",
            padx=20,
            pady=(10, 20)
        )

    # ==========================================
    # ENTRADA DE FUNCIÓN
    # ==========================================

    def crear_entrada(self):

        tarjeta = ctk.CTkFrame(
            self.panel,
            fg_color=TARJETA,
            corner_radius=16,
            border_width=1,
            border_color=BORDE
        )

        tarjeta.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            tarjeta,
            text="Función matemática",
            font=(FUENTE, 16, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            tarjeta,
            text="Introduce una función de x.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        self.entrada_funcion = ctk.CTkEntry(
            tarjeta,
            height=45,
            corner_radius=10,
            border_color=BORDE,
            fg_color=TARJETA_SECUNDARIA,
            text_color=TEXTO,
            placeholder_text="Ejemplo: x^2 + 3x - 4",
            font=(FUENTE, 14)
        )

        self.entrada_funcion.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            tarjeta,
            text="Valores de X (separados por comas)",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        self.entrada_valores = ctk.CTkEntry(
            tarjeta,
            height=45,
            corner_radius=10,
            border_color=BORDE,
            fg_color=TARJETA_SECUNDARIA,
            text_color=TEXTO,
            placeholder_text="Ejemplo: -2, 0, 1, 2, 3",
            font=(FUENTE, 14)
        )

        self.entrada_valores.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.entrada_funcion.bind(
            "<Return>",
            lambda evento: self.calcular()
        )

        self.boton_calcular = ctk.CTkButton(
            tarjeta,
            text="Evaluar función",
            height=45,
            corner_radius=10,
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            font=(FUENTE, 14, "bold"),
            command=self.calcular
        )

        self.boton_calcular.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )


    def crear_boton_graficar(self):
        self.boton_graficar = ctk.CTkButton(
            self.panel,
            text="VISUALIZAR GRÁFICA",
            height=42,
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            font=(FUENTE, 13, "bold"),
            command=self.abrir_selector_grafica
        )

        self.boton_graficar.pack(
            fill="x",
            padx=20,
            pady=(10, 20)
        )

    # ==========================================
    # RESULTADOS
    # ==========================================

    def crear_resultados(self):

        self.resultado_card = ctk.CTkFrame(
            self.panel,
            fg_color=TARJETA,
            corner_radius=16,
            border_width=1,
            border_color=BORDE
        )

        self.resultado_card.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            self.resultado_card,
            text="Resultados de evaluación",
            font=(FUENTE, 18, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.resultados = ctk.CTkFrame(
            self.resultado_card,
            fg_color="transparent"
        )

        self.resultados.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.mostrar_mensaje_inicial()

    # ==========================================
    # CALCULAR
    # ==========================================

    def calcular(self):

        texto_funcion = self.entrada_funcion.get().strip()
        texto_valores = self.entrada_valores.get().strip()

        if not texto_funcion or not texto_valores:

            messagebox.showwarning(
                "Datos incompletos",
                "Introduce una función y sus valores de X."
            )

            return

        try:

            funcion = convertir_expresion(texto_funcion)

            if funcion.free_symbols - {X}:

                raise ValueError(
                    "Por ahora solo se admiten funciones de una variable: x."
                )

            valores = [
                convertir_expresion(valor.strip())
                for valor in texto_valores.split(",")
            ]

            if not valores:
                raise ValueError("No se introdujeron valores.")

            resultados = evaluar_funcion(
                funcion,
                valores
            )

            self.funcion = funcion

            analisis = analizar_funcion(funcion)
            clasificacion = clasificar_funcion(funcion)
            explicacion_clasificacion = generar_explicacion_clasificacion(
                clasificacion)
            explicaciones = generar_explicaciones(
                funcion,
                analisis)
            
            self.mostrar_resultados(
                funcion,
                resultados,
                analisis,
                explicaciones,
                clasificacion,
                explicacion_clasificacion)

            # Actualizar contexto de Rebellion

            self.ultimo_contexto = {
                "modulo": "Funciones",
                "tipo_operacion": "Evaluación y análisis",
                "funcion_original": texto_funcion,
                "funcion_simbolica": str(funcion),
                "valores_evaluados": str(valores),
                "resultados_evaluacion": str(resultados),
                "clasificacion": str(clasificacion),
                "dominio": str(analisis.get("dominio")),
                "rango": str(analisis.get("rango")),
                "raices": str(analisis.get("raices")),
                "interseccion_y": str(analisis.get("interseccion_y")),
                "paridad": str(analisis.get("paridad")),
                "procedimiento": str(explicaciones)
            }

            self.actualizar_contexto_rebellion()

        except Exception as error:

            messagebox.showerror(
                "Error matemático",
                str(error)
            )

    def crear_imagen_matematica(
        self,
        contenedor,
        expresion,
        fontsize=24,
        max_width=650,
        color="#F5F5F5",
        side="top",
        pady=3
    ):
        """Renderiza una expresión SymPy como imagen matemática compacta."""

        imagen = expresion_a_imagen(
            expresion,
            fontsize=fontsize,
            dpi=180
        )

        # Recortar el espacio transparente que deja Matplotlib.
        bbox = imagen.getbbox()
        if bbox:
            imagen = imagen.crop(bbox)

        # Aplicar un color legible conservando la transparencia.
        alpha = imagen.getchannel("A")
        imagen_color = Image.new("RGBA", imagen.size, color)
        imagen_color.putalpha(alpha)
        imagen = imagen_color

        # Limitar el tamaño para evitar desbordamientos.
        factor = min(
            1,
            max_width / max(imagen.width, 1),
            85 / max(imagen.height, 1)
        )

        if factor < 1:
            imagen = imagen.resize(
                (
                    max(1, int(imagen.width * factor)),
                    max(1, int(imagen.height * factor))
                ),
                Image.Resampling.LANCZOS
            )

        imagen_ctk = ctk.CTkImage(
            light_image=imagen,
            dark_image=imagen,
            size=imagen.size
        )

        etiqueta = ctk.CTkLabel(
            contenedor,
            text="",
            image=imagen_ctk,
            fg_color="transparent"
        )
        etiqueta.image = imagen_ctk

        etiqueta.pack(
            side=side,
            anchor="center",
            padx=8,
            pady=pady
        )

        return etiqueta

    # ==========================================
    # MOSTRAR RESULTADOS
    # ==========================================

    
    def mostrar_resultados(self, funcion, resultados, analisis, explicaciones, clasificacion, 
        explicacion_clasificacion):

        self.limpiar_frame(self.resultados)

        # FUNCIÓN ORIGINAL

        ctk.CTkLabel(
            self.resultados,
            text=f"f(x) = {sp.sstr(funcion)}",
            font=(FUENTE, 16, "bold"),
            text_color=AZUL
        ).pack(
            anchor="w",
            padx=10,
            pady=(8, 15)
        )

        
        # ======================================
        # CLASIFICACIÓN DE LA FUNCIÓN
        # ======================================

        clasificacion_card = ctk.CTkFrame(
            self.resultados,
            fg_color=TARJETA_SECUNDARIA,
            corner_radius=12,
            border_width=1,
            border_color=BORDE
        )

        clasificacion_card.pack(
            fill="x",
            padx=8,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            clasificacion_card,
            text="Clasificación matemática",
            font=(FUENTE, 15, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=15,
            pady=(14, 8)
        )

        ctk.CTkLabel(
            clasificacion_card,
            text=clasificacion["categoria"],
            font=(FUENTE, 20, "bold"),
            text_color=VERDE
        ).pack(
            anchor="w",
            padx=15,
            pady=5
        )

        if clasificacion["componentes"]:

            ctk.CTkLabel(
                clasificacion_card,
                text="Categorías: " + ", ".join(
                    clasificacion["componentes"]
                ),
                font=(FUENTE, 12),
                text_color=TEXTO_SECUNDARIO,
                wraplength=600
            ).pack(
                anchor="w",
                padx=15,
                pady=5
            )

        if clasificacion["grado"] is not None:

            ctk.CTkLabel(
                clasificacion_card,
                text=f"Grado polinómico: {clasificacion['grado']}",
                font=(FUENTE, 12),
                text_color=TEXTO
            ).pack(
                anchor="w",
                padx=15,
                pady=5
            )

        for paso in explicacion_clasificacion:

            ctk.CTkLabel(
                clasificacion_card,
                text="• " + paso,
                font=(FUENTE, 12),
                text_color=TEXTO_SECUNDARIO,
                wraplength=600,
                justify="left"
            ).pack(
                fill="x",
                padx=18,
                pady=4
            )



        # EVALUACIONES

        ctk.CTkLabel(
            self.resultados,
            text="Evaluación de valores",
            font=(FUENTE, 15, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=10,
            pady=(5, 10)
        )

        for resultado in resultados:

            valor = resultado["valor_x"]
            resultado_final = resultado["resultado"]

            tarjeta = ctk.CTkFrame(
                self.resultados,
                fg_color=TARJETA_SECUNDARIA,
                corner_radius=10
            )
            tarjeta.pack(
                fill="x",
                pady=5
            )

            # Mostrar la entrada exacta y el resultado.
            formula = sp.Eq(
                sp.Function("f")(valor),
                resultado_final,
                evaluate=False
            )

            self.crear_imagen_matematica(
                tarjeta,
                formula,
                fontsize=25,
                max_width=650,
                color="#F5F5F5",
                pady=(10, 5)
            )

            ctk.CTkLabel(
                tarjeta,
                text=f"Resultado: {sp.sstr(resultado_final)}",
                font=(FUENTE, 14, "bold"),
                text_color=VERDE
            ).pack(
                anchor="w",
                padx=15,
                pady=(2, 10)
            )

        # ANÁLISIS MATEMÁTICO

        ctk.CTkFrame(
            self.resultados,
            height=1,
            fg_color=BORDE
        ).pack(
            fill="x",
            padx=8,
            pady=18
        )

        ctk.CTkLabel(
            self.resultados,
            text="Análisis de la función",
            font=(FUENTE, 17, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=10,
            pady=(0, 12)
        )

        propiedades = [
            ("Dominio", analisis["dominio"]),
            ("Rango", analisis["rango"]),
            ("Raíces", analisis["raices"]),
            ("Intersección con Y", analisis["interseccion_y"]),
            ("Paridad", analisis["paridad"])
        ]

        for nombre, valor in propiedades:

            tarjeta = ctk.CTkFrame(
                self.resultados,
                fg_color=TARJETA_SECUNDARIA,
                corner_radius=10
            )
            tarjeta.pack(
                fill="x",
                pady=4
            )

            fila = ctk.CTkFrame(
                tarjeta,
                fg_color="transparent"
            )
            fila.pack(
                fill="x",
                padx=15,
                pady=8
            )

            ctk.CTkLabel(
                fila,
                text=nombre,
                font=(FUENTE, 13, "bold"),
                text_color=TEXTO
            ).pack(
                side="left",
                anchor="center"
            )

            if valor is None:
                ctk.CTkLabel(
                    fila,
                    text="No se pudo determinar automáticamente.",
                    font=(FUENTE, 12),
                    text_color=ROJO
                ).pack(side="right")

            elif isinstance(valor, str):
                ctk.CTkLabel(
                    fila,
                    text=valor,
                    font=(FUENTE, 13),
                    text_color=VERDE
                ).pack(side="right")

            else:
                self.crear_imagen_matematica(
                    fila,
                    valor,
                    fontsize=17,
                    max_width=450,
                    color="#16D978",
                    side="right",
                    pady=2
                )

        # ======================================
        # PROCEDIMIENTOS MATEMÁTICOS
        # ======================================

        ctk.CTkFrame(
            self.resultados,
            height=1,
            fg_color=BORDE
        ).pack(
            fill="x",
            padx=8,
            pady=18
        )

        ctk.CTkLabel(
            self.resultados,
            text="Procedimiento matemático",
            font=(FUENTE, 18, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=10,
            pady=(0, 15)
        )

        titulos = {
            "dominio": "1. Dominio",
            "rango": "2. Rango",
            "raices": "3. Cálculo de raíces",
            "interseccion_y": "4. Intersección con el eje Y",
            "paridad": "5. Análisis de paridad"
        }

        for clave, pasos in explicaciones.items():

            tarjeta = ctk.CTkFrame(
                self.resultados,
                fg_color=TARJETA_SECUNDARIA,
                corner_radius=12
            )

            tarjeta.pack(
                fill="x",
                pady=6
            )

            ctk.CTkLabel(
                tarjeta,
                text=titulos[clave],
                font=(FUENTE, 14, "bold"),
                text_color=AZUL
            ).pack(
                anchor="w",
                padx=15,
                pady=(14, 8)
            )

            for indice, paso in enumerate(pasos, start=1):

                ctk.CTkLabel(
                    tarjeta,
                    text=f"{indice}. {paso}",
                    font=(FUENTE, 12),
                    text_color=TEXTO,
                    justify="left",
                    anchor="w",
                    wraplength=650
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(3, 6)
                )

            ctk.CTkFrame(
                tarjeta,
                height=5,
                fg_color="transparent"
            ).pack()



    # ==========================================
    # MENSAJE INICIAL
    # ==========================================

    def mostrar_mensaje_inicial(self):

        ctk.CTkLabel(
            self.resultados,
            text="f(x) → Evaluación",
            font=(FUENTE, 22, "bold"),
            text_color=AZUL
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self.resultados,
            text="Introduce una función para comenzar.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(pady=(0, 15))

    # ==========================================
    # UTILIDADES
    # ==========================================

    @staticmethod
    def limpiar_frame(frame):

        for widget in frame.winfo_children():
            widget.destroy()

    def pack(self, **kwargs):
        self.contenedor.pack(**kwargs)

    def grid(self, **kwargs):
        self.contenedor.grid(**kwargs)

    def place(self, **kwargs):
        self.contenedor.place(**kwargs)

    def destroy(self):
        self.contenedor.destroy()


    
    def crear_operaciones(self):

        self.operaciones_card = ctk.CTkFrame(
            self.panel,
            fg_color=TARJETA,
            corner_radius=16,
            border_width=1,
            border_color=BORDE
        )

        self.operaciones_card.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            self.operaciones_card,
            text="Operaciones entre funciones",
            font=(FUENTE, 18, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            self.operaciones_card,
            text="Introduce dos funciones para operar con ellas.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        self.entrada_f = ctk.CTkEntry(
            self.operaciones_card,
            height=42,
            placeholder_text="Primera función: x^2 + 2x"
        )

        self.entrada_f.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.entrada_g = ctk.CTkEntry(
            self.operaciones_card,
            height=42,
            placeholder_text="Segunda función: x + 3"
        )

        self.entrada_g.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.selector_operacion = ctk.CTkOptionMenu(
            self.operaciones_card,
            values=[
                "Suma",
                "Resta",
                "Multiplicación",
                "División",
                "f(g(x))",
                "g(f(x))"
            ],
            height=40,
            fg_color=AZUL,
            button_color=AZUL,
            button_hover_color=AZUL_HOVER,
            font=(FUENTE, 13)
        )

        self.selector_operacion.pack(
            fill="x",
            padx=20,
            pady=10
        )

        ctk.CTkButton(
            self.operaciones_card,
            text="Calcular operación",
            height=43,
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            font=(FUENTE, 13, "bold"),
            command=self.calcular_operacion
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )


    def calcular_operacion(self):

        texto_f = self.entrada_f.get().strip()
        texto_g = self.entrada_g.get().strip()

        if not texto_f or not texto_g:

            messagebox.showwarning(
                "Datos incompletos",
                "Introduce las dos funciones."
            )

            return

        try:

            f = convertir_expresion(texto_f)
            g = convertir_expresion(texto_g)

            # Comprobar que ambas sean funciones de la variable compartida X.
            if f.free_symbols - {X} or g.free_symbols - {X}:

                raise ValueError(
                    "Solo se admiten funciones de una variable: x."
                )

            operacion = self.selector_operacion.get()

            datos = operar_funciones(
                f,
                g,
                operacion
            )

            pasos = generar_procedimiento(datos)

            self.mostrar_operacion(datos, pasos)

            # Actualizar contexto de Rebellion

            self.ultimo_contexto = {
                "modulo": "Funciones",
                "tipo_operacion": "Operaciones entre funciones",
                "primera_funcion": str(datos["funcion_f"]),
                "segunda_funcion": str(datos["funcion_g"]),
                "operacion": self.selector_operacion.get(),
                "resultado": str(datos["resultado"]),
                "procedimiento": "\n".join(
                    str(paso) for paso in pasos
                )
            }

            self.actualizar_contexto_rebellion()

        except Exception as error:

            messagebox.showerror(
                "Error en la operación",
                str(error)
            )


    def mostrar_operacion(self, datos, pasos):

        # Limpiamos únicamente los resultados anteriores
        # de operaciones, sin borrar la evaluación principal.

        if hasattr(self, "operacion_resultado"):
            self.operacion_resultado.destroy()

        self.operacion_resultado = ctk.CTkFrame(
            self.operaciones_card,
            fg_color=TARJETA_SECUNDARIA,
            corner_radius=12
        )

        self.operacion_resultado.pack(
            fill="x",
            padx=20,
            pady=(0, 18)
        )

        ctk.CTkLabel(
            self.operacion_resultado,
            text="Resultado de la operación",
            font=(FUENTE, 15, "bold"),
            text_color=VERDE
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 8)
        )

        ctk.CTkLabel(
            self.operacion_resultado,
            text=f"f(x) = {sp.sstr(datos['funcion_f'])}",
            font=(FUENTE, 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=15, pady=3)

        ctk.CTkLabel(
            self.operacion_resultado,
            text=f"g(x) = {sp.sstr(datos['funcion_g'])}",
            font=(FUENTE, 12),
            text_color=TEXTO
        ).pack(anchor="w", padx=15, pady=3)

        ctk.CTkLabel(
            self.operacion_resultado,
            text=f"Resultado: {sp.sstr(datos['resultado'])}",
            font=(FUENTE, 16, "bold"),
            text_color=VERDE,
            wraplength=600
        ).pack(
            anchor="w",
            padx=15,
            pady=10
        )

        ctk.CTkFrame(
            self.operacion_resultado,
            height=1,
            fg_color=BORDE
        ).pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(
            self.operacion_resultado,
            text="Procedimiento",
            font=(FUENTE, 14, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=15,
            pady=(5, 8)
        )

        for indice, paso in enumerate(pasos, start=1):

            ctk.CTkLabel(
                self.operacion_resultado,
                text=f"{indice}. {paso}",
                font=(FUENTE, 12),
                text_color=TEXTO_SECUNDARIO,
                wraplength=600,
                justify="left",
                anchor="w"
            ).pack(
                fill="x",
                padx=18,
                pady=4
            )

        ctk.CTkFrame(
            self.operacion_resultado,
            height=5,
            fg_color="transparent"
        ).pack()

    def abrir_selector_grafica(self):
        if self.funcion is None:
            messagebox.showwarning(
                "Sin resultados",
                "Primero debes calcular una función."
            )
            return

        selector = GraphSelector(
            self.parent,
            fondo=FONDO,
            texto=TEXTO,
            texto_secundario=TEXTO_SECUNDARIO,
            fuente=FUENTE,
            color_2d=GRAPH_2D_COLOR,
            hover_2d=GRAPH_2D_HOVER,
            color_3d=GRAPH_3D_COLOR,
            hover_3d=GRAPH_3D_HOVER,
            on_2d=self.abrir_grafica_2d,
            on_3d=self.abrir_grafica_3d,
            on_ar=self.abrir_camara_ar,
            descripcion="¿Cómo deseas explorar tu función?",
        )
        self.ventana_graficas = selector.ventana

    def abrir_grafica_2d(self):
        self.ventana_graficas.destroy()

        GraphView(
            self.parent,
            [
                ("Función", self.funcion)
            ],
            titulo="Funciones - 2D"
        )


    def abrir_grafica_3d(self):
        self.ventana_graficas.destroy()

        try:
            datos = generar_datos_3d(
                self.funcion
            )

            visor = Graph3D(
                usar_gestos=detectar_camara()
            )

            visor.mostrar_superficie(datos)

        except Exception as error:
            messagebox.showerror(
                "Error de visualización 3D",
                f"No se pudo abrir el visor.\n\n{error}"
            )
    def abrir_camara_ar(self):
        self.ventana_graficas.destroy()

        try:
            datos = generar_datos_3d(self.funcion)

            ventana = ctk.CTkToplevel(self.parent)
            ventana.title("Devil Math Cry - Realidad Aumentada")
            ventana.geometry("1000x750")
            ventana.configure(fg_color=FONDO)
            ventana.minsize(700, 500)

            ventana.transient(self.parent.winfo_toplevel())
            ventana.lift()
            ventana.focus_force()

            visor = CameraView(ventana, datos)
            visor.iniciar()

        except Exception as error:
            messagebox.showerror(
                "Error de cámara AR",
                f"No se pudo iniciar la visualización.\\n\\n{error}"
            )

    # ==========================================
    # CONTEXTO DE REBELLION
    # ==========================================

    def actualizar_contexto_rebellion(self):

        if self.chat_rebellion is None:
            return

        self.chat_rebellion.actualizar_contexto(
            self.ultimo_contexto
        )