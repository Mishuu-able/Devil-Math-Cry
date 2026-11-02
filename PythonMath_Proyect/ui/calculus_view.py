import customtkinter as ctk
import sympy as sp
from tkinter import messagebox

from mathematics.calculus.derivates import calcular_derivada
from mathematics.renderer import expresion_a_imagen
from ui.graph_view import GraphView
from mathematics.graphics.graph_engine import generar_datos_3d
from visualization.graph_3D import Graph3D
from visualization.graph_3D import Graph3D, detectar_camara
from ui.camera_view import CameraView


# ============================================================
# PALETA CENTRALIZADA - MÓDULO CÁLCULO
# ============================================================

from ui.theme import (
    CALCULUS_BG as FONDO,
    CALCULUS_CARD as TARJETA,
    CALCULUS_CARD_SECONDARY as TARJETA_SECUNDARIA,
    CALCULUS_ERROR_TEXT,

    CALCULUS_PRIMARY as AZUL,
    CALCULUS_PRIMARY_HOVER as AZUL_HOVER,

    CALCULUS_TEXT as TEXTO,
    CALCULUS_TEXT_SECONDARY as TEXTO_SECUNDARIO,

    CALCULUS_BORDER as BORDE,

    CALCULUS_SUCCESS as VERDE,
    CALCULUS_ERROR as ROJO,

    FONT_FAMILY as FUENTE,

    CALCULUS_GRAPH_2D as GRAPH_2D_COLOR,
    CALCULUS_GRAPH_2D_HOVER as GRAPH_2D_HOVER,

    CALCULUS_GRAPH_3D as GRAPH_3D_COLOR,
    CALCULUS_GRAPH_3D_HOVER as GRAPH_3D_HOVER
)

from ui.theme import CALCULUS_ERROR_TEXT as ERROR_TEXT_COLOR


