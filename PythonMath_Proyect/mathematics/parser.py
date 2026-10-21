import sympy as sp

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)


# Transformaciones que permiten escribir
# matemáticas de forma natural.
TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def convertir_expresion(expresion):
    """
    Convierte una expresión escrita de forma natural
    a una expresión que SymPy pueda interpretar.

    Ejemplos:

        2x       -> 2*x
        x^2      -> x**2
        3(x+1)   -> 3*(x+1)
        2x^2     -> 2*x**2
    """

    x = sp.Symbol("x")

    try:

        resultado = parse_expr(
            expresion,
            transformations=TRANSFORMACIONES,
            local_dict={
                "x": x,
                "sin": sp.sin,
                "cos": sp.cos,
                "tan": sp.tan,
                "sqrt": sp.sqrt,
                "log": sp.log,
                "ln": sp.log,
                "exp": sp.exp,
                "pi": sp.pi,
                "e": sp.E
            }
        )

        return resultado

    except Exception as error:

        raise ValueError(
            "No se pudo interpretar la expresión matemática."
        ) from error