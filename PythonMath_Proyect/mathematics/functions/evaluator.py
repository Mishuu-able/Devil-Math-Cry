import sympy as sp
from ..parser import X


def evaluar_funcion(expresion, valores):
    """
    Evalúa una función matemática en uno o varios puntos.

    Args:
        expresion: expresión SymPy.
        valores: lista de valores numéricos.

    Returns:
        Lista de resultados con sus pasos.
    """

    x = X

    resultados = []

    for valor in valores:

        sustitucion = expresion.subs(X, valor)

        resultado = sp.simplify(sustitucion)

        resultados.append({
            "valor_x": valor,
            "sustitucion": sustitucion,
            "resultado": resultado,
            "numerico": sp.N(resultado)
        })

    return resultados
