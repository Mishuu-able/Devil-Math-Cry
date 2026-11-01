import customtkinter as ctk
import sympy as sp
from ui.graph_view import GraphView

from mathematics.algebra.operations import (
    simplificar,
    desarrollar,
    factorizar,
    resolver_ecuacion, 
    resolver_sistema,
)

from mathematics.parser import convertir_expresion
from mathematics.renderer import expresion_a_imagen


# ─────────────────────────────────────────────
# PALETA DE COLORES
# ─────────────────────────────────────────────

FONDO = "#0B1120"
TARJETA = "#111C30"
TARJETA_SECUNDARIA = "#17243B"
AZUL = "#3B82F6"
AZUL_HOVER = "#2563EB"
TEXTO = "#F1F5F9"
TEXTO_SECUNDARIO = "#94A3B8"
BORDE = "#263650"
VERDE = "#34D399"
ROJO = "#F87171"

FUENTE = "Poppins"


class AlgebraView:

    OPERACIONES = [
        "Simplificar",
        "Desarrollar",
        "Factorizar",
        "Resolver ecuación",
        "Resolver sistema",
    ]

    def __init__(self, parent):
        self.parent = parent
        self.imagenes = []
        self.ultima_expresion = None

        self.crear_interfaz()

    # ─────────────────────────────────────────
    # INTERFAZ
    # ─────────────────────────────────────────

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
            fg_color=FONDO
        )

        encabezado.pack(
            fill="x",
            padx=30,
            pady=(24, 12)
        )

        ctk.CTkLabel(
            encabezado,
            text="Álgebra",
            font=(FUENTE, 27, "bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            encabezado,
            text="Resuelve y transforma expresiones algebraicas paso a paso.",
            font=(FUENTE, 13),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # PANEL DESPLAZABLE

        self.panel = ctk.CTkScrollableFrame(
            self.contenedor,
            fg_color=FONDO,
            corner_radius=0,
            scrollbar_button_color=AZUL,
            scrollbar_button_hover_color=AZUL_HOVER
        )

        self.panel.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 15)
        )

        contenido = ctk.CTkFrame(
            self.panel,
            fg_color="transparent"
        )

        contenido.bind(
            "<MouseWheel>",
            self._scroll_sistema,
            add="+")

        contenido.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # ─────────────────────────────────────
        # ENTRADA
        # ─────────────────────────────────────

        entrada_card = ctk.CTkFrame(
            contenido,
            fg_color=TARJETA,
            corner_radius=16,
            border_width=1,
            border_color=BORDE
        )

        entrada_card.bind(
            "<MouseWheel>",
            self._scroll_sistema,
            add="+")

        
        entrada_card.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            entrada_card,
            text="Operación algebraica",
            font=(FUENTE, 16, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        self.selector = ctk.CTkOptionMenu(
            entrada_card,
            values=self.OPERACIONES,
            height=42,
            corner_radius=10,
            fg_color=TARJETA_SECUNDARIA,
            button_color=AZUL,
            button_hover_color=AZUL_HOVER,
            text_color=TEXTO,
            font=(FUENTE, 13),
            command=self.cambiar_operacion
        )

        self.selector.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.etiqueta_entrada = ctk.CTkLabel(
            entrada_card,
            text="Expresión matemática",
            font=(FUENTE, 13, "bold"),
            text_color=TEXTO
        )

        self.etiqueta_entrada.pack(
            anchor="w",
            padx=20,
            pady=(0, 7)
        )

        self.entrada = ctk.CTkEntry(
            entrada_card,
            height=48,
            corner_radius=10,
            border_width=1,
            border_color=BORDE,
            fg_color=TARJETA_SECUNDARIA,
            text_color=TEXTO,
            placeholder_text="Ejemplo: 2x + 3x - 5",
            placeholder_text_color=TEXTO_SECUNDARIO,
            font=(FUENTE, 14)
        )

        self.entrada.pack(
            fill="x",
            padx=20,
            pady=(0, 10)
        )

        self.entrada.bind(
            "<Return>",
            lambda evento: self.calcular()
        )

        self.entrada_sistema = ctk.CTkTextbox(
            entrada_card,
            height=110,
            corner_radius=10,
            border_width=1,
            border_color=BORDE,
            fg_color=TARJETA_SECUNDARIA,
            text_color=TEXTO,
            font=(FUENTE, 14)
        )

        self.entrada_sistema._textbox.bind(
            "<MouseWheel>",
            self._scroll_sistema,
            add="+")

        self.entrada_sistema.bind(
            "<MouseWheel>",
            self._scroll_sistema,
            add="+")

        self.ayuda = ctk.CTkLabel(
            entrada_card,
            text="Puedes escribir 2x, x^2 o 3(x + 1).",
            font=(FUENTE, 11),
            text_color=TEXTO_SECUNDARIO
        )

        self.ayuda.pack(
            anchor="w",
            padx=20,
            pady=(0, 14)
        )

        self.boton_calcular = ctk.CTkButton(
            entrada_card,
            text="Calcular",
            height=45,
            corner_radius=10,
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            text_color="white",
            font=(FUENTE, 14, "bold"),
            command=self.calcular
        )

        self.boton_calcular.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.boton_graficar = ctk.CTkButton(
            entrada_card,
            text="Graficar expresión",
            height=45,
            corner_radius=10,
            fg_color="#17243B",
            hover_color="#263650",
            text_color=TEXTO,
            font=(FUENTE, 14, "bold"),
            command=self.graficar
        )

        self.boton_graficar.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # ─────────────────────────────────────
        # RESULTADO
        # ─────────────────────────────────────

        self.resultado_card = ctk.CTkFrame(
            contenido,
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
            text="Resultado",
            font=(FUENTE, 18, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.resultado_frame = ctk.CTkFrame(
            self.resultado_card,
            fg_color="transparent"
        )

        self.resultado_frame.pack(
            fill="x",
            padx=15,
            pady=(0, 18)
        )

        # ─────────────────────────────────────
        # PROCEDIMIENTO
        # ─────────────────────────────────────

        self.pasos_card = ctk.CTkFrame(
            contenido,
            fg_color=TARJETA,
            corner_radius=16,
            border_width=1,
            border_color=BORDE
        )

        self.pasos_card.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            self.pasos_card,
            text="Procedimiento paso a paso",
            font=(FUENTE, 18, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.pasos = ctk.CTkFrame(
            self.pasos_card,
            fg_color="transparent"
        )

        self.pasos.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.cambiar_operacion("Simplificar")
        self.mostrar_mensaje_inicial()

    # ─────────────────────────────────────────
    # CAMBIAR OPERACIÓN
    # ─────────────────────────────────────────

    def cambiar_operacion(self, operacion):

        if operacion == "Resolver sistema":

            self.entrada.pack_forget()

            self.entrada_sistema.pack(
                fill="x",
                padx=20,
                pady=(0, 10)
            )

            self.etiqueta_entrada.configure(
                text="Ecuaciones del sistema"
            )

            self.ayuda.configure(
                text="Escribe una ecuación por línea."
            )

            self.boton_calcular.configure(
                text="Resolver sistema"
            )

        else:

            self.entrada_sistema.pack_forget()

            self.entrada.pack(
                fill="x",
                padx=20,
                pady=(0, 10)
            )

            self.etiqueta_entrada.configure(
                text="Expresión matemática"
            )

            ejemplos = {
                "Simplificar": "Ejemplo: 2x + 3x - 5",
                "Desarrollar": "Ejemplo: (x + 2)(x - 3)",
                "Factorizar": "Ejemplo: x^2 + 5x + 6",
                "Resolver ecuación": "Ejemplo: 2x + 5 = 13"
            }

            self.ayuda.configure(
                text=ejemplos.get(operacion, "")
            )

            self.boton_calcular.configure(
                text="Resolver ecuación"
                if operacion == "Resolver ecuación"
                else "Calcular"
            )

    # ─────────────────────────────────────────
    # CÁLCULO
    # ─────────────────────────────────────────

    def calcular(self):

        operacion = self.selector.get()

        if operacion == "Resolver sistema":

            texto = self.entrada_sistema.get(
                "1.0",
                "end"
            ).strip()

            ecuaciones = [
                linea.strip()
                for linea in texto.splitlines()
                if linea.strip()
            ]

            if len(ecuaciones) < 2:
                self.mostrar_error(
                    "Introduce al menos dos ecuaciones."
                )
                return

        else:

            texto = self.entrada.get().strip()

            if not texto:
                self.mostrar_error(
                    "Introduce una expresión matemática."
                )
                return

        self.boton_calcular.configure(
            state="disabled",
            text="Calculando..."
        )

        try:

            funciones = {
                "Simplificar": simplificar,
                "Desarrollar": desarrollar,
                "Factorizar": factorizar,
                "Resolver ecuación": resolver_ecuacion,
                "Resolver sistema": resolver_sistema
            }

            if operacion == "Resolver sistema":
                resultado, pasos = resolver_sistema(ecuaciones)
                entrada_original = "\n".join(ecuaciones)
            else:
                resultado, pasos = funciones[operacion](texto)
                entrada_original = texto
                self.ultima_expresion = convertir_expresion(texto)

            self.limpiar_frame(self.resultado_frame)
            self.limpiar_frame(self.pasos)
            self.imagenes.clear()

            self.mostrar_resultado(
                operacion,
                entrada_original,
                resultado
            )

            self.mostrar_pasos(pasos)

        except Exception as error:

            self.mostrar_error(
                "No se pudo realizar la operación.\n\n"
                f"Detalle: {error}"
            )

        finally:

            self.boton_calcular.configure(
                state="normal",
                text="Resolver sistema"
                if operacion == "Resolver sistema"
                else "Resolver ecuación"
                if operacion == "Resolver ecuación"
                else "Calcular"
            )

    # ─────────────────────────────────────────
    # RESULTADO
    # ─────────────────────────────────────────

    def mostrar_resultado(
        self,
        operacion,
        entrada,
        resultado
    ):

        ctk.CTkLabel(
            self.resultado_frame,
            text="Expresión original",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=8,
            pady=(5, 5)
        )

        if operacion == "Resolver sistema":

            self.mostrar_sistema_original(entrada)

        else:

            self.agregar_formula(
                self.resultado_frame,
                self.a_latex(entrada),
                ancho=520,
                alto=90
            )

        ctk.CTkFrame(
            self.resultado_frame,
            height=1,
            fg_color=BORDE
        ).pack(
            fill="x",
            padx=8,
            pady=12
        )

        ctk.CTkLabel(
            self.resultado_frame,
            text="Resultado obtenido",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=8,
            pady=(0, 5)
        )

        if isinstance(resultado, str):

            ctk.CTkLabel(
                self.resultado_frame,
                text=resultado,
                font=(FUENTE, 13, "bold"),
                text_color=TEXTO,
                wraplength=500,
                justify="left"
            ).pack(
                anchor="w",
                padx=8,
                pady=10
            )

        else:

            self.agregar_formula(
                self.resultado_frame,
                self.a_latex(resultado),
                ancho=520,
                alto=100
            )

        ctk.CTkLabel(
            self.resultado_frame,
            text="✓ Operación completada",
            font=(FUENTE, 12, "bold"),
            text_color=VERDE
        ).pack(
            anchor="w",
            padx=8,
            pady=(10, 0)
        )

    # ─────────────────────────────────────────
    # PROCEDIMIENTO
    # ─────────────────────────────────────────

    def mostrar_pasos(self, pasos):

        self.limpiar_frame(self.pasos)

        if not pasos:
            ctk.CTkLabel(
                self.pasos,
                text="No hay pasos detallados disponibles.",
                font=(FUENTE, 12),
                text_color=TEXTO_SECUNDARIO
            ).pack(padx=10, pady=10)

            return

        if isinstance(pasos, str):
            pasos = [pasos]

        for indice, paso in enumerate(pasos, start=1):

            tarjeta = ctk.CTkFrame(
                self.pasos,
                fg_color=TARJETA_SECUNDARIA,
                corner_radius=12,
                border_width=1,
                border_color=BORDE
            )

            tarjeta.pack(
                fill="x",
                pady=(0, 12)
            )

            encabezado = ctk.CTkFrame(
                tarjeta,
                fg_color="transparent"
            )

            encabezado.pack(
                fill="x",
                padx=15,
                pady=(14, 8)
            )

            ctk.CTkLabel(
                encabezado,
                text=str(indice),
                width=30,
                height=30,
                corner_radius=15,
                fg_color=AZUL,
                text_color="white",
                font=(FUENTE, 13, "bold")
            ).pack(
                side="left",
                padx=(0, 10)
            )

            if isinstance(paso, dict):

                titulo = paso.get(
                    "titulo",
                    f"Paso {indice}"
                )

                formula = paso.get("formula", "")
                explicacion = paso.get("explicacion", "")

            else:

                titulo = f"Paso {indice}"
                formula = ""
                explicacion = str(paso)

            ctk.CTkLabel(
                encabezado,
                text=titulo,
                font=(FUENTE, 14, "bold"),
                text_color=TEXTO,
                anchor="w",
                wraplength=430
            ).pack(
                side="left",
                fill="x",
                expand=True
            )

            if formula:

                self.agregar_formula(
                    tarjeta,
                    self.a_latex(formula),
                    ancho=500,
                    alto=80
                )

            if explicacion:

                ctk.CTkLabel(
                    tarjeta,
                    text=explicacion,
                    font=(FUENTE, 12),
                    text_color=TEXTO_SECUNDARIO,
                    justify="left",
                    anchor="w",
                    wraplength=510
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(8, 15)
                )

    # ─────────────────────────────────────────
    # LATEX
    # ─────────────────────────────────────────

    @staticmethod
    def a_latex(valor):

        if isinstance(valor, sp.Basic):
            return sp.latex(valor)

        if isinstance(valor, dict):
            if not valor:
                return r"\varnothing"

            return r"\qquad".join(
                f"{sp.latex(k)} = {sp.latex(v)}"
                for k, v in valor.items()
            )

        if isinstance(valor, (list, tuple)):
            if len(valor) == 1:
                return sp.latex(valor[0])

            return r",\quad ".join(
                sp.latex(item) for item in valor
            )

        return str(valor)

    # ─────────────────────────────────────────
    # RENDERIZADO
    # ─────────────────────────────────────────

    def agregar_formula(
        self,
        contenedor,
        formula,
        ancho=500,
        alto=75
    ):

        try:

            imagen_pil = expresion_a_imagen(formula)

            ancho_original, alto_original = imagen_pil.size

            escala = min(
                ancho / max(ancho_original, 1),
                alto / max(alto_original, 1),
                1.0
            )

            nuevo_ancho = max(
                1,
                int(ancho_original * escala)
            )

            nuevo_alto = max(
                1,
                int(alto_original * escala)
            )

            imagen_ctk = ctk.CTkImage(
                light_image=imagen_pil,
                dark_image=imagen_pil,
                size=(nuevo_ancho, nuevo_alto)
            )

            self.imagenes.append(imagen_ctk)

            ctk.CTkLabel(
                contenedor,
                text="",
                image=imagen_ctk
            ).pack(
                anchor="center",
                padx=8,
                pady=5
            )

        except Exception as error:

            print(f"Error al renderizar fórmula: {error}")

            ctk.CTkLabel(
                contenedor,
                text=formula,
                font=("Consolas", 14),
                text_color=TEXTO,
                wraplength=500
            ).pack(
                anchor="w",
                padx=12,
                pady=8
            )

    # ─────────────────────────────────────────
    # MENSAJES
    # ─────────────────────────────────────────

    def mostrar_mensaje_inicial(self):

        self.limpiar_frame(self.resultado_frame)
        self.limpiar_frame(self.pasos)

        ctk.CTkLabel(
            self.resultado_frame,
            text="f(x)",
            font=(FUENTE, 27, "bold"),
            text_color=AZUL
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self.resultado_frame,
            text="Tu resultado aparecerá aquí.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(pady=(0, 15))

        ctk.CTkLabel(
            self.pasos,
            text="Selecciona una operación e introduce una expresión.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO,
            wraplength=500
        ).pack(
            anchor="w",
            padx=10,
            pady=12
        )

    def mostrar_error(self, mensaje):

        self.limpiar_frame(self.resultado_frame)
        self.limpiar_frame(self.pasos)
        self.imagenes.clear()

        ctk.CTkLabel(
            self.resultado_frame,
            text="No se pudo completar la operación",
            font=(FUENTE, 15, "bold"),
            text_color=ROJO
        ).pack(
            anchor="w",
            padx=10,
            pady=(12, 5)
        )

        ctk.CTkLabel(
            self.resultado_frame,
            text=mensaje,
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO,
            wraplength=500,
            justify="left"
        ).pack(
            anchor="w",
            padx=10,
            pady=(0, 15)
        )

    # ─────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────

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

    def _scroll_sistema(self, event):

        self.panel._parent_canvas.yview_scroll(
            int(-event.delta / 6),
            "units"
        )

        return "break"


    def mostrar_sistema_original(self, entrada):

        for linea in entrada.splitlines():

            if "=" not in linea:
                continue

            izquierda, derecha = linea.split("=", 1)

            izquierda = convertir_expresion(izquierda)
            derecha = convertir_expresion(derecha)

            formula = sp.latex(
                sp.Eq(izquierda, derecha, evaluate=False)
            )

            self.agregar_formula(
                self.resultado_frame,
                formula,
                ancho=520,
                alto=65
            )
    
    def graficar(self):

        operacion = self.selector.get()

        if operacion == "Resolver sistema":
            from tkinter import messagebox

            messagebox.showwarning(
                "Operación no compatible",
                "La gráfica de sistemas de ecuaciones "
                "se implementará por separado."
            )
            return

        texto = self.entrada.get().strip()

        if not texto:
            from tkinter import messagebox

            messagebox.showwarning(
                "Sin expresión",
                "Introduce una expresión matemática."
            )
            return

        try:
            expresion = convertir_expresion(texto)

            if not isinstance(expresion, sp.Expr):
                raise ValueError("La expresión no es válida.")

            variables = expresion.free_symbols

            if len(variables) != 1:
                raise ValueError(
                    "Por ahora, las gráficas 2D requieren "
                    "una sola variable, por ejemplo x."
                )

            variable = next(iter(variables))

            if variable.name != "x":
                expresion = expresion.subs(
                    variable,
                    sp.Symbol("x")
                )

            GraphView(
                self.parent,
                [("Expresión original", expresion)],
                titulo="Gráfica algebraica"
            )

        except Exception as error:
            from tkinter import messagebox

            messagebox.showerror(
                "Error al graficar",
                str(error)
            )
