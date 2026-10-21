
import customtkinter as ctk
import sympy as sp

from mathematics.calculus.limits import calcular_limite
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


class LimitsView:
    def __init__(self, parent):
        self.parent = parent
        self.imagenes = []

        self.crear_interfaz()

    # ─────────────────────────────────────────
    # INTERFAZ PRINCIPAL
    # ─────────────────────────────────────────

    def crear_interfaz(self):
        self.contenedor = ctk.CTkFrame(
            self.parent,
            fg_color=FONDO,
            corner_radius=0)

        self.contenedor.pack(
            fill="both",
            expand=True)

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
            text="Cálculo de límites",
            font=(FUENTE, 27, "bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            encabezado,
            text=(
                "Evalúa límites y comprende cada paso "
                "del procedimiento matemático."
            ),
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
            text="Expresión matemática",
            font=(FUENTE, 16, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 8)
        )

        ctk.CTkLabel(
            entrada_card,
            text=(
                "Escribe la función y el valor al que tiende x.\n"
                "Ejemplo: (x^2 - 4)/(x - 2), cuando x tiende a 2."
            ),
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO,
            justify="left"
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
            placeholder_text="Ejemplo: (x^2 - 4)/(x - 2)",
            placeholder_text_color=TEXTO_SECUNDARIO,
            font=(FUENTE, 14)
        )
        self.entrada.pack(
            fill="x",
            padx=20,
            pady=(0, 12)
        )

        self.entrada.bind(
            "<Return>",
            lambda evento: self.entrada_punto.focus_set()
        )

        ctk.CTkLabel(
            entrada_card,
            text="Valor al que tiende x",
            font=(FUENTE, 13, "bold"),
            text_color=TEXTO
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 7)
        )

        self.entrada_punto = ctk.CTkEntry(
            entrada_card,
            height=45,
            corner_radius=10,
            border_width=1,
            border_color=BORDE,
            fg_color=TARJETA_SECUNDARIA,
            text_color=TEXTO,
            placeholder_text="Ejemplo: 2, 0, oo o -oo",
            placeholder_text_color=TEXTO_SECUNDARIO,
            font=(FUENTE, 14)
        )
        self.entrada_punto.pack(
            fill="x",
            padx=20,
            pady=(0, 14)
        )

        self.entrada_punto.bind(
            "<Return>",
            lambda evento: self.calcular()
        )

        self.boton_calcular = ctk.CTkButton(
            entrada_card,
            text="Calcular límite",
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
        # TARJETA DEL PROCEDIMIENTO
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

        # Este frame NO tiene otro scroll.
        # El scroll general mueve toda la interfaz.
        self.pasos = ctk.CTkFrame(
            self.pasos_card,
            fg_color="transparent"
        )
        self.pasos.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.mostrar_mensaje_inicial()

    # ─────────────────────────────────────────
    # CALCULAR LÍMITE
    # ─────────────────────────────────────────

    def calcular(self):
        expresion = self.entrada.get().strip()
        punto = self.entrada_punto.get().strip()

        if not expresion or not punto:
            self.mostrar_error(
                "Introduce una función y el valor al que tiende x."
            )
            return

        self.boton_calcular.configure(
            state="disabled",
            text="Calculando..."
        )

        try:
            funcion, punto, resultado, pasos = calcular_limite(
                expresion,
                punto
            )

            # Destruir los widgets anteriores antes de liberar
            # las referencias a sus imágenes.
            self.limpiar_frame(self.resultado_frame)
            self.limpiar_frame(self.pasos)
            self.imagenes.clear()

            self.mostrar_resultado(
                funcion,
                punto,
                resultado
            )
            self.mostrar_pasos(pasos)

        except Exception as error:
            self.mostrar_error(
                "No se pudo calcular el límite.\n"
                "Revisa la expresión y el valor de x.\n\n"
                f"Detalle: {error}"
            )

        finally:
            self.boton_calcular.configure(
                state="normal",
                text="Calcular límite"
            )

    # ─────────────────────────────────────────
    # MOSTRAR RESULTADO
    # ─────────────────────────────────────────

    def mostrar_resultado(self, funcion, punto, resultado):
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

        self.agregar_formula(
            self.resultado_frame,
            rf"f(x) = {sp.latex(funcion)}",
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
            text="Límite obtenido",
            font=(FUENTE, 12),
            text_color=TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=8,
            pady=(0, 5)
        )

        formula_limite = (
            rf"\lim_{{x\to {sp.latex(punto)}}}"
            rf"\left({sp.latex(funcion)}\right)"
            rf" = {sp.latex(resultado)}"
        )

        self.agregar_formula(
            self.resultado_frame,
            formula_limite,
            ancho=520,
            alto=90
        )

        ctk.CTkLabel(
            self.resultado_frame,
            text="✓ Límite calculado",
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
                text=(
                    "El cálculo terminó, pero no hay pasos "
                    "detallados disponibles para esta expresión."
                ),
                font=(FUENTE, 12),
                text_color=TEXTO_SECUNDARIO,
                wraplength=500,
                justify="left"
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

            ctk.CTkLabel(
                encabezado,
                text=paso.get("titulo", f"Paso {indice}"),
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
                    alto=75
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

    # ─────────────────────────────────────────
    # RENDERIZAR FÓRMULAS
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
                ancho / ancho_original,
                alto / alto_original,
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
            text="lim f(x)",
            font=(FUENTE, 25, "bold"),
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
            text=(
                "Introduce una función y el valor al que tiende x "
                "para consultar el procedimiento."
            ),
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
    # MOSTRAR ERRORES
    # ─────────────────────────────────────────

    def mostrar_error(self, mensaje):
        self.limpiar_frame(self.resultado_frame)
        self.limpiar_frame(self.pasos)
        self.imagenes.clear()

        ctk.CTkLabel(
            self.resultado_frame,
            text="No se pudo completar el cálculo",
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
