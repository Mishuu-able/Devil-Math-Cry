import sympy as sp

from mathematics.parser import convertir_expresion


# ─────────────────────────────────────────────
# SIMPLIFICAR
# ─────────────────────────────────────────────

def simplificar(texto):

    expresion = convertir_expresion(texto)

    resultado = sp.simplify(expresion)

    pasos = [
        "Identificamos los términos y expresiones semejantes.",
        f"Expresión original: {sp.latex(expresion)}",
        f"Aplicamos las reglas de simplificación: {sp.latex(resultado)}",
        "Obtenemos la expresión simplificada."
    ]

    return resultado, pasos


# ─────────────────────────────────────────────
# DESARROLLAR
# ─────────────────────────────────────────────

def desarrollar(texto):

    expresion = convertir_expresion(texto)

    resultado = sp.expand(expresion)

    pasos = [
        "Identificamos los productos y paréntesis.",
        f"Expresión original: {sp.latex(expresion)}",
        f"Aplicamos la propiedad distributiva: {sp.latex(resultado)}",
        "Obtenemos la expresión desarrollada."
    ]

    return resultado, pasos


# ─────────────────────────────────────────────
# FACTORIZAR
# ─────────────────────────────────────────────

def factorizar(texto):

    expresion = convertir_expresion(texto)
    resultado = sp.factor(expresion)

    pasos = []

    # ------------------------------------------------
    # PASO 1: IDENTIFICAR LA EXPRESIÓN
    # ------------------------------------------------

    pasos.append({
        "titulo": "Identificamos la expresión",
        "formula": sp.latex(expresion),
        "explicacion": (
            "Analizamos los términos, sus coeficientes "
            "y las potencias de las variables."
        )
    })

    # ------------------------------------------------
    # PASO 2: BUSCAR FACTOR COMÚN
    # ------------------------------------------------

    expresion_reducida = sp.factor_terms(expresion)

    if sp.simplify(expresion_reducida - expresion) != 0:

        pasos.append({
            "titulo": "Extraemos el factor común",
            "formula": (
                sp.latex(expresion)
                + " = "
                + sp.latex(expresion_reducida)
            ),
            "explicacion": (
                "Identificamos el factor que se repite "
                "en todos los términos y lo colocamos "
                "fuera del paréntesis."
            )
        })

    # ------------------------------------------------
    # ANALIZAR LA FACTORIZACIÓN RESTANTE
    # ------------------------------------------------

    factores = sp.factor_list(expresion_reducida)[1]

    # ------------------------------------------------
    # DIFERENCIA DE CUADRADOS
    # ------------------------------------------------

    terminos = sp.Add.make_args(expresion_reducida)

    if len(terminos) == 2:

        positivo = None
        negativo = None

        for termino in terminos:

            if termino.could_extract_minus_sign():
                negativo = -termino
            else:
                positivo = termino

        if positivo is not None and negativo is not None:

            raiz_a = sp.sqrt(positivo)
            raiz_b = sp.sqrt(negativo)

            es_cuadrado = (
                sp.simplify(raiz_a**2 - positivo) == 0
                and sp.simplify(raiz_b**2 - negativo) == 0
            )

            if es_cuadrado:

                pasos.append({
                    "titulo": "Identificamos una diferencia de cuadrados",
                    "formula": (
                        sp.latex(positivo)
                        + " - "
                        + sp.latex(negativo)
                    ),
                    "explicacion": (
                        "Reconocemos dos términos que son "
                        "cuadrados perfectos separados por "
                        "una resta."
                    )
                })

                pasos.append({
                    "titulo": "Aplicamos la identidad notable",
                    "formula": (
                        r"a^2-b^2=(a-b)(a+b)"
                    ),
                    "explicacion": (
                        "Aplicamos la identidad de diferencia "
                        "de cuadrados: la raíz de cada término "
                        "forma dos binomios conjugados."
                    )
                })

    # ------------------------------------------------
    # TRINOMIO CUADRADO PERFECTO
    # ------------------------------------------------

    elif len(terminos) == 3:

        variables = sorted(
            expresion_reducida.free_symbols,
            key=lambda v: v.name
        )

        if len(variables) == 1:

            variable = variables[0]

            try:
                polinomio = sp.Poly(
                    expresion_reducida,
                    variable
                )

                if polinomio.degree() == 2:

                    a = polinomio.coeff_monomial(variable**2)
                    b = polinomio.coeff_monomial(variable)
                    c = polinomio.coeff_monomial(1)

                    raiz_a = sp.sqrt(a)
                    raiz_c = sp.sqrt(c)

                    if (
                        sp.simplify(raiz_a**2 - a) == 0
                        and sp.simplify(raiz_c**2 - c) == 0
                        and sp.simplify(b**2 - 4*a*c) == 0
                    ):

                        signo = "+" if b > 0 else "-"

                        pasos.append({
                            "titulo": "Identificamos un trinomio cuadrado perfecto",
                            "formula": sp.latex(
                                sp.Eq(
                                    expresion_reducida,
                                    (raiz_a*variable + signo + raiz_c)**2
                                )
                            ) if False else (
                                sp.latex(expresion_reducida)
                            ),
                            "explicacion": (
                                "Los extremos son cuadrados perfectos "
                                "y el término central es el doble "
                                "producto de sus raíces, con el signo "
                                "correspondiente."
                            )
                        })

                        pasos.append({
                            "titulo": "Aplicamos la identidad notable",
                            "formula": (
                                r"a^2 \pm 2ab+b^2=(a\pm b)^2"
                            ),
                            "explicacion": (
                                "Agrupamos los términos en un binomio "
                                "elevado al cuadrado."
                            )
                        })

            except sp.PolynomialError:
                pass

    # ------------------------------------------------
    # TRINOMIOS DE SEGUNDO GRADO
    # ------------------------------------------------

    variables = sorted(
        expresion_reducida.free_symbols,
        key=lambda v: v.name
    )

    if len(variables) == 1:

        variable = variables[0]

        try:
            polinomio = sp.Poly(
                expresion_reducida,
                variable
            )

            if polinomio.degree() == 2:

                a = polinomio.coeff_monomial(variable**2)
                b = polinomio.coeff_monomial(variable)
                c = polinomio.coeff_monomial(1)

                if a == 1:

                    pasos.append({
                        "titulo": "Identificamos el trinomio",
                        "formula": (
                            rf"{variable}^2"
                            rf" + ({sp.latex(b)}){variable}"
                            rf" + ({sp.latex(c)})"
                        ),
                        "explicacion": (
                            "Buscamos dos números cuyo producto "
                            f"sea {c} y cuya suma sea {b}."
                        )
                    })

                    if len(factores) == 2:

                        for factor, potencia in factores:
                            if potencia == 1:
                                pass

                        raices = sp.solve(
                            expresion_reducida,
                            variable
                        )

                        if len(raices) == 2:

                            m = -raices[0]
                            n = -raices[1]

                            pasos.append({
                                "titulo": "Encontramos los números",
                                "formula": (
                                    rf"{sp.latex(m)} + {sp.latex(n)}"
                                    rf" = {sp.latex(b)}"
                                    r"\qquad"
                                    rf"{sp.latex(m)} \cdot {sp.latex(n)}"
                                    rf" = {sp.latex(c)}"
                                ),
                                "explicacion": (
                                    "Los dos números cumplen las "
                                    "condiciones de suma y producto."
                                )
                            })

                else:

                    pasos.append({
                        "titulo": "Identificamos el trinomio general",
                        "formula": sp.latex(expresion_reducida),
                        "explicacion": (
                            "Como el coeficiente principal es diferente "
                            "de uno, buscamos dos números cuyo producto "
                            "sea a·c y cuya suma sea b."
                        )
                    })

                    pasos.append({
                        "titulo": "Calculamos el producto a·c",
                        "formula": (
                            rf"a \cdot c = "
                            rf"{sp.latex(a)} \cdot {sp.latex(c)}"
                            rf" = {sp.latex(a*c)}"
                        ),
                        "explicacion": (
                            "Multiplicamos el coeficiente principal "
                            "por el término independiente."
                        )
                    })

        except sp.PolynomialError:
            pass

    # ------------------------------------------------
    # PASO FINAL: RESULTADO
    # ------------------------------------------------

    if sp.simplify(resultado - expresion) == 0:

        pasos.append({
            "titulo": "La expresión no se puede factorizar más",
            "formula": sp.latex(resultado),
            "explicacion": (
                "No encontramos factores algebraicos "
                "adicionales dentro del dominio racional."
            )
        })

    else:

        pasos.append({
            "titulo": "Obtenemos la factorización",
            "formula": sp.latex(resultado),
            "explicacion": (
                "Multiplicando los factores obtenemos "
                "la expresión original. La factorización "
                "ha sido completada."
            )
        })

    return resultado, pasos


