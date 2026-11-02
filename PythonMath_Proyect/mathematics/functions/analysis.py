
import sympy as sp

from sympy.calculus.util import (
    continuous_domain,
    function_range
)


def analizar_dominio(expresion):
    """Calcula el dominio real de una función."""

    x = sp.Symbol("x")

    try:
        return continuous_domain(
            expresion,
            x,
            sp.S.Reals
        )
    except Exception:
        return None


def analizar_rango(expresion):
    """Calcula el recorrido real de una función."""

    x = sp.Symbol("x")

    try:
        return function_range(
            expresion,
            x,
            sp.S.Reals
        )
    except Exception:
        return None


def analizar_raices(expresion):
    """Calcula las raíces reales de una función."""

    x = sp.Symbol("x")

    try:
        return sp.solveset(
            expresion,
            x,
            domain=sp.S.Reals
        )
    except Exception:
        return None


def analizar_interseccion_y(expresion):
    """Calcula la intersección con el eje Y."""

    x = sp.Symbol("x")

    dominio = analizar_dominio(expresion)

    if dominio is None:
        return None

    pertenece = dominio.contains(0)

    if pertenece is not sp.S.true:
        return None

    try:
        return sp.simplify(expresion.subs(x, 0))
    except Exception:
        return None


def analizar_paridad(expresion):
    """Determina si una función es par, impar o ninguna."""

    x = sp.Symbol("x")

    diferencia_par = sp.simplify(
        expresion.subs(x, -x) - expresion
    )

    diferencia_impar = sp.simplify(
        expresion.subs(x, -x) + expresion
    )

    if diferencia_par == 0:
        return "Par"

    if diferencia_impar == 0:
        return "Impar"

    return "Ninguna"


def analizar_funcion(expresion):
    """
    Ejecuta el análisis general de una función.

    Cada propiedad se calcula independientemente
    para evitar que un fallo impida obtener las demás.
    """

    return {
        "dominio": analizar_dominio(expresion),
        "rango": analizar_rango(expresion),
        "raices": analizar_raices(expresion),
        "interseccion_y": analizar_interseccion_y(expresion),
        "paridad": analizar_paridad(expresion)
    }


def generar_explicaciones(expresion, analisis):
    """
    Genera explicaciones matemáticas para las propiedades
    calculadas de una función.
    """

    x = sp.Symbol("x")

    explicaciones = {}

    # ======================================
    # DOMINIO
    # ======================================

    dominio = analisis["dominio"]

    explicaciones["dominio"] = [
        "El dominio representa todos los valores de x "
        "para los cuales la función está definida.",
        f"Expresión original: f(x) = {sp.sstr(expresion)}",
        f"Dominio obtenido: {dominio}"
    ]

    # ======================================
    # RANGO
    # ======================================

    rango = analisis["rango"]

    explicaciones["rango"] = [
        "El rango representa todos los valores que puede "
        "tomar la función en su dominio.",
        "Se analiza el conjunto de valores de f(x) "
        "cuando x recorre los números reales.",
        f"Rango obtenido: {rango}"
    ]

    # ======================================
    # RAÍCES
    # ======================================

    raices = analisis["raices"]

    explicaciones["raices"] = [
        "Las raíces son los valores de x donde la función "
        "corta o toca el eje X.",
        "Para encontrarlas igualamos la función a cero:",
        f"{sp.sstr(expresion)} = 0",
        f"Solución: x ∈ {raices}"
    ]

    # ======================================
    # INTERSECCIÓN CON Y
    # ======================================

    interseccion = analisis["interseccion_y"]

    explicaciones["interseccion_y"] = [
        "Para encontrar la intersección con el eje Y, "
        "evaluamos la función cuando x = 0.",
        f"f(0) = {sp.sstr(expresion.subs(x, 0))}",
        f"Intersección: (0, {interseccion})"
        if interseccion is not None
        else "La función no está definida en x = 0."
    ]

    # ======================================
    # PARIDAD
    # ======================================

    reflejada = sp.simplify(
        expresion.subs(x, -x)
    )

    diferencia_par = sp.simplify(reflejada - expresion)
    diferencia_impar = sp.simplify(reflejada + expresion)

    explicaciones["paridad"] = [
        "Para determinar la paridad sustituimos x por -x.",
        f"f(-x) = {sp.sstr(reflejada)}",
        f"f(-x) - f(x) = {sp.sstr(diferencia_par)}",
        f"f(-x) + f(x) = {sp.sstr(diferencia_impar)}",
        (
            "Como f(-x) = f(x), la función es par."
            if analisis["paridad"] == "Par"
            else
            "Como f(-x) = -f(x), la función es impar."
            if analisis["paridad"] == "Impar"
            else
            "No cumple las condiciones de paridad ni imparidad."
        )
    ]

    return explicaciones
