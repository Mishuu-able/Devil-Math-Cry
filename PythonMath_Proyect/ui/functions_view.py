
import customtkinter as ctk
import sympy as sp


from tkinter import messagebox

from mathematics.parser import convertir_expresion
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


class FunctionsView:

    def __init__(self, parent):

        self.parent = parent
        self.funcion = None

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

            # Validar que solo dependa de x.
            x = sp.Symbol("x")

            if funcion.free_symbols - {x}:

                raise ValueError(
                    "Por ahora solo se admiten funciones de una variable: x."
                )

            valores = [
                float(valor.strip())
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

        except Exception as error:

            messagebox.showerror(
                "Error matemático",
                str(error)
            )

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

        ctk.CTkFrame(
            clasificacion_card,
            height=5,
            fg_color="transparent"
        ).pack()


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

            tarjeta = ctk.CTkFrame(
                self.resultados,
                fg_color=TARJETA_SECUNDARIA,
                corner_radius=10
            )

            tarjeta.pack(
                fill="x",
                pady=5
            )

            valor = resultado["valor_x"]
            sustitucion = resultado["sustitucion"]
            resultado_final = resultado["resultado"]

            texto = (
                f"f({valor}) = {sustitucion}\n"
                f"Resultado = {resultado_final}"
            )

            ctk.CTkLabel(
                tarjeta,
                text=texto,
                font=(FUENTE, 13),
                text_color=TEXTO,
                justify="left"
            ).pack(
                anchor="w",
                padx=15,
                pady=12
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

            if valor is None:
                texto_valor = "No se pudo determinar automáticamente."
            else:
                texto_valor = str(valor)

            fila = ctk.CTkFrame(
                tarjeta,
                fg_color="transparent"
            )

            fila.pack(
                fill="x",
                padx=15,
                pady=12
            )

            ctk.CTkLabel(
                fila,
                text=nombre,
                font=(FUENTE, 13, "bold"),
                text_color=TEXTO
            ).pack(
                side="left"
            )

            ctk.CTkLabel(
                fila,
                text=texto_valor,
                font=(FUENTE, 13),
                text_color=VERDE if valor is not None else ROJO
            ).pack(
                side="right"
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

            x = sp.Symbol("x")

            # Comprobar que ambas sean funciones de x.
            if f.free_symbols - {x} or g.free_symbols - {x}:

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

        self.ventana_graficas = ctk.CTkToplevel(self.parent)

        self.ventana_graficas.title("Seleccionar visualización")
        self.ventana_graficas.geometry("500x300")
        self.ventana_graficas.configure(fg_color=FONDO)

        self.ventana_graficas.attributes("-topmost", True)
        self.ventana_graficas.transient(self.parent)
        self.ventana_graficas.grab_set()
        self.ventana_graficas.resizable(False, False)

        # Centrar ventana
        self.ventana_graficas.update_idletasks()

        ancho = self.ventana_graficas.winfo_width()
        alto = self.ventana_graficas.winfo_height()

        x = (self.ventana_graficas.winfo_screenwidth() - ancho) // 2
        y = (self.ventana_graficas.winfo_screenheight() - alto) // 2

        self.ventana_graficas.geometry(
            f"{ancho}x{alto}+{x}+{y}"
        )

        ctk.CTkLabel(
            self.ventana_graficas,
            text="Seleccionar visualización",
            font=(FUENTE, 22, "bold"),
            text_color=TEXTO
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self.ventana_graficas,
            text="¿Cómo deseas explorar tu función?",
            font=(FUENTE, 13),
            text_color=TEXTO_SECUNDARIO
        ).pack(pady=(0, 25))

        botones = ctk.CTkFrame(
            self.ventana_graficas,
            fg_color="transparent"
        )
        botones.pack(fill="x", padx=25)

        ctk.CTkButton(
            botones,
            text="GRÁFICA 2D",
            height=100,
            corner_radius=12,
            fg_color= GRAPH_2D_COLOR,
            hover_color= GRAPH_2D_HOVER,
            font=(FUENTE, 16, "bold"),
            command=self.abrir_grafica_2d
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        ctk.CTkButton(
            botones,
            text="GRÁFICA 3D",
            height=100,
            corner_radius=12,
            fg_color= GRAPH_3D_COLOR,
            hover_color= GRAPH_3D_HOVER,
            font=(FUENTE, 16, "bold"),
            command=self.abrir_grafica_3d
        ).pack(
            side="right",
            fill="both",
            expand=True,
            padx=(8, 0)
        )

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