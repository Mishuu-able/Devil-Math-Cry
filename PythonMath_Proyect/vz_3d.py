
import sympy as sp

from mathematics.graphics.graph_engine import generar_datos_3d
from visualization.graph_3D import Graph3D


x, y = sp.symbols("x y")

expresion = x**2 + y**2

datos = generar_datos_3d(
    expresion,
    x_min=-5,
    x_max=5,
    y_min=-5,
    y_max=5,
    puntos=100
)

visualizador = Graph3D()
visualizador.mostrar_superficie(datos)
