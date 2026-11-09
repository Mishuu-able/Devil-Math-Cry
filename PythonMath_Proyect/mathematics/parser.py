
import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication,
    implicit_application,
    function_exponentiation,
    split_symbols_custom,
    convert_xor,
)

# Variable simbolica compartida para todas las expresiones matemáticas
X = sp.Symbol("x", real=True)

# ============================================================
# TRANSFORMACIONES
# ============================================================

_NOMBRES_NO_DIVIDIR = {
    "pi", "e", "E", "Euler", "oo", "inf", "Infinity", "zoo", "nan", "I",
    "sin", "cos", "tan", "sec", "csc", "cot", "asin", "acos", "atan",
    "asec", "acsc", "acot", "sinh", "cosh", "tanh", "sech", "csch", "coth",
    "asinh", "acosh", "atanh", "asech", "acsch", "acoth", "sqrt", "exp",
    "log", "ln", "log10", "log2", "Abs", "abs", "floor", "ceiling", "ceil",
    "gamma", "loggamma", "erf", "erfc", "sign", "frac", "sinc", "Heaviside",
    "DiracDelta", "factorial", "binomial", "zeta", "Ei", "li", "polylog",
    "re", "im", "arg", "conjugate", "Min", "Max",
    "theta", "alpha", "beta", "delta", "lambda", "mu", "sigma", "omega",
}


def _se_puede_separar_simbolo(nombre):
    return (
        len(nombre) > 1
        and nombre.isalpha()
        and nombre not in _NOMBRES_NO_DIVIDIR
    )


TRANSFORMACIONES = standard_transformations + (
    split_symbols_custom(_se_puede_separar_simbolo),
    implicit_multiplication,
    implicit_application,
    function_exponentiation,
    convert_xor,
)


# ============================================================
# FUNCIONES TRIGONOMÉTRICAS
# ============================================================

FUNCIONES_TRIGONOMETRICAS = (
    "sin", "cos", "tan", "sec", "csc", "cot",
    "asin", "acos", "atan", "asec", "acsc", "acot",
    "sinh", "cosh", "tanh", "sech", "csch", "coth",
    "asinh", "acosh", "atanh", "asech", "acsch", "acoth",
)


_SUPERINDICES = str.maketrans({
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
})


def _convertir_potencias_trigonometricas(texto):

    nombres = "|".join(FUNCIONES_TRIGONOMETRICAS)

    patron = re.compile(
        rf"(?<![A-Za-z_])({nombres})\s*\^\s*(\d+)\s*\(",
        re.IGNORECASE,
    )

    while True:

        coincidencia = patron.search(texto)

        if coincidencia is None:
            break

        apertura = coincidencia.end() - 1
        profundidad = 0
        cierre = None

        for indice in range(apertura, len(texto)):

            if texto[indice] == "(":
                profundidad += 1

            elif texto[indice] == ")":

                profundidad -= 1

                if profundidad == 0:
                    cierre = indice
                    break

        if cierre is None:
            raise ValueError(
                "Faltan paréntesis en la función trigonométrica."
            )

        llamada = (
            coincidencia.group(1)
            + texto[apertura:cierre + 1]
        )

        exponente = coincidencia.group(2)

        reemplazo = f"({llamada})**{exponente}"

        texto = (
            texto[:coincidencia.start()]
            + reemplazo
            + texto[cierre + 1:]
        )

    return texto


# ============================================================
# RAÍCES CUADRADAS UNICODE
# ============================================================

def _convertir_raices_unicode(texto):

    while "√(" in texto:

        inicio = texto.index("√(")
        apertura = inicio + 1

        profundidad = 0
        cierre = None

        for indice in range(apertura, len(texto)):

            if texto[indice] == "(":
                profundidad += 1

            elif texto[indice] == ")":

                profundidad -= 1

                if profundidad == 0:
                    cierre = indice
                    break

        if cierre is None:
            raise ValueError(
                "Faltan paréntesis en la raíz cuadrada."
            )

        texto = (
            texto[:inicio]
            + "sqrt"
            + texto[apertura:cierre + 1]
            + texto[cierre + 1:]
        )

    texto = re.sub(
        r"√\s*([A-Za-z_]\w*|\d+(?:\.\d+)?)",
        r"sqrt(\1)",
        texto
    )

    return texto


# ============================================================
# NORMALIZACIÓN GENERAL
# ============================================================

def normalizar_expresion(expresion):

    texto = str(expresion).strip()

    if not texto:
        raise ValueError("La expresión matemática está vacía.")

    texto = texto.replace("·", "*").replace("×", "*")
    texto = texto.replace("ℯ", "E")

    texto = re.sub(
        r"\bEuler\b",
        "E",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r"π(?=[A-Za-z_(])",
        "pi*",
        texto
    )

    texto = texto.replace("π", "pi")

    texto = re.sub(
        r"([A-Za-z_][A-Za-z_0-9]*)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)",
        lambda m: (
            m.group(1)
            + "^"
            + m.group(2).translate(_SUPERINDICES)
        ),
        texto
    )

    texto = texto.translate(_SUPERINDICES)

    texto = _convertir_raices_unicode(texto)
    texto = _convertir_potencias_trigonometricas(texto)

    return texto


# ============================================================
# DICCIONARIO MATEMÁTICO
# ============================================================

def obtener_diccionario_matematico():

    nombres_funciones = (
        "sin", "cos", "tan", "sec", "csc", "cot",
        "asin", "acos", "atan", "asec", "acsc", "acot",
        "sinh", "cosh", "tanh", "sech", "csch", "coth",
        "asinh", "acosh", "atanh", "asech", "acsch", "acoth",
        "sqrt", "exp", "log", "Abs", "floor", "ceiling",
        "gamma", "loggamma", "erf", "erfc", "sign", "frac",
        "sinc", "Heaviside", "DiracDelta", "factorial", "binomial",
        "zeta", "Ei", "li", "polylog", "re", "im", "arg",
        "conjugate", "Min", "Max",
    )

    diccionario = {
        nombre: getattr(sp, nombre)
        for nombre in nombres_funciones
    }

    diccionario.update({

        "x": X,

        # Constantes
        "pi": sp.pi,
        "e": sp.E,
        "E": sp.E,
        "Euler": sp.E,

        # Logaritmos
        "ln": sp.log,
        "log": lambda argumento: sp.log(argumento, 10),
        "log10": lambda argumento: sp.log(argumento, 10),
        "log2": lambda argumento: sp.log(argumento, 2),

        # Alias
        "abs": sp.Abs,
        "ceil": sp.ceiling,

        # Infinito y números especiales
        "oo": sp.oo,
        "inf": sp.oo,
        "Infinity": sp.oo,
        "zoo": sp.zoo,
        "nan": sp.nan,
        "I": sp.I,
    })

    return diccionario


# ============================================================
# CONVERSIÓN PRINCIPAL
# ============================================================

def convertir_expresion(expresion):

    try:

        texto = normalizar_expresion(expresion)

        resultado = parse_expr(
            texto,
            transformations=TRANSFORMACIONES,
            local_dict=obtener_diccionario_matematico()
        )

        return resultado

    except Exception as error:

        raise ValueError(
            f"No se pudo interpretar la expresión matemática: {error}"
        ) from error
