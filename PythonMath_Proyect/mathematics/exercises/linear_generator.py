
import random
import re
from fractions import Fraction


class LinearExerciseGenerator:
    """
    Genera ecuaciones lineales de la forma:

        ax + b = c

    La solución se calcula antes de mostrar el ejercicio.
    """

    def __init__(self):
        self.ejercicio_actual = None

    @staticmethod
    def _formatear_termino(numero, variable=False):
        if variable:
            if numero == 1:
                return "x"
            if numero == -1:
                return "-x"
            return f"{numero}x"

        return str(numero)

    def generar_ejercicio(self, dificultad="facil"):
        configuraciones = {
            "facil": {
                "coef_min": 1,
                "coef_max": 5,
                "const_min": -10,
                "const_max": 10,
                "sol_min": -10,
                "sol_max": 10
            },
            "intermedio": {
                "coef_min": 2,
                "coef_max": 10,
                "const_min": -20,
                "const_max": 20,
                "sol_min": -15,
                "sol_max": 15
            },
            "dificil": {
                "coef_min": 3,
                "coef_max": 15,
                "const_min": -40,
                "const_max": 40,
                "sol_min": -20,
                "sol_max": 20
            }
        }

        dificultad = dificultad.lower()

        if dificultad not in configuraciones:
            dificultad = "facil"

        config = configuraciones[dificultad]

        # Coeficiente distinto de cero.
        a = random.randint(
            config["coef_min"],
            config["coef_max"]
        )

        # Variamos el signo del coeficiente.
        if random.choice([True, False]):
            a *= -1

        b = random.randint(
            config["const_min"],
            config["const_max"]
        )

        # Elegimos primero la solución.
        x = random.randint(
            config["sol_min"],
            config["sol_max"]
        )

        # Calculamos c para garantizar que x sea la solución.
        c = a * x + b

        signo = "+" if b >= 0 else "-"
        ecuacion = (
            f"{self._formatear_termino(a, True)} "
            f"{signo} {abs(b)} = {c}"
        )

        # Si b es cero, evitamos mostrar "+ 0".
        if b == 0:
            ecuacion = f"{self._formatear_termino(a, True)} = {c}"

        self.ejercicio_actual = {
            "tipo": "ecuacion_lineal",
            "dificultad": dificultad,
            "ecuacion": ecuacion,
            "a": a,
            "b": b,
            "c": c,
            "solucion": Fraction(x, 1),
            "respondido": False
        }

        return self.ejercicio_actual.copy()

    def verificar_respuesta(self, respuesta):
        """
        Acepta respuestas como:
            5
            x = 5
            -3
            x=-3
            3/2
        """

        if self.ejercicio_actual is None:
            return {
                "valida": False,
                "correcta": False,
                "mensaje": "Primero debes generar un ejercicio."
            }

        if self.ejercicio_actual["respondido"]:
            return {
                "valida": False,
                "correcta": False,
                "mensaje": "Este ejercicio ya fue respondido."
            }

        texto = str(respuesta).strip().lower().replace(" ", "")

        if texto.startswith("x="):
            texto = texto[2:]

        # Solo números, signo negativo y fracciones.
        if not re.fullmatch(r"-?\d+(?:/-?\d+)?", texto):
            return {
                "valida": False,
                "correcta": False,
                "mensaje": "Introduce un número válido. Ejemplo: 5 o -3."
            }

        try:
            valor = Fraction(texto)
        except (ValueError, ZeroDivisionError):
            return {
                "valida": False,
                "correcta": False,
                "mensaje": "La respuesta no tiene un formato válido."
            }

        correcta = valor == self.ejercicio_actual["solucion"]

        self.ejercicio_actual["respondido"] = True

        return {
            "valida": True,
            "correcta": correcta,
            "respuesta_usuario": valor,
            "respuesta_correcta": self.ejercicio_actual["solucion"],
            "mensaje": (
                "¡Respuesta correcta!"
                if correcta
                else "Respuesta incorrecta."
            )
        }

    def obtener_procedimiento(self):
        if self.ejercicio_actual is None:
            return []

        ejercicio = self.ejercicio_actual

        a = ejercicio["a"]
        b = ejercicio["b"]
        c = ejercicio["c"]
        resultado = ejercicio["solucion"]

        pasos = []

        pasos.append(
            f"Ecuación original: {ejercicio['ecuacion']}"
        )

        # Despejar el término con x.
        if b > 0:
            pasos.append(
                f"Restamos {b} en ambos lados: "
                f"{a}x = {c - b}"
            )
        elif b < 0:
            pasos.append(
                f"Sumamos {abs(b)} en ambos lados: "
                f"{a}x = {c - b}"
            )
        else:
            pasos.append(
                f"La ecuación ya tiene la forma {a}x = {c}."
            )

        pasos.append(
            f"Dividimos ambos lados entre {a}: "
            f"x = {resultado}"
        )

        pasos.append(
            f"Solución final: x = {resultado}"
        )

        return pasos
