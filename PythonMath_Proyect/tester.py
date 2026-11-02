
import customtkinter as ctk
import sympy as sp

from ui.graph_view import GraphView


# ============================================================
# CONFIGURACIÓN
# ============================================================

ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.geometry("400x200")
root.title("Devil Math Cry - Graph Tests")

x = sp.Symbol("x")


# ============================================================
# FUNCIONES DE PRUEBA
# ============================================================

funciones = [
    ("Hueco", (x**2 - 4) / (x - 2)),
    ("Salto", sp.Piecewise((0, x < 2), (1, True))),
    ("Asíntota", 1 / (x - 2))
]


# ============================================================
# ABRIR GRÁFICA
# ============================================================

GraphView(
    root,
    funciones,
    titulo="Prueba de discontinuidades"
)

root.mainloop()
