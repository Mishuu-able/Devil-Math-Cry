
import customtkinter as ctk
from ui.calculus_view import CalculusView
from ui.limits_view import LimitsView


# ============================================================
# CONFIGURACIÓN
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# VENTANA PRINCIPAL
# ============================================================

app = ctk.CTk()

app.title("Devil Math Cry")
app.geometry("1000x650")
app.minsize(800, 500)


# ============================================================
# CONTENEDOR PRINCIPAL
# ============================================================

main_container = ctk.CTkFrame(
    app,
    corner_radius=0
)

main_container.pack(
    fill="both",
    expand=True
)


# ============================================================
# MENÚ LATERAL
# ============================================================

sidebar = ctk.CTkFrame(
    main_container,
    width=220,
    corner_radius=0
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


# ============================================================
# TÍTULO DEL MENÚ
# ============================================================

logo = ctk.CTkLabel(
    sidebar,
    text="Devil Math Cry",
    font=ctk.CTkFont(
        size=26,
        weight="bold"
    )
)

logo.pack(
    pady=(35, 5)
)


subtitle = ctk.CTkLabel(
    sidebar,
    text="Matemáticas Universitarias",
    font=ctk.CTkFont(size=11)
)

subtitle.pack(
    pady=(0, 35)
)


# ============================================================
# FUNCIONES DEL MENÚ
# ============================================================


def limpiar_modulo():
    for widget in module_container.winfo_children():
        widget.destroy()

def ocultar_bienvenida():
    header.pack_forget()

    content.configure(fg_color="#0B1120")
    module_container.configure(fg_color="#0B1120")


def mostrar_calculo():
    ocultar_bienvenida()
    limpiar_modulo()
    CalculusView(module_container)


def mostrar_limites():
    ocultar_bienvenida()
    limpiar_modulo()
    LimitsView(module_container)


def mostrar_algebra():
    ocultar_bienvenida()
    limpiar_modulo()

    vista = ctk.CTkFrame(
        module_container,
        fg_color="#0B1120",
        corner_radius=0
    )
    vista.pack(fill="both", expand=True)

    ctk.CTkLabel(
        vista,
        text="Álgebra",
        font=("Poppins", 27, "bold"),
        text_color="#F1F5F9"
    ).pack(anchor="w", padx=30, pady=(24, 12))


def mostrar_funciones():
    ocultar_bienvenida()
    limpiar_modulo()

    vista = ctk.CTkFrame(
        module_container,
        fg_color="#0B1120",
        corner_radius=0
    )
    vista.pack(fill="both", expand=True)

    ctk.CTkLabel(
        vista,
        text="Funciones",
        font=("Poppins", 27, "bold"),
        text_color="#F1F5F9"
    ).pack(anchor="w", padx=30, pady=(24, 12))


def mostrar_ejercicios():
    ocultar_bienvenida()
    limpiar_modulo()

    vista = ctk.CTkFrame(
        module_container,
        fg_color="#0B1120",
        corner_radius=0
    )
    vista.pack(fill="both", expand=True)

    ctk.CTkLabel(
        vista,
        text="Ejercicios",
        font=("Poppins", 27, "bold"),
        text_color="#F1F5F9"
    ).pack(anchor="w", padx=30, pady=(24, 12))



# ============================================================
# BOTONES
# ============================================================

boton_algebra = ctk.CTkButton(
    sidebar,
    text="Álgebra",
    height=45,
    command=mostrar_algebra
)

boton_algebra.pack(
    padx=20,
    pady=8,
    fill="x"
)


boton_calculo = ctk.CTkButton(
    sidebar,
    text="Cálculo",
    height=45,
    command=mostrar_calculo
)

boton_calculo.pack(
    padx=20,
    pady=8,
    fill="x"
)


boton_funciones = ctk.CTkButton(
    sidebar,
    text="Funciones",
    height=45,
    command=mostrar_funciones
)

boton_funciones.pack(
    padx=20,
    pady=8,
    fill="x"
)


boton_ejercicios = ctk.CTkButton(
    sidebar,
    text="Ejercicios",
    height=45,
    command=mostrar_ejercicios
)

boton_ejercicios.pack(
    padx=20,
    pady=8,
    fill="x"
)

boton_limites = ctk.CTkButton(
    sidebar,
    text="Límites",
    command=mostrar_limites
)

boton_limites.pack(
    padx=20,
    pady=5,
    fill="x"
)


#
# ============================================================
# ÁREA DE CONTENIDO
# ============================================================

content = ctk.CTkFrame(
    main_container,
    corner_radius=0,
    fg_color="#212121"
)

content.pack(
    side="right",
    fill="both",
    expand=True,
    padx=0,
    pady=0
)

# ============================================================
# ENCABEZADO (NO SE DESTRUYE AL CAMBIAR DE MÓDULO)
# ============================================================

header = ctk.CTkFrame(
    content,
    fg_color="transparent"
)

header.pack(fill="x")

titulo_contenido = ctk.CTkLabel(
    header,
    text="Bienvenido a Devil Math Cry",
    font=ctk.CTkFont(size=32, weight="bold")
)

titulo_contenido.pack(pady=(30, 20))

descripcion = ctk.CTkLabel(
    header,
    text=(
        "Una herramienta para estudiar "
        "matemáticas universitarias.\n\n"
        "Selecciona un módulo del menú lateral."
    ),
    font=ctk.CTkFont(size=18),
    justify="center"
)

descripcion.pack(pady=20)

# ============================================================
# CONTENEDOR EXCLUSIVO PARA LOS MÓDULOS
# ============================================================

module_container = ctk.CTkFrame(
    content,
    fg_color="transparent",
    corner_radius=0
)

module_container.pack(
    fill="both",
    expand=True,
    padx=0,
    pady=0
)

# ============================================================
# EJECUTAR
# ============================================================

app.mainloop()
