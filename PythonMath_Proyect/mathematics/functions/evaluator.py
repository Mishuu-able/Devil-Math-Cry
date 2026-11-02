
import sympy as sp


def evaluar_funcion(expresion, valores):
    """
    Evalúa una función matemática en uno o varios puntos.

    Args:
        expresion: expresión SymPy.
        valores: lista de valores numéricos.

    Returns:
        Lista de resultados con sus pasos.
    """

    x = sp.Symbol("x")

    resultados = []

    for valor in valores:

        sustitucion = expresion.subs(x, valor)

        resultado = sp.simplify(sustitucion)

        resultados.append({
            "valor_x": valor,
            "sustitucion": sustitucion,
            "resultado": resultado,
            "numerico": sp.N(resultado)
        })

    return resultados
