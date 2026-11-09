import customtkinter as ctk


class GraphSelector:
    """Ventana reutilizable para elegir el tipo de visualización gráfica."""

    def __init__(
        self,
        parent,
        *,
        fondo,
        texto,
        texto_secundario,
        fuente,
        color_2d,
        hover_2d,
        color_3d,
        hover_3d,
        on_2d,
        on_3d,
        on_ar,
        titulo="Seleccionar visualización",
        descripcion="¿Cómo deseas explorar tu función?",
        color_ar="#164E63",
        hover_ar="#155E75",
    ):
        self.ventana = ctk.CTkToplevel(parent)
        self.ventana.title(titulo)
        self.ventana.geometry("720x320")
        self.ventana.configure(fg_color=fondo)
        self.ventana.attributes("-topmost", True)
        self.ventana.transient(parent)
        self.ventana.grab_set()
        self.ventana.resizable(False, False)

        self._centrar_ventana()
        self._crear_contenido(
            texto=texto,
            texto_secundario=texto_secundario,
            fuente=fuente,
            color_2d=color_2d,
            hover_2d=hover_2d,
            color_3d=color_3d,
            hover_3d=hover_3d,
            color_ar=color_ar,
            hover_ar=hover_ar,
            on_2d=on_2d,
            on_3d=on_3d,
            on_ar=on_ar,
            titulo=titulo,
            descripcion=descripcion,
        )

    def _centrar_ventana(self):
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() - ancho) // 2
        y = (self.ventana.winfo_screenheight() - alto) // 2
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _crear_contenido(
        self,
        *,
        texto,
        texto_secundario,
        fuente,
        color_2d,
        hover_2d,
        color_3d,
        hover_3d,
        color_ar,
        hover_ar,
        on_2d,
        on_3d,
        on_ar,
        titulo,
        descripcion,
    ):
        ctk.CTkLabel(
            self.ventana,
            text=titulo,
            font=(fuente, 22, "bold"),
            text_color=texto,
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            self.ventana,
            text=descripcion,
            font=(fuente, 13),
            text_color=texto_secundario,
        ).pack(pady=(0, 25))

        botones = ctk.CTkFrame(self.ventana, fg_color="transparent")
        botones.pack(fill="x", padx=25, pady=(0, 20))

        opciones = (
            ("GRÁFICA 2D", color_2d, hover_2d, on_2d),
            ("GRÁFICA 3D", color_3d, hover_3d, on_3d),
            ("CÁMARA AR", color_ar, hover_ar, on_ar),
        )

        for indice, (etiqueta, color, hover, comando) in enumerate(opciones):
            padx = (0, 6) if indice == 0 else ((6, 0) if indice == 2 else 6)
            ctk.CTkButton(
                botones,
                text=etiqueta,
                height=110,
                corner_radius=12,
                fg_color=color,
                hover_color=hover,
                font=(fuente, 15, "bold"),
                command=comando,
            ).pack(
                side="left",
                fill="both",
                expand=True,
                padx=padx,
            )
