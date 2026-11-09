
import sympy as sp

from ..parser import convertir_expresion, X



# ============================================================
# CÁLCULO PRINCIPAL
# ============================================================

def calcular_limite(expresion, punto):
    x = X

    try:
        funcion = convertir_expresion(expresion)
        punto = interpretar_punto(punto)

        resultado = sp.limit(funcion, x, punto)

        if resultado.has(sp.Limit):
            raise ValueError(
                "No se pudo determinar el límite."
            )

        pasos = generar_pasos(
            funcion, punto, x, resultado
        )

        return funcion, punto, resultado, pasos

    except Exception as error:
        raise ValueError(
            f"No se pudo calcular el límite: {error}"
        ) from error


# ============================================================
# INTERPRETACIÓN DEL PUNTO
# ============================================================

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

    return sp.sympify(
        punto,
        locals={
            "pi": sp.pi,
            "oo": sp.oo,
            "inf": sp.oo,
        }
    )


# ============================================================
# ANÁLISIS DE LÍMITES LATERALES
# ============================================================


def calcular_limite_lateral(funcion, x, punto, direccion):
    """
    Calcula un límite lateral y maneja explícitamente
    las expresiones Piecewise.
    """

    if not isinstance(funcion, sp.Piecewise):
        return sp.limit(
            funcion,
            x,
            punto,
            dir=direccion
        )

    epsilon = sp.Symbol(
        "_epsilon",
        positive=True
    )

    desplazamiento = (
        -epsilon if direccion == "-" else epsilon
    )

    # Analizar las condiciones de cada rama
    for expresion, condicion in funcion.args:

        if condicion == sp.true:
            return sp.limit(
                expresion,
                x,
                punto,
                dir=direccion
            )

        condicion_lateral = sp.simplify(
            condicion.subs(
                x,
                punto + desplazamiento
            )
        )

        if condicion_lateral == sp.true:
            return sp.limit(
                expresion,
                x,
                punto,
                dir=direccion
            )

        if condicion_lateral == sp.false:
            continue

    # Respaldo para condiciones que no pudimos resolver
    return sp.limit(
        funcion,
        x,
        punto,
        dir=direccion
    )


def analizar_comportamiento_limite(funcion, punto, x=None):
    """
    Analiza el comportamiento de una función alrededor
    de un punto mediante límites laterales.

    Clasificaciones:
        - continua
        - removible
        - salto
        - infinita
        - oscilatoria_o_no_existente
        - indeterminada

    Retorna un diccionario con los resultados.
    """

    if x is None:
        simbolos_x = [
            simbolo
            for simbolo in funcion.free_symbols
            if simbolo.name == "x"
        ]

        x = simbolos_x[0] if simbolos_x else X

    punto = sp.sympify(punto)

    if punto in (sp.oo, -sp.oo):
        raise ValueError(
            "El análisis lateral requiere un punto finito."
        )

    try:
        # Límite por izquierda
        limite_izquierdo = calcular_limite_lateral(
            funcion,
            x,
            punto,
            "-"
        )

        limite_derecho = calcular_limite_lateral(
            funcion,
            x,
            punto,
            "+"
        )

        # Valor de la función en el punto
        valor_funcion = sp.simplify(
            funcion.subs(x, punto)
        )

    except Exception as error:
        raise ValueError(
            f"No se pudieron calcular los límites laterales: {error}"
        ) from error

    # Comprobar si los resultados son válidos
    if (
        limite_izquierdo.has(sp.Limit)
        or limite_derecho.has(sp.Limit)
    ):
        tipo = "indeterminada"
        existe_limite = False

    else:
        tipo, existe_limite = clasificar_limite(
            limite_izquierdo,
            limite_derecho,
            valor_funcion
        )

    # Detectar asíntota vertical
    hay_asintota_vertical = (
        es_infinito(limite_izquierdo)
        or es_infinito(limite_derecho)
    )

    return {
        "limite_izquierdo": limite_izquierdo,
        "limite_derecho": limite_derecho,
        "valor_funcion": valor_funcion,

        "existe_limite": existe_limite,
        "tipo": tipo,

        "asintota_vertical": hay_asintota_vertical,

        "punto": punto
    }


# ============================================================
# CLASIFICACIÓN
# ============================================================

def clasificar_limite(
    limite_izquierdo,
    limite_derecho,
    valor_funcion
):
    """
    Compara los límites laterales y el valor de la función.
    """

    # Comprobar límites infinitos
    if (
        es_infinito(limite_izquierdo)
        or es_infinito(limite_derecho)
    ):
        return "infinita", False

    # Comprobar si ambos límites son finitos
    if not (
        es_finito(limite_izquierdo)
        and es_finito(limite_derecho)
    ):
        return "indeterminada", False

    # Comparar ambos límites
    iguales = son_iguales(
        limite_izquierdo,
        limite_derecho
    )

    if not iguales:
        return "salto", False

    # Los límites laterales coinciden
    limite_comun = limite_izquierdo

    # Comprobar continuidad
    if es_finito(valor_funcion) and son_iguales(
        limite_comun,
        valor_funcion
    ):
        return "continua", True

    # El límite existe, pero la función no coincide
    # con él en el punto o no está definida allí.
    return "removible", True


# ============================================================
# UTILIDADES MATEMÁTICAS
# ============================================================

def es_infinito(valor):
    valor = sp.sympify(valor)

    return (
        valor in (sp.oo, -sp.oo, sp.zoo)
        or valor.is_infinite is True
    )


def es_finito(valor):
    valor = sp.sympify(valor)

    if valor.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
        return False

    return valor.is_finite is True


def son_iguales(a, b):
    try:
        diferencia = sp.simplify(a - b)

        return diferencia == 0 or diferencia.is_zero is True

    except Exception:
        return False


# ============================================================
# GENERACIÓN DE PROCEDIMIENTOS
# ============================================================

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

    if punto in (sp.oo, -sp.oo):
        return generar_pasos_infinito(
            funcion, punto, x, resultado, pasos
        )

    valor_directo = sp.simplify(
        funcion.subs(x, punto)
    )

    numerador, denominador = sp.fraction(
        sp.together(funcion)
    )

    valor_num = sp.simplify(
        numerador.subs(x, punto)
    )

    valor_den = sp.simplify(
        denominador.subs(x, punto)
    )

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
                "indeterminación 0/0. Debemos transformar "
                "la expresión antes de calcular el límite."
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
                "para identificar factores comunes."
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
                    "Cancelamos los factores comunes. "
                    "La expresión simplificada permite "
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
                        "en el punto indicado."
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
                    "simplificar la expresión. Se puede "
                    "intentar L'Hôpital si se cumplen "
                    "sus condiciones."
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
                    "las derivadas."
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
            "aproxima la función cuando x tiende al punto."
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
            "la función cuando x crece sin límite."
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
