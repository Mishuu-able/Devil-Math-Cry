
import sympy as sp


def operar_funciones(funcion_f, funcion_g, operacion):

    x = sp.Symbol("x")

    if operacion == "Suma":
        resultado = sp.simplify(funcion_f + funcion_g)

    elif operacion == "Resta":
        resultado = sp.simplify(funcion_f - funcion_g)

    elif operacion == "Multiplicación":
        resultado = sp.simplify(funcion_f * funcion_g)

    elif operacion == "División":

        if funcion_g == 0:
            raise ValueError("No se puede dividir entre cero.")

        resultado = sp.simplify(funcion_f / funcion_g)

    elif operacion == "f(g(x))":
        resultado = sp.simplify(
            funcion_f.subs(x, funcion_g)
        )

    elif operacion == "g(f(x))":
        resultado = sp.simplify(
            funcion_g.subs(x, funcion_f)
        )

    else:
        raise ValueError("Operación no reconocida.")

    return {
        "funcion_f": funcion_f,
        "funcion_g": funcion_g,
        "operacion": operacion,
        "resultado": resultado
    }


def generar_procedimiento(datos):

    f = datos["funcion_f"]
    g = datos["funcion_g"]
    operacion = datos["operacion"]
    resultado = datos["resultado"]

    pasos = [
        f"Primera función: f(x) = {sp.sstr(f)}",
        f"Segunda función: g(x) = {sp.sstr(g)}"
    ]

    if operacion == "Suma":
        pasos.extend([
            "Sumamos ambas funciones:",
            f"f(x) + g(x) = ({sp.sstr(f)}) + ({sp.sstr(g)})"
        ])

    elif operacion == "Resta":
        pasos.extend([
            "Restamos ambas funciones:",
            f"f(x) - g(x) = ({sp.sstr(f)}) - ({sp.sstr(g)})"
        ])

    elif operacion == "Multiplicación":
        pasos.extend([
            "Multiplicamos ambas funciones:",
            f"f(x) · g(x) = ({sp.sstr(f)}) · ({sp.sstr(g)})"
        ])

    elif operacion == "División":
        pasos.extend([
            "Dividimos la primera función entre la segunda:",
            f"f(x) / g(x) = ({sp.sstr(f)}) / ({sp.sstr(g)})",
            "Debemos excluir los valores donde g(x) = 0."
        ])

    elif operacion == "f(g(x))":
        pasos.extend([
            "Sustituimos cada x de f(x) por g(x):",
            f"f(g(x)) = f({sp.sstr(g)})",
            f"Resultado de la sustitución: {sp.sstr(resultado)}"
        ])

    elif operacion == "g(f(x))":
        pasos.extend([
            "Sustituimos cada x de g(x) por f(x):",
            f"g(f(x)) = g({sp.sstr(f)})",
            f"Resultado de la sustitución: {sp.sstr(resultado)}"
        ])

    pasos.append(f"Resultado simplificado: {sp.sstr(resultado)}")

    return pasos