# ─────────────────────────────────────────────
# RESOLVER ECUACIÓN
# ─────────────────────────────────────────────

def resolver_ecuacion(texto):

    if "=" not in texto:
        raise ValueError("Debes introducir una ecuación con signo =.")

    izquierda, derecha = texto.split("=", 1)

    izquierda = convertir_expresion(izquierda)
    derecha = convertir_expresion(derecha)

    x = sp.Symbol("x")

    ecuacion = sp.Eq(izquierda, derecha)
    expresion = sp.expand(izquierda - derecha)

    try:
        polinomio = sp.Poly(expresion, x)
    except sp.PolynomialError:
        raise ValueError("Introduce una ecuación polinómica válida.")

    grado = polinomio.degree()

    if grado > 2:
        raise ValueError(
            "Por ahora se admiten ecuaciones de hasta segundo grado."
        )

    if grado == 0:
        if sp.simplify(expresion) == 0:
            return "Infinitas soluciones", [
                {
                    "titulo": "Analizamos la ecuación",
                    "formula": r"0=0",
                    "explicacion": "La igualdad es verdadera para cualquier valor de x."
                }
            ]

        return "Sin solución", [
            {
                "titulo": "Analizamos la ecuación",
                "formula": sp.latex(sp.Eq(expresion, 0)),
                "explicacion": "La igualdad es falsa. No existen soluciones."
            }
        ]

    a = polinomio.coeff_monomial(x**2)
    b = polinomio.coeff_monomial(x)
    c = polinomio.coeff_monomial(1)

    pasos = []

    # ─────────────────────────────────────
    # ECUACIÓN LINEAL
    # ─────────────────────────────────────

    if grado == 1:

        pasos.append({
            "titulo": "Planteamiento",
            "formula": sp.latex(ecuacion),
            "explicacion": "Identificamos la ecuación y la incógnita."
        })

        pasos.append({
            "titulo": "Agrupamos los términos",
            "formula": sp.latex(sp.Eq(a*x + c, 0, evaluate=False)),
            "explicacion": "Pasamos todos los términos al lado izquierdo."
        })

        pasos.append({
            "titulo": "Aislamos la incógnita",
            "formula": sp.latex(sp.Eq(a*x, -c, evaluate=False)),
            "explicacion": f"Restamos {sp.latex(c)} en ambos lados."
        })

        solucion = sp.simplify(-c / a)

        pasos.append({
            "titulo": "Despejamos x",
            "formula": sp.latex(sp.Eq(x, solucion)),
            "explicacion": f"Dividimos ambos lados entre {sp.latex(a)}."
        })

        soluciones = [solucion]

    # ─────────────────────────────────────
    # ECUACIÓN CUADRÁTICA
    # ─────────────────────────────────────

    else:

        pasos.append({
            "titulo": "Identificamos los coeficientes",
            "formula": sp.latex(sp.Eq(a*x**2 + b*x + c, 0)),
            "explicacion": (
                f"Comparamos con ax² + bx + c = 0. "
                f"Por tanto, a = {a}, b = {b} y c = {c}."
            )
        })

        # Discriminante
        discriminante = sp.simplify(b**2 - 4*a*c)

        pasos.append({
            "titulo": "Calculamos el discriminante",
            "formula": (
                rf"\Delta = b^2 - 4ac = "
                rf"{sp.latex(discriminante)}"
            ),
            "explicacion": (
                "El discriminante permite determinar "
                "la naturaleza de las raíces."
            )
        })

        if discriminante > 0:
            tipo = "Dos soluciones reales diferentes."
        elif discriminante == 0:
            tipo = "Una solución real doble."
        else:
            tipo = "Dos soluciones complejas conjugadas."

        pasos.append({
            "titulo": "Interpretamos el discriminante",
            "formula": rf"\Delta = {sp.latex(discriminante)}",
            "explicacion": tipo
        })

        # Fórmula general
        pasos.append({
            "titulo": "Aplicamos la fórmula general",
            "formula": (
                r"x = \frac{-b \pm \sqrt{\Delta}}{2a}"
            ),
            "explicacion": (
                "Sustituimos los coeficientes en la fórmula "
                "general de segundo grado."
            )
        })

        # Sustitución
        formula_sustituida = (
            rf"x = \frac{{-({sp.latex(b)}) "
            rf"\pm \sqrt{{{sp.latex(discriminante)}}}}}"
            rf"{{2({sp.latex(a)})}}"
        )

        pasos.append({
            "titulo": "Sustituimos los valores",
            "formula": formula_sustituida,
            "explicacion": "Reemplazamos a, b y Δ por sus respectivos valores."
        })

        # Soluciones
        raiz_delta = sp.sqrt(discriminante)

        x1 = sp.simplify(
            (-b + raiz_delta) / (2 * a)
        )

        x2 = sp.simplify(
            (-b - raiz_delta) / (2 * a)
        )

        soluciones = [x1, x2]

        pasos.append({
            "titulo": "Calculamos las raíces",
            "formula": (
                r"x_1 = " + sp.latex(soluciones[0])
                + (
                    r", \quad x_2 = " + sp.latex(soluciones[1])
                    if len(soluciones) > 1 else ""
                )
            ),
            "explicacion": "Estas son las soluciones de la ecuación."
        })

    # ─────────────────────────────────────
    # COMPROBACIÓN
    # ─────────────────────────────────────

    for indice, solucion in enumerate(soluciones, start=1):

        valor_izquierda = sp.simplify(
            izquierda.subs(x, solucion)
        )

        valor_derecha = sp.simplify(
            derecha.subs(x, solucion)
        )

        pasos.append({
            "titulo": f"Comprobación de la solución {indice}",
            "formula": (
                rf"{sp.latex(valor_izquierda)}"
                rf" = {sp.latex(valor_derecha)}"
            ),
            "explicacion": (
                f"Sustituimos x = {sp.latex(solucion)} "
                "en la ecuación original. "
                "Verificamos que ambos lados sean iguales."
            )
        })

    return soluciones, pasos


