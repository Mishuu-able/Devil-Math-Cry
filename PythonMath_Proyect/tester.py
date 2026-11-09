import sympy as sp

from mathematics.parser import convertir_expresion, X
from mathematics.functions.evaluator import evaluar_funcion
from mathematics.functions.analysis import analizar_funcion
from mathematics.functions.operations import operar_funciones
from mathematics.calculus.limits import calcular_limite


# ============================================================
# PRUEBA 1: IDENTIDAD DE LA VARIABLE
# ============================================================

print("\n--- IDENTIDAD DE X ---")

expresion = convertir_expresion("sin(x)")

print("Expresión:", expresion)
print("Variables:", expresion.free_symbols)
print("¿Utiliza X compartida?", X in expresion.free_symbols)


# ============================================================
# PRUEBA 2: EVALUACIÓN
# ============================================================

print("\n--- EVALUACIÓN ---")

resultado = evaluar_funcion(
    convertir_expresion("sin(x)"),
    [0, sp.pi / 2]
)

for dato in resultado:
    print(dato)


# ============================================================
# PRUEBA 3: ANÁLISIS
# ============================================================

print("\n--- ANÁLISIS ---")

funcion = convertir_expresion("cos(x)")

print(analizar_funcion(funcion))


# ============================================================
# PRUEBA 4: OPERACIONES
# ============================================================

print("\n--- COMPOSICIÓN ---")

f = convertir_expresion("sin(x)")
g = convertir_expresion("2*x")

resultado = operar_funciones(f, g, "f(g(x))")

print(resultado["resultado"])


# ============================================================
# PRUEBA 5: LÍMITES
# ============================================================

print("\n--- LÍMITE ---")

funcion, punto, limite, pasos = calcular_limite(
    "sin(x)/x",
    0
)

print("Resultado:", limite)