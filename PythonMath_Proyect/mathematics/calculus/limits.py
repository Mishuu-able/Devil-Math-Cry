
import sympy as sp

from ..parser import convertir_expresion


def calcular_limite(expresion, punto):
    x = sp.Symbol("x")

    try:
        funcion = convertir_expresion(expresion)
        punto = interpretar_punto(punto)

        resultado = sp.limit(funcion, x, punto)

        if resultado.has(sp.Limit):
            raise ValueError(
                "No se pudo determinar el límite."
            )

        pasos = generar_pasos(funcion, punto, x, resultado)

        return funcion, punto, resultado, pasos

    except Exception as error:
        raise ValueError(
            f"No se pudo calcular el límite: {error}"
        ) from error


def interpretar_punto(punto):
    punto = str(punto).strip().replace("^", "**")

    valores = {
        "oo": sp.oo,
        "+oo": sp.oo,
        "inf": sp.oo,
        "+inf": sp.oo,
        "-oo": -sp.oo,
        "-inf": -sp.oo,
        "pi": sp.pi,
    }

    if punto.lower() in valores:
        return valores[punto.lower()]

    return sp.sympify(punto, locals={
        "pi": sp.pi,
        "oo": sp.oo,
        "inf": sp.oo,
    })


def generar_pasos(funcion, punto, x, resultado):
    pasos = []

    funcion_latex = sp.latex(funcion)
    punto_latex = sp.latex(punto)

    pasos.append({
        "titulo": "1. Identificamos el límite",
        "formula": (
            rf"\lim_{{x \to {punto_latex}}}"
            rf"\left({funcion_latex}\right)"
        ),
        "explicacion": (
            f"Queremos determinar a qué valor se aproxima "
            f"la función cuando x se acerca a {punto}. "
            "Primero analizaremos qué sucede al sustituir "
            "directamente ese valor."
        ),
    })

    # Límites en infinito: no hacemos sustitución directa.
    if punto in (sp.oo, -sp.oo):
        return generar_pasos_infinito(
            funcion, punto, x, resultado, pasos
        )

    # Intentamos evaluar directamente.
    valor_directo = sp.simplify(funcion.subs(x, punto))

    numerador, denominador = sp.fraction(
        sp.together(funcion)
    )

    valor_num = sp.simplify(numerador.subs(x, punto))
    valor_den = sp.simplify(denominador.subs(x, punto))

    if valor_den != 0:
        pasos.append({
            "titulo": "2. Sustitución directa",
            "formula": (
                rf"f({punto_latex}) = "
                rf"{sp.latex(valor_directo)}"
            ),
            "explicacion": (
                "Sustituimos x por el valor al que tiende. "
                "Como el denominador no se anula, podemos "
                "evaluar directamente la expresión."
            ),
        })

    elif valor_num == 0:
        pasos.append({
            "titulo": "2. Detectamos una indeterminación",
            "formula": r"\frac{0}{0}",
            "explicacion": (
                "Al sustituir, el numerador y el denominador "
                "dan cero. La expresión presenta la "
                "indeterminación 0/0, por lo que no podemos "
                "concluir que el límite sea cero. Debemos "
                "transformar la expresión."
            ),
        })

        numerador_factorizado = sp.factor(numerador)
        denominador_factorizado = sp.factor(denominador)

        pasos.append({
            "titulo": "3. Factorizamos",
            "formula": (
                rf"\frac{{{sp.latex(numerador_factorizado)}}}"
                rf"{{{sp.latex(denominador_factorizado)}}}"
            ),
            "explicacion": (
                "Factorizamos el numerador y el denominador "
                "para identificar factores comunes. "
                "Esta transformación permite buscar una "
                "expresión equivalente para x distinto "
                "del punto de interés."
            ),
        })

        simplificada = sp.cancel(funcion)

        if sp.simplify(simplificada - funcion) != 0:
            pasos.append({
                "titulo": "4. Simplificamos",
                "formula": (
                    rf"\frac{{{sp.latex(numerador)}}}"
                    rf"{{{sp.latex(denominador)}}}"
                    rf" = {sp.latex(simplificada)}"
                ),
                "explicacion": (
                    "Cancelamos los factores comunes del "
                    "numerador y el denominador. La expresión "
                    "simplificada coincide con la original "
                    "donde ambas están definidas, y nos permite "
                    "calcular el límite con mayor facilidad."
                ),
            })

            valor_simplificado = sp.simplify(
                simplificada.subs(x, punto)
            )

            if not valor_simplificado.has(sp.zoo, sp.nan):
                pasos.append({
                    "titulo": "5. Volvemos a sustituir",
                    "formula": (
                        rf"\lim_{{x\to {punto_latex}}}"
                        rf"{sp.latex(simplificada)}"
                        rf" = {sp.latex(valor_simplificado)}"
                    ),
                    "explicacion": (
                        "Evaluamos la expresión simplificada "
                        "en el punto indicado. Como ya no "
                        "aparece la indeterminación inicial, "
                        "obtenemos el valor del límite."
                    ),
                })

        else:
            pasos.append({
                "titulo": "3. Aplicamos la regla de L'Hôpital",
                "formula": (
                    rf"\lim_{{x\to {punto_latex}}}"
                    rf"\frac{{{sp.latex(sp.diff(numerador, x))}}}"
                    rf"{{{sp.latex(sp.diff(denominador, x))}}}"
                ),
                "explicacion": (
                    "La factorización no ha permitido "
                    "simplificar la expresión. Intentamos "
                    "la regla de L'Hôpital: derivamos por "
                    "separado el numerador y el denominador. "
                    "Esta regla solo es válida si se cumplen "
                    "sus condiciones y persiste la forma 0/0."
                ),
            })

            derivada_num = sp.diff(numerador, x)
            derivada_den = sp.diff(denominador, x)

            pasos.append({
                "titulo": "4. Evaluamos las derivadas",
                "formula": (
                    rf"\lim_{{x\to {punto_latex}}}"
                    rf"\frac{{{sp.latex(derivada_num)}}}"
                    rf"{{{sp.latex(derivada_den)}}}"
                ),
                "explicacion": (
                    "Calculamos el límite del cociente de "
                    "las derivadas. Si sigue existiendo una "
                    "indeterminación, puede ser necesario "
                    "aplicar L'Hôpital nuevamente."
                ),
            })

    else:
        pasos.append({
            "titulo": "2. Analizamos la sustitución",
            "formula": (
                rf"f({punto_latex}) = "
                rf"{sp.latex(valor_directo)}"
            ),
            "explicacion": (
                "La sustitución directa no permite obtener "
                "un valor finito válido. Analizaremos el "
                "comportamiento de la función alrededor "
                "del punto."
            ),
        })

    pasos.append({
        "titulo": "Resultado del límite",
        "formula": (
            rf"\lim_{{x\to {punto_latex}}}"
            rf"\left({funcion_latex}\right)"
            rf" = {sp.latex(resultado)}"
        ),
        "explicacion": (
            "Este es el resultado calculado para el límite. "
            "La expresión final resume el valor al que se "
            "aproxima la función cuando x tiende al punto "
            "indicado. Revisa los pasos anteriores para "
            "comprender la transformación aplicada."
        ),
    })

    return pasos


def generar_pasos_infinito(funcion, punto, x, resultado, pasos):
    funcion_latex = sp.latex(funcion)
    punto_latex = sp.latex(punto)

    pasos.append({
        "titulo": "2. Analizamos el comportamiento",
        "formula": (
            rf"\lim_{{x\to {punto_latex}}}"
            rf"\left({funcion_latex}\right)"
        ),
        "explicacion": (
            "Como x tiende al infinito, no sustituimos x "
            "por un número. Estudiamos cómo se comporta "
            "la función cuando x crece sin límite en la "
            "dirección indicada."
        ),
    })

    pasos.append({
        "titulo": "Resultado del límite",
        "formula": (
            rf"\lim_{{x\to {punto_latex}}}"
            rf"\left({funcion_latex}\right)"
            rf" = {sp.latex(resultado)}"
        ),
        "explicacion": (
            "El resultado describe el comportamiento límite "
            "de la función en la dirección analizada."
        ),
    })

    return pasos
