
import sympy as sp


def clasificar_funcion(expresion):

    x = sp.Symbol("x")

    componentes = []

    # ======================================
    # FUNCIONES CONSTANTES Y POLINÓMICAS
    # ======================================

    if expresion.is_polynomial(x):

        grado = sp.degree(expresion, x)

        if grado == 0:
            componentes.append("Constante")

        elif grado == 1:
            componentes.append("Lineal")

        elif grado == 2:
            componentes.append("Cuadrática")

        else:
            componentes.append("Polinómica")

    # ======================================
    # FUNCIONES RACIONALES
    # ======================================

    numerador, denominador = sp.fraction(
        sp.cancel(expresion)
    )

    if denominador.has(x):
        componentes.append("Racional")

    # ======================================
    # FUNCIONES RADICALES
    # ======================================

    for potencia in expresion.atoms(sp.Pow):

        exponente = potencia.exp

        if (
            potencia.base.has(x)
            and exponente.is_integer is not True
        ):
            componentes.append("Radical")
            break

    # ======================================
    # FUNCIONES EXPONENCIALES
    # ======================================

    for potencia in expresion.atoms(sp.Pow):

        if (
            potencia.base.has(x) is False
            and potencia.exp.has(x)
        ):
            componentes.append("Exponencial")
            break

    if expresion.has(sp.exp):
        componentes.append("Exponencial")

    # ======================================
    # FUNCIONES LOGARÍTMICAS
    # ======================================

    if expresion.has(sp.log):
        componentes.append("Logarítmica")

    # ======================================
    # FUNCIONES TRIGONOMÉTRICAS
    # ======================================

    funciones_trigonometricas = (
        sp.sin,
        sp.cos,
        sp.tan,
        sp.cot,
        sp.sec,
        sp.csc
    )

    if any(expresion.has(funcion) for funcion in funciones_trigonometricas):
        componentes.append("Trigonométrica")

    # ======================================
    # ELIMINAR REPETICIONES
    # ======================================

    componentes = list(dict.fromkeys(componentes))

    # ======================================
    # DETERMINAR CATEGORÍA PRINCIPAL
    # ======================================

    if not componentes:

        categoria = "Función no clasificada"

    elif len(componentes) == 1:

        categoria = componentes[0]

    else:

        categoria = "Función mixta"

    # ======================================
    # GRADO POLINÓMICO
    # ======================================

    grado = None

    if expresion.is_polynomial(x):
        grado = sp.degree(expresion, x)

    return {
        "categoria": categoria,
        "componentes": componentes,
        "grado": grado,
        "expresion": expresion
    }


def generar_explicacion_clasificacion(clasificacion):

    componentes = clasificacion["componentes"]
    grado = clasificacion["grado"]

    explicaciones = []

    explicaciones.append(
        "Se analiza la estructura algebraica de la expresión."
    )

    if not componentes:

        explicaciones.append(
            "No se identificó una categoría compatible "
            "con las reglas actuales del clasificador."
        )

        return explicaciones

    if "Constante" in componentes:
        explicaciones.append(
            "Es constante porque no depende de la variable x."
        )

    if "Lineal" in componentes:
        explicaciones.append(
            "Es lineal porque es un polinomio de grado 1."
        )

    if "Cuadrática" in componentes:
        explicaciones.append(
            "Es cuadrática porque su mayor exponente "
            "es 2 y su grado es 2."
        )

    if "Polinómica" in componentes:
        explicaciones.append(
            f"Es polinómica porque es un polinomio "
            f"de grado {grado}."
        )

    if "Racional" in componentes:
        explicaciones.append(
            "Es racional porque puede expresarse como "
            "un cociente de polinomios con denominador "
            "dependiente de x."
        )

    if "Radical" in componentes:
        explicaciones.append(
            "Es radical porque contiene potencias "
            "fraccionarias de expresiones que dependen de x."
        )

    if "Exponencial" in componentes:
        explicaciones.append(
            "Es exponencial porque la variable aparece "
            "en el exponente."
        )

    if "Logarítmica" in componentes:
        explicaciones.append(
            "Es logarítmica porque contiene una expresión "
            "logarítmica."
        )

    if "Trigonométrica" in componentes:
        explicaciones.append(
            "Es trigonométrica porque contiene funciones "
            "como seno, coseno o tangente."
        )

    return explicaciones
