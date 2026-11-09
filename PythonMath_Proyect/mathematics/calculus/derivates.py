import sympy as sp

from ..parser import convertir_expresion, normalizar_expresion

def calcular_derivada(expresion, orden=1):
    x = sp.Symbol("x", real=True)

    try:
        orden = int(orden)

        if orden < 1 or orden > 10:
            raise ValueError(
                "El orden debe estar entre 1 y 10."
            )

        funcion = convertir_expresion(expresion)

        derivadas = []
        actual = funcion

        for _ in range(orden):
            actual = sp.simplify(sp.diff(actual, x))
            derivadas.append(actual)

        pasos = generar_pasos(funcion, derivadas)

        return funcion, derivadas[-1], pasos

    except Exception as error:
        raise ValueError(
            f"No se pudo calcular la derivada: {error}"
        ) from error

def generar_pasos(funcion, derivadas):

    pasos = [{
        "titulo": "Función original",
        "formula": rf"f(x) = {sp.latex(funcion)}",
        "explicacion": (
            "Identificamos la función original que vamos a derivar "
            "respecto a la variable x."
        )
    }]

    anterior = funcion

    for nivel, derivada in enumerate(derivadas, start=1):

        nombre_anterior = (
            "f(x)" if nivel == 1
            else rf"f^{{({nivel - 1})}}(x)"
        )

        nombre_actual = (
            "f'(x)" if nivel == 1
            else rf"f^{{({nivel})}}(x)"
        )

        pasos.append({
            "titulo": (
                "Primera derivada" if nivel == 1
                else f"Derivada de orden {nivel}"
            ),
            "formula": (
                rf"\frac{{d}}{{dx}}\left[{nombre_anterior}\right]"
                rf" = {nombre_actual} = {sp.latex(derivada)}"
            ),
            "explicacion": (
                "Aplicamos las reglas de derivación correspondientes. "
                "SymPy reconoce las potencias, funciones trigonométricas, "
                "exponenciales y sus combinaciones."
            )
        })

        anterior = derivada

    pasos.append({
        "titulo": "Resultado final",
        "formula": (
            rf"f^{{({len(derivadas)})}}(x)"
            rf" = {sp.latex(derivadas[-1])}"
        ),
        "explicacion": (
            f"Esta es la derivada de orden {len(derivadas)}."
        )
    })

    return pasos