# ─────────────────────────────────────────────
# RESOLVER SISTEMA
# ─────────────────────────────────────────────

def resolver_sistema(textos):

    if len(textos) != 2:
        raise ValueError("Introduce exactamente dos ecuaciones.")

    ecuaciones = []
    variables = set()

    # Interpretar las ecuaciones
    for texto in textos:

        if "=" not in texto:
            raise ValueError(
                f"La ecuación '{texto}' necesita un signo =."
            )

        izquierda, derecha = texto.split("=", 1)

        izquierda = convertir_expresion(izquierda)
        derecha = convertir_expresion(derecha)

        expresion = sp.expand(izquierda - derecha)

        ecuaciones.append(expresion)
        variables.update(expresion.free_symbols)

    variables = sorted(variables, key=lambda v: v.name)

    if len(variables) != 2:
        raise ValueError(
            "El sistema debe tener exactamente dos incógnitas."
        )

    x, y = variables
    e1, e2 = ecuaciones

    # Comprobar que sean ecuaciones lineales
    try:
        polinomios = [sp.Poly(e, x, y) for e in ecuaciones]
    except sp.PolynomialError:
        raise ValueError("Este método admite sistemas lineales.")

    if any(p.total_degree() > 1 for p in polinomios):
        raise ValueError("Este método admite sistemas lineales.")

    # Coeficientes
    a1 = e1.coeff(x)
    b1 = e1.coeff(y)
    c1 = -e1.subs({x: 0, y: 0})

    a2 = e2.coeff(x)
    b2 = e2.coeff(y)
    c2 = -e2.subs({x: 0, y: 0})

    determinante = sp.simplify(a1 * b2 - a2 * b1)

    pasos = []

    # Paso 1: planteamiento
    pasos.append({
        "titulo": "Planteamiento del sistema",
        "formula": (
            rf"{sp.latex(a1*x + b1*y)} = {sp.latex(c1)}"
            rf"\qquad"
            rf"{sp.latex(a2*x + b2*y)} = {sp.latex(c2)}"
        ),
        "explicacion": (
            "Identificamos las dos ecuaciones y "
            "las incógnitas del sistema."
        )
    })

    # Sistemas sin solución única
    if determinante == 0:

        soluciones = sp.linsolve(ecuaciones, (x, y))

        if soluciones == sp.EmptySet:
            return "Sistema incompatible: no tiene solución.", pasos + [{
                "titulo": "Analizamos el sistema",
                "formula": r"\Delta = 0",
                "explicacion": (
                    "Las ecuaciones son incompatibles. "
                    "No existe ningún par de valores que satisfaga ambas."
                )
            }]

        return "Sistema compatible indeterminado: tiene infinitas soluciones.", pasos + [{
            "titulo": "Analizamos el sistema",
            "formula": r"\Delta = 0",
            "explicacion": (
                "Las ecuaciones representan la misma recta "
                "o son dependientes. Existen infinitas soluciones."
            )
        }]

    # Paso 2: preparar eliminación
    pasos.append({
        "titulo": "Preparamos el método de eliminación",
        "formula": (
            rf"{sp.latex(a2)}({sp.latex(a1*x + b1*y)} = {sp.latex(c1)})"
            r"\qquad - \qquad"
            rf"{sp.latex(a1)}({sp.latex(a2*x + b2*y)} = {sp.latex(c2)})"
        ),
        "explicacion": (
            f"Multiplicamos la primera ecuación por {a2} "
            f"y la segunda por {a1}, para eliminar {x}."
        )
    })

    # Paso 3: eliminar x
    coef_y = sp.simplify(b1*a2 - b2*a1)
    resultado_y = sp.simplify(c1*a2 - c2*a1)

    pasos.append({
        "titulo": f"Eliminamos la incógnita {x}",
        "formula": sp.latex(sp.Eq(coef_y*y, resultado_y)),
        "explicacion": (
            "Restamos las ecuaciones transformadas. "
            f"Los términos con {x} desaparecen."
        )
    })

    # Paso 4: despejar y
    solucion_y = sp.simplify(resultado_y / coef_y)

    pasos.append({
        "titulo": f"Despejamos {y}",
        "formula": sp.latex(sp.Eq(y, solucion_y)),
        "explicacion": (
            f"Dividimos ambos lados entre {coef_y}."
        )
    })

    # Paso 5: sustituir y despejar x
    if a1 != 0:
        expresion_x = sp.Eq(
            a1*x + b1*solucion_y,
            c1
        )
        solucion_x = sp.simplify(
            (c1 - b1*solucion_y) / a1
        )
    else:
        expresion_x = sp.Eq(
            a2*x + b2*solucion_y,
            c2
        )
        solucion_x = sp.simplify(
            (c2 - b2*solucion_y) / a2
        )

    pasos.append({
        "titulo": f"Sustituimos para despejar {x}",
        "formula": sp.latex(expresion_x),
        "explicacion": (
            f"Sustituimos {y} = {sp.latex(solucion_y)} "
            "en una de las ecuaciones originales."
        )
    })

    pasos.append({
        "titulo": "Obtenemos la segunda incógnita",
        "formula": sp.latex(sp.Eq(x, solucion_x)),
        "explicacion": "Despejamos la incógnita restante."
    })

    resultado = {
        x: solucion_x,
        y: solucion_y
    }

    # Comprobación
    for indice, ecuacion in enumerate(ecuaciones, start=1):

        comprobacion = sp.simplify(
            ecuacion.subs(resultado)
        )

        cumple = comprobacion == 0

        if cumple:
            explicacion = (
                f"Los valores obtenidos satisfacen "
                f"la ecuación {indice}. La igualdad se cumple."
            )
        else:
            explicacion = (
                f"Los valores obtenidos no satisfacen "
                f"la ecuación {indice}."
            )

        pasos.append({
            "titulo": f"Comprobación de la ecuación {indice}",
            "formula": sp.latex(
                sp.Eq(comprobacion, 0)
            ),
            "explicacion": explicacion
        })

    return resultado, pasos