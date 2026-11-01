
import customtkinter as ctk
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from mathematics.graphics.graph_engine import generar_datos_2d


FONDO = "#0B1120"
TARJETA = "#111C30"
TEXTO = "#F1F5F9"
AZUL = "#3B82F6"


class GraphView:

    def __init__(self, parent, expresiones, titulo="Gráfica matemática"):
        self.parent = parent
        self.expresiones = expresiones

        self.ventana = ctk.CTkToplevel(parent)
        self.ventana.title(titulo)
        self.ventana.geometry("850x600")
        self.ventana.configure(fg_color=FONDO)

        self.crear_interfaz()

    def crear_interfaz(self):

        encabezado = ctk.CTkFrame(
            self.ventana,
            fg_color="transparent"
        )
        encabezado.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            encabezado,
            text="Visualización gráfica",
            font=("Poppins", 22, "bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        self.figura, self.ax = plt.subplots(
            figsize=(8, 5),
            dpi=100
        )

        self.figura.patch.set_facecolor(TARJETA)
        self.ax.set_facecolor(TARJETA)

        self.ax.axhline(0, linewidth=0.8, color="gray")
        self.ax.axvline(0, linewidth=0.8, color="gray")

        self.ax.grid(
            True,
            linestyle="--",
            alpha=0.2
        )

        self.ax.set_xlabel("X", color=TEXTO)
        self.ax.set_ylabel("Y", color=TEXTO)
        self.ax.tick_params(colors=TEXTO)

        for borde in self.ax.spines.values():
            borde.set_color("#64748B")

        for nombre, expresion in self.expresiones:

            datos = generar_datos_2d(expresion)

            self.ax.plot(
                datos["x"],
                datos["y"],
                label=nombre,
                linewidth=2
            )

        self.ax.legend(facecolor=TARJETA, labelcolor=TEXTO)
        self.figura.tight_layout()

        self.canvas = FigureCanvasTkAgg(
            self.figura,
            master=self.ventana
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.ventana.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar
        )

    def cerrar(self):
        plt.close(self.figura)
        self.ventana.destroy()
