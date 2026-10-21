
import sympy as sp

from ..parser import convertir_expresion


def calcular_derivada(expresion):
    x = sp.Symbol("x")

    try:
        funcion = convertir_expresion(expresion)
        derivada = sp.simplify(sp.diff(funcion, x))

        pasos = generar_pasos(funcion, derivada, x)

        return funcion, derivada, pasos

    except Exception as error:
        raise ValueError(
            f"No se pudo calcular la derivada: {error}"
        ) from error


def generar_pasos(funcion, derivada, x):
    funcion_latex = sp.latex(funcion)
    derivada_latex = sp.latex(derivada)

    pasos = [
        {
            "titulo": "1. Función original",
            "formula": rf"f(x) = {funcion_latex}",
            "explicacion": (
                "Identificamos la función que vamos a derivar. "
                "Nuestro objetivo es encontrar cómo cambia f(x) "
                "respecto a la variable x."
            ),
        }
    ]

    # Regla de la potencia: ax^n
    if funcion.is_Mul or funcion.is_Pow or funcion.is_Number:
        coeficiente, resto = funcion.as_coeff_Mul()

        if resto == x:
            pasos.append({
                "titulo": "2. Identificamos la regla",
                "formula": (
                    r"\frac{d}{dx}(ax^n)=anx^{n-1}"
                ),
                "explicacion": (
                    "Aplicamos la regla de la potencia. "
                    "Multiplicamos el coeficiente por el exponente "
                    "y después restamos 1 al exponente de x."
                ),
            })

        elif (
            isinstance(resto, sp.Pow)
            and resto.base == x
            and resto.exp.is_number
        ):
            exponente = resto.exp

            pasos.append({
                "titulo": "2. Identificamos la regla",
                "formula": (
                    r"\frac{d}{dx}(ax^n)=anx^{n-1}"
                ),
                "explicacion": (
                    f"Aplicamos la regla de la potencia. "
                    f"El coeficiente es {coeficiente} y el "
                    f"exponente es {exponente}. Multiplicamos "
                    "el coeficiente por el exponente y reducimos "
                    "el exponente en una unidad."
                ),
            })

            sustitucion = sp.Mul(
                coeficiente,
                exponente,
                sp.Pow(x, exponente - 1, evaluate=False),
                evaluate=False
            )

            pasos.append({
                "titulo": "3. Sustituimos en la fórmula",
                "formula": (
                    rf"\frac{{d}}{{dx}}\left[{funcion_latex}\right]"
                    rf" = {sp.latex(sustitucion)}"
                ),
                "explicacion": (
                    f"Sustituimos a = {coeficiente} y "
                    f"n = {exponente} en la regla. "
                    f"Multiplicamos {coeficiente} por {exponente} "
                    f"y calculamos {exponente} - 1."
                ),
            })

    # Derivación general mediante SymPy
    pasos.append({
        "titulo": "Resultado de la derivación",
        "formula": rf"f'(x) = {derivada_latex}",
        "explicacion": (
            "Simplificamos las operaciones obtenidas y "
            "presentamos la derivada final. "
            "Puedes comprobar el resultado comparándolo "
            "con la función original."
        ),
    })

    return pasos
