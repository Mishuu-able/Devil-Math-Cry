
import numpy as np
import sympy as sp


def _evaluar_seguro(funcion, *variables):
    resultado = np.asarray(
        funcion(*variables),
        dtype=np.complex128
    )

    resultado = np.real_if_close(resultado)

    if np.iscomplexobj(resultado):
        resultado = np.where(
            np.abs(np.imag(resultado)) < 1e-10,
            np.real(resultado),
            np.nan
        )

    return np.asarray(resultado, dtype=float)


def generar_datos_2d(
    expresion,
    x_min=-10,
    x_max=10,
    puntos=500
):
    x = sp.Symbol("x")

    funcion = sp.lambdify(
        x,
        expresion,
        modules=["numpy"]
    )

    valores_x = np.linspace(x_min, x_max, puntos)
    valores_y = _evaluar_seguro(funcion, valores_x)

    valores_y[~np.isfinite(valores_y)] = np.nan

    return {
        "type": "curve",
        "expression": str(expresion),
        "x": valores_x,
        "y": valores_y,
        "metadata": {
            "x_label": "X",
            "y_label": "Y"
        }
    }


def generar_datos_3d(
    expresion,
    x_min=-5,
    x_max=5,
    y_min=-5,
    y_max=5,
    puntos=100
):
    x, y = sp.symbols("x y")

    funcion = sp.lambdify(
        (x, y),
        expresion,
        modules=["numpy"]
    )

    valores_x = np.linspace(x_min, x_max, puntos)
    valores_y = np.linspace(y_min, y_max, puntos)

    X, Y = np.meshgrid(valores_x, valores_y)

    Z = _evaluar_seguro(funcion, X, Y)

    # Garantizar que Z tenga las mismas dimensiones que X e Y.
    Z = np.broadcast_to(Z, X.shape).copy()

    Z[~np.isfinite(Z)] = np.nan

    return {
        "type": "surface",
        "expression": str(expresion),
        "x": valores_x,
        "y": valores_y,
        "X": X,
        "Y": Y,
        "Z": Z,
        "metadata": {
            "x_label": "X",
            "y_label": "Y",
            "z_label": "Z"
        }
    }
