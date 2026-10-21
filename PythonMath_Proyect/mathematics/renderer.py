
import io

import sympy as sp
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.family"] = "STIXGeneral"

from PIL import Image


def expresion_a_latex(expresion):
    """
    Convierte una expresión matemática a LaTeX.

    Acepta expresiones SymPy y cadenas de texto.
    """
    if isinstance(expresion, str):
        latex = expresion
    else:
        latex = sp.latex(expresion)

    # Limpiar tabulaciones y saltos de línea accidentales.
    latex = latex.replace("\t", " ")
    latex = latex.replace("\r", " ")
    latex = latex.replace("\n", " ")
    latex = latex.strip()

    return latex

def latex_a_imagen(latex, fontsize=24, dpi=180):
    latex = str(latex).replace("\t", " ").replace("\n", " ").strip()

    fig = None
    buffer = io.BytesIO()

    try:
        fig = plt.figure(figsize=(8, 1.2), dpi=dpi)
        fig.patch.set_alpha(0)

        fig.text(
            0.5,
            0.5,
            f"${latex}$",
            ha="center",
            va="center",
            fontsize=fontsize
        )

        buffer = io.BytesIO()

        fig.savefig(
            buffer,
            format="png",
            transparent=True,
            bbox_inches="tight",
            pad_inches=0.2,
            dpi=dpi
        )

        buffer.seek(0)

        with Image.open(buffer) as imagen:
            return imagen.convert("RGBA").copy()

    finally:
        if fig is not None:
            plt.close(fig)
        buffer.close()


def expresion_a_imagen(expresion, fontsize=24, dpi=180):
    latex = expresion_a_latex(expresion)
    return latex_a_imagen(
        latex,
        fontsize=fontsize,
        dpi=dpi
    )
