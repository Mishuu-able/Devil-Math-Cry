
import requests


class AIService:

    API_URL = (
        "https://solvian.app.n8n.cloud/webhook/ia-matematica"
    )

    def preguntar(
        self,
        mensaje,
        nivel="universidad",
        modo="procedimiento"
    ):

        payload = {
            "ejercicio": mensaje,
            "nivel": nivel,
            "modo": modo
        }

        try:
            response = requests.post(
                self.API_URL,
                json=payload,
                timeout=90
            )

            response.raise_for_status()
            data = response.json()

            estado = data.get("estado")

            if estado == "error":
                raise Exception(
                    data.get(
                        "mensaje_error",
                        "La API encontró un error."
                    )
                )

            if estado == "no_soportado":
                return (
                    "Todavía no puedo resolver este tipo "
                    "de ejercicio.\n\n"
                    + data.get("explicacion", "")
                )

            if estado != "ok":
                raise Exception(
                    "La API devolvió una respuesta desconocida."
                )

            resultado = data.get("resultado", "")
            procedimiento = data.get("procedimiento", [])
            explicacion = data.get("explicacion", "")
            tipo = data.get("tipo_ejercicio", "")

            respuesta = f"Tipo de ejercicio: {tipo}\n\n"
            respuesta += f"Resultado:\n{resultado}\n\n"

            if modo == "procedimiento" and procedimiento:
                respuesta += "Procedimiento:\n"

                for i, paso in enumerate(procedimiento, 1):
                    respuesta += f"{i}. {paso}\n"

                respuesta += "\n"

            respuesta += f"Explicación:\n{explicacion}"

            if data.get("verificado") is True:
                respuesta += "\n\n✓ Resultado verificado por la API."

            return respuesta

        except requests.exceptions.Timeout:
            raise Exception(
                "La API tardó demasiado en responder."
            )

        except requests.exceptions.ConnectionError:
            raise Exception(
                "No se pudo conectar con el servidor."
            )

        except requests.exceptions.HTTPError as error:
            detalle = response.text

            raise Exception(
                f"Error HTTP: {error}\n\n"
                f"Respuesta del servidor:\n{detalle}"
            )

        except ValueError:
            raise Exception(
                "La API devolvió una respuesta JSON inválida."
            )