class CalculusView:
    def __init__(self, parent):
        self.parent = parent
        self.imagenes = []
        self.ultima_funcion = None
        self.ultima_derivada = None

        self.crear_interfaz()

    # ─────────────────────────────────────────
    # INTERFAZ PRINCIPAL
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

        # Encabezado fijo
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
            text="Cálculo diferencial",
            font=(FUENTE, 27, "bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            encabezado,
            text="Calcula derivadas y comprende el procedimiento paso a paso.",
            font=(FUENTE, 13),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # ÚNICO contenedor desplazable
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
        contenido.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        # ─────────────────────────────────────
        # TARJETA DE ENTRADA
        # ─────────────────────────────────────

        entrada_card = ctk.CTkFrame(
            contenido,
            fg_color=TARJETA,
            corner_radius=16,
            border_width=1,
            border_color=BORDE
        )
        entrada_card.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            entrada_card,
            text="Función matemática",
            font=(FUENTE, 16, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            entrada_card,
            text="Escribe una función de x. Por ejemplo: x^2 + 3x + 2",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 12)
        )

        self.entrada = ctk.CTkEntry(
            entrada_card,
            height=48,
            corner_radius=10,
            border_width=1,
            border_color=BORDE,
            fg_color=TARJETA_SECUNDARIA,
            text_color=TEXTO,
            placeholder_text="Ejemplo: 2x^3 + sin(x)",
            placeholder_text_color=TEXTO_SECUNDARIO,
            font=(FUENTE, 15)
        )
        self.entrada.pack(
            fill="x",
            padx=20,
            pady=(0, 14)
        )

        self.entrada.bind(
            "<Return>",
            lambda evento: self.calcular()
        )

        self.boton_calcular = ctk.CTkButton(
            entrada_card,
            text="Calcular derivada",
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
            text="Graficar función y derivada",
            height=45,
            corner_radius=10,
            fg_color= TARJETA_SECUNDARIA,
            hover_color= BORDE,
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
        # TARJETA DEL RESULTADO
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
        # CONTENEDOR DE LOS PASOS
        # IMPORTANTE: se crea ANTES de mostrar
        # el mensaje inicial.
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

        # Se llama DESPUÉS de crear todos los frames.
        self.mostrar_mensaje_inicial()

    # ─────────────────────────────────────────
    # CALCULAR DERIVADA
    # ─────────────────────────────────────────

    def calcular(self):
        expresion = self.entrada.get().strip()

        if not expresion:
            self.mostrar_error(
                "Escribe una función antes de calcular."
            )
            return

        self.boton_calcular.configure(
            state="disabled",
            text="Calculando..."
        )

        try:
            funcion, derivada, pasos = calcular_derivada(
                expresion
            )

            # Eliminar los widgets anteriores antes de
            # liberar las referencias a las imágenes.
            self.limpiar_frame(self.resultado_frame)
            self.limpiar_frame(self.pasos)

            self.imagenes.clear()

            self.mostrar_resultado(funcion, derivada)
            self.mostrar_pasos(pasos)
            self.ultima_funcion = funcion
            self.ultima_derivada = derivada

        except Exception as error:
            self.mostrar_error(
                f"No se pudo calcular la derivada.\n"
                f"Revisa la función e inténtalo de nuevo.\n\n"
                f"Detalle: {error}"
            )

        finally:
            self.boton_calcular.configure(
                state="normal",
                text="Calcular derivada"
            )

    # ─────────────────────────────────────────
    # MOSTRAR RESULTADO
    # ─────────────────────────────────────────

    def mostrar_resultado(self, funcion, derivada):
        self.limpiar_frame(self.resultado_frame)

        ctk.CTkLabel(
            self.resultado_frame,
            text="Función original",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=8,
            pady=(5, 5)
        )

        formula_original = rf"f\; (x) = {sp.latex(funcion)}"

        self.agregar_formula(
            self.resultado_frame,
            formula_original,
            ancho=520,
            alto=80
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
            text="Derivada obtenida",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=8,
            pady=(0, 5)
        )

        formula_derivada = rf"f'(x) = {sp.latex(derivada)}"
        
        self.agregar_formula(
            self.resultado_frame,
            formula_derivada,
            ancho=520,
            alto=80)

        ctk.CTkLabel(
            self.resultado_frame,
            text="✓ Derivada calculada correctamente",
            font=(FUENTE, 12, "bold"),
            text_color=VERDE
        ).pack(
            anchor="w",
            padx=8,
            pady=(10, 0)
        )

    # ─────────────────────────────────────────
    # MOSTRAR PROCEDIMIENTO
    # ─────────────────────────────────────────

    def mostrar_pasos(self, pasos):
        self.limpiar_frame(self.pasos)

        if not pasos:
            ctk.CTkLabel(
                self.pasos,
                text="No hay pasos detallados disponibles para esta función.",
                font=(FUENTE, 12),
                text_color=TEXTO_SECUNDARIO,
                wraplength=500
            ).pack(
                anchor="w",
                padx=10,
                pady=10
            )
            return

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

            numero = ctk.CTkLabel(
                encabezado,
                text=str(indice),
                width=30,
                height=30,
                corner_radius=15,
                fg_color=AZUL,
                text_color="white",
                font=(FUENTE, 13, "bold")
            )
            numero.pack(
                side="left",
                padx=(0, 10)
            )

            titulo = paso.get(
                "titulo",
                f"Paso {indice}"
            )

            ctk.CTkLabel(
                encabezado,
                text=titulo,
                font=(FUENTE, 14, "bold"),
                text_color=TEXTO,
                anchor="w",
                justify="left",
                wraplength=430
            ).pack(
                side="left",
                fill="x",
                expand=True
            )

            formula = paso.get("formula", "")

            if formula:
                self.agregar_formula(
                    tarjeta,
                    formula,
                    ancho=500,
                    alto=65
                )

            explicacion = paso.get("explicacion", "")

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
            else:
                ctk.CTkFrame(
                    tarjeta,
                    height=8,
                    fg_color="transparent"
                ).pack()

    # ─────────────────────────────────────────
    # RENDERIZAR FÓRMULAS MATEMÁTICAS
    # ─────────────────────────────────────────

    

    def agregar_formula(
        self,
        contenedor,
        formula,
        ancho=500,
        alto=65
    ):
        try:
            imagen_pil = expresion_a_imagen(formula)

            # Conservar la proporción original de la fórmula.
            ancho_original, alto_original = imagen_pil.size

            escala = min(
                ancho / ancho_original,
                alto / alto_original,
                1.0
            )

            nuevo_ancho = max(1, int(ancho_original * escala))
            nuevo_alto = max(1, int(alto_original * escala))

            imagen_ctk = ctk.CTkImage(
                light_image=imagen_pil,
                dark_image=imagen_pil,
                size=(nuevo_ancho, nuevo_alto)
            )

            self.imagenes.append(imagen_ctk)

            etiqueta = ctk.CTkLabel(
                contenedor,
                text="",
                image=imagen_ctk
            )

            etiqueta.pack(
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
                wraplength=500,
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=8
            )



    # ─────────────────────────────────────────
    # MENSAJE INICIAL
    # ─────────────────────────────────────────

    def mostrar_mensaje_inicial(self):
        self.limpiar_frame(self.resultado_frame)
        self.limpiar_frame(self.pasos)

        ctk.CTkLabel(
            self.resultado_frame,
            text="f(x)  →  f'(x)",
            font=(FUENTE, 24, "bold"),
            text_color=AZUL
        ).pack(
            pady=(15, 5)
        )

        ctk.CTkLabel(
            self.resultado_frame,
            text="Tu resultado aparecerá aquí.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            pady=(0, 15)
        )

        ctk.CTkLabel(
            self.pasos,
            text="Introduce una función y pulsa «Calcular derivada» "
                 "para ver el procedimiento.",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO,
            wraplength=500,
            justify="left"
        ).pack(
            anchor="w",
            padx=10,
            pady=12
        )


    # ─────────────────────────────────────────
    # UTILIDAD: LIMPIAR CONTENEDORES
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

    def graficar(self):

        if self.ultima_funcion is None:
            messagebox.showwarning(
                "Sin resultados",
                "Primero debes calcular una derivada."
            )
            return

        self.ventana_graficas = ctk.CTkToplevel(self.parent)

        self.ventana_graficas.title("Seleccionar visualización")
        self.ventana_graficas.geometry("720x320")
        self.ventana_graficas.configure(fg_color=FONDO)

        # Mantener encima de la aplicación
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

        self.ventana_graficas.geometry(f"{ancho}x{alto}+{x}+{y}")

        # Encabezado
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


        # ======================================
        # CONTENEDOR DE BOTONES
        # ======================================

        botones = ctk.CTkFrame(
            self.ventana_graficas,
            fg_color="transparent"
        )

        botones.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        # ======================================
        # GRÁFICA 2D
        # ======================================

        ctk.CTkButton(
            botones,
            text="GRÁFICA 2D",
            height=110,
            corner_radius=12,
            fg_color=GRAPH_2D_COLOR,
            hover_color=GRAPH_2D_HOVER,
            font=(FUENTE, 15, "bold"),
            command=self.abrir_grafica_2d
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 6)
        )

        # ======================================
        # GRÁFICA 3D
        # ======================================

        ctk.CTkButton(
            botones,
            text="GRÁFICA 3D",
            height=110,
            corner_radius=12,
            fg_color=GRAPH_3D_COLOR,
            hover_color=GRAPH_3D_HOVER,
            font=(FUENTE, 15, "bold"),
            command=self.abrir_grafica_3d
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        # ======================================
        # CÁMARA AR
        # ======================================

        ctk.CTkButton(
            botones,
            text="CÁMARA AR",
            height=110,
            corner_radius=12,
            fg_color="#164E63",
            hover_color="#155E75",
            font=(FUENTE, 15, "bold"),
            command=self.abrir_camara_ar
        ).pack(
            side="right",
            fill="both",
            expand=True,
            padx=(6, 0)
        )


    def abrir_grafica_2d(self):

        self.ventana_graficas.destroy()

        GraphView(
            self.parent,
            [
                ("Función original", self.ultima_funcion),
                ("Derivada", self.ultima_derivada)
            ],
            titulo="Cálculo diferencial - 2D"
        )


    def abrir_grafica_3d(self):

        self.ventana_graficas.destroy()

        try:
            datos = generar_datos_3d(
                self.ultima_funcion
            )

            visor = Graph3D(
                modo_debug=True)

            visor.mostrar_superficie(datos)

        except Exception as error:
            messagebox.showerror(
                "Error de visualización 3D",
                f"No se pudo abrir el visor.\n\n{error}"
            )
    
    def abrir_camara_ar(self):

        try:

            datos = generar_datos_3d(
                self.ultima_funcion
            )

            ventana = ctk.CTkToplevel(self.parent)

            ventana.title("Devil Math Cry - Realidad Aumentada")
            ventana.geometry("1000x750")
            ventana.configure(fg_color=FONDO)
            ventana.minsize(700, 500)

            visor = CameraView(
                ventana,
                datos
            )

            visor.iniciar()

        except Exception as error:

            messagebox.showerror(
                "Error de cámara AR",
                f"No se pudo iniciar la visualización.\n\n{error}"
            )

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en el área de resultados."""
        self.limpiar_frame(self.resultado_frame)

        ctk.CTkLabel(
            self.resultado_frame,
            text=mensaje,
            font=("Poppins", 14),
            text_color= ERROR_TEXT_COLOR,
            wraplength=500,
            justify="center"
        ).pack(
            padx=12,
            pady=15
        )
